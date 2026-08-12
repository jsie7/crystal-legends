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
from tests.support.legendary_scenario import (
    advance_with_a_until,
    place_player,
    prepare_battle_party,
    walk_steps,
)
from tests.support.phase_06_scenario import (
    ROAM_STRUCT_LENGTH,
    force_roamer_rng,
    loaded_phase_6_checkpoint,
    loaded_phase_6_saved_game,
    start_roaming_battle,
    start_wild_battle,
)
from tests.support.pyboy_session import PyBoySession
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.emulator, pytest.mark.phase6]


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_06_roamers.json").read_text()
    )


@pytest.fixture(scope="module")
def phase_6_constants(
    repo_root: Path, tmp_path_factory, scenario: dict
) -> dict[str, int]:
    names = {
        "SPAWN_N_A",
        "MAPSETUP_WARP",
        "STATUSFLAGS_POKEDEX_F",
        "EVENT_RELEASED_THE_BEASTS",
        "EVENT_BURNED_TOWER_B1F_BEASTS_1",
        "EVENT_BURNED_TOWER_B1F_BEASTS_2",
        "EVENT_BEAT_TWINS_ANN_AND_ANNE",
        "EVENT_BEAT_PSYCHIC_GREG",
        "EVENT_SAW_SUICUNE_ON_ROUTE_42",
        "PLAYER_SURF",
        "GROUP_N_A",
        "MAP_N_A",
        "BATTLETYPE_ROAMING",
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
        "QUICK_ATTACK",
        "SWIFT",
        "MASTER_BALL",
        "FAST_BALL",
        "BALL_POCKET",
        "LEDYBA",
        "GROWLITHE",
        "PIDGEY",
        "PIDGEOTTO",
        "LEDIAN",
        "SPINARAK",
        "STANTLER",
        "HOOTHOOT",
        "NOCTOWL",
        "ARIADOS",
    }
    for key in ("release", "encounter", "water_rejection"):
        record = scenario[key]
        if "map" in record:
            names.update((f"GROUP_{record['map']}", f"MAP_{record['map']}"))
    names.update(
        (
            f"GROUP_{scenario['encounter']['different_route']}",
            f"MAP_{scenario['encounter']['different_route']}",
        )
    )
    for roamer in scenario["roamers"]:
        names.update(
            (
                roamer["species"],
                f"GROUP_{roamer['starting_route']}",
                f"MAP_{roamer['starting_route']}",
                f"LANDMARK_{roamer['starting_route']}",
            )
        )
    names.update(
        (
            "LANDMARK_ROUTE_37",
            "LANDMARK_ROUTE_38",
            "LANDMARK_ROUTE_42",
        )
    )
    constants = resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_6_runtime_constants"),
        sorted(names),
    )
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    for name in (
        "SCENE_BURNEDTOWERB1F_RELEASE_THE_BEASTS",
        "SCENE_ROUTE42_NOOP",
    ):
        constants[name] = symbols.constant(name)
    return constants


def _roamer(scenario: dict, species: str) -> dict:
    return next(row for row in scenario["roamers"] if row["species"] == species)


def _prepare_party(
    constants: dict[str, int],
    *,
    strong: bool,
    ball: bool = False,
    ball_item: int | None = None,
):
    def prepare(session) -> None:
        prepare_battle_party(session, constants, constants["RAIKOU"], strong)
        if not strong:
            session.write_symbol("wPartyMon1Level", 100)
            session.write_symbol_bytes("wPartyMon1HP", (999).to_bytes(2, "big"))
            session.write_symbol_bytes(
                "wPartyMon1MaxHP", (999).to_bytes(2, "big")
            )
            session.write_symbol_bytes("wPartyMon1Attack", (1).to_bytes(2, "big"))
            session.write_symbol_bytes("wPartyMon1Speed", (999).to_bytes(2, "big"))
            session.write_symbol("wPartyMon1Moves", constants["SWIFT"])
            session.write_symbol("wPartyMon1PP", 20)
        if ball or ball_item is not None:
            item = constants["MASTER_BALL"] if ball_item is None else ball_item
            session.write_symbol("wNumBalls", 1)
            session.write_symbol_bytes(
                "wBalls",
                bytes([item, 1, 0xFF]),
            )
            session.write_symbol("wLastPocket", constants["BALL_POCKET"])

    return prepare


def _prepare_tracker(constants: dict[str, int], species: str):
    party_setup = _prepare_party(constants, strong=True)

    def prepare(session) -> None:
        party_setup(session)
        session.write_symbol("wPrevDexEntry", constants[species])

    return prepare


def test_first_release_initializes_complete_stock_slots(
    repo_root: Path,
    tmp_path: Path,
    phase_6_constants: dict[str, int],
    scenario: dict,
) -> None:
    with loaded_phase_6_checkpoint(
        repo_root,
        tmp_path,
        phase_6_constants,
        scenario,
        checkpoint="release",
    ) as session:
        place_player(session, 10, 7)
        session.enable_script_tracing()
        walk_steps(
            session,
            "up",
            "wYCoord",
            -1,
            1,
            scenario["max_frames_per_step"],
        )
        session.wait_for_script("ReleaseTheBeasts", scenario["max_frames_per_step"])
        session.wait_until(
            lambda current: event_is_set(
                current, phase_6_constants["EVENT_RELEASED_THE_BEASTS"]
            ),
            scenario["max_frames_per_step"],
            "legendary beasts release event",
        )
        wait_for_idle(session, scenario["max_frames_per_step"])
        assert session.read_symbol_bytes("wRoamMon1", ROAM_STRUCT_LENGTH) == bytes(
            [
                phase_6_constants["RAIKOU"],
                40,
                phase_6_constants["GROUP_ROUTE_42"],
                phase_6_constants["MAP_ROUTE_42"],
                0,
                0,
                0,
            ]
        )
        assert session.read_symbol_bytes("wRoamMon2", ROAM_STRUCT_LENGTH) == bytes(
            [
                phase_6_constants["ENTEI"],
                40,
                phase_6_constants["GROUP_ROUTE_37"],
                phase_6_constants["MAP_ROUTE_37"],
                0,
                0,
                0,
            ]
        )


@pytest.mark.parametrize("species", ["RAIKOU", "ENTEI"])
def test_seen_active_roamer_uses_live_pokedex_area_route(
    repo_root: Path,
    tmp_path: Path,
    phase_6_constants: dict[str, int],
    scenario: dict,
    species: str,
) -> None:
    roamer = _roamer(scenario, species)
    with loaded_phase_6_checkpoint(
        repo_root,
        tmp_path,
        phase_6_constants,
        scenario,
        checkpoint="land",
        selected_species=species,
        before_overworld=_prepare_tracker(phase_6_constants, species),
    ) as session:
        nest_landmarks: list[int] = []
        for label in (
            "StartMenu.loop",
            "Pokedex",
            "Pokedex_UpdateMainScreen",
            "Pokedex_InitDexEntryScreen",
            "Pokedex_UpdateDexEntryScreen",
            "DexEntryScreen_MenuActionJumptable.Area",
            "Pokedex_GetArea.loop",
            "FindNest",
            f"FindNest.RoamMon{1 if species == 'RAIKOU' else 2}",
        ):
            session.register_hook(label)
        session.register_hook(
            "StartMenu_Pokedex",
            lambda current: current.pyboy.button_release("a"),
        )
        session.register_hook(
            "Pokedex_GetArea.nestloop",
            lambda current: nest_landmarks.append(current.read_symbol("wTilemap")),
        )
        session.write_symbol_bytes(
            f"{roamer['slot']}MapGroup",
            bytes(
                [
                    phase_6_constants["GROUP_ROUTE_37"],
                    phase_6_constants["MAP_ROUTE_37"],
                ]
            ),
        )
        session.write_symbol("wBattleMenuCursorPosition", 1)
        session.tap("start", 10, 10)
        session.wait_for_hook("StartMenu.loop", scenario["max_frames_per_step"])
        session.tick(60)
        session.tap("a", 10, 10)
        session.wait_for_hook("StartMenu_Pokedex", scenario["max_frames_per_step"])
        session.wait_for_hook("Pokedex", scenario["max_frames_per_step"])
        session.wait_for_hook("Pokedex_UpdateMainScreen", scenario["max_frames_per_step"])
        session.tap("a", 10, 10)
        session.wait_for_hook("Pokedex_UpdateDexEntryScreen", scenario["max_frames_per_step"])
        session.tap("right", 10, 10)
        session.tap("a", 10, 10)
        session.wait_for_hook("Pokedex_GetArea.loop", scenario["max_frames_per_step"])
        assert f"FindNest.RoamMon{1 if species == 'RAIKOU' else 2}" in session.hook_history
        assert nest_landmarks[-1] == phase_6_constants["LANDMARK_ROUTE_37"]

        session.tap("b", 10, 20)
        session.wait_for_hook_count(
            "Pokedex_UpdateDexEntryScreen", 2, scenario["max_frames_per_step"]
        )
        session.write_symbol_bytes(
            f"{roamer['slot']}MapGroup",
            bytes(
                [
                    phase_6_constants["GROUP_ROUTE_38"],
                    phase_6_constants["MAP_ROUTE_38"],
                ]
            ),
        )
        nest_count = len(nest_landmarks)
        session.tap("a", 10, 10)
        session.wait_until(
            lambda current: len(nest_landmarks) > nest_count,
            scenario["max_frames_per_step"],
            "updated Route 38 Pokédex nest",
        )
        assert nest_landmarks[-1] == phase_6_constants["LANDMARK_ROUTE_38"]

        session.tap("b", 10, 20)
        session.wait_for_hook_count(
            "Pokedex_UpdateDexEntryScreen", 3, scenario["max_frames_per_step"]
        )
        session.write_symbol(f"{roamer['slot']}Species", 0)
        nest_count = len(nest_landmarks)
        session.tap("a", 10, 10)
        session.wait_until(
            lambda current: len(nest_landmarks) > nest_count,
            scenario["max_frames_per_step"],
            "cleared Pokédex roamer nest",
        )
        assert nest_landmarks[-1] == 0


@pytest.mark.parametrize("species", ["RAIKOU", "ENTEI"])
def test_same_land_route_enters_the_stock_roaming_battle(
    repo_root: Path,
    tmp_path: Path,
    phase_6_constants: dict[str, int],
    scenario: dict,
    species: str,
) -> None:
    roamer = _roamer(scenario, species)
    with loaded_phase_6_checkpoint(
        repo_root,
        tmp_path,
        phase_6_constants,
        scenario,
        checkpoint="land",
        selected_species=species,
        before_overworld=_prepare_party(phase_6_constants, strong=True),
    ) as session:
        start_roaming_battle(session, phase_6_constants, scenario, roamer)


def test_different_route_and_water_reject_the_roamer_branch(
    repo_root: Path,
    tmp_path: Path,
    phase_6_constants: dict[str, int],
    scenario: dict,
) -> None:
    roamer = _roamer(scenario, "RAIKOU")
    for checkpoint in ("different_route", "water"):
        with loaded_phase_6_checkpoint(
            repo_root,
            tmp_path / checkpoint,
            phase_6_constants,
            scenario,
            checkpoint=checkpoint,
            selected_species="RAIKOU",
            before_overworld=_prepare_party(phase_6_constants, strong=True),
        ) as session:
            session.register_hook("CheckEncounterRoamMon.DontEncounterRoamMon")
            force_roamer_rng(session, roamer["rng_selection"])
            session.write_symbol_bytes("wMornEncounterRate", b"\xff\xff\xff")
            if checkpoint == "water":
                assert session.read_symbol("wPlayerState") == phase_6_constants[
                    "PLAYER_SURF"
                ]
            start = session.frames
            direction_index = 0
            directions = ("right", "left")
            while (
                "CheckEncounterRoamMon.DontEncounterRoamMon"
                not in session.hook_history
                and session.frames - start < scenario["max_frames_per_step"]
            ):
                session.tap(directions[direction_index % 2], 2, 12)
                direction_index += 1
            assert "CheckEncounterRoamMon.DontEncounterRoamMon" in session.hook_history
            assert session.read_symbol("wBattleType") != phase_6_constants[
                "BATTLETYPE_ROAMING"
            ]


def test_flee_persists_hp_and_dvs_through_native_save_reload(
    repo_root: Path,
    tmp_path: Path,
    phase_6_constants: dict[str, int],
    scenario: dict,
) -> None:
    roamer = _roamer(scenario, "RAIKOU")
    max_frames = scenario["max_frames_per_step"]
    saved = tmp_path / "fled.sav"
    with loaded_phase_6_checkpoint(
        repo_root,
        tmp_path / "battle",
        phase_6_constants,
        scenario,
        checkpoint="land",
        selected_species="RAIKOU",
        before_overworld=_prepare_party(phase_6_constants, strong=False),
    ) as session:
        start_roaming_battle(session, phase_6_constants, scenario, roamer)
        initial_hp = session.read_symbol_bytes("wEnemyMonHP", 2)
        lowered_hp = int.from_bytes(initial_hp, "big") - 10
        initial_dvs = session.read_symbol_bytes("wEnemyMonDVs", 2)
        assert initial_dvs != b"\x00\x00"
        session.write_symbol_bytes("wEnemyMonHP", lowered_hp.to_bytes(2, "big"))
        session.write_symbol_bytes("wBattleMonSpeed", (999).to_bytes(2, "big"))
        session.write_symbol_bytes("wEnemyMonSpeed", (1).to_bytes(2, "big"))
        session.write_symbol(
            "wBattleMonMoves", phase_6_constants["QUICK_ATTACK"]
        )
        session.write_symbol("wBattleMonPP", 20)
        session.register_hook("TryEnemyFlee.Flee")
        session.register_hook("BattleEnd_HandleRoamMons")
        session.write_symbol("wBattleMenuCursorPosition", 1)
        advance_with_a_until(
            session,
            lambda current: "BattleEnd_HandleRoamMons" in current.hook_history,
            max_frames,
            "roamer flee battle end",
        )
        session.tick(30)
        stored = session.read_symbol_bytes(roamer["slot"], ROAM_STRUCT_LENGTH)
        assert stored[0] == phase_6_constants["RAIKOU"]
        assert "TryEnemyFlee.Flee" in session.hook_history
        assert stored[4] == lowered_hp
        assert stored[5:7] == initial_dvs
        session.wait_until(
            lambda current: current.read_symbol("wBattleMode") == 0,
            max_frames,
            "battle cleanup after roamer flee",
        )
        wait_for_idle(session, max_frames)
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, saved)

    with loaded_phase_6_saved_game(
        repo_root,
        tmp_path / "reload",
        phase_6_constants,
        scenario,
        saved,
    ) as session:
        assert session.read_symbol_bytes(roamer["slot"], ROAM_STRUCT_LENGTH) == stored


def _use_fast_ball_and_record_multiplier(
    session: PyBoySession,
    max_frames: int,
) -> tuple[int, int]:
    observed: dict[str, int] = {}

    def record_before(current: PyBoySession) -> None:
        observed.setdefault("before", current.pyboy.register_file.B)

    def record_after(current: PyBoySession) -> None:
        observed.setdefault("after", current.pyboy.register_file.B)

    session.register_hook(
        "FastBallMultiplier",
        record_before,
    )
    session.register_hook(
        "PokeBallEffect.skip_or_return_from_ball_fn",
        record_after,
    )
    session.write_symbol("wBattleMenuCursorPosition", 3)
    session.tap("a", 2, 2)
    advance_with_a_until(
        session,
        lambda current: "after" in observed,
        max_frames,
        "Fast Ball multiplier return",
    )
    assert "FastBallMultiplier" in session.hook_history
    return observed["before"], observed["after"]


def test_fast_ball_boosts_entei_as_second_always_flee_species(
    repo_root: Path,
    tmp_path: Path,
    phase_6_constants: dict[str, int],
    scenario: dict,
) -> None:
    roamer = _roamer(scenario, "ENTEI")
    with loaded_phase_6_checkpoint(
        repo_root,
        tmp_path,
        phase_6_constants,
        scenario,
        checkpoint="land",
        selected_species="ENTEI",
        before_overworld=_prepare_party(
            phase_6_constants,
            strong=True,
            ball_item=phase_6_constants["FAST_BALL"],
        ),
    ) as session:
        start_roaming_battle(session, phase_6_constants, scenario, roamer)
        before, after = _use_fast_ball_and_record_multiplier(
            session, scenario["max_frames_per_step"]
        )
        assert session.read_symbol("wTempEnemyMonSpecies") == phase_6_constants[
            "ENTEI"
        ]
        assert after == min(before * 4, 0xFF)


def test_fast_ball_leaves_route_37_non_fleeing_species_unchanged(
    repo_root: Path,
    tmp_path: Path,
    phase_6_constants: dict[str, int],
    scenario: dict,
) -> None:
    route_37_species = {
        phase_6_constants[name]
        for name in (
            "LEDYBA",
            "GROWLITHE",
            "PIDGEY",
            "PIDGEOTTO",
            "LEDIAN",
            "SPINARAK",
            "STANTLER",
            "HOOTHOOT",
            "NOCTOWL",
            "ARIADOS",
        )
    }
    with loaded_phase_6_checkpoint(
        repo_root,
        tmp_path,
        phase_6_constants,
        scenario,
        checkpoint="land",
        selected_species="ENTEI",
        before_overworld=_prepare_party(
            phase_6_constants,
            strong=True,
            ball_item=phase_6_constants["FAST_BALL"],
        ),
    ) as session:
        start_wild_battle(session, phase_6_constants, scenario)
        assert session.read_symbol("wTempEnemyMonSpecies") in route_37_species
        before, after = _use_fast_ball_and_record_multiplier(
            session, scenario["max_frames_per_step"]
        )
        assert after == before


@pytest.mark.parametrize("species", ["RAIKOU", "ENTEI"])
@pytest.mark.parametrize("outcome", ["defeat", "capture"])
def test_defeat_and_capture_remain_permanent_after_save_reload(
    repo_root: Path,
    tmp_path: Path,
    phase_6_constants: dict[str, int],
    scenario: dict,
    species: str,
    outcome: str,
) -> None:
    roamer = _roamer(scenario, species)
    max_frames = scenario["max_frames_per_step"]
    saved = tmp_path / f"{species.lower()}-{outcome}.sav"
    with loaded_phase_6_checkpoint(
        repo_root,
        tmp_path / "battle",
        phase_6_constants,
        scenario,
        checkpoint="land",
        selected_species=species,
        before_overworld=_prepare_party(
            phase_6_constants, strong=True, ball=outcome == "capture"
        ),
    ) as session:
        start_roaming_battle(session, phase_6_constants, scenario, roamer)
        session.register_hook("BattleEnd_HandleRoamMons")
        session.register_hook("BattleEnd_HandleRoamMons.caught_or_defeated_roam_mon")
        if outcome == "capture":
            session.register_hook("PokeBallEffect")
            session.write_symbol("wBattleMenuCursorPosition", 3)
            session.tap("a", 2, 2)
            advance_with_a_until(
                session,
                lambda current: "PokeBallEffect" in current.hook_history,
                max_frames,
                "Master Ball use",
            )
        else:
            session.write_symbol_bytes("wBattleMonSpeed", (999).to_bytes(2, "big"))
            session.write_symbol_bytes("wEnemyMonSpeed", (1).to_bytes(2, "big"))
            session.write_symbol(
                "wBattleMonMoves", phase_6_constants["QUICK_ATTACK"]
            )
            session.write_symbol("wBattleMonPP", 20)
            session.register_hook(
                "HasEnemyFainted",
                lambda current: current.write_symbol_bytes(
                    "wEnemyMonHP", b"\x00\x00"
                ),
            )
            session.write_symbol("wBattleMenuCursorPosition", 1)
        advance_with_a_until(
            session,
            lambda current: (
                "BattleEnd_HandleRoamMons.caught_or_defeated_roam_mon"
                in current.hook_history
            ),
            max_frames,
            f"roamer {outcome} removal",
        )
        session.tick(30)
        assert session.read_symbol(f"{roamer['slot']}Species") == 0
        if outcome == "capture":
            assert read_progress(session).owns(phase_6_constants[species])
        session.wait_until(
            lambda current: current.read_symbol("wBattleMode") == 0,
            max_frames,
            f"battle cleanup after roamer {outcome}",
        )
        wait_for_idle(session, max_frames)
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, saved)

    with loaded_phase_6_saved_game(
        repo_root,
        tmp_path / "reload",
        phase_6_constants,
        scenario,
        saved,
    ) as session:
        assert session.read_symbol_bytes(roamer["slot"], ROAM_STRUCT_LENGTH)[:5] == bytes(
            [
                0,
                40,
                phase_6_constants["GROUP_N_A"] & 0xFF,
                phase_6_constants["MAP_N_A"] & 0xFF,
                0,
            ]
        )
        if outcome == "capture":
            assert read_progress(session).owns(phase_6_constants[species])
