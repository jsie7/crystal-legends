from pathlib import Path
import re

import pytest

from tests.support.asm_conditions import active_lines
from tests.support.map_assets import parse_block_paths, parse_collision_rows
from tools.generate_cave_lab_tiles import (
    CAVE_FLOOR_TILE,
    FIXTURES,
    FURNITURE_BLOCKS,
    generate_assets,
    read_palettes,
    read_png_graphics,
)


pytestmark = [pytest.mark.static, pytest.mark.phase10]
CUSTOM = {"_CRYSTAL11", "_CRYSTALLEGENDS"}
REFERENCE = {"_CRYSTAL11"}


def test_cave_lab_assets_reproduce_from_checked_in_sources(repo_root: Path) -> None:
    for path, expected in generate_assets(repo_root).items():
        assert (repo_root / path).read_bytes() == expected, path


def test_only_furniture_blocks_and_unneeded_graphic_slots_change(repo_root: Path) -> None:
    stock = (repo_root / "data/tilesets/cave_metatiles.bin").read_bytes()
    custom = (repo_root / "data/tilesets/cave_metatiles_crystallegends.bin").read_bytes()
    assert len(stock) == len(custom) == 64 * 16
    changed = {
        block for block in range(64)
        if stock[block * 16:(block + 1) * 16] != custom[block * 16:(block + 1) * 16]
    }
    assert changed == set(FURNITURE_BLOCKS) == {0x03, 0x16, 0x17}
    original_gfx = read_png_graphics(repo_root / "gfx/tilesets/cave.png")
    custom_gfx = read_png_graphics(repo_root / "gfx/tilesets/cave_crystallegends.png")
    assert len(original_gfx) == len(custom_gfx) == 96 * 16
    changed_tiles = {
        tile for tile in range(96)
        if original_gfx[tile * 16:(tile + 1) * 16] != custom_gfx[tile * 16:(tile + 1) * 16]
    }
    imported_tiles = {
        tile for block in FURNITURE_BLOCKS
        for tile in custom[block * 16:(block + 1) * 16]
    } - {CAVE_FLOOR_TILE}
    assert len(imported_tiles) == 32
    assert changed_tiles <= imported_tiles
    assert changed_tiles.intersection(stock) == {0x04}
    # The one reclaimed graphic belongs only to the retired grass block.
    preserved_tiles = {
        tile for block in range(64) if block not in FURNITURE_BLOCKS
        for tile in stock[block * 16:(block + 1) * 16]
    }
    assert not changed_tiles.intersection(preserved_tiles)
    assert not changed_tiles.intersection({0, 0x14, 0x40})
    original_pal = read_palettes(repo_root / "gfx/tilesets/cave_palette_map.asm")
    custom_pal = read_palettes(repo_root / "gfx/tilesets/cave_crystallegends_palette_map.asm")
    assert original_pal[1] == custom_pal[1]
    for tile in range(96):
        if tile not in imported_tiles:
            assert original_pal[0][tile] == custom_pal[0][tile]


def test_imports_preserve_fixture_art_and_use_nonanimated_cave_floor(repo_root: Path) -> None:
    custom_gfx = read_png_graphics(repo_root / "gfx/tilesets/cave_crystallegends.png")
    custom_meta = (repo_root / "data/tilesets/cave_metatiles_crystallegends.bin").read_bytes()
    custom_pal = read_palettes(repo_root / "gfx/tilesets/cave_crystallegends_palette_map.asm")
    for fixture in FIXTURES:
        donor_gfx = read_png_graphics(repo_root / f"gfx/tilesets/{fixture.graphics}.png")
        donor_meta = (repo_root / f"data/tilesets/{fixture.metatiles}.bin").read_bytes()
        donor_pal = read_palettes(repo_root / f"gfx/tilesets/{fixture.palettes}_palette_map.asm")
        source = donor_meta[fixture.donor_block * 16:(fixture.donor_block + 1) * 16]
        target = custom_meta[fixture.block * 16:(fixture.block + 1) * 16]
        replacements = dict(fixture.tile_replacements)
        for before, after in zip(source, target):
            before = replacements.get(before, before)
            assert after < 0x60
            assert custom_pal[0][after] != "WATER"
            if before in fixture.floor_tiles:
                assert after == CAVE_FLOOR_TILE
                assert custom_pal[0][after] == "BROWN"
                continue
            bank = int(before >= 0x80)
            local_tile = before - 0x80 if bank else before
            index = bank * 96 + local_tile
            assert custom_gfx[after * 16:(after + 1) * 16] == donor_gfx[index * 16:(index + 1) * 16]
            assert custom_pal[0][after] == donor_pal[bank][local_tile]


@pytest.mark.parametrize("block", [0x03, 0x17])
def test_table_and_terminal_bottom_rows_match_the_cave_ground(repo_root: Path, block: int) -> None:
    meta = (repo_root / "data/tilesets/cave_metatiles_crystallegends.bin").read_bytes()
    # The two previously blank donor-$26 cells must match the other floor cells.
    assert meta[block * 16 + 12:(block + 1) * 16] == bytes([CAVE_FLOOR_TILE]) * 4
    assert meta[0x09 * 16:0x0a * 16] == bytes([CAVE_FLOOR_TILE]) * 16


def test_empty_table_reuses_terminal_base_and_retires_only_grass(repo_root: Path) -> None:
    stock = (repo_root / "data/tilesets/cave_metatiles.bin").read_bytes()
    meta = (repo_root / "data/tilesets/cave_metatiles_crystallegends.bin").read_bytes()
    gfx = read_png_graphics(repo_root / "gfx/tilesets/cave_crystallegends.png")
    donor = read_png_graphics(repo_root / "gfx/tilesets/facility_crystallegends.png")
    table = meta[0x03 * 16:0x04 * 16]
    assert stock[0x03 * 16:0x04 * 16] == bytes([0x04]) * 16
    assert 0x04 in table
    assert table[8:] == meta[0x17 * 16 + 8:0x18 * 16]
    # A bare tabletop: no papers ($48/$49), computer, or terminal controls.
    for source, target in zip((0x40, 0x41, 0x41, 0x42, 0x50, 0x51, 0x51, 0x52), table[:8]):
        assert gfx[target * 16:(target + 1) * 16] == donor[source * 16:(source + 1) * 16]
    assert meta[0x3f * 16:] == stock[0x3f * 16:]


def test_existing_cave_maps_never_use_the_reserved_blocks(repo_root: Path) -> None:
    paths = parse_block_paths((repo_root / "data/maps/blocks.asm").read_text())
    headers = active_lines((repo_root / "data/maps/maps.asm").read_text(), CUSTOM)
    attrs_source = (repo_root / "data/maps/attributes.asm").read_text()
    attrs_source = re.sub(r"(?ms)^MACRO\b.*?^ENDM\s*$", "", attrs_source)
    attrs = "\n".join(line.text for line in active_lines(attrs_source, CUSTOM))
    checked = []
    for line in headers:
        match = re.match(r"\s*map (\w+), TILESET_(?:DARK_)?CAVE,", line.text)
        if not match or match[1] == "CeruleanCave":
            continue
        name = match[1]
        checked.append(name)
        assert not set((repo_root / paths[name]).read_bytes()).intersection(FURNITURE_BLOCKS), name
        border = re.search(r"\bmap_attributes " + name + r",\s*\w+,\s*\$([\da-f]+)", attrs)
        assert border, name
        assert int(border[1], 16) not in FURNITURE_BLOCKS, name
        for code in active_lines((repo_root / f"maps/{name}.asm").read_text(), CUSTOM):
            change = re.match(r"\s*changeblock [^,]+, [^,]+, \$([\da-f]+)", code.text)
            if change:
                assert int(change[1], 16) not in FURNITURE_BLOCKS, name
    assert len(checked) >= 32


def test_collision_footprints_are_custom_only(repo_root: Path) -> None:
    text = (repo_root / "data/tilesets/cave_collision.asm").read_text()
    stock = parse_collision_rows(text, REFERENCE)
    custom = parse_collision_rows(text, CUSTOM)
    assert len(stock) == len(custom) == 64
    assert custom[0x03] == ("WALL", "WALL", "FLOOR", "FLOOR")
    assert custom[0x16] == ("FLOOR", "FLOOR", "WALL", "WALL")
    assert custom[0x17] == ("WALL", "WALL", "FLOOR", "FLOOR")
    assert stock[0x16] == ("WALL", "FLOOR", "WALL", "WARP_CARPET_DOWN")
    assert stock[0x17] == ("FLOOR", "WALL", "FLOOR", "FLOOR")
    assert stock[0x03] == ("TALL_GRASS",) * 4
    assert [i for i in range(64) if stock[i] != custom[i]] == [0x03, 0x16, 0x17]


def test_reference_builds_select_only_original_cave_assets(repo_root: Path) -> None:
    for definitions, suffix in ((CUSTOM, "_crystallegends"), (REFERENCE, "")):
        gfx = "\n".join(line.text for line in active_lines(
            (repo_root / "gfx/tilesets.asm").read_text(), definitions
        ))
        cave = gfx[gfx.index("TilesetCaveGFX::"):gfx.index('SECTION "Tileset Data 3"')]
        assert f'INCBIN "gfx/tilesets/cave{suffix}.2bpp.lz"' in cave
        assert f'INCBIN "data/tilesets/cave_metatiles{suffix}.bin"' in cave
        palette = "\n".join(line.text for line in active_lines(
            (repo_root / "gfx/tileset_palette_maps.asm").read_text(), definitions
        ))
        assert f'INCLUDE "gfx/tilesets/cave{suffix}_palette_map.asm"' in palette
        if not suffix:
            assert "cave_crystallegends" not in cave + palette
            assert "cave_metatiles_crystallegends" not in cave
