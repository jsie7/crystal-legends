from __future__ import annotations

from tests.support.bedroom_scenario import wait_for_idle
from tests.support.game_state import read_progress
from tests.support.legendary_scenario import advance_with_a_until, place_player
from tests.support.pyboy_session import PyBoySession


def cross_map_warp(
    session: PyBoySession,
    constants: dict[str, int],
    approach: tuple[int, int],
    direction: str,
    destination: str,
    max_frames: int,
) -> None:
    # Skip walking across the room, but enter the actual production warp by input.
    place_player(session, *approach)
    session.write_symbol("wPlayerDirection", constants[f"OW_{direction.upper()}"])
    session.tap(direction, 2, 20)
    session.wait_until(
        lambda current: (
            current.read_symbol("wMapGroup") == constants[f"GROUP_{destination}"]
            and current.read_symbol("wMapNumber") == constants[f"MAP_{destination}"]
        ),
        max_frames,
        f"production warp into {destination}",
    )
    session.tick(120)  # Finish the fade and automatic doorway step.
    wait_for_idle(session, max_frames)


def _gift_map_object(session: PyBoySession, constants: dict[str, int], gift: dict) -> int:
    pointer = session.symbols[gift["script"]].address
    matches = [
        index for index in range(1, constants["NUM_OBJECTS"])
        if int.from_bytes(
            session.read_symbol_bytes(f"wMap{index}ObjectScript", 2), "little"
        ) == pointer
    ]
    assert len(matches) == 1
    return matches[0]


def assert_gift_absent(
    session: PyBoySession, constants: dict[str, int], scenario: dict
) -> None:
    gift = scenario.get("gift", scenario)
    assert (session.read_symbol("wXCoord"), session.read_symbol("wYCoord")) == (
        gift["start"]["x"], gift["start"]["y"]
    )
    map_object = _gift_map_object(session, constants, gift)
    assert session.read_symbol(f"wMap{map_object}ObjectStructID") == 0xFF
    before = read_progress(session)
    session.enable_script_tracing()
    calls = session.script_history.count(gift["script"])
    session.write_symbol(
        "wPlayerDirection", constants[f"OW_{gift['start']['facing']}"]
    )
    session.tap("a", 2, 30)
    assert session.script_history.count(gift["script"]) == calls
    assert read_progress(session) == before


def assert_completed_gift_is_inert(
    session: PyBoySession, constants: dict[str, int], scenario: dict
) -> None:
    gift = scenario.get("gift", scenario)
    map_object = _gift_map_object(session, constants, gift)
    assert session.read_symbol(f"wMap{map_object}ObjectStructID") != 0xFF
    # Simulate a stale visible object so the script guard is tested independently.
    event = constants[scenario["completion_event"]]
    flags = session.symbols["wEventFlags"]
    address = flags.address + event // 8
    session.pyboy.memory[flags.bank, address] |= 1 << (event % 8)
    before = read_progress(session)
    session.enable_script_tracing()
    session.register_hook("GivePoke")
    grants = session.hook_history.count("GivePoke")
    session.write_symbol(
        "wPlayerDirection", constants[f"OW_{gift['start']['facing']}"]
    )
    session.tap("a", 2, 60)
    assert gift["script"] in session.script_history
    assert session.read_symbol("wScriptMode") == 0
    assert session.hook_history.count("GivePoke") == grants
    assert read_progress(session) == before


def _finish_text(session: PyBoySession, max_frames: int) -> None:
    start = session.frames
    while session.read_symbol("wScriptMode") != 0 and session.frames - start < max_frames:
        session.tap("a", 2, 20)
    wait_for_idle(session, 1)


def interact_with_gift(
    session: PyBoySession,
    scenario: dict,
    *,
    accept: bool | None,
) -> int | None:
    max_frames = scenario["max_frames_per_step"]
    gift = scenario.get("gift", scenario)
    party_count = session.read_symbol("wPartyCount")
    box_count = session.read_symbol("sBoxCount")
    yes_no_count = session.hook_history.count("_YesNoBox") + 1
    menu_count = session.hook_history.count("VerticalMenu") + 1
    nickname_count = session.hook_history.count("GiveANickname_YesNo") + 1
    nickname_menu_count = menu_count + 1
    storage_label = gift.get("storage_label", f"{gift['script']}.StorageFull")
    storage_count = session.script_history.count(storage_label) + 1
    for label in (
        "_YesNoBox",
        "VerticalMenu",
        "GiveANickname_YesNo",
        "PromptButton",
        "Script_waitbutton",
    ):
        session.register_hook(label)
    session.enable_script_tracing()
    session.tap(gift["start"]["facing"].lower(), 2, 10)
    session.tap("a", 2, 10)
    session.wait_for_script(gift["script"], max_frames)

    if accept is None:
        _finish_text(session, max_frames)
        return None

    advance_with_a_until(
        session,
        lambda current: (
            current.hook_history.count("_YesNoBox") >= yes_no_count
            and current.hook_history.count("VerticalMenu") >= menu_count
        ),
        max_frames,
        f"{scenario['species']} gift confirmation",
    )
    session.tick(20)
    session.tap("a" if accept else "b", 2, 10)
    if not accept:
        _finish_text(session, max_frames)
        return None

    advance_with_a_until(
        session,
        lambda current: (
            current.hook_history.count("GiveANickname_YesNo") >= nickname_count
            or current.script_history.count(storage_label) >= storage_count
        ),
        max_frames,
        f"{scenario['species']} nickname prompt or storage-full branch",
    )
    if session.script_history.count(storage_label) >= storage_count:
        _finish_text(session, max_frames)
        return 2

    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("VerticalMenu")
        >= nickname_menu_count,
        max_frames,
        f"{scenario['species']} nickname menu",
    )
    session.tick(20)
    session.tap("b", 2, 10)
    _finish_text(session, max_frames)
    if session.read_symbol("wPartyCount") == party_count + 1:
        return 0
    if session.read_symbol("sBoxCount") == box_count + 1:
        return 1
    raise AssertionError(f"{scenario['species']} gift reported success without delivery")


def set_party_full(session: PyBoySession, species: int, party_length: int) -> None:
    session.write_symbol("wPartyCount", party_length)
    session.write_symbol_bytes(
        "wPartySpecies", bytes([species] * party_length + [0xFF])
    )


def set_current_box_full(session: PyBoySession, species: int, box_length: int) -> None:
    session.write_symbol("sBoxCount", box_length)
    session.write_symbol_bytes("sBoxSpecies", bytes([species] * box_length + [0xFF]))


def clear_current_box(session: PyBoySession) -> None:
    session.write_symbol("sBoxCount", 0)
    session.write_symbol("sBoxSpecies", 0xFF)
