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


def build_phase_8_checkpoint(
    repo_root: Path,
    destination: Path,
    constants: dict[str, int],
    scenario: dict,
    branch: dict,
    *,
    start: str,
    mt_moon_won: bool,
    released: bool = False,
    weekly_fight: bool = False,
) -> Path:
    fixture = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    save = BatterySave.load(fixture, symbols)

    for candidate in (
        "EVENT_GOT_ARTICUNO_FROM_ELM",
        "EVENT_GOT_ZAPDOS_FROM_ELM",
        "EVENT_GOT_MOLTRES_FROM_ELM",
    ):
        save.set_event(constants[candidate], candidate == branch["choice_event"])
    save.set_event(constants["EVENT_GOT_A_POKEMON_FROM_ELM"], True)
    save.set_event(constants["EVENT_OAK_MOVED_THIRD_BIRD"], True)
    save.set_event(constants["EVENT_BEAT_RIVAL_IN_MT_MOON"], mt_moon_won)
    save.set_event(constants["EVENT_MT_MOON_RIVAL"], mt_moon_won)
    save.set_event(constants["EVENT_COP_IN_ELMS_LAB"], True)
    save.set_event(constants["EVENT_INDIGO_PLATEAU_POKECENTER_RIVAL"], True)
    save.set_event(constants["EVENT_RIVAL_DRAGONS_DEN"], True)
    save.set_event(constants["EVENT_SILVER_BIRD_RELEASED"], released)
    for event in scenario["events"]["availability"]:
        save.set_event(
            constants[event], released and event == branch["availability_event"]
        )

    if start == "mount_moon":
        target = scenario["mount_moon"]
        coordinate = target["start"]
    elif start == "elms_lab":
        target = scenario["elms_lab"]
        coordinate = target["entry_start"]
    elif start == "indigo":
        target = scenario["indigo"]
        coordinate = target["entrances"][0]
    elif start == "dragons_den":
        target = scenario["dragons_den"]
        coordinate = target["start"]
    elif start == "dragon_shrine":
        target = {
            "map": scenario["dragons_den"]["shrine_map"],
        }
        coordinate = scenario["dragons_den"]["shrine_start"]
        save.set_event(constants["EVENT_GOT_DRATINI"], True)
        save.set_event(constants["EVENT_TEMPORARY_UNTIL_MAP_RELOAD_1"], False)
        save.set_event(constants["EVENT_TEMPORARY_UNTIL_MAP_RELOAD_7"], False)
    else:
        raise ValueError(f"unsupported Phase 8 checkpoint {start}")

    weekly_bit = (
        constants["ENGINE_INDIGO_PLATEAU_RIVAL_FIGHT"]
        - constants["ENGINE_MT_MOON_SQUARE_CLEFAIRY"]
    )
    save.set_saved_bit("wDailyFlags2", weekly_bit, weekly_fight)

    save.write_saved_u8("wWarpNumber", 0)
    save.write_saved_u8("wMapGroup", constants[f"GROUP_{target['map']}"])
    save.write_saved_u8("wMapNumber", constants[f"MAP_{target['map']}"])
    save.write_saved_u8("wXCoord", coordinate["x"])
    save.write_saved_u8("wYCoord", coordinate["y"])
    save.write_saved_u8(
        "wPlayerDirection", constants[f"OW_{coordinate['facing']}"]
    )
    save.write_saved_u8(
        "wMountMoonSceneID",
        constants[
            "SCENE_MOUNTMOON_NOOP"
            if mt_moon_won
            else "SCENE_MOUNTMOON_RIVAL_BATTLE"
        ],
    )
    save.write_saved_u8(
        "wElmsLabSceneID",
        constants[
            "SCENE_ELMSLAB_SILVER_RETURNS_BIRD"
            if mt_moon_won and not released
            else "SCENE_ELMSLAB_NOOP"
        ],
    )
    save.write_saved_u8(
        "wIndigoPlateauPokecenter1FSceneID",
        constants["SCENE_INDIGOPLATEAUPOKECENTER1F_RIVAL_BATTLE"],
    )
    save.write_saved_u8(
        "wDragonsDenB1FSceneID", constants["SCENE_DRAGONSDENB1F_NOOP"]
    )
    save.write_saved_u8(
        "wDragonShrineSceneID", constants["SCENE_DRAGONSHRINE_NOOP"]
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


def _start_automatic_scene(
    session: PyBoySession,
    max_frames: int,
    before_overworld: Callable[[PyBoySession], None],
) -> None:
    for label in (
        "TitleScreenMain",
        "MainMenu",
        "Continue",
        "ConfirmContinue",
        "FinishContinueFunction",
        "OverworldLoop",
    ):
        session.register_hook(
            label, before_overworld if label == "OverworldLoop" else None
        )
    session.wait_for_hook("TitleScreenMain", max_frames)
    session.tap("start", 10, 10)
    session.wait_for_hook("MainMenu", max_frames)
    session.tick(120)
    session.tap("a", 10, 10)
    session.wait_for_hook("Continue", max_frames)
    session.wait_for_hook("ConfirmContinue", max_frames)
    session.tick(30)
    session.tap("a", 10, 10)
    session.wait_for_hook("FinishContinueFunction", max_frames)
    session.wait_for_hook("OverworldLoop", max_frames)
    session.tick(30)


@contextmanager
def loaded_phase_8_checkpoint(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    scenario: dict,
    branch: dict,
    *,
    start: str,
    mt_moon_won: bool,
    released: bool = False,
    weekday: int | None = None,
    weekly_fight: bool = False,
    before_overworld: Callable[[PyBoySession], None] | None = None,
) -> Iterator[PyBoySession]:
    canonical = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    canonical_hash = _sha256(canonical)
    fixture = build_phase_8_checkpoint(
        repo_root,
        work_dir / f"phase-08-{start}-{branch['id']}.sav",
        constants,
        scenario,
        branch,
        start=start,
        mt_moon_won=mt_moon_won,
        released=released,
        weekly_fight=weekly_fight,
    )
    prepared = prepare_rom(
        work_dir / "rom",
        repo_root / scenario["rom"],
        repo_root / scenario["symbols"],
        save_fixture=fixture,
    )
    try:
        with PyBoySession(prepared) as session:
            if weekday is not None:
                session.register_hook(
                    "GetWeekday",
                    lambda current: current.write_symbol("wCurDay", weekday),
                )

            def prepare(current: PyBoySession) -> None:
                current.write_symbol(
                    "wDefaultSpawnpoint", constants["SPAWN_N_A"] & 0xFF
                )
                current.write_symbol("hMapEntryMethod", constants["MAPSETUP_WARP"])
                if before_overworld is not None:
                    before_overworld(current)

            if (start == "mount_moon" and not mt_moon_won) or (
                start == "elms_lab" and mt_moon_won and not released
            ):
                _start_automatic_scene(
                    session, scenario["max_frames_per_step"], prepare
                )
            else:
                start_saved_game(
                    session, scenario["max_frames_per_step"], prepare
                )
            yield session
    finally:
        assert _sha256(canonical) == canonical_hash


@contextmanager
def loaded_phase_8_saved_game(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    scenario: dict,
    save_fixture: Path,
    *,
    weekday: int | None = None,
) -> Iterator[PyBoySession]:
    prepared = prepare_rom(
        work_dir,
        repo_root / scenario["rom"],
        repo_root / scenario["symbols"],
        save_fixture=save_fixture,
    )
    with PyBoySession(prepared) as session:
        if weekday is not None:
            session.register_hook(
                "GetWeekday",
                lambda current: current.write_symbol("wCurDay", weekday),
            )

        def force_fresh_map_load(current: PyBoySession) -> None:
            current.write_symbol("wDefaultSpawnpoint", constants["SPAWN_N_A"] & 0xFF)
            current.write_symbol("hMapEntryMethod", constants["MAPSETUP_WARP"])

        start_saved_game(
            session,
            scenario["max_frames_per_step"],
            force_fresh_map_load,
        )
        yield session
