from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Iterator

from tests.support.bedroom_scenario import start_saved_game, wait_for_idle
from tests.support.legendary_scenario import advance_with_a_until
from tests.support.pyboy_session import PyBoySession, prepare_rom
from tests.support.save_fixture import BatterySave
from tests.support.symbol_table import SymbolTable


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def build_phase_4_checkpoint(
    repo_root: Path,
    destination: Path,
    constants: dict[str, int],
    scenario: dict,
    *,
    prerequisite: bool,
    completed: bool = False,
) -> Path:
    fixture = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    save = BatterySave.load(fixture, symbols)
    save.write_saved_u8("wWarpNumber", 0)
    save.write_saved_u8("wMapGroup", constants[f"GROUP_{scenario['map']}"])
    save.write_saved_u8("wMapNumber", constants[f"MAP_{scenario['map']}"])
    save.write_saved_u8("wXCoord", scenario["start"]["x"])
    save.write_saved_u8("wYCoord", scenario["start"]["y"])
    for event in (
        "EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST",
        "EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER",
        "EVENT_GOT_TOTODILE_FROM_CIANWOOD",
    ):
        save.set_event(constants[event], event == scenario["completion_event"] and completed)
    save.set_event(constants[scenario["prerequisite_event"]], prerequisite)
    _configure_map_state(save, constants, scenario, prerequisite)

    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


def _configure_map_state(
    save: BatterySave,
    constants: dict[str, int],
    scenario: dict,
    prerequisite: bool,
) -> None:
    if scenario["map"] != "BURNED_TOWER_B1F":
        return
    save.write_saved_u8(
        "wBurnedTowerB1FSceneID",
        constants[
            "SCENE_BURNEDTOWERB1F_NOOP"
            if prerequisite
            else "SCENE_BURNEDTOWERB1F_RELEASE_THE_BEASTS"
        ],
    )
    save.set_event(constants["EVENT_BURNED_TOWER_B1F_BEASTS_1"], True)
    save.set_event(constants["EVENT_BURNED_TOWER_B1F_BEASTS_2"], prerequisite)


def retarget_phase_4_save(
    repo_root: Path,
    source: Path,
    destination: Path,
    constants: dict[str, int],
    scenario: dict,
) -> Path:
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    save = BatterySave.load(source, symbols)
    save.write_saved_u8("wWarpNumber", 0)
    save.write_saved_u8("wMapGroup", constants[f"GROUP_{scenario['map']}"])
    save.write_saved_u8("wMapNumber", constants[f"MAP_{scenario['map']}"])
    save.write_saved_u8("wXCoord", scenario["start"]["x"])
    save.write_saved_u8("wYCoord", scenario["start"]["y"])
    save.set_event(constants[scenario["prerequisite_event"]], True)
    save.set_event(constants[scenario["completion_event"]], False)
    _configure_map_state(save, constants, scenario, True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


@contextmanager
def loaded_phase_4_checkpoint(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    scenario: dict,
    *,
    prerequisite: bool,
    completed: bool = False,
) -> Iterator[PyBoySession]:
    canonical = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    canonical_hash = _sha256(canonical)
    fixture = build_phase_4_checkpoint(
        repo_root,
        work_dir / f"{scenario['scenario_id']}.sav",
        constants,
        scenario,
        prerequisite=prerequisite,
        completed=completed,
    )
    prepared = prepare_rom(
        work_dir / "rom",
        repo_root / "crystallegends.gbc",
        repo_root / "crystallegends.sym",
        save_fixture=fixture,
    )
    try:
        with PyBoySession(prepared) as session:

            def force_fresh_map_load(current: PyBoySession) -> None:
                current.write_symbol(
                    "wDefaultSpawnpoint", constants["SPAWN_N_A"] & 0xFF
                )
                current.write_symbol("hMapEntryMethod", constants["MAPSETUP_WARP"])

            start_saved_game(
                session,
                scenario["max_frames_per_step"],
                force_fresh_map_load,
            )
            yield session
    finally:
        assert _sha256(canonical) == canonical_hash


@contextmanager
def loaded_phase_4_saved_game(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    scenario: dict,
    save_fixture: Path,
) -> Iterator[PyBoySession]:
    prepared = prepare_rom(
        work_dir,
        repo_root / "crystallegends.gbc",
        repo_root / "crystallegends.sym",
        save_fixture=save_fixture,
    )
    with PyBoySession(prepared) as session:
        def force_fresh_map_load(current: PyBoySession) -> None:
            current.write_symbol("wDefaultSpawnpoint", constants["SPAWN_N_A"] & 0xFF)
            current.write_symbol("hMapEntryMethod", constants["MAPSETUP_WARP"])

        start_saved_game(
            session,
            scenario["max_frames_per_step"],
            force_fresh_map_load,
        )
        yield session


def _finish_text(session: PyBoySession, max_frames: int) -> None:
    start = session.frames
    while session.read_symbol("wScriptMode") != 0 and session.frames - start < max_frames:
        session.tap("a", 2, 20)
    wait_for_idle(session, 1)


def interact_with_phase_4_gift(
    session: PyBoySession,
    scenario: dict,
    *,
    accept: bool | None,
) -> int | None:
    max_frames = scenario["max_frames_per_step"]
    party_count = session.read_symbol("wPartyCount")
    box_count = session.read_symbol("sBoxCount")
    yes_no_count = session.hook_history.count("_YesNoBox") + 1
    menu_count = session.hook_history.count("VerticalMenu") + 1
    nickname_count = session.hook_history.count("GiveANickname_YesNo") + 1
    nickname_menu_count = menu_count + 1
    storage_label = f"{scenario['script']}.StorageFull"
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
    session.tap(scenario["start"]["facing"].lower(), 2, 10)
    session.tap("a", 2, 10)
    session.wait_for_script(scenario["script"], max_frames)

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
