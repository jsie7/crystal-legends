from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase8]


@pytest.fixture(scope="module")
def phase_8_contract(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/contracts/legendary_branches.json").read_text()
    )


@pytest.fixture(scope="module")
def phase_8_constants(repo_root: Path, tmp_path_factory, phase_8_contract: dict) -> dict[str, int]:
    names = {
        "EVENT_SILVER_BIRD_RELEASED",
        "EVENT_ARTICUNO_AVAILABLE",
        "EVENT_ZAPDOS_AVAILABLE",
        "EVENT_MOLTRES_AVAILABLE",
        "NUM_EVENTS",
        "TRAINERTYPE_MOVES",
        "setevent_command",
        "setmapscene_command",
        "RIVAL2_1_ARTICUNO",
        "RIVAL2_1_ZAPDOS",
        "RIVAL2_1_MOLTRES",
        "RIVAL2_2_ARTICUNO",
        "RIVAL2_2_ZAPDOS",
        "RIVAL2_2_MOLTRES",
        "SNEASEL",
        "CROBAT",
        "MAGNETON",
        "GENGAR",
        "ALAKAZAM",
        "GROUP_ELMS_LAB",
        "MAP_ELMS_LAB",
        "EVENT_BEAT_RIVAL_IN_MT_MOON",
    }
    for branch in phase_8_contract["branches"]:
        names.update(
            {
                branch["returned_species"],
                branch["availability_event"],
                branch["mt_moon_party"],
                branch["indigo_party"],
            }
        )
    return resolve_constants(
        repo_root, tmp_path_factory.mktemp("phase_8_rom_constants"), sorted(names)
    )


def _rival2_parties(
    rom: RomImage, symbols: SymbolTable, trainer_type_moves: int
) -> list[list[tuple[int, ...]]]:
    offset = symbols["Rival2Group"].rom_offset
    parties: list[list[tuple[int, ...]]] = []
    for _ in range(6):
        while rom.u8(offset) != 0x50:
            offset += 1
        offset += 1
        assert rom.u8(offset) == trainer_type_moves
        offset += 1
        members: list[tuple[int, ...]] = []
        while rom.u8(offset) != 0xFF:
            members.append(tuple(rom.slice(offset, 6)))
            offset += 6
        offset += 1
        parties.append(members)
    return parties


def test_compiled_phase_8_ids_append_without_expanding_save_layout(
    repo_root: Path, phase_8_constants: dict[str, int]
) -> None:
    assert [
        phase_8_constants["EVENT_SILVER_BIRD_RELEASED"],
        phase_8_constants["EVENT_ARTICUNO_AVAILABLE"],
        phase_8_constants["EVENT_ZAPDOS_AVAILABLE"],
        phase_8_constants["EVENT_MOLTRES_AVAILABLE"],
    ] == [2011, 2012, 2013, 2014]
    assert phase_8_constants["NUM_EVENTS"] == 2048

    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    assert symbols["wCurBox"].address - symbols["wEventFlags"].address == 256


def test_compiled_silver_parties_and_numeric_slots_remain_stable(
    repo_root: Path, phase_8_constants: dict[str, int]
) -> None:
    assert [
        phase_8_constants["RIVAL2_1_ARTICUNO"],
        phase_8_constants["RIVAL2_1_ZAPDOS"],
        phase_8_constants["RIVAL2_1_MOLTRES"],
        phase_8_constants["RIVAL2_2_ARTICUNO"],
        phase_8_constants["RIVAL2_2_ZAPDOS"],
        phase_8_constants["RIVAL2_2_MOLTRES"],
    ] == [1, 2, 3, 4, 5, 6]

    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    parties = _rival2_parties(rom, symbols, phase_8_constants["TRAINERTYPE_MOVES"])
    birds = ("ARTICUNO", "ZAPDOS", "MOLTRES")
    for party, bird in zip(parties[:3], birds):
        assert len(party) == 6
        assert party[-1][:2] == (60, phase_8_constants[bird])

    expected_species = [
        phase_8_constants[name]
        for name in ("SNEASEL", "CROBAT", "MAGNETON", "GENGAR", "ALAKAZAM")
    ]
    for party in parties[3:]:
        assert len(party) == 5
        assert [member[1] for member in party] == expected_species
        assert [member[0] for member in party] == [45, 48, 45, 46, 46]
        assert all(member[1] not in {phase_8_constants[name] for name in birds} for member in party)


def test_compiled_mt_moon_victory_schedules_custom_scene_only(
    repo_root: Path, phase_8_constants: dict[str, int]
) -> None:
    custom_rom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference_rom = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())
    scene = custom_symbols.constant("SCENE_ELMSLAB_SILVER_RETURNS_BIRD")
    assert scene == reference_symbols.constant("SCENE_ELMSLAB_UNUSED") == 4

    custom = custom_rom.slice(
        custom_symbols["MountMoonRivalBattleScript.FinishBattle"].rom_offset,
        custom_symbols["MountMoonRivalMovementBefore"].rom_offset
        - custom_symbols["MountMoonRivalBattleScript.FinishBattle"].rom_offset,
    )
    reference = reference_rom.slice(
        reference_symbols["MountMoonRivalBattleScript.FinishBattle"].rom_offset,
        reference_symbols["MountMoonRivalMovementBefore"].rom_offset
        - reference_symbols["MountMoonRivalBattleScript.FinishBattle"].rom_offset,
    )
    set_victory = bytes([phase_8_constants["setevent_command"]]) + phase_8_constants[
        "EVENT_BEAT_RIVAL_IN_MT_MOON"
    ].to_bytes(2, "little")
    schedule = bytes(
        [
            phase_8_constants["setmapscene_command"],
            phase_8_constants["GROUP_ELMS_LAB"],
            phase_8_constants["MAP_ELMS_LAB"],
            scene,
        ]
    )
    assert custom.count(set_victory) == 1
    assert custom.count(schedule) == 1
    assert schedule not in reference
    for event in (
        "EVENT_SILVER_BIRD_RELEASED",
        "EVENT_ARTICUNO_AVAILABLE",
        "EVENT_ZAPDOS_AVAILABLE",
        "EVENT_MOLTRES_AVAILABLE",
    ):
        mutation = bytes([phase_8_constants["setevent_command"]]) + phase_8_constants[
            event
        ].to_bytes(2, "little")
        assert mutation not in custom
