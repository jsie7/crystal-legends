from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Callable, Iterator

from tests.support.bedroom_scenario import start_saved_game
from tests.support.pyboy_session import PyBoySession, prepare_rom
from tests.support.save_fixture import BatterySave
from tests.support.symbol_table import SymbolTable


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_badge_count(save: BatterySave, count: int) -> None:
    if count not in range(17):
        raise ValueError("badge count must be in 0..16")
    johto = min(count, 8)
    kanto = count - johto
    save.write_saved_u8("wJohtoBadges", (1 << johto) - 1)
    save.write_saved_u8("wKantoBadges", (1 << kanto) - 1)


def build_phase_10_checkpoint(
    repo_root: Path,
    destination: Path,
    constants: dict[str, int],
    scenario: dict,
    *,
    map_name: str,
    x: int,
    y: int,
    facing: str = "UP",
    badge_count: int = 16,
    events: dict[str, bool] | None = None,
) -> Path:
    fixture = repo_root / "tests/fixtures/saves" / scenario["save_fixture"]
    symbols = SymbolTable.parse((repo_root / scenario["symbols"]).read_text())
    save = BatterySave.load(fixture, symbols)
    save.write_saved_u8("wWarpNumber", 0)
    save.write_saved_u8("wMapGroup", constants[f"GROUP_{map_name}"])
    save.write_saved_u8("wMapNumber", constants[f"MAP_{map_name}"])
    save.write_saved_u8("wXCoord", x)
    save.write_saved_u8("wYCoord", y)
    save.write_saved_u8("wPlayerDirection", constants[f"OW_{facing}"])
    _write_badge_count(save, badge_count)

    for group in scenario["events"].values():
        for event, _ in group:
            save.set_event(constants[event], False)
    for event, enabled in (events or {}).items():
        save.set_event(constants[event], enabled)

    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


@contextmanager
def loaded_phase_10_checkpoint(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    scenario: dict,
    *,
    map_name: str,
    x: int,
    y: int,
    facing: str = "UP",
    badge_count: int = 16,
    events: dict[str, bool] | None = None,
    before_overworld: Callable[[PyBoySession], None] | None = None,
) -> Iterator[PyBoySession]:
    canonical = repo_root / "tests/fixtures/saves" / scenario["save_fixture"]
    canonical_hash = _sha256(canonical)
    fixture = build_phase_10_checkpoint(
        repo_root,
        work_dir / "phase-10-cerulean-cave.sav",
        constants,
        scenario,
        map_name=map_name,
        x=x,
        y=y,
        facing=facing,
        badge_count=badge_count,
        events=events,
    )
    prepared = prepare_rom(
        work_dir / "rom",
        repo_root / scenario["rom"],
        repo_root / scenario["symbols"],
        save_fixture=fixture,
    )
    try:
        with PyBoySession(prepared) as session:

            def prepare(current: PyBoySession) -> None:
                current.write_symbol("wDefaultSpawnpoint", constants["SPAWN_N_A"] & 0xFF)
                current.write_symbol("hMapEntryMethod", constants["MAPSETUP_WARP"])
                if before_overworld is not None:
                    before_overworld(current)

            start_saved_game(session, scenario["max_frames_per_step"], prepare)
            yield session
    finally:
        assert _sha256(canonical) == canonical_hash


@contextmanager
def loaded_phase_10_saved_game(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    scenario: dict,
    save_fixture: Path,
) -> Iterator[PyBoySession]:
    prepared = prepare_rom(
        work_dir,
        repo_root / scenario["rom"],
        repo_root / scenario["symbols"],
        save_fixture=save_fixture,
    )
    with PyBoySession(prepared) as session:

        def force_fresh_map_load(current: PyBoySession) -> None:
            current.write_symbol("wDefaultSpawnpoint", constants["SPAWN_N_A"] & 0xFF)
            current.write_symbol("hMapEntryMethod", constants["MAPSETUP_WARP"])

        start_saved_game(
            session,
            scenario["max_frames_per_step"],
            force_fresh_map_load,
        )
        yield session


@contextmanager
def loaded_phase_10_baseline_save(
    repo_root: Path,
    work_dir: Path,
    scenario: dict,
) -> Iterator[PyBoySession]:
    fixture = repo_root / "tests/fixtures/saves" / scenario["save_fixture"]
    canonical_hash = _sha256(fixture)
    prepared = prepare_rom(
        work_dir,
        repo_root / scenario["rom"],
        repo_root / scenario["symbols"],
        save_fixture=fixture,
    )
    try:
        with PyBoySession(prepared) as session:
            start_saved_game(session, scenario["max_frames_per_step"])
            yield session
    finally:
        assert _sha256(fixture) == canonical_hash
