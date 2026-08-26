#!/usr/bin/env python3
"""Reproduce the three custom cave fixtures from checked-in graphics, without Pillow."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import struct
import zlib


ROOT = Path(__file__).resolve().parents[1]
CAVE_FLOOR_TILE = 0x16
FURNITURE_BLOCKS = (0x03, 0x16, 0x17)


@dataclass(frozen=True)
class Fixture:
    block: int
    donor_block: int
    graphics: str
    metatiles: str
    palettes: str
    floor_tiles: tuple[int, ...]
    tile_replacements: tuple[tuple[int, int], ...] = ()
    reclaimed_tiles: tuple[int, ...] = ()


FIXTURES = (
    Fixture(0x16, 0x21, "lab", "lab_metatiles", "lab", (0x10,)),
    Fixture(
        0x17, 0x08, "facility_crystallegends",
        # Both the patterned floor ($01) and blank floor ($26) need cave ground.
        "facility_metatiles_crystallegends", "facility", (0x01, 0x26),
    ),
    # Append the table to preserve both existing fixtures' graphic allocations.
    # Facility $29 has papers on the desk; use its empty tabletop tile instead.
    Fixture(
        0x03, 0x29, "facility_crystallegends",
        "facility_metatiles_crystallegends", "facility", (0x01, 0x26),
        tile_replacements=((0x48, 0x51), (0x49, 0x51)),
        reclaimed_tiles=(0x04,),  # Retired grass graphic, unique to Cave $03.
    ),
)


def read_png_graphics(path: Path) -> bytes:
    """Decode the repository's unfiltered, two-bit grayscale tileset PNGs."""
    raw = path.read_bytes()
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"not a PNG: {path}")
    position = 8
    compressed = bytearray()
    width = height = 0
    while position < len(raw):
        length = int.from_bytes(raw[position:position + 4], "big")
        kind = raw[position + 4:position + 8]
        data = raw[position + 8:position + 8 + length]
        position += length + 12
        if kind == b"IHDR":
            width, height, depth, color, compression, filtering, interlace = struct.unpack(
                ">IIBBBBB", data
            )
            if width != 128 or height % 8 or (depth, color, compression, filtering, interlace) != (2, 0, 0, 0, 0):
                raise ValueError(f"expected a 128px-wide two-bit grayscale tileset: {path}")
        elif kind == b"IDAT":
            compressed.extend(data)
        elif kind == b"IEND":
            break
    packed = zlib.decompress(compressed)
    stride = width // 4 + 1
    if len(packed) != height * stride or any(packed[y * stride] for y in range(height)):
        raise ValueError(f"expected unfiltered PNG rows: {path}")
    graphics = bytearray()
    for tile_y in range(height // 8):
        for tile_x in range(width // 8):
            for y in range(8):
                low = high = 0
                for x in range(8):
                    pixel_x = tile_x * 8 + x
                    value = packed[(tile_y * 8 + y) * stride + 1 + pixel_x // 4]
                    shade = 3 - ((value >> (6 - (pixel_x % 4) * 2)) & 3)
                    low |= (shade & 1) << (7 - x)
                    high |= (shade >> 1) << (7 - x)
                graphics.extend((low, high))
    return bytes(graphics)


def encode_png(graphics: bytes) -> bytes:
    width, height = 128, len(graphics) // 16 // 16 * 8
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(0, width, 4):
            packed = 0
            for dx in range(4):
                px = x + dx
                tile = (y // 8) * 16 + px // 8
                low, high = graphics[tile * 16 + (y % 8) * 2:tile * 16 + (y % 8) * 2 + 2]
                shift = 7 - px % 8
                shade = ((high >> shift) & 1) * 2 + ((low >> shift) & 1)
                packed |= (3 - shade) << (6 - dx * 2)
            rows.append(packed)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(
            ">I", zlib.crc32(kind + data) & 0xffffffff
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 2, 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + chunk(b"IEND", b"")
    )


def read_palettes(path: Path) -> dict[int, list[str]]:
    palettes: dict[int, list[str]] = {0: [], 1: []}
    for line in path.read_text().splitlines():
        match = re.match(r"\s*tilepal ([01]),\s*(.*)", line)
        if match:
            palettes[int(match[1])].extend(value.strip() for value in match[2].split(","))
    if any(len(values) != 96 for values in palettes.values()):
        raise ValueError(f"expected two 96-tile palette banks: {path}")
    return palettes


def generate_assets(root: Path = ROOT) -> dict[str, bytes]:
    graphics = bytearray(read_png_graphics(root / "gfx/tilesets/cave.png"))
    metatiles = bytearray((root / "data/tilesets/cave_metatiles.bin").read_bytes())
    palettes = read_palettes(root / "gfx/tilesets/cave_palette_map.asm")
    if len(graphics) != 96 * 16 or len(metatiles) != 64 * 16:
        raise ValueError("stock cave tileset dimensions changed")
    if metatiles[0x09 * 16:0x0a * 16] != bytes([CAVE_FLOOR_TILE]) * 16:
        raise ValueError("stock raised cave floor changed")

    # Start with slots unreferenced even by stock unused block definitions.
    # A fixture may also reclaim graphics unique to the block it replaces.
    # Preserve tile zero and the two animated water tiles ($14 and $40).
    occupied = set(metatiles) | {0, 0x14, 0x40}
    slots = [tile for tile in range(96) if tile not in occupied]
    slots.sort(key=lambda tile: (not any(graphics[tile * 16:(tile + 1) * 16]), tile))
    imported: dict[tuple[bytes, str], int] = {}

    for fixture in FIXTURES:
        start, end = fixture.block * 16, (fixture.block + 1) * 16
        for tile in fixture.reclaimed_tiles:
            if (
                tile in (0, 0x14, 0x40)
                or tile not in metatiles[start:end]
                or tile in metatiles[:start] + metatiles[end:]
                or tile in imported.values()
            ):
                raise ValueError(f"graphic ${tile:02x} is not exclusive to block ${fixture.block:02x}")
        slots[len(imported):len(imported)] = fixture.reclaimed_tiles
        donor_gfx = read_png_graphics(root / f"gfx/tilesets/{fixture.graphics}.png")
        donor_meta = (root / f"data/tilesets/{fixture.metatiles}.bin").read_bytes()
        donor_palettes = read_palettes(root / f"gfx/tilesets/{fixture.palettes}_palette_map.asm")
        replacements = dict(fixture.tile_replacements)
        block = bytearray()
        for tile in donor_meta[fixture.donor_block * 16:(fixture.donor_block + 1) * 16]:
            tile = replacements.get(tile, tile)
            if tile in fixture.floor_tiles:
                block.append(CAVE_FLOOR_TILE)
                continue
            bank = int(tile >= 0x80)
            bank_tile = tile - 0x80 if bank else tile
            source = bank * 96 + bank_tile
            pattern = donor_gfx[source * 16:(source + 1) * 16]
            palette = donor_palettes[bank][bank_tile]
            key = pattern, palette
            if key not in imported:
                target = slots[len(imported)]
                imported[key] = target
                graphics[target * 16:(target + 1) * 16] = pattern
                palettes[0][target] = palette
            block.append(imported[key])
        metatiles[fixture.block * 16:(fixture.block + 1) * 16] = block

    palette_lines = ["; Generated by tools/generate_cave_lab_tiles.py; non-furniture terrain is preserved."]
    for bank in (0, 1):
        if bank:
            palette_lines.extend(("", "rept 16", "\tdb $ff", "endr", ""))
        for start in range(0, 96, 8):
            palette_lines.append(f"\ttilepal {bank}, " + ", ".join(palettes[bank][start:start + 8]))

    return {
        "gfx/tilesets/cave_crystallegends.png": encode_png(bytes(graphics)),
        "data/tilesets/cave_metatiles_crystallegends.bin": bytes(metatiles),
        "gfx/tilesets/cave_crystallegends_palette_map.asm": ("\n".join(palette_lines) + "\n").encode(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify source assets without writing")
    args = parser.parse_args()
    for name, expected in generate_assets().items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_bytes() != expected:
                raise SystemExit(f"stale asset: {name}")
        else:
            path.write_bytes(expected)
        print(("verified " if args.check else "generated ") + name)


if __name__ == "__main__":
    main()
