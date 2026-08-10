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


def _write_key_items(save: BatterySave, items: list[int]) -> None:
    if len(items) > 25:
        raise ValueError("key-item pocket supports at most 25 entries")
    save.write_saved_u8("wNumKeyItems", len(items))
    save.write_saved_bytes("wKeyItems", bytes([*items, 0xFF]))


def build_phase_2_checkpoint(
    repo_root: Path,
    destination: Path,
    constants: dict[str, int],
    checkpoint: str,
    *,
    hall_of_fame: bool = False,
    full_key_items: bool = False,
) -> Path:
    fixture = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    save = BatterySave.load(fixture, symbols)
    save.write_saved_u8("wWarpNumber", 0)

    relevant_events = (
        "EVENT_BEAT_ELITE_FOUR",
        "EVENT_GOT_GS_BALL_FROM_GOLDENROD_POKEMON_CENTER",
        "EVENT_CAN_GIVE_GS_BALL_TO_KURT",
        "EVENT_GAVE_GS_BALL_TO_KURT",
        "EVENT_FOREST_IS_RESTLESS",
        "EVENT_AZALEA_TOWN_KURT",
        "EVENT_ROUTE_34_ILEX_FOREST_GATE_LASS",
        "EVENT_ILEX_FOREST_LASS",
        "EVENT_KURTS_HOUSE_KURT_1",
        "EVENT_KURTS_HOUSE_KURT_2",
        "EVENT_CLEARED_SLOWPOKE_WELL",
        "EVENT_KURT_GAVE_YOU_LURE_BALL",
    )
    for event in relevant_events:
        save.set_event(constants[event], False)
    save.set_saved_bit("wDailyFlags1", 0, False)
    save.set_saved_bit(
        "wCelebiEvent", constants["CELEBIEVENT_FOREST_IS_RESTLESS_F"], False
    )

    if checkpoint == "goldenrod_delivery":
        save.write_saved_u8(
            "wMapGroup", constants["GROUP_GOLDENROD_POKECENTER_1F"]
        )
        save.write_saved_u8(
            "wMapNumber", constants["MAP_GOLDENROD_POKECENTER_1F"]
        )
        save.write_saved_u8("wXCoord", 3)
        save.write_saved_u8("wYCoord", 6)
        save.write_saved_u8("wGoldenrodPokecenter1FSceneID", 0)
        save.set_event(constants["EVENT_BEAT_ELITE_FOUR"], hall_of_fame)
        key_items = list(range(1, 26)) if full_key_items else []
        key_items = [item for item in key_items if item != constants["GS_BALL"]]
        while full_key_items and len(key_items) < 25:
            key_items.append(0xFE - len(key_items))
        _write_key_items(save, key_items)
    elif checkpoint == "kurt_wait":
        save.write_saved_u8("wMapGroup", constants["GROUP_KURTS_HOUSE"])
        save.write_saved_u8("wMapNumber", constants["MAP_KURTS_HOUSE"])
        save.write_saved_u8("wXCoord", 3)
        save.write_saved_u8("wYCoord", 3)
        save.set_event(constants["EVENT_CLEARED_SLOWPOKE_WELL"], True)
        save.set_event(constants["EVENT_KURT_GAVE_YOU_LURE_BALL"], True)
        save.set_event(constants["EVENT_CAN_GIVE_GS_BALL_TO_KURT"], True)
        save.set_event(constants["EVENT_KURTS_HOUSE_KURT_2"], True)
        _write_key_items(save, [constants["GS_BALL"]])
    elif checkpoint == "celebi_shrine":
        save.write_saved_u8("wMapGroup", constants["GROUP_ILEX_FOREST"])
        save.write_saved_u8("wMapNumber", constants["MAP_ILEX_FOREST"])
        save.write_saved_u8("wXCoord", 8)
        save.write_saved_u8("wYCoord", 23)
        save.set_event(constants["EVENT_FOREST_IS_RESTLESS"], True)
        save.set_event(constants["EVENT_AZALEA_TOWN_KURT"], True)
        save.set_event(constants["EVENT_ROUTE_34_ILEX_FOREST_GATE_LASS"], True)
        save.set_event(constants["EVENT_ILEX_FOREST_LASS"], True)
        save.set_saved_bit(
            "wCelebiEvent", constants["CELEBIEVENT_FOREST_IS_RESTLESS_F"], True
        )
        _write_key_items(save, [constants["GS_BALL"]])
    else:
        raise ValueError(f"unknown Phase 2 checkpoint {checkpoint}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


@contextmanager
def loaded_phase_2_checkpoint(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    checkpoint: str,
    max_frames: int,
    *,
    hall_of_fame: bool = False,
    full_key_items: bool = False,
    before_overworld: Callable[[PyBoySession], None] | None = None,
) -> Iterator[PyBoySession]:
    canonical = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    canonical_hash = _sha256(canonical)
    fixture = build_phase_2_checkpoint(
        repo_root,
        work_dir / f"{checkpoint}.sav",
        constants,
        checkpoint,
        hall_of_fame=hall_of_fame,
        full_key_items=full_key_items,
    )
    prepared = prepare_rom(
        work_dir / "rom",
        repo_root / "crystallegends.gbc",
        repo_root / "crystallegends.sym",
        save_fixture=fixture,
    )
    try:
        with PyBoySession(prepared) as session:

            def force_checkpoint_load(current: PyBoySession) -> None:
                if before_overworld is not None:
                    before_overworld(current)
                current.write_symbol("wDefaultSpawnpoint", constants["SPAWN_N_A"] & 0xFF)
                current.write_symbol("hMapEntryMethod", constants["MAPSETUP_WARP"])

            start_saved_game(session, max_frames, force_checkpoint_load)
            yield session
    finally:
        assert _sha256(canonical) == canonical_hash
