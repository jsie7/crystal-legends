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
from tests.support.legendary_scenario import place_player, walk_steps
from tests.support.phase_04_scenario import (
    clear_current_box,
    interact_with_phase_4_gift,
    loaded_phase_4_checkpoint,
    loaded_phase_4_saved_game,
    retarget_phase_4_save,
    set_current_box_full,
    set_party_full,
)
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.emulator, pytest.mark.phase4]


@pytest.fixture(scope="module")
def scenarios(repo_root: Path) -> list[dict]:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_04_johto_gifts.json").read_text()
    )


@pytest.fixture(scope="module")
def phase_4_constants(
    repo_root: Path, tmp_path_factory, scenarios: list[dict]
) -> dict[str, int]:
    names = {
        "SPAWN_N_A",
        "MAPSETUP_WARP",
        "PARTY_LENGTH",
        "MONS_PER_BOX",
        "EEVEE",
        "EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST",
        "EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER",
        "EVENT_GOT_TOTODILE_FROM_CIANWOOD",
        "EVENT_BURNED_TOWER_B1F_BEASTS_1",
        "EVENT_BURNED_TOWER_B1F_BEASTS_2",
        "EVENT_SAW_SUICUNE_AT_CIANWOOD_CITY",
        "RAIKOU",
        "ENTEI",
        "SECRETPOTION",
        "EVENT_JASMINE_RETURNED_TO_GYM",
    }
    for scenario in scenarios:
        names.update(
            {
                scenario["species"],
                scenario["prerequisite_event"],
                scenario["completion_event"],
                f"GROUP_{scenario['map']}",
                f"MAP_{scenario['map']}",
            }
        )
    constants = resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_4_runtime_constants"),
        sorted(names),
    )
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    for scene in (
        "SCENE_BURNEDTOWERB1F_RELEASE_THE_BEASTS",
        "SCENE_BURNEDTOWERB1F_NOOP",
    ):
        constants[scene] = symbols.constant(scene)
    return constants


@pytest.fixture(scope="module")
def chikorita(scenarios: list[dict]) -> dict:
    return next(row for row in scenarios if row["species"] == "CHIKORITA")


@pytest.fixture(scope="module")
def cyndaquil(scenarios: list[dict]) -> dict:
    return next(row for row in scenarios if row["species"] == "CYNDAQUIL")


@pytest.fixture(scope="module")
def totodile(scenarios: list[dict]) -> dict:
    return next(row for row in scenarios if row["species"] == "TOTODILE")


@pytest.fixture(scope="module")
def implemented_gifts(
    chikorita: dict, cyndaquil: dict, totodile: dict
) -> dict[str, dict]:
    return {row["species"]: row for row in (chikorita, cyndaquil, totodile)}


def test_chikorita_requires_cut_and_decline_remains_retryable(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    chikorita: dict,
) -> None:
    completion = phase_4_constants[chikorita["completion_event"]]
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "not-ready",
        phase_4_constants,
        chikorita,
        prerequisite=False,
    ) as session:
        before = read_progress(session)
        yes_no_count = session.hook_history.count("_YesNoBox")
        assert interact_with_phase_4_gift(session, chikorita, accept=None) is None
        assert session.hook_history.count("_YesNoBox") == yes_no_count
        assert not event_is_set(session, completion)
        assert read_progress(session) == before

    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "decline",
        phase_4_constants,
        chikorita,
        prerequisite=True,
    ) as session:
        assert interact_with_phase_4_gift(session, chikorita, accept=False) is None
        assert not event_is_set(session, completion)
        assert read_progress(session).party.count == 0
        assert interact_with_phase_4_gift(session, chikorita, accept=False) is None
        assert session.script_history.count(chikorita["script"]) == 2


@pytest.mark.parametrize("species_name", ["CHIKORITA", "CYNDAQUIL", "TOTODILE"])
@pytest.mark.parametrize("destination", ["party", "current-box"])
def test_phase_4_party_and_box_delivery_finalize_once(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    implemented_gifts: dict[str, dict],
    species_name: str,
    destination: str,
) -> None:
    scenario = implemented_gifts[species_name]
    completion = phase_4_constants[scenario["completion_event"]]
    species = phase_4_constants[scenario["species"]]
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path,
        phase_4_constants,
        scenario,
        prerequisite=True,
    ) as session:
        if destination == "current-box":
            set_party_full(
                session,
                phase_4_constants["EEVEE"],
                phase_4_constants["PARTY_LENGTH"],
            )
        expected_outcome = 0 if destination == "party" else 1
        assert (
            interact_with_phase_4_gift(session, scenario, accept=True)
            == expected_outcome
        )
        progress = read_progress(session)
        assert event_is_set(session, completion)
        assert progress.owns(species)
        if destination == "party":
            assert progress.party.species == (species,)
            assert session.read_symbol("wPartyMon1Level") == scenario["level"]
            assert progress.current_box.count == 0
        else:
            assert progress.current_box.species == (species,)
            assert session.read_symbol("sBoxMon1Level") == scenario["level"]


@pytest.mark.parametrize("species_name", ["CHIKORITA", "CYNDAQUIL", "TOTODILE"])
def test_phase_4_full_storage_is_atomic_and_retryable(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    implemented_gifts: dict[str, dict],
    species_name: str,
) -> None:
    scenario = implemented_gifts[species_name]
    completion = phase_4_constants[scenario["completion_event"]]
    species = phase_4_constants[scenario["species"]]
    filler = phase_4_constants["EEVEE"]
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path,
        phase_4_constants,
        scenario,
        prerequisite=True,
    ) as session:
        set_party_full(session, filler, phase_4_constants["PARTY_LENGTH"])
        set_current_box_full(session, filler, phase_4_constants["MONS_PER_BOX"])
        before = read_progress(session)
        assert interact_with_phase_4_gift(session, scenario, accept=True) == 2
        assert not event_is_set(session, completion)
        assert read_progress(session) == before

        clear_current_box(session)
        assert interact_with_phase_4_gift(session, scenario, accept=True) == 1
        assert event_is_set(session, completion)
        assert read_progress(session).current_box.species == (species,)


@pytest.mark.parametrize("species_name", ["CHIKORITA", "CYNDAQUIL", "TOTODILE"])
def test_phase_4_completion_survives_native_save_reload_without_duplicates(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    implemented_gifts: dict[str, dict],
    species_name: str,
) -> None:
    scenario = implemented_gifts[species_name]
    completion = phase_4_constants[scenario["completion_event"]]
    species = phase_4_constants[scenario["species"]]
    persisted = tmp_path / "persisted.sav"
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "initial",
        phase_4_constants,
        scenario,
        prerequisite=True,
    ) as session:
        assert interact_with_phase_4_gift(session, scenario, accept=True) == 0
        save_game_from_overworld(session, scenario["max_frames_per_step"])
        dump_battery_ram(session, persisted)

    with loaded_phase_4_saved_game(
        repo_root,
        tmp_path / "reload",
        phase_4_constants,
        scenario,
        persisted,
    ) as session:
        assert event_is_set(session, completion)
        assert read_progress(session).party.species == (species,)
        for other in implemented_gifts.values():
            if other is not scenario:
                assert not event_is_set(
                    session, phase_4_constants[other["completion_event"]]
                )
        session.enable_script_tracing()
        session.tap("a", 2, 30)
        assert scenario["script"] not in session.script_history
        assert read_progress(session).party.species == (species,)


def test_cyndaquil_is_hidden_before_release_and_after_completion(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    cyndaquil: dict,
) -> None:
    completion = phase_4_constants[cyndaquil["completion_event"]]
    for label, completed in (("before-release", False), ("completed", True)):
        with loaded_phase_4_checkpoint(
            repo_root,
            tmp_path / label,
            phase_4_constants,
            cyndaquil,
            prerequisite=completed,
            completed=completed,
        ) as session:
            session.enable_script_tracing()
            session.tap("a", 2, 30)
            assert cyndaquil["script"] not in session.script_history
            assert event_is_set(session, completion) is completed


def test_cyndaquil_appears_in_release_scene_and_restores_while_pending(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    cyndaquil: dict,
) -> None:
    released = phase_4_constants[cyndaquil["prerequisite_event"]]
    completion = phase_4_constants[cyndaquil["completion_event"]]
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "same-scene",
        phase_4_constants,
        cyndaquil,
        prerequisite=False,
    ) as session:
        place_player(session, 10, 7)
        session.enable_script_tracing()
        walk_steps(session, "up", "wYCoord", -1, 1, cyndaquil["max_frames_per_step"])
        session.wait_for_script("ReleaseTheBeasts", cyndaquil["max_frames_per_step"])
        session.wait_until(
            lambda current: event_is_set(current, released),
            cyndaquil["max_frames_per_step"],
            "legendary beasts to be released",
        )
        wait_for_idle(session, cyndaquil["max_frames_per_step"])
        assert not event_is_set(session, completion)
        assert session.read_symbol("wRoamMon1Species") == phase_4_constants["RAIKOU"]
        assert session.read_symbol("wRoamMon2Species") == phase_4_constants["ENTEI"]
        assert not event_is_set(
            session, phase_4_constants["EVENT_SAW_SUICUNE_AT_CIANWOOD_CITY"]
        )
        walk_steps(session, "up", "wYCoord", -1, 1, cyndaquil["max_frames_per_step"])
        assert interact_with_phase_4_gift(session, cyndaquil, accept=False) is None

    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "reload-pending",
        phase_4_constants,
        cyndaquil,
        prerequisite=True,
    ) as session:
        assert interact_with_phase_4_gift(session, cyndaquil, accept=False) is None
        assert not event_is_set(session, completion)
        assert interact_with_phase_4_gift(session, cyndaquil, accept=False) is None


def test_totodile_clue_and_secretpotion_paths_preserve_story_state(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    totodile: dict,
) -> None:
    completion = phase_4_constants[totodile["completion_event"]]
    jasmine = phase_4_constants["EVENT_JASMINE_RETURNED_TO_GYM"]
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "not-ready",
        phase_4_constants,
        totodile,
        prerequisite=False,
    ) as session:
        before = read_progress(session)
        yes_no_count = session.hook_history.count("_YesNoBox")
        assert interact_with_phase_4_gift(session, totodile, accept=None) is None
        assert session.hook_history.count("_YesNoBox") == yes_no_count
        assert not event_is_set(session, completion)
        assert read_progress(session) == before

    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "with-potion",
        phase_4_constants,
        totodile,
        prerequisite=True,
    ) as session:
        secretpotion = phase_4_constants["SECRETPOTION"]
        session.write_symbol("wNumKeyItems", 1)
        session.write_symbol_bytes("wKeyItems", bytes([secretpotion, 0xFF]))
        before_inventory = read_progress(session).inventory
        jasmine_before = event_is_set(session, jasmine)
        assert interact_with_phase_4_gift(session, totodile, accept=True) == 0
        assert event_is_set(session, completion)
        assert read_progress(session).inventory == before_inventory
        assert event_is_set(session, jasmine) is jasmine_before


def test_all_three_johto_starters_are_obtainable_on_one_save(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    implemented_gifts: dict[str, dict],
) -> None:
    ordered = [
        implemented_gifts[name]
        for name in ("CHIKORITA", "CYNDAQUIL", "TOTODILE")
    ]
    source_save: Path | None = None
    expected_species: list[int] = []
    for index, scenario in enumerate(ordered):
        if source_save is None:
            context = loaded_phase_4_checkpoint(
                repo_root,
                tmp_path / f"step-{index}",
                phase_4_constants,
                scenario,
                prerequisite=True,
            )
        else:
            retargeted = retarget_phase_4_save(
                repo_root,
                source_save,
                tmp_path / f"retargeted-{index}.sav",
                phase_4_constants,
                scenario,
            )
            context = loaded_phase_4_saved_game(
                repo_root,
                tmp_path / f"step-{index}",
                phase_4_constants,
                scenario,
                retargeted,
            )
        with context as session:
            assert interact_with_phase_4_gift(session, scenario, accept=True) == 0
            expected_species.append(phase_4_constants[scenario["species"]])
            assert read_progress(session).party.species == tuple(expected_species)
            for completed in ordered[: index + 1]:
                assert event_is_set(
                    session,
                    phase_4_constants[completed["completion_event"]],
                )
            if index < len(ordered) - 1:
                save_game_from_overworld(session, scenario["max_frames_per_step"])
                source_save = dump_battery_ram(
                    session, tmp_path / f"completed-{index}.sav"
                )
