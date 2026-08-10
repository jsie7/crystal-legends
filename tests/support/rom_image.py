from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from tests.support.symbol_table import Symbol, SymbolTable


class RomImageError(ValueError):
    pass


@dataclass(frozen=True)
class BackgroundEvent:
    y: int
    x: int
    event_type: int
    script_pointer: int


class RomImage:
    def __init__(self, data: bytes, path: Path | None = None) -> None:
        self.data = data
        self.path = path

    @classmethod
    def load(cls, path: Path) -> "RomImage":
        return cls(path.read_bytes(), path)

    @property
    def sha256(self) -> str:
        return sha256(self.data).hexdigest()

    def slice(self, offset: int, length: int) -> bytes:
        if offset < 0 or length < 0 or offset + length > len(self.data):
            raise RomImageError(
                f"ROM read [{offset:#x}, {offset + length:#x}) exceeds "
                f"image size {len(self.data):#x}"
            )
        return self.data[offset : offset + length]

    def u8(self, offset: int) -> int:
        return self.slice(offset, 1)[0]

    def u16le(self, offset: int) -> int:
        return int.from_bytes(self.slice(offset, 2), "little")

    def at(self, symbol: Symbol, length: int) -> bytes:
        return self.slice(symbol.rom_offset, length)


def decode_background_events(
    rom: RomImage,
    symbols: SymbolTable,
    map_events_label: str,
    warp_event_size: int,
    coord_event_size: int,
    bg_event_size: int,
) -> list[BackgroundEvent]:
    if bg_event_size != 5:
        raise RomImageError(f"unsupported BG_EVENT_SIZE {bg_event_size}")
    offset = symbols[map_events_label].rom_offset + 2
    warp_count = rom.u8(offset)
    offset += 1 + warp_count * warp_event_size
    coord_count = rom.u8(offset)
    offset += 1 + coord_count * coord_event_size
    bg_count = rom.u8(offset)
    offset += 1
    events: list[BackgroundEvent] = []
    for index in range(bg_count):
        record = offset + index * bg_event_size
        events.append(
            BackgroundEvent(
                y=rom.u8(record),
                x=rom.u8(record + 1),
                event_type=rom.u8(record + 2),
                script_pointer=rom.u16le(record + 3),
            )
        )
    return events


def validate_header(rom: RomImage) -> None:
    failures: list[str] = []
    expected_fields = {
        "size": (len(rom.data), 2 * 1024 * 1024),
        "title": (rom.slice(0x134, 11), b"CRYSTAL LGD"),
        "game id": (rom.slice(0x13F, 4), b"CLGE"),
        "CGB flag": (rom.u8(0x143), 0xC0),
        "cartridge type": (rom.u8(0x147), 0x10),
        "ROM size code": (rom.u8(0x148), 0x06),
        "RAM size code": (rom.u8(0x149), 0x03),
        "version": (rom.u8(0x14C), 0),
    }
    for name, (actual, expected) in expected_fields.items():
        if actual != expected:
            failures.append(f"{name}: expected {expected!r}, got {actual!r}")

    header_checksum = 0
    for value in rom.slice(0x134, 0x14D - 0x134):
        header_checksum = (header_checksum - value - 1) & 0xFF
    if header_checksum != rom.u8(0x14D):
        failures.append(
            f"header checksum: calculated ${header_checksum:02x}, "
            f"stored ${rom.u8(0x14D):02x}"
        )

    global_checksum = (
        sum(rom.data[:0x14E]) + sum(rom.data[0x150:])
    ) & 0xFFFF
    stored_checksum = int.from_bytes(rom.slice(0x14E, 2), "big")
    if global_checksum != stored_checksum:
        failures.append(
            f"global checksum: calculated ${global_checksum:04x}, "
            f"stored ${stored_checksum:04x}"
        )
    if failures:
        raise RomImageError("\n".join(failures))
