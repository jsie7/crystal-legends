from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from tests.support.asm_conditions import active_lines
from tests.support.content_data import parse_trainer_parties


pytestmark = [pytest.mark.static, pytest.mark.phase8]


CRYSTAL_LEGENDS = {"_CRYSTAL11", "_CRYSTALLEGENDS"}
REFERENCE = {"_CRYSTAL11"}


def _active_code(path: Path, definitions: set[str]) -> list[str]:
    return [
        line.text.split(";", 1)[0].strip()
        for line in active_lines(path.read_text(), definitions)
        if line.text.split(";", 1)[0].strip()
    ]


def _definitions(lines: list[str]) -> dict[str, str]:
    definitions: dict[str, str] = {}
    for line in lines:
        match = re.fullmatch(r"DEF\s+(\w+)\s+EQU\s+(\w+)", line)
        if match:
            definitions[match.group(1)] = match.group(2)
    return definitions


def _assert_contiguous(lines: list[str], expected: list[str]) -> None:
    width = len(expected)
    assert any(lines[index : index + width] == expected for index in range(len(lines)))


def test_phase_8_scenario_and_branch_contracts(repo_root: Path) -> None:
    scenario = json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_08_silver_arc.json").read_text()
    )
    branches = json.loads(
        (repo_root / scenario["branches_contract"]).read_text()
    )["branches"]

    assert scenario["scenario_id"] == "phase-08-silver-arc"
    assert scenario["rom"] == "crystallegends.gbc"
    assert scenario["reference_rom"] == "pokecrystal11.gbc"
    assert scenario["save_fixture"] == "bedroom_initialized.sav"
    assert scenario["max_frames_per_step"] == 60000
    assert scenario["event_order"] == ["availability", "released", "completed_scene"]
    assert scenario["events"]["availability"] == [
        "EVENT_ARTICUNO_AVAILABLE",
        "EVENT_ZAPDOS_AVAILABLE",
        "EVENT_MOLTRES_AVAILABLE",
    ]

    assert [
        (
            branch["player"],
            branch["returned_species"],
            branch["oak"],
            branch["availability_event"],
        )
        for branch in branches
    ] == [
        ("ARTICUNO", "MOLTRES", "ZAPDOS", "EVENT_MOLTRES_AVAILABLE"),
        ("ZAPDOS", "ARTICUNO", "MOLTRES", "EVENT_ARTICUNO_AVAILABLE"),
        ("MOLTRES", "ZAPDOS", "ARTICUNO", "EVENT_ZAPDOS_AVAILABLE"),
    ]
    for branch in branches:
        assert branch["returned_species"] == branch["rival"]
        assert len(
            {
                branch["availability_event"],
                branch["player_availability_event"],
                branch["oak_availability_event"],
            }
        ) == 3


def test_phase_8_event_slots_are_explicit_and_reference_reserved(repo_root: Path) -> None:
    source = repo_root / "constants/event_flags.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    events = [
        "EVENT_SILVER_BIRD_RELEASED",
        "EVENT_ARTICUNO_AVAILABLE",
        "EVENT_ZAPDOS_AVAILABLE",
        "EVENT_MOLTRES_AVAILABLE",
    ]

    _assert_contiguous(
        crystal,
        [
            "const EVENT_CAUGHT_PROJECT_MEW_SUBJECT",
            *(f"const {event}" for event in events),
            "const_next 2048",
            "DEF NUM_EVENTS EQU const_value",
        ],
    )
    assert all(not any(event in line for line in reference) for event in events)
    _assert_contiguous(
        reference,
        [
            "const_skip",
            "const_skip 3",
            "const_skip 3",
            "const_skip 4",
            "const_skip 4",
            "const_next 2048",
            "DEF NUM_EVENTS EQU const_value",
        ],
    )


def test_current_mt_moon_selectors_match_phase_8_branch_contract(repo_root: Path) -> None:
    contract = json.loads(
        (repo_root / "tests/contracts/legendary_branches.json").read_text()
    )["branches"]
    definitions = _definitions(
        _active_code(repo_root / "maps/MountMoon.asm", CRYSTAL_LEGENDS)
    )
    by_path = {
        "default": "MOUNT_MOON_RIVAL_DEFAULT_PARTY",
        "second": "MOUNT_MOON_RIVAL_SECOND_PARTY",
        "third": "MOUNT_MOON_RIVAL_THIRD_PARTY",
    }
    for branch in contract:
        assert definitions[by_path[branch["rival_path"]]] == branch["mt_moon_party"]


def test_silver_mt_moon_and_indigo_parties_remain_frozen(repo_root: Path) -> None:
    parties = [
        party
        for party in parse_trainer_parties(
            (repo_root / "data/trainers/parties.asm").read_text()
        )
        if party.group == "Rival2Group"
    ]
    assert len(parties) == 6
    bird_rows = {
        "ARTICUNO": ("60", "ARTICUNO", "WING_ATTACK", "ICE_BEAM", "MIND_READER", "BLIZZARD"),
        "ZAPDOS": ("60", "ZAPDOS", "DRILL_PECK", "THUNDERBOLT", "LIGHT_SCREEN", "THUNDER"),
        "MOLTRES": ("60", "MOLTRES", "WING_ATTACK", "FLAMETHROWER", "SAFEGUARD", "SKY_ATTACK"),
    }
    for party, species in zip(parties[:3], ("ARTICUNO", "ZAPDOS", "MOLTRES")):
        assert len(party.members) == 6
        assert party.members[-1] == bird_rows[species]

    expected_rematch = (
        ("45", "SNEASEL", "QUICK_ATTACK", "SCREECH", "FAINT_ATTACK", "FURY_CUTTER"),
        ("48", "CROBAT", "TOXIC", "BITE", "CONFUSE_RAY", "WING_ATTACK"),
        ("45", "MAGNETON", "THUNDER", "SONICBOOM", "THUNDER_WAVE", "SWIFT"),
        ("46", "GENGAR", "MEAN_LOOK", "CURSE", "SHADOW_BALL", "CONFUSE_RAY"),
        ("46", "ALAKAZAM", "RECOVER", "FUTURE_SIGHT", "PSYCHIC_M", "REFLECT"),
    )
    for party in parties[3:]:
        assert party.members == expected_rematch
        assert all(member[1] not in {"ARTICUNO", "ZAPDOS", "MOLTRES"} for member in party.members)
        assert max(int(member[0]) for member in party.members) == 48

    battle_music = _active_code(
        repo_root / "engine/battle/start_battle.asm", CRYSTAL_LEGENDS
    )
    _assert_contiguous(
        battle_music,
        [
            "ld a, [wOtherTrainerID]",
            "cp RIVAL2_2_ARTICUNO",
            "jr c, .done",
            "ld de, MUSIC_CHAMPION_BATTLE",
        ],
    )
