from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.asm_conditions import active_lines
from tests.support.map_assets import (
    block_paths_for_maps,
    collision_at,
    parse_block_paths,
    parse_map_tilesets,
)
from tests.support.map_model import parse_map_dimensions


pytestmark = [pytest.mark.static, pytest.mark.phase7]


CRYSTAL_LEGENDS = {"_CRYSTAL11", "_CRYSTALLEGENDS"}
REFERENCE = {"_CRYSTAL11"}


def test_project_mew_runtime_scenario_contract(repo_root: Path) -> None:
    scenario = json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_07_project_mew.json").read_text()
    )

    assert scenario["scenario_id"] == "phase-07-project-mew"
    assert scenario["rom"] == "crystallegends.gbc"
    assert scenario["symbols"] == "crystallegends.sym"
    assert scenario["save_fixture"] == "bedroom_initialized.sav"
    assert scenario["max_frames_per_step"] == 60000
    assert scenario["annex"] == {
        "map": "RADIO_TOWER_TRANSMITTER_ANNEX",
        "entry_start": {"x": 4, "y": 6, "facing": "UP"},
        "terminal_start": {"x": 6, "y": 6, "facing": "UP"},
        "subject_start": {"x": 4, "y": 3, "facing": "UP"},
        "exit_start": {"x": 4, "y": 6, "facing": "DOWN"},
    }
    assert scenario["radio_tower_5f"] == {
        "map": "RADIO_TOWER_5F",
        "boss_start": {"x": 16, "y": 6, "facing": "UP"},
        "resume_start": {"x": 16, "y": 6, "facing": "UP"},
    }
    assert scenario["events"] == {
        "boss": "EVENT_BEAT_ROCKET_EXECUTIVEM_1",
        "data_sent": "EVENT_PROJECT_MEW_DATA_SENT",
        "resolved": "EVENT_PROJECT_MEW_RESOLVED",
        "transformed": "EVENT_PROJECT_MEW_TRANSFORMED",
        "caught": "EVENT_CAUGHT_PROJECT_MEW_SUBJECT",
    }
    assert scenario["outcomes"] == [
        {"id": "reverse", "species": "MEW", "transformed": False},
        {"id": "stabilize", "species": "MEWTWO", "transformed": True},
    ]


def _active_code(path: Path, definitions: set[str]) -> list[str]:
    return [
        line.text.split(";", 1)[0].strip()
        for line in active_lines(path.read_text(), definitions)
        if line.text.split(";", 1)[0].strip()
    ]


def _section(lines: list[str], start: str, end: str) -> list[str]:
    first = lines.index(start)
    return lines[first : lines.index(end, first + 1)]


def _assert_contiguous(lines: list[str], expected: list[str]) -> None:
    width = len(expected)
    assert any(lines[index : index + width] == expected for index in range(len(lines)))


def test_slowpoke_well_foreshadows_research_without_naming_subject(
    repo_root: Path,
) -> None:
    source = repo_root / "maps/SlowpokeWellB1F.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    story = _section(crystal, "GruntM29AfterBattleText:", "GruntM1SeenText:")
    story += _section(crystal, "GruntF1AfterBattleText:", "SlowpokeWellB1FSlowpokeWithMailText:")

    assert 'text "Sure, we\'ve been"' in story
    assert 'para "The lab paid extra"' in story
    assert 'para "The science crew"' in story
    assert 'line "regrowth data."' in story
    assert all("MEW" not in line for line in story)
    assert 'para "The lab paid extra"' not in reference
    assert 'para "The science crew"' not in reference


def test_lake_of_rage_frames_forced_evolution_as_proof_without_replacing_it(
    repo_root: Path,
) -> None:
    source = repo_root / "maps/LakeOfRage.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    story = _section(
        crystal, "LakeOfRageLanceRadioSignalText:", "LakeOfRageLanceRefusedText:"
    )

    for row in (
        'para "are being forced"',
        'line "to evolve."',
        'para "A mysterious radio"',
        'para "from MAHOGANY is"',
        'para "The red GYARADOS"',
        'para "signal could force"',
        'cont "far beyond this."',
    ):
        assert row in story
    assert 'para "The red GYARADOS"' not in reference
    assert "loadwildmon GYARADOS, 30" in crystal
    assert "giveitem RED_SCALE" in crystal


def test_mahogany_reveal_uses_existing_people_office_lab_and_transmitter(
    repo_root: Path,
) -> None:
    b3f_source = repo_root / "maps/TeamRocketBaseB3F.asm"
    b2f_source = repo_root / "maps/TeamRocketBaseB2F.asm"
    b3f = _active_code(b3f_source, CRYSTAL_LEGENDS)
    b3f_reference = _active_code(b3f_source, REFERENCE)
    b2f = _active_code(b2f_source, CRYSTAL_LEGENDS)
    b2f_reference = _active_code(b2f_source, REFERENCE)

    for row in (
        "TrainerScientistRoss:",
        "TrainerScientistMitch:",
        'para "The LAKE trial was"',
        'para "The GOLDENROD rig"',
        "TeamRocketBaseB3FProjectMewDossierScript:",
        "TeamRocketBaseB3FProjectMewTestDataScript:",
        'text "PROJECT MEW"',
        'para "SUBJECT: one MEW."',
        'cont "captive."',
        'line "near CERULEAN."',
        'text "LAKE TRIAL: PROOF"',
        "bg_event  8,  2, BGEVENT_READ, TeamRocketBaseB3FProjectMewDossierScript",
        "bg_event  9,  2, BGEVENT_READ, TeamRocketBaseB3FProjectMewDossierScript",
        "bg_event 20,  6, BGEVENT_READ, TeamRocketBaseB3FProjectMewTestDataScript",
        "bg_event 24,  6, BGEVENT_READ, TeamRocketBaseB3FProjectMewTestDataScript",
        "bg_event 20, 10, BGEVENT_READ, TeamRocketBaseB3FProjectMewTestDataScript",
        "bg_event 22, 10, BGEVENT_READ, TeamRocketBaseB3FProjectMewTestDataScript",
    ):
        assert row in b3f
    assert 'para "The PROJECT MEW"' in b3f

    for row in (
        "TeamRocketBaseB2FTransmitterScript:",
        'para "SUBJECT TRANSFER:"',
        'para "PROJECT MEW data"',
        'cont "GOLDENROD TOWER."',
    ):
        assert row in b2f

    for token in (
        "ProjectMewDossier",
        "ProjectMewTestData",
        'text "PROJECT MEW"',
        'para "The PROJECT MEW"',
    ):
        assert not any(token in line for line in b3f_reference)
    for token in ('para "SUBJECT TRANSFER:"', 'para "PROJECT MEW data"'):
        assert token not in b2f_reference


def test_radio_tower_scientist_names_project_mew_signal_in_custom_build(
    repo_root: Path,
) -> None:
    source = repo_root / "maps/RadioTower3F.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    crystal_dialogue = _section(
        crystal, "ScientistMarcAfterBattleText:", "RadioTower3FCardKeySlotText:"
    )
    reference_dialogue = _section(
        reference, "ScientistMarcAfterBattleText:", "RadioTower3FCardKeySlotText:"
    )

    _assert_contiguous(
        crystal_dialogue,
        [
            'text "Bwahahaha…"',
            'para "I can transmit the"',
            'line "signal PROJECT MEW"',
            'cont "needs from here."',
            "done",
        ],
    )
    _assert_contiguous(
        reference_dialogue,
        [
            'text "Bwahahaha…"',
            'para "I can transmit as"',
            'line "strong a signal as"',
            'cont "I need from here."',
            "done",
        ],
    )


def test_stock_rocket_story_progression_operations_remain_present(
    repo_root: Path,
) -> None:
    lake = _active_code(repo_root / "maps/LakeOfRage.asm", CRYSTAL_LEGENDS)
    b2f = _active_code(repo_root / "maps/TeamRocketBaseB2F.asm", CRYSTAL_LEGENDS)
    radio = _active_code(repo_root / "maps/RadioTower5F.asm", CRYSTAL_LEGENDS)

    for row in (
        "loadwildmon GYARADOS, 30",
        "giveitem RED_SCALE",
        "setmapscene MAHOGANY_MART_1F, SCENE_MAHOGANYMART1F_LANCE_UNCOVERS_STAIRS",
    ):
        assert row in lake
    for row in (
        "setevent EVENT_CLEARED_ROCKET_HIDEOUT",
        "clearflag ENGINE_ROCKET_SIGNAL_ON_CH20",
        "setevent EVENT_MAHOGANY_TOWN_POKEFAN_M_BLOCKS_GYM",
    ):
        assert row in b2f
    for row in (
        "verbosegiveitem BASEMENT_KEY",
        "verbosegiveitem CLEAR_BELL",
        "setevent EVENT_CLEARED_RADIO_TOWER",
        "setevent EVENT_BLACKTHORN_CITY_SUPER_NERD_BLOCKS_GYM",
        "setmapscene ECRUTEAK_TIN_TOWER_ENTRANCE, SCENE_ECRUTEAKTINTOWERENTRANCE_SAGE_BLOCKS",
        "setevent EVENT_TEAM_ROCKET_DISBANDED",
    ):
        assert row in radio


def test_project_mew_event_slots_are_explicit_and_reference_reserved(
    repo_root: Path,
) -> None:
    source = repo_root / "constants/event_flags.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    events = [
        "EVENT_PROJECT_MEW_DATA_SENT",
        "EVENT_PROJECT_MEW_RESOLVED",
        "EVENT_PROJECT_MEW_TRANSFORMED",
        "EVENT_CAUGHT_PROJECT_MEW_SUBJECT",
    ]

    _assert_contiguous(
        crystal,
        [
            "const EVENT_GOT_AERODACTYL_FROM_ALPH",
            *(f"const {event}" for event in events),
            "const EVENT_SILVER_BIRD_RELEASED",
            "const EVENT_ARTICUNO_AVAILABLE",
            "const EVENT_ZAPDOS_AVAILABLE",
            "const EVENT_MOLTRES_AVAILABLE",
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


def test_annex_scene_state_uses_custom_reserved_byte_and_map_scene_entry(
    repo_root: Path,
) -> None:
    custom_wram = _active_code(repo_root / "ram/wram.asm", CRYSTAL_LEGENDS)
    reference_wram = _active_code(repo_root / "ram/wram.asm", REFERENCE)
    custom_scenes = _active_code(repo_root / "data/maps/scenes.asm", CRYSTAL_LEGENDS)
    reference_scenes = _active_code(repo_root / "data/maps/scenes.asm", REFERENCE)

    _assert_contiguous(
        custom_wram,
        [
            "wMobileBattleRoomSceneID::                        db",
            "wRadioTowerTransmitterAnnexSceneID::               db",
            "ds 48",
        ],
    )
    _assert_contiguous(
        reference_wram,
        [
            "wMobileBattleRoomSceneID::                        db",
            "ds 49",
        ],
    )
    entry = (
        "scene_var RADIO_TOWER_TRANSMITTER_ANNEX,                "
        "wRadioTowerTransmitterAnnexSceneID"
    )
    assert entry in custom_scenes
    assert entry not in reference_scenes


def test_annex_map_and_subject_sprites_append_only_to_custom_tables(
    repo_root: Path,
) -> None:
    map_constants = repo_root / "constants/map_constants.asm"
    map_table = repo_root / "data/maps/maps.asm"
    sprite_constants = repo_root / "constants/sprite_constants.asm"
    sprite_table = repo_root / "data/sprites/sprite_mons.asm"
    crystal_maps = _active_code(map_constants, CRYSTAL_LEGENDS)
    reference_maps = _active_code(map_constants, REFERENCE)
    crystal_table = _active_code(map_table, CRYSTAL_LEGENDS)
    reference_table = _active_code(map_table, REFERENCE)
    crystal_sprites = _active_code(sprite_constants, CRYSTAL_LEGENDS)
    reference_sprites = _active_code(sprite_constants, REFERENCE)
    crystal_mons = _active_code(sprite_table, CRYSTAL_LEGENDS)
    reference_mons = _active_code(sprite_table, REFERENCE)

    _assert_contiguous(
        crystal_maps,
        [
            "map_const VICTORY_ROAD,                                10, 36",
            "map_const RADIO_TOWER_TRANSMITTER_ANNEX,                 5,  4",
            "DEF SCENE_RADIOTOWERTRANSMITTERANNEX_LOCK_ENTRY EQU 0",
            "DEF SCENE_RADIOTOWERTRANSMITTERANNEX_NOOP       EQU 1",
            "EXPORT SCENE_RADIOTOWERTRANSMITTERANNEX_LOCK_ENTRY",
            "EXPORT SCENE_RADIOTOWERTRANSMITTERANNEX_NOOP",
            "endgroup",
        ],
    )
    assert not any("RADIO_TOWER_TRANSMITTER_ANNEX" in row for row in reference_maps)
    assert any(row.startswith("map RadioTowerTransmitterAnnex,") for row in crystal_table)
    assert not any(row.startswith("map RadioTowerTransmitterAnnex,") for row in reference_table)
    _assert_contiguous(
        crystal_sprites,
        [
            "const SPRITE_AERODACTYL",
            "const SPRITE_MEW",
            "const SPRITE_MEWTWO",
            "DEF NUM_POKEMON_SPRITES EQU const_value - SPRITE_POKEMON",
        ],
    )
    _assert_contiguous(
        crystal_sprites,
        [
            "const SPRITE_JANINE_IMPERSONATOR",
            "const SPRITE_PROJECT_MEW_SUBJECT",
        ],
    )
    _assert_contiguous(
        crystal_mons,
        [
            "db AERODACTYL",
            "db MEW",
            "db MEWTWO",
            "assert_table_length NUM_POKEMON_SPRITES",
        ],
    )
    assert not any("SPRITE_MEW" in row for row in reference_sprites)
    assert "db MEW" not in reference_mons
    assert "db MEWTWO" not in reference_mons


def test_annex_asset_has_southern_controls_continuous_glass_and_sealed_boundary(
    repo_root: Path,
) -> None:
    dimensions = parse_map_dimensions(
        (repo_root / "constants/map_constants.asm").read_text()
    )
    block_paths = block_paths_for_maps(
        dimensions,
        parse_block_paths((repo_root / "data/maps/blocks.asm").read_text()),
    )
    tilesets = parse_map_tilesets((repo_root / "data/maps/maps.asm").read_text())
    name = "RADIO_TOWER_TRANSMITTER_ANNEX"
    blocks = (repo_root / block_paths[name]).read_bytes()

    assert (dimensions[name].width_blocks, dimensions[name].height_blocks) == (5, 4)
    assert blocks == bytes.fromhex(
        "02 02 02 02 02 15 15 15 15 15 01 12 01 12 01 40 40 07 40 40"
    )
    assert collision_at(
        repo_root, name, (2, 5), dimensions, block_paths, tilesets
    ) == "PC"
    assert collision_at(
        repo_root, name, (6, 5), dimensions, block_paths, tilesets
    ) == "PC"
    assert collision_at(
        repo_root, name, (4, 3), dimensions, block_paths, tilesets
    ) == "WALL"
    assert collision_at(
        repo_root, name, (4, 6), dimensions, block_paths, tilesets
    ) == "FLOOR"
    assert collision_at(
        repo_root, name, (4, 7), dimensions, block_paths, tilesets
    ) == "WARP_CARPET_DOWN"
    collision_rows = (repo_root / "data/tilesets/radio_tower_collision.asm").read_text()
    assert "tilecoll FLOOR, FLOOR, WARP_CARPET_DOWN, WARP_CARPET_DOWN ; 07" in collision_rows
    assert "tilecoll FLOOR, FLOOR, WALL, WALL ; 40" in collision_rows
    tilesets_source = (repo_root / "gfx/tilesets.asm").read_text()
    custom_tilesets = _active_code(repo_root / "gfx/tilesets.asm", CRYSTAL_LEGENDS)
    reference_tilesets = _active_code(repo_root / "gfx/tilesets.asm", REFERENCE)
    _assert_contiguous(
        custom_tilesets,
        [
            "TilesetRadioTowerBlock40::",
            "db $01, $01, $01, $01",
            "db $01, $01, $01, $01",
            "db $39, $39, $39, $39",
            "db $39, $39, $39, $39",
        ],
    )
    assert "TilesetRadioTowerBlock40::" in tilesets_source
    assert "TilesetRadioTowerBlock40::" not in reference_tilesets


def test_final_executive_sends_data_before_battle_and_opens_existing_flag_gate(
    repo_root: Path,
) -> None:
    source = repo_root / "maps/RadioTower5F.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    boss = _section(crystal, "RadioTower5FRocketBossScript:", "RadioTower5FDirectorCleanupScript:")
    dialogue = _section(
        crystal, "RadioTower5FRocketBossBeforeText:", "RadioTower5FRocketBossWinText:"
    )
    after_dialogue = _section(
        crystal,
        "RadioTower5FRocketBossAfterText:",
        "RadioTower5FProjectMewEntranceOpenedText:",
    )
    entrance_dialogue = _section(
        crystal,
        "RadioTower5FProjectMewEntranceOpenedText:",
        "RadioTower5FDirectorThankYouText:",
    )
    reference_after_dialogue = _section(
        reference,
        "RadioTower5FRocketBossAfterText:",
        "RadioTower5FDirectorThankYouText:",
    )

    assert boss.index("setevent EVENT_PROJECT_MEW_DATA_SENT") < boss.index("startbattle")
    _assert_contiguous(
        boss,
        [
            "setevent EVENT_BEAT_ROCKET_EXECUTIVEM_1",
            "playsound SFX_ENTER_DOOR",
            "changeblock 14, 0, $1d",
            "refreshmap",
        ],
    )
    assert "setscene SCENE_RADIOTOWER5F_PROJECT_MEW" in boss
    _assert_contiguous(
        boss,
        [
            "setmapscene RADIO_TOWER_TRANSMITTER_ANNEX, SCENE_RADIOTOWERTRANSMITTERANNEX_LOCK_ENTRY",
            "applymovement PLAYER, RadioTower5FPlayerEntersAnnexMovement",
            "warpfacing UP, RADIO_TOWER_TRANSMITTER_ANNEX, 4, 6",
            "end",
        ],
    )
    callback = _section(
        crystal,
        "RadioTower5FProjectMewEntranceCallback:",
        "RadioTower5FResumeProjectMewScript:",
    )
    assert "checkevent EVENT_BEAT_ROCKET_EXECUTIVEM_1" in callback
    assert "changeblock 14, 0, $1d" in callback
    assert "changeblock 14, 0, $02" in callback
    resume = _section(
        crystal,
        "RadioTower5FResumeProjectMewScript:",
        "RadioTower5FNoop3Scene:",
    )
    _assert_contiguous(
        resume,
        [
            "checkevent EVENT_PROJECT_MEW_RESOLVED",
            "iffalse .ReturnToAnnex",
            "applymovement PLAYER, RadioTower5FPlayerReturnsFromAnnexMovement",
            "sjump RadioTower5FDirectorCleanupScript",
            ".ReturnToAnnex:",
            "setmapscene RADIO_TOWER_TRANSMITTER_ANNEX, SCENE_RADIOTOWERTRANSMITTERANNEX_LOCK_ENTRY",
            "warpfacing UP, RADIO_TOWER_TRANSMITTER_ANNEX, 4, 6",
            "end",
        ],
    )
    assert "warp RADIO_TOWER_TRANSMITTER_ANNEX, 4, 6" not in crystal
    assert "EVENT_PROJECT_MEW_ACCESS" not in "\n".join(crystal)
    _assert_contiguous(
        dialogue,
        [
            'para "We seized this"',
            'line "RADIO TOWER for"',
            'cont "PROJECT MEW."',
            'para "Its signal will"',
            'line "finish the captive"',
            'cont "subject\'s change!"',
            'para "Then we\'ll declare"',
            'line "TEAM ROCKET\'s"',
            'cont "comeback."',
            'para "That should bring"',
            'line "our boss GIOVANNI"',
            'para "back from his solo"',
            'line "training."',
            'para "We are going to"',
            'line "regain our former"',
            'cont "glory."',
            'para "…"',
            'para "Too late! The data"',
            'line "just reached"',
            'cont "GIOVANNI."',
            'para "I won\'t allow you"',
        ],
    )
    assert not any('para "already reached"' in row for row in dialogue)
    _assert_contiguous(
        after_dialogue,
        [
            'para "disband TEAM"',
            'line "ROCKET here today."',
            'para "But PROJECT MEW"',
            'line "is out of my hands"',
            'cont "now."',
            'para "Farewell."',
        ],
    )
    _assert_contiguous(
        entrance_dialogue,
        [
            'text "A hidden stairway"',
            'line "opened beside the"',
            'cont "old stairs!"',
            'para "The PROJECT MEW"',
            'line "transmitter lies"',
            'cont "beyond it."',
            "done",
        ],
    )
    assert 'line "signal is below."' not in entrance_dialogue
    _assert_contiguous(
        reference_after_dialogue,
        [
            'para "disband TEAM"',
            'line "ROCKET here today."',
            'para "Farewell."',
        ],
    )
    assert not any("PROJECT_MEW" in row for row in reference)
    assert not any('para "But PROJECT MEW"' in row for row in reference)
    assert not any('para "…"' in row for row in reference)


def test_annex_terminal_is_cancelable_confirmed_permanent_and_capture_optional(
    repo_root: Path,
) -> None:
    annex = _active_code(
        repo_root / "maps/RadioTowerTransmitterAnnex.asm", CRYSTAL_LEGENDS
    )
    terminal = _section(
        annex,
        "RadioTowerTransmitterAnnexTerminalScript:",
        "RadioTowerTransmitterAnnexMewScript:",
    )
    director = _section(
        _active_code(repo_root / "maps/RadioTower5F.asm", CRYSTAL_LEGENDS),
        "RadioTower5FDirectorCleanupScript:",
        "Ben:",
    )

    for row in (
        'db "REVERSE SEQ.@"',
        'db "STABILIZE@"',
        'db "CANCEL@"',
        'text "Run REVERSE"',
        'text "Run STABILIZE"',
        "yesorno",
        "setevent EVENT_PROJECT_MEW_RESOLVED",
        "clearevent EVENT_PROJECT_MEW_TRANSFORMED",
        "setevent EVENT_PROJECT_MEW_TRANSFORMED",
        "changeblock 4, 2, $01",
        "changeblock 4, 6, $07",
        "changeblock 4, 6, $40",
    ):
        assert row in annex
    cancel = terminal[terminal.index(".Cancel:") : terminal.index(".Resolved:")]
    assert not any("setevent EVENT_PROJECT_MEW" in row for row in cancel)
    assert "EVENT_CAUGHT_PROJECT_MEW_SUBJECT" not in director
    for row in (
        "setevent EVENT_CLEARED_RADIO_TOWER",
        "verbosegiveitem CLEAR_BELL",
        "setevent EVENT_GOT_CLEAR_BELL",
        "setevent EVENT_TEAM_ROCKET_DISBANDED",
    ):
        assert row in director


def test_annex_entry_walks_to_the_stairs_seals_once_and_reconstructs_tiles(
    repo_root: Path,
) -> None:
    radio = _active_code(repo_root / "maps/RadioTower5F.asm", CRYSTAL_LEGENDS)
    annex = _active_code(
        repo_root / "maps/RadioTowerTransmitterAnnex.asm", CRYSTAL_LEGENDS
    )
    _assert_contiguous(
        radio,
        [
            "RadioTower5FPlayerEntersAnnexMovement:",
            "step RIGHT",
            "step RIGHT",
            "step UP",
            "step UP",
            "step UP",
            "step LEFT",
            "step UP",
            "step LEFT",
            "step UP",
            "step_end",
            "RadioTower5FPlayerReturnsFromAnnexMovement:",
            "step DOWN",
            "step RIGHT",
            "step DOWN",
            "step RIGHT",
            "step DOWN",
            "step DOWN",
            "step DOWN",
            "step LEFT",
            "step LEFT",
            "step_end",
        ],
    )
    dimensions = parse_map_dimensions(
        (repo_root / "constants/map_constants.asm").read_text()
    )
    block_paths = block_paths_for_maps(
        dimensions,
        parse_block_paths((repo_root / "data/maps/blocks.asm").read_text()),
    )
    tilesets = parse_map_tilesets((repo_root / "data/maps/maps.asm").read_text())
    corridor = [
        (14, 5),
        (15, 5),
        (16, 5),
        (16, 4),
        (16, 3),
        (16, 2),
        (15, 2),
        (15, 1),
        (14, 1),
    ]
    assert all(
        collision_at(
            repo_root,
            "RADIO_TOWER_5F",
            coordinate,
            dimensions,
            block_paths,
            tilesets,
        )
        == "FLOOR"
        for coordinate in corridor
    )
    assert (
        collision_at(
            repo_root,
            "RADIO_TOWER_5F",
            (16, 1),
            dimensions,
            block_paths,
            tilesets,
        )
        == "BOOKSHELF"
    )
    _assert_contiguous(
        annex,
        [
            "def_scene_scripts",
            "scene_script RadioTowerTransmitterAnnexLockEntryScene",
            "scene_script RadioTowerTransmitterAnnexNoopScene",
            "assert _NUM_SCENE_SCRIPTS == SCENE_RADIOTOWERTRANSMITTERANNEX_NOOP + 1",
        ],
    )
    callback = _section(
        annex,
        "RadioTowerTransmitterAnnexExitCallback:",
        "RadioTowerTransmitterAnnexSealEntryScript:",
    )
    for row in (
        "checkevent EVENT_PROJECT_MEW_RESOLVED",
        "checkscene",
        "ifequal SCENE_RADIOTOWERTRANSMITTERANNEX_LOCK_ENTRY, .Entering",
        "changeblock 4, 6, $40",
        "changeblock 4, 6, $07",
        "changeblock 4, 2, $01",
    ):
        assert row in callback
    seal = _section(
        annex,
        "RadioTowerTransmitterAnnexSealEntryScript:",
        "RadioTowerTransmitterAnnexSubjectSpriteCallback:",
    )
    _assert_contiguous(
        seal,
        [
            "checkevent EVENT_PROJECT_MEW_RESOLVED",
            "iftrue .Resolved",
            "applymovement PLAYER, RadioTowerTransmitterAnnexEntryMovement",
            "reanchormap",
            "playsound SFX_ENTER_DOOR",
            "changeblock 4, 6, $40",
            "refreshmap",
            "setscene SCENE_RADIOTOWERTRANSMITTERANNEX_NOOP",
            "waitsfx",
            "end",
        ],
    )
    _assert_contiguous(
        annex,
        [
            "RadioTowerTransmitterAnnexEntryMovement:",
            "step UP",
            "step_end",
        ],
    )


def test_annex_uses_one_event_masked_variable_subject_and_readable_controls(
    repo_root: Path,
) -> None:
    annex = _active_code(
        repo_root / "maps/RadioTowerTransmitterAnnex.asm", CRYSTAL_LEGENDS
    )
    callback = _section(
        annex,
        "RadioTowerTransmitterAnnexSubjectSpriteCallback:",
        "RadioTowerTransmitterAnnexUploadMonitorScript:",
    )
    assert (
        "callback MAPCALLBACK_SPRITES, RadioTowerTransmitterAnnexSubjectSpriteCallback"
        in annex
    )
    assert "callback MAPCALLBACK_OBJECTS" not in annex
    for event in ("EVENT_PROJECT_MEW_RESOLVED", "EVENT_PROJECT_MEW_TRANSFORMED"):
        assert f"checkevent {event}" in callback
    assert "checkcode VAR_PARTYCOUNT" not in callback
    assert not any("POKEDEX" in row or "PARTY" in row for row in callback)
    assert "variablesprite SPRITE_PROJECT_MEW_SUBJECT, SPRITE_MEW" in callback
    assert "variablesprite SPRITE_PROJECT_MEW_SUBJECT, SPRITE_MEWTWO" in callback
    assert not any(row.startswith(("appear ", "disappear ")) for row in callback)
    assert "bg_event 2, 5, BGEVENT_READ, RadioTowerTransmitterAnnexUploadMonitorScript" in annex
    assert "bg_event 6, 5, BGEVENT_READ, RadioTowerTransmitterAnnexTerminalScript" in annex
    assert "bg_event 4, 3, BGEVENT_IFNOTSET, RadioTowerTransmitterAnnexGlassObservation" in annex
    assert "conditional_event EVENT_PROJECT_MEW_RESOLVED, .Script" in annex
    assert sum(row.startswith("object_event 4, 2,") for row in annex) == 1
    assert any(
        row.startswith(
            "object_event 4, 2, SPRITE_PROJECT_MEW_SUBJECT, SPRITEMOVEDATA_POKEMON"
        )
        and row.endswith(
            "RadioTowerTransmitterAnnexSubjectScript, EVENT_CAUGHT_PROJECT_MEW_SUBJECT"
        )
        for row in annex
    )


def test_generic_caught_result_is_custom_only_and_keeps_celebi_compatible(
    repo_root: Path,
) -> None:
    constants = _active_code(
        repo_root / "constants/battle_constants.asm", CRYSTAL_LEGENDS
    )
    custom_items = _active_code(
        repo_root / "engine/items/item_effects.asm", CRYSTAL_LEGENDS
    )
    reference_items = _active_code(
        repo_root / "engine/items/item_effects.asm", REFERENCE
    )
    custom_specials = _active_code(
        repo_root / "data/events/special_pointers.asm", CRYSTAL_LEGENDS
    )
    reference_specials = _active_code(
        repo_root / "data/events/special_pointers.asm", REFERENCE
    )
    custom_celebi = _active_code(repo_root / "engine/events/celebi.asm", CRYSTAL_LEGENDS)
    reference_celebi = _active_code(repo_root / "engine/events/celebi.asm", REFERENCE)

    _assert_contiguous(
        constants,
        [
            "DEF BATTLERESULT_CAUGHT_POKEMON EQU 6",
            "DEF BATTLERESULT_CAUGHT_CELEBI EQU BATTLERESULT_CAUGHT_POKEMON",
            "DEF BATTLERESULT_BOX_FULL EQU 7",
        ],
    )
    custom_catch = _section(custom_items, ".skip_pokedex", ".SendToPC:")
    reference_catch = _section(reference_items, ".skip_pokedex", ".SendToPC:")
    assert "set BATTLERESULT_CAUGHT_POKEMON, [hl]" in custom_catch
    assert "cp BATTLETYPE_CELEBI" not in custom_catch
    assert "cp BATTLETYPE_CELEBI" in reference_catch
    assert "set BATTLERESULT_CAUGHT_CELEBI, [hl]" in reference_catch
    assert custom_specials[-1] == "add_special CheckCaughtPokemon"
    assert "add_special CheckCaughtPokemon" not in reference_specials
    _assert_contiguous(
        custom_celebi,
        [
            "CheckCaughtPokemon:",
            "CheckCaughtCelebi:",
            "ld a, [wBattleResult]",
            "bit BATTLERESULT_CAUGHT_POKEMON, a",
        ],
    )
    assert "CheckCaughtPokemon:" not in reference_celebi
    assert "CheckCaughtCelebi:" in reference_celebi


@pytest.mark.parametrize(
    ("species", "script"),
    [
        ("MEW", "RadioTowerTransmitterAnnexMewScript"),
        ("MEWTWO", "RadioTowerTransmitterAnnexMewtwoScript"),
    ],
)
def test_selected_subject_is_level_30_normal_retry_until_captured_encounter(
    repo_root: Path, species: str, script: str
) -> None:
    annex = _active_code(
        repo_root / "maps/RadioTowerTransmitterAnnex.asm", CRYSTAL_LEGENDS
    )
    start = annex.index(f"{script}:")
    end = (
        annex.index("RadioTowerTransmitterAnnexMewtwoScript:")
        if species == "MEW"
        else annex.index("RadioTowerTransmitterAnnexTerminalMenuHeader:")
    )
    encounter = annex[start:end]

    _assert_contiguous(
        encounter,
        [
            f"loadwildmon {species}, 30",
            "startbattle",
            "special CheckCaughtPokemon",
            "iffalse .NotCaught",
            "setevent EVENT_CAUGHT_PROJECT_MEW_SUBJECT",
            "disappear RADIOTOWERTRANSMITTERANNEX_SUBJECT",
            ".NotCaught:",
            "reloadmapafterbattle",
            "end",
        ],
    )
    assert encounter.index("special CheckCaughtPokemon") < encounter.index(
        "reloadmapafterbattle"
    )
    assert encounter.index(f"cry {species}") < encounter.index("opentext")
    assert not any("BATTLETYPE" in row or row.startswith("loadvar") for row in encounter)
    assert not any(
        token in row
        for token in ("HP", "STATUS", "ATTEMPT", "POKEDEX", "PARTY")
        for row in encounter
    )
