from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Callable, Iterator

from tests.support.bedroom_scenario import start_saved_game
from tests.support.pyboy_session import PyBoySession, prepare_rom
from tests.support.save_fixture import BatterySave
from tests.support.symbol_table import SymbolTable


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def build_phase_7_checkpoint(
    repo_root: Path,
    destination: Path,
    constants: dict[str, int],
    scenario: dict,
    *,
    start: str,
    resolved: bool,
    transformed: bool = False,
    caught: bool = False,
) -> Path:
    fixture = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    save = BatterySave.load(fixture, symbols)
    boss_checkpoint = start == "boss"
    target = scenario["radio_tower_5f"] if boss_checkpoint else scenario["annex"]
    coordinate = target["boss_start" if boss_checkpoint else f"{start}_start"]
    events = scenario["events"]

    save.write_saved_u8("wWarpNumber", 0)
    save.write_saved_u8("wMapGroup", constants[f"GROUP_{target['map']}"])
    save.write_saved_u8("wMapNumber", constants[f"MAP_{target['map']}"])
    save.write_saved_u8("wXCoord", coordinate["x"])
    save.write_saved_u8("wYCoord", coordinate["y"])
    save.write_saved_u8(
        "wPlayerDirection", constants[f"OW_{coordinate['facing']}"]
    )
    save.write_saved_u8(
        "wRadioTower5FSceneID",
        constants[
            "SCENE_RADIOTOWER5F_ROCKET_BOSS"
            if boss_checkpoint
            else "SCENE_RADIOTOWER5F_PROJECT_MEW"
        ],
    )
    save.set_event(constants[events["boss"]], not boss_checkpoint)
    save.set_event(constants[events["data_sent"]], not boss_checkpoint)
    save.set_event(constants[events["resolved"]], resolved)
    save.set_event(constants[events["transformed"]], transformed)
    save.set_event(constants[events["caught"]], caught)
    for event in (
        "EVENT_CLEARED_RADIO_TOWER",
        "EVENT_GOT_CLEAR_BELL",
        "EVENT_TEAM_ROCKET_DISBANDED",
    ):
        save.set_event(constants[event], False)
    if boss_checkpoint:
        save.set_event(constants["EVENT_RADIO_TOWER_ROCKET_TAKEOVER"], False)
    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


@contextmanager
def loaded_phase_7_checkpoint(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    scenario: dict,
    *,
    start: str,
    resolved: bool,
    transformed: bool = False,
    caught: bool = False,
    before_overworld: Callable[[PyBoySession], None] | None = None,
) -> Iterator[PyBoySession]:
    canonical = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    canonical_hash = _sha256(canonical)
    fixture = build_phase_7_checkpoint(
        repo_root,
        work_dir / "phase-07-project-mew.sav",
        constants,
        scenario,
        start=start,
        resolved=resolved,
        transformed=transformed,
        caught=caught,
    )
    prepared = prepare_rom(
        work_dir / "rom",
        repo_root / scenario["rom"],
        repo_root / scenario["symbols"],
        save_fixture=fixture,
    )
    try:
        with PyBoySession(prepared) as session:

            def prepare(current: PyBoySession) -> None:
                current.write_symbol(
                    "wDefaultSpawnpoint", constants["SPAWN_N_A"] & 0xFF
                )
                current.write_symbol("hMapEntryMethod", constants["MAPSETUP_WARP"])
                if before_overworld is not None:
                    before_overworld(current)

            start_saved_game(
                session,
                scenario["max_frames_per_step"],
                prepare,
            )
            yield session
    finally:
        assert _sha256(canonical) == canonical_hash


@contextmanager
def loaded_phase_7_saved_game(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    scenario: dict,
    save_fixture: Path,
) -> Iterator[PyBoySession]:
    prepared = prepare_rom(
        work_dir,
        repo_root / scenario["rom"],
        repo_root / scenario["symbols"],
        save_fixture=save_fixture,
    )
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
