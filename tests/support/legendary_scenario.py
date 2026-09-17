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


def build_story_checkpoint(
    repo_root: Path,
    destination: Path,
    constants: dict[str, int],
    branch: dict,
    checkpoint: str,
) -> Path:
    fixture = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    save = BatterySave.load(fixture, symbols)
    for candidate in (
        "EVENT_GOT_ARTICUNO_FROM_ELM",
        "EVENT_GOT_ZAPDOS_FROM_ELM",
        "EVENT_GOT_MOLTRES_FROM_ELM",
    ):
        save.set_event(
            constants[candidate],
            checkpoint != "starter_choice" and candidate == branch["choice_event"],
        )
    save.set_event(
        constants["EVENT_GOT_A_POKEMON_FROM_ELM"], checkpoint != "starter_choice"
    )
    save.write_saved_u8("wWarpNumber", 0)

    if checkpoint == "starter_choice":
        save.write_saved_u8("wMapGroup", constants["GROUP_ELMS_LAB"])
        save.write_saved_u8("wMapNumber", constants["MAP_ELMS_LAB"])
        save.write_saved_u8(
            "wXCoord", {"LEFT": 6, "CENTER": 7, "RIGHT": 8}[branch["starter_slot"]]
        )
        save.write_saved_u8("wYCoord", 4)
        save.write_saved_u8("wElmsLabSceneID", constants["SCENE_ELMSLAB_CANT_LEAVE"])
        save.write_saved_u8(
            "wNewBarkTownSceneID", constants["SCENE_NEWBARKTOWN_TEACHER_STOPS_YOU"]
        )
        save.set_event(constants["EVENT_COP_IN_ELMS_LAB"], True)
        for event in (
            "EVENT_ARTICUNO_POKEBALL_IN_ELMS_LAB",
            "EVENT_ZAPDOS_POKEBALL_IN_ELMS_LAB",
            "EVENT_MOLTRES_POKEBALL_IN_ELMS_LAB",
            "EVENT_RIVAL_CHERRYGROVE_CITY",
        ):
            save.set_event(constants[event], False)
    elif checkpoint == "first_silver":
        save.write_saved_u8("wMapGroup", constants["GROUP_CHERRYGROVE_CITY"])
        save.write_saved_u8("wMapNumber", constants["MAP_CHERRYGROVE_CITY"])
        save.write_saved_u8("wXCoord", 34)
        save.write_saved_u8("wYCoord", 6)
        save.write_saved_u8(
            "wCherrygroveCitySceneID",
            constants["SCENE_CHERRYGROVECITY_MEET_RIVAL"],
        )
        save.set_event(constants["EVENT_RIVAL_CHERRYGROVE_CITY"], False)
    elif checkpoint == "elm_handoff":
        save.write_saved_u8("wMapGroup", constants["GROUP_ELMS_LAB"])
        save.write_saved_u8("wMapNumber", constants["MAP_ELMS_LAB"])
        save.write_saved_u8("wXCoord", 5)
        save.write_saved_u8("wYCoord", 3)
        save.write_saved_u8("wElmsLabSceneID", constants["SCENE_ELMSLAB_NOOP"])
        save.write_saved_u8(
            "wNewBarkTownSceneID", constants["SCENE_NEWBARKTOWN_NOOP"]
        )
        save.set_event(constants["EVENT_GOT_MYSTERY_EGG_FROM_MR_POKEMON"], True)
        save.set_event(constants["EVENT_GAVE_MYSTERY_EGG_TO_ELM"], False)
        save.set_event(constants["EVENT_OAK_MOVED_THIRD_BIRD"], False)
        save.set_event(constants["EVENT_COP_IN_ELMS_LAB"], True)
    else:
        raise ValueError(f"unknown legendary checkpoint {checkpoint}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


@contextmanager
def loaded_story_checkpoint(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    branch: dict,
    checkpoint: str,
    max_frames: int,
) -> Iterator[PyBoySession]:
    canonical = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    canonical_hash = _sha256(canonical)
    fixture = build_story_checkpoint(
        repo_root,
        work_dir / f"{checkpoint}-{branch['id']}.sav",
        constants,
        branch,
        checkpoint,
    )
    prepared = prepare_rom(
        work_dir / "rom",
        repo_root / "crystallegends.gbc",
        repo_root / "crystallegends.sym",
        save_fixture=fixture,
    )
    try:
        with PyBoySession(prepared) as session:
            spawn_name = {
                "starter_choice": "SPAWN_N_A",
                "first_silver": "SPAWN_CHERRYGROVE",
                "elm_handoff": "SPAWN_NEW_BARK",
            }[checkpoint]
            spawn = constants[spawn_name]

            def force_fresh_map_load(current: PyBoySession) -> None:
                current.write_symbol("wDefaultSpawnpoint", spawn & 0xFF)
                current.write_symbol("hMapEntryMethod", constants["MAPSETUP_WARP"])

            start_saved_game(session, max_frames, force_fresh_map_load)
            yield session
    finally:
        assert _sha256(canonical) == canonical_hash


def prepare_battle_party(
    session: PyBoySession,
    constants: dict[str, int],
    species: int,
    should_win: bool,
) -> None:
    length = constants["PARTYMON_STRUCT_LENGTH"]
    mon = bytearray(length)
    mon[constants["MON_SPECIES"]] = species
    mon[constants["MON_MOVES"]] = constants["TACKLE"]
    mon[constants["MON_PP"]] = 35
    mon[constants["MON_LEVEL"]] = 100 if should_win else 2
    stat = 999 if should_win else 1
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
        mon[offset : offset + 2] = stat.to_bytes(2, "big")
    session.write_symbol("wPartyCount", 1)
    session.write_symbol_bytes("wPartySpecies", bytes([species, 0xFF]))
    session.write_symbol_bytes("wPartyMon1", bytes(mon))
    session.write_symbol_bytes("wPartyMon1OT", bytes([0x50]) * 11)
    session.write_symbol_bytes("wPartyMon1Nickname", bytes([0x50]) * 11)


def advance_with_a_until(
    session: PyBoySession,
    predicate,
    max_frames: int,
    description: str,
) -> None:
    start = session.frames
    while session.frames - start < max_frames:
        if predicate(session):
            return
        session.tap("a", 2, 20)
    session.wait_until(predicate, 1, description)


def place_player(session: PyBoySession, x: int, y: int) -> None:
    session.write_symbol("wXCoord", x)
    session.write_symbol("wYCoord", y)
    player = bytearray(session.read_symbol_bytes("wPlayerStruct", 0x21))
    map_x = x + 4
    map_y = y + 4
    player[0x10:0x14] = bytes([map_x, map_y, map_x, map_y])
    session.write_symbol_bytes("wPlayerStruct", player)


def walk_steps(
    session: PyBoySession,
    button: str,
    coordinate_label: str,
    delta: int,
    steps: int,
    max_frames: int,
) -> None:
    for _ in range(steps):
        origin = session.read_symbol(coordinate_label)
        target = origin + delta
        session.tap(button, 2, 2)
        session.tick(20)
        if session.read_symbol(coordinate_label) == origin:
            session.tap(button, 2, 2)
        session.wait_until(
            lambda current: current.read_symbol(coordinate_label) == target,
            max_frames,
            f"{coordinate_label} to become {target}",
        )
