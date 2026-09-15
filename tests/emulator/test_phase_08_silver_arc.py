from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.bedroom_scenario import (
    dump_battery_ram,
    event_is_set,
    save_game_from_overworld,
)
from tests.support.constant_resolver import resolve_constants
from tests.support.legendary_scenario import (
    advance_with_a_until,
    place_player,
    prepare_battle_party,
)
from tests.support.phase_08_scenario import (
    loaded_phase_8_checkpoint,
    loaded_phase_8_saved_game,
)
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.emulator, pytest.mark.phase8]


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_08_silver_arc.json").read_text()
    )


@pytest.fixture(scope="module")
def branches(repo_root: Path) -> list[dict]:
    return json.loads(
        (repo_root / "tests/contracts/legendary_branches.json").read_text()
    )["branches"]


@pytest.fixture(scope="module")
def phase_8_runtime_constants(repo_root: Path, tmp_path_factory) -> dict[str, int]:
    names = {
        "SPAWN_N_A",
        "MAPSETUP_WARP",
        "OW_UP",
        "OW_RIGHT",
        "OW_DOWN",
        "GROUP_MOUNT_MOON",
        "MAP_MOUNT_MOON",
        "GROUP_ELMS_LAB",
        "MAP_ELMS_LAB",
        "GROUP_INDIGO_PLATEAU_POKECENTER_1F",
        "MAP_INDIGO_PLATEAU_POKECENTER_1F",
        "GROUP_DRAGONS_DEN_B1F",
        "MAP_DRAGONS_DEN_B1F",
        "GROUP_DRAGON_SHRINE",
        "MAP_DRAGON_SHRINE",
        "EVENT_GOT_A_POKEMON_FROM_ELM",
        "EVENT_GOT_ARTICUNO_FROM_ELM",
        "EVENT_GOT_ZAPDOS_FROM_ELM",
        "EVENT_GOT_MOLTRES_FROM_ELM",
        "EVENT_OAK_MOVED_THIRD_BIRD",
        "EVENT_COP_IN_ELMS_LAB",
        "EVENT_INDIGO_PLATEAU_POKECENTER_RIVAL",
        "EVENT_RIVAL_DRAGONS_DEN",
        "EVENT_GOT_DRATINI",
        "EVENT_TEMPORARY_UNTIL_MAP_RELOAD_1",
        "EVENT_TEMPORARY_UNTIL_MAP_RELOAD_7",
        "EVENT_MT_MOON_RIVAL",
        "EVENT_BEAT_RIVAL_IN_MT_MOON",
        "EVENT_SILVER_BIRD_RELEASED",
        "EVENT_ARTICUNO_AVAILABLE",
        "EVENT_ZAPDOS_AVAILABLE",
        "EVENT_MOLTRES_AVAILABLE",
        "RIVAL2",
        "ENGINE_MT_MOON_SQUARE_CLEFAIRY",
        "ENGINE_INDIGO_PLATEAU_RIVAL_FIGHT",
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "MUSIC_CHAMPION_BATTLE",
        "WIN",
        "LOSE",
        "ARTICUNO",
        "ZAPDOS",
        "MOLTRES",
        "SNEASEL",
        "CROBAT",
        "URSARING",
        "MAGNETON",
        "GENGAR",
        "ALAKAZAM",
        "PARTYMON_STRUCT_LENGTH",
        "MON_SPECIES",
        "MON_MOVES",
        "MON_PP",
        "MON_LEVEL",
        "MON_HP",
        "MON_MAXHP",
        "MON_ATK",
        "MON_DEF",
        "MON_SPD",
        "MON_SAT",
        "MON_SDF",
        "TACKLE",
    }
    constants = resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_8_runtime_constants"),
        sorted(names),
    )
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    for scene in (
        "SCENE_MOUNTMOON_RIVAL_BATTLE",
        "SCENE_MOUNTMOON_NOOP",
        "SCENE_ELMSLAB_SILVER_RETURNS_BIRD",
        "SCENE_ELMSLAB_NOOP",
        "SCENE_INDIGOPLATEAUPOKECENTER1F_RIVAL_BATTLE",
        "SCENE_DRAGONSDENB1F_NOOP",
        "SCENE_DRAGONSHRINE_NOOP",
    ):
        constants[scene] = symbols.constant(scene)
    for branch in json.loads(
        (repo_root / "tests/contracts/legendary_branches.json").read_text()
    )["branches"]:
        constants[branch["mt_moon_party"]] = resolve_constants(
            repo_root,
            tmp_path_factory.mktemp(f"phase_8_{branch['id']}_party"),
            [branch["mt_moon_party"]],
        )[branch["mt_moon_party"]]
        constants[branch["indigo_party"]] = resolve_constants(
            repo_root,
            tmp_path_factory.mktemp(f"phase_8_{branch['id']}_rematch_party"),
            [branch["indigo_party"]],
        )[branch["indigo_party"]]
    return constants


def _event(session, constants: dict[str, int], name: str) -> bool:
    return event_is_set(session, constants[name])


def _indigo_weekly_flag(session, constants: dict[str, int]) -> bool:
    bit = (
        constants["ENGINE_INDIGO_PLATEAU_RIVAL_FIGHT"]
        - constants["ENGINE_MT_MOON_SQUARE_CLEFAIRY"]
    )
    return bool(session.read_symbol("wDailyFlags2") & (1 << bit))


def _step_to_coordinate_event(session, x: int, max_frames: int) -> None:
    place_player(session, x, 5)
    session.tap("up", 10, 20)
    if session.read_symbol("wYCoord") == 5:
        session.tap("up", 10, 20)
    session.wait_until(
        lambda current: current.read_symbol("wYCoord") == 4,
        max_frames,
        "Indigo Plateau coordinate event",
    )


def _interaction_state(session) -> tuple[bytes, ...]:
    return (
        session.read_symbol_bytes("wPartyCount", 1),
        session.read_symbol_bytes("wPartySpecies", 7),
        session.read_symbol_bytes("wPartyMon1", 48),
        session.read_symbol_bytes("wNumItems", 1),
        session.read_symbol_bytes("wItems", 42),
        session.read_symbol_bytes("wMoney", 3),
        session.read_symbol_bytes("wPokedexCaught", 32),
        session.read_symbol_bytes("wPokedexSeen", 32),
        session.read_symbol_bytes("wDailyFlags2", 1),
    )


def _prepare_party(constants: dict[str, int], species: int, should_win: bool):
    def prepare(session) -> None:
        prepare_battle_party(session, constants, species, should_win)

    return prepare


@pytest.mark.parametrize("branch_index", [0, 1, 2], ids=["articuno", "zapdos", "moltres"])
def test_mt_moon_victory_selects_the_branch_and_schedules_elm(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    branches: list[dict],
    phase_8_runtime_constants: dict[str, int],
    branch_index: int,
) -> None:
    branch = branches[branch_index]
    constants = phase_8_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_8_checkpoint(
        repo_root,
        tmp_path / branch["id"],
        constants,
        scenario,
        branch,
        start="mount_moon",
        mt_moon_won=False,
        before_overworld=_prepare_party(
            constants, constants[branch["player"]], True
        ),
    ) as session:
        session.enable_script_tracing()
        session.register_hook("ReadTrainerParty")
        session.register_hook("ExitBattle")
        session.register_hook(
            "HasEnemyFainted",
            lambda current: current.write_symbol_bytes("wEnemyMonHP", b"\0\0"),
        )
        advance_with_a_until(
            session,
            lambda current: "ReadTrainerParty" in current.hook_history,
            max_frames,
            "Mt. Moon Silver party load",
        )
        assert session.read_symbol("wOtherTrainerClass") == constants["RIVAL2"]
        assert session.read_symbol("wOtherTrainerID") == constants[
            branch["mt_moon_party"]
        ]
        session.wait_until(
            lambda current: current.read_symbol("wOTPartyCount") == 6,
            max_frames,
            "Mt. Moon six-Pokemon party",
        )
        assert session.read_symbol_bytes("wOTPartySpecies", 6)[-1] == constants[
            branch["returned_species"]
        ]
        session.write_symbol("wBattleMenuCursorPosition", 1)
        advance_with_a_until(
            session,
            lambda current: "ExitBattle" in current.hook_history,
            max_frames,
            "Mt. Moon Silver victory",
        )
        assert session.read_symbol("wBattleResult") == constants["WIN"]
        advance_with_a_until(
            session,
            lambda current: (
                _event(current, constants, "EVENT_BEAT_RIVAL_IN_MT_MOON")
                and current.read_symbol("wScriptMode") == 0
            ),
            max_frames,
            "Mt. Moon post-victory completion",
        )
        assert session.read_symbol("wMountMoonSceneID") == constants[
            "SCENE_MOUNTMOON_NOOP"
        ]
        assert session.read_symbol("wElmsLabSceneID") == constants[
            "SCENE_ELMSLAB_SILVER_RETURNS_BIRD"
        ]
        assert _event(session, constants, "EVENT_MT_MOON_RIVAL")
        assert not _event(session, constants, "EVENT_SILVER_BIRD_RELEASED")
        assert not any(
            _event(session, constants, event)
            for event in scenario["events"]["availability"]
        )


def test_mt_moon_loss_leaves_every_phase_8_state_pending(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    branches: list[dict],
    phase_8_runtime_constants: dict[str, int],
) -> None:
    branch = branches[0]
    constants = phase_8_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_8_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        branch,
        start="mount_moon",
        mt_moon_won=False,
        before_overworld=_prepare_party(
            constants, constants[branch["player"]], False
        ),
    ) as session:
        session.register_hook("ReadTrainerParty")
        session.register_hook("ExitBattle")
        session.register_hook(
            "HasPlayerFainted",
            lambda current: current.write_symbol_bytes("wBattleMonHP", b"\0\0"),
        )
        advance_with_a_until(
            session,
            lambda current: "ReadTrainerParty" in current.hook_history,
            max_frames,
            "Mt. Moon Silver loss party load",
        )
        session.write_symbol("wBattleMenuCursorPosition", 1)
        advance_with_a_until(
            session,
            lambda current: "ExitBattle" in current.hook_history,
            max_frames,
            "Mt. Moon Silver loss",
        )
        assert session.read_symbol("wBattleResult") == constants["LOSE"]
        advance_with_a_until(
            session,
            lambda current: current.read_symbol("wBattleMode") == 0,
            max_frames,
            "Mt. Moon whiteout completion",
        )
        assert not _event(session, constants, "EVENT_BEAT_RIVAL_IN_MT_MOON")
        assert not _event(session, constants, "EVENT_MT_MOON_RIVAL")
        assert not _event(session, constants, "EVENT_SILVER_BIRD_RELEASED")
        assert not any(
            _event(session, constants, event)
            for event in scenario["events"]["availability"]
        )
        assert session.read_symbol("wElmsLabSceneID") == constants["SCENE_ELMSLAB_NOOP"]


def test_pending_elm_return_survives_native_save_reload(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    branches: list[dict],
    phase_8_runtime_constants: dict[str, int],
) -> None:
    branch = branches[0]
    constants = phase_8_runtime_constants
    persisted = tmp_path / "pending-return.sav"
    with loaded_phase_8_checkpoint(
        repo_root,
        tmp_path / "initial",
        constants,
        scenario,
        branch,
        start="mount_moon",
        mt_moon_won=True,
    ) as session:
        save_game_from_overworld(session, scenario["max_frames_per_step"])
        dump_battery_ram(session, persisted)

    with loaded_phase_8_saved_game(
        repo_root,
        tmp_path / "reload",
        constants,
        scenario,
        persisted,
    ) as session:
        assert _event(session, constants, "EVENT_BEAT_RIVAL_IN_MT_MOON")
        assert _event(session, constants, "EVENT_MT_MOON_RIVAL")
        assert not _event(session, constants, "EVENT_SILVER_BIRD_RELEASED")
        assert session.read_symbol("wElmsLabSceneID") == constants[
            "SCENE_ELMSLAB_SILVER_RETURNS_BIRD"
        ]


@pytest.mark.parametrize("branch_index", [0, 1, 2], ids=["articuno", "zapdos", "moltres"])
def test_elm_release_scene_is_branch_correct_atomic_and_replay_safe(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    branches: list[dict],
    phase_8_runtime_constants: dict[str, int],
    branch_index: int,
) -> None:
    branch = branches[branch_index]
    constants = phase_8_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    cry_species: list[int] = []
    persisted = tmp_path / f"completed-{branch['id']}.sav"
    with loaded_phase_8_checkpoint(
        repo_root,
        tmp_path / "scene",
        constants,
        scenario,
        branch,
        start="elms_lab",
        mt_moon_won=True,
    ) as session:
        session.enable_script_tracing()
        session.register_hook(
            "PlayMonCry",
            lambda current: cry_species.append(current.pyboy.register_file.A),
        )
        session.wait_until(
            lambda current: current.read_symbol("wMap7ObjectStructID") != 0xFF,
            max_frames,
            "Phase 8 Silver object to load",
        )
        assert session.read_symbol("wMap7ObjectStructID") != 0xFF
        assert session.read_symbol("wMap8ObjectStructID") != 0xFF
        assert session.read_symbol("wMap6ObjectStructID") == 0xFF
        advance_with_a_until(
            session,
            lambda current: (
                _event(current, constants, "EVENT_SILVER_BIRD_RELEASED")
                and current.read_symbol("wScriptMode") == 0
            ),
            max_frames,
            "Elm's Lab Silver release scene",
        )
        assert "ElmsLabSilverArcScript" in session.script_history
        assert "ElmsLabSilverSetAvailability" in session.script_history
        assert cry_species == [constants[branch["returned_species"]]]
        assert _event(session, constants, branch["availability_event"])
        assert not _event(session, constants, branch["player_availability_event"])
        assert not _event(session, constants, branch["oak_availability_event"])
        assert session.read_symbol("wElmsLabSceneID") == constants["SCENE_ELMSLAB_NOOP"]
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (4, 4)
        assert session.read_symbol("wMap7ObjectStructID") == 0xFF
        assert session.read_symbol("wMap8ObjectStructID") == 0xFF
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, persisted)

    with loaded_phase_8_saved_game(
        repo_root,
        tmp_path / "reload",
        constants,
        scenario,
        persisted,
    ) as session:
        assert _event(session, constants, "EVENT_SILVER_BIRD_RELEASED")
        assert _event(session, constants, branch["availability_event"])
        assert session.read_symbol("wElmsLabSceneID") == constants["SCENE_ELMSLAB_NOOP"]
        assert session.read_symbol("wMap7ObjectStructID") == 0xFF
        assert session.read_symbol("wMap8ObjectStructID") == 0xFF
        session.enable_script_tracing()
        place_player(session, 5, 3)
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: (
                "ProfElmScript" in current.script_history
                and current.read_symbol("wScriptMode") == 0
            ),
            max_frames,
            "ordinary post-release Elm interaction",
        )
        assert "ProfElmScript" in session.script_history
        assert "ElmsLabSilverArcScript" not in session.script_history


def test_elm_actors_are_absent_before_mt_moon(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    branches: list[dict],
    phase_8_runtime_constants: dict[str, int],
) -> None:
    with loaded_phase_8_checkpoint(
        repo_root,
        tmp_path,
        phase_8_runtime_constants,
        scenario,
        branches[0],
        start="elms_lab",
        mt_moon_won=False,
    ) as session:
        assert session.read_symbol("wMap7ObjectStructID") == 0xFF
        assert session.read_symbol("wMap8ObjectStructID") == 0xFF


@pytest.mark.parametrize(
    ("entrance", "released", "weekday", "weekly_fight", "expected_battle"),
    [
        (0, False, "MONDAY", False, False),
        (1, False, "MONDAY", False, False),
        (0, True, "MONDAY", False, True),
        (0, True, "WEDNESDAY", False, True),
        (0, True, "MONDAY", True, False),
        (0, True, "TUESDAY", False, False),
    ],
    ids=(
        "left-before-release",
        "right-before-release",
        "monday-after-release",
        "wednesday-after-release",
        "weekly-flag-set",
        "excluded-tuesday",
    ),
)
def test_indigo_rematch_release_weekday_and_weekly_gates(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    branches: list[dict],
    phase_8_runtime_constants: dict[str, int],
    entrance: int,
    released: bool,
    weekday: str,
    weekly_fight: bool,
    expected_battle: bool,
) -> None:
    constants = phase_8_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_8_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        branches[0],
        start="indigo",
        mt_moon_won=True,
        released=released,
        weekday=constants[weekday],
        weekly_fight=weekly_fight,
        before_overworld=_prepare_party(
            constants, constants[branches[0]["player"]], True
        ),
    ) as session:
        session.enable_script_tracing()
        session.register_hook("ReadTrainerParty")
        x = scenario["indigo"]["entrances"][entrance]["x"]
        _step_to_coordinate_event(session, x, max_frames)
        if expected_battle:
            advance_with_a_until(
                session,
                lambda current: "ReadTrainerParty" in current.hook_history,
                max_frames,
                "eligible Indigo Plateau rematch",
            )
            assert session.read_symbol("wOtherTrainerID") == constants[
                branches[0]["indigo_party"]
            ]
            session.wait_until(
                lambda current: current.read_symbol("wOTPartyCount") == 6,
                max_frames,
                "complete Indigo Plateau rematch party",
            )
        else:
            session.wait_until(
                lambda current: current.read_symbol("wScriptMode") == 0,
                max_frames,
                "ineligible Indigo Plateau rematch to return control",
            )
            assert "ReadTrainerParty" not in session.hook_history
            assert session.read_symbol("wMap4ObjectStructID") == 0xFF


def test_indigo_rematch_party_music_victory_and_reload_cadence(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    branches: list[dict],
    phase_8_runtime_constants: dict[str, int],
) -> None:
    branch = branches[0]
    constants = phase_8_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    persisted = tmp_path / "indigo-complete.sav"
    music_ids: list[int] = []
    with loaded_phase_8_checkpoint(
        repo_root,
        tmp_path / "battle",
        constants,
        scenario,
        branch,
        start="indigo",
        mt_moon_won=True,
        released=True,
        weekday=constants["MONDAY"],
        before_overworld=_prepare_party(constants, constants[branch["player"]], True),
    ) as session:
        session.register_hook("ReadTrainerParty")
        session.register_hook("ExitBattle")
        session.register_hook(
            "PlayMusic",
            lambda current: music_ids.append(
                (current.pyboy.register_file.D << 8) | current.pyboy.register_file.E
            ),
        )
        session.register_hook(
            "HasEnemyFainted",
            lambda current: current.write_symbol_bytes("wEnemyMonHP", b"\0\0"),
        )
        _step_to_coordinate_event(session, 16, max_frames)
        advance_with_a_until(
            session,
            lambda current: "ReadTrainerParty" in current.hook_history,
            max_frames,
            "Indigo Plateau party load",
        )
        assert session.read_symbol("wOtherTrainerClass") == constants["RIVAL2"]
        assert session.read_symbol("wOtherTrainerID") == constants[
            branch["indigo_party"]
        ]
        session.wait_until(
            lambda current: (
                current.read_symbol("wOTPartyCount") == 6
                and current.read_symbol("wOTPartyMon6Level") == 52
            ),
            max_frames,
            "complete Indigo Plateau rematch party",
        )
        assert session.read_symbol("wOTPartyCount") == 6
        assert list(session.read_symbol_bytes("wOTPartySpecies", 6)) == [
            constants[name]
            for name in ("SNEASEL", "MAGNETON", "GENGAR", "ALAKAZAM", "URSARING", "CROBAT")
        ]
        party = session.read_symbol_bytes("wOTPartyMon1", 6 * constants["PARTYMON_STRUCT_LENGTH"])
        assert [
            party[index * constants["PARTYMON_STRUCT_LENGTH"] + constants["MON_LEVEL"]]
            for index in range(6)
        ] == [48, 48, 49, 49, 50, 52]
        assert not {
            constants["ARTICUNO"], constants["ZAPDOS"], constants["MOLTRES"]
        } & set(session.read_symbol_bytes("wOTPartySpecies", 6))
        session.write_symbol("wBattleMenuCursorPosition", 1)
        advance_with_a_until(
            session,
            lambda current: "ExitBattle" in current.hook_history,
            max_frames,
            "Indigo Plateau rematch victory",
        )
        assert constants["MUSIC_CHAMPION_BATTLE"] in music_ids
        advance_with_a_until(
            session,
            lambda current: (
                _indigo_weekly_flag(current, constants)
                and current.read_symbol("wScriptMode") == 0
            ),
            max_frames,
            "Indigo Plateau weekly completion",
        )
        assert _indigo_weekly_flag(session, constants)
        previous_loads = session.hook_history.count("ReadTrainerParty")
        _step_to_coordinate_event(session, 16, max_frames)
        session.wait_until(
            lambda current: current.read_symbol("wScriptMode") == 0,
            max_frames,
            "same-day Indigo rematch rejection",
        )
        assert session.hook_history.count("ReadTrainerParty") == previous_loads
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, persisted)

    with loaded_phase_8_saved_game(
        repo_root,
        tmp_path / "reload",
        constants,
        scenario,
        persisted,
        weekday=constants["MONDAY"],
    ) as session:
        assert _event(session, constants, "EVENT_SILVER_BIRD_RELEASED")
        assert _indigo_weekly_flag(session, constants)
        session.register_hook("ReadTrainerParty")
        _step_to_coordinate_event(session, 16, max_frames)
        session.wait_until(
            lambda current: current.read_symbol("wScriptMode") == 0,
            max_frames,
            "saved weekly Indigo rematch rejection",
        )
        assert "ReadTrainerParty" not in session.hook_history


@pytest.mark.parametrize(
    ("released", "weekday", "visible"),
    [
        (False, "TUESDAY", False),
        (True, "TUESDAY", True),
        (True, "THURSDAY", True),
        (True, "MONDAY", False),
    ],
    ids=("before-release", "tuesday", "thursday", "excluded-monday"),
)
def test_dragons_den_cameo_requires_release_and_training_day(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    branches: list[dict],
    phase_8_runtime_constants: dict[str, int],
    released: bool,
    weekday: str,
    visible: bool,
) -> None:
    constants = phase_8_runtime_constants
    with loaded_phase_8_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        branches[0],
        start="dragons_den",
        mt_moon_won=True,
        released=released,
        weekday=constants[weekday],
    ) as session:
        assert (session.read_symbol("wMap3ObjectStructID") != 0xFF) is visible


def test_dragons_den_dialogue_repeats_then_resets_after_save_reload(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    branches: list[dict],
    phase_8_runtime_constants: dict[str, int],
) -> None:
    constants = phase_8_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    persisted = tmp_path / "dragons-den.sav"
    with loaded_phase_8_checkpoint(
        repo_root,
        tmp_path / "initial",
        constants,
        scenario,
        branches[0],
        start="dragons_den",
        mt_moon_won=True,
        released=True,
        weekday=constants["TUESDAY"],
    ) as session:
        session.enable_script_tracing()
        before = _interaction_state(session)
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: (
                "DragonsDenB1FRivalScript" in current.script_history
                and current.read_symbol("wScriptMode") == 0
            ),
            max_frames,
            "first Dragon's Den interaction",
        )
        assert "DragonsDenB1FRivalScript" in session.script_history
        assert _event(session, constants, "EVENT_TEMPORARY_UNTIL_MAP_RELOAD_1")
        first_trace_length = len(session.script_history)
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: (
                current.read_symbol("wScriptMode") == 0
                and len(current.script_history) > first_trace_length
            ),
            max_frames,
            "repeat Dragon's Den interaction",
        )
        assert "DragonsDenB1FRivalScript.RivalTalkAgain" in session.script_history
        assert _interaction_state(session) == before
        assert session.read_symbol("wBattleMode") == 0
        assert all(
            _event(session, constants, event)
            == (event == branches[0]["availability_event"])
            for event in scenario["events"]["availability"]
        )
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, persisted)

    with loaded_phase_8_saved_game(
        repo_root,
        tmp_path / "reload",
        constants,
        scenario,
        persisted,
        weekday=constants["TUESDAY"],
    ) as session:
        assert session.read_symbol("wMap3ObjectStructID") != 0xFF
        assert not _event(session, constants, "EVENT_TEMPORARY_UNTIL_MAP_RELOAD_1")
        session.enable_script_tracing()
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: (
                "DragonsDenB1FRivalScript" in current.script_history
                and current.read_symbol("wScriptMode") == 0
            ),
            max_frames,
            "post-reload Dragon's Den interaction",
        )
        assert "DragonsDenB1FRivalScript" in session.script_history
        assert "DragonsDenB1FRivalScript.RivalTalkAgain" not in session.script_history


@pytest.mark.parametrize("released", [False, True], ids=("before-release", "after-release"))
def test_dragon_shrine_elder_hint_follows_release_state(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    branches: list[dict],
    phase_8_runtime_constants: dict[str, int],
    released: bool,
) -> None:
    constants = phase_8_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_8_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        branches[0],
        start="dragon_shrine",
        mt_moon_won=True,
        released=released,
        weekday=constants["TUESDAY"],
    ) as session:
        session.enable_script_tracing()
        before = _interaction_state(session)
        assert session.read_symbol("wMap1ObjectStructID") != 0xFF
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        session.tap("a", 10, 10)
        advance_with_a_until(
            session,
            lambda current: (
                (
                    "DragonShrineElder1Script.BeatRivalInMtMoon"
                    in current.script_history
                    or "DragonShrineElder1Script.ClairsGrandfather"
                    in current.script_history
                )
                and current.read_symbol("wScriptMode") == 0
            ),
            max_frames,
            "Dragon Shrine elder interaction",
        )
        expected = (
            "DragonShrineElder1Script.BeatRivalInMtMoon"
            if released
            else "DragonShrineElder1Script.ClairsGrandfather"
        )
        rejected = (
            "DragonShrineElder1Script.ClairsGrandfather"
            if released
            else "DragonShrineElder1Script.BeatRivalInMtMoon"
        )
        assert expected in session.script_history
        assert rejected not in session.script_history
        assert _interaction_state(session) == before
        assert session.read_symbol("wBattleMode") == 0
