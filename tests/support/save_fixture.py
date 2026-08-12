from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tests.support.symbol_table import Symbol, SymbolTable


class SaveFixtureError(ValueError):
    pass


@dataclass
class BatterySave:
    data: bytearray
    symbols: SymbolTable

    @classmethod
    def load(cls, path: Path, symbols: SymbolTable) -> "BatterySave":
        return cls(bytearray(path.read_bytes()), symbols)

    def _offset(self, symbol: Symbol) -> int:
        if symbol.domain != "SRAM":
            raise SaveFixtureError(f"{symbol.label} is not an SRAM symbol")
        offset = symbol.bank * 0x2000 + symbol.address - 0xA000
        if not 0 <= offset < len(self.data):
            raise SaveFixtureError(
                f"{symbol.label} maps outside the battery save at {offset:#x}"
            )
        return offset

    def _saved_symbols_for_field(self, field: Symbol) -> tuple[Symbol, Symbol]:
        ranges = (
            ("wPlayerData", "wPlayerDataEnd", "sPlayerData", "sBackupPlayerData"),
            ("wCurMapData", "wCurMapDataEnd", "sCurMapData", "sBackupCurMapData"),
            ("wPokemonData", "wPokemonDataEnd", "sPokemonData", "sBackupPokemonData"),
        )
        for wram_start, wram_end, primary_start, backup_start in ranges:
            start = self.symbols[wram_start]
            end = self.symbols[wram_end]
            if start.address <= field.address < end.address:
                delta = field.address - start.address
                primary = self.symbols[primary_start]
                backup = self.symbols[backup_start]
                return (
                    Symbol(primary.bank, primary.address + delta, field.label),
                    Symbol(backup.bank, backup.address + delta, field.label),
                )
        raise SaveFixtureError(f"{field.label} is not in a saved WRAM region")

    def write_saved_u8(self, wram_label: str, value: int) -> None:
        if not 0 <= value <= 0xFF:
            raise SaveFixtureError(f"byte value out of range: {value}")
        self.write_saved_bytes(wram_label, bytes([value]))

    def write_saved_bytes(self, wram_label: str, values: bytes) -> None:
        if not values:
            raise SaveFixtureError("saved byte sequence must not be empty")
        for symbol in self._saved_symbols_for_field(self.symbols[wram_label]):
            offset = self._offset(symbol)
            self.data[offset : offset + len(values)] = values

    def set_saved_bit(self, wram_label: str, bit: int, enabled: bool) -> None:
        if bit not in range(8):
            raise SaveFixtureError(f"bit index out of range: {bit}")
        for symbol in self._saved_symbols_for_field(self.symbols[wram_label]):
            offset = self._offset(symbol)
            mask = 1 << bit
            if enabled:
                self.data[offset] |= mask
            else:
                self.data[offset] &= ~mask

    def set_saved_bit_offset(
        self, wram_label: str, bit_offset: int, enabled: bool
    ) -> None:
        if bit_offset < 0:
            raise SaveFixtureError(f"bit offset out of range: {bit_offset}")
        base = self.symbols[wram_label]
        field = Symbol(
            base.bank,
            base.address + bit_offset // 8,
            f"{wram_label}[{bit_offset // 8}]",
        )
        for symbol in self._saved_symbols_for_field(field):
            offset = self._offset(symbol)
            mask = 1 << (bit_offset % 8)
            if enabled:
                self.data[offset] |= mask
            else:
                self.data[offset] &= ~mask

    def set_event(self, event_number: int, enabled: bool) -> None:
        event_flags = self.symbols["wEventFlags"]
        field = Symbol(
            event_flags.bank,
            event_flags.address + event_number // 8,
            f"wEventFlags[{event_number // 8}]",
        )
        for symbol in self._saved_symbols_for_field(field):
            offset = self._offset(symbol)
            mask = 1 << (event_number % 8)
            if enabled:
                self.data[offset] |= mask
            else:
                self.data[offset] &= ~mask

    def _checksum(self, start_label: str, end_label: str) -> int:
        start = self._offset(self.symbols[start_label])
        end = self._offset(self.symbols[end_label])
        return sum(self.data[start:end]) & 0xFFFF

    def refresh_checksums(self) -> None:
        pairs = (
            ("sGameData", "sGameDataEnd", "sChecksum"),
            ("sBackupGameData", "sBackupGameDataEnd", "sBackupChecksum"),
        )
        for start, end, destination in pairs:
            offset = self._offset(self.symbols[destination])
            self.data[offset : offset + 2] = self._checksum(start, end).to_bytes(
                2, "little"
            )

    def write(self, path: Path) -> None:
        self.refresh_checksums()
        path.write_bytes(self.data)
