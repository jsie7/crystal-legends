from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase6]


@pytest.fixture(scope="module")
def phase_6_constants(repo_root: Path, tmp_path_factory) -> dict[str, int]:
    return resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_6_rom_constants"),
        [
            "RAIKOU",
            "ENTEI",
            "GROUP_ROUTE_42",
            "MAP_ROUTE_42",
            "GROUP_ROUTE_37",
            "MAP_ROUTE_37",
            "BATTLETYPE_ROAMING",
            "GROUP_N_A",
            "MAP_N_A",
        ],
    )


def _range(
    rom: RomImage, symbols: SymbolTable, start: str, end: str
) -> bytes:
    first = symbols[start].rom_offset
    last = symbols[end].rom_offset
    return rom.slice(first, last - first)


def _ld_a_store(value: int, address: int) -> bytes:
    return bytes([0x3E, value, 0xEA, address & 0xFF, address >> 8])


def test_compiled_stock_roamer_engine_matches_reference(repo_root: Path) -> None:
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )
    ranges = (
        ("FindNest", "TryWildEncounter"),
        ("InitRoamMons", "CheckEncounterRoamMon"),
        ("CheckEncounterRoamMon", "UpdateRoamMons"),
        ("UpdateRoamMons", "ValidateTempWildMonSpecies"),
        ("BattleEnd_HandleRoamMons", "GetRoamMonMapGroup"),
    )
    for start, end in ranges:
        assert _range(custom, custom_symbols, start, end) == _range(
            reference, reference_symbols, start, end
        )


def test_compiled_initial_roamer_slots_match_stock_constants(
    repo_root: Path, phase_6_constants: dict[str, int]
) -> None:
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    routine = _range(rom, symbols, "InitRoamMons", "CheckEncounterRoamMon")
    expected = (
        ("RAIKOU", "wRoamMon1Species"),
        ("ENTEI", "wRoamMon2Species"),
        ("GROUP_ROUTE_42", "wRoamMon1MapGroup"),
        ("MAP_ROUTE_42", "wRoamMon1MapNumber"),
        ("GROUP_ROUTE_37", "wRoamMon2MapGroup"),
        ("MAP_ROUTE_37", "wRoamMon2MapNumber"),
    )
    for constant, destination in expected:
        assert _ld_a_store(
            phase_6_constants[constant], symbols[destination].address
        ) in routine
    level_sequence = bytes([0x3E, 40])
    assert level_sequence in routine
    assert bytes([0xAF, 0xEA]) in routine


def test_compiled_roam_struct_and_saved_range_are_unchanged(repo_root: Path) -> None:
    custom = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())
    for symbols in (custom, reference):
        assert symbols["wRoamMon2"].address - symbols["wRoamMon1"].address == 7
        assert symbols["wRoamMon3"].address - symbols["wRoamMon2"].address == 7
        assert (
            symbols["wRoamMons_CurMapNumber"].address
            - symbols["wRoamMon1"].address
            == 21
        )
    assert custom["wRoamMon1"].address == reference["wRoamMon1"].address
    assert custom["wRoamMons_CurMapNumber"].address == reference[
        "wRoamMons_CurMapNumber"
    ].address
