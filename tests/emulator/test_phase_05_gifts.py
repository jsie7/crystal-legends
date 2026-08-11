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
from tests.support.phase_05_scenario import (
    loaded_phase_5_checkpoint,
    loaded_phase_5_saved_game,
)
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.emulator, pytest.mark.phase5]


@pytest.fixture(scope="module")
def scenarios(repo_root: Path) -> list[dict]:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_05_ruins_gifts.json").read_text()
    )


@pytest.fixture(scope="module")
def phase_5_constants(
    repo_root: Path, tmp_path_factory, scenarios: list[dict]
) -> dict[str, int]:
    names = {
        "SPAWN_N_A",
        "MAPSETUP_WARP",
        "EVENT_GOT_KABUTO_FROM_ALPH",
        "EVENT_GOT_OMANYTE_FROM_ALPH",
        "EVENT_GOT_AERODACTYL_FROM_ALPH",
        "PARTY_LENGTH",
        "MONS_PER_BOX",
        "EEVEE",
    }
    for scenario in scenarios:
        names.update(
            {
                scenario["picture_event"],
                scenario["wall_event"],
                scenario["species"],
                f"GROUP_{scenario['map']}",
                f"MAP_{scenario['map']}",
                f"GROUP_{scenario['chamber']['map']}",
                f"MAP_{scenario['chamber']['map']}",
            }
        )
        names.update(scenario["item_events"])
    constants = resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_5_runtime_constants"),
        sorted(names),
    )
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    for scenario in scenarios:
        for scene in ("check_scene", "noop_scene"):
            label = scenario["chamber"][scene]
            constants[label] = symbols.constant(label)
    return constants


def _assert_current_map(
    session, constants: dict[str, int], map_name: str
) -> None:
    assert session.read_symbol("wMapGroup") == constants[f"GROUP_{map_name}"]
    assert session.read_symbol("wMapNumber") == constants[f"MAP_{map_name}"]


def _enter_hidden_room(session, constants: dict[str, int], scenario: dict) -> None:
    max_frames = scenario["max_frames_per_step"]
    chamber = scenario["chamber"]["map"]
    item_room = scenario["map"]
    session.tap("up", 2, 2)
    session.tick(20)
    if (
        session.read_symbol("wMapGroup") == constants[f"GROUP_{chamber}"]
        and session.read_symbol("wMapNumber") == constants[f"MAP_{chamber}"]
        and session.read_symbol("wYCoord") == scenario["chamber"]["start"]["y"]
    ):
        session.tap("up", 2, 2)
    session.wait_until(
        lambda current: (
            current.read_symbol("wMapGroup") == constants[f"GROUP_{item_room}"]
            and current.read_symbol("wMapNumber") == constants[f"MAP_{item_room}"]
        ),
        max_frames,
        f"warp into {item_room}",
    )


@pytest.mark.parametrize(
    ("picture", "wall", "opens"),
    [(False, False, False), (False, True, False), (True, False, False), (True, True, True)],
)
def test_phase_5_chamber_wall_requires_picture_and_original_condition(
    repo_root: Path,
    tmp_path: Path,
    phase_5_constants: dict[str, int],
    scenarios: list[dict],
    picture: bool,
    wall: bool,
    opens: bool,
) -> None:
    for scenario in scenarios:
        chamber = scenario["chamber"]
        with loaded_phase_5_checkpoint(
            repo_root,
            tmp_path / f"{scenario['species']}-{picture}-{wall}",
            phase_5_constants,
            scenario,
            location="chamber",
            picture=picture,
            wall=wall,
        ) as session:
            _assert_current_map(session, phase_5_constants, chamber["map"])
            assert event_is_set(
                session, phase_5_constants[scenario["picture_event"]]
            ) is picture
            assert event_is_set(
                session, phase_5_constants[scenario["wall_event"]]
            ) is wall
            expected_scene = chamber["noop_scene"] if opens else chamber["check_scene"]
            if opens:
                session.wait_until(
                    lambda current: current.read_symbol(chamber["scene_variable"])
                    == phase_5_constants[expected_scene],
                    scenario["max_frames_per_step"],
                    f"{scenario['species']} wall opening scene",
                )
                wait_for_idle(session, scenario["max_frames_per_step"])
            assert session.read_symbol(chamber["scene_variable"]) == phase_5_constants[
                expected_scene
            ]
            if opens:
                _enter_hidden_room(session, phase_5_constants, scenario)
            else:
                session.tap("up", 2, 30)
                _assert_current_map(session, phase_5_constants, chamber["map"])
                assert session.read_symbol("wYCoord") == chamber["start"]["y"]


def test_opened_chamber_scene_survives_native_save_reload(
    repo_root: Path,
    tmp_path: Path,
    phase_5_constants: dict[str, int],
    scenarios: list[dict],
) -> None:
    scenario = scenarios[0]
    chamber = scenario["chamber"]
    persisted = tmp_path / "opened-kabuto.sav"
    with loaded_phase_5_checkpoint(
        repo_root,
        tmp_path / "initial",
        phase_5_constants,
        scenario,
        location="chamber",
        picture=True,
        wall=True,
    ) as session:
        session.wait_until(
            lambda current: current.read_symbol(chamber["scene_variable"])
            == phase_5_constants[chamber["noop_scene"]],
            scenario["max_frames_per_step"],
            "Kabuto wall opening scene",
        )
        wait_for_idle(session, scenario["max_frames_per_step"])
        assert session.read_symbol(chamber["scene_variable"]) == phase_5_constants[
            chamber["noop_scene"]
        ]
        save_game_from_overworld(session, scenario["max_frames_per_step"])
        dump_battery_ram(session, persisted)

    with loaded_phase_5_saved_game(
        repo_root,
        tmp_path / "reload",
        phase_5_constants,
        scenario,
        persisted,
    ) as session:
        _assert_current_map(session, phase_5_constants, chamber["map"])
        assert session.read_symbol(chamber["scene_variable"]) == phase_5_constants[
            chamber["noop_scene"]
        ]
        _enter_hidden_room(session, phase_5_constants, scenario)


@pytest.mark.parametrize("species_name", ["KABUTO", "OMANYTE"])
def test_gift_visibility_and_decline_are_retryable(
    repo_root: Path,
    tmp_path: Path,
    phase_5_constants: dict[str, int],
    scenarios: list[dict],
    species_name: str,
) -> None:
    scenario = next(row for row in scenarios if row["species"] == species_name)
    completion = phase_5_constants[scenario["completion_event"]]
    for label, picture, wall, completed in (
        ("no-picture", False, True, False),
        ("no-wall", True, False, False),
        ("completed", True, True, True),
    ):
        with loaded_phase_5_checkpoint(
            repo_root,
            tmp_path / f"{species_name}-{label}",
            phase_5_constants,
            scenario,
            location="item_room",
            picture=picture,
            wall=wall,
            completed=completed,
        ) as session:
            session.enable_script_tracing()
            session.tap("a", 2, 30)
            assert scenario["script"] not in session.script_history
            assert event_is_set(session, completion) is completed

    with loaded_phase_5_checkpoint(
        repo_root,
        tmp_path / f"{species_name}-decline",
        phase_5_constants,
        scenario,
        location="item_room",
        picture=True,
        wall=True,
    ) as session:
        assert interact_with_gift(session, scenario, accept=False) is None
        assert not event_is_set(session, completion)
        assert read_progress(session).party.count == 0
        assert interact_with_gift(session, scenario, accept=False) is None
        assert session.script_history.count(scenario["script"]) == 2


@pytest.mark.parametrize("destination", ["party", "current-box"])
@pytest.mark.parametrize("species_name", ["KABUTO", "OMANYTE"])
def test_gift_party_and_box_delivery_finalize_once(
    repo_root: Path,
    tmp_path: Path,
    phase_5_constants: dict[str, int],
    scenarios: list[dict],
    destination: str,
    species_name: str,
) -> None:
    scenario = next(row for row in scenarios if row["species"] == species_name)
    completion = phase_5_constants[scenario["completion_event"]]
    species = phase_5_constants[scenario["species"]]
    with loaded_phase_5_checkpoint(
        repo_root,
        tmp_path / f"{species_name}-{destination}",
        phase_5_constants,
        scenario,
        location="item_room",
        picture=True,
        wall=True,
    ) as session:
        if destination == "current-box":
            set_party_full(
                session,
                phase_5_constants["EEVEE"],
                phase_5_constants["PARTY_LENGTH"],
            )
        expected = 0 if destination == "party" else 1
        assert interact_with_gift(session, scenario, accept=True) == expected
        progress = read_progress(session)
        assert event_is_set(session, completion)
        assert progress.owns(species)
        if destination == "party":
            assert progress.party.species == (species,)
            assert session.read_symbol("wPartyMon1Level") == scenario["level"]
        else:
            assert progress.current_box.species == (species,)
            assert session.read_symbol("sBoxMon1Level") == scenario["level"]
        for event_name in scenario["item_events"]:
            assert not event_is_set(session, phase_5_constants[event_name])
        session.tap("a", 2, 30)
        assert session.script_history.count(scenario["script"]) == 1


@pytest.mark.parametrize("species_name", ["KABUTO", "OMANYTE"])
def test_gift_full_storage_is_atomic_and_retryable(
    repo_root: Path,
    tmp_path: Path,
    phase_5_constants: dict[str, int],
    scenarios: list[dict],
    species_name: str,
) -> None:
    scenario = next(row for row in scenarios if row["species"] == species_name)
    completion = phase_5_constants[scenario["completion_event"]]
    species = phase_5_constants[scenario["species"]]
    filler = phase_5_constants["EEVEE"]
    with loaded_phase_5_checkpoint(
        repo_root,
        tmp_path / species_name,
        phase_5_constants,
        scenario,
        location="item_room",
        picture=True,
        wall=True,
    ) as session:
        set_party_full(session, filler, phase_5_constants["PARTY_LENGTH"])
        set_current_box_full(session, filler, phase_5_constants["MONS_PER_BOX"])
        before = read_progress(session)
        assert interact_with_gift(session, scenario, accept=True) == 2
        assert not event_is_set(session, completion)
        assert read_progress(session) == before

        clear_current_box(session)
        assert interact_with_gift(session, scenario, accept=True) == 1
        assert event_is_set(session, completion)
        assert read_progress(session).current_box.species == (species,)


@pytest.mark.parametrize("species_name", ["KABUTO", "OMANYTE"])
def test_gift_completion_survives_native_save_reload(
    repo_root: Path,
    tmp_path: Path,
    phase_5_constants: dict[str, int],
    scenarios: list[dict],
    species_name: str,
) -> None:
    scenario = next(row for row in scenarios if row["species"] == species_name)
    completion = phase_5_constants[scenario["completion_event"]]
    species = phase_5_constants[scenario["species"]]
    persisted = tmp_path / f"{species_name.lower()}-complete.sav"
    with loaded_phase_5_checkpoint(
        repo_root,
        tmp_path / "initial",
        phase_5_constants,
        scenario,
        location="item_room",
        picture=True,
        wall=True,
    ) as session:
        assert interact_with_gift(session, scenario, accept=True) == 0
        save_game_from_overworld(session, scenario["max_frames_per_step"])
        dump_battery_ram(session, persisted)

    with loaded_phase_5_saved_game(
        repo_root,
        tmp_path / "reload",
        phase_5_constants,
        scenario,
        persisted,
    ) as session:
        assert event_is_set(session, completion)
        assert read_progress(session).party.species == (species,)
        session.enable_script_tracing()
        session.tap("a", 2, 30)
        assert scenario["script"] not in session.script_history
