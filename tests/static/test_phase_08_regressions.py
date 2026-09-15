from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from tests.support.asm_conditions import active_lines
from tests.support.content_data import parse_trainer_parties
from tests.support.map_assets import (
    block_paths_for_maps,
    collision_at,
    parse_block_paths,
    parse_map_tilesets,
)
from tests.support.map_model import parse_map_dimensions


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


def _section(lines: list[str], start: str, end: str) -> list[str]:
    first = lines.index(start)
    return lines[first : lines.index(end, first + 1)]


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
    assert scenario["indigo"]["entrances"] == [
        {"x": 16, "y": 5, "facing": "UP"},
        {"x": 17, "y": 5, "facing": "UP"},
    ]
    assert scenario["indigo"]["weekdays"] == ["MONDAY", "WEDNESDAY"]
    assert scenario["indigo"]["excluded_weekday"] == "TUESDAY"
    assert scenario["dragons_den"]["start"] == {
        "x": 20,
        "y": 22,
        "facing": "DOWN",
    }
    assert scenario["dragons_den"]["weekdays"] == ["TUESDAY", "THURSDAY"]
    assert scenario["dragons_den"]["excluded_weekday"] == "MONDAY"

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
            "const EVENT_HELPED_ERIKA_CLEAN_CELADON_POND",
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
            "const_skip 24",
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


def test_silver_mt_moon_and_indigo_parties_match_phase_12(repo_root: Path) -> None:
    parties = [
        party
        for party in parse_trainer_parties(
            (repo_root / "data/trainers/parties.asm").read_text()
        )
        if party.group == "Rival2Group"
    ]
    assert len(parties) == 6
    bird_rows = {
        "ARTICUNO": ("50", "ARTICUNO", "WING_ATTACK", "ICE_BEAM", "REFLECT", "AGILITY"),
        "ZAPDOS": ("50", "ZAPDOS", "DRILL_PECK", "THUNDERBOLT", "LIGHT_SCREEN", "THUNDER_WAVE"),
        "MOLTRES": ("50", "MOLTRES", "WING_ATTACK", "FLAMETHROWER", "SAFEGUARD", "AGILITY"),
    }
    for party, species in zip(parties[:3], ("ARTICUNO", "ZAPDOS", "MOLTRES")):
        assert len(party.members) == 6
        assert party.members[-1] == bird_rows[species]

    expected_rematch = (
        ('48', 'SNEASEL', 'STRENGTH', 'SCREECH', 'FAINT_ATTACK', 'ICY_WIND'),
        ('48', 'MAGNETON', 'THUNDER', 'SONICBOOM', 'THUNDER_WAVE', 'SWIFT'),
        ('49', 'GENGAR', 'MEAN_LOOK', 'CURSE', 'SHADOW_BALL', 'CONFUSE_RAY'),
        ('49', 'ALAKAZAM', 'RECOVER', 'FUTURE_SIGHT', 'PSYCHIC_M', 'REFLECT'),
        ('50', 'URSARING', 'FAINT_ATTACK', 'REST', 'SLASH', 'SNORE'),
        ('52', 'CROBAT', 'TOXIC', 'BITE', 'CONFUSE_RAY', 'WING_ATTACK'),
    )
    for party in parties[3:]:
        assert party.members == expected_rematch
        assert all(member[1] not in {"ARTICUNO", "ZAPDOS", "MOLTRES"} for member in party.members)
        assert max(int(member[0]) for member in party.members) == 52

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


def test_mt_moon_victory_buffers_the_returned_bird_and_schedules_elm(
    repo_root: Path,
) -> None:
    crystal = _active_code(repo_root / "maps/MountMoon.asm", CRYSTAL_LEGENDS)
    reference = _active_code(repo_root / "maps/MountMoon.asm", REFERENCE)
    finish = _section(crystal, ".FinishBattle:", "MountMoonRivalMovementBefore:")

    _assert_contiguous(
        finish,
        [
            "checkevent MOUNT_MOON_RIVAL_SECOND_STARTER_EVENT",
            "iftrue .BufferSecondBird",
            "checkevent MOUNT_MOON_RIVAL_THIRD_STARTER_EVENT",
            "iftrue .BufferThirdBird",
            "getmonname STRING_BUFFER_3, MOLTRES",
            "sjump .BirdBuffered",
        ],
    )
    _assert_contiguous(
        finish,
        [
            ".BufferSecondBird:",
            "getmonname STRING_BUFFER_3, ARTICUNO",
            "sjump .BirdBuffered",
            ".BufferThirdBird:",
            "getmonname STRING_BUFFER_3, ZAPDOS",
            ".BirdBuffered:",
        ],
    )
    _assert_contiguous(
        finish,
        [
            "setscene SCENE_MOUNTMOON_NOOP",
            "setevent EVENT_BEAT_RIVAL_IN_MT_MOON",
            "setmapscene ELMS_LAB, SCENE_ELMSLAB_SILVER_RETURNS_BIRD",
            "playmapmusic",
            "end",
        ],
    )
    assert not any("EVENT_SILVER_BIRD_RELEASED" in line for line in finish)
    assert not any("_AVAILABLE" in line for line in finish)
    assert not any("SCENE_ELMSLAB_SILVER_RETURNS_BIRD" in line for line in reference)


def test_mt_moon_uses_the_approved_custom_post_victory_dialogue_only(
    repo_root: Path,
) -> None:
    crystal = _active_code(repo_root / "maps/MountMoon.asm", CRYSTAL_LEGENDS)
    reference = _active_code(repo_root / "maps/MountMoon.asm", REFERENCE)
    custom_text = _section(crystal, "MountMoonRivalTextAfter:", "MountMoonRivalTextLoss:")
    reference_text = _section(reference, "MountMoonRivalTextAfter:", "MountMoonRivalTextLoss:")

    _assert_contiguous(
        custom_text,
        [
            'para "Even @"',
            "text_ram wStringBuffer3",
            'text "…"',
            'line "It chose to stand"',
            'cont "with me."',
        ],
    )
    for row in (
        'para "But that doesn\'t"',
        'para "I took it from"',
        'line "PROF.ELM."',
        'para "Getting stronger"',
        'cont "right."',
        'cont "NEW BARK TOWN."',
        'line "this right."',
    ):
        assert row in custom_text
    assert 'para "I admit it. But"' not in custom_text
    assert 'para "I admit it. But"' in reference_text
    for label in ("MountMoonRivalTextBefore:", "MountMoonRivalTextWin:", "MountMoonRivalTextLoss:"):
        crystal_section = _section(
            crystal,
            label,
            {
                "MountMoonRivalTextBefore:": "MountMoonRivalTextWin:",
                "MountMoonRivalTextWin:": "MountMoonRivalTextAfter:",
                "MountMoonRivalTextLoss:": "MountMoon_MapEvents:",
            }[label],
        )
        reference_section = _section(
            reference,
            label,
            {
                "MountMoonRivalTextBefore:": "MountMoonRivalTextWin:",
                "MountMoonRivalTextWin:": "MountMoonRivalTextAfter:",
                "MountMoonRivalTextLoss:": "MountMoon_MapEvents:",
            }[label],
        )
        assert crystal_section == reference_section


def test_elm_scene_four_is_custom_named_without_adding_a_scene(repo_root: Path) -> None:
    crystal = _active_code(repo_root / "maps/ElmsLab.asm", CRYSTAL_LEGENDS)
    reference = _active_code(repo_root / "maps/ElmsLab.asm", REFERENCE)
    crystal_scenes = _section(crystal, "ElmsLab_MapScripts:", "ElmsLabMeetElmScene:")
    reference_scenes = _section(reference, "ElmsLab_MapScripts:", "ElmsLabMeetElmScene:")
    assert (
        "scene_script ElmsLabSilverReturnsBirdScene, SCENE_ELMSLAB_SILVER_RETURNS_BIRD"
        in crystal_scenes
    )
    assert "scene_script ElmsLabNoop4Scene,   SCENE_ELMSLAB_UNUSED" in reference_scenes
    assert sum(line.startswith("scene_script ") for line in crystal_scenes) == 6
    assert sum(line.startswith("scene_script ") for line in reference_scenes) == 6


def test_elm_release_entry_objects_and_bank_include_are_custom_only(
    repo_root: Path,
) -> None:
    crystal = _active_code(repo_root / "maps/ElmsLab.asm", CRYSTAL_LEGENDS)
    reference = _active_code(repo_root / "maps/ElmsLab.asm", REFERENCE)
    object_start = crystal.index("def_object_events")
    crystal_objects = crystal[object_start:]
    reference_objects = reference[reference.index("def_object_events") :]

    _assert_contiguous(
        crystal,
        [
            "ElmsLabSilverReturnsBirdScene:",
            "sdefer ElmsLabSilverReturnsBirdScript",
            "end",
        ],
    )
    _assert_contiguous(
        crystal,
        [
            "ElmsLabSilverReturnsBirdScript:",
            "appear ELMSLAB_SILVER",
            "appear ELMSLAB_SILVERS_BIRD",
            "setevent EVENT_INITIALIZED_EVENTS",
            "turnobject ELMSLAB_SILVER, DOWN",
            "applymovement PLAYER, ElmsLabSilverReturnPlayerMovement",
            "farsjump ElmsLabSilverArcScript",
        ],
    )
    assert "const ELMSLAB_SILVER" in crystal
    assert "const ELMSLAB_SILVERS_BIRD" in crystal
    assert any(
        line.startswith(
            "object_event  4,  3, SPRITE_RIVAL, SPRITEMOVEDATA_STANDING_DOWN"
        )
        and line.endswith("ObjectEvent, EVENT_INITIALIZED_EVENTS")
        for line in crystal_objects
    )
    assert any(
        line.startswith(
            "object_event  5,  3, SPRITE_BIRD, SPRITEMOVEDATA_STANDING_DOWN"
        )
        and line.endswith("ObjectEvent, EVENT_INITIALIZED_EVENTS")
        for line in crystal_objects
    )
    assert not any("ELMSLAB_SILVER" in line for line in reference)
    assert len(crystal_objects) == len(reference_objects) + 2

    includes = _active_code(repo_root / "data/maps/scripts.asm", CRYSTAL_LEGENDS)
    reference_includes = _active_code(repo_root / "data/maps/scripts.asm", REFERENCE)
    assert 'INCLUDE "maps/ElmsLabSilverArc.asm"' in includes
    assert 'INCLUDE "maps/ElmsLabSilverArc.asm"' not in reference_includes


def test_release_script_has_approved_choreography_branching_and_event_order(
    repo_root: Path,
) -> None:
    lines = _active_code(repo_root / "maps/ElmsLabSilverArc.asm", CRYSTAL_LEGENDS)
    core = _section(
        lines, "ElmsLabSilverArcScript:", "ElmsLabSilverBufferReturnedBird:"
    )
    assert "appear ELMSLAB_SILVER" not in core
    assert "appear ELMSLAB_SILVERS_BIRD" not in core
    expected_order = [
        "writetext ElmsLabSilverArrivalText",
        "applymovement ELMSLAB_SILVER, ElmsLabSilverHandoffMovement",
        "writetext ElmsLabSilverReturnsBirdText",
        "writetext ElmsLabElmReleaseDecisionText",
        "applymovement ELMSLAB_SILVER, ElmsLabSilverFacesBirdMovement",
        "writetext ElmsLabElmSetsBirdFreeText",
        "scall ElmsLabSilverCryReturnedBird",
        "applymovement ELMSLAB_SILVERS_BIRD, ElmsLabSilverBirdExitMovement",
        "disappear ELMSLAB_SILVERS_BIRD",
        "scall ElmsLabSilverSetAvailability",
        "setevent EVENT_SILVER_BIRD_RELEASED",
        "writetext ElmsLabSilverFarewellText",
        "applymovement ELMSLAB_SILVER, ElmsLabSilverExitMovement",
        "disappear ELMSLAB_SILVER",
        "setscene SCENE_ELMSLAB_NOOP",
    ]
    positions = [core.index(row) for row in expected_order]
    assert positions == sorted(positions)

    buffer = _section(
        lines, "ElmsLabSilverBufferReturnedBird:", "ElmsLabSilverCryReturnedBird:"
    )
    cry = _section(
        lines, "ElmsLabSilverCryReturnedBird:", "ElmsLabSilverSetAvailability:"
    )
    availability = _section(
        lines, "ElmsLabSilverSetAvailability:", "ElmsLabSilverHandoffMovement:"
    )
    for helper, tails in (
        (buffer, ("MOLTRES", "ARTICUNO", "ZAPDOS")),
        (cry, ("MOLTRES", "ARTICUNO", "ZAPDOS")),
        (
            availability,
            (
                "EVENT_MOLTRES_AVAILABLE",
                "EVENT_ARTICUNO_AVAILABLE",
                "EVENT_ZAPDOS_AVAILABLE",
            ),
        ),
    ):
        assert helper[:4] == [
            helper[0],
            "checkevent EVENT_GOT_ZAPDOS_FROM_ELM",
            "iftrue .Articuno",
            "checkevent EVENT_GOT_MOLTRES_FROM_ELM",
        ]
        assert all(any(tail in row for row in helper) for tail in tails)
    assert not any("PARTY" in row or "POKEDEX" in row for row in lines)

    bird_movement = _section(
        lines, "ElmsLabSilverBirdExitMovement:", "ElmsLabSilverExitMovement:"
    )
    assert bird_movement.count("turn_head LEFT") == 1
    assert bird_movement.count("turn_head DOWN") == 1
    assert bird_movement.count("step_sleep 8") == 4
    assert bird_movement.count("step DOWN") == 8
    silver_movement = _section(
        lines, "ElmsLabSilverExitMovement:", "ElmsLabSilverArrivalText:"
    )
    assert silver_movement.count("step RIGHT") == 1
    assert silver_movement.count("step DOWN") == 8


def test_release_dialogue_matches_the_approved_story_beats(repo_root: Path) -> None:
    lines = _active_code(repo_root / "maps/ElmsLabSilverArc.asm", CRYSTAL_LEGENDS)
    _assert_contiguous(
        lines,
        [
            "ElmsLabSilverFarewellText:",
            'text "<RIVAL>: …"',
            'para "@"',
            "text_ram wStringBuffer3",
            'text " looked"',
            'line "back."',
        ],
    )
    text = "\n".join(lines[lines.index("ElmsLabSilverArrivalText:") :])
    for expected in (
        'text "<RIVAL>: …You"',
        'text "<RIVAL>: PROF.ELM…"',
        'text "ELM: …<RIVAL>."',
        'para "I brought"',
        'para "It fought beside"',
        'para "I was the one who"',
        'para "But I won\'t decide"',
        'para "It should choose"',
        'text "ELM: Go, @"',
        'text "<RIVAL>: …"',
        'text " looked"',
        'para "I don\'t regret"',
        'para "But this was the"',
        'para "I\'m moving on with"',
        'para "…See you, <PLAYER>."',
    ):
        assert expected in text
    assert text.count("text_ram wStringBuffer3") == 6
    assert "SILVER" not in text
    assert "where you can" not in text
    assert "ElmText_CallYou" not in text


def test_elm_release_staging_and_exit_paths_are_walkable(repo_root: Path) -> None:
    dimensions = parse_map_dimensions(
        (repo_root / "constants/map_constants.asm").read_text()
    )
    block_paths = block_paths_for_maps(
        dimensions,
        parse_block_paths((repo_root / "data/maps/blocks.asm").read_text()),
    )
    tilesets = parse_map_tilesets((repo_root / "data/maps/maps.asm").read_text())
    traversed = (
        *((4, y) for y in range(2, 11)),
        *((5, y) for y in range(3, 12)),
    )
    for coordinate in traversed:
        expected = "WARP_CARPET_DOWN" if coordinate == (5, 11) else "FLOOR"
        assert (
            collision_at(
                repo_root,
                "ELMS_LAB",
                coordinate,
                dimensions,
                block_paths,
                tilesets,
            )
            == expected
        )


def test_post_release_gates_are_custom_only_and_keep_stock_text(
    repo_root: Path,
) -> None:
    indigo_custom = _active_code(
        repo_root / "maps/IndigoPlateauPokecenter1F.asm", CRYSTAL_LEGENDS
    )
    indigo_reference = _active_code(
        repo_root / "maps/IndigoPlateauPokecenter1F.asm", REFERENCE
    )
    for label, end in (
        ("PlateauRivalBattle1:", "PlateauRivalBattle2:"),
        ("PlateauRivalBattle2:", "PlateauRivalBattleCommon:"),
    ):
        custom = _section(indigo_custom, label, end)
        reference = _section(indigo_reference, label, end)
        _assert_contiguous(
            custom,
            [
                "checkevent EVENT_BEAT_RIVAL_IN_MT_MOON",
                "iffalse PlateauRivalScriptDone",
                "checkevent EVENT_SILVER_BIRD_RELEASED",
                "iffalse PlateauRivalScriptDone",
            ],
        )
        assert not any("EVENT_SILVER_BIRD_RELEASED" in row for row in reference)
    assert _section(
        indigo_custom, "PlateauRivalText1:", "TeleportGuyText1:"
    ) == _section(indigo_reference, "PlateauRivalText1:", "TeleportGuyText1:")

    den_custom = _active_code(repo_root / "maps/DragonsDenB1F.asm", CRYSTAL_LEGENDS)
    den_reference = _active_code(repo_root / "maps/DragonsDenB1F.asm", REFERENCE)
    callback = _section(
        den_custom,
        "DragonsDenB1FCheckRivalCallback:",
        "DragonsDenB1F_ClairScene:",
    )
    _assert_contiguous(
        callback,
        [
            ".CheckDay:",
            "checkevent EVENT_SILVER_BIRD_RELEASED",
            "iffalse .HideRival",
            "readvar VAR_WEEKDAY",
        ],
    )
    assert not any(
        "EVENT_SILVER_BIRD_RELEASED" in row
        for row in _section(
            den_reference,
            "DragonsDenB1FCheckRivalCallback:",
            "DragonsDenB1F_ClairScene:",
        )
    )
    assert _section(
        den_custom, "RivalText_Training1:", "CooltrainermDarinSeenText:"
    ) == _section(
        den_reference, "RivalText_Training1:", "CooltrainermDarinSeenText:"
    )

    shrine_custom = _active_code(repo_root / "maps/DragonShrine.asm", CRYSTAL_LEGENDS)
    shrine_reference = _active_code(repo_root / "maps/DragonShrine.asm", REFERENCE)
    elder = _section(
        shrine_custom, "DragonShrineElder1Script:", "DragonShrineElder2Script:"
    )
    _assert_contiguous(
        elder,
        [
            "checkevent EVENT_BEAT_RIVAL_IN_MT_MOON",
            "iffalse .ClairsGrandfather",
            "checkevent EVENT_SILVER_BIRD_RELEASED",
            "iftrue .BeatRivalInMtMoon",
            ".ClairsGrandfather:",
        ],
    )
    assert not any(
        "EVENT_SILVER_BIRD_RELEASED" in row
        for row in _section(
            shrine_reference,
            "DragonShrineElder1Script:",
            "DragonShrineElder2Script:",
        )
    )
    assert _section(
        shrine_custom,
        "DragonShrineClairsGrandfatherText:",
        "DragonShrineWrongAnswerText1:",
    ) == _section(
        shrine_reference,
        "DragonShrineClairsGrandfatherText:",
        "DragonShrineWrongAnswerText1:",
    )
