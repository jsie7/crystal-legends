from __future__ import annotations

from tests.support.bedroom_scenario import wait_for_idle
from tests.support.legendary_scenario import advance_with_a_until
from tests.support.pyboy_session import PyBoySession


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
