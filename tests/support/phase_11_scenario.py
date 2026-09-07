from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from typing import Callable, Iterator, Sequence

from tests.support.bedroom_scenario import start_saved_game
from tests.support.pyboy_session import PyBoySession, prepare_rom
from tests.support.save_fixture import BatterySave
from tests.support.symbol_table import SymbolTable


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def caught_bitfield(
    count: int, omissions: Sequence[int] | None = None
) -> bytes:
    if count not in range(252):
        raise ValueError("caught count must be in 0..251")
    if omissions is None:
        omitted = set(range(count + 1, 252))
    else:
        omitted = set(omissions)
        if len(omitted) != 251 - count:
            raise ValueError("omission count does not match caught count")
        if any(species not in range(1, 252) for species in omitted):
            raise ValueError("omitted species must be in 1..251")
    caught = bytearray(32)
    for species in range(1, 252):
        if species in omitted:
            continue
        index = species - 1
        caught[index // 8] |= 1 << (index % 8)
    assert sum(value.bit_count() for value in caught) == count
    assert caught[-1] & 0b11111000 == 0
    return bytes(caught)


def _write_badges(save: BatterySave) -> None:
    save.write_saved_u8("wJohtoBadges", 0xFF)
    save.write_saved_u8("wKantoBadges", 0xFF)


def build_phase_11_checkpoint(
    repo_root: Path,
    destination: Path,
    constants: dict[str, int],
    scenario: dict,
    *,
    checkpoint: str,
    caught: int,
    starter_event: str | None = "EVENT_GOT_ARTICUNO_FROM_ELM",
    red_defeated: bool = False,
    oak_defeated: bool = False,
    red_visible: bool = True,
    omissions: Sequence[int] | None = None,
    reference: bool = False,
) -> Path:
    fixture = repo_root / "tests/fixtures/saves" / scenario["save_fixture"]
    symbols_key = "reference_symbols" if reference else "symbols"
    symbols = SymbolTable.parse((repo_root / scenario[symbols_key]).read_text())
    save = BatterySave.load(fixture, symbols)
    target = scenario["checkpoints"][checkpoint]

    save.write_saved_u8("wWarpNumber", 0)
    save.write_saved_u8("wMapGroup", constants[f"GROUP_{target['map']}"])
    save.write_saved_u8("wMapNumber", constants[f"MAP_{target['map']}"])
    save.write_saved_u8("wXCoord", target["x"])
    save.write_saved_u8("wYCoord", target["y"])
    save.write_saved_u8("wPlayerDirection", constants[f"OW_{target['facing']}"])
    _write_badges(save)
    save.set_saved_bit(
        "wStatusFlags", constants["STATUSFLAGS_HALL_OF_FAME_F"], True
    )
    save.write_saved_u8("wHallOfFameCount", 1)
    dex = caught_bitfield(caught, omissions)
    save.write_saved_bytes("wPokedexCaught", dex)
    save.write_saved_bytes("wPokedexSeen", dex)

    save.set_event(constants["EVENT_OPENED_MT_SILVER"], True)
    save.set_event(constants["EVENT_TALKED_TO_OAK_IN_KANTO"], True)
    save.set_event(constants["EVENT_BEAT_RED"], red_defeated)
    save.set_event(constants["EVENT_BEAT_PROFESSOR_OAK"], oak_defeated)
    save.set_event(constants["EVENT_RED_IN_MT_SILVER"], not red_visible)
    for candidate in (
        "EVENT_GOT_ARTICUNO_FROM_ELM",
        "EVENT_GOT_ZAPDOS_FROM_ELM",
        "EVENT_GOT_MOLTRES_FROM_ELM",
    ):
        save.set_event(constants[candidate], candidate == starter_event)

    destination.parent.mkdir(parents=True, exist_ok=True)
    save.write(destination)
    return destination


@contextmanager
def loaded_phase_11_checkpoint(
    repo_root: Path,
    work_dir: Path,
    constants: dict[str, int],
    scenario: dict,
    *,
    checkpoint: str,
    caught: int,
    starter_event: str | None = "EVENT_GOT_ARTICUNO_FROM_ELM",
    red_defeated: bool = False,
    oak_defeated: bool = False,
    red_visible: bool = True,
    omissions: Sequence[int] | None = None,
    before_overworld: Callable[[PyBoySession], None] | None = None,
    reference: bool = False,
) -> Iterator[PyBoySession]:
    canonical = repo_root / "tests/fixtures/saves" / scenario["save_fixture"]
    canonical_hash = _sha256(canonical)
    fixture = build_phase_11_checkpoint(
        repo_root,
        work_dir / f"phase-11-{checkpoint}.sav",
        constants,
        scenario,
        checkpoint=checkpoint,
        caught=caught,
        starter_event=starter_event,
        red_defeated=red_defeated,
        oak_defeated=oak_defeated,
        red_visible=red_visible,
        omissions=omissions,
        reference=reference,
    )
    rom_key = "reference_rom" if reference else "rom"
    symbols_key = "reference_symbols" if reference else "symbols"
    prepared = prepare_rom(
        work_dir / "rom",
        repo_root / scenario[rom_key],
        repo_root / scenario[symbols_key],
        save_fixture=fixture,
    )
    try:
        with PyBoySession(prepared) as session:
            prepared_overworld = False

            def prepare(current: PyBoySession) -> None:
                nonlocal prepared_overworld
                if prepared_overworld:
                    return
                prepared_overworld = True
                current.write_symbol(
                    "wDefaultSpawnpoint", constants["SPAWN_N_A"] & 0xFF
                )
                current.write_symbol("hMapEntryMethod", constants["MAPSETUP_WARP"])
                if before_overworld is not None:
                    before_overworld(current)

            start_saved_game(session, scenario["max_frames_per_step"], prepare)
            yield session
    finally:
        assert _sha256(canonical) == canonical_hash


@contextmanager
def loaded_phase_11_saved_game(
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
        prepared_overworld = False

        def prepare(current: PyBoySession) -> None:
            nonlocal prepared_overworld
            if prepared_overworld:
                return
            prepared_overworld = True
            current.write_symbol(
                "wDefaultSpawnpoint", constants["SPAWN_N_A"] & 0xFF
            )
            current.write_symbol("hMapEntryMethod", constants["MAPSETUP_WARP"])

        start_saved_game(session, scenario["max_frames_per_step"], prepare)
        yield session
