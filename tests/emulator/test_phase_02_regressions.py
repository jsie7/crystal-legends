from __future__ import annotations

from pathlib import Path
import json

import pytest

from tests.support.bedroom_scenario import event_is_set, loaded_session, wait_for_idle
from tests.support.constant_resolver import resolve_constants
from tests.support.game_state import read_inventory, read_progress
from tests.support.legendary_scenario import advance_with_a_until, prepare_battle_party
from tests.support.phase_02_scenario import loaded_phase_2_checkpoint


pytestmark = pytest.mark.emulator


@pytest.fixture(scope="module")
def evolution_contract(repo_root: Path) -> list[dict]:
    return json.loads(
        (repo_root / "tests/contracts/phase_02_evolutions.json").read_text()
    )


@pytest.fixture(scope="module")
def phase_2_constants(
    repo_root: Path, tmp_path_factory, evolution_contract: list[dict]
) -> dict[str, int]:
    names = {
        "EVENT_BEAT_ELITE_FOUR",
        "EVENT_GOT_GS_BALL_FROM_GOLDENROD_POKEMON_CENTER",
        "EVENT_CAN_GIVE_GS_BALL_TO_KURT",
        "EVENT_GAVE_GS_BALL_TO_KURT",
        "EVENT_FOREST_IS_RESTLESS",
        "EVENT_AZALEA_TOWN_KURT",
        "EVENT_ROUTE_34_ILEX_FOREST_GATE_LASS",
        "EVENT_ILEX_FOREST_LASS",
        "EVENT_KURTS_HOUSE_KURT_1",
        "EVENT_KURTS_HOUSE_KURT_2",
        "EVENT_CLEARED_SLOWPOKE_WELL",
        "EVENT_KURT_GAVE_YOU_LURE_BALL",
        "CELEBIEVENT_FOREST_IS_RESTLESS_F",
        "GROUP_GOLDENROD_POKECENTER_1F",
        "MAP_GOLDENROD_POKECENTER_1F",
        "GROUP_KURTS_HOUSE",
        "MAP_KURTS_HOUSE",
        "GROUP_ILEX_FOREST",
        "MAP_ILEX_FOREST",
        "SPAWN_N_A",
        "MAPSETUP_WARP",
        "GS_BALL",
        "MASTER_BALL",
        "ARTICUNO",
        "CELEBI",
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
        "BATTLERESULT_CAUGHT_CELEBI",
        "BATTLERESULT_BOX_FULL",
        "BALL_POCKET",
        "ITEM_POCKET",
        "RARE_CANDY",
        "STATUSFLAGS_POKEDEX_F",
    }
    for row in evolution_contract:
        names.update(
            (
                row["source"].upper(),
                row["target"],
            )
        )
        if not row["condition"].isdigit():
            names.add(row["condition"])
    return resolve_constants(
        repo_root, tmp_path_factory.mktemp("phase_2_runtime_constants"), sorted(names)
    )


def _finish_script(session, max_frames: int, description: str) -> None:
    advance_with_a_until(
        session,
        lambda current: current.read_symbol("wScriptMode") == 0,
        max_frames,
        description,
    )


def _has_key_item(session, item: int) -> bool:
    return item in read_inventory(session).key_items


def _prepare_evolution_candidate(
    session, constants: dict[str, int], species: int, item: int, level: int
) -> None:
    prepare_battle_party(session, constants, species, True)
    session.write_symbol("wPartyMon1Level", level)
    session.write_symbol("wNumItems", 1)
    session.write_symbol_bytes("wItems", bytes([item, 2, 0xFF]))
    session.write_symbol("wLastPocket", constants["ITEM_POCKET"])
    session.write_symbol(
        "wStatusFlags",
        session.read_symbol("wStatusFlags")
        | (1 << constants["STATUSFLAGS_POKEDEX_F"]),
    )


def _use_first_item_on_first_mon(session, max_frames: int, effect: str) -> None:
    session.register_hook("StartMenu")
    session.register_hook("StartMenu.loop")
    session.register_hook("ScrollingMenu")
    session.register_hook("VerticalMenu")
    session.register_hook(effect)
    session.register_hook("LoadPartyMenuGFX")
    scrolling_menus = session.hook_history.count("ScrollingMenu") + 1
    vertical_menus = session.hook_history.count("VerticalMenu") + 1
    session.write_symbol("wBattleMenuCursorPosition", 3)
    session.tap("start", 10, 10)
    session.wait_for_hook("StartMenu", max_frames)
    session.wait_for_hook("StartMenu.loop", max_frames)
    session.tap("a", 10, 10)
    session.wait_for_hook_count("ScrollingMenu", scrolling_menus, max_frames)
    session.tap("a", 10, 10)
    session.wait_for_hook_count("VerticalMenu", vertical_menus, max_frames)
    session.tap("a", 10, 10)
    session.wait_for_hook(effect, max_frames)
    session.wait_for_hook("LoadPartyMenuGFX", max_frames)
    session.tap("a", 10, 10)


@pytest.mark.parametrize("row_index", range(4), ids=["kadabra", "machoke", "graveler", "haunter"])
def test_level_36_evolution_boundaries_run_through_rare_candy(
    repo_root: Path,
    tmp_path: Path,
    phase_2_constants: dict[str, int],
    evolution_contract: list[dict],
    row_index: int,
) -> None:
    row = evolution_contract[row_index]
    scenario = json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_03_cheat_mode.json").read_text()
    )
    max_frames = 30_000
    source = phase_2_constants[row["source"].upper()]
    target = phase_2_constants[row["target"]]
    with loaded_session(repo_root, tmp_path, scenario) as session:
        _prepare_evolution_candidate(
            session, phase_2_constants, source, phase_2_constants["RARE_CANDY"], 35
        )
        assert session.read_symbol("wPartyMon1Level") == 35
        assert session.read_symbol("wPartySpecies") == source
        _use_first_item_on_first_mon(session, max_frames, "RareCandyEffect")
        advance_with_a_until(
            session,
            lambda current: current.read_symbol("wPartySpecies") == target,
            max_frames,
            f"{row['source']} level-36 evolution",
        )
        assert session.read_symbol("wPartyMon1Level") == 36
        assert read_inventory(session).items == (
            (phase_2_constants["RARE_CANDY"], 1),
        )


@pytest.mark.parametrize(
    "row_index",
    range(4, 10),
    ids=["politoed", "slowking", "steelix", "scizor", "kingdra", "porygon2"],
)
def test_all_direct_item_evolutions_consume_exactly_one_item(
    repo_root: Path,
    tmp_path: Path,
    phase_2_constants: dict[str, int],
    evolution_contract: list[dict],
    row_index: int,
) -> None:
    row = evolution_contract[row_index]
    scenario = json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_03_cheat_mode.json").read_text()
    )
    max_frames = 30_000
    source = phase_2_constants[row["source"].upper()]
    target = phase_2_constants[row["target"]]
    item = phase_2_constants[row["condition"]]
    with loaded_session(repo_root, tmp_path, scenario) as session:
        _prepare_evolution_candidate(session, phase_2_constants, source, item, 35)
        _use_first_item_on_first_mon(session, max_frames, "EvoStoneEffect")
        advance_with_a_until(
            session,
            lambda current: current.read_symbol("wPartySpecies") == target,
            max_frames,
            f"{row['source']} direct-item evolution",
        )
        assert read_inventory(session).items == ((item, 1),)


def test_incompatible_evolution_item_is_preserved(
    repo_root: Path,
    tmp_path: Path,
    phase_2_constants: dict[str, int],
) -> None:
    scenario = json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_03_cheat_mode.json").read_text()
    )
    max_frames = 15_000
    item = phase_2_constants["KINGS_ROCK"]
    with loaded_session(repo_root, tmp_path, scenario) as session:
        _prepare_evolution_candidate(
            session, phase_2_constants, phase_2_constants["ARTICUNO"], item, 35
        )
        session.register_hook("WontHaveAnyEffectMessage")
        _use_first_item_on_first_mon(session, max_frames, "EvoStoneEffect")
        advance_with_a_until(
            session,
            lambda current: "WontHaveAnyEffectMessage" in current.hook_history,
            max_frames,
            "incompatible evolution-item rejection",
        )
        assert read_inventory(session).items == ((item, 2),)
        assert session.read_symbol("wPartySpecies") == phase_2_constants["ARTICUNO"]


def test_gs_ball_delivery_hall_of_fame_gate_and_one_time_receipt(
    repo_root: Path,
    tmp_path: Path,
    phase_2_constants: dict[str, int],
) -> None:
    max_frames = 15_000
    receipt = phase_2_constants[
        "EVENT_GOT_GS_BALL_FROM_GOLDENROD_POKEMON_CENTER"
    ]
    kurt = phase_2_constants["EVENT_CAN_GIVE_GS_BALL_TO_KURT"]
    gs_ball = phase_2_constants["GS_BALL"]

    with loaded_phase_2_checkpoint(
        repo_root,
        tmp_path / "pre-hof",
        phase_2_constants,
        "goldenrod_delivery",
        max_frames,
    ) as session:
        session.tap("down", 2, 20)
        wait_for_idle(session, max_frames)
        assert not event_is_set(session, receipt)
        assert not event_is_set(session, kurt)
        assert not _has_key_item(session, gs_ball)

    with loaded_phase_2_checkpoint(
        repo_root,
        tmp_path / "post-hof",
        phase_2_constants,
        "goldenrod_delivery",
        max_frames,
        hall_of_fame=True,
    ) as session:
        session.enable_script_tracing()
        session.tap("down", 2, 20)
        advance_with_a_until(
            session,
            lambda current: event_is_set(current, receipt),
            max_frames,
            "post-Hall-of-Fame GS Ball receipt",
        )
        _finish_script(session, max_frames, "GS Ball delivery completion")
        assert event_is_set(session, kurt)
        assert read_inventory(session).key_items.count(gs_ball) == 1
        delivery_count = session.script_history.count(
            "GoldenrodPokecenter1F_GSBallSceneLeft.gsball"
        )
        session.tap("down", 2, 20)
        session.tap("up", 2, 20)
        session.tap("down", 2, 20)
        wait_for_idle(session, max_frames)
        assert read_inventory(session).key_items.count(gs_ball) == 1
        assert (
            session.script_history.count(
                "GoldenrodPokecenter1F_GSBallSceneLeft.gsball"
            )
            == delivery_count
        )


def test_full_key_item_delivery_is_atomic_and_retryable(
    repo_root: Path,
    tmp_path: Path,
    phase_2_constants: dict[str, int],
) -> None:
    max_frames = 15_000
    receipt = phase_2_constants[
        "EVENT_GOT_GS_BALL_FROM_GOLDENROD_POKEMON_CENTER"
    ]
    kurt = phase_2_constants["EVENT_CAN_GIVE_GS_BALL_TO_KURT"]
    gs_ball = phase_2_constants["GS_BALL"]
    with loaded_phase_2_checkpoint(
        repo_root,
        tmp_path,
        phase_2_constants,
        "goldenrod_delivery",
        max_frames,
        hall_of_fame=True,
        full_key_items=True,
    ) as session:
        session.tap("down", 2, 20)
        _finish_script(session, max_frames, "full-pocket delivery refusal")
        inventory = read_inventory(session)
        assert len(inventory.key_items) == 25
        assert gs_ball not in inventory.key_items
        assert not event_is_set(session, receipt)
        assert not event_is_set(session, kurt)

    def free_key_slot(session) -> None:
        items = read_inventory(session).key_items[:-1]
        session.write_symbol("wNumKeyItems", len(items))
        session.write_symbol_bytes("wKeyItems", bytes([*items, 0xFF]))

    with loaded_phase_2_checkpoint(
        repo_root,
        tmp_path / "retry",
        phase_2_constants,
        "goldenrod_delivery",
        max_frames,
        hall_of_fame=True,
        full_key_items=True,
        before_overworld=free_key_slot,
    ) as session:
        session.tap("down", 2, 20)
        advance_with_a_until(
            session,
            lambda current: event_is_set(current, receipt),
            max_frames,
            "GS Ball retry after freeing one key-item slot",
        )
        _finish_script(session, max_frames, "retried GS Ball delivery completion")
        assert event_is_set(session, kurt)
        assert _has_key_item(session, gs_ball)


def test_kurt_handoff_preserves_wait_and_unlocks_the_shrine(
    repo_root: Path,
    tmp_path: Path,
    phase_2_constants: dict[str, int],
) -> None:
    max_frames = 15_000
    gave = phase_2_constants["EVENT_GAVE_GS_BALL_TO_KURT"]
    can_give = phase_2_constants["EVENT_CAN_GIVE_GS_BALL_TO_KURT"]
    restless = phase_2_constants["EVENT_FOREST_IS_RESTLESS"]
    gs_ball = phase_2_constants["GS_BALL"]
    with loaded_phase_2_checkpoint(
        repo_root,
        tmp_path,
        phase_2_constants,
        "kurt_wait",
        max_frames,
    ) as session:
        session.enable_script_tracing()
        session.tap("up", 2, 2)
        session.tap("a")
        advance_with_a_until(
            session,
            lambda current: event_is_set(current, gave),
            max_frames,
            "Kurt GS Ball handoff",
        )
        _finish_script(session, max_frames, "Kurt handoff completion")
        assert not _has_key_item(session, gs_ball)
        assert session.read_symbol("wDailyFlags1") & 1

        session.tap("a")
        _finish_script(session, max_frames, "Kurt waiting dialogue")
        assert "Kurt1.GaveGSBallToKurt" in session.script_history
        assert event_is_set(session, gave)
        assert not event_is_set(session, restless)

        session.write_symbol("wDailyFlags1", session.read_symbol("wDailyFlags1") & 0xFE)
        session.tap("a")
        advance_with_a_until(
            session,
            lambda current: event_is_set(current, restless),
            max_frames,
            "Kurt shrine unlock",
        )
        _finish_script(session, max_frames, "Kurt shrine-unlock scene completion")
        assert not event_is_set(session, gave)
        assert not event_is_set(session, can_give)


def _prepare_celebi_party(constants: dict[str, int], *, box_full: bool = False):
    def prepare(session) -> None:
        prepare_battle_party(session, constants, constants["ARTICUNO"], True)
        session.write_symbol("wNumBalls", 1)
        session.write_symbol_bytes(
            "wBalls", bytes([constants["MASTER_BALL"], 1, 0xFF])
        )
        session.write_symbol("wLastPocket", constants["BALL_POCKET"])
        if box_full:
            mon = session.read_symbol_bytes(
                "wPartyMon1", constants["PARTYMON_STRUCT_LENGTH"]
            )
            session.write_symbol("wPartyCount", 6)
            session.write_symbol_bytes(
                "wPartySpecies", bytes([constants["ARTICUNO"]] * 6 + [0xFF])
            )
            session.write_symbol_bytes("wPartyMons", mon * 6)
            session.write_symbol("sBoxCount", 20)
            session.write_symbol_bytes(
                "sBoxSpecies", bytes([constants["ARTICUNO"]] * 20 + [0xFF])
            )

    return prepare


def _start_shrine_battle(session, max_frames: int) -> None:
    session.enable_script_tracing()
    session.register_hook("BattleMenu")
    session.register_hook("CheckCaughtCelebi")
    session.tap("up", 2, 2)
    session.tap("a")
    advance_with_a_until(
        session,
        lambda current: "BattleMenu" in current.hook_history,
        max_frames,
        "Celebi battle menu",
    )


def _assert_celebi_retry_state(session, constants: dict[str, int]) -> None:
    assert event_is_set(session, constants["EVENT_FOREST_IS_RESTLESS"])
    assert _has_key_item(session, constants["GS_BALL"])
    assert not read_progress(session).owns(constants["CELEBI"])
    bit = constants["CELEBIEVENT_FOREST_IS_RESTLESS_F"]
    assert session.read_symbol("wCelebiEvent") & (1 << bit)


def test_celebi_knockout_restores_the_retry_path(
    repo_root: Path,
    tmp_path: Path,
    phase_2_constants: dict[str, int],
) -> None:
    max_frames = 60_000
    with loaded_phase_2_checkpoint(
        repo_root,
        tmp_path,
        phase_2_constants,
        "celebi_shrine",
        max_frames,
        before_overworld=_prepare_celebi_party(phase_2_constants),
    ) as session:
        _start_shrine_battle(session, max_frames)
        advance_with_a_until(
            session,
            lambda current: "CheckCaughtCelebi" in current.hook_history,
            max_frames,
            "knocked-out Celebi result check",
        )
        _finish_script(session, max_frames, "Celebi knockout retry restoration")
        _assert_celebi_retry_state(session, phase_2_constants)

        checked = session.hook_history.count("CheckCaughtCelebi")
        session.tap("up", 2, 2)
        session.tap("a")
        advance_with_a_until(
            session,
            lambda current: current.hook_history.count("BattleMenu") >= 2,
            max_frames,
            "retried Celebi encounter",
        )
        assert session.hook_history.count("CheckCaughtCelebi") == checked


@pytest.mark.parametrize("box_full", [False, True], ids=["capture", "box-full"])
def test_celebi_capture_and_capacity_outcomes(
    repo_root: Path,
    tmp_path: Path,
    phase_2_constants: dict[str, int],
    box_full: bool,
) -> None:
    max_frames = 60_000
    with loaded_phase_2_checkpoint(
        repo_root,
        tmp_path,
        phase_2_constants,
        "celebi_shrine",
        max_frames,
        before_overworld=_prepare_celebi_party(
            phase_2_constants, box_full=box_full
        ),
    ) as session:
        _start_shrine_battle(session, max_frames)
        session.register_hook("PokeBallEffect")
        if box_full:
            session.register_hook("Ball_BoxIsFullMessage")
        session.tap("down", 2, 2)
        session.tap("a", 2, 2)
        advance_with_a_until(
            session,
            lambda current: "PokeBallEffect" in current.hook_history,
            max_frames,
            "Master Ball use",
        )
        if box_full:
            advance_with_a_until(
                session,
                lambda current: "Ball_BoxIsFullMessage" in current.hook_history,
                max_frames,
                "box-full ball rejection",
            )
            session.tap("a", 2, 20)
            assert read_inventory(session).balls == (
                (phase_2_constants["MASTER_BALL"], 1),
            )
            battle_menus = session.hook_history.count("BattleMenu")
            start = session.frames
            while (
                session.hook_history.count("BattleMenu") == battle_menus
                and session.frames - start < max_frames
            ):
                session.tap("b", 2, 20)
            assert session.hook_history.count("BattleMenu") > battle_menus
            session.tap("up", 2, 2)
            session.tap("a", 2, 2)
        advance_with_a_until(
            session,
            lambda current: "CheckCaughtCelebi" in current.hook_history,
            max_frames,
            "Celebi capture result check",
        )
        result = session.read_symbol("wBattleResult")
        _finish_script(session, max_frames, "Celebi capture/capacity completion")
        if box_full:
            _assert_celebi_retry_state(session, phase_2_constants)
        else:
            assert result & (
                1 << phase_2_constants["BATTLERESULT_CAUGHT_CELEBI"]
            )
            assert read_progress(session).owns(phase_2_constants["CELEBI"])
            assert not event_is_set(
                session, phase_2_constants["EVENT_FOREST_IS_RESTLESS"]
            )
            assert not _has_key_item(session, phase_2_constants["GS_BALL"])
            encounters = session.hook_history.count("BattleMenu")
            session.tap("up", 2, 2)
            session.tap("a")
            _finish_script(session, max_frames, "completed shrine reread")
            assert session.hook_history.count("BattleMenu") == encounters
