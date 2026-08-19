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
from tests.support.legendary_scenario import advance_with_a_until, prepare_battle_party
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
        "GROUP_MOUNT_MOON",
        "MAP_MOUNT_MOON",
        "GROUP_ELMS_LAB",
        "MAP_ELMS_LAB",
        "EVENT_GOT_A_POKEMON_FROM_ELM",
        "EVENT_GOT_ARTICUNO_FROM_ELM",
        "EVENT_GOT_ZAPDOS_FROM_ELM",
        "EVENT_GOT_MOLTRES_FROM_ELM",
        "EVENT_OAK_MOVED_THIRD_BIRD",
        "EVENT_COP_IN_ELMS_LAB",
        "EVENT_MT_MOON_RIVAL",
        "EVENT_BEAT_RIVAL_IN_MT_MOON",
        "EVENT_SILVER_BIRD_RELEASED",
        "EVENT_ARTICUNO_AVAILABLE",
        "EVENT_ZAPDOS_AVAILABLE",
        "EVENT_MOLTRES_AVAILABLE",
        "RIVAL2",
        "WIN",
        "LOSE",
        "ARTICUNO",
        "ZAPDOS",
        "MOLTRES",
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
    return constants


def _event(session, constants: dict[str, int], name: str) -> bool:
    return event_is_set(session, constants[name])


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
