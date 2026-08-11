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
    }
    for scenario in scenarios:
        names.update(
            {
                scenario["picture_event"],
                scenario["wall_event"],
                f"GROUP_{scenario['map']}",
                f"MAP_{scenario['map']}",
                f"GROUP_{scenario['chamber']['map']}",
                f"MAP_{scenario['chamber']['map']}",
            }
        )
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
