from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase4]


@pytest.fixture(scope="module")
def phase_4_constants(repo_root: Path, tmp_path_factory) -> dict[str, int]:
    return resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_4_rom_constants"),
        [
            "EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST",
            "EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER",
            "EVENT_GOT_TOTODILE_FROM_CIANWOOD",
            "SPRITE_CHIKORITA",
            "SPRITE_CYNDAQUIL",
            "SPRITE_TOTODILE",
            "NUM_POKEMON_SPRITES",
            "CHIKORITA",
            "CYNDAQUIL",
            "TOTODILE",
        ],
    )


def test_compiled_phase_4_ids_use_the_reserved_numeric_slots(
    phase_4_constants: dict[str, int],
) -> None:
    assert [
        phase_4_constants["EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST"],
        phase_4_constants["EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER"],
        phase_4_constants["EVENT_GOT_TOTODILE_FROM_CIANWOOD"],
    ] == [2001, 2002, 2003]
    assert [
        phase_4_constants["SPRITE_CHIKORITA"],
        phase_4_constants["SPRITE_CYNDAQUIL"],
        phase_4_constants["SPRITE_TOTODILE"],
    ] == [0xA3, 0xA4, 0xA5]
    assert phase_4_constants["NUM_POKEMON_SPRITES"] == 38


def test_compiled_phase_4_sprite_table_extends_only_the_custom_rom(
    repo_root: Path, phase_4_constants: dict[str, int]
) -> None:
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_start = custom_symbols["SpriteMons"].rom_offset
    custom_end = custom_symbols["OutdoorSprites"].rom_offset
    custom_table = custom.slice(custom_start, custom_end - custom_start)
    assert len(custom_table) == phase_4_constants["NUM_POKEMON_SPRITES"]
    assert custom_table[-3:] == bytes(
        phase_4_constants[name] for name in ("CHIKORITA", "CYNDAQUIL", "TOTODILE")
    )

    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_start = reference_symbols["SpriteMons"].rom_offset
    reference_end = reference_symbols["OutdoorSprites"].rom_offset
    assert reference_end - reference_start == 35
    assert custom_table[:35] == reference.slice(reference_start, 35)
