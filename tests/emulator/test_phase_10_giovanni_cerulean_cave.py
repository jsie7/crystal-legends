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
from tests.support.game_state import read_progress
from tests.support.gift_scenario import (
    clear_current_box,
    set_current_box_full,
    set_party_full,
)
from tests.support.legendary_scenario import (
    advance_with_a_until,
    place_player,
    prepare_battle_party,
    walk_steps,
)
from tests.support.phase_10_scenario import (
    loaded_phase_10_baseline_save,
    loaded_phase_10_checkpoint,
    loaded_phase_10_saved_game,
)


pytestmark = [pytest.mark.emulator, pytest.mark.phase10]


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_10_giovanni_cerulean_cave.json").read_text()
    )


@pytest.fixture(scope="module")
def phase_10_runtime_constants(
    repo_root: Path, tmp_path_factory, scenario: dict
) -> dict[str, int]:
    names = {
        "SPAWN_N_A",
        "MAPSETUP_WARP",
        "OW_UP",
        "OW_DOWN",
        "OW_LEFT",
        "OW_RIGHT",
        "GROUP_ROUTE_4",
        "MAP_ROUTE_4",
        "GROUP_CERULEAN_CAVE",
        "MAP_CERULEAN_CAVE",
        "EVENT_PROJECT_MEW_RESOLVED",
        "EVENT_PROJECT_MEW_TRANSFORMED",
        "EVENT_SILVER_BIRD_RELEASED",
        "SPRITE_VARS",
        "SPRITE_PROJECT_MEW_SUBJECT",
        "SPRITE_MEW",
        "SPRITE_MEWTWO",
        "MEW",
        "MEWTWO",
        "ARTICUNO",
        "MASTER_BALL",
        "POTION",
        "POKE_BALL",
        "EEVEE",
        "BALL_POCKET",
        "ITEM_POCKET",
        "MAX_ITEMS",
        "MAX_BALLS",
        "PARTY_LENGTH",
        "MONS_PER_BOX",
        "BATTLERESULT_CAUGHT_POKEMON",
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
    names.update(name for group in scenario["events"].values() for name, _ in group)
    names.update(pickup["item"] for pickup in scenario["pickups"])
    names.add(scenario["hidden_pickup"]["item"])
    return resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_10_runtime_constants"),
        sorted(names),
    )


def _event(session, constants: dict[str, int], name: str) -> bool:
    return event_is_set(session, constants[name])


def _phase_10_snapshot(session, scenario: dict, constants: dict[str, int]) -> tuple[bool, ...]:
    return tuple(
        _event(session, constants, name)
        for group in scenario["events"].values()
        for name, _ in group
    )


def _prepare_party(constants: dict[str, int], *, master_ball: bool, strong: bool = True):
    def prepare(session) -> None:
        prepare_battle_party(session, constants, constants["ARTICUNO"], strong)
        if master_ball:
            session.write_symbol("wNumBalls", 1)
            session.write_symbol_bytes(
                "wBalls", bytes([constants["MASTER_BALL"], 1, 0xFF])
            )
            session.write_symbol("wLastPocket", constants["BALL_POCKET"])

    return prepare


def _start_object_battle(
    session,
    scenario: dict,
    constants: dict[str, int],
    *,
    menu_cursor: int,
    description: str,
) -> None:
    max_frames = scenario["max_frames_per_step"]
    session.enable_script_tracing()
    session.register_hook(
        "BattleMenu",
        lambda current: current.write_symbol("wBattleMenuCursorPosition", menu_cursor),
    )
    battle_count = session.hook_history.count("BattleMenu") + 1
    session.write_symbol("wPlayerDirection", constants["OW_UP"])
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("BattleMenu") >= battle_count,
        max_frames,
        description,
    )


def _finish_overworld_script(session, max_frames: int) -> None:
    advance_with_a_until(
        session,
        lambda current: current.read_symbol("wScriptMode") == 0,
        max_frames,
        "Phase 10 overworld script completion",
    )
    wait_for_idle(session, max_frames)


def _walk_until_map(
    session,
    button: str,
    constants: dict[str, int],
    map_name: str,
    max_frames: int,
) -> None:
    start = session.frames
    while session.frames - start < max_frames:
        if (
            session.read_symbol("wMapGroup") == constants[f"GROUP_{map_name}"]
            and session.read_symbol("wMapNumber") == constants[f"MAP_{map_name}"]
        ):
            session.tick(60)
            return
        session.tap(button, 2, 12)
    session.wait_until(lambda current: False, 1, f"warp to {map_name}")


def _cave_events(*, boss_defeated: bool = True, caught: bool = False) -> dict[str, bool]:
    return {
        "EVENT_PROJECT_MEW_RESOLVED": True,
        "EVENT_PROJECT_MEW_TRANSFORMED": False,
        "EVENT_SILVER_BIRD_RELEASED": True,
        "EVENT_BEAT_GIOVANNI": boss_defeated,
        "EVENT_CAUGHT_CERULEAN_CAVE_COUNTERPART": caught,
    }


def _fill_item_pocket(session, constants: dict[str, int], pocket: str) -> None:
    if pocket == "BALL_POCKET":
        capacity = constants["MAX_BALLS"]
        session.write_symbol("wNumBalls", capacity)
        session.write_symbol_bytes(
            "wBalls", bytes([constants["POKE_BALL"], 1] * capacity + [0xFF])
        )
        return
    if pocket != "ITEM_POCKET":
        raise ValueError(f"unsupported pocket {pocket}")
    capacity = constants["MAX_ITEMS"]
    session.write_symbol("wNumItems", capacity)
    session.write_symbol_bytes(
        "wItems", bytes([constants["POTION"], 1] * capacity + [0xFF])
    )


def _open_item_pocket_slot(session, constants: dict[str, int], pocket: str) -> None:
    if pocket == "BALL_POCKET":
        capacity = constants["MAX_BALLS"] - 1
        session.write_symbol("wNumBalls", capacity)
        session.write_symbol_bytes(
            "wBalls", bytes([constants["POKE_BALL"], 1] * capacity + [0xFF])
        )
        return
    capacity = constants["MAX_ITEMS"] - 1
    session.write_symbol("wNumItems", capacity)
    session.write_symbol_bytes(
        "wItems", bytes([constants["POTION"], 1] * capacity + [0xFF])
    )


def test_pre_phase_10_battery_save_loads_with_every_new_bit_clear(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
) -> None:
    with loaded_phase_10_baseline_save(repo_root, tmp_path, scenario) as session:
        assert not any(
            _phase_10_snapshot(session, scenario, phase_10_runtime_constants)
        )


@pytest.mark.parametrize(
    ("project_resolved", "silver_released", "badges", "guard_present"),
    [
        (False, False, 0, True),
        (False, True, 16, True),
        (True, False, 16, True),
        (True, True, 13, True),
        (True, True, 14, False),
        (True, True, 16, False),
    ],
)
def test_route_4_guard_derives_the_complete_access_matrix(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
    project_resolved: bool,
    silver_released: bool,
    badges: int,
    guard_present: bool,
) -> None:
    constants = phase_10_runtime_constants
    events = {
        "EVENT_PROJECT_MEW_RESOLVED": project_resolved,
        "EVENT_SILVER_BIRD_RELEASED": silver_released,
    }
    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="ROUTE_4",
        x=39,
        y=4,
        facing="LEFT",
        badge_count=badges,
        events=events,
    ) as session:
        assert (session.read_symbol("wMap5ObjectStructID") != 0xFF) is guard_present, (
            badges,
            session.read_symbol("wJohtoBadges"),
            session.read_symbol("wKantoBadges"),
            session.read_symbol("wScriptVar"),
            session.read_symbol("wMap5ObjectSprite"),
            session.read_symbol("wMap5ObjectStructID"),
        )
        before = _phase_10_snapshot(session, scenario, constants)
        if guard_present:
            session.tap("left", 2, 30)
            session.tap("left", 2, 30)
            assert session.read_symbol("wXCoord") == 39
        else:
            walk_steps(
                session,
                "left",
                "wXCoord",
                -1,
                1,
                scenario["max_frames_per_step"],
            )
        assert _phase_10_snapshot(session, scenario, constants) == before


def test_eligible_route_4_entrance_round_trips_through_the_native_cave_warp(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
) -> None:
    constants = phase_10_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="ROUTE_4",
        x=39,
        y=4,
        facing="LEFT",
        badge_count=14,
        events={
            "EVENT_PROJECT_MEW_RESOLVED": True,
            "EVENT_SILVER_BIRD_RELEASED": True,
        },
    ) as session:
        before = _phase_10_snapshot(session, scenario, constants)
        walk_steps(session, "left", "wXCoord", -1, 1, max_frames)
        _walk_until_map(session, "up", constants, "CERULEAN_CAVE", max_frames)
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            21,
            33,
        )
        walk_steps(session, "up", "wYCoord", -1, 1, max_frames)
        _walk_until_map(session, "down", constants, "ROUTE_4", max_frames)
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            38,
            4,
        )
        assert _phase_10_snapshot(session, scenario, constants) == before


def test_all_paired_lab_records_are_repeatable_and_stateless(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
) -> None:
    constants = phase_10_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="CERULEAN_CAVE",
        x=4,
        y=5,
        events=_cave_events(),
    ) as session:
        session.enable_script_tracing()
        before = _phase_10_snapshot(session, scenario, constants)
        for record in scenario["lab_records"]:
            for x, y in record["coordinates"]:
                place_player(session, x, y + 1)
                session.write_symbol("wPlayerDirection", constants["OW_UP"])
                count = session.script_history.count(record["script"]) + 1
                session.tap("a", 2, 10)
                advance_with_a_until(
                    session,
                    lambda current, script=record["script"], expected=count: current.script_history.count(script)
                    >= expected,
                    max_frames,
                    f"lab record {record['script']} at {(x, y)}",
                )
                _finish_overworld_script(session, max_frames)
        assert _phase_10_snapshot(session, scenario, constants) == before


@pytest.mark.parametrize(
    ("boss_defeated", "caught", "branch_label"),
    [
        (False, False, None),
        (True, False, "CeruleanCaveContainmentTerminal.Released"),
        (True, True, "CeruleanCaveContainmentTerminal.Caught"),
    ],
)
def test_containment_terminal_reports_each_persistent_state_without_writing_it(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
    boss_defeated: bool,
    caught: bool,
    branch_label: str | None,
) -> None:
    constants = phase_10_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="CERULEAN_CAVE",
        x=4,
        y=5,
        events=_cave_events(boss_defeated=boss_defeated, caught=caught),
    ) as session:
        session.enable_script_tracing()
        before = _phase_10_snapshot(session, scenario, constants)
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        session.tap("a", 2, 10)
        session.wait_for_script("CeruleanCaveContainmentTerminal", max_frames)
        _finish_overworld_script(session, max_frames)
        if branch_label is None:
            assert "CeruleanCaveContainmentTerminal.Released" not in session.script_history
            assert "CeruleanCaveContainmentTerminal.Caught" not in session.script_history
        else:
            assert branch_label in session.script_history
        assert _phase_10_snapshot(session, scenario, constants) == before


@pytest.mark.parametrize(
    ("boss_defeated", "counterpart_caught", "crew_present", "counterpart_present"),
    [
        (False, False, True, True),
        (True, False, False, True),
        (True, True, False, False),
    ],
)
def test_native_map_load_reconstructs_crew_and_counterpart_visibility(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
    boss_defeated: bool,
    counterpart_caught: bool,
    crew_present: bool,
    counterpart_present: bool,
) -> None:
    constants = phase_10_runtime_constants
    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="CERULEAN_CAVE",
        x=6,
        y=5,
        events={
            "EVENT_PROJECT_MEW_RESOLVED": True,
            "EVENT_PROJECT_MEW_TRANSFORMED": False,
            "EVENT_SILVER_BIRD_RELEASED": True,
            "EVENT_BEAT_GIOVANNI": boss_defeated,
            "EVENT_CAUGHT_CERULEAN_CAVE_COUNTERPART": counterpart_caught,
        },
    ) as session:
        masks = session.read_symbol_bytes("wObjectMasks", 13)[1:]
        assert (masks[0] == 0) is counterpart_present
        assert all(
            (masks[index] == 0) is crew_present for index in range(1, 8)
        ), masks
        assert masks[8:12] == b"\0\0\0\0"


@pytest.mark.parametrize("pickup_index", [0, 1, 2, 3])
def test_visible_pickups_retry_at_capacity_and_persist_independently(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
    pickup_index: int,
) -> None:
    constants = phase_10_runtime_constants
    pickup = scenario["pickups"][pickup_index]
    x, y = pickup["coordinate"]
    max_frames = scenario["max_frames_per_step"]
    persisted = tmp_path / f"{pickup['item'].lower()}-collected.sav"
    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path / "initial",
        constants,
        scenario,
        map_name="CERULEAN_CAVE",
        x=x,
        y=y + 1,
        facing="UP",
        events=_cave_events(caught=True),
    ) as session:
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        _fill_item_pocket(session, constants, pickup["pocket"])
        session.tap("a", 2, 10)
        _finish_overworld_script(session, max_frames)
        assert not _event(session, constants, pickup["event"])
        assert session.read_symbol_bytes("wObjectMasks", 13)[9 + pickup_index] == 0

        _open_item_pocket_slot(session, constants, pickup["pocket"])
        session.tap("a", 2, 10)
        _finish_overworld_script(session, max_frames)
        assert _event(session, constants, pickup["event"])
        assert session.read_symbol_bytes("wObjectMasks", 13)[9 + pickup_index] == 0xFF
        inventory = read_progress(session).inventory
        entries = inventory.balls if pickup["pocket"] == "BALL_POCKET" else inventory.items
        assert sum(quantity for item, quantity in entries if item == constants[pickup["item"]]) == 1
        for other in scenario["pickups"]:
            if other is not pickup:
                assert not _event(session, constants, other["event"])
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, persisted)

    with loaded_phase_10_saved_game(
        repo_root,
        tmp_path / "reload",
        constants,
        scenario,
        persisted,
    ) as session:
        assert _event(session, constants, pickup["event"])
        assert session.read_symbol_bytes("wObjectMasks", 13)[9 + pickup_index] == 0xFF
        inventory = read_progress(session).inventory
        entries = inventory.balls if pickup["pocket"] == "BALL_POCKET" else inventory.items
        assert sum(quantity for item, quantity in entries if item == constants[pickup["item"]]) == 1


def test_hidden_brightpowder_retries_at_capacity_and_sets_only_its_event(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
) -> None:
    constants = phase_10_runtime_constants
    pickup = scenario["hidden_pickup"]
    x, y = pickup["coordinate"]
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="CERULEAN_CAVE",
        x=x,
        y=y + 1,
        facing="UP",
        events=_cave_events(caught=True),
    ) as session:
        before = _phase_10_snapshot(session, scenario, constants)
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        _fill_item_pocket(session, constants, pickup["pocket"])
        session.tap("a", 2, 10)
        _finish_overworld_script(session, max_frames)
        assert _phase_10_snapshot(session, scenario, constants) == before

        _open_item_pocket_slot(session, constants, pickup["pocket"])
        session.tap("a", 2, 10)
        _finish_overworld_script(session, max_frames)
        assert _event(session, constants, pickup["event"])
        after = _phase_10_snapshot(session, scenario, constants)
        assert sum(left != right for left, right in zip(before, after, strict=True)) == 1
        assert sum(
            quantity
            for item, quantity in read_progress(session).inventory.items
            if item == constants[pickup["item"]]
        ) == 1


def test_sight_zero_scientist_requires_interaction_and_defeat_persists(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
) -> None:
    constants = phase_10_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    event = "EVENT_BEAT_CERULEAN_CAVE_SCIENTIST_1"
    persisted = tmp_path / "mitch-defeated.sav"
    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path / "initial",
        constants,
        scenario,
        map_name="CERULEAN_CAVE",
        x=7,
        y=22,
        facing="RIGHT",
        events=_cave_events(boss_defeated=False),
        before_overworld=_prepare_party(constants, master_ball=False),
    ) as session:
        session.write_symbol_bytes("wMornEncounterRate", b"\0\0\0\0")
        walk_steps(session, "left", "wXCoord", -1, 3, max_frames)
        walk_steps(session, "up", "wYCoord", -1, 1, max_frames)
        session.enable_script_tracing()
        session.register_hook("SeenByTrainerScript")
        session.tick(30)
        assert "SeenByTrainerScript" not in session.hook_history
        assert not _event(session, constants, event)

        session.register_hook(
            "BattleMenu",
            lambda current: current.write_symbol("wBattleMenuCursorPosition", 1),
        )
        session.register_hook(
            "HasEnemyFainted",
            lambda current: current.write_symbol_bytes("wEnemyMonHP", b"\0\0"),
        )
        session.write_symbol("wPlayerDirection", constants["OW_RIGHT"])
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: _event(current, constants, event)
            and current.read_symbol("wScriptMode") == 0,
            max_frames,
            "sight-zero scientist manual battle victory",
        )
        assert not any(
            _event(session, constants, remnant["event"])
            for remnant in scenario["remnants"]
            if remnant["event"] != event
        )
        assert not _event(session, constants, "EVENT_BEAT_GIOVANNI")
        assert session.read_symbol("wMap3ObjectStructID") != 0xFF
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, persisted)

    with loaded_phase_10_saved_game(
        repo_root,
        tmp_path / "reload",
        constants,
        scenario,
        persisted,
    ) as session:
        assert _event(session, constants, event)
        assert not _event(session, constants, "EVENT_BEAT_GIOVANNI")
        assert session.read_symbol("wMap3ObjectStructID") != 0xFF


def test_giovanni_loss_sets_returned_but_keeps_defeat_and_crew_clear(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
) -> None:
    constants = phase_10_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    persisted = tmp_path / "giovanni-loss.sav"
    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path / "initial",
        constants,
        scenario,
        map_name="CERULEAN_CAVE",
        x=6,
        y=5,
        events={
            "EVENT_PROJECT_MEW_RESOLVED": True,
            "EVENT_SILVER_BIRD_RELEASED": True,
        },
        before_overworld=_prepare_party(constants, master_ball=False, strong=False),
    ) as session:
        _start_object_battle(
            session,
            scenario,
            constants,
            menu_cursor=1,
            description="first Giovanni battle",
        )
        assert _event(session, constants, "EVENT_GIOVANNI_RETURNED")
        assert not _event(session, constants, "EVENT_BEAT_GIOVANNI")
        session.register_hook(
            "HasPlayerFainted",
            lambda current: current.write_symbol_bytes("wBattleMonHP", b"\0\0"),
        )
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: current.read_symbol("wBattleMode") == 0
            and (
                current.read_symbol("wMapGroup"),
                current.read_symbol("wMapNumber"),
            )
            != (constants["GROUP_CERULEAN_CAVE"], constants["MAP_CERULEAN_CAVE"]),
            max_frames,
            "Giovanni player-loss whiteout",
        )
        assert _event(session, constants, "EVENT_GIOVANNI_RETURNED")
        assert not _event(session, constants, "EVENT_BEAT_GIOVANNI")
        assert not any(
            _event(session, constants, name)
            for name, _ in scenario["events"]["trainers"][1:]
        )
        session.tick(180)
        wait_for_idle(session, max_frames)
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, persisted)

    with loaded_phase_10_saved_game(
        repo_root,
        tmp_path / "reload",
        constants,
        scenario,
        persisted,
    ) as session:
        assert _event(session, constants, "EVENT_GIOVANNI_RETURNED")
        assert not _event(session, constants, "EVENT_BEAT_GIOVANNI")


def test_giovanni_victory_removes_only_the_seven_rockets(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
) -> None:
    constants = phase_10_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="CERULEAN_CAVE",
        x=6,
        y=5,
        events={
            "EVENT_PROJECT_MEW_RESOLVED": True,
            "EVENT_PROJECT_MEW_TRANSFORMED": False,
            "EVENT_SILVER_BIRD_RELEASED": True,
            "EVENT_GIOVANNI_RETURNED": True,
        },
        before_overworld=_prepare_party(constants, master_ball=False),
    ) as session:
        session.register_hook(
            "HasEnemyFainted",
            lambda current: current.write_symbol_bytes("wEnemyMonHP", b"\0\0"),
        )
        _start_object_battle(
            session,
            scenario,
            constants,
            menu_cursor=1,
            description="Giovanni retry battle",
        )
        advance_with_a_until(
            session,
            lambda current: _event(current, constants, "EVENT_BEAT_GIOVANNI")
            and current.read_symbol("wScriptMode") == 0,
            max_frames,
            "Giovanni victory and cave blackout",
        )
        assert _event(session, constants, "EVENT_GIOVANNI_RETURNED")
        assert _event(session, constants, "EVENT_BEAT_GIOVANNI")
        assert not any(
            _event(session, constants, name)
            for name, _ in scenario["events"]["trainers"][1:]
        )
        masks = session.read_symbol_bytes("wObjectMasks", 13)[1:]
        assert masks[0] == 0
        assert masks[1:8] == b"\xff" * 7
        assert masks[8:12] == b"\0" * 4
        session.tap("up", 2, 30)
        assert session.read_symbol("wYCoord") == 4


@pytest.mark.parametrize(
    ("transformed", "species"),
    [(False, "MEWTWO"), (True, "MEW")],
)
@pytest.mark.parametrize("outcome", ["knockout", "escape"])
def test_counterpart_non_capture_results_leave_a_healthy_branch_exact_retry(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
    transformed: bool,
    species: str,
    outcome: str,
) -> None:
    constants = phase_10_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="CERULEAN_CAVE",
        x=19,
        y=3,
        events={
            "EVENT_PROJECT_MEW_RESOLVED": True,
            "EVENT_PROJECT_MEW_TRANSFORMED": transformed,
            "EVENT_SILVER_BIRD_RELEASED": True,
            "EVENT_BEAT_GIOVANNI": True,
        },
        before_overworld=_prepare_party(constants, master_ball=False),
    ) as session:
        variable_index = (
            constants["SPRITE_PROJECT_MEW_SUBJECT"] - constants["SPRITE_VARS"]
        )
        assert session.read_symbol_bytes("wVariableSprites", 16)[variable_index] == constants[
            f"SPRITE_{species}"
        ]
        session.register_hook("CheckCaughtPokemon")
        _start_object_battle(
            session,
            scenario,
            constants,
            menu_cursor=1 if outcome == "knockout" else 4,
            description=f"Cerulean counterpart {outcome} battle",
        )
        assert session.read_symbol("wEnemyMonSpecies") == constants[species]
        assert session.read_symbol("wEnemyMonLevel") == 70
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
        checked = session.hook_history.count("CheckCaughtPokemon") + 1
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: current.hook_history.count("CheckCaughtPokemon") >= checked,
            max_frames,
            f"counterpart {outcome} capture check",
        )
        advance_with_a_until(
            session,
            lambda current: current.read_symbol("wScriptMode") == 0,
            max_frames,
            f"counterpart {outcome} map return",
        )
        assert not _event(session, constants, "EVENT_CAUGHT_CERULEAN_CAVE_COUNTERPART")
        assert session.read_symbol("wMap1ObjectStructID") != 0xFF

        _start_object_battle(
            session,
            scenario,
            constants,
            menu_cursor=1,
            description="healthy counterpart retry",
        )
        assert session.read_symbol("wEnemyMonSpecies") == constants[species]
        assert session.read_symbol_bytes("wEnemyMonHP", 2) == session.read_symbol_bytes(
            "wEnemyMonMaxHP", 2
        )
        assert session.read_symbol("wEnemyMonStatus") == 0


def test_counterpart_player_loss_keeps_completion_clear(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
) -> None:
    constants = phase_10_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="CERULEAN_CAVE",
        x=19,
        y=3,
        events={
            "EVENT_PROJECT_MEW_RESOLVED": True,
            "EVENT_PROJECT_MEW_TRANSFORMED": False,
            "EVENT_SILVER_BIRD_RELEASED": True,
            "EVENT_BEAT_GIOVANNI": True,
        },
        before_overworld=_prepare_party(constants, master_ball=False, strong=False),
    ) as session:
        session.register_hook("CheckCaughtPokemon")
        _start_object_battle(
            session,
            scenario,
            constants,
            menu_cursor=1,
            description="counterpart player-loss battle",
        )
        session.register_hook(
            "HasPlayerFainted",
            lambda current: current.write_symbol_bytes("wBattleMonHP", b"\0\0"),
        )
        checked = session.hook_history.count("CheckCaughtPokemon") + 1
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: current.hook_history.count("CheckCaughtPokemon") >= checked
            and current.read_symbol("wBattleMode") == 0,
            max_frames,
            "counterpart player-loss result",
        )
        assert not _event(session, constants, "EVENT_CAUGHT_CERULEAN_CAVE_COUNTERPART")


def test_counterpart_full_storage_rejection_is_atomic_and_retryable(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
) -> None:
    constants = phase_10_runtime_constants
    max_frames = scenario["max_frames_per_step"]

    def prepare_full_storage(session) -> None:
        _prepare_party(constants, master_ball=True)(session)
        set_party_full(session, constants["EEVEE"], constants["PARTY_LENGTH"])
        set_current_box_full(session, constants["EEVEE"], constants["MONS_PER_BOX"])

    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="CERULEAN_CAVE",
        x=19,
        y=3,
        events={
            "EVENT_PROJECT_MEW_RESOLVED": True,
            "EVENT_PROJECT_MEW_TRANSFORMED": False,
            "EVENT_SILVER_BIRD_RELEASED": True,
            "EVENT_BEAT_GIOVANNI": True,
        },
        before_overworld=prepare_full_storage,
    ) as session:
        session.register_hook("PokeBallEffect")
        session.register_hook("Ball_BoxIsFullMessage")
        _start_object_battle(
            session,
            scenario,
            constants,
            menu_cursor=3,
            description="full-storage counterpart battle",
        )
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: "PokeBallEffect" in current.hook_history,
            max_frames,
            "full-storage counterpart Master Ball use",
        )
        advance_with_a_until(
            session,
            lambda current: "Ball_BoxIsFullMessage" in current.hook_history,
            max_frames,
            "full-storage counterpart ball rejection",
        )
        assert not _event(
            session, constants, "EVENT_CAUGHT_CERULEAN_CAVE_COUNTERPART"
        )
        assert read_progress(session).inventory.balls == (
            (constants["MASTER_BALL"], 1),
        )

        clear_current_box(session)
        session.tap("a", 2, 20)
        battle_menus = session.hook_history.count("BattleMenu")
        start = session.frames
        while (
            session.hook_history.count("BattleMenu") == battle_menus
            and session.frames - start < max_frames
        ):
            session.tap("b", 2, 20)
        assert session.hook_history.count("BattleMenu") > battle_menus
        ball_effects = session.hook_history.count("PokeBallEffect")
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: current.hook_history.count("PokeBallEffect")
            > ball_effects,
            max_frames,
            "counterpart Master Ball retry after opening box space",
        )
        advance_with_a_until(
            session,
            lambda current: _event(
                current, constants, "EVENT_CAUGHT_CERULEAN_CAVE_COUNTERPART"
            ),
            max_frames,
            "counterpart capture after opening box space",
        )
        assert read_progress(session).owns(constants["MEWTWO"])


@pytest.mark.parametrize(
    ("transformed", "species"),
    [(False, "MEWTWO"), (True, "MEW")],
)
def test_counterpart_capture_and_absence_survive_native_continue(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_10_runtime_constants: dict[str, int],
    transformed: bool,
    species: str,
) -> None:
    constants = phase_10_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    persisted = tmp_path / f"{species.lower()}-captured.sav"
    with loaded_phase_10_checkpoint(
        repo_root,
        tmp_path / "initial",
        constants,
        scenario,
        map_name="CERULEAN_CAVE",
        x=19,
        y=3,
        events={
            "EVENT_PROJECT_MEW_RESOLVED": True,
            "EVENT_PROJECT_MEW_TRANSFORMED": transformed,
            "EVENT_SILVER_BIRD_RELEASED": True,
            "EVENT_BEAT_GIOVANNI": True,
        },
        before_overworld=_prepare_party(constants, master_ball=True),
    ) as session:
        _start_object_battle(
            session,
            scenario,
            constants,
            menu_cursor=3,
            description=f"{species} capture battle",
        )
        assert session.read_symbol("wEnemyMonSpecies") == constants[species]
        session.register_hook("PokeBallEffect")
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: "PokeBallEffect" in current.hook_history,
            max_frames,
            f"{species} Master Ball use",
        )
        advance_with_a_until(
            session,
            lambda current: _event(
                current, constants, "EVENT_CAUGHT_CERULEAN_CAVE_COUNTERPART"
            ),
            max_frames,
            f"{species} counterpart capture",
        )
        result = session.read_symbol("wBattleResult")
        advance_with_a_until(
            session,
            lambda current: current.read_symbol("wScriptMode") == 0,
            max_frames,
            f"{species} capture map return",
        )
        assert result & (1 << constants["BATTLERESULT_CAUGHT_POKEMON"])
        assert read_progress(session).owns(constants[species])
        assert session.read_symbol("wMap1ObjectStructID") == 0xFF
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, persisted)

    with loaded_phase_10_saved_game(
        repo_root,
        tmp_path / "reload",
        constants,
        scenario,
        persisted,
    ) as session:
        assert _event(session, constants, "EVENT_BEAT_GIOVANNI")
        assert _event(session, constants, "EVENT_CAUGHT_CERULEAN_CAVE_COUNTERPART")
        assert _event(session, constants, "EVENT_PROJECT_MEW_TRANSFORMED") is transformed
        assert read_progress(session).owns(constants[species])
        assert session.read_symbol("wMap1ObjectStructID") == 0xFF
        wait_for_idle(session, max_frames)
