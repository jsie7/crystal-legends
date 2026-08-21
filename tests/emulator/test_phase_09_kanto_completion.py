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
    build_phase_9_gift_checkpoint,
    loaded_phase_9_gift_checkpoint,
    loaded_phase_9_map_checkpoint,
    loaded_phase_9_saved_game,
    relocate_phase_9_saved_game,
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
        "NEVERMELTICE",
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
        "EVENT_ERIKA_REQUESTED_CELADON_POND_HELP",
        "EVENT_BLAINE_REQUESTED_CINNABAR_HELP",
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
        "EVENT_ARTICUNO_AVAILABLE",
        "EVENT_ZAPDOS_AVAILABLE",
        "EVENT_MOLTRES_AVAILABLE",
        "EVENT_OAK_MOVED_THIRD_BIRD",
        "EVENT_GOT_ARTICUNO_FROM_ELM",
        "EVENT_GOT_ZAPDOS_FROM_ELM",
        "EVENT_GOT_MOLTRES_FROM_ELM",
        "EVENT_CAUGHT_ARTICUNO_IN_KANTO",
        "EVENT_CAUGHT_ZAPDOS_IN_KANTO",
        "EVENT_CAUGHT_MOLTRES_IN_KANTO",
        "EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION",
        "EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION",
        "EVENT_MOLTRES_NOT_AT_KANTO_LOCATION",
        "EVENT_SEAFOAM_ISLANDS_CAVE_ULTRA_BALL",
        "EVENT_SEAFOAM_ISLANDS_CAVE_HIDDEN_NEVERMELTICE",
        "EVENT_POWER_PLANT_ANNEX_AUTHORIZED",
        "EVENT_OPENED_POWER_PLANT_ANNEX",
        "EVENT_RESTORED_POWER_TO_KANTO",
        "EVENT_RETURNED_MACHINE_PART",
        "EVENT_GOT_TM07_ZAP_CANNON",
        "EVENT_BEAT_ELITE_FOUR",
        "GROUP_ROUTE_20",
        "MAP_ROUTE_20",
        "GROUP_SEAFOAM_ISLANDS_CAVE",
        "MAP_SEAFOAM_ISLANDS_CAVE",
        "GROUP_POWER_PLANT",
        "MAP_POWER_PLANT",
        "GROUP_POWER_PLANT_GENERATOR_ANNEX",
        "MAP_POWER_PLANT_GENERATOR_ANNEX",
        "GROUP_VICTORY_ROAD",
        "MAP_VICTORY_ROAD",
        "GROUP_OAKS_LAB",
        "MAP_OAKS_LAB",
        "MORN",
        "DAY",
        "NITE",
        "MORN_F",
        "DAY_F",
        "NITE_F",
        "PLAYER_SURF",
        "COLL_WATER_21",
        "COLL_WATER",
        "COLL_FLOOR",
        "COLL_ICE",
        "BATTLETYPE_NORMAL",
        "BATTLETYPE_KANTO_BIRD",
        "WILD_BATTLE",
        "MANKEY",
        "MAREEP",
        "VULPIX",
        "REMORAID",
        "MUK",
        "ARTICUNO",
        "ZAPDOS",
        "MOLTRES",
        "MASTER_BALL",
        "BALL_POCKET",
        "BATTLERESULT_CAUGHT_POKEMON",
        "OW_UP",
        "OW_DOWN",
        "OW_RIGHT",
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
        if gift["giver"] == "ERIKA":
            assert event_is_set(
                session,
                phase_9_constants["EVENT_ERIKA_REQUESTED_CELADON_POND_HELP"],
            )
        if gift["giver"] == "BLAINE":
            assert event_is_set(
                session,
                phase_9_constants["EVENT_BLAINE_REQUESTED_CINNABAR_HELP"],
            )

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
        assert session.read_symbol_bytes(f"{prefix}ID", 2) == gift[
            "ot_id"
        ].to_bytes(2, "big")
        symbols = SymbolTable.parse(
            (repo_root / scenario["symbols"]).read_text()
        )
        rom = (repo_root / scenario["rom"]).read_bytes()
        ot_symbol = symbols[f"{gift['giver'].title()}StarterOTName"]
        expected_ot = rom[
            ot_symbol.rom_offset : ot_symbol.rom_offset + len(gift["ot_name"]) + 1
        ]
        assert session.read_symbol_bytes(f"{prefix}OT", len(expected_ot)) == expected_ot
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
        tmp_path / "fisher-before-request",
        constants,
        scenario,
        map_name="CINNABAR_POKECENTER_1F",
        x=2,
        y=5,
        events={
            "EVENT_BLAINE_REQUESTED_CINNABAR_HELP": False,
            "EVENT_RECOVERED_BLAINES_LOG": False,
        },
        badges=("ENGINE_VOLCANOBADGE",),
    ) as session:
        session.enable_script_tracing()
        session.tap("up", 2, 10)
        session.tap("a", 2, 10)
        session.wait_for_script("CinnabarPokecenter1FFisherScript", max_frames)
        _finish_overworld_script(session, max_frames)
        assert not event_is_set(
            session, constants["EVENT_LEARNED_LOCATION_OF_BLAINES_LOG"]
        )

    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "fisher-after-request",
        constants,
        scenario,
        map_name="CINNABAR_POKECENTER_1F",
        x=2,
        y=5,
        events={
            "EVENT_BLAINE_REQUESTED_CINNABAR_HELP": True,
            "EVENT_RECOVERED_BLAINES_LOG": False,
        },
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
    session.register_hook("ExitBattle")
    session.register_hook(
        "BattleMenu",
        lambda current: current.write_symbol(
            "wBattleMenuCursorPosition", menu_cursor
        ),
    )
    battle_count = session.hook_history.count("BattleMenu") + 1
    walk_steps(session, "up", "wYCoord", -1, 1, max_frames)
    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("BattleMenu") >= battle_count,
        max_frames,
        "Celadon Muk battle menu",
    )


def test_celadon_pond_is_request_gated(
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
        session.register_hook("BattleMenu")
        before = read_progress(session)
        session.tap("down", 2, 10)
        session.tap("a", 2, 10)
        _finish_overworld_script(session, max_frames)
        assert "BattleMenu" not in session.hook_history
        assert not event_is_set(session, service)
        assert read_progress(session) == before

    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "not-requested",
        constants,
        scenario,
        map_name="CELADON_CITY",
        x=14,
        y=19,
        events={
            "EVENT_HELPED_ERIKA_CLEAN_CELADON_POND": False,
            "EVENT_ERIKA_REQUESTED_CELADON_POND_HELP": False,
        },
        badges=("ENGINE_RAINBOWBADGE",),
        player_state="PLAYER_SURF",
    ) as session:
        session.register_hook("BattleMenu")
        assert session.read_symbol("wPlayerState") == constants["PLAYER_SURF"]
        assert session.read_symbol("wPlayerTileCollision") in (
            constants["COLL_WATER"],
            constants["COLL_WATER_21"],
        )
        walk_steps(session, "up", "wYCoord", -1, 1, max_frames)
        _finish_overworld_script(session, max_frames)
        assert session.read_symbol("wYCoord") == 18
        assert "BattleMenu" not in session.hook_history
        assert not event_is_set(session, service)


@pytest.mark.parametrize("entry_x", [13, 14, 15])
def test_each_celadon_pond_entry_tile_starts_the_requested_muk_directly(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    entry_x: int,
) -> None:
    constants = phase_9_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="CELADON_CITY",
        x=entry_x,
        y=19,
        events={
            "EVENT_HELPED_ERIKA_CLEAN_CELADON_POND": False,
            "EVENT_ERIKA_REQUESTED_CELADON_POND_HELP": True,
        },
        badges=("ENGINE_RAINBOWBADGE",),
        player_state="PLAYER_SURF",
    ) as session:
        prepare_battle_party(
            session, constants, constants["ARTICUNO"], should_win=True
        )
        session.register_hook("_YesNoBox")
        session.register_hook("BattleMenu")
        walk_steps(session, "up", "wYCoord", -1, 1, max_frames)
        advance_with_a_until(
            session,
            lambda current: "BattleMenu" in current.hook_history,
            max_frames,
            f"Celadon pond entry at x={entry_x}",
        )
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            entry_x,
            18,
        )
        assert "_YesNoBox" not in session.hook_history


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
        y=19,
        events={
            "EVENT_HELPED_ERIKA_CLEAN_CELADON_POND": False,
            "EVENT_ERIKA_REQUESTED_CELADON_POND_HELP": True,
        },
        badges=("ENGINE_RAINBOWBADGE",),
        player_state="PLAYER_SURF",
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
        y=19,
        events={
            "EVENT_HELPED_ERIKA_CLEAN_CELADON_POND": False,
            "EVENT_ERIKA_REQUESTED_CELADON_POND_HELP": True,
        },
        badges=("ENGINE_RAINBOWBADGE",),
        player_state="PLAYER_SURF",
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


def _articuno_checkpoint_events(
    branch: str,
    *,
    silver_available: bool = False,
    oak_handoff: bool = False,
    caught: bool = False,
    mask: bool = False,
) -> dict[str, bool]:
    return {
        "EVENT_GOT_ARTICUNO_FROM_ELM": branch == "articuno",
        "EVENT_GOT_ZAPDOS_FROM_ELM": branch == "zapdos",
        "EVENT_GOT_MOLTRES_FROM_ELM": branch == "moltres",
        "EVENT_ARTICUNO_AVAILABLE": silver_available,
        "EVENT_OAK_MOVED_THIRD_BIRD": oak_handoff,
        "EVENT_CAUGHT_ARTICUNO_IN_KANTO": caught,
        "EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION": mask,
    }


@pytest.mark.parametrize(
    ("branch", "silver_available", "oak_handoff", "caught", "visible"),
    [
        ("none", True, True, False, False),
        ("articuno", True, True, False, False),
        ("zapdos", False, True, False, False),
        ("zapdos", True, False, False, True),
        ("moltres", True, False, False, False),
        ("moltres", False, True, False, True),
        ("moltres", False, True, True, False),
    ],
    ids=[
        "invalid-no-starter-choice",
        "player-species",
        "silver-pending",
        "silver-released",
        "oak-pending",
        "oak-handoff",
        "already-caught",
    ],
)
def test_articuno_visibility_uses_only_the_locked_branch_source(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    branch: str,
    silver_available: bool,
    oak_handoff: bool,
    caught: bool,
    visible: bool,
) -> None:
    constants = phase_9_constants
    articuno = scenario["seafoam"]["articuno"]
    mask_event = constants["EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION"]
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="SEAFOAM_ISLANDS_CAVE",
        x=articuno["approach"][0],
        y=articuno["approach"][1],
        events=_articuno_checkpoint_events(
            branch,
            silver_available=silver_available,
            oak_handoff=oak_handoff,
            caught=caught,
            mask=visible,
        ),
    ) as session:
        assert event_is_set(session, mask_event) is not visible
        assert (session.read_symbol("wMap1ObjectStructID") != 0xFF) is visible


def test_route_20_seafoam_round_trip_and_forced_slide_are_runtime_safe(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
) -> None:
    constants = phase_9_constants
    max_frames = scenario["max_frames_per_step"]
    events = _articuno_checkpoint_events("moltres", oak_handoff=True)
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "round-trip",
        constants,
        scenario,
        map_name="ROUTE_20",
        x=32,
        y=6,
        events=events,
    ) as session:
        _walk_until_map(
            session,
            "up",
            constants,
            "SEAFOAM_ISLANDS_CAVE",
            max_frames,
        )
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            10,
            17,
        )
        walk_steps(session, "up", "wYCoord", -1, 1, max_frames)
        _walk_until_map(session, "down", constants, "ROUTE_20", max_frames)
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            32,
            6,
        )

    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "slide",
        constants,
        scenario,
        map_name="SEAFOAM_ISLANDS_CAVE",
        x=10,
        y=16,
        events=events,
    ) as session:
        def slide_until(
            direction: str, symbol: str, target: int, description: str
        ) -> None:
            session.pyboy.button_press(direction)
            session.wait_until(
                lambda current: current.read_symbol(symbol) == target,
                max_frames,
                description,
            )
            session.pyboy.button_release(direction)
            session.tick(1)
            wait_for_idle(session, max_frames)

        walk_steps(session, "up", "wYCoord", -1, 3, max_frames)
        walk_steps(session, "left", "wXCoord", -1, 4, max_frames)
        walk_steps(session, "up", "wYCoord", -1, 1, max_frames)
        slide_until("up", "wYCoord", 9, "northbound western Seafoam ice slide")
        walk_steps(session, "up", "wYCoord", -1, 3, max_frames)
        walk_steps(session, "right", "wXCoord", 1, 1, max_frames)
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            7,
            6,
        )

        slide_until("right", "wXCoord", 11, "eastbound upper Seafoam ice slide")
        slide_until("down", "wYCoord", 9, "southbound divider Seafoam ice slide")
        slide_until("left", "wXCoord", 9, "westbound central Seafoam ice slide")
        slide_until("up", "wYCoord", 5, "northbound central Seafoam ice slide")
        walk_steps(session, "left", "wXCoord", -1, 1, max_frames)
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == tuple(
            scenario["seafoam"]["articuno"]["approach"]
        )
        assert session.read_symbol("wPlayerTileCollision") == constants["COLL_FLOOR"]
        assert session.read_symbol("wBattleMode") == 0

        walk_steps(session, "right", "wXCoord", 1, 1, max_frames)
        slide_until("down", "wYCoord", 9, "southbound central Seafoam ice slide")
        slide_until("right", "wXCoord", 11, "eastbound central Seafoam ice slide")
        slide_until("up", "wYCoord", 6, "northbound divider Seafoam ice slide")
        slide_until("left", "wXCoord", 7, "westbound upper Seafoam ice slide")
        walk_steps(session, "left", "wXCoord", -1, 1, max_frames)
        walk_steps(session, "down", "wYCoord", 1, 3, max_frames)
        slide_until("down", "wYCoord", 12, "southbound western Seafoam ice slide")
        walk_steps(session, "down", "wYCoord", 1, 1, max_frames)
        walk_steps(session, "right", "wXCoord", 1, 4, max_frames)
        walk_steps(session, "down", "wYCoord", 1, 3, max_frames)
        _walk_until_map(session, "down", constants, "ROUTE_20", max_frames)
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            32,
            6,
        )


def _start_articuno_battle(session, constants: dict[str, int], max_frames: int, cursor: int) -> None:
    session.enable_script_tracing()
    session.register_hook(
        "BattleMenu",
        lambda current: current.write_symbol("wBattleMenuCursorPosition", cursor),
    )
    session.register_hook("CheckCaughtPokemon")
    battle_count = session.hook_history.count("BattleMenu") + 1
    session.write_symbol("wPlayerDirection", constants["OW_UP"])
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("BattleMenu") >= battle_count,
        max_frames,
        "Articuno battle menu",
    )
    assert session.read_symbol("wEnemyMonSpecies") == constants["ARTICUNO"]
    assert session.read_symbol("wEnemyMonLevel") == 60
    assert session.read_symbol("wBattleType") == constants["BATTLETYPE_KANTO_BIRD"]


def test_kanto_bird_battle_type_reaches_the_nonflee_guard(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
) -> None:
    constants = phase_9_constants
    articuno = scenario["seafoam"]["articuno"]
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="SEAFOAM_ISLANDS_CAVE",
        x=articuno["approach"][0],
        y=articuno["approach"][1],
        events=_articuno_checkpoint_events("moltres", oak_handoff=True),
    ) as session:
        prepare_battle_party(session, constants, constants["MAREEP"], should_win=False)
        _start_articuno_battle(session, constants, max_frames, 1)
        session.write_symbol_bytes("wBattleMonHP", (999).to_bytes(2, "big"))
        session.write_symbol_bytes("wBattleMonMaxHP", (999).to_bytes(2, "big"))
        session.write_symbol_bytes("wBattleMonDefense", (999).to_bytes(2, "big"))
        session.write_symbol_bytes("wBattleMonSpeed", (999).to_bytes(2, "big"))
        for label in ("TryEnemyFlee", "TryEnemyFlee.Stay", "TryEnemyFlee.Flee"):
            session.register_hook(label)
        advance_with_a_until(
            session,
            lambda current: "TryEnemyFlee.Stay" in current.hook_history,
            max_frames,
            "Kanto bird nonflee guard",
        )
        assert "TryEnemyFlee" in session.hook_history
        assert "TryEnemyFlee.Flee" not in session.hook_history


@pytest.mark.parametrize("outcome", ["knockout", "escape"])
def test_articuno_non_capture_results_restore_a_healthy_retry(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    outcome: str,
) -> None:
    constants = phase_9_constants
    articuno = scenario["seafoam"]["articuno"]
    max_frames = scenario["max_frames_per_step"]
    capture_event = constants["EVENT_CAUGHT_ARTICUNO_IN_KANTO"]
    mask_event = constants["EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION"]
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="SEAFOAM_ISLANDS_CAVE",
        x=articuno["approach"][0],
        y=articuno["approach"][1],
        events=_articuno_checkpoint_events("moltres", oak_handoff=True),
    ) as session:
        prepare_battle_party(session, constants, constants["MAREEP"], should_win=True)
        _start_articuno_battle(
            session, constants, max_frames, 1 if outcome == "knockout" else 4
        )
        if outcome == "knockout":
            session.register_hook(
                "HasEnemyFainted",
                lambda current: current.write_symbol_bytes("wEnemyMonHP", b"\0\0"),
            )
        else:
            session.write_symbol_bytes("wBattleMonSpeed", (999).to_bytes(2, "big"))
            session.write_symbol_bytes("wEnemyMonSpeed", (1).to_bytes(2, "big"))
        checked = session.hook_history.count("CheckCaughtPokemon") + 1
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: current.hook_history.count("CheckCaughtPokemon") >= checked,
            max_frames,
            f"Articuno {outcome} capture query",
        )
        _finish_overworld_script(session, max_frames)
        assert not event_is_set(session, capture_event)
        assert not event_is_set(session, mask_event)
        assert session.read_symbol("wMap1ObjectStructID") != 0xFF

        place_player(session, *articuno["approach"])
        _start_articuno_battle(session, constants, max_frames, 1)
        assert session.read_symbol_bytes("wEnemyMonHP", 2) == session.read_symbol_bytes(
            "wEnemyMonMaxHP", 2
        )
        assert session.read_symbol("wEnemyMonStatus") == 0


def test_articuno_capture_and_absence_survive_native_continue(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
) -> None:
    constants = phase_9_constants
    articuno = scenario["seafoam"]["articuno"]
    max_frames = scenario["max_frames_per_step"]
    capture_event = constants["EVENT_CAUGHT_ARTICUNO_IN_KANTO"]
    mask_event = constants["EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION"]
    persisted = tmp_path / "articuno-captured.sav"
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "capture",
        constants,
        scenario,
        map_name="SEAFOAM_ISLANDS_CAVE",
        x=articuno["approach"][0],
        y=articuno["approach"][1],
        events=_articuno_checkpoint_events("moltres", oak_handoff=True),
    ) as session:
        prepare_battle_party(session, constants, constants["MAREEP"], should_win=True)
        session.write_symbol("wNumBalls", 1)
        session.write_symbol_bytes(
            "wBalls", bytes([constants["MASTER_BALL"], 1, 0xFF])
        )
        session.write_symbol("wLastPocket", constants["BALL_POCKET"])
        _start_articuno_battle(session, constants, max_frames, 3)
        session.register_hook("PokeBallEffect")
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: "PokeBallEffect" in current.hook_history,
            max_frames,
            "Articuno Master Ball use",
        )
        advance_with_a_until(
            session,
            lambda current: event_is_set(current, capture_event),
            max_frames,
            "Articuno capture fact",
        )
        result = session.read_symbol("wBattleResult")
        _finish_overworld_script(session, max_frames)
        assert result & (1 << constants["BATTLERESULT_CAUGHT_POKEMON"])
        assert event_is_set(session, mask_event)
        assert session.read_symbol("wMap1ObjectStructID") == 0xFF
        assert read_progress(session).owns(constants["ARTICUNO"])
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, persisted)

    with loaded_phase_9_saved_game(
        repo_root,
        tmp_path / "continue",
        constants,
        scenario,
        persisted,
    ) as session:
        assert event_is_set(session, capture_event)
        assert event_is_set(session, mask_event)
        assert session.read_symbol("wMap1ObjectStructID") == 0xFF
        assert read_progress(session).owns(constants["ARTICUNO"])
        session.register_hook("BattleMenu")
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        for _ in range(20):
            session.tap("a", 2, 10)
        assert "BattleMenu" not in session.hook_history


def _remaining_bird_checkpoint_events(
    bird: str,
    branch: str,
    *,
    silver_available: bool = False,
    oak_handoff: bool = False,
    location_gate: bool = False,
    caught: bool = False,
    mask: bool = False,
) -> dict[str, bool]:
    upper = bird.upper()
    events = {
        "EVENT_GOT_ARTICUNO_FROM_ELM": branch == "articuno",
        "EVENT_GOT_ZAPDOS_FROM_ELM": branch == "zapdos",
        "EVENT_GOT_MOLTRES_FROM_ELM": branch == "moltres",
        "EVENT_ARTICUNO_AVAILABLE": False,
        "EVENT_ZAPDOS_AVAILABLE": False,
        "EVENT_MOLTRES_AVAILABLE": False,
        "EVENT_OAK_MOVED_THIRD_BIRD": oak_handoff,
        "EVENT_RESTORED_POWER_TO_KANTO": bird == "zapdos" and location_gate,
        "EVENT_BEAT_ELITE_FOUR": bird == "moltres" and location_gate,
        "EVENT_CAUGHT_ZAPDOS_IN_KANTO": bird == "zapdos" and caught,
        "EVENT_CAUGHT_MOLTRES_IN_KANTO": bird == "moltres" and caught,
        "EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION": bird == "zapdos" and mask,
        "EVENT_MOLTRES_NOT_AT_KANTO_LOCATION": bird == "moltres" and mask,
    }
    events[f"EVENT_{upper}_AVAILABLE"] = silver_available
    return events


@pytest.mark.parametrize(
    (
        "bird",
        "branch",
        "silver_available",
        "oak_handoff",
        "location_gate",
        "caught",
        "visible",
    ),
    [
        ("zapdos", "none", True, True, True, False, False),
        ("zapdos", "zapdos", True, True, True, False, False),
        ("zapdos", "moltres", False, True, True, False, False),
        ("zapdos", "moltres", True, False, True, False, True),
        ("zapdos", "articuno", True, False, True, False, False),
        ("zapdos", "articuno", False, True, True, False, True),
        ("zapdos", "articuno", False, True, False, False, False),
        ("zapdos", "articuno", False, True, True, True, False),
        ("moltres", "none", True, True, True, False, False),
        ("moltres", "moltres", True, True, True, False, False),
        ("moltres", "articuno", False, True, True, False, False),
        ("moltres", "articuno", True, False, True, False, True),
        ("moltres", "zapdos", True, False, True, False, False),
        ("moltres", "zapdos", False, True, True, False, True),
        ("moltres", "zapdos", False, True, False, False, False),
        ("moltres", "zapdos", False, True, True, True, False),
    ],
    ids=[
        "zapdos-invalid-no-starter-choice",
        "zapdos-player-species",
        "zapdos-silver-pending",
        "zapdos-silver-released",
        "zapdos-oak-pending",
        "zapdos-oak-handoff",
        "zapdos-power-pending",
        "zapdos-already-caught",
        "moltres-invalid-no-starter-choice",
        "moltres-player-species",
        "moltres-silver-pending",
        "moltres-silver-released",
        "moltres-oak-pending",
        "moltres-oak-handoff",
        "moltres-league-pending",
        "moltres-already-caught",
    ],
)
def test_remaining_bird_visibility_uses_branch_source_and_location_gate(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    bird: str,
    branch: str,
    silver_available: bool,
    oak_handoff: bool,
    location_gate: bool,
    caught: bool,
    visible: bool,
) -> None:
    constants = phase_9_constants
    contract = (
        scenario["power_plant_annex"]["zapdos"]
        if bird == "zapdos"
        else scenario["victory_road_bird"]["moltres"]
    )
    map_name = (
        scenario["power_plant_annex"]["map"]
        if bird == "zapdos"
        else scenario["victory_road_bird"]["map"]
    )
    object_symbol = "wMap1ObjectStructID" if bird == "zapdos" else "wMap7ObjectStructID"
    mask_event = constants[contract["mask_event"]]
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name=map_name,
        x=contract["approach"][0],
        y=contract["approach"][1],
        events=_remaining_bird_checkpoint_events(
            bird,
            branch,
            silver_available=silver_available,
            oak_handoff=oak_handoff,
            location_gate=location_gate,
            caught=caught,
            mask=visible,
        ),
    ) as session:
        assert event_is_set(session, mask_event) is not visible
        assert (session.read_symbol(object_symbol) != 0xFF) is visible


@pytest.mark.parametrize("caught", [False, True], ids=["over-limit", "stable"])
@pytest.mark.parametrize("console_x", [2, 3], ids=["left-console", "right-console"])
def test_both_generator_consoles_reflect_zapdos_capture(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    caught: bool,
    console_x: int,
) -> None:
    constants = phase_9_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="POWER_PLANT_GENERATOR_ANNEX",
        x=console_x,
        y=5,
        events={
            "EVENT_CAUGHT_ZAPDOS_IN_KANTO": caught,
            "EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION": caught,
        },
    ) as session:
        place_player(session, console_x, 5)
        session.enable_script_tracing()
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        session.tap("a", 2, 10)
        session.wait_for_script("PowerPlantGeneratorAnnexConsole", max_frames)
        _finish_overworld_script(session, max_frames)
        assert (
            "PowerPlantGeneratorAnnexConsole.Stable" in session.script_history
        ) is caught


def _interact_with_power_plant_shutter(
    session, constants: dict[str, int], max_frames: int, *, y: int = 11
) -> None:
    place_player(session, 19, y)
    session.enable_script_tracing()
    session.write_symbol("wPlayerDirection", constants["OW_RIGHT"])
    session.tap("a", 2, 10)
    session.wait_for_script("PowerPlantAnnexShutter", max_frames)
    _finish_overworld_script(session, max_frames)


@pytest.mark.parametrize(
    ("powered", "authorized"),
    [(False, False), (True, False)],
    ids=["unpowered", "manager-authorization-required"],
)
@pytest.mark.parametrize("door_y", [10, 11], ids=["upper-carpet", "lower-carpet"])
def test_power_plant_shutter_stays_closed_without_each_access_fact(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    powered: bool,
    authorized: bool,
    door_y: int,
) -> None:
    constants = phase_9_constants
    shutter = scenario["power_plant_annex"]["shutter"]
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="POWER_PLANT",
        x=19,
        y=door_y,
        events={
            shutter["power_event"]: powered,
            shutter["authorization_event"]: authorized,
            shutter["open_event"]: False,
        },
    ) as session:
        assert _loaded_block(session, *shutter["block_origin"]) == shutter[
            "closed_block"
        ]
        _interact_with_power_plant_shutter(
            session, constants, scenario["max_frames_per_step"], y=door_y
        )
        assert not event_is_set(session, constants[shutter["open_event"]])
        assert _loaded_block(session, *shutter["block_origin"]) == shutter[
            "closed_block"
        ]


def test_manager_authorizes_the_annex_only_after_the_repair_reward_flow(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
) -> None:
    constants = phase_9_constants
    authorization = constants["EVENT_POWER_PLANT_ANNEX_AUTHORIZED"]
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name="POWER_PLANT",
        x=14,
        y=11,
        events={
            "EVENT_RETURNED_MACHINE_PART": True,
            "EVENT_RESTORED_POWER_TO_KANTO": True,
            "EVENT_GOT_TM07_ZAP_CANNON": True,
            "EVENT_POWER_PLANT_ANNEX_AUTHORIZED": False,
        },
    ) as session:
        session.enable_script_tracing()
        place_player(session, 14, 11)
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        session.tap("a", 2, 10)
        session.wait_for_script("PowerPlantManager", scenario["max_frames_per_step"])
        _finish_overworld_script(session, scenario["max_frames_per_step"])
        assert event_is_set(session, authorization)


@pytest.mark.parametrize(
    ("door_y", "annex_y"),
    [(10, 5), (11, 6)],
    ids=["upper-carpet", "lower-carpet"],
)
def test_power_plant_annex_round_trip_and_open_block_survive_native_continue(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    door_y: int,
    annex_y: int,
) -> None:
    constants = phase_9_constants
    annex = scenario["power_plant_annex"]
    shutter = annex["shutter"]
    persisted = tmp_path / "power-plant-annex-open.sav"
    events = {
        **_remaining_bird_checkpoint_events(
            "zapdos", "zapdos", location_gate=True
        ),
        shutter["authorization_event"]: True,
        shutter["open_event"]: False,
    }
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "open",
        constants,
        scenario,
        map_name="POWER_PLANT",
        x=19,
        y=door_y,
        events=events,
    ) as session:
        _interact_with_power_plant_shutter(
            session, constants, scenario["max_frames_per_step"], y=door_y
        )
        assert event_is_set(session, constants[shutter["open_event"]])

        _walk_until_map(
            session,
            "right",
            constants,
            annex["map"],
            scenario["max_frames_per_step"],
        )
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            0,
            annex_y,
        )
        walk_steps(
            session,
            "right",
            "wXCoord",
            1,
            1,
            scenario["max_frames_per_step"],
        )
        _walk_until_map(
            session,
            "left",
            constants,
            "POWER_PLANT",
            scenario["max_frames_per_step"],
        )
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            19,
            door_y,
        )
        assert _loaded_block(session, *shutter["block_origin"]) == shutter[
            "open_block"
        ]
        walk_steps(
            session,
            "left",
            "wXCoord",
            -1,
            1,
            scenario["max_frames_per_step"],
        )
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            18,
            door_y,
        )
        save_game_from_overworld(session, scenario["max_frames_per_step"])
        dump_battery_ram(session, persisted)

    with loaded_phase_9_saved_game(
        repo_root,
        tmp_path / "continue",
        constants,
        scenario,
        persisted,
    ) as session:
        assert event_is_set(session, constants[shutter["open_event"]])
        assert _loaded_block(session, *shutter["block_origin"]) == shutter["open_block"]


def _remaining_bird_runtime_contract(scenario: dict, bird: str) -> tuple[dict, str, str, str]:
    if bird == "zapdos":
        return (
            scenario["power_plant_annex"]["zapdos"],
            scenario["power_plant_annex"]["map"],
            "articuno",
            "wMap1ObjectStructID",
        )
    return (
        scenario["victory_road_bird"]["moltres"],
        scenario["victory_road_bird"]["map"],
        "zapdos",
        "wMap7ObjectStructID",
    )


def _start_remaining_bird_battle(
    session,
    constants: dict[str, int],
    contract: dict,
    max_frames: int,
    cursor: int,
) -> None:
    session.enable_script_tracing()
    session.register_hook(
        "BattleMenu",
        lambda current: current.write_symbol("wBattleMenuCursorPosition", cursor),
    )
    session.register_hook("CheckCaughtPokemon")
    battle_count = session.hook_history.count("BattleMenu") + 1
    session.write_symbol("wPlayerDirection", constants["OW_UP"])
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("BattleMenu") >= battle_count,
        max_frames,
        f'{contract["species"]} battle menu',
    )
    assert session.read_symbol("wEnemyMonSpecies") == constants[contract["species"]]
    assert session.read_symbol("wEnemyMonLevel") == contract["level"]
    assert session.read_symbol("wBattleType") == constants["BATTLETYPE_KANTO_BIRD"]


@pytest.mark.parametrize(
    ("bird", "outcome"),
    [("zapdos", "escape"), ("moltres", "knockout")],
)
def test_remaining_bird_non_capture_results_restore_a_healthy_retry(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    bird: str,
    outcome: str,
) -> None:
    constants = phase_9_constants
    max_frames = scenario["max_frames_per_step"]
    contract, map_name, branch, object_symbol = _remaining_bird_runtime_contract(
        scenario, bird
    )
    capture_event = constants[contract["capture_event"]]
    mask_event = constants[contract["mask_event"]]
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        map_name=map_name,
        x=contract["approach"][0],
        y=contract["approach"][1],
        events=_remaining_bird_checkpoint_events(
            bird,
            branch,
            oak_handoff=True,
            location_gate=True,
        ),
    ) as session:
        prepare_battle_party(session, constants, constants["MAREEP"], should_win=True)
        _start_remaining_bird_battle(
            session, constants, contract, max_frames, 4 if outcome == "escape" else 1
        )
        if outcome == "knockout":
            session.register_hook(
                "HasEnemyFainted",
                lambda current: current.write_symbol_bytes("wEnemyMonHP", b"\0\0"),
            )
        else:
            session.write_symbol_bytes("wBattleMonSpeed", (999).to_bytes(2, "big"))
            session.write_symbol_bytes("wEnemyMonSpeed", (1).to_bytes(2, "big"))
        checked = session.hook_history.count("CheckCaughtPokemon") + 1
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: current.hook_history.count("CheckCaughtPokemon") >= checked,
            max_frames,
            f'{contract["species"]} {outcome} capture query',
        )
        _finish_overworld_script(session, max_frames)
        assert not event_is_set(session, capture_event)
        assert not event_is_set(session, mask_event)
        assert session.read_symbol(object_symbol) != 0xFF

        place_player(session, *contract["approach"])
        _start_remaining_bird_battle(session, constants, contract, max_frames, 1)
        assert session.read_symbol_bytes("wEnemyMonHP", 2) == session.read_symbol_bytes(
            "wEnemyMonMaxHP", 2
        )
        assert session.read_symbol("wEnemyMonStatus") == 0


@pytest.mark.parametrize("bird", ["zapdos", "moltres"])
def test_remaining_bird_capture_and_absence_survive_native_continue(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    bird: str,
) -> None:
    constants = phase_9_constants
    max_frames = scenario["max_frames_per_step"]
    contract, map_name, branch, object_symbol = _remaining_bird_runtime_contract(
        scenario, bird
    )
    capture_event = constants[contract["capture_event"]]
    mask_event = constants[contract["mask_event"]]
    persisted = tmp_path / f"{bird}-captured.sav"
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / "capture",
        constants,
        scenario,
        map_name=map_name,
        x=contract["approach"][0],
        y=contract["approach"][1],
        events=_remaining_bird_checkpoint_events(
            bird,
            branch,
            oak_handoff=True,
            location_gate=True,
        ),
    ) as session:
        prepare_battle_party(session, constants, constants["MAREEP"], should_win=True)
        session.write_symbol("wNumBalls", 1)
        session.write_symbol_bytes(
            "wBalls", bytes([constants["MASTER_BALL"], 1, 0xFF])
        )
        session.write_symbol("wLastPocket", constants["BALL_POCKET"])
        _start_remaining_bird_battle(session, constants, contract, max_frames, 3)
        session.register_hook("PokeBallEffect")
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: "PokeBallEffect" in current.hook_history,
            max_frames,
            f'{contract["species"]} Master Ball use',
        )
        advance_with_a_until(
            session,
            lambda current: event_is_set(current, capture_event),
            max_frames,
            f'{contract["species"]} capture fact',
        )
        result = session.read_symbol("wBattleResult")
        _finish_overworld_script(session, max_frames)
        assert result & (1 << constants["BATTLERESULT_CAUGHT_POKEMON"])
        assert event_is_set(session, mask_event)
        assert session.read_symbol(object_symbol) == 0xFF
        assert read_progress(session).owns(constants[contract["species"]])
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, persisted)

    with loaded_phase_9_saved_game(
        repo_root,
        tmp_path / "continue",
        constants,
        scenario,
        persisted,
    ) as session:
        assert event_is_set(session, capture_event)
        assert event_is_set(session, mask_event)
        assert session.read_symbol(object_symbol) == 0xFF
        assert read_progress(session).owns(constants[contract["species"]])
        session.register_hook("BattleMenu")
        place_player(session, *contract["approach"])
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        for _ in range(20):
            session.tap("a", 2, 10)
        assert "BattleMenu" not in session.hook_history


def test_single_save_collects_all_gifts_and_both_nonstarter_birds(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
) -> None:
    constants = phase_9_constants
    max_frames = scenario["max_frames_per_step"]
    gifts = scenario["gifts"]
    initial = build_phase_9_gift_checkpoint(
        repo_root,
        tmp_path / "combined-initial.sav",
        constants,
        scenario,
        gifts[0],
        service_complete=True,
    )
    combined_events = {
        **{gift["service_event"]: True for gift in gifts},
        **{gift["completion_event"]: False for gift in gifts},
        "EVENT_GOT_ARTICUNO_FROM_ELM": False,
        "EVENT_GOT_ZAPDOS_FROM_ELM": True,
        "EVENT_GOT_MOLTRES_FROM_ELM": False,
        "EVENT_OAK_MOVED_THIRD_BIRD": True,
        "EVENT_ARTICUNO_AVAILABLE": True,
        "EVENT_ZAPDOS_AVAILABLE": False,
        "EVENT_MOLTRES_AVAILABLE": False,
        "EVENT_BEAT_ELITE_FOUR": True,
        "EVENT_CAUGHT_ARTICUNO_IN_KANTO": False,
        "EVENT_CAUGHT_ZAPDOS_IN_KANTO": False,
        "EVENT_CAUGHT_MOLTRES_IN_KANTO": False,
    }
    relocate_phase_9_saved_game(
        repo_root,
        initial,
        initial,
        constants,
        map_name=gifts[0]["map"],
        x=gifts[0]["start"]["x"],
        y=gifts[0]["start"]["y"],
        events=combined_events,
        badges=tuple(gift["badge"] for gift in gifts),
    )

    current_save = initial
    collected_species: list[int] = []
    for index, gift in enumerate(gifts):
        if index:
            relocated = tmp_path / f"combined-gift-{index}-ready.sav"
            relocate_phase_9_saved_game(
                repo_root,
                current_save,
                relocated,
                constants,
                map_name=gift["map"],
                x=gift["start"]["x"],
                y=gift["start"]["y"],
            )
            current_save = relocated
        persisted = tmp_path / f"combined-gift-{index}-complete.sav"
        with loaded_phase_9_saved_game(
            repo_root,
            tmp_path / f"combined-gift-{index}",
            constants,
            scenario,
            current_save,
        ) as session:
            assert (
                interact_with_gift(
                    session, _gift_scenario(scenario, gift), accept=True
                )
                == 0
            )
            collected_species.append(constants[gift["species"]])
            progress = read_progress(session)
            assert all(progress.owns(species) for species in collected_species)
            assert all(
                event_is_set(session, constants[completed["completion_event"]])
                for completed in gifts[: index + 1]
            )
            save_game_from_overworld(session, max_frames)
            dump_battery_ram(session, persisted)
        current_save = persisted

    articuno = scenario["seafoam"]["articuno"]
    articuno_ready = relocate_phase_9_saved_game(
        repo_root,
        current_save,
        tmp_path / "combined-articuno-ready.sav",
        constants,
        map_name=scenario["seafoam"]["map"],
        x=articuno["approach"][0],
        y=articuno["approach"][1],
    )
    articuno_caught = tmp_path / "combined-articuno-caught.sav"
    with loaded_phase_9_saved_game(
        repo_root,
        tmp_path / "combined-articuno",
        constants,
        scenario,
        articuno_ready,
    ) as session:
        session.write_symbol("wNumBalls", 1)
        session.write_symbol_bytes(
            "wBalls", bytes([constants["MASTER_BALL"], 1, 0xFF])
        )
        session.write_symbol("wLastPocket", constants["BALL_POCKET"])
        _start_articuno_battle(session, constants, max_frames, 3)
        session.register_hook("PokeBallEffect")
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: event_is_set(
                current, constants[articuno["capture_event"]]
            ),
            max_frames,
            "combined-save Articuno capture",
        )
        _finish_overworld_script(session, max_frames)
        progress = read_progress(session)
        assert progress.owns(constants["ARTICUNO"])
        assert all(progress.owns(species) for species in collected_species)
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, articuno_caught)

    moltres = scenario["victory_road_bird"]["moltres"]
    moltres_ready = relocate_phase_9_saved_game(
        repo_root,
        articuno_caught,
        tmp_path / "combined-moltres-ready.sav",
        constants,
        map_name=scenario["victory_road_bird"]["map"],
        x=moltres["approach"][0],
        y=moltres["approach"][1],
    )
    completed = tmp_path / "combined-complete.sav"
    with loaded_phase_9_saved_game(
        repo_root,
        tmp_path / "combined-moltres",
        constants,
        scenario,
        moltres_ready,
    ) as session:
        session.write_symbol("wNumBalls", 1)
        session.write_symbol_bytes(
            "wBalls", bytes([constants["MASTER_BALL"], 1, 0xFF])
        )
        session.write_symbol("wLastPocket", constants["BALL_POCKET"])
        _start_remaining_bird_battle(
            session, constants, moltres, max_frames, 3
        )
        session.register_hook("PokeBallEffect")
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: event_is_set(
                current, constants[moltres["capture_event"]]
            ),
            max_frames,
            "combined-save Moltres capture",
        )
        _finish_overworld_script(session, max_frames)
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, completed)

    with loaded_phase_9_saved_game(
        repo_root,
        tmp_path / "combined-continue",
        constants,
        scenario,
        completed,
    ) as session:
        expected_species = [
            *collected_species,
            constants["ARTICUNO"],
            constants["MOLTRES"],
        ]
        progress = read_progress(session)
        assert all(progress.owns(species) for species in expected_species)
        assert all(
            event_is_set(session, constants[gift["completion_event"]])
            for gift in gifts
        )
        assert event_is_set(session, constants[articuno["capture_event"]])
        assert event_is_set(session, constants[moltres["capture_event"]])
        assert not event_is_set(
            session, constants["EVENT_CAUGHT_ZAPDOS_IN_KANTO"]
        )


@pytest.mark.parametrize(
    ("case", "events", "expected_label"),
    [
        (
            "stock-before-handoff",
            {
                "EVENT_GOT_ARTICUNO_FROM_ELM": True,
                "EVENT_OAK_MOVED_THIRD_BIRD": False,
            },
            None,
        ),
        (
            "zapdos-repair-hint",
            {
                "EVENT_GOT_ARTICUNO_FROM_ELM": True,
                "EVENT_OAK_MOVED_THIRD_BIRD": True,
                "EVENT_RESTORED_POWER_TO_KANTO": False,
            },
            "Phase9OaksAssistantZapdosHint",
        ),
        (
            "zapdos-closed-shutter-hint",
            {
                "EVENT_GOT_MOLTRES_FROM_ELM": True,
                "EVENT_OAK_MOVED_THIRD_BIRD": True,
                "EVENT_CAUGHT_ARTICUNO_IN_KANTO": True,
                "EVENT_ZAPDOS_AVAILABLE": True,
                "EVENT_RESTORED_POWER_TO_KANTO": True,
                "EVENT_POWER_PLANT_ANNEX_AUTHORIZED": True,
                "EVENT_OPENED_POWER_PLANT_ANNEX": False,
            },
            "Phase9OaksAssistantZapdosHint",
        ),
        (
            "both-nonstarter-birds-caught",
            {
                "EVENT_GOT_ZAPDOS_FROM_ELM": True,
                "EVENT_OAK_MOVED_THIRD_BIRD": True,
                "EVENT_CAUGHT_ARTICUNO_IN_KANTO": True,
                "EVENT_CAUGHT_MOLTRES_IN_KANTO": True,
            },
            "Phase9OaksAssistant2Hints.BothCaught",
        ),
    ],
)
def test_oaks_second_assistant_tracks_handoff_and_capture_state(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_9_constants: dict[str, int],
    case: str,
    events: dict[str, bool],
    expected_label: str | None,
) -> None:
    constants = phase_9_constants
    defaults = {
        "EVENT_GOT_ARTICUNO_FROM_ELM": False,
        "EVENT_GOT_ZAPDOS_FROM_ELM": False,
        "EVENT_GOT_MOLTRES_FROM_ELM": False,
        "EVENT_ARTICUNO_AVAILABLE": False,
        "EVENT_ZAPDOS_AVAILABLE": False,
        "EVENT_MOLTRES_AVAILABLE": False,
        "EVENT_OAK_MOVED_THIRD_BIRD": False,
        "EVENT_RESTORED_POWER_TO_KANTO": False,
        "EVENT_POWER_PLANT_ANNEX_AUTHORIZED": False,
        "EVENT_OPENED_POWER_PLANT_ANNEX": False,
        "EVENT_BEAT_ELITE_FOUR": False,
        "EVENT_CAUGHT_ARTICUNO_IN_KANTO": False,
        "EVENT_CAUGHT_ZAPDOS_IN_KANTO": False,
        "EVENT_CAUGHT_MOLTRES_IN_KANTO": False,
    }
    with loaded_phase_9_map_checkpoint(
        repo_root,
        tmp_path / case,
        constants,
        scenario,
        map_name="OAKS_LAB",
        x=8,
        y=10,
        events={**defaults, **events},
    ) as session:
        session.enable_script_tracing()
        object_struct = session.read_symbol("wMap3ObjectStructID")
        assistant_x = session.read_symbol(f"wObject{object_struct}MapX") - 4
        assistant_y = session.read_symbol(f"wObject{object_struct}MapY") - 4
        # Prime the camera-relative object coordinates after the save-fixture
        # checkpoint places the player beside this walking NPC.
        place_player(session, assistant_x, assistant_y + 1)
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        session.tick(10)
        session.tap("a", 2, 10)
        place_player(session, assistant_x, assistant_y - 1)
        session.write_symbol("wPlayerDirection", constants["OW_DOWN"])
        session.tick(10)
        session.tap("a", 2, 10)
        session.wait_for_script("OaksAssistant2Script", scenario["max_frames_per_step"])
        if expected_label is None:
            _finish_overworld_script(session, scenario["max_frames_per_step"])
            assert "Phase9OaksAssistant2Hints" not in session.script_history
        else:
            session.wait_for_script(
                expected_label, scenario["max_frames_per_step"]
            )
            _finish_overworld_script(session, scenario["max_frames_per_step"])
            assert "Phase9OaksAssistant2Hints" in session.script_history
