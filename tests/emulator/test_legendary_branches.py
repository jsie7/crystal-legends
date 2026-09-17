from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.bedroom_scenario import (
    dump_battery_ram,
    event_is_set,
    save_game_from_overworld,
    start_saved_game,
)
from tests.support.constant_resolver import resolve_constants
from tests.support.game_state import read_progress
from tests.support.gift_scenario import (
    interact_with_gift,
    set_current_box_full,
    set_party_full,
)
from tests.support.legendary_scenario import (
    advance_with_a_until,
    loaded_story_checkpoint,
    place_player,
    prepare_battle_party,
    walk_steps,
)
from tests.support.pyboy_session import PyBoySession, prepare_rom
from tests.support.symbol_table import SymbolTable


pytestmark = pytest.mark.emulator


@pytest.fixture(scope="module")
def branch_contract(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/contracts/legendary_branches.json").read_text()
    )


@pytest.fixture(scope="module")
def branch_constants(
    repo_root: Path, tmp_path_factory, branch_contract: dict
) -> dict[str, int]:
    names = {
        "EVENT_GOT_A_POKEMON_FROM_ELM",
        "EVENT_GOT_ARTICUNO_FROM_ELM",
        "EVENT_GOT_ZAPDOS_FROM_ELM",
        "EVENT_GOT_MOLTRES_FROM_ELM",
        "EVENT_GOT_MYSTERY_EGG_FROM_MR_POKEMON",
        "EVENT_GAVE_MYSTERY_EGG_TO_ELM",
        "EVENT_RIVAL_CHERRYGROVE_CITY",
        "EVENT_OAK_MOVED_THIRD_BIRD",
        "EVENT_COP_IN_ELMS_LAB",
        "GROUP_CHERRYGROVE_CITY",
        "MAP_CHERRYGROVE_CITY",
        "GROUP_ELMS_LAB",
        "MAP_ELMS_LAB",
        "SPAWN_CHERRYGROVE",
        "SPAWN_NEW_BARK",
        "SPAWN_N_A",
        "PARTY_LENGTH",
        "MONS_PER_BOX",
        "EEVEE",
        "BERRY",
        "MAPSETUP_WARP",
        "WIN",
        "LOSE",
        "RIVAL1",
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
    for branch in branch_contract["branches"]:
        names.update(
            {
                branch["player"],
                branch["choice_event"],
                branch["pokeball_event"],
                branch["rival"],
                branch["rival_party"],
            }
        )
    constants = resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("legendary_runtime_constants"),
        sorted(names),
    )
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    for scene in (
        "SCENE_CHERRYGROVECITY_MEET_RIVAL",
        "SCENE_CHERRYGROVECITY_NOOP",
        "SCENE_ELMSLAB_NOOP",
        "SCENE_ELMSLAB_CANT_LEAVE",
        "SCENE_ELMSLAB_AIDE_GIVES_POTION",
        "SCENE_NEWBARKTOWN_NOOP",
        "SCENE_NEWBARKTOWN_TEACHER_STOPS_YOU",
    ):
        constants[scene] = symbols.constant(scene)
    return constants


def _starter_scenario(branch: dict) -> dict:
    return {
        "species": branch["player"],
        "script": branch["starter_script"],
        "storage_label": "ElmStarterStorageFullScript",
        "start": {
            "x": {"LEFT": 6, "CENTER": 7, "RIGHT": 8}[branch["starter_slot"]],
            "y": 4,
            "facing": "UP",
        },
        "max_frames_per_step": 12_000,
    }


def _assert_starter_unclaimed(
    session: PyBoySession, constants: dict[str, int], branches: list[dict]
) -> None:
    for branch in branches:
        assert not event_is_set(session, constants[branch["choice_event"]])
        assert not event_is_set(session, constants[branch["pokeball_event"]])
    assert not event_is_set(session, constants["EVENT_GOT_A_POKEMON_FROM_ELM"])
    assert not event_is_set(session, constants["EVENT_RIVAL_CHERRYGROVE_CITY"])
    assert session.read_symbol("wElmsLabSceneID") == constants["SCENE_ELMSLAB_CANT_LEAVE"]
    assert session.read_symbol("wNewBarkTownSceneID") == constants[
        "SCENE_NEWBARKTOWN_TEACHER_STOPS_YOU"
    ]
    # Elm and his aide precede the three Poké Balls in the native object list.
    for index in range(3, 6):
        assert session.read_symbol(f"wMap{index}ObjectStructID") != 0xFF


def _assert_starter_claimed(
    session: PyBoySession,
    constants: dict[str, int],
    branches: list[dict],
    chosen: dict,
) -> None:
    for branch in branches:
        expected = branch == chosen
        assert event_is_set(session, constants[branch["choice_event"]]) == expected
        assert event_is_set(session, constants[branch["pokeball_event"]]) == expected
    assert event_is_set(session, constants["EVENT_GOT_A_POKEMON_FROM_ELM"])
    assert event_is_set(session, constants["EVENT_RIVAL_CHERRYGROVE_CITY"])
    assert session.read_symbol("wElmsLabSceneID") == constants[
        "SCENE_ELMSLAB_AIDE_GIVES_POTION"
    ]
    assert session.read_symbol("wNewBarkTownSceneID") == constants["SCENE_NEWBARKTOWN_NOOP"]


@pytest.mark.parametrize("branch_index", [0, 1, 2], ids=["articuno", "zapdos", "moltres"])
@pytest.mark.parametrize("destination", ["party", "current-box"])
def test_starter_full_storage_preserves_choice_through_continue_and_retry(
    repo_root: Path,
    tmp_path: Path,
    branch_contract: dict,
    branch_constants: dict[str, int],
    branch_index: int,
    destination: str,
) -> None:
    branches = branch_contract["branches"]
    branch = branches[branch_index]
    constants = branch_constants
    scenario = _starter_scenario(branch)
    max_frames = scenario["max_frames_per_step"]
    with loaded_story_checkpoint(
        repo_root, tmp_path / "full", constants, branch, "starter_choice", max_frames
    ) as session:
        set_party_full(session, constants["EEVEE"], constants["PARTY_LENGTH"])
        set_current_box_full(session, constants["EEVEE"], constants["MONS_PER_BOX"])
        before = read_progress(session)
        flags = session.read_symbol_range("wEventFlags", "wBoxNames")
        assert interact_with_gift(session, scenario, accept=True) == 2
        assert read_progress(session) == before
        assert session.read_symbol_range("wEventFlags", "wBoxNames") == flags
        _assert_starter_unclaimed(session, constants, branches)
        assert "ElmDirectionsScript" not in session.script_history
        save_game_from_overworld(session, max_frames)
        saved = dump_battery_ram(session, tmp_path / "refused.sav")

    prepared = prepare_rom(
        tmp_path / "continue",
        repo_root / "crystallegends.gbc",
        repo_root / "crystallegends.sym",
        save_fixture=saved,
    )
    with PyBoySession(prepared) as session:
        start_saved_game(session, max_frames)
        _assert_starter_unclaimed(session, constants, branches)
        assert read_progress(session) == before
        assert interact_with_gift(session, scenario, accept=True) == 2
        _assert_starter_unclaimed(session, constants, branches)
        assert read_progress(session) == before

        if destination == "party":
            set_party_full(session, constants["EEVEE"], constants["PARTY_LENGTH"] - 1)
            prefix = f"wPartyMon{constants['PARTY_LENGTH']}"
            expected_result = 0
        else:
            set_current_box_full(
                session, constants["EEVEE"], constants["MONS_PER_BOX"] - 1
            )
            prefix = "sBoxMon1"
            expected_result = 1
        assert interact_with_gift(session, scenario, accept=True) == expected_result
        _assert_starter_claimed(session, constants, branches, branch)
        after = read_progress(session)
        assert after.party.count == constants["PARTY_LENGTH"]
        assert after.current_box.count == constants["MONS_PER_BOX"]
        assert after.owns(constants[branch["player"]])
        assert session.read_symbol(f"{prefix}Species") == constants[branch["player"]]
        assert session.read_symbol(f"{prefix}Level") == 5
        if destination == "party":
            assert session.read_symbol(f"{prefix}Item") == constants["BERRY"]

        other = _starter_scenario(branches[(branch_index + 1) % len(branches)])
        place_player(session, other["start"]["x"], other["start"]["y"])
        assert interact_with_gift(session, other, accept=None) is None
        assert "LookAtElmPokeBallScript" in session.script_history
        assert read_progress(session) == after
        _assert_starter_claimed(session, constants, branches, branch)


@pytest.mark.parametrize("branch_index", [0, 1, 2], ids=["articuno", "zapdos", "moltres"])
def test_starter_decline_then_normal_empty_party_delivery(
    repo_root: Path,
    tmp_path: Path,
    branch_contract: dict,
    branch_constants: dict[str, int],
    branch_index: int,
) -> None:
    branch = branch_contract["branches"][branch_index]
    scenario = _starter_scenario(branch)
    with loaded_story_checkpoint(
        repo_root,
        tmp_path,
        branch_constants,
        branch,
        "starter_choice",
        scenario["max_frames_per_step"],
    ) as session:
        before = read_progress(session)
        assert interact_with_gift(session, scenario, accept=False) is None
        _assert_starter_unclaimed(session, branch_constants, branch_contract["branches"])
        assert read_progress(session) == before
        assert interact_with_gift(session, scenario, accept=True) == 0
        _assert_starter_claimed(
            session, branch_constants, branch_contract["branches"], branch
        )
        assert read_progress(session).party.species == (
            branch_constants[branch["player"]],
        )
        assert session.read_symbol("wPartyMon1Level") == 5
        assert session.read_symbol("wPartyMon1Item") == branch_constants["BERRY"]


@pytest.mark.parametrize(
    ("branch_index", "should_win"),
    [(0, True), (1, True), (2, True), (0, False)],
    ids=["articuno-win", "zapdos-win", "moltres-win", "articuno-loss"],
)
def test_first_silver_runtime_mapping_and_battle_outcomes(
    repo_root: Path,
    tmp_path: Path,
    branch_contract: dict,
    branch_constants: dict[str, int],
    branch_index: int,
    should_win: bool,
) -> None:
    branch = branch_contract["branches"][branch_index]
    max_frames = 60_000
    with loaded_story_checkpoint(
        repo_root,
        tmp_path,
        branch_constants,
        branch,
        "first_silver",
        max_frames,
    ) as session:
        assert session.read_symbol("wMapGroup") == branch_constants[
            "GROUP_CHERRYGROVE_CITY"
        ]
        assert session.read_symbol("wXCoord") == 29
        assert session.read_symbol("wYCoord") == 4
        prepare_battle_party(
            session,
            branch_constants,
            branch_constants[branch["player"]],
            should_win,
        )
        session.enable_script_tracing()
        session.register_hook("ReadTrainerParty")
        session.register_hook("ExitBattle")
        walk_steps(session, "down", "wYCoord", 1, 3, max_frames)
        walk_steps(
            session,
            "right",
            "wXCoord",
            1,
            4,
            max_frames,
        )
        advance_with_a_until(
            session,
            lambda current: "ReadTrainerParty" in current.hook_history,
            max_frames,
            "first Silver party load",
        )
        session.wait_until(
            lambda current: current.read_symbol("wOTPartyCount") == 1,
            max_frames,
            "first Silver party data",
        )
        assert session.read_symbol("wOtherTrainerClass") == branch_constants["RIVAL1"]
        assert session.read_symbol("wOtherTrainerID") == branch_constants[
            branch["rival_party"]
        ]
        assert session.read_symbol("wOTPartySpecies") == branch_constants[
            branch["rival"]
        ]
        advance_with_a_until(
            session,
            lambda current: "ExitBattle" in current.hook_history,
            max_frames,
            "first Silver battle completion",
        )
        assert session.read_symbol("wBattleResult") == branch_constants[
            "WIN" if should_win else "LOSE"
        ]
        advance_with_a_until(
            session,
            lambda current: (
                current.read_symbol("wCherrygroveCitySceneID")
                == branch_constants["SCENE_CHERRYGROVECITY_NOOP"]
                and current.read_symbol("wScriptMode") == 0
            ),
            max_frames,
            "first Silver scene completion",
        )
        battle_loads = session.hook_history.count("ReadTrainerParty")
        session.tap("left", 10, 10)
        session.tap("right", 10, 10)
        session.tick(180)
        assert session.hook_history.count("ReadTrainerParty") == battle_loads


@pytest.mark.parametrize("branch_index", [0, 1, 2], ids=["articuno", "zapdos", "moltres"])
def test_elm_oak_handoff_runs_once_for_every_branch(
    repo_root: Path,
    tmp_path: Path,
    branch_contract: dict,
    branch_constants: dict[str, int],
    branch_index: int,
) -> None:
    branch = branch_contract["branches"][branch_index]
    max_frames = 12_000
    with loaded_story_checkpoint(
        repo_root,
        tmp_path,
        branch_constants,
        branch,
        "elm_handoff",
        max_frames,
    ) as session:
        walk_steps(session, "left", "wXCoord", -1, 7, max_frames)
        walk_steps(session, "up", "wYCoord", -1, 2, max_frames)
        session.tap("up", 2, 2)
        session.wait_until(
            lambda current: (
                current.read_symbol("wMapGroup")
                == branch_constants["GROUP_ELMS_LAB"]
                and current.read_symbol("wMapNumber")
                == branch_constants["MAP_ELMS_LAB"]
            ),
            max_frames,
            "Elm's Lab entry",
        )
        place_player(session, 5, 3)
        session.tap("up", 2, 20)
        session.enable_script_tracing()
        session.tap("a")
        advance_with_a_until(
            session,
            lambda current: event_is_set(
                current, branch_constants["EVENT_OAK_MOVED_THIRD_BIRD"]
            ),
            max_frames,
            "Oak third-bird handoff",
        )
        advance_with_a_until(
            session,
            lambda current: current.read_symbol("wScriptMode") == 0,
            max_frames,
            "Elm handoff dialogue completion",
        )
        assert branch["oak_branch"] in session.script_history
        for ball_event in (
            candidate["pokeball_event"] for candidate in branch_contract["branches"]
        ):
            assert event_is_set(session, branch_constants[ball_event])
        handoff_count = session.script_history.count("ElmArrangeThirdBirdTransferScript")
        session.tap("a")
        advance_with_a_until(
            session,
            lambda current: current.read_symbol("wScriptMode") == 0,
            max_frames,
            "replayed Elm dialogue completion",
        )
        assert session.script_history.count("ElmArrangeThirdBirdTransferScript") == handoff_count
