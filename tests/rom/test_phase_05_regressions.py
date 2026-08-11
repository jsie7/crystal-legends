from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase5]


@pytest.fixture(scope="module")
def phase_5_constants(repo_root: Path, tmp_path_factory) -> dict[str, int]:
    return resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_5_rom_constants"),
        [
            "EVENT_GOT_KABUTO_FROM_ALPH",
            "EVENT_GOT_OMANYTE_FROM_ALPH",
            "EVENT_GOT_AERODACTYL_FROM_ALPH",
            "NUM_EVENTS",
            "SPRITE_KABUTO",
            "SPRITE_OMANYTE",
            "SPRITE_AERODACTYL",
            "NUM_POKEMON_SPRITES",
            "KABUTO",
            "OMANYTE",
            "AERODACTYL",
        ],
    )


def test_compiled_phase_5_ids_use_the_reserved_numeric_slots(
    phase_5_constants: dict[str, int],
) -> None:
    assert [
        phase_5_constants["EVENT_GOT_KABUTO_FROM_ALPH"],
        phase_5_constants["EVENT_GOT_OMANYTE_FROM_ALPH"],
        phase_5_constants["EVENT_GOT_AERODACTYL_FROM_ALPH"],
    ] == [2004, 2005, 2006]
    assert phase_5_constants["NUM_EVENTS"] == 2048
    assert [
        phase_5_constants["SPRITE_KABUTO"],
        phase_5_constants["SPRITE_OMANYTE"],
        phase_5_constants["SPRITE_AERODACTYL"],
    ] == [0xA6, 0xA7, 0xA8]
    assert phase_5_constants["NUM_POKEMON_SPRITES"] == 41


def test_compiled_phase_5_sprite_table_extends_only_the_custom_rom(
    repo_root: Path, phase_5_constants: dict[str, int]
) -> None:
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_start = custom_symbols["SpriteMons"].rom_offset
    custom_end = custom_symbols["OutdoorSprites"].rom_offset
    custom_table = custom.slice(custom_start, custom_end - custom_start)
    assert len(custom_table) == phase_5_constants["NUM_POKEMON_SPRITES"]
    assert custom_table[-3:] == bytes(
        phase_5_constants[name] for name in ("KABUTO", "OMANYTE", "AERODACTYL")
    )

    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_start = reference_symbols["SpriteMons"].rom_offset
    reference_end = reference_symbols["OutdoorSprites"].rom_offset
    assert reference_end - reference_start == 35
    assert custom_table[:35] == reference.slice(reference_start, 35)


def test_phase_5_identity_does_not_change_the_save_layout(repo_root: Path) -> None:
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    assert symbols["wEventFlags"].bank == 1
    assert symbols["wEventFlags"].address == 55922
    assert symbols["wCurBox"].address - symbols["wEventFlags"].address == 256
