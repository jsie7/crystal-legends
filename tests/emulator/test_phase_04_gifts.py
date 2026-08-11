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
from tests.support.game_state import read_progress
from tests.support.phase_04_scenario import (
    clear_current_box,
    interact_with_phase_4_gift,
    loaded_phase_4_checkpoint,
    loaded_phase_4_saved_game,
    set_current_box_full,
    set_party_full,
)


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
    return resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_4_runtime_constants"),
        sorted(names),
    )


@pytest.fixture(scope="module")
def chikorita(scenarios: list[dict]) -> dict:
    return next(row for row in scenarios if row["species"] == "CHIKORITA")


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


@pytest.mark.parametrize("destination", ["party", "current-box"])
def test_chikorita_party_and_box_delivery_finalize_once(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    chikorita: dict,
    destination: str,
) -> None:
    completion = phase_4_constants[chikorita["completion_event"]]
    species = phase_4_constants[chikorita["species"]]
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path,
        phase_4_constants,
        chikorita,
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
            interact_with_phase_4_gift(session, chikorita, accept=True)
            == expected_outcome
        )
        progress = read_progress(session)
        assert event_is_set(session, completion)
        assert progress.owns(species)
        if destination == "party":
            assert progress.party.species == (species,)
            assert session.read_symbol("wPartyMon1Level") == chikorita["level"]
            assert progress.current_box.count == 0
        else:
            assert progress.current_box.species == (species,)
            assert session.read_symbol("sBoxMon1Level") == chikorita["level"]


def test_chikorita_full_storage_is_atomic_and_retryable(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    chikorita: dict,
) -> None:
    completion = phase_4_constants[chikorita["completion_event"]]
    species = phase_4_constants[chikorita["species"]]
    filler = phase_4_constants["EEVEE"]
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path,
        phase_4_constants,
        chikorita,
        prerequisite=True,
    ) as session:
        set_party_full(session, filler, phase_4_constants["PARTY_LENGTH"])
        set_current_box_full(session, filler, phase_4_constants["MONS_PER_BOX"])
        before = read_progress(session)
        assert interact_with_phase_4_gift(session, chikorita, accept=True) == 2
        assert not event_is_set(session, completion)
        assert read_progress(session) == before

        clear_current_box(session)
        assert interact_with_phase_4_gift(session, chikorita, accept=True) == 1
        assert event_is_set(session, completion)
        assert read_progress(session).current_box.species == (species,)


def test_chikorita_completion_survives_native_save_reload_without_duplicates(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    chikorita: dict,
) -> None:
    completion = phase_4_constants[chikorita["completion_event"]]
    species = phase_4_constants[chikorita["species"]]
    persisted = tmp_path / "persisted.sav"
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "initial",
        phase_4_constants,
        chikorita,
        prerequisite=True,
    ) as session:
        assert interact_with_phase_4_gift(session, chikorita, accept=True) == 0
        save_game_from_overworld(session, chikorita["max_frames_per_step"])
        dump_battery_ram(session, persisted)

    with loaded_phase_4_saved_game(
        repo_root,
        tmp_path / "reload",
        phase_4_constants,
        chikorita,
        persisted,
    ) as session:
        assert event_is_set(session, completion)
        assert read_progress(session).party.species == (species,)
        for other in (
            "EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER",
            "EVENT_GOT_TOTODILE_FROM_CIANWOOD",
        ):
            assert not event_is_set(session, phase_4_constants[other])
        session.enable_script_tracing()
        session.tap("a", 2, 30)
        assert chikorita["script"] not in session.script_history
        assert read_progress(session).party.species == (species,)
