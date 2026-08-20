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
        "ENGINE_SOULBADGE",
        "EVENT_GOT_TM19_GIGA_DRAIN",
        "EVENT_TRAINERS_IN_CERULEAN_GYM",
        "EVENT_CERULEAN_GYM_ROCKET",
        "PARTY_LENGTH",
        "MONS_PER_BOX",
        "MAX_KEY_ITEMS",
        "MAX_ITEMS",
        "MAX_BALLS",
        "BICYCLE",
        "BLAINES_LOG",
        "POTION",
        "POKE_BALL",
        "ULTRA_BALL",
        "MAX_REVIVE",
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
        "GROUP_SAFARI_ZONE_WARDENS_HOME",
        "MAP_SAFARI_ZONE_WARDENS_HOME",
        "GROUP_FUCHSIA_CITY",
        "MAP_FUCHSIA_CITY",
        "GROUP_SAFARI_ZONE_FUCHSIA_GATE_BETA",
        "MAP_SAFARI_ZONE_FUCHSIA_GATE_BETA",
        "GROUP_SAFARI_ZONE_BETA",
        "MAP_SAFARI_ZONE_BETA",
        "EVENT_TALKED_TO_WARDENS_GRANDDAUGHTER",
        "EVENT_SAFARI_ZONE_ACCESSIBLE",
        "EVENT_SAFARI_ZONE_BETA_ULTRA_BALL",
        "EVENT_SAFARI_ZONE_BETA_MAX_REVIVE",
        "MORN",
        "DAY",
        "NITE",
        "MORN_F",
        "DAY_F",
        "NITE_F",
        "PLAYER_SURF",
        "COLL_WATER_21",
        "COLL_WATER",
        "BATTLETYPE_NORMAL",
        "WILD_BATTLE",
        "MANKEY",
        "MAREEP",
        "VULPIX",
        "REMORAID",
        "MUK",
        "ARTICUNO",
        "MASTER_BALL",
        "BALL_POCKET",
        "ITEM_POCKET",
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


def _interact_with_wardens_granddaughter(session, max_frames: int) -> None:
    session.enable_script_tracing()
    session.tap("left", 2, 10)
    session.tap("a", 2, 10)
    session.wait_for_script("WardensGranddaughter", max_frames)
    _finish_overworld_script(session, max_frames)


def _set_soul_badge(session, constants: dict[str, int]) -> None:
    bit = constants["ENGINE_SOULBADGE"] - constants["ENGINE_BOULDERBADGE"]
    session.write_symbol(
        "wKantoBadges", session.read_symbol("wKantoBadges") | (1 << bit)
    )


@pytest.mark.parametrize("badge_first", [False, True], ids=["talk-first", "badge-first"])
def test_safari_access_orders_converge_only_in_the_granddaughter_conversation(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    badge_first: bool,
) -> None:
    constants = phase_9_constants
    owner = scenario["safari"]["quest_owner"]
    initial_badges = (owner["badge"],) if badge_first else ()
    persisted = tmp_path / "safari-access.sav"
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name=owner["map"],
        x=3,
        y=4,
        events={
            owner["first_talk_event"]: False,
            owner["access_event"]: False,
        },
        badges=initial_badges,
    ) as session:
        _interact_with_wardens_granddaughter(
            session, scenario["max_frames_per_step"]
        )
        assert event_is_set(session, constants[owner["first_talk_event"]])
        assert event_is_set(session, constants[owner["access_event"]]) is badge_first
        if not badge_first:
            _set_soul_badge(session, constants)
            _interact_with_wardens_granddaughter(
                session, scenario["max_frames_per_step"]
            )
            assert event_is_set(session, constants[owner["access_event"]])
        save_game_from_overworld(session, scenario["max_frames_per_step"])
        dump_battery_ram(session, persisted)

    with loaded_phase_9_saved_game(
        repo_root,
        tmp_path / "reload",
        constants,
        scenario,
        persisted,
    ) as session:
        assert event_is_set(session, constants[owner["first_talk_event"]])
        assert event_is_set(session, constants[owner["access_event"]])


def _loaded_block(session, x: int, y: int) -> int:
    width = session.read_symbol("wMapWidth")
    row_width = width + 6
    offset = row_width * 3 + 3 + (y // 2) * row_width + (x // 2)
    return session.read_symbol_bytes("wOverworldMapBlocks", offset + 1)[offset]


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


def test_fuchsia_gate_stays_solid_until_access_then_round_trips_through_safari(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
) -> None:
    constants = phase_9_constants
    safari = scenario["safari"]
    access = safari["quest_owner"]["access_event"]
    gate = safari["fuchsia_gate"]
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "locked",
        constants,
        scenario,
        map_name="FUCHSIA_CITY",
        x=18,
        y=4,
        events={access: False},
    ) as session:
        assert _loaded_block(session, *gate["block_coordinate"]) == gate[
            "closed_block"
        ]
        session.tap("up", 2, 30)
        assert session.read_symbol("wMapGroup") == constants["GROUP_FUCHSIA_CITY"]
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            18,
            4,
        )

    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "open",
        constants,
        scenario,
        map_name="FUCHSIA_CITY",
        x=18,
        y=4,
        events={access: True},
    ) as session:
        assert _loaded_block(session, *gate["block_coordinate"]) == gate["open_block"]
        _walk_until_map(
            session,
            "up",
            constants,
            "SAFARI_ZONE_FUCHSIA_GATE_BETA",
            max_frames,
        )
        assert session.read_symbol("wMap1ObjectStructID") == 0xFF
        _walk_until_map(
            session, "up", constants, "SAFARI_ZONE_BETA", max_frames
        )
        assert session.read_symbol("wMapGroup") == constants["GROUP_SAFARI_ZONE_BETA"]
        walk_steps(session, "up", "wYCoord", -1, 1, max_frames)
        _walk_until_map(
            session,
            "down",
            constants,
            "SAFARI_ZONE_FUCHSIA_GATE_BETA",
            max_frames,
        )
        _walk_until_map(session, "down", constants, "FUCHSIA_CITY", max_frames)
        assert _loaded_block(session, *gate["block_coordinate"]) == gate["open_block"]


@pytest.mark.parametrize("pickup_index", [0, 1], ids=["ultra-ball", "max-revive"])
def test_safari_pickups_retry_when_items_are_full_and_finalize_independently(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    pickup_index: int,
) -> None:
    constants = phase_9_constants
    pickup = scenario["safari"]["preserve"]["pickups"][pickup_index]
    x, y = pickup["coordinate"]
    max_frames = scenario["max_frames_per_step"]
    persisted = tmp_path / f"{pickup['item'].lower()}-collected.sav"
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="SAFARI_ZONE_BETA",
        x=x,
        y=y + 1,
        events={
            "EVENT_SAFARI_ZONE_BETA_ULTRA_BALL": False,
            "EVENT_SAFARI_ZONE_BETA_MAX_REVIVE": False,
        },
    ) as session:
        object_label = f"wMap{pickup_index + 1}ObjectStructID"
        session.wait_until(
            lambda current: current.read_symbol(object_label) != 0xFF,
            max_frames,
            f"{pickup['item']} object to load",
        )
        if pickup["pocket"] == "BALL_POCKET":
            count_label = "wNumBalls"
            entries_label = "wBalls"
            capacity = constants["MAX_BALLS"]
            filler = constants["POKE_BALL"]
            inventory_pocket = "balls"
        else:
            count_label = "wNumItems"
            entries_label = "wItems"
            capacity = constants["MAX_ITEMS"]
            filler = constants["POTION"]
            inventory_pocket = "items"
        session.write_symbol(count_label, capacity)
        session.write_symbol_bytes(
            entries_label,
            bytes([filler, 1] * capacity + [0xFF]),
        )
        session.tap("up", 2, 10)
        session.tap("a", 2, 10)
        _finish_overworld_script(session, max_frames)
        assert not event_is_set(session, constants[pickup["event"]])
        assert session.read_symbol(object_label) != 0xFF

        session.write_symbol(count_label, capacity - 1)
        session.write_symbol_bytes(
            entries_label,
            bytes([filler, 1] * (capacity - 1) + [0xFF]),
        )
        session.tap("a", 2, 10)
        _finish_overworld_script(session, max_frames)
        assert event_is_set(session, constants[pickup["event"]])
        assert session.read_symbol(object_label) == 0xFF
        assert sum(
            quantity
            for item, quantity in getattr(
                read_progress(session).inventory, inventory_pocket
            )
            if item == constants[pickup["item"]]
        ) == pickup["quantity"]
        other = scenario["safari"]["preserve"]["pickups"][1 - pickup_index]
        assert not event_is_set(session, constants[other["event"]])
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, persisted)

    with loaded_phase_9_saved_game(
        repo_root,
        tmp_path / "reload",
        constants,
        scenario,
        persisted,
    ) as session:
        assert session.read_symbol("wMapGroup") == constants["GROUP_SAFARI_ZONE_BETA"]
        assert session.read_symbol("wMapNumber") == constants["MAP_SAFARI_ZONE_BETA"]
        assert event_is_set(session, constants[pickup["event"]])
        assert not event_is_set(session, constants[other["event"]])
        assert session.read_symbol(object_label) == 0xFF
        assert sum(
            quantity
            for item, quantity in getattr(
                read_progress(session).inventory, inventory_pocket
            )
            if item == constants[pickup["item"]]
        ) == pickup["quantity"]


def _force_wild_selection(session, selection: int) -> None:
    if selection not in range(100):
        raise ValueError("wild selection must be in 0..99")
    start = session.symbols["ChooseWildEncounter.randomloop"]
    end = session.symbols["ChooseWildEncounter.got_it"]
    random = session.symbols["Random"]
    rom = session.prepared.rom.read_bytes()
    physical_start = start.bank * 0x4000 + (start.address - 0x4000)
    physical_end = physical_start + (end.address - start.address)
    call = bytes([0xCD, random.address & 0xFF, random.address >> 8])
    call_offset = rom.find(call, physical_start, physical_end)
    if call_offset < 0:
        raise AssertionError("ChooseWildEncounter no longer calls Random")
    after_call = start.address + (call_offset - physical_start) + len(call)

    def force(current) -> None:
        current.pyboy.register_file.A = selection

    session.pyboy.hook_register(start.bank, after_call, force, session)


def _start_safari_wild_battle(
    session,
    constants: dict[str, int],
    scenario: dict,
    *,
    time: str,
    selection: int,
    water: bool,
    battle_cursor: int | None = None,
) -> None:
    max_frames = scenario["max_frames_per_step"]
    session.write_symbol("wTimeOfDay", constants[f"{time}_F"])
    prepare_battle_party(session, constants, constants["ARTICUNO"], should_win=True)
    session.register_hook(
        "ChooseWildEncounter",
        lambda current: current.write_symbol(
            "wTimeOfDay", constants[f"{time}_F"]
        ),
    )
    session.register_hook(
        "BattleMenu",
        (
            lambda current: current.write_symbol(
                "wBattleMenuCursorPosition", battle_cursor
            )
        )
        if battle_cursor is not None
        else None,
    )
    session.register_hook("SafariBattleMenu")
    _force_wild_selection(session, selection)
    session.write_symbol_bytes("wMornEncounterRate", b"\xff\xff\xff\xff")
    if water:
        directions = ("right", "right", "left", "left")
    else:
        place_player(session, 4, 2)
        directions = ("right",)
    start = session.frames
    index = 0
    while (
        "BattleMenu" not in session.hook_history
        and session.frames - start < max_frames
    ):
        if session.read_symbol("wBattleMode") or session.read_symbol("wScriptMode"):
            session.tap("a", 2, 20)
        else:
            session.tap(directions[index % len(directions)], 2, 12)
            index += 1
    session.wait_for_hook("BattleMenu", max_frames)


@pytest.mark.parametrize(
    ("time", "species"),
    [("MORN", "MANKEY"), ("DAY", "MAREEP"), ("NITE", "VULPIX")],
    ids=["morning-mankey", "day-mareep", "night-vulpix"],
)
def test_safari_common_grass_slots_start_normal_battles_with_pack_access(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    time: str,
    species: str,
) -> None:
    constants = phase_9_constants
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="SAFARI_ZONE_BETA",
        x=4,
        y=2,
    ) as session:
        assert session.read_symbol_bytes("wMornEncounterRate", 4) == bytes(
            [25, 25, 25, 15]
        )
        session.write_symbol("wSafariBallsRemaining", 17)
        session.write_symbol_bytes("wSafariTimeRemaining", b"\x12\x34")
        safari_state = session.read_symbol_bytes("wSafariBallsRemaining", 3)
        if species == "MANKEY":
            session.register_hook("BattlePack")
        _start_safari_wild_battle(
            session,
            constants,
            scenario,
            time=time,
            selection=0,
            water=False,
            battle_cursor=3 if species == "MANKEY" else None,
        )
        assert session.read_symbol("wBattleType") == constants["BATTLETYPE_NORMAL"]
        assert session.read_symbol("wBattleMode") == constants["WILD_BATTLE"]
        assert session.read_symbol("wEnemyMonSpecies") == constants[species]
        assert session.read_symbol("wEnemyMonLevel") == {
            "MANKEY": 22,
            "MAREEP": 20,
            "VULPIX": 24,
        }[species]
        assert "SafariBattleMenu" not in session.hook_history
        assert session.read_symbol_bytes("wSafariBallsRemaining", 3) == safari_state
        if species == "MANKEY":
            session.tap("a", 2, 10)
            session.wait_for_hook("BattlePack", scenario["max_frames_per_step"])


def test_safari_water_slot_uses_remoraid_in_a_normal_surf_battle(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
) -> None:
    constants = phase_9_constants
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="SAFARI_ZONE_BETA",
        x=12,
        y=4,
        player_state="PLAYER_SURF",
    ) as session:
        assert session.read_symbol("wPlayerState") == constants["PLAYER_SURF"]
        assert session.read_symbol("wPlayerTileCollision") == constants[
            "COLL_WATER"
        ]
        _start_safari_wild_battle(
            session,
            constants,
            scenario,
            time="MORN",
            selection=0,
            water=True,
        )
        assert session.read_symbol("wBattleType") == constants["BATTLETYPE_NORMAL"]
        assert session.read_symbol("wBattleMode") == constants["WILD_BATTLE"]
        assert session.read_symbol("wEnemyMonSpecies") == constants["REMORAID"]
        assert 22 <= session.read_symbol("wEnemyMonLevel") <= 26
        assert "SafariBattleMenu" not in session.hook_history
