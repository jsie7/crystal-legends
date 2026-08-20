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
    interact_with_gift,
    set_current_box_full,
    set_party_full,
)
from tests.support.legendary_scenario import (
    advance_with_a_until,
    place_player,
    prepare_battle_party,
    walk_steps,
)
from tests.support.phase_09_scenario import (
    loaded_phase_9_gift_checkpoint,
    loaded_phase_9_map_checkpoint,
    loaded_phase_9_saved_game,
)
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.emulator, pytest.mark.phase9]


def _gift_scenario(scenario: dict, gift: dict) -> dict:
    return {**gift, "max_frames_per_step": scenario["max_frames_per_step"]}


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (
            repo_root
            / "tests/fixtures/scenarios/phase_09_kanto_completion.json"
        ).read_text()
    )


@pytest.fixture(scope="module")
def phase_9_constants(
    repo_root: Path, tmp_path_factory, scenario: dict
) -> dict[str, int]:
    names = {
        "SPAWN_N_A",
        "MAPSETUP_WARP",
        "ENGINE_BOULDERBADGE",
        "EVENT_GOT_TM19_GIGA_DRAIN",
        "EVENT_TRAINERS_IN_CERULEAN_GYM",
        "EVENT_CERULEAN_GYM_ROCKET",
        "PARTY_LENGTH",
        "MONS_PER_BOX",
        "MAX_KEY_ITEMS",
        "BICYCLE",
        "BLAINES_LOG",
        "EEVEE",
        "GROUP_CINNABAR_ISLAND",
        "MAP_CINNABAR_ISLAND",
        "GROUP_CINNABAR_POKECENTER_1F",
        "MAP_CINNABAR_POKECENTER_1F",
        "EVENT_BLUE_IN_CINNABAR",
        "EVENT_LEARNED_LOCATION_OF_BLAINES_LOG",
        "EVENT_RECOVERED_BLAINES_LOG",
        "EVENT_RETURNED_BLAINES_LOG",
        "GROUP_CELADON_CITY",
        "MAP_CELADON_CITY",
        "MUK",
        "ARTICUNO",
        "MASTER_BALL",
        "BALL_POCKET",
        "WIN",
        "LOSE",
        "DRAW",
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
    for gift in scenario["gifts"]:
        names.update(
            {
                gift["species"],
                gift["badge"],
                gift["service_event"],
                gift["completion_event"],
                f"GROUP_{gift['map']}",
                f"MAP_{gift['map']}",
                *gift["generated_moves"],
            }
        )
    constants = resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_9_runtime_constants"),
        sorted(names),
    )
    symbols = SymbolTable.parse((repo_root / scenario["symbols"]).read_text())
    constants["SCENE_CERULEANGYM_NOOP"] = symbols.constant(
        "SCENE_CERULEANGYM_NOOP"
    )
    return constants


@pytest.mark.parametrize("gift_index", [0, 1, 2], ids=["erika", "misty", "blaine"])
def test_kanto_gifts_require_service_and_declines_remain_retryable(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    gift_index: int,
) -> None:
    gift = scenario["gifts"][gift_index]
    completion = phase_9_constants[gift["completion_event"]]
    with loaded_phase_9_gift_checkpoint(
        repo_root,
        tmp_path / f"{gift['species']}-not-ready",
        phase_9_constants,
        scenario,
        gift,
        service_complete=False,
    ) as session:
        yes_no_count = session.hook_history.count("_YesNoBox")
        assert interact_with_gift(
            session, _gift_scenario(scenario, gift), accept=None
        ) is None
        assert session.hook_history.count("_YesNoBox") == yes_no_count
        assert not event_is_set(session, completion)
        assert read_progress(session).party.count == 0

    with loaded_phase_9_gift_checkpoint(
        repo_root,
        tmp_path / f"{gift['species']}-decline",
        phase_9_constants,
        scenario,
        gift,
        service_complete=True,
    ) as session:
        assert interact_with_gift(
            session, _gift_scenario(scenario, gift), accept=False
        ) is None
        assert not event_is_set(session, completion)
        assert interact_with_gift(
            session, _gift_scenario(scenario, gift), accept=False
        ) is None
        assert session.script_history.count(gift["script"]) == 2


@pytest.mark.parametrize("destination", ["party", "current-box"])
@pytest.mark.parametrize("gift_index", [0, 1, 2], ids=["erika", "misty", "blaine"])
def test_kanto_gifts_deliver_generated_level_28_moves_and_finalize_once(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    gift_index: int,
    destination: str,
) -> None:
    gift = scenario["gifts"][gift_index]
    species = phase_9_constants[gift["species"]]
    completion = phase_9_constants[gift["completion_event"]]
    with loaded_phase_9_gift_checkpoint(
        repo_root,
        tmp_path / f"{gift['species']}-{destination}",
        phase_9_constants,
        scenario,
        gift,
        service_complete=True,
    ) as session:
        if destination == "current-box":
            set_party_full(
                session,
                phase_9_constants["EEVEE"],
                phase_9_constants["PARTY_LENGTH"],
            )
        expected_destination = 0 if destination == "party" else 1
        assert (
            interact_with_gift(
                session, _gift_scenario(scenario, gift), accept=True
            )
            == expected_destination
        )
        assert event_is_set(session, completion)
        for other in scenario["gifts"]:
            if other is not gift:
                assert not event_is_set(
                    session, phase_9_constants[other["completion_event"]]
                )
        progress = read_progress(session)
        assert progress.owns(species)
        prefix = "wPartyMon1" if destination == "party" else "sBoxMon1"
        assert session.read_symbol(f"{prefix}Level") == gift["level"]
        assert session.read_symbol_bytes(f"{prefix}Moves", 4) == bytes(
            phase_9_constants[move] for move in gift["generated_moves"]
        )
        yes_no_count = session.hook_history.count("_YesNoBox")
        before_repeat = read_progress(session)
        session.tap("a", 2, 30)
        assert session.hook_history.count("_YesNoBox") == yes_no_count
        assert read_progress(session) == before_repeat


@pytest.mark.parametrize("gift_index", [0, 1, 2], ids=["erika", "misty", "blaine"])
def test_kanto_gifts_are_atomic_when_party_and_current_box_are_full(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    gift_index: int,
) -> None:
    gift = scenario["gifts"][gift_index]
    species = phase_9_constants[gift["species"]]
    completion = phase_9_constants[gift["completion_event"]]
    filler = phase_9_constants["EEVEE"]
    with loaded_phase_9_gift_checkpoint(
        repo_root,
        tmp_path / gift["species"],
        phase_9_constants,
        scenario,
        gift,
        service_complete=True,
    ) as session:
        set_party_full(session, filler, phase_9_constants["PARTY_LENGTH"])
        set_current_box_full(session, filler, phase_9_constants["MONS_PER_BOX"])
        before = read_progress(session)
        gift_scenario = _gift_scenario(scenario, gift)
        assert interact_with_gift(session, gift_scenario, accept=True) == 2
        assert not event_is_set(session, completion)
        assert read_progress(session) == before

        clear_current_box(session)
        assert interact_with_gift(session, gift_scenario, accept=True) == 1
        assert event_is_set(session, completion)
        assert read_progress(session).current_box.species == (species,)


@pytest.mark.parametrize("gift_index", [0, 1, 2], ids=["erika", "misty", "blaine"])
def test_kanto_gift_completion_survives_native_continue_without_duplication(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    gift_index: int,
) -> None:
    gift = scenario["gifts"][gift_index]
    species = phase_9_constants[gift["species"]]
    completion = phase_9_constants[gift["completion_event"]]
    persisted = tmp_path / f"{gift['species'].lower()}-complete.sav"
    with loaded_phase_9_gift_checkpoint(
        repo_root,
        tmp_path / "initial",
        phase_9_constants,
        scenario,
        gift,
        service_complete=True,
    ) as session:
        assert (
            interact_with_gift(
                session, _gift_scenario(scenario, gift), accept=True
            )
            == 0
        )
        save_game_from_overworld(session, scenario["max_frames_per_step"])
        dump_battery_ram(session, persisted)

    with loaded_phase_9_saved_game(
        repo_root,
        tmp_path / "reload",
        phase_9_constants,
        scenario,
        persisted,
    ) as session:
        assert event_is_set(session, completion)
        assert read_progress(session).party.species == (species,)
        session.register_hook("_YesNoBox")
        session.tap(gift["start"]["facing"].lower(), 2, 10)
        session.tap("a", 2, 10)
        _finish_overworld_script(session, scenario["max_frames_per_step"])
        assert "_YesNoBox" not in session.hook_history
        assert read_progress(session).party.species == (species,)


def _finish_overworld_script(session, max_frames: int) -> None:
    advance_with_a_until(
        session,
        lambda current: current.read_symbol("wScriptMode") == 0,
        max_frames,
        "Phase 9 overworld script completion",
    )
    wait_for_idle(session, max_frames)


def test_cinnabar_staircase_survivor_clue_and_log_capacity_are_runtime_safe(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
) -> None:
    constants = phase_9_constants
    max_frames = scenario["max_frames_per_step"]
    common_events = {
        "EVENT_BLUE_IN_CINNABAR": True,
        "EVENT_RECOVERED_BLAINES_LOG": False,
    }

    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "stairs",
        constants,
        scenario,
        map_name="CINNABAR_ISLAND",
        x=7,
        y=6,
        events=common_events,
    ) as session:
        place_player(session, 7, 6)
        walk_steps(session, "up", "wYCoord", -1, 2, max_frames)
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            7,
            4,
        )
        walk_steps(session, "down", "wYCoord", 1, 2, max_frames)

    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "fisher",
        constants,
        scenario,
        map_name="CINNABAR_POKECENTER_1F",
        x=2,
        y=5,
        events={"EVENT_RECOVERED_BLAINES_LOG": False},
        badges=("ENGINE_VOLCANOBADGE",),
    ) as session:
        session.enable_script_tracing()
        session.tap("up", 2, 10)
        session.tap("a", 2, 10)
        session.wait_for_script("CinnabarPokecenter1FFisherScript", max_frames)
        _finish_overworld_script(session, max_frames)
        assert event_is_set(
            session, constants["EVENT_LEARNED_LOCATION_OF_BLAINES_LOG"]
        )

    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "case-before-clue",
        constants,
        scenario,
        map_name="CINNABAR_ISLAND",
        x=13,
        y=7,
        events={
            **common_events,
            "EVENT_LEARNED_LOCATION_OF_BLAINES_LOG": False,
        },
    ) as session:
        session.enable_script_tracing()
        session.tap("up", 2, 10)
        session.tap("a", 2, 10)
        session.wait_for_script("CinnabarIslandBlainesLogRubble", max_frames)
        _finish_overworld_script(session, max_frames)
        assert not event_is_set(
            session, constants["EVENT_RECOVERED_BLAINES_LOG"]
        )
        assert constants["BLAINES_LOG"] not in read_progress(session).inventory.key_items

    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "case-full-pocket",
        constants,
        scenario,
        map_name="CINNABAR_ISLAND",
        x=13,
        y=7,
        events={
            **common_events,
            "EVENT_LEARNED_LOCATION_OF_BLAINES_LOG": True,
        },
    ) as session:
        session.write_symbol("wNumKeyItems", constants["MAX_KEY_ITEMS"])
        session.write_symbol_bytes(
            "wKeyItems",
            bytes(
                [constants["BICYCLE"]] * constants["MAX_KEY_ITEMS"] + [0xFF]
            ),
        )
        session.enable_script_tracing()
        session.tap("up", 2, 10)
        session.tap("a", 2, 10)
        session.wait_for_script("CinnabarIslandBlainesLogRubble", max_frames)
        _finish_overworld_script(session, max_frames)
        assert not event_is_set(
            session, constants["EVENT_RECOVERED_BLAINES_LOG"]
        )

        session.write_symbol("wNumKeyItems", 0)
        session.write_symbol("wKeyItems", 0xFF)
        session.tap("a", 2, 10)
        _finish_overworld_script(session, max_frames)
        assert event_is_set(session, constants["EVENT_RECOVERED_BLAINES_LOG"])
        assert read_progress(session).inventory.key_items == (
            constants["BLAINES_LOG"],
        )


def test_blaine_consumes_the_log_before_retryable_charmander_storage(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
) -> None:
    gift = next(row for row in scenario["gifts"] if row["species"] == "CHARMANDER")
    constants = phase_9_constants
    filler = constants["EEVEE"]
    with loaded_phase_9_gift_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        gift,
        service_complete=False,
    ) as session:
        session.write_symbol("wNumKeyItems", 1)
        session.write_symbol_bytes(
            "wKeyItems", bytes([constants["BLAINES_LOG"], 0xFF])
        )
        set_party_full(session, filler, constants["PARTY_LENGTH"])
        set_current_box_full(session, filler, constants["MONS_PER_BOX"])
        gift_scenario = _gift_scenario(scenario, gift)
        assert interact_with_gift(session, gift_scenario, accept=True) == 2
        assert event_is_set(session, constants["EVENT_RETURNED_BLAINES_LOG"])
        assert not event_is_set(
            session, constants["EVENT_GOT_CHARMANDER_FROM_BLAINE"]
        )
        assert constants["BLAINES_LOG"] not in read_progress(session).inventory.key_items

        clear_current_box(session)
        assert interact_with_gift(session, gift_scenario, accept=True) == 1
        assert event_is_set(
            session, constants["EVENT_GOT_CHARMANDER_FROM_BLAINE"]
        )


def _start_muk_battle(session, max_frames: int, menu_cursor: int) -> None:
    session.enable_script_tracing()
    for label in ("_YesNoBox", "VerticalMenu", "ExitBattle"):
        session.register_hook(label)
    session.register_hook(
        "BattleMenu",
        lambda current: current.write_symbol(
            "wBattleMenuCursorPosition", menu_cursor
        ),
    )
    yes_no_count = session.hook_history.count("_YesNoBox") + 1
    menu_count = session.hook_history.count("VerticalMenu") + 1
    battle_count = session.hook_history.count("BattleMenu") + 1
    session.tap("down", 2, 10)
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: (
            current.hook_history.count("_YesNoBox") >= yes_no_count
            and current.hook_history.count("VerticalMenu") >= menu_count
        ),
        max_frames,
        "Celadon pond confirmation",
    )
    session.tick(20)
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("BattleMenu") >= battle_count,
        max_frames,
        "Celadon Muk battle menu",
    )


def test_celadon_pond_is_badge_gated_and_decline_is_non_mutating(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
) -> None:
    constants = phase_9_constants
    max_frames = scenario["max_frames_per_step"]
    service = constants["EVENT_HELPED_ERIKA_CLEAN_CELADON_POND"]
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "no-badge",
        constants,
        scenario,
        map_name="CELADON_CITY",
        x=15,
        y=17,
        events={"EVENT_HELPED_ERIKA_CLEAN_CELADON_POND": False},
    ) as session:
        session.register_hook("_YesNoBox")
        before = read_progress(session)
        session.tap("down", 2, 10)
        session.tap("a", 2, 10)
        _finish_overworld_script(session, max_frames)
        assert "_YesNoBox" not in session.hook_history
        assert not event_is_set(session, service)
        assert read_progress(session) == before

    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "decline",
        constants,
        scenario,
        map_name="CELADON_CITY",
        x=15,
        y=17,
        events={"EVENT_HELPED_ERIKA_CLEAN_CELADON_POND": False},
        badges=("ENGINE_RAINBOWBADGE",),
    ) as session:
        session.register_hook("_YesNoBox")
        session.register_hook("VerticalMenu")
        session.tap("down", 2, 10)
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: (
                "_YesNoBox" in current.hook_history
                and "VerticalMenu" in current.hook_history
            ),
            max_frames,
            "Celadon pond decline menu",
        )
        session.tap("b", 2, 10)
        _finish_overworld_script(session, max_frames)
        assert not event_is_set(session, service)


@pytest.mark.parametrize("outcome", ["escape", "knockout", "capture"])
def test_celadon_muk_battle_outcomes_match_the_service_contract(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    outcome: str,
) -> None:
    constants = phase_9_constants
    max_frames = scenario["max_frames_per_step"]
    service = constants["EVENT_HELPED_ERIKA_CLEAN_CELADON_POND"]
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / outcome,
        constants,
        scenario,
        map_name="CELADON_CITY",
        x=15,
        y=17,
        events={"EVENT_HELPED_ERIKA_CLEAN_CELADON_POND": False},
        badges=("ENGINE_RAINBOWBADGE",),
    ) as session:
        prepare_battle_party(
            session, constants, constants["ARTICUNO"], should_win=True
        )
        if outcome == "capture":
            session.write_symbol("wNumBalls", 1)
            session.write_symbol_bytes(
                "wBalls", bytes([constants["MASTER_BALL"], 1, 0xFF])
            )
            session.write_symbol("wLastPocket", constants["BALL_POCKET"])
        menu_cursor = {"knockout": 1, "capture": 3, "escape": 4}[outcome]
        _start_muk_battle(session, max_frames, menu_cursor)
        assert session.read_symbol("wEnemyMonSpecies") == constants["MUK"]
        assert session.read_symbol("wEnemyMonLevel") == scenario["erika_task"]["level"]

        if outcome == "escape":
            session.write_symbol_bytes("wBattleMonSpeed", (999).to_bytes(2, "big"))
            session.write_symbol_bytes("wEnemyMonSpeed", (1).to_bytes(2, "big"))
            session.tap("a", 2, 10)
        elif outcome == "knockout":
            session.register_hook(
                "HasEnemyFainted",
                lambda current: current.write_symbol_bytes("wEnemyMonHP", b"\0\0"),
            )
            session.tap("a", 2, 10)
        else:
            session.tap("a", 2, 10)
            advance_with_a_until(
                session,
                lambda current: event_is_set(current, service),
                max_frames,
                "captured Muk service completion",
            )

        _finish_overworld_script(session, max_frames)
        assert event_is_set(session, service) is (outcome != "escape"), (
            outcome,
            session.read_symbol("wBattleResult"),
        )
        if outcome == "capture":
            assert read_progress(session).owns(constants["MUK"])


def test_celadon_muk_player_loss_leaves_service_pending(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
) -> None:
    constants = phase_9_constants
    max_frames = scenario["max_frames_per_step"]
    service = constants["EVENT_HELPED_ERIKA_CLEAN_CELADON_POND"]
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="CELADON_CITY",
        x=15,
        y=17,
        events={"EVENT_HELPED_ERIKA_CLEAN_CELADON_POND": False},
        badges=("ENGINE_RAINBOWBADGE",),
    ) as session:
        prepare_battle_party(
            session, constants, constants["ARTICUNO"], should_win=False
        )
        session.register_hook(
            "HasPlayerFainted",
            lambda current: current.write_symbol_bytes("wBattleMonHP", b"\0\0"),
        )
        _start_muk_battle(session, max_frames, 1)
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: current.read_symbol("wBattleMode") == 0,
            max_frames,
            "Muk player-loss whiteout",
        )
        assert not event_is_set(session, service)
