from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
import shutil
from typing import Callable

from tests.support.symbol_table import SymbolTable


class EmulatorError(RuntimeError):
    pass


class EmulatorTimeout(EmulatorError):
    pass


@dataclass(frozen=True)
class PreparedRom:
    rom: Path
    symbols: Path
    save: Path
    rtc: Path
    sha256: str


@dataclass(frozen=True)
class ScriptLocation:
    bank: int
    address: int

    def __str__(self) -> str:
        return f"{self.bank:02x}:{self.address:04x}"


def prepare_rom(
    work_dir: Path,
    rom_path: Path,
    symbol_path: Path,
    save_fixture: Path | None = None,
    rtc_fixture: Path | None = None,
) -> PreparedRom:
    work_dir.mkdir(parents=True, exist_ok=True)
    rom = work_dir / rom_path.name
    symbols = work_dir / symbol_path.name
    shutil.copy2(rom_path, rom)
    shutil.copy2(symbol_path, symbols)
    save = Path(f"{rom}.ram")
    rtc = Path(f"{rom}.rtc")
    if save_fixture is not None:
        shutil.copy2(save_fixture, save)
    if rtc_fixture is not None:
        shutil.copy2(rtc_fixture, rtc)
    return PreparedRom(
        rom=rom,
        symbols=symbols,
        save=save,
        rtc=rtc,
        sha256=sha256(rom.read_bytes()).hexdigest(),
    )


class PyBoySession:
    def __init__(self, prepared: PreparedRom, pyboy_factory=None) -> None:
        if pyboy_factory is None:
            from pyboy import PyBoy

            pyboy_factory = PyBoy
        self.prepared = prepared
        self.symbols = SymbolTable.parse(prepared.symbols.read_text())
        self.pyboy = pyboy_factory(
            str(prepared.rom),
            window="null",
            symbols=str(prepared.symbols),
            sound_emulated=False,
            log_level="ERROR",
        )
        self.pyboy.set_emulation_speed(0)
        self.frames = 0
        self.hook_history: list[str] = []
        self.script_history: list[str] = []
        self.script_trace: list[str] = []
        self._registered_hooks: set[str] = set()
        self._script_tracing = False
        self.stopped = False

    def __enter__(self) -> "PyBoySession":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        if not self.stopped:
            self.pyboy.stop(False)
            self.stopped = True

    def register_hook(self, label: str) -> None:
        if label in self._registered_hooks:
            return
        self.symbols[label]

        def record_hook(context: tuple["PyBoySession", str]) -> None:
            session, hook_label = context
            session.hook_history.append(hook_label)

        self.pyboy.hook_register(None, label, record_hook, (self, label))
        self._registered_hooks.add(label)

    def tick(self, count: int = 1, render: bool = False) -> None:
        if count < 1:
            raise ValueError("tick count must be positive")
        alive = self.pyboy.tick(count, render)
        self.frames += count
        if not alive:
            raise EmulatorError(f"emulation stopped unexpectedly\n{self.diagnostics()}")

    def wait_until(
        self,
        predicate: Callable[["PyBoySession"], bool],
        max_frames: int,
        description: str,
    ) -> None:
        if predicate(self):
            return
        start = self.frames
        while self.frames - start < max_frames:
            self.tick()
            if predicate(self):
                return
        raise EmulatorTimeout(
            f"timed out waiting for {description} after {max_frames} frames\n"
            f"{self.diagnostics()}"
        )

    def wait_for_hook(self, label: str, max_frames: int) -> None:
        self.register_hook(label)
        self.wait_until(
            lambda session: label in session.hook_history,
            max_frames,
            f"hook {label}",
        )

    def wait_for_hook_count(self, label: str, count: int, max_frames: int) -> None:
        self.register_hook(label)
        self.wait_until(
            lambda session: session.hook_history.count(label) >= count,
            max_frames,
            f"hook {label} occurrence {count}",
        )

    def enable_script_tracing(self) -> None:
        if self._script_tracing:
            return
        self.symbols["RunScriptCommand"]

        def record_script(context: "PyBoySession") -> None:
            location = context.script_location()
            labels = context.symbols.labels_at(location.bank, location.address)
            rendered = str(location)
            if labels:
                context.script_history.extend(labels)
                rendered += " " + ",".join(labels)
            context.script_trace.append(rendered)

        self.pyboy.hook_register(None, "RunScriptCommand", record_script, self)
        self._registered_hooks.add("RunScriptCommand")
        self._script_tracing = True

    def wait_for_script(self, label: str, max_frames: int) -> None:
        self.symbols[label]
        self.enable_script_tracing()
        self.wait_until(
            lambda session: label in session.script_history,
            max_frames,
            f"script {label}",
        )

    def tap(self, button: str, hold_frames: int = 2, release_frames: int = 2) -> None:
        self.pyboy.button_press(button)
        self.tick(hold_frames)
        self.pyboy.button_release(button)
        self.tick(release_frames)

    def read_symbol(self, label: str) -> int:
        symbol = self.symbols[label]
        if symbol.domain in {"WRAM", "SRAM"} and symbol.bank:
            return self.pyboy.memory[symbol.bank, symbol.address]
        return self.pyboy.memory[symbol.address]

    def read_symbol_bytes(self, label: str, length: int) -> bytes:
        if length < 1:
            raise ValueError("read length must be positive")
        symbol = self.symbols[label]
        if symbol.domain in {"WRAM", "SRAM"} and symbol.bank:
            return bytes(
                self.pyboy.memory[symbol.bank, symbol.address + offset]
                for offset in range(length)
            )
        return bytes(
            self.pyboy.memory[symbol.address + offset] for offset in range(length)
        )

    def read_symbol_u16(self, label: str) -> int:
        return int.from_bytes(self.read_symbol_bytes(label, 2), "little")

    def read_symbol_range(self, first_label: str, end_label: str) -> bytes:
        first = self.symbols[first_label]
        end = self.symbols[end_label]
        if first.domain != end.domain or first.bank != end.bank:
            raise ValueError(
                f"symbol range crosses memory domains: {first_label} to {end_label}"
            )
        return self.read_symbol_bytes(first_label, end.address - first.address)

    def script_location(self) -> ScriptLocation:
        return ScriptLocation(
            bank=self.read_symbol("wScriptBank"),
            address=self.read_symbol_u16("wScriptPos"),
        )

    def diagnostics(self) -> str:
        state: list[str] = [
            f"ROM SHA-256: {self.prepared.sha256}",
            f"PyBoy: {version('pyboy')}",
            f"frames: {self.frames}",
            f"PC: ${self.pyboy.register_file.PC:04x}",
            "hooks: " + (", ".join(self.hook_history[-20:]) or "<none>"),
            "scripts: " + (", ".join(self.script_trace[-20:]) or "<none>"),
        ]
        for label in ("wMapGroup", "wMapNumber", "wXCoord", "wYCoord", "wScriptMode"):
            if label in self.symbols:
                try:
                    state.append(f"{label}: ${self.read_symbol(label):02x}")
                except Exception as error:  # diagnostics must not hide the failure
                    state.append(f"{label}: <unavailable: {error}>")
        return "\n".join(state)
