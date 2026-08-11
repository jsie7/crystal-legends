from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterator

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.pyboy_session import PyBoySession, prepare_rom


pytestmark = pytest.mark.emulator


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return _load_json(
        repo_root / "tests/fixtures/scenarios/phase_03_cheat_mode.json"
    )


@pytest.fixture(scope="module")
def fixture_metadata(repo_root: Path) -> dict:
    return _load_json(
        repo_root / "tests/fixtures/saves/bedroom_initialized.json"
    )


@pytest.fixture(scope="module")
def runtime_constants(repo_root: Path, tmp_path_factory) -> dict[str, int]:
    return resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("bedroom_constants"),
        [
            "GROUP_PLAYERS_HOUSE_1F",
            "MAP_PLAYERS_HOUSE_1F",
            "GROUP_PLAYERS_HOUSE_2F",
            "MAP_PLAYERS_HOUSE_2F",
            "EVENT_TEMPORARY_UNTIL_MAP_RELOAD_2",
            "OW_UP",
        ],
    )


def _start_saved_game(session: PyBoySession, max_frames: int) -> None:
    for label in (
        "TitleScreenMain",
        "MainMenu",
        "Continue",
        "ConfirmContinue",
        "FinishContinueFunction",
        "OverworldLoop",
    ):
        session.register_hook(label)
    session.wait_for_hook("TitleScreenMain", max_frames)
    session.tap("start", 10, 10)
    session.wait_for_hook("MainMenu", max_frames)
    session.tick(120)
    session.tap("a", 10, 10)
    session.wait_for_hook("Continue", max_frames)
    session.wait_for_hook("ConfirmContinue", max_frames)
    session.tick(30)
    session.tap("a", 10, 10)
    session.wait_for_hook("FinishContinueFunction", max_frames)
    session.wait_for_hook("OverworldLoop", max_frames)
    _wait_for_idle(session, max_frames)
    session.tick(30)


@contextmanager
def _loaded_session(
    repo_root: Path,
    work_dir: Path,
    scenario: dict,
    *,
    reference: bool = False,
) -> Iterator[PyBoySession]:
    fixture = repo_root / "tests/fixtures/saves" / scenario["save_fixture"]
    fixture_hash = _sha256(fixture)
    subject = scenario["reference_negative"] if reference else scenario
    prepared = prepare_rom(
        work_dir,
        repo_root / subject["rom"],
        repo_root / subject["symbols"],
        save_fixture=fixture,
    )
    try:
        with PyBoySession(prepared) as session:
            _start_saved_game(session, scenario["max_frames_per_step"])
            yield session
    finally:
        assert _sha256(fixture) == fixture_hash, "canonical save fixture was mutated"


def _event_is_set(session: PyBoySession, event_number: int) -> bool:
    event_flags = session.symbols["wEventFlags"]
    value = session.pyboy.memory[
        event_flags.bank,
        event_flags.address + event_number // 8,
    ]
    return bool(value & (1 << (event_number % 8)))


def _wait_for_idle(session: PyBoySession, max_frames: int) -> None:
    session.wait_until(
        lambda current: current.read_symbol("wScriptMode") == 0,
        max_frames,
        "idle overworld script state",
    )


def _progression_snapshot(session: PyBoySession) -> bytes:
    # This stable range covers badges, inventory, scene IDs, story event flags,
    # and the current box while excluding clocks and live map object state.
    return session.read_symbol_range("wStatusFlags", "wBoxNames")


def _assert_scenario_start(
    session: PyBoySession, scenario: dict, constants: dict[str, int]
) -> None:
    start = scenario["start"]
    map_name = start["map"]
    assert session.read_symbol("wMapGroup") == constants[f"GROUP_{map_name}"]
    assert session.read_symbol("wMapNumber") == constants[f"MAP_{map_name}"]
    assert session.read_symbol("wXCoord") == start["x"]
    assert session.read_symbol("wYCoord") == start["y"]
    assert session.read_symbol("wPlayerDirection") == constants[
        f"OW_{start['facing']}"
    ]


def _inspect_tv_once(
    session: PyBoySession,
    scenario: dict,
    event_number: int,
) -> None:
    max_frames = scenario["max_frames_per_step"]
    script = scenario["expected_scripts"]["first_inspection"]
    session.enable_script_tracing()
    wait_count = session.hook_history.count("Script_waitbutton") + 1
    session.register_hook("Script_waitbutton")
    session.tap("a")
    session.wait_for_script(script, max_frames)
    session.wait_until(
        lambda current: _event_is_set(current, event_number),
        max_frames,
        f"{scenario['sequence_event']} to be set",
    )
    session.wait_for_hook_count("Script_waitbutton", wait_count, max_frames)
    session.tap("a", 10, 10)
    _wait_for_idle(session, max_frames)


def _open_cheat_mode_and_cancel(
    session: PyBoySession,
    scenario: dict,
    event_number: int,
) -> None:
    max_frames = scenario["max_frames_per_step"]
    script = scenario["expected_scripts"]["second_inspection"]
    yes_no_count = session.hook_history.count("_YesNoBox") + 1
    menu_count = session.hook_history.count("VerticalMenu") + 1
    handled_prompts = session.hook_history.count("PromptButton")
    session.register_hook("_YesNoBox")
    session.register_hook("VerticalMenu")
    session.register_hook("PromptButton")
    session.enable_script_tracing()
    session.tap("a")
    session.wait_for_script(script, max_frames)
    session.wait_until(
        lambda current: not _event_is_set(current, event_number),
        max_frames,
        f"{scenario['sequence_event']} to clear on CHEAT MODE entry",
    )
    while session.hook_history.count("_YesNoBox") < yes_no_count:
        session.wait_until(
            lambda current: (
                current.hook_history.count("_YesNoBox") >= yes_no_count
                or current.hook_history.count("PromptButton") > handled_prompts
            ),
            max_frames,
            "warning text prompt or CHEAT MODE confirmation",
        )
        if session.hook_history.count("_YesNoBox") >= yes_no_count:
            break
        handled_prompts += 1
        session.tap("a", 10, 10)
    session.wait_for_hook_count("_YesNoBox", yes_no_count, max_frames)
    session.wait_for_hook_count("VerticalMenu", menu_count, max_frames)
    session.tick(20)
    session.tap("b", 10, 10)
    session.wait_for_script("PlayersHouse2FDebugTVScript.Exit", max_frames)
    _wait_for_idle(session, max_frames)


def _step_to(
    session: PyBoySession,
    button: str,
    coordinate_label: str,
    expected: int,
    max_frames: int,
) -> None:
    session.tap(button, 10, 10)
    session.wait_until(
        lambda current: current.read_symbol(coordinate_label) == expected,
        max_frames,
        f"{coordinate_label} to become {expected}",
    )
    session.tick(20)


@pytest.mark.smoke
def test_approved_battery_fixture_loads_immutably_into_bedroom(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    fixture_metadata: dict,
    runtime_constants: dict[str, int],
) -> None:
    fixture = repo_root / "tests/fixtures/saves" / scenario["save_fixture"]
    assert _sha256(fixture) == fixture_metadata["save_sha256"]
    source_rom_sha256 = fixture_metadata["source_rom_sha256"]
    assert len(source_rom_sha256) == 64
    int(source_rom_sha256, 16)
    with _loaded_session(repo_root, tmp_path, scenario) as session:
        _assert_scenario_start(session, scenario, runtime_constants)
        expected = fixture_metadata["expected"]
        assert session.read_symbol("wJohtoBadges") == expected["johto_badges"]
        assert session.read_symbol("wKantoBadges") == expected["kanto_badges"]
        assert session.read_symbol("wPartyCount") == expected["party_count"]
        assert session.read_symbol("wCurBox") == expected["current_box"]
        assert session.read_symbol("wNumItems") == expected["bag_item_count"]
        assert session.read_symbol("wNumKeyItems") == expected["key_item_count"]
        assert session.read_symbol("wNumBalls") == expected["ball_count"]
        assert int.from_bytes(session.read_symbol_bytes("wMoney", 3), "big") == expected[
            "money"
        ]
        assert not _event_is_set(
            session, runtime_constants[scenario["sequence_event"]]
        )


def test_two_tv_inspections_enter_cheat_mode_and_cancel_cleanly(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    runtime_constants: dict[str, int],
) -> None:
    event_number = runtime_constants[scenario["sequence_event"]]
    with _loaded_session(repo_root, tmp_path, scenario) as session:
        _assert_scenario_start(session, scenario, runtime_constants)
        before = _progression_snapshot(session)
        _inspect_tv_once(session, scenario, event_number)
        _open_cheat_mode_and_cancel(session, scenario, event_number)
        assert _progression_snapshot(session) == before


def test_other_bedroom_interaction_resets_tv_sequence(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    runtime_constants: dict[str, int],
) -> None:
    max_frames = scenario["max_frames_per_step"]
    event_number = runtime_constants[scenario["sequence_event"]]
    with _loaded_session(repo_root, tmp_path, scenario) as session:
        before = _progression_snapshot(session)
        _inspect_tv_once(session, scenario, event_number)
        _step_to(session, "right", "wXCoord", 5, max_frames)
        session.tap("up", 4, 10)
        wait_count = session.hook_history.count("Script_waitbutton") + 1
        prompt_count = session.hook_history.count("PromptButton") + 1
        session.register_hook("Script_waitbutton")
        session.register_hook("PromptButton")
        session.enable_script_tracing()
        session.tap("a")
        session.wait_for_script(
            scenario["expected_scripts"]["other_interaction"], max_frames
        )
        session.wait_until(
            lambda current: not _event_is_set(current, event_number),
            max_frames,
            f"{scenario['sequence_event']} to clear after another interaction",
        )
        session.wait_for_hook_count("PromptButton", prompt_count, max_frames)
        session.tap("a", 10, 10)
        session.wait_for_hook_count("Script_waitbutton", wait_count, max_frames)
        session.tap("a", 10, 10)
        _wait_for_idle(session, max_frames)
        assert _progression_snapshot(session) == before


def test_map_reload_resets_tv_sequence(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    runtime_constants: dict[str, int],
) -> None:
    max_frames = scenario["max_frames_per_step"]
    event_number = runtime_constants[scenario["sequence_event"]]
    with _loaded_session(repo_root, tmp_path, scenario) as session:
        _inspect_tv_once(session, scenario, event_number)
        for x in (5, 6, 7):
            _step_to(session, "right", "wXCoord", x, max_frames)
        _step_to(session, "up", "wYCoord", 1, max_frames)
        session.tap("up", 10, 10)
        session.wait_until(
            lambda current: (
                current.read_symbol("wMapGroup")
                == runtime_constants["GROUP_PLAYERS_HOUSE_1F"]
                and current.read_symbol("wMapNumber")
                == runtime_constants["MAP_PLAYERS_HOUSE_1F"]
            ),
            max_frames,
            "normal staircase reload into PLAYERS_HOUSE_1F",
        )
        _wait_for_idle(session, max_frames)
        assert not _event_is_set(session, event_number)


def test_reference_rom_tv_cannot_enter_crystal_legends_cheat_mode(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    runtime_constants: dict[str, int],
) -> None:
    max_frames = scenario["max_frames_per_step"]
    event_number = runtime_constants[scenario["sequence_event"]]
    reference = scenario["reference_negative"]
    with _loaded_session(
        repo_root, tmp_path, scenario, reference=True
    ) as session:
        for forbidden in reference["forbidden_symbols"]:
            assert forbidden not in session.symbols
        session.enable_script_tracing()
        session.register_hook("Script_waitbutton")
        expected_script = reference["expected_script"]
        for inspection in (1, 2):
            wait_count = session.hook_history.count("Script_waitbutton") + 1
            session.tap("a")
            session.wait_until(
                lambda current, count=inspection: current.script_history.count(
                    expected_script
                )
                >= count,
                max_frames,
                f"stock TV script inspection {inspection}",
            )
            session.wait_for_hook_count("Script_waitbutton", wait_count, max_frames)
            assert not _event_is_set(session, event_number)
            session.tap("a", 10, 10)
            _wait_for_idle(session, max_frames)
