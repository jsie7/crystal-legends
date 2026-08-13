from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.bedroom_scenario import (
    dump_battery_ram,
    event_is_set,
    save_game_from_overworld,
    wait_for_idle,
)
from tests.support.constant_resolver import resolve_constants
from tests.support.game_state import read_inventory, read_progress
from tests.support.legendary_scenario import (
    advance_with_a_until,
    place_player,
    prepare_battle_party,
)
from tests.support.phase_07_scenario import (
    loaded_phase_7_checkpoint,
    loaded_phase_7_saved_game,
)
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.emulator, pytest.mark.phase7]


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_07_project_mew.json").read_text()
    )


@pytest.fixture(scope="module")
def phase_7_runtime_constants(repo_root: Path, tmp_path_factory) -> dict[str, int]:
    names = {
        "SPAWN_N_A",
        "MAPSETUP_WARP",
        "OW_UP",
        "OW_DOWN",
        "GROUP_RADIO_TOWER_TRANSMITTER_ANNEX",
        "MAP_RADIO_TOWER_TRANSMITTER_ANNEX",
        "GROUP_RADIO_TOWER_5F",
        "MAP_RADIO_TOWER_5F",
        "EVENT_BEAT_ROCKET_EXECUTIVEM_1",
        "EVENT_PROJECT_MEW_DATA_SENT",
        "EVENT_PROJECT_MEW_RESOLVED",
        "EVENT_PROJECT_MEW_TRANSFORMED",
        "EVENT_CAUGHT_PROJECT_MEW_SUBJECT",
        "EVENT_CLEARED_RADIO_TOWER",
        "EVENT_GOT_CLEAR_BELL",
        "EVENT_TEAM_ROCKET_DISBANDED",
        "EVENT_BLACKTHORN_CITY_SUPER_NERD_BLOCKS_GYM",
        "EVENT_RADIO_TOWER_ROCKET_TAKEOVER",
        "MEW",
        "MEWTWO",
        "ARTICUNO",
        "MASTER_BALL",
        "CLEAR_BELL",
        "BALL_POCKET",
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
        "BATTLERESULT_CAUGHT_POKEMON",
    }
    constants = resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_7_runtime_constants"),
        sorted(names),
    )
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    for scene in (
        "SCENE_RADIOTOWER5F_PROJECT_MEW",
        "SCENE_RADIOTOWER5F_ROCKET_BOSS",
        "SCENE_RADIOTOWER5F_NOOP",
    ):
        constants[scene] = symbols.constant(scene)
    return constants


def _event(session, constants: dict[str, int], name: str) -> bool:
    return event_is_set(session, constants[name])


def _run_terminal(
    session,
    constants: dict[str, int],
    scenario: dict,
    choice: str,
) -> None:
    if choice not in {"cancel", "reverse", "stabilize"}:
        raise ValueError(f"unknown terminal choice {choice}")
    max_frames = scenario["max_frames_per_step"]
    session.enable_script_tracing()
    session.register_hook("VerticalMenu")
    session.register_hook("_YesNoBox")
    menu_count = session.hook_history.count("VerticalMenu") + 1
    session.write_symbol("wPlayerDirection", constants["OW_UP"])
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("VerticalMenu") >= menu_count,
        max_frames,
        "Project Mew terminal menu",
    )
    if choice == "cancel":
        session.tap("b", 2, 10)
        advance_with_a_until(
            session,
            lambda current: current.read_symbol("wScriptMode") == 0,
            max_frames,
            "Project Mew terminal cancellation",
        )
        return

    if choice == "stabilize":
        session.tap("down", 2, 10)
    confirmation_count = session.hook_history.count("_YesNoBox") + 1
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("_YesNoBox")
        >= confirmation_count,
        max_frames,
        f"Project Mew {choice} confirmation",
    )
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: (
            _event(current, constants, "EVENT_PROJECT_MEW_RESOLVED")
            and current.read_symbol("wScriptMode") == 0
        ),
        max_frames,
        f"Project Mew {choice} completion",
    )


def _prepare_subject_party(
    constants: dict[str, int], *, master_ball: bool, strong: bool = True
):
    def prepare(session) -> None:
        prepare_battle_party(session, constants, constants["ARTICUNO"], strong)
        if master_ball:
            session.write_symbol("wNumBalls", 1)
            session.write_symbol_bytes(
                "wBalls", bytes([constants["MASTER_BALL"], 1, 0xFF])
            )
            session.write_symbol("wLastPocket", constants["BALL_POCKET"])

    return prepare


def _start_subject_battle(
    session, constants: dict[str, int], scenario: dict, *, menu_cursor: int = 1
) -> None:
    max_frames = scenario["max_frames_per_step"]
    session.enable_script_tracing()
    session.register_hook(
        "BattleMenu",
        lambda current: current.write_symbol(
            "wBattleMenuCursorPosition", menu_cursor
        ),
    )
    session.register_hook("CheckCaughtPokemon")
    menu_count = session.hook_history.count("BattleMenu") + 1
    session.write_symbol("wPlayerDirection", constants["OW_UP"])
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("BattleMenu") >= menu_count,
        max_frames,
        "Project Mew subject battle",
    )
    assert session.read_symbol("wEnemyMonLevel") == 30


def test_terminal_cancel_changes_no_outcome_and_can_be_reopened(
    repo_root: Path,
    tmp_path: Path,
    phase_7_runtime_constants: dict[str, int],
    scenario: dict,
) -> None:
    constants = phase_7_runtime_constants
    with loaded_phase_7_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        start="terminal",
        resolved=False,
    ) as session:
        _run_terminal(session, constants, scenario, "cancel")
        assert not _event(session, constants, "EVENT_PROJECT_MEW_RESOLVED")
        assert not _event(session, constants, "EVENT_PROJECT_MEW_TRANSFORMED")
        assert not _event(session, constants, "EVENT_CAUGHT_PROJECT_MEW_SUBJECT")

        _run_terminal(session, constants, scenario, "reverse")
        assert _event(session, constants, "EVENT_PROJECT_MEW_RESOLVED")
        assert not _event(session, constants, "EVENT_PROJECT_MEW_TRANSFORMED")


@pytest.mark.parametrize(
    ("choice", "transformed", "species"),
    [("reverse", False, "MEW"), ("stabilize", True, "MEWTWO")],
)
def test_terminal_confirmation_selects_exact_permanent_subject(
    repo_root: Path,
    tmp_path: Path,
    phase_7_runtime_constants: dict[str, int],
    scenario: dict,
    choice: str,
    transformed: bool,
    species: str,
) -> None:
    constants = phase_7_runtime_constants
    with loaded_phase_7_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        start="terminal",
        resolved=False,
    ) as session:
        _run_terminal(session, constants, scenario, choice)
        assert _event(session, constants, "EVENT_PROJECT_MEW_RESOLVED")
        assert _event(session, constants, "EVENT_PROJECT_MEW_TRANSFORMED") is transformed
        assert not _event(session, constants, "EVENT_CAUGHT_PROJECT_MEW_SUBJECT")
        assert constants[species] in (constants["MEW"], constants["MEWTWO"])


def test_stabilized_outcome_survives_native_save_reload(
    repo_root: Path,
    tmp_path: Path,
    phase_7_runtime_constants: dict[str, int],
    scenario: dict,
) -> None:
    constants = phase_7_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    persisted = tmp_path / "stabilized.sav"
    with loaded_phase_7_checkpoint(
        repo_root,
        tmp_path / "initial",
        constants,
        scenario,
        start="terminal",
        resolved=False,
    ) as session:
        _run_terminal(session, constants, scenario, "stabilize")
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, persisted)

    with loaded_phase_7_saved_game(
        repo_root,
        tmp_path / "reload",
        constants,
        scenario,
        persisted,
    ) as session:
        assert _event(session, constants, "EVENT_PROJECT_MEW_RESOLVED")
        assert _event(session, constants, "EVENT_PROJECT_MEW_TRANSFORMED")
        assert not _event(session, constants, "EVENT_CAUGHT_PROJECT_MEW_SUBJECT")
        prepare_battle_party(session, constants, constants["ARTICUNO"], True)
        subject_start = scenario["annex"]["subject_start"]
        place_player(session, subject_start["x"], subject_start["y"])
        _start_subject_battle(session, constants, scenario)
        assert session.read_symbol("wEnemyMonSpecies") == constants["MEWTWO"]
        assert session.read_symbol("wEnemyMonLevel") == 30


def test_final_executive_upload_fact_precedes_battle_and_survives_loss(
    repo_root: Path,
    tmp_path: Path,
    phase_7_runtime_constants: dict[str, int],
    scenario: dict,
) -> None:
    constants = phase_7_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_7_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        start="boss",
        resolved=False,
        before_overworld=_prepare_subject_party(
            constants, master_ball=False, strong=False
        ),
    ) as session:
        session.register_hook("BattleMenu")
        session.enable_script_tracing()
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        session.tap("up", 2, 20)
        advance_with_a_until(
            session,
            lambda current: "BattleMenu" in current.hook_history,
            max_frames,
            "final Rocket Executive battle",
        )
        assert _event(session, constants, "EVENT_PROJECT_MEW_DATA_SENT")
        assert not _event(session, constants, "EVENT_BEAT_ROCKET_EXECUTIVEM_1")
        assert not _event(session, constants, "EVENT_CLEARED_RADIO_TOWER")

        session.register_hook(
            "HasPlayerFainted",
            lambda current: current.write_symbol_bytes("wBattleMonHP", b"\0\0"),
        )
        session.write_symbol("wBattleMenuCursorPosition", 1)
        advance_with_a_until(
            session,
            lambda current: (
                current.read_symbol("wBattleMode") == 0
                and (
                    current.read_symbol("wMapGroup"),
                    current.read_symbol("wMapNumber"),
                )
                != (
                    constants["GROUP_RADIO_TOWER_5F"],
                    constants["MAP_RADIO_TOWER_5F"],
                )
            ),
            max_frames,
            "final Executive loss",
        )
        assert _event(session, constants, "EVENT_PROJECT_MEW_DATA_SENT")
        assert not _event(session, constants, "EVENT_BEAT_ROCKET_EXECUTIVEM_1")
        assert not _event(session, constants, "EVENT_CLEARED_RADIO_TOWER")


def test_final_executive_victory_opens_annex_before_director_cleanup(
    repo_root: Path,
    tmp_path: Path,
    phase_7_runtime_constants: dict[str, int],
    scenario: dict,
) -> None:
    constants = phase_7_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_7_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        start="boss",
        resolved=False,
        before_overworld=_prepare_subject_party(constants, master_ball=False),
    ) as session:
        session.enable_script_tracing()
        session.register_hook("BattleMenu")
        session.register_hook(
            "HasEnemyFainted",
            lambda current: current.write_symbol_bytes("wEnemyMonHP", b"\0\0"),
        )
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        session.tap("up", 2, 20)
        advance_with_a_until(
            session,
            lambda current: "BattleMenu" in current.hook_history,
            max_frames,
            "final Rocket Executive battle",
        )
        assert _event(session, constants, "EVENT_PROJECT_MEW_DATA_SENT")
        assert not _event(session, constants, "EVENT_BEAT_ROCKET_EXECUTIVEM_1")

        session.write_symbol("wBattleMenuCursorPosition", 1)
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: (
                current.read_symbol("wBattleMode") == 0
                and current.read_symbol("wMapGroup")
                == constants["GROUP_RADIO_TOWER_TRANSMITTER_ANNEX"]
                and current.read_symbol("wMapNumber")
                == constants["MAP_RADIO_TOWER_TRANSMITTER_ANNEX"]
            ),
            max_frames,
            "Project Mew annex handoff",
        )
        assert _event(session, constants, "EVENT_BEAT_ROCKET_EXECUTIVEM_1")
        assert _event(session, constants, "EVENT_PROJECT_MEW_DATA_SENT")
        assert not _event(session, constants, "EVENT_PROJECT_MEW_RESOLVED")
        assert not _event(session, constants, "EVENT_CLEARED_RADIO_TOWER")
        assert (
            session.read_symbol("wRadioTower5FSceneID")
            == constants["SCENE_RADIOTOWER5F_PROJECT_MEW"]
        )


@pytest.mark.parametrize("outcome", ["knockout", "escape"])
def test_knockout_and_escape_restore_a_full_healthy_retry(
    repo_root: Path,
    tmp_path: Path,
    phase_7_runtime_constants: dict[str, int],
    scenario: dict,
    outcome: str,
) -> None:
    constants = phase_7_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_7_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        start="subject",
        resolved=True,
        transformed=False,
        before_overworld=_prepare_subject_party(constants, master_ball=False),
    ) as session:
        _start_subject_battle(
            session,
            constants,
            scenario,
            menu_cursor=1 if outcome == "knockout" else 4,
        )
        if outcome == "knockout":
            session.register_hook(
                "HasEnemyFainted",
                lambda current: current.write_symbol_bytes("wEnemyMonHP", b"\0\0"),
            )
        else:
            session.write_symbol_bytes("wEnemyMonHP", b"\0\1")
            session.write_symbol("wEnemyMonStatus", 1)
            session.write_symbol_bytes("wBattleMonSpeed", (999).to_bytes(2, "big"))
            session.write_symbol_bytes("wEnemyMonSpeed", (1).to_bytes(2, "big"))
        check_count = session.hook_history.count("CheckCaughtPokemon") + 1
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: current.hook_history.count("CheckCaughtPokemon")
            >= check_count,
            max_frames,
            f"Project Mew {outcome} result query",
        )
        advance_with_a_until(
            session,
            lambda current: current.read_symbol("wScriptMode") == 0,
            max_frames,
            f"Project Mew {outcome} map return",
        )
        assert not _event(session, constants, "EVENT_CAUGHT_PROJECT_MEW_SUBJECT")

        _start_subject_battle(session, constants, scenario)
        assert session.read_symbol("wEnemyMonSpecies") == constants["MEW"]
        assert session.read_symbol_bytes(
            "wEnemyMonHP", 2
        ) == session.read_symbol_bytes("wEnemyMonMaxHP", 2)
        assert session.read_symbol("wEnemyMonStatus") == 0


def test_player_defeat_leaves_resolved_subject_uncaught(
    repo_root: Path,
    tmp_path: Path,
    phase_7_runtime_constants: dict[str, int],
    scenario: dict,
) -> None:
    constants = phase_7_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_7_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        start="subject",
        resolved=True,
        transformed=False,
        before_overworld=_prepare_subject_party(
            constants, master_ball=False, strong=False
        ),
    ) as session:
        _start_subject_battle(session, constants, scenario)
        session.register_hook(
            "HasPlayerFainted",
            lambda current: current.write_symbol_bytes("wBattleMonHP", b"\0\0"),
        )
        checked = session.hook_history.count("CheckCaughtPokemon")
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: (
                current.read_symbol("wBattleMode") == 0
                and (
                    current.read_symbol("wMapGroup"),
                    current.read_symbol("wMapNumber"),
                )
                != (
                    constants["GROUP_RADIO_TOWER_TRANSMITTER_ANNEX"],
                    constants["MAP_RADIO_TOWER_TRANSMITTER_ANNEX"],
                )
            ),
            max_frames,
            "Project Mew player defeat",
        )
        assert _event(session, constants, "EVENT_PROJECT_MEW_RESOLVED")
        assert not _event(session, constants, "EVENT_CAUGHT_PROJECT_MEW_SUBJECT")
        assert session.hook_history.count("CheckCaughtPokemon") == checked


@pytest.mark.parametrize(
    ("transformed", "species"),
    [(False, "MEW"), (True, "MEWTWO")],
)
def test_successful_capture_sets_fact_and_removes_selected_subject(
    repo_root: Path,
    tmp_path: Path,
    phase_7_runtime_constants: dict[str, int],
    scenario: dict,
    transformed: bool,
    species: str,
) -> None:
    constants = phase_7_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_7_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        start="subject",
        resolved=True,
        transformed=transformed,
        before_overworld=_prepare_subject_party(constants, master_ball=True),
    ) as session:
        _start_subject_battle(session, constants, scenario, menu_cursor=3)
        assert session.read_symbol("wEnemyMonSpecies") == constants[species]
        session.register_hook("PokeBallEffect")
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: "PokeBallEffect" in current.hook_history,
            max_frames,
            "Project Mew Master Ball use",
        )
        advance_with_a_until(
            session,
            lambda current: _event(
                current, constants, "EVENT_CAUGHT_PROJECT_MEW_SUBJECT"
            ),
            max_frames,
            "Project Mew capture fact",
        )
        result = session.read_symbol("wBattleResult")
        advance_with_a_until(
            session,
            lambda current: current.read_symbol("wScriptMode") == 0,
            max_frames,
            "Project Mew capture completion",
        )
        assert result & (1 << constants["BATTLERESULT_CAUGHT_POKEMON"])
        assert read_progress(session).owns(constants[species])
        battle_count = session.hook_history.count("BattleMenu")
        session.tap("up", 2, 10)
        session.tap("a", 2, 30)
        assert session.hook_history.count("BattleMenu") == battle_count


def test_return_without_capture_resumes_stock_director_progression_once(
    repo_root: Path,
    tmp_path: Path,
    phase_7_runtime_constants: dict[str, int],
    scenario: dict,
) -> None:
    constants = phase_7_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_7_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        start="exit",
        resolved=True,
        transformed=False,
    ) as session:
        session.enable_script_tracing()
        session.write_symbol("wPlayerDirection", constants["OW_DOWN"])
        session.tap("down", 2, 20)
        session.tap("down", 2, 20)
        session.wait_for_script("RadioTower5FDirectorCleanupScript", max_frames)
        advance_with_a_until(
            session,
            lambda current: (
                _event(current, constants, "EVENT_TEAM_ROCKET_DISBANDED")
                and current.read_symbol("wScriptMode") == 0
            ),
            max_frames,
            "stock Radio Tower Director cleanup",
        )
        assert session.read_symbol("wMapGroup") == constants["GROUP_RADIO_TOWER_5F"]
        assert session.read_symbol("wMapNumber") == constants["MAP_RADIO_TOWER_5F"]
        assert _event(session, constants, "EVENT_CLEARED_RADIO_TOWER")
        assert _event(session, constants, "EVENT_GOT_CLEAR_BELL")
        assert _event(session, constants, "EVENT_TEAM_ROCKET_DISBANDED")
        assert _event(
            session, constants, "EVENT_BLACKTHORN_CITY_SUPER_NERD_BLOCKS_GYM"
        )
        assert not _event(session, constants, "EVENT_CAUGHT_PROJECT_MEW_SUBJECT")
        assert constants["CLEAR_BELL"] in read_inventory(session).key_items
        assert (
            session.read_symbol("wRadioTower5FSceneID")
            == constants["SCENE_RADIOTOWER5F_NOOP"]
        )

        cleanup_count = session.script_history.count(
            "RadioTower5FDirectorCleanupScript"
        )
        session.tick(120)
        assert (
            session.script_history.count("RadioTower5FDirectorCleanupScript")
            == cleanup_count
        )
