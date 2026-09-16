from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Iterator

from tests.support.bedroom_scenario import start_saved_game
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
    save.write_saved_u8("wBurnedTower1FSceneID", constants["SCENE_BURNEDTOWER1F_NOOP"])
    save.set_event(constants["EVENT_HOLE_IN_BURNED_TOWER"], True)
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
    *,
    fresh_map: bool = False,
) -> Iterator[PyBoySession]:
    """Use native Continue unless explicitly testing a fresh or retargeted map."""
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
            force_fresh_map_load if fresh_map else None,
        )
        yield session
