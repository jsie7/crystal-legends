from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Callable, Iterator

from tests.support.pyboy_session import PyBoySession, prepare_rom


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def wait_for_idle(session: PyBoySession, max_frames: int) -> None:
    session.wait_until(
        lambda current: current.read_symbol("wScriptMode") == 0,
        max_frames,
        "idle overworld script state",
    )


def start_saved_game(
    session: PyBoySession,
    max_frames: int,
    before_overworld: Callable[[PyBoySession], None] | None = None,
) -> None:
    for label in (
        "TitleScreenMain",
        "MainMenu",
        "Continue",
        "ConfirmContinue",
        "FinishContinueFunction",
        "OverworldLoop",
    ):
        session.register_hook(
            label, before_overworld if label == "OverworldLoop" else None
        )
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
    wait_for_idle(session, max_frames)
    session.tick(30)


@contextmanager
def loaded_session(
    repo_root: Path,
    work_dir: Path,
    scenario: dict,
    *,
    reference: bool = False,
) -> Iterator[PyBoySession]:
    fixture = repo_root / "tests/fixtures/saves" / scenario["save_fixture"]
    fixture_hash = sha256_file(fixture)
    subject = scenario["reference_negative"] if reference else scenario
    prepared = prepare_rom(
        work_dir,
        repo_root / subject["rom"],
        repo_root / subject["symbols"],
        save_fixture=fixture,
    )
    try:
        with PyBoySession(prepared) as session:
            start_saved_game(session, scenario["max_frames_per_step"])
            yield session
    finally:
        assert sha256_file(fixture) == fixture_hash, "canonical save fixture was mutated"


def event_is_set(session: PyBoySession, event_number: int) -> bool:
    event_flags = session.symbols["wEventFlags"]
    value = session.pyboy.memory[
        event_flags.bank,
        event_flags.address + event_number // 8,
    ]
    return bool(value & (1 << (event_number % 8)))


def progression_snapshot(session: PyBoySession) -> bytes:
    return session.read_symbol_range("wStatusFlags", "wBoxNames")


def assert_scenario_start(
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


def inspect_tv_once(
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
        lambda current: event_is_set(current, event_number),
        max_frames,
        f"{scenario['sequence_event']} to be set",
    )
    session.wait_for_hook_count("Script_waitbutton", wait_count, max_frames)
    session.tap("a", 10, 10)
    wait_for_idle(session, max_frames)


def _advance_warning_to_confirmation(
    session: PyBoySession,
    scenario: dict,
    event_number: int,
) -> tuple[int, int]:
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
        lambda current: not event_is_set(current, event_number),
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
    return yes_no_count, menu_count


def open_cheat_mode_and_cancel(
    session: PyBoySession,
    scenario: dict,
    event_number: int,
) -> None:
    max_frames = scenario["max_frames_per_step"]
    _advance_warning_to_confirmation(session, scenario, event_number)
    session.tick(20)
    session.tap("b", 10, 10)
    session.wait_for_script("PlayersHouse2FDebugTVScript.Exit", max_frames)
    wait_for_idle(session, max_frames)


def open_cheat_mode(
    session: PyBoySession,
    scenario: dict,
    event_number: int,
) -> None:
    max_frames = scenario["max_frames_per_step"]
    _, confirmation_menu_count = _advance_warning_to_confirmation(
        session, scenario, event_number
    )
    main_menu_count = confirmation_menu_count + 1
    session.tick(20)
    session.tap("a", 10, 10)
    session.wait_for_script("PlayersHouse2FDebugTVScript.MainMenu", max_frames)
    session.wait_for_hook_count("VerticalMenu", main_menu_count, max_frames)


def step_to(
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


def _drain_text_to_idle(
    session: PyBoySession,
    max_frames: int,
    handled_prompts: int,
    handled_waits: int,
) -> None:
    while session.read_symbol("wScriptMode") != 0:
        session.wait_until(
            lambda current: (
                current.read_symbol("wScriptMode") == 0
                or current.hook_history.count("PromptButton") > handled_prompts
                or current.hook_history.count("Script_waitbutton") > handled_waits
            ),
            max_frames,
            "gift text prompt, wait button, or idle script state",
        )
        if session.read_symbol("wScriptMode") == 0:
            break
        if session.hook_history.count("PromptButton") > handled_prompts:
            handled_prompts += 1
        elif session.hook_history.count("Script_waitbutton") > handled_waits:
            handled_waits += 1
        session.tap("a", 10, 10)


def grant_cheat_pokemon(
    session: PyBoySession,
    scenario: dict,
    event_number: int,
    menu_index: int = 1,
) -> int:
    if menu_index not in range(1, 5):
        raise ValueError("CHEAT MODE Pokémon menu index must be 1..4")
    max_frames = scenario["max_frames_per_step"]
    inspect_tv_once(session, scenario, event_number)
    open_cheat_mode(session, scenario, event_number)

    pokemon_menu_count = session.hook_history.count("VerticalMenu") + 1
    session.tap("down", 10, 10)
    session.tap("down", 10, 10)
    session.tap("a", 10, 10)
    session.wait_for_script("PlayersHouse2FDebugTVScript.PokemonMenu", max_frames)
    session.wait_for_hook_count("VerticalMenu", pokemon_menu_count, max_frames)

    nickname_count = session.hook_history.count("GiveANickname_YesNo") + 1
    nickname_menu_count = session.hook_history.count("VerticalMenu") + 1
    handled_prompts = session.hook_history.count("PromptButton")
    handled_waits = session.hook_history.count("Script_waitbutton")
    session.register_hook("GiveANickname_YesNo")
    session.register_hook("PromptButton")
    session.register_hook("Script_waitbutton")
    for _ in range(menu_index - 1):
        session.tap("down", 10, 10)
    session.tap("a", 10, 10)
    session.wait_until(
        lambda current: (
            current.hook_history.count("GiveANickname_YesNo") >= nickname_count
            or "PlayersHouse2FDebugTVScript.PokemonStorageFull"
            in current.script_history
        ),
        max_frames,
        "gift nickname prompt or storage-full branch",
    )
    if session.hook_history.count("GiveANickname_YesNo") >= nickname_count:
        while session.hook_history.count("VerticalMenu") < nickname_menu_count:
            session.wait_until(
                lambda current: (
                    current.hook_history.count("VerticalMenu")
                    >= nickname_menu_count
                    or current.hook_history.count("PromptButton")
                    > handled_prompts
                ),
                max_frames,
                "nickname text prompt or nickname yes/no menu",
            )
            if session.hook_history.count("VerticalMenu") >= nickname_menu_count:
                break
            handled_prompts += 1
            session.tap("a", 10, 10)
        session.wait_for_hook_count("VerticalMenu", nickname_menu_count, max_frames)
        session.tick(20)
        session.tap("b", 10, 10)
    _drain_text_to_idle(session, max_frames, handled_prompts, handled_waits)
    return session.read_symbol("wScriptVar")
