from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Iterator

from tests.support.bedroom_scenario import start_saved_game
from tests.support.pyboy_session import PyBoySession, prepare_rom
from tests.support.save_fixture import BatterySave
from tests.support.symbol_table import SymbolTable


_GIFT_EVENTS = (
    "EVENT_GOT_KABUTO_FROM_ALPH",
    "EVENT_GOT_OMANYTE_FROM_ALPH",
    "EVENT_GOT_AERODACTYL_FROM_ALPH",
)


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def build_phase_5_checkpoint(
    repo_root: Path,
    destination: Path,
    constants: dict[str, int],
    scenario: dict,
    *,
    location: str,
    picture: bool,
    wall: bool,
    completed: bool = False,
) -> Path:
    fixture = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    save = BatterySave.load(fixture, symbols)
    if location == "chamber":
        target = scenario["chamber"]
        save.write_saved_u8(
            target["scene_variable"], constants[target["check_scene"]]
        )
    elif location == "item_room":
        target = {"map": scenario["map"], "start": scenario["start"]}
    else:
        raise ValueError(f"unknown Phase 5 location {location}")

    save.write_saved_u8("wWarpNumber", 0)
    save.write_saved_u8("wMapGroup", constants[f"GROUP_{target['map']}"])
    save.write_saved_u8("wMapNumber", constants[f"MAP_{target['map']}"])
    save.write_saved_u8("wXCoord", target["start"]["x"])
    save.write_saved_u8("wYCoord", target["start"]["y"])
    for event in _GIFT_EVENTS:
        save.set_event(
            constants[event], event == scenario["completion_event"] and completed
        )
    save.set_event(constants[scenario["picture_event"]], picture)
    save.set_event(constants[scenario["wall_event"]], wall)
    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


@contextmanager
def loaded_phase_5_checkpoint(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    scenario: dict,
    *,
    location: str,
    picture: bool,
    wall: bool,
    completed: bool = False,
) -> Iterator[PyBoySession]:
    canonical = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    canonical_hash = _sha256(canonical)
    fixture = build_phase_5_checkpoint(
        repo_root,
        work_dir / f"{scenario['scenario_id']}.sav",
        constants,
        scenario,
        location=location,
        picture=picture,
        wall=wall,
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
def loaded_phase_5_saved_game(
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
