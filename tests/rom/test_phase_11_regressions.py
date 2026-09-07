from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase11]


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_11_endgame.json").read_text()
    )


@pytest.fixture(scope="module")
def phase_11_constants(repo_root: Path, tmp_path_factory, scenario: dict) -> dict[str, int]:
    names = {
        "NUM_EVENTS",
        "TRAINERTYPE_MOVES",
        "RED",
        "EVENT_BEAT_RED",
        "EVENT_BEAT_PROFESSOR_OAK",
    }
    for boss in (scenario["red"],):
        for _, species, moves in boss["party"]:
            names.add(species)
            names.update(moves)
    return resolve_constants(
        repo_root, tmp_path_factory.mktemp("phase_11_constants"), sorted(names)
    )


def _decode_moves_party(
    rom: RomImage, offset: int, trainer_type_moves: int
) -> list[tuple[int, ...]]:
    while rom.u8(offset) != 0x50:
        offset += 1
    offset += 1
    assert rom.u8(offset) == trainer_type_moves
    offset += 1
    party = []
    while rom.u8(offset) != 0xFF:
        party.append(tuple(rom.slice(offset, 6)))
        offset += 6
    return party


def test_compiled_phase_11_event_ids_preserve_save_layout(
    repo_root: Path, scenario: dict, phase_11_constants: dict[str, int]
) -> None:
    for name, expected in scenario["events"]:
        assert phase_11_constants[name] == expected
    assert phase_11_constants["NUM_EVENTS"] == 2048
    symbols = SymbolTable.parse((repo_root / scenario["symbols"]).read_text())
    assert symbols["wCurBox"].address - symbols["wEventFlags"].address == 256


def test_compiled_red_party_is_custom_and_reference_red_remains_stock(
    repo_root: Path, scenario: dict, phase_11_constants: dict[str, int]
) -> None:
    custom = RomImage.load(repo_root / scenario["rom"])
    custom_symbols = SymbolTable.parse((repo_root / scenario["symbols"]).read_text())
    custom_party = _decode_moves_party(
        custom,
        custom_symbols["RedGroup"].rom_offset,
        phase_11_constants["TRAINERTYPE_MOVES"],
    )
    expected = [
        tuple(
            [level, phase_11_constants[species]]
            + [phase_11_constants[move] for move in moves]
        )
        for level, species, moves in scenario["red"]["party"]
    ]
    assert custom_party == expected

    reference = RomImage.load(repo_root / scenario["reference_rom"])
    reference_symbols = SymbolTable.parse(
        (repo_root / scenario["reference_symbols"]).read_text()
    )
    reference_party = _decode_moves_party(
        reference,
        reference_symbols["RedGroup"].rom_offset,
        phase_11_constants["TRAINERTYPE_MOVES"],
    )
    assert [member[0] for member in reference_party] == [81, 73, 75, 77, 77, 77]
    assert [member[1] for member in reference_party] == [member[1] for member in expected]


def test_compiled_red_dvs_are_maxed_only_in_crystal_legends(
    repo_root: Path, phase_11_constants: dict[str, int]
) -> None:
    class_index = phase_11_constants["RED"] - 1
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())
    assert custom.slice(custom_symbols["TrainerClassDVs"].rom_offset + class_index * 2, 2) == bytes([0xFF, 0xFF])
    assert reference.slice(reference_symbols["TrainerClassDVs"].rom_offset + class_index * 2, 2) == bytes([0xFD, 0xDE])
