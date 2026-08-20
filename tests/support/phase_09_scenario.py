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
    "EVENT_GOT_BULBASAUR_FROM_ERIKA",
    "EVENT_GOT_SQUIRTLE_FROM_MISTY",
    "EVENT_GOT_CHARMANDER_FROM_BLAINE",
)


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _set_kanto_badge(
    save: BatterySave,
    constants: dict[str, int],
    badge: str,
    enabled: bool,
) -> None:
    bit = constants[badge] - constants["ENGINE_BOULDERBADGE"]
    save.set_saved_bit("wKantoBadges", bit, enabled)


def build_phase_9_gift_checkpoint(
    repo_root: Path,
    destination: Path,
    constants: dict[str, int],
    scenario: dict,
    gift: dict,
    *,
    service_complete: bool,
    gift_complete: bool = False,
) -> Path:
    fixture = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    save = BatterySave.load(fixture, symbols)
    save.write_saved_u8("wWarpNumber", 0)
    save.write_saved_u8("wMapGroup", constants[f"GROUP_{gift['map']}"])
    save.write_saved_u8("wMapNumber", constants[f"MAP_{gift['map']}"])
    save.write_saved_u8("wXCoord", gift["start"]["x"])
    save.write_saved_u8("wYCoord", gift["start"]["y"])
    _set_kanto_badge(save, constants, gift["badge"], True)
    save.set_event(constants[gift["service_event"]], service_complete)
    for event in _GIFT_EVENTS:
        save.set_event(
            constants[event], event == gift["completion_event"] and gift_complete
        )

    # Keep each leader on the post-battle, immediately interactive map state.
    save.set_event(constants["EVENT_GOT_TM19_GIGA_DRAIN"], True)
    save.set_event(constants["EVENT_TRAINERS_IN_CERULEAN_GYM"], False)
    save.set_event(constants["EVENT_CERULEAN_GYM_ROCKET"], True)
    save.write_saved_u8(
        "wCeruleanGymSceneID", constants["SCENE_CERULEANGYM_NOOP"]
    )

    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


def build_phase_9_map_checkpoint(
    repo_root: Path,
    destination: Path,
    constants: dict[str, int],
    *,
    map_name: str,
    x: int,
    y: int,
    events: dict[str, bool] | None = None,
    badges: tuple[str, ...] = (),
) -> Path:
    fixture = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    save = BatterySave.load(fixture, symbols)
    save.write_saved_u8("wWarpNumber", 0)
    save.write_saved_u8("wMapGroup", constants[f"GROUP_{map_name}"])
    save.write_saved_u8("wMapNumber", constants[f"MAP_{map_name}"])
    save.write_saved_u8("wXCoord", x)
    save.write_saved_u8("wYCoord", y)
    for badge in badges:
        _set_kanto_badge(save, constants, badge, True)
    for event, enabled in (events or {}).items():
        save.set_event(constants[event], enabled)
    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


@contextmanager
def loaded_phase_9_gift_checkpoint(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    scenario: dict,
    gift: dict,
    *,
    service_complete: bool,
    gift_complete: bool = False,
) -> Iterator[PyBoySession]:
    canonical = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    canonical_hash = _sha256(canonical)
    fixture = build_phase_9_gift_checkpoint(
        repo_root,
        work_dir / f"{gift['species'].lower()}.sav",
        constants,
        scenario,
        gift,
        service_complete=service_complete,
        gift_complete=gift_complete,
    )
    prepared = prepare_rom(
        work_dir / "rom",
        repo_root / scenario["rom"],
        repo_root / scenario["symbols"],
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
def loaded_phase_9_map_checkpoint(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    scenario: dict,
    *,
    map_name: str,
    x: int,
    y: int,
    events: dict[str, bool] | None = None,
    badges: tuple[str, ...] = (),
) -> Iterator[PyBoySession]:
    canonical = repo_root / "tests/fixtures/saves/bedroom_initialized.sav"
    canonical_hash = _sha256(canonical)
    fixture = build_phase_9_map_checkpoint(
        repo_root,
        work_dir / f"{map_name.lower()}.sav",
        constants,
        map_name=map_name,
        x=x,
        y=y,
        events=events,
        badges=badges,
    )
    prepared = prepare_rom(
        work_dir / "rom",
        repo_root / scenario["rom"],
        repo_root / scenario["symbols"],
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
def loaded_phase_9_saved_game(
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
            current.write_symbol("wDefaultSpawnpoint", constants["SPAWN_N_A"] & 0xFF)
            current.write_symbol("hMapEntryMethod", constants["MAPSETUP_WARP"])

        start_saved_game(
            session,
            scenario["max_frames_per_step"],
            force_fresh_map_load,
        )
        yield session
