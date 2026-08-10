from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.bedroom_scenario import event_is_set
from tests.support.constant_resolver import resolve_constants
from tests.support.legendary_scenario import (
    advance_with_a_until,
    loaded_story_checkpoint,
    place_player,
    prepare_battle_party,
    walk_steps,
)
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
        "SCENE_NEWBARKTOWN_NOOP",
    ):
        constants[scene] = symbols.constant(scene)
    return constants


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
