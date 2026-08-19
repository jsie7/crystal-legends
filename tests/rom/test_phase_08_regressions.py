from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage, decode_object_events
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
        "EVENT_INITIALIZED_EVENTS",
        "WARP_EVENT_SIZE",
        "COORD_EVENT_SIZE",
        "BG_EVENT_SIZE",
        "OBJECT_EVENT_SIZE",
        "SPRITE_RIVAL",
        "SPRITE_MOLTRES",
        "SPRITEMOVEDATA_STANDING_DOWN",
        "SPRITEMOVEDATA_POKEMON",
        "OBJECTTYPE_SCRIPT",
        "appear_command",
        "farsjump_command",
        "checkevent_command",
        "setscene_command",
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


def _object_events(
    rom: RomImage,
    symbols: SymbolTable,
    constants: dict[str, int],
):
    return decode_object_events(
        rom,
        symbols,
        "ElmsLab_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
        constants["OBJECT_EVENT_SIZE"],
    )


def _event_check(constants: dict[str, int], event: str) -> bytes:
    return bytes([constants["checkevent_command"]]) + constants[event].to_bytes(
        2, "little"
    )


def test_compiled_elm_scene_objects_and_cross_bank_entry_are_isolated(
    repo_root: Path, phase_8_constants: dict[str, int]
) -> None:
    constants = phase_8_constants
    custom_rom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference_rom = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )

    custom_only = {
        "ElmsLabSilverReturnsBirdScene",
        "ElmsLabSilverReturnsBirdScript",
        "ElmsLabSilverReturnPlayerMovement",
        "ElmsLabSilverArcScript",
        "ElmsLabSilverBirdExitMovement",
        "ElmsLabSilverExitMovement",
    }
    assert all(label in custom_symbols for label in custom_only)
    assert all(label not in reference_symbols for label in custom_only)

    custom_table = custom_symbols["ElmsLab_MapScripts"].rom_offset
    reference_table = reference_symbols["ElmsLab_MapScripts"].rom_offset
    assert custom_rom.u8(custom_table) == reference_rom.u8(reference_table) == 6
    scene_4_offset = 1 + 4 * 4
    assert custom_rom.u16le(custom_table + scene_4_offset) == custom_symbols[
        "ElmsLabSilverReturnsBirdScene"
    ].address
    assert reference_rom.u16le(reference_table + scene_4_offset) == reference_symbols[
        "ElmsLabNoop4Scene"
    ].address

    custom_objects = _object_events(custom_rom, custom_symbols, constants)
    reference_objects = _object_events(reference_rom, reference_symbols, constants)
    assert len(custom_objects) == 8
    assert len(reference_objects) == 6
    silver, bird = custom_objects[-2:]
    assert (silver.x, silver.y, silver.sprite, silver.movement) == (
        4,
        3,
        constants["SPRITE_RIVAL"],
        constants["SPRITEMOVEDATA_STANDING_DOWN"],
    )
    assert (bird.x, bird.y, bird.sprite, bird.movement) == (
        5,
        3,
        constants["SPRITE_MOLTRES"],
        constants["SPRITEMOVEDATA_POKEMON"],
    )
    for event in (silver, bird):
        assert event.palette_and_type & 0xF == constants["OBJECTTYPE_SCRIPT"]
        assert event.script_pointer == custom_symbols["ObjectEvent"].address
        assert event.event_flag == constants["EVENT_INITIALIZED_EVENTS"]

    stub = custom_rom.slice(
        custom_symbols["ElmsLabSilverReturnsBirdScript"].rom_offset,
        custom_symbols["ElmsLabWalkUpToElmScript"].rom_offset
        - custom_symbols["ElmsLabSilverReturnsBirdScript"].rom_offset,
    )
    target = custom_symbols["ElmsLabSilverArcScript"]
    far_jump = bytes([constants["farsjump_command"], target.bank]) + target.address.to_bytes(
        2, "little"
    )
    assert stub.count(far_jump) == 1
    assert target.bank != custom_symbols["ElmsLabSilverReturnsBirdScript"].bank


def test_compiled_release_helpers_encode_all_availability_facts_then_completion(
    repo_root: Path, phase_8_constants: dict[str, int]
) -> None:
    constants = phase_8_constants
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    helper = rom.slice(
        symbols["ElmsLabSilverSetAvailability"].rom_offset,
        symbols["ElmsLabSilverHandoffMovement"].rom_offset
        - symbols["ElmsLabSilverSetAvailability"].rom_offset,
    )
    for event in (
        "EVENT_ARTICUNO_AVAILABLE",
        "EVENT_ZAPDOS_AVAILABLE",
        "EVENT_MOLTRES_AVAILABLE",
    ):
        mutation = bytes([constants["setevent_command"]]) + constants[event].to_bytes(
            2, "little"
        )
        assert helper.count(mutation) == 1

    core = rom.slice(
        symbols["ElmsLabSilverArcScript"].rom_offset,
        symbols["ElmsLabSilverBufferReturnedBird"].rom_offset
        - symbols["ElmsLabSilverArcScript"].rom_offset,
    )
    release = bytes([constants["setevent_command"]]) + constants[
        "EVENT_SILVER_BIRD_RELEASED"
    ].to_bytes(2, "little")
    complete = bytes(
        [
            constants["setscene_command"],
            symbols.constant("SCENE_ELMSLAB_NOOP"),
        ]
    )
    assert core.count(release) == 1
    assert core.count(complete) == 1
    assert core.index(release) < core.index(complete)


def test_compiled_post_release_paths_add_only_the_custom_release_checks(
    repo_root: Path, phase_8_constants: dict[str, int]
) -> None:
    constants = phase_8_constants
    custom_rom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference_rom = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )
    release_check = _event_check(constants, "EVENT_SILVER_BIRD_RELEASED")
    ranges = (
        ("PlateauRivalBattle1", "PlateauRivalBattle2"),
        ("PlateauRivalBattle2", "PlateauRivalBattleCommon"),
        ("DragonsDenB1FCheckRivalCallback", "DragonsDenB1F_ClairScene"),
        ("DragonShrineElder1Script", "DragonShrineElder2Script"),
    )
    for start, end in ranges:
        custom = custom_rom.slice(
            custom_symbols[start].rom_offset,
            custom_symbols[end].rom_offset - custom_symbols[start].rom_offset,
        )
        reference = reference_rom.slice(
            reference_symbols[start].rom_offset,
            reference_symbols[end].rom_offset - reference_symbols[start].rom_offset,
        )
        assert custom.count(release_check) == 1
        assert release_check not in reference
