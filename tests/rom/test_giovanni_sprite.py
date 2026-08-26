from hashlib import sha256
from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.linker_map import parse_linker_map
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase10]


def test_compiled_giovanni_sprite_pointer_size_type_and_palette(
    repo_root: Path, tmp_path: Path,
) -> None:
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    constants = resolve_constants(repo_root, tmp_path, [
        "SPRITE_GIOVANNI", "SPRITE_STANDING_YOUNGSTER", "NUM_OVERWORLD_SPRITES",
        "SPRITE_POKEMON", "NUM_SPRITEDATA_FIELDS", "STANDING_SPRITE", "PAL_OW_BROWN",
    ])
    assert constants["SPRITE_GIOVANNI"] == constants["SPRITE_STANDING_YOUNGSTER"] + 1
    assert constants["SPRITE_GIOVANNI"] == constants["NUM_OVERWORLD_SPRITES"]
    assert constants["SPRITE_GIOVANNI"] < constants["SPRITE_POKEMON"]
    start, end = symbols["GiovanniSpriteGFX"], symbols["GiovanniSpriteGFXEnd"]
    assert start.bank == end.bank == 0x2c
    assert end.address - start.address == 192
    data = rom.at(start, 192)
    assert data == (repo_root / "gfx/sprites/giovanni.2bpp").read_bytes()
    assert sha256(data).hexdigest() == "d06c85addab6141e8949c58c27f39072ce3f9f7aab2e14a9a81542daeb1a3795"
    entry = symbols["OverworldSprites"].rom_offset + (
        constants["SPRITE_GIOVANNI"] - 1
    ) * constants["NUM_SPRITEDATA_FIELDS"]
    assert rom.slice(entry, constants["NUM_SPRITEDATA_FIELDS"]) == (
        start.address.to_bytes(2, "little")
        + bytes([192, start.bank, constants["STANDING_SPRITE"], constants["PAL_OW_BROWN"]])
    )
    usage = parse_linker_map((repo_root / "crystallegends.map").read_text())
    assert usage[("ROMX", start.bank)].free >= 0x2000


def test_reference_has_no_giovanni_and_existing_sprite_records_are_identical(
    repo_root: Path, tmp_path: Path,
) -> None:
    custom_rom = RomImage.load(repo_root / "crystallegends.gbc")
    custom = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference_rom = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())
    assert "GiovanniSpriteGFX" not in reference
    assert "GiovanniSpriteGFXEnd" not in reference
    constants = resolve_constants(repo_root, tmp_path, [
        "SPRITE_STANDING_YOUNGSTER", "NUM_SPRITEDATA_FIELDS",
    ])
    length = constants["SPRITE_STANDING_YOUNGSTER"] * constants["NUM_SPRITEDATA_FIELDS"]
    assert custom_rom.at(custom["OverworldSprites"], length) == reference_rom.at(
        reference["OverworldSprites"], length
    )
    for label in ("ChrisSpriteGFX", "PokefanMSpriteGFX", "StandingYoungsterSpriteGFX"):
        assert custom[label] == reference[label]
    # Both original sprite banks remain entirely unchanged, including padding.
    for label in ("ChrisSpriteGFX", "PokefanMSpriteGFX"):
        offset = custom[label].bank * 0x4000
        assert custom_rom.slice(offset, 0x4000) == reference_rom.slice(offset, 0x4000)
