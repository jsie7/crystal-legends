from pathlib import Path
import subprocess

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.linker_map import parse_linker_map
from tests.support.map_assets import parse_collision_rows
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable
from tools.generate_cave_lab_tiles import read_palettes, read_png_graphics


pytestmark = [pytest.mark.rom, pytest.mark.phase10]


@pytest.mark.parametrize("custom", [False, True])
def test_compiled_cave_furniture_assets_and_reference_isolation(
    repo_root: Path, tmp_path: Path, custom: bool
) -> None:
    stem = "crystallegends" if custom else "pokecrystal11"
    suffix = "_crystallegends" if custom else ""
    definitions = {"_CRYSTAL11", "_CRYSTALLEGENDS"} if custom else {"_CRYSTAL11"}
    rom = RomImage.load(repo_root / f"{stem}.gbc")
    symbols = SymbolTable.parse((repo_root / f"{stem}.sym").read_text())
    graphics = (repo_root / f"gfx/tilesets/cave{suffix}.2bpp.lz").read_bytes()
    assert rom.at(symbols["TilesetCaveGFX"], len(graphics)) == graphics
    dark = (repo_root / "gfx/tilesets/dark_cave.2bpp.lz").read_bytes()
    assert rom.at(symbols["TilesetDarkCaveGFX"], len(dark)) == dark
    metatiles = (repo_root / f"data/tilesets/cave_metatiles{suffix}.bin").read_bytes()
    for label in ("TilesetCaveMeta", "TilesetDarkCaveMeta"):
        assert rom.at(symbols[label], 1024) == metatiles

    colors = ("GRAY", "RED", "GREEN", "WATER", "YELLOW", "BROWN", "ROOF", "TEXT")
    constants = resolve_constants(repo_root, tmp_path, [
        "COLL_FLOOR", "COLL_WALL", "COLL_TALL_GRASS", "COLL_WARP_CARPET_DOWN", "OAM_BANK0", "OAM_BANK1",
        *(f"PAL_BG_{color}" for color in colors),
    ])
    rows = parse_collision_rows(
        (repo_root / "data/tilesets/cave_collision.asm").read_text(), definitions
    )
    for label in ("TilesetCaveColl", "TilesetDarkCaveColl"):
        for block in (0x03, 0x16, 0x17):
            actual = rom.slice(symbols[label].rom_offset + block * 4, 4)
            assert actual == bytes(constants[f"COLL_{value}"] for value in rows[block])

    palettes = read_palettes(repo_root / f"gfx/tilesets/cave{suffix}_palette_map.asm")
    encoded = bytearray()
    for bank in (0, 1):
        if bank:
            encoded.extend([0xff] * 16)
        for i in range(0, 96, 2):
            a, b = (constants[f"PAL_BG_{color}"] | constants[f"OAM_BANK{bank}"]
                    for color in palettes[bank][i:i + 2])
            encoded.append(a | b << 4)
    for label in ("TilesetCavePalMap", "TilesetDarkCavePalMap"):
        assert rom.at(symbols[label], len(encoded)) == bytes(encoded)


def test_compiled_collision_changes_are_limited_to_three_unused_blocks(repo_root: Path) -> None:
    outputs = []
    for stem in ("pokecrystal11", "crystallegends"):
        symbols = SymbolTable.parse((repo_root / f"{stem}.sym").read_text())
        rom = RomImage.load(repo_root / f"{stem}.gbc")
        outputs.append(rom.at(symbols["TilesetCaveColl"], 64 * 4))
    before, after = outputs
    assert [block for block in range(64)
            if before[block * 4:(block + 1) * 4] != after[block * 4:(block + 1) * 4]] == [0x03, 0x16, 0x17]


def test_optimized_cave_graphics_keep_the_original_bank_and_reserve(repo_root: Path) -> None:
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    assert symbols["TilesetCaveGFX"].bank == 0x07
    packed = (repo_root / "gfx/tilesets/cave_crystallegends.2bpp.lz").read_bytes()
    assert len(packed) == 1008
    unpacked = subprocess.run(
        [str(repo_root / "tools/lzcompress"), "--uncompress", "--", "-", "-"],
        input=packed, capture_output=True, check=True,
    ).stdout
    assert unpacked == read_png_graphics(repo_root / "gfx/tilesets/cave_crystallegends.png")
    usage = parse_linker_map((repo_root / "crystallegends.map").read_text())
    assert usage[("ROMX", 0x07)].free == 0x0034
