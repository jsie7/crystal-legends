from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage, decode_background_events
from tests.support.symbol_table import SymbolTable


pytestmark = pytest.mark.rom


def test_compiled_bedroom_tv_event_matches_symbols(
    repo_root: Path, tmp_path: Path
) -> None:
    constants = resolve_constants(
        repo_root,
        tmp_path,
        ["WARP_EVENT_SIZE", "COORD_EVENT_SIZE", "BG_EVENT_SIZE", "BGEVENT_UP"],
    )
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    events = decode_background_events(
        rom,
        symbols,
        "PlayersHouse2F_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
    )
    matching = [
        event
        for event in events
        if (event.x, event.y) == (4, 1)
        and event.event_type == constants["BGEVENT_UP"]
        and event.script_pointer == symbols["PlayersHouse2FTVScript"].address
    ]
    assert len(events) == 5
    assert len(matching) == 1
    assert symbols["PlayersHouse2FTVScript"].bank == symbols[
        "PlayersHouse2F_MapEvents"
    ].bank


def test_reference_rom_has_no_custom_bedroom_event(
    repo_root: Path, tmp_path: Path
) -> None:
    constants = resolve_constants(
        repo_root,
        tmp_path,
        ["WARP_EVENT_SIZE", "COORD_EVENT_SIZE", "BG_EVENT_SIZE"],
    )
    symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())
    assert "PlayersHouse2FTVScript" not in symbols
    assert "PlayersHouse2FDebugTVScript" not in symbols
    events = decode_background_events(
        RomImage.load(repo_root / "pokecrystal11.gbc"),
        symbols,
        "PlayersHouse2F_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
    )
    assert len(events) == 4
    assert not any((event.x, event.y) == (4, 1) for event in events)
