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
from tests.support.legendary_scenario import (
    advance_with_a_until,
    place_player,
    prepare_battle_party,
    walk_steps,
)
from tests.support.phase_11_scenario import (
    caught_bitfield,
    loaded_phase_11_checkpoint,
    loaded_phase_11_saved_game,
)


pytestmark = [pytest.mark.emulator, pytest.mark.phase11]


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_11_endgame.json").read_text()
    )


@pytest.fixture(scope="module")
def phase_11_runtime_constants(
    repo_root: Path, tmp_path_factory, scenario: dict
) -> dict[str, int]:
    names = {
        "SPAWN_N_A",
        "SPAWN_RED",
        "SPAWN_OAK",
        "SPAWN_PALLET",
        "MAPSETUP_WARP",
        "OW_UP",
        "OW_LEFT",
        "GROUP_OAKS_LAB",
        "MAP_OAKS_LAB",
        "GROUP_SILVER_CAVE_ROOM_3",
        "MAP_SILVER_CAVE_ROOM_3",
        "GROUP_SILVER_CAVE_POKECENTER_1F",
        "MAP_SILVER_CAVE_POKECENTER_1F",
        "GROUP_SILVER_CAVE_OUTSIDE",
        "MAP_SILVER_CAVE_OUTSIDE",
        "GROUP_PALLET_TOWN",
        "MAP_PALLET_TOWN",
        "STATUSFLAGS_HALL_OF_FAME_F",
        "EVENT_OPENED_MT_SILVER",
        "EVENT_TALKED_TO_OAK_IN_KANTO",
        "EVENT_RED_IN_MT_SILVER",
        "EVENT_BEAT_RED",
        "EVENT_BEAT_PROFESSOR_OAK",
        "EVENT_GOT_ARTICUNO_FROM_ELM",
        "EVENT_GOT_ZAPDOS_FROM_ELM",
        "EVENT_GOT_MOLTRES_FROM_ELM",
        "POKEMON_PROF",
        "RED",
        "RED1",
        "OAK_ARTICUNO_PLAYER",
        "OAK_ZAPDOS_PLAYER",
        "OAK_MOLTRES_PLAYER",
        "WIN",
        "LOSE",
        "ARTICUNO",
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
    for boss in (scenario["red"],):
        for _, species, moves in boss["party"]:
            names.add(species)
            names.update(moves)
    for branch in scenario["oak"]["parties"]:
        names.add(branch["starter"])
        names.add(branch["trainer"])
    for _, species, moves in scenario["oak"]["common"]:
        names.add(species)
        names.update(moves)
    names.add(scenario["oak"]["ace"][1])
    names.update(scenario["oak"]["ace"][2])
    return resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_11_runtime_constants"),
        sorted(names),
    )


def _event(session, constants: dict[str, int], name: str) -> bool:
    return event_is_set(session, constants[name])


def _strong_party(constants: dict[str, int]):
    def prepare(session) -> None:
        prepare_battle_party(session, constants, constants["ARTICUNO"], True)

    return prepare


def _interact_with_oak(
    session, constants: dict[str, int], max_frames: int, *, decline: bool = False
) -> None:
    session.enable_script_tracing()
    yes_no_count = session.hook_history.count("_YesNoBox") + 1
    session.register_hook("_YesNoBox")
    place_player(session, 4, 3)
    session.write_symbol("wPlayerDirection", constants["OW_UP"])
    session.tap("a", 2, 10)
    session.wait_for_script("Phase11OakEndgameScript", max_frames)
    if decline:
        advance_with_a_until(
            session,
            lambda current: current.hook_history.count("_YesNoBox") >= yes_no_count,
            max_frames,
            "Oak challenge prompt",
        )
        session.tap("b", 2, 10)
    advance_with_a_until(
        session,
        lambda current: current.read_symbol("wScriptMode") == 0,
        max_frames,
        "Oak interaction completion",
    )
    wait_for_idle(session, max_frames)


def _begin_oak_battle(session, constants: dict[str, int], max_frames: int) -> None:
    session.register_hook("_YesNoBox")
    session.register_hook("ReadTrainerParty")
    session.enable_script_tracing()
    place_player(session, 4, 3)
    session.write_symbol("wPlayerDirection", constants["OW_UP"])
    yes_no_count = session.hook_history.count("_YesNoBox") + 1
    party_count = session.hook_history.count("ReadTrainerParty") + 1
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("_YesNoBox") >= yes_no_count,
        max_frames,
        "Oak challenge prompt",
    )
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("ReadTrainerParty") >= party_count,
        max_frames,
        "Oak party load",
    )


def _begin_red_battle(session, constants: dict[str, int], max_frames: int) -> None:
    session.register_hook("ReadTrainerParty")
    place_player(session, 9, 11)
    session.write_symbol("wPlayerDirection", constants["OW_UP"])
    party_count = session.hook_history.count("ReadTrainerParty") + 1
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("ReadTrainerParty") >= party_count,
        max_frames,
        "Red party load",
    )
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("ReadTrainerParty") >= party_count,
        max_frames,
        "Oak party load",
    )


def _skip_credits_to_map(
    session,
    constants: dict[str, int],
    map_name: str,
    max_frames: int,
) -> None:
    start = session.frames
    while session.frames - start < max_frames:
        if (
            session.read_symbol("wMapGroup") == constants[f"GROUP_{map_name}"]
            and session.read_symbol("wMapNumber") == constants[f"MAP_{map_name}"]
            and session.read_symbol("wBattleMode") == 0
        ):
            _wait_for_overworld_input(session, max_frames, map_name)
            return
        session.tap("start", 2, 12)
        session.tap("a", 2, 12)
    session.wait_until(lambda current: False, 1, f"credits return to {map_name}")


def _wait_for_overworld_input(
    session, max_frames: int, description: str
) -> None:
    menu_check_count = session.hook_history.count("CheckMenuOW") + 1
    session.register_hook("CheckMenuOW")
    session.wait_until(
        lambda current: current.hook_history.count("CheckMenuOW")
        >= menu_check_count,
        max_frames,
        f"ready overworld input on {description}",
    )
    wait_for_idle(session, max_frames)


def test_caught_bitfields_cover_exact_boundaries_and_omission_sets() -> None:
    for count in (0, 239, 240, 251):
        dex = caught_bitfield(count)
        assert sum(value.bit_count() for value in dex) == count
        assert dex[-1] & 0b11111000 == 0
    rare_omissions = (144, 145, 146, 150, 151, 243, 244, 245, 249, 250, 251)
    alternate = tuple(range(1, 12))
    assert caught_bitfield(240, rare_omissions) != caught_bitfield(240, alternate)


def test_pre_phase_11_save_starts_with_both_completion_facts_clear(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_11_runtime_constants: dict[str, int],
) -> None:
    constants = phase_11_runtime_constants
    canonical = repo_root / "tests/fixtures/saves" / scenario["save_fixture"]
    with loaded_phase_11_saved_game(
        repo_root, tmp_path, constants, scenario, canonical
    ) as session:
        assert not _event(session, constants, "EVENT_BEAT_RED")
        assert not _event(session, constants, "EVENT_BEAT_PROFESSOR_OAK")


@pytest.mark.parametrize(
    "omissions",
    [
        (144, 145, 146, 150, 151, 243, 244, 245, 249, 250, 251),
        tuple(range(1, 12)),
    ],
    ids=["rare-story-species", "early-dex-species"],
)
def test_any_240_species_reaches_the_same_oak_offer(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_11_runtime_constants: dict[str, int],
    omissions: tuple[int, ...],
) -> None:
    constants = phase_11_runtime_constants
    with loaded_phase_11_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        checkpoint="oak",
        caught=240,
        omissions=omissions,
        red_defeated=True,
    ) as session:
        _interact_with_oak(
            session, constants, scenario["max_frames_per_step"], decline=True
        )
        assert "Phase11OakEndgameScript.Declined" in session.script_history
        assert not _event(session, constants, "EVENT_BEAT_PROFESSOR_OAK")


@pytest.mark.parametrize(
    ("red_defeated", "caught", "oak_defeated", "expected_label", "offer"),
    [
        (False, 239, False, "Phase11OakEndgameScript.OrdinaryGoodbye", False),
        (False, 240, False, "Phase11OakEndgameScript.ReadyBeforeRed", False),
        (False, 251, False, "Phase11OakEndgameScript.ReadyBeforeRed", False),
        (True, 239, False, "Phase11OakEndgameScript.BelowRequirement", False),
        (True, 240, False, "Phase11OakEndgameScript.Declined", True),
        (True, 251, False, "Phase11OakEndgameScript.Declined", True),
        (True, 240, True, "Phase11OakEndgameScript.Complete", False),
    ],
)
def test_oak_unlock_truth_table_runs_through_normal_interaction(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_11_runtime_constants: dict[str, int],
    red_defeated: bool,
    caught: int,
    oak_defeated: bool,
    expected_label: str,
    offer: bool,
) -> None:
    constants = phase_11_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    case = f"{int(red_defeated)}-{caught}-{int(oak_defeated)}"
    with loaded_phase_11_checkpoint(
        repo_root,
        tmp_path / case,
        constants,
        scenario,
        checkpoint="oak",
        caught=caught,
        red_defeated=red_defeated,
        oak_defeated=oak_defeated,
    ) as session:
        session.register_hook("ProfOaksPCBoot")
        session.register_hook("ReadTrainerParty")
        _interact_with_oak(session, constants, max_frames, decline=offer)
        assert expected_label in session.script_history
        assert ("ProfOaksPCBoot" in session.hook_history) is not oak_defeated
        assert "ReadTrainerParty" not in session.hook_history
        assert _event(session, constants, "EVENT_BEAT_RED") is red_defeated
        assert _event(session, constants, "EVENT_BEAT_PROFESSOR_OAK") is oak_defeated


@pytest.mark.parametrize(
    ("starter_event", "trainer", "starter"),
    [
        ("EVENT_GOT_ARTICUNO_FROM_ELM", "OAK_ARTICUNO_PLAYER", "CHARIZARD"),
        ("EVENT_GOT_ZAPDOS_FROM_ELM", "OAK_ZAPDOS_PLAYER", "VENUSAUR"),
        ("EVENT_GOT_MOLTRES_FROM_ELM", "OAK_MOLTRES_PLAYER", "BLASTOISE"),
    ],
)
def test_oak_selects_exactly_one_branch_party(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_11_runtime_constants: dict[str, int],
    starter_event: str,
    trainer: str,
    starter: str,
) -> None:
    constants = phase_11_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_11_checkpoint(
        repo_root,
        tmp_path / trainer,
        constants,
        scenario,
        checkpoint="oak",
        caught=240,
        starter_event=starter_event,
        red_defeated=True,
        before_overworld=_strong_party(constants),
    ) as session:
        _begin_oak_battle(session, constants, max_frames)
        assert session.read_symbol("wOtherTrainerClass") == constants["POKEMON_PROF"]
        assert session.read_symbol("wOtherTrainerID") == constants[trainer]
        session.wait_until(
            lambda current: current.read_symbol("wOTPartyCount") == 6,
            max_frames,
            "Oak six-Pokemon party",
        )
        species = session.read_symbol_bytes("wOTPartySpecies", 6)
        assert species[4] == constants[starter]
        assert species[5] == constants["TYRANITAR"]
        assert not _event(session, constants, "EVENT_BEAT_PROFESSOR_OAK")


def test_declining_oak_twice_leaves_the_offer_retryable(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_11_runtime_constants: dict[str, int],
) -> None:
    constants = phase_11_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_11_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        checkpoint="oak",
        caught=240,
        red_defeated=True,
    ) as session:
        session.register_hook("_YesNoBox")
        _interact_with_oak(session, constants, max_frames, decline=True)
        first = session.hook_history.count("_YesNoBox")
        _interact_with_oak(session, constants, max_frames, decline=True)
        assert session.hook_history.count("_YesNoBox") == first + 1
        assert not _event(session, constants, "EVENT_BEAT_PROFESSOR_OAK")


def test_invalid_starter_state_never_defaults_to_an_oak_party(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_11_runtime_constants: dict[str, int],
) -> None:
    constants = phase_11_runtime_constants
    with loaded_phase_11_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        checkpoint="oak",
        caught=240,
        starter_event=None,
        red_defeated=True,
    ) as session:
        session.register_hook("ReadTrainerParty")
        _interact_with_oak(
            session, constants, scenario["max_frames_per_step"], decline=False
        )
        assert "ReadTrainerParty" not in session.hook_history
        assert session.read_symbol("wOtherTrainerClass") == 0
        assert not _event(session, constants, "EVENT_BEAT_PROFESSOR_OAK")


def test_oak_loss_sets_no_completion_fact(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_11_runtime_constants: dict[str, int],
) -> None:
    constants = phase_11_runtime_constants
    max_frames = scenario["max_frames_per_step"]

    def weak_party(session) -> None:
        prepare_battle_party(session, constants, constants["ARTICUNO"], False)

    with loaded_phase_11_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        checkpoint="oak",
        caught=240,
        red_defeated=True,
        before_overworld=weak_party,
    ) as session:
        session.register_hook("ExitBattle")
        session.register_hook(
            "HasPlayerFainted",
            lambda current: current.write_symbol_bytes("wBattleMonHP", b"\0\0"),
        )
        _begin_oak_battle(session, constants, max_frames)
        session.write_symbol("wBattleMenuCursorPosition", 1)
        advance_with_a_until(
            session,
            lambda current: "ExitBattle" in current.hook_history,
            max_frames,
            "Oak player loss",
        )
        assert session.read_symbol("wBattleResult") == constants["LOSE"]
        session.wait_until(
            lambda current: current.read_symbol("wBattleMode") == 0,
            max_frames,
            "Oak loss whiteout",
        )
        assert not _event(session, constants, "EVENT_BEAT_PROFESSOR_OAK")


def test_red_loss_preserves_retry_state(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_11_runtime_constants: dict[str, int],
) -> None:
    constants = phase_11_runtime_constants
    max_frames = scenario["max_frames_per_step"]

    def weak_party(session) -> None:
        prepare_battle_party(session, constants, constants["ARTICUNO"], False)

    with loaded_phase_11_checkpoint(
        repo_root,
        tmp_path,
        constants,
        scenario,
        checkpoint="red",
        caught=0,
        before_overworld=weak_party,
    ) as session:
        session.register_hook("ReadTrainerParty")
        session.register_hook("ExitBattle")
        session.register_hook(
            "HasPlayerFainted",
            lambda current: current.write_symbol_bytes("wBattleMonHP", b"\0\0"),
        )
        _begin_red_battle(session, constants, max_frames)
        session.write_symbol("wBattleMenuCursorPosition", 1)
        advance_with_a_until(
            session,
            lambda current: "ExitBattle" in current.hook_history,
            max_frames,
            "Red player loss",
        )
        assert session.read_symbol("wBattleResult") == constants["LOSE"]
        session.wait_until(
            lambda current: current.read_symbol("wBattleMode") == 0,
            max_frames,
            "Red loss whiteout",
        )
        assert not _event(session, constants, "EVENT_BEAT_RED")
        assert not _event(session, constants, "EVENT_RED_IN_MT_SILVER")


@pytest.mark.parametrize("oak_defeated", [False, True], ids=["first-win", "post-oak-rematch"])
def test_red_victory_and_post_oak_rematch_both_return_to_mt_silver(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_11_runtime_constants: dict[str, int],
    oak_defeated: bool,
) -> None:
    constants = phase_11_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    with loaded_phase_11_checkpoint(
        repo_root,
        tmp_path / str(int(oak_defeated)),
        constants,
        scenario,
        checkpoint="red",
        caught=240,
        red_defeated=oak_defeated,
        oak_defeated=oak_defeated,
        red_visible=True,
        before_overworld=_strong_party(constants),
    ) as session:
        session.register_hook("ExitBattle")
        session.register_hook("RedCredits")
        session.register_hook("HealParty")
        session.register_hook(
            "HasEnemyFainted",
            lambda current: current.write_symbol_bytes("wEnemyMonHP", b"\0\0"),
        )
        _begin_red_battle(session, constants, max_frames)
        assert session.read_symbol("wOtherTrainerClass") == constants["RED"]
        assert session.read_symbol("wOtherTrainerID") == constants["RED1"]
        session.wait_until(
            lambda current: current.read_symbol("wOTPartyCount") == 6,
            max_frames,
            "Red six-Pokemon party",
        )
        if not oak_defeated:
            length = constants["PARTYMON_STRUCT_LENGTH"]
            party = session.read_symbol_bytes("wOTPartyMon1", length * 6)
            for index, (level, species, moves) in enumerate(scenario["red"]["party"]):
                member = party[index * length : (index + 1) * length]
                assert member[constants["MON_LEVEL"]] == level
                assert member[constants["MON_SPECIES"]] == constants[species]
                assert member[
                    constants["MON_MOVES"] : constants["MON_MOVES"] + 4
                ] == bytes(constants[move] for move in moves)

        session.write_symbol("wBattleMenuCursorPosition", 1)
        advance_with_a_until(
            session,
            lambda current: _event(current, constants, "EVENT_BEAT_RED"),
            max_frames,
            "durable Red victory",
        )
        advance_with_a_until(
            session,
            lambda current: "RedCredits" in current.hook_history,
            max_frames,
            "Red credits entry",
        )
        assert _event(session, constants, "EVENT_RED_IN_MT_SILVER")
        assert "HealParty" in session.hook_history
        session.tick(30)
        assert session.read_symbol("wSpawnAfterChampion") == constants["SPAWN_RED"]
        _skip_credits_to_map(session, constants, "SILVER_CAVE_OUTSIDE", max_frames)
        assert session.read_symbol("wSpawnAfterChampion") == 0
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            23,
            20,
        )
        assert _event(session, constants, "EVENT_BEAT_PROFESSOR_OAK") is oak_defeated


def test_oak_victory_runs_true_ending_returns_to_pallet_and_persists(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_11_runtime_constants: dict[str, int],
) -> None:
    constants = phase_11_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    persisted = tmp_path / "phase-11-complete.sav"
    with loaded_phase_11_checkpoint(
        repo_root,
        tmp_path / "victory",
        constants,
        scenario,
        checkpoint="oak",
        caught=240,
        red_defeated=True,
        before_overworld=_strong_party(constants),
    ) as session:
        initial_hof_count = session.read_symbol("wHallOfFameCount")
        session.register_hook("Phase11PrepareOakCredits")
        session.register_hook("RedCredits")
        session.register_hook("ExitBattle")
        session.register_hook(
            "BattleMenu",
            lambda current: current.write_symbol("wBattleMenuCursorPosition", 1),
        )
        session.register_hook("HealParty")
        session.register_hook(
            "HasEnemyFainted",
            lambda current: current.write_symbol_bytes("wEnemyMonHP", b"\0\0"),
        )
        _begin_oak_battle(session, constants, max_frames)
        assert not _event(session, constants, "EVENT_BEAT_PROFESSOR_OAK")
        advance_with_a_until(
            session,
            lambda current: "BattleMenu" in current.hook_history,
            5000,
            "Oak first battle menu",
        )
        session.write_symbol("wBattleMenuCursorPosition", 1)
        advance_with_a_until(
            session,
            lambda current: "ExitBattle" in current.hook_history,
            max_frames,
            "Oak battle victory",
        )
        assert session.read_symbol("wBattleResult") == constants["WIN"]
        advance_with_a_until(
            session,
            lambda current: _event(current, constants, "EVENT_BEAT_PROFESSOR_OAK"),
            max_frames,
            "Oak completion fact",
        )
        assert "Phase11PrepareOakCredits" not in session.hook_history
        advance_with_a_until(
            session,
            lambda current: "Phase11PrepareOakCredits" in current.hook_history,
            max_frames,
            "Oak credits preparation",
        )
        session.tick(10)
        assert session.read_symbol("wSpawnAfterChampion") == constants["SPAWN_OAK"]
        assert session.read_symbol_bytes("wPartyMon1HP", 2) == session.read_symbol_bytes(
            "wPartyMon1MaxHP", 2
        )
        advance_with_a_until(
            session,
            lambda current: "RedCredits" in current.hook_history,
            max_frames,
            "true-ending credits entry",
        )
        session.tick(30)
        assert session.read_symbol("wSpawnAfterChampion") == constants["SPAWN_OAK"]
        _skip_credits_to_map(session, constants, "PALLET_TOWN", max_frames)
        assert session.read_symbol("wSpawnAfterChampion") == 0
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            scenario["post_credits"]["x"],
            scenario["post_credits"]["y"],
        )
        assert session.read_symbol("wHallOfFameCount") == initial_hof_count
        assert _event(session, constants, "EVENT_BEAT_RED")
        assert _event(session, constants, "EVENT_BEAT_PROFESSOR_OAK")
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, persisted)

    with loaded_phase_11_saved_game(
        repo_root,
        tmp_path / "reload",
        constants,
        scenario,
        persisted,
    ) as session:
        assert _event(session, constants, "EVENT_BEAT_RED")
        assert _event(session, constants, "EVENT_BEAT_PROFESSOR_OAK")
        assert (
            session.read_symbol("wMapGroup"),
            session.read_symbol("wMapNumber"),
            session.read_symbol("wXCoord"),
            session.read_symbol("wYCoord"),
        ) == (
            constants["GROUP_PALLET_TOWN"],
            constants["MAP_PALLET_TOWN"],
            scenario["post_credits"]["x"],
            scenario["post_credits"]["y"],
        )
        place_player(session, 12, 12)
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        session.tap("up", 2, 20)
        session.wait_until(
            lambda current: (
                current.read_symbol("wMapGroup"), current.read_symbol("wMapNumber")
            )
            == (constants["GROUP_OAKS_LAB"], constants["MAP_OAKS_LAB"]),
            max_frames,
            "Oak's Lab entry after true ending",
        )
        _wait_for_overworld_input(session, max_frames, "Oak's Lab")
        walk_steps(session, "up", "wYCoord", -1, 7, max_frames)
        _interact_with_oak(session, constants, max_frames)
        assert "Phase11OakEndgameScript.Complete" in session.script_history


def test_reference_oak_and_red_keep_their_stock_runtime_paths(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    phase_11_runtime_constants: dict[str, int],
) -> None:
    constants = phase_11_runtime_constants
    max_frames = scenario["max_frames_per_step"]
    forbidden = ("Phase11OakEndgameScript", "Phase11PrepareOakCredits")

    with loaded_phase_11_checkpoint(
        repo_root,
        tmp_path / "oak",
        constants,
        scenario,
        checkpoint="oak",
        caught=240,
        red_defeated=False,
        reference=True,
    ) as session:
        assert all(label not in session.symbols for label in forbidden)
        session.register_hook("ProfOaksPCBoot")
        session.register_hook("ReadTrainerParty")
        place_player(session, 4, 3)
        session.write_symbol("wPlayerDirection", constants["OW_UP"])
        session.tap("a", 2, 10)
        advance_with_a_until(
            session,
            lambda current: "ProfOaksPCBoot" in current.hook_history,
            max_frames,
            "stock Oak Pokedex rating",
        )
        advance_with_a_until(
            session,
            lambda current: current.read_symbol("wScriptMode") == 0,
            max_frames,
            "stock Oak interaction completion",
        )
        assert "ReadTrainerParty" not in session.hook_history

    with loaded_phase_11_checkpoint(
        repo_root,
        tmp_path / "red",
        constants,
        scenario,
        checkpoint="red",
        caught=0,
        before_overworld=_strong_party(constants),
        reference=True,
    ) as session:
        assert all(label not in session.symbols for label in forbidden)
        session.register_hook("RedCredits")
        session.register_hook(
            "HasEnemyFainted",
            lambda current: current.write_symbol_bytes("wEnemyMonHP", b"\0\0"),
        )
        _begin_red_battle(session, constants, max_frames)
        session.wait_until(
            lambda current: current.read_symbol("wOTPartyCount") == 6,
            max_frames,
            "stock Red six-Pokemon party",
        )
        length = constants["PARTYMON_STRUCT_LENGTH"]
        party = session.read_symbol_bytes("wOTPartyMon1", length * 6)
        assert [
            party[index * length + constants["MON_LEVEL"]] for index in range(6)
        ] == [81, 73, 75, 77, 77, 77]
        session.write_symbol("wBattleMenuCursorPosition", 1)
        advance_with_a_until(
            session,
            lambda current: "RedCredits" in current.hook_history,
            max_frames,
            "stock Red credits entry",
        )
        _skip_credits_to_map(
            session, constants, "SILVER_CAVE_OUTSIDE", max_frames
        )
        assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
            23,
            20,
        )
