from __future__ import annotations

from dataclasses import dataclass
import re


_SYMBOL_RE = re.compile(
    r"^([0-9a-fA-F]{2}):([0-9a-fA-F]{4})\s+([^\s;]+)\s*$"
)
_CONSTANT_RE = re.compile(r"^[0-9a-fA-F]+\s+[^\s;]+\s*$")


class SymbolTableError(ValueError):
    pass


@dataclass(frozen=True)
class Symbol:
    bank: int
    address: int
    label: str

    @property
    def domain(self) -> str:
        if self.address <= 0x7FFF:
            return "ROM"
        if 0xA000 <= self.address <= 0xBFFF:
            return "SRAM"
        if 0xC000 <= self.address <= 0xDFFF:
            return "WRAM"
        if 0xFF80 <= self.address <= 0xFFFE:
            return "HRAM"
        return "OTHER"

    @property
    def rom_offset(self) -> int:
        if self.domain != "ROM":
            raise SymbolTableError(f"{self.label} is in {self.domain}, not ROM")
        if self.bank == 0:
            return self.address
        if not 0x4000 <= self.address <= 0x7FFF:
            raise SymbolTableError(
                f"banked ROM symbol {self.label} has invalid address "
                f"${self.address:04x}"
            )
        return self.bank * 0x4000 + self.address - 0x4000


class SymbolTable:
    def __init__(self, symbols: dict[str, Symbol]) -> None:
        self._symbols = symbols
        reverse: dict[tuple[int, int], list[str]] = {}
        for symbol in symbols.values():
            reverse.setdefault((symbol.bank, symbol.address), []).append(symbol.label)
        self._reverse = reverse

    @classmethod
    def parse(cls, text: str) -> "SymbolTable":
        symbols: dict[str, Symbol] = {}
        for number, line in enumerate(text.splitlines(), start=1):
            if not line or line.startswith(";"):
                continue
            match = _SYMBOL_RE.match(line)
            if match is None:
                if _CONSTANT_RE.match(line):
                    continue
                raise SymbolTableError(f"line {number}: malformed symbol: {line}")
            bank, address, label = match.groups()
            if label in symbols:
                raise SymbolTableError(f"line {number}: duplicate label {label}")
            symbols[label] = Symbol(int(bank, 16), int(address, 16), label)
        return cls(symbols)

    def __contains__(self, label: str) -> bool:
        return label in self._symbols

    def __getitem__(self, label: str) -> Symbol:
        try:
            return self._symbols[label]
        except KeyError as error:
            raise SymbolTableError(f"required symbol is missing: {label}") from error

    def labels_at(self, bank: int, address: int) -> tuple[str, ...]:
        return tuple(self._reverse.get((bank, address), ()))
