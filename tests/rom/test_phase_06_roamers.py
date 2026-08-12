from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase6]


FLEE_GROUPS = (
    (
        "MAGNEMITE",
        "GRIMER",
        "TANGELA",
        "MR__MIME",
        "EEVEE",
        "PORYGON",
        "DRATINI",
        "DRAGONAIR",
        "TOGETIC",
        "UMBREON",
        "UNOWN",
        "SNUBBULL",
        "HERACROSS",
    ),
    (
        "CUBONE",
        "ARTICUNO",
        "ZAPDOS",
        "MOLTRES",
        "QUAGSIRE",
        "DELIBIRD",
        "PHANPY",
        "TEDDIURSA",
    ),
    ("RAIKOU", "ENTEI"),
)


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
            *(species for group in FLEE_GROUPS for species in group),
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


def _fast_ball_mismatch_target(
    rom: RomImage, symbols: SymbolTable
) -> tuple[int, int, bytes]:
    start = symbols["FastBallMultiplier"]
    routine = _range(rom, symbols, "FastBallMultiplier", "LevelBallMultiplier")
    compare_index = routine.index(b"\xb9\x20")
    branch_index = compare_index + 1
    displacement = routine[branch_index + 1]
    if displacement >= 0x80:
        displacement -= 0x100
    branch_address = start.address + branch_index
    return branch_index + 1, branch_address + 2 + displacement, routine


def test_compiled_fast_ball_branch_is_custom_only(repo_root: Path) -> None:
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse(
        (repo_root / "crystallegends.sym").read_text()
    )
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )
    custom_difference, custom_target, custom_routine = _fast_ball_mismatch_target(
        custom, custom_symbols
    )
    reference_difference, reference_target, reference_routine = (
        _fast_ball_mismatch_target(reference, reference_symbols)
    )
    assert custom_target == custom_symbols["FastBallMultiplier.loop"].address
    assert reference_target == reference_symbols["FastBallMultiplier.next"].address
    assert custom_difference == reference_difference
    assert len(custom_routine) == len(reference_routine)
    assert [
        index
        for index, pair in enumerate(zip(custom_routine, reference_routine))
        if pair[0] != pair[1]
    ] == [custom_difference]


def test_compiled_flee_groups_and_fast_ball_math_remain_stock(
    repo_root: Path, phase_6_constants: dict[str, int]
) -> None:
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse(
        (repo_root / "crystallegends.sym").read_text()
    )
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )
    expected_table = b"".join(
        bytes([*(phase_6_constants[species] for species in group), 0xFF])
        for group in FLEE_GROUPS
    )
    custom_table = _range(
        custom, custom_symbols, "SometimesFleeMons", "CompareMovePriority"
    )
    reference_table = _range(
        reference, reference_symbols, "SometimesFleeMons", "CompareMovePriority"
    )
    assert custom_table == reference_table == expected_table

    custom_routine = _range(
        custom, custom_symbols, "FastBallMultiplier", "LevelBallMultiplier"
    )
    assert custom_routine.count(b"\xcb\x20") == 2  # sla b
    assert b"\x06\xff\xc9" in custom_routine  # ld b, $ff; ret
