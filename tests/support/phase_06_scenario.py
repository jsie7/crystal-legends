from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Callable, Iterator

from tests.support.bedroom_scenario import start_saved_game
from tests.support.pyboy_session import PyBoySession, prepare_rom
from tests.support.save_fixture import BatterySave
from tests.support.symbol_table import SymbolTable


ROAM_STRUCT_LENGTH = 7


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _slot_bytes(
    constants: dict[str, int],
    species: str,
    route: str,
    *,
    hp: int = 0,
    dvs: bytes = b"\x00\x00",
) -> bytes:
    if len(dvs) != 2:
        raise ValueError("roamer DVs must contain exactly two bytes")
    return bytes(
        [
            constants[species],
            40,
            constants[f"GROUP_{route}"],
            constants[f"MAP_{route}"],
            hp,
            *dvs,
        ]
    )


def build_phase_6_checkpoint(
    repo_root: Path,
    destination: Path,
    constants: dict[str, int],
    scenario: dict,
    *,
    checkpoint: str,
    selected_species: str = "RAIKOU",
    selected_route: str | None = None,
    seen: bool = True,
) -> Path:
    fixture = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    save = BatterySave.load(fixture, symbols)
    save.write_saved_u8("wWarpNumber", 0)
    save.write_saved_bytes("wPokedexSeen", bytes(32))
    save.write_saved_bytes("wPokedexCaught", bytes(32))
    save.set_saved_bit("wStatusFlags", constants["STATUSFLAGS_POKEDEX_F"], True)
    save.set_event(constants["EVENT_RELEASED_THE_BEASTS"], checkpoint != "release")

    if checkpoint == "release":
        target = scenario["release"]
        save.write_saved_bytes("wRoamMon1", bytes(ROAM_STRUCT_LENGTH * 3))
        save.write_saved_u8(
            "wBurnedTowerB1FSceneID",
            constants["SCENE_BURNEDTOWERB1F_RELEASE_THE_BEASTS"],
        )
        save.set_event(constants["EVENT_BURNED_TOWER_B1F_BEASTS_1"], True)
        save.set_event(constants["EVENT_BURNED_TOWER_B1F_BEASTS_2"], False)
    elif checkpoint in {"land", "different_route"}:
        target = {
            "map": scenario["encounter"]["map"],
            "start": {
                "x": scenario["encounter"]["grass"][0][0],
                "y": scenario["encounter"]["grass"][0][1],
            },
        }
        for event in ("EVENT_BEAT_TWINS_ANN_AND_ANNE", "EVENT_BEAT_PSYCHIC_GREG"):
            save.set_event(constants[event], True)
    elif checkpoint == "water":
        target = {
            "map": scenario["water_rejection"]["map"],
            "start": {
                "x": scenario["water_rejection"]["coordinate"][0],
                "y": scenario["water_rejection"]["coordinate"][1],
            },
        }
        save.write_saved_u8("wPlayerState", constants["PLAYER_SURF"])
        save.write_saved_u8("wRoute42SceneID", constants["SCENE_ROUTE42_NOOP"])
        save.set_event(constants["EVENT_SAW_SUICUNE_ON_ROUTE_42"], True)
    else:
        raise ValueError(f"unknown Phase 6 checkpoint {checkpoint}")

    save.write_saved_u8("wMapGroup", constants[f"GROUP_{target['map']}"])
    save.write_saved_u8("wMapNumber", constants[f"MAP_{target['map']}"])
    save.write_saved_u8("wXCoord", target["start"]["x"])
    save.write_saved_u8("wYCoord", target["start"]["y"])

    if checkpoint != "release":
        for roamer in scenario["roamers"]:
            route = roamer["starting_route"]
            if roamer["species"] == selected_species:
                route = selected_route or (
                    scenario["encounter"]["different_route"]
                    if checkpoint == "different_route"
                    else target["map"]
                )
            save.write_saved_bytes(
                roamer["slot"],
                _slot_bytes(constants, roamer["species"], route),
            )
        save.write_saved_bytes(
            "wRoamMon3",
            bytes(
                [
                    0,
                    0,
                    constants["GROUP_N_A"] & 0xFF,
                    constants["MAP_N_A"] & 0xFF,
                    0,
                    0x55,
                    0xAA,
                ]
            ),
        )
        if seen:
            save.set_saved_bit_offset(
                "wPokedexSeen", constants[selected_species] - 1, True
            )

    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


@contextmanager
def loaded_phase_6_checkpoint(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    scenario: dict,
    *,
    checkpoint: str,
    selected_species: str = "RAIKOU",
    selected_route: str | None = None,
    before_overworld: Callable[[PyBoySession], None] | None = None,
) -> Iterator[PyBoySession]:
    canonical = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    canonical_hash = _sha256(canonical)
    fixture = build_phase_6_checkpoint(
        repo_root,
        work_dir / f"phase_06_{checkpoint}_{selected_species.lower()}.sav",
        constants,
        scenario,
        checkpoint=checkpoint,
        selected_species=selected_species,
        selected_route=selected_route,
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
                if before_overworld is not None:
                    before_overworld(current)
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
def loaded_phase_6_saved_game(
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


def force_roamer_rng(session: PyBoySession, selection: int) -> None:
    if selection not in (1, 2):
        raise ValueError("roamer RNG selection must be 1 or 2")

    routine = session.symbols["CheckEncounterRoamMon"]
    routine_end = session.symbols["CheckEncounterRoamMon.DontEncounterRoamMon"]
    random = session.symbols["Random"]
    rom = session.prepared.rom.read_bytes()
    physical_start = routine.bank * 0x4000 + (routine.address - 0x4000)
    physical_end = physical_start + (routine_end.address - routine.address)
    call_random = bytes([0xCD, random.address & 0xFF, random.address >> 8])
    call_offset = rom.find(call_random, physical_start, physical_end)
    if call_offset < 0:
        raise AssertionError("CheckEncounterRoamMon no longer calls Random")
    after_call = routine.address + (call_offset - physical_start) + len(call_random)

    def force(current: PyBoySession) -> None:
        current.pyboy.register_file.A = selection

    session.pyboy.hook_register(routine.bank, after_call, force, session)


def start_roaming_battle(
    session: PyBoySession,
    constants: dict[str, int],
    scenario: dict,
    roamer: dict,
) -> None:
    rejections: list[dict[str, object]] = []
    session.register_hook("CheckEncounterRoamMon")
    session.register_hook("BattleMenu")
    session.register_hook(
        "CheckEncounterRoamMon.DontEncounterRoamMon",
        lambda current: rejections.append(
            {
                "slot": current.read_symbol_bytes(
                    roamer["slot"], ROAM_STRUCT_LENGTH
                ).hex(),
                "map": (
                    current.read_symbol("wMapGroup"),
                    current.read_symbol("wMapNumber"),
                ),
                "collision": current.read_symbol("wPlayerTileCollision"),
                "a": current.pyboy.register_file.A,
                "d": current.pyboy.register_file.D,
                "e": current.pyboy.register_file.E,
            }
        ),
    )
    force_roamer_rng(session, roamer["rng_selection"])
    session.write_symbol_bytes(
        f"{roamer['slot']}MapGroup",
        bytes(
            [
                session.read_symbol("wMapGroup"),
                session.read_symbol("wMapNumber"),
            ]
        ),
    )
    session.write_symbol_bytes("wMornEncounterRate", b"\xff\xff\xff")
    directions = ("right", "left")
    max_frames = scenario["max_frames_per_step"]
    start = session.frames
    index = 0
    while (
        session.read_symbol("wBattleType") != constants["BATTLETYPE_ROAMING"]
        and session.frames - start < max_frames
    ):
        session.tap(directions[index % 2], 2, 12)
        index += 1
    if session.read_symbol("wBattleType") == constants["BATTLETYPE_ROAMING"]:
        while (
            "BattleMenu" not in session.hook_history
            and session.frames - start < max_frames
        ):
            session.tap("a", 2, 8)
    if "BattleMenu" not in session.hook_history:
        raise AssertionError(
            f"roaming battle did not start; last rejections: {rejections[-5:]}\n"
            f"{session.diagnostics()}"
        )
    assert session.read_symbol("wBattleType") == constants["BATTLETYPE_ROAMING"]
    assert session.read_symbol("wEnemyMonSpecies") == constants[roamer["species"]]
    assert session.read_symbol("wEnemyMonLevel") == roamer["level"]


def start_wild_battle(
    session: PyBoySession,
    constants: dict[str, int],
    scenario: dict,
) -> None:
    session.register_hook("BattleMenu")
    unavailable = bytes(
        [constants["GROUP_N_A"] & 0xFF, constants["MAP_N_A"] & 0xFF]
    )
    for slot in (1, 2):
        session.write_symbol_bytes(f"wRoamMon{slot}MapGroup", unavailable)
    session.write_symbol_bytes("wMornEncounterRate", b"\xff\xff\xff")

    max_frames = scenario["max_frames_per_step"]
    start = session.frames
    direction_index = 0
    directions = ("right", "left")
    while (
        session.read_symbol("wBattleMode") == 0
        and session.frames - start < max_frames
    ):
        session.tap(directions[direction_index % 2], 2, 12)
        direction_index += 1
    while (
        "BattleMenu" not in session.hook_history
        and session.frames - start < max_frames
    ):
        session.tap("a", 2, 8)
    if "BattleMenu" not in session.hook_history:
        raise AssertionError(
            f"ordinary wild battle did not start\n{session.diagnostics()}"
        )
    assert session.read_symbol("wBattleType") != constants["BATTLETYPE_ROAMING"]
