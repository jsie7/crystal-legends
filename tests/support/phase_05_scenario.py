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
    elif location == "gift_room":
        target = scenario["gift"]
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


def retarget_phase_5_save(
    source: Path,
    destination: Path,
    repo_root: Path,
    constants: dict[str, int],
    scenario: dict,
) -> Path:
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    save = BatterySave.load(source, symbols)
    save.write_saved_u8("wWarpNumber", 0)
    gift = scenario["gift"]
    save.write_saved_u8("wMapGroup", constants[f"GROUP_{gift['map']}"])
    save.write_saved_u8("wMapNumber", constants[f"MAP_{gift['map']}"])
    save.write_saved_u8("wXCoord", gift["start"]["x"])
    save.write_saved_u8("wYCoord", gift["start"]["y"])
    save.set_event(constants[scenario["picture_event"]], True)
    save.set_event(constants[scenario["wall_event"]], True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


def build_kim_trade_checkpoint(
    repo_root: Path,
    destination: Path,
    constants: dict[str, int],
) -> Path:
    fixture = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    save = BatterySave.load(fixture, symbols)
    save.write_saved_u8("wWarpNumber", 0)
    save.write_saved_u8("wMapGroup", constants["GROUP_ROUTE_14"])
    save.write_saved_u8("wMapNumber", constants["MAP_ROUTE_14"])
    save.write_saved_u8("wXCoord", 7)
    save.write_saved_u8("wYCoord", 6)
    save.set_saved_bit("wTradeFlags", constants["NPC_TRADE_KIM"], False)
    save.set_event(constants["EVENT_GOT_AERODACTYL_FROM_ALPH"], False)
    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


def prepare_level_28_chansey(
    session: PyBoySession,
    constants: dict[str, int],
    nickname: bytes,
    ot_name: bytes,
) -> None:
    mon = bytearray(constants["PARTYMON_STRUCT_LENGTH"])
    mon[constants["MON_SPECIES"]] = constants["CHANSEY"]
    mon[constants["MON_ITEM"]] = constants["NO_ITEM"]
    mon[constants["MON_MOVES"]] = constants["TACKLE"]
    mon[constants["MON_PP"]] = 35
    mon[constants["MON_OT_ID"] : constants["MON_OT_ID"] + 2] = (12345).to_bytes(
        2, "big"
    )
    mon[constants["MON_EXP"] : constants["MON_EXP"] + 3] = (
        4 * 28**3 // 5
    ).to_bytes(3, "big")
    mon[constants["MON_DVS"] : constants["MON_DVS"] + 2] = bytes([0x77, 0x77])
    mon[constants["MON_HAPPINESS"]] = 70
    mon[constants["MON_LEVEL"]] = 28
    for field in (
        "MON_HP",
        "MON_MAXHP",
        "MON_ATK",
        "MON_DEF",
        "MON_SPD",
        "MON_SAT",
        "MON_SDF",
    ):
        offset = constants[field]
        mon[offset : offset + 2] = (100).to_bytes(2, "big")

    session.write_symbol("wPartyCount", 1)
    session.write_symbol_bytes(
        "wPartySpecies", bytes([constants["CHANSEY"], 0xFF])
    )
    session.write_symbol_bytes("wPartyMon1", bytes(mon))
    session.write_symbol_bytes("wPartyMon1OT", ot_name)
    session.write_symbol_bytes("wPartyMon1Nickname", nickname)


@contextmanager
def loaded_kim_trade_checkpoint(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    max_frames: int,
) -> Iterator[PyBoySession]:
    canonical = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    canonical_hash = _sha256(canonical)
    fixture = build_kim_trade_checkpoint(
        repo_root,
        work_dir / "phase_05_kim_trade.sav",
        constants,
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

            start_saved_game(session, max_frames, force_fresh_map_load)
            yield session
    finally:
        assert _sha256(canonical) == canonical_hash


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
