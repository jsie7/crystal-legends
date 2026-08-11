from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage, decode_object_events
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase4]


@pytest.fixture(scope="module")
def phase_4_constants(repo_root: Path, tmp_path_factory) -> dict[str, int]:
    return resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_4_rom_constants"),
        [
            "EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST",
            "EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER",
            "EVENT_GOT_TOTODILE_FROM_CIANWOOD",
            "EVENT_GOT_HM01_CUT",
            "EVENT_RELEASED_THE_BEASTS",
            "SPRITE_CHIKORITA",
            "SPRITE_CYNDAQUIL",
            "SPRITE_TOTODILE",
            "NUM_POKEMON_SPRITES",
            "CHIKORITA",
            "CYNDAQUIL",
            "TOTODILE",
            "WARP_EVENT_SIZE",
            "COORD_EVENT_SIZE",
            "BG_EVENT_SIZE",
            "OBJECT_EVENT_SIZE",
            "SPRITEMOVEDATA_POKEMON",
            "PAL_NPC_GREEN",
            "PAL_NPC_RED",
            "OBJECTTYPE_SCRIPT",
            "NO_ITEM",
            "FALSE",
            "givepoke_command",
            "checkevent_command",
            "ifequal_command",
            "setevent_command",
            "disappear_command",
            "appear_command",
        ],
    )


def _pointer(value: int) -> bytes:
    return value.to_bytes(2, "little")


def _object_events(
    repo_root: Path,
    rom_name: str,
    symbol_name: str,
    map_label: str,
    constants: dict[str, int],
):
    rom = RomImage.load(repo_root / rom_name)
    symbols = SymbolTable.parse((repo_root / symbol_name).read_text())
    return decode_object_events(
        rom,
        symbols,
        map_label,
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
        constants["OBJECT_EVENT_SIZE"],
    )


def test_compiled_phase_4_ids_use_the_reserved_numeric_slots(
    phase_4_constants: dict[str, int],
) -> None:
    assert [
        phase_4_constants["EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST"],
        phase_4_constants["EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER"],
        phase_4_constants["EVENT_GOT_TOTODILE_FROM_CIANWOOD"],
    ] == [2001, 2002, 2003]
    assert [
        phase_4_constants["SPRITE_CHIKORITA"],
        phase_4_constants["SPRITE_CYNDAQUIL"],
        phase_4_constants["SPRITE_TOTODILE"],
    ] == [0xA3, 0xA4, 0xA5]
    assert phase_4_constants["NUM_POKEMON_SPRITES"] == 38


def test_compiled_phase_4_sprite_table_extends_only_the_custom_rom(
    repo_root: Path, phase_4_constants: dict[str, int]
) -> None:
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_start = custom_symbols["SpriteMons"].rom_offset
    custom_end = custom_symbols["OutdoorSprites"].rom_offset
    custom_table = custom.slice(custom_start, custom_end - custom_start)
    assert len(custom_table) == phase_4_constants["NUM_POKEMON_SPRITES"]
    assert custom_table[-3:] == bytes(
        phase_4_constants[name] for name in ("CHIKORITA", "CYNDAQUIL", "TOTODILE")
    )

    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_start = reference_symbols["SpriteMons"].rom_offset
    reference_end = reference_symbols["OutdoorSprites"].rom_offset
    assert reference_end - reference_start == 35
    assert custom_table[:35] == reference.slice(reference_start, 35)


def test_compiled_ilex_chikorita_object_and_script_match_the_contract(
    repo_root: Path, phase_4_constants: dict[str, int]
) -> None:
    custom_events = _object_events(
        repo_root,
        "crystallegends.gbc",
        "crystallegends.sym",
        "IlexForest_MapEvents",
        phase_4_constants,
    )
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    matching = [
        event
        for event in custom_events
        if (event.x, event.y) == (9, 23)
        and event.sprite == phase_4_constants["SPRITE_CHIKORITA"]
        and event.script_pointer == symbols["IlexForestChikoritaScript"].address
    ]
    assert len(custom_events) == 12
    assert len(matching) == 1
    event = matching[0]
    assert event.movement == phase_4_constants["SPRITEMOVEDATA_POKEMON"]
    assert event.radius == 0
    assert event.palette_and_type == (
        phase_4_constants["PAL_NPC_GREEN"] << 4
        | phase_4_constants["OBJECTTYPE_SCRIPT"]
    )
    assert event.event_flag == phase_4_constants[
        "EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST"
    ]

    rom = RomImage.load(repo_root / "crystallegends.gbc")
    start = symbols["IlexForestChikoritaScript"].rom_offset
    end = symbols["MovementData_Farfetchd_Pos1_Pos2"].rom_offset
    script = rom.slice(start, end - start)
    check = bytes([phase_4_constants["checkevent_command"]]) + _pointer(
        phase_4_constants["EVENT_GOT_HM01_CUT"]
    )
    gift = bytes(
        [
            phase_4_constants["givepoke_command"],
            phase_4_constants["CHIKORITA"],
            14,
            phase_4_constants["NO_ITEM"],
            phase_4_constants["FALSE"],
        ]
    )
    full = (
        bytes([phase_4_constants["ifequal_command"], 2])
        + _pointer(symbols["IlexForestChikoritaScript.StorageFull"].address)
    )
    complete = bytes([phase_4_constants["setevent_command"]]) + _pointer(
        phase_4_constants["EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST"]
    )
    disappear = bytes(
        [phase_4_constants["disappear_command"], 13]
    )
    positions = [script.index(pattern) for pattern in (check, gift, full, complete, disappear)]
    assert positions == sorted(positions)

    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )
    assert "IlexForestChikoritaScript" not in reference_symbols
    reference_events = _object_events(
        repo_root,
        "pokecrystal11.gbc",
        "pokecrystal11.sym",
        "IlexForest_MapEvents",
        phase_4_constants,
    )
    assert len(reference_events) == 11


def test_compiled_burned_tower_cyndaquil_uses_callback_visibility(
    repo_root: Path, phase_4_constants: dict[str, int]
) -> None:
    custom_events = _object_events(
        repo_root,
        "crystallegends.gbc",
        "crystallegends.sym",
        "BurnedTowerB1F_MapEvents",
        phase_4_constants,
    )
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    matching = [
        event
        for event in custom_events
        if (event.x, event.y) == (10, 4)
        and event.sprite == phase_4_constants["SPRITE_CYNDAQUIL"]
        and event.script_pointer == symbols["BurnedTowerB1FCyndaquilScript"].address
    ]
    assert len(custom_events) == 10
    assert len(matching) == 1
    event = matching[0]
    assert event.movement == phase_4_constants["SPRITEMOVEDATA_POKEMON"]
    assert event.palette_and_type == (
        phase_4_constants["PAL_NPC_RED"] << 4
        | phase_4_constants["OBJECTTYPE_SCRIPT"]
    )
    assert event.event_flag == 0xFFFF

    rom = RomImage.load(repo_root / "crystallegends.gbc")
    start = symbols["BurnedTowerB1FCyndaquilScript"].rom_offset
    end = symbols["BurnedTowerB1FEusine"].rom_offset
    script = rom.slice(start, end - start)
    check = bytes([phase_4_constants["checkevent_command"]]) + _pointer(
        phase_4_constants["EVENT_RELEASED_THE_BEASTS"]
    )
    gift = bytes(
        [
            phase_4_constants["givepoke_command"],
            phase_4_constants["CYNDAQUIL"],
            19,
            phase_4_constants["NO_ITEM"],
            phase_4_constants["FALSE"],
        ]
    )
    full = (
        bytes([phase_4_constants["ifequal_command"], 2])
        + _pointer(symbols["BurnedTowerB1FCyndaquilScript.StorageFull"].address)
    )
    complete = bytes([phase_4_constants["setevent_command"]]) + _pointer(
        phase_4_constants["EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER"]
    )
    disappear = bytes([phase_4_constants["disappear_command"], 11])
    positions = [script.index(pattern) for pattern in (check, gift, full, complete, disappear)]
    assert positions == sorted(positions)

    callback_start = symbols["BurnedTowerB1FCyndaquilCallback"].rom_offset
    callback_end = symbols["ReleaseTheBeasts"].rom_offset
    callback = rom.slice(callback_start, callback_end - callback_start)
    assert callback.index(
        bytes([phase_4_constants["checkevent_command"]])
        + _pointer(phase_4_constants["EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER"])
    ) < callback.index(
        bytes([phase_4_constants["checkevent_command"]])
        + _pointer(phase_4_constants["EVENT_RELEASED_THE_BEASTS"])
    )
    assert bytes([phase_4_constants["appear_command"], 11]) in callback
    assert bytes([phase_4_constants["disappear_command"], 11]) in callback

    release_start = symbols["ReleaseTheBeasts"].rom_offset
    release_end = symbols["BurnedTowerB1FCyndaquilScript"].rom_offset
    release = rom.slice(release_start, release_end - release_start)
    release_event = bytes([phase_4_constants["setevent_command"]]) + _pointer(
        phase_4_constants["EVENT_RELEASED_THE_BEASTS"]
    )
    appear = bytes([phase_4_constants["appear_command"], 11])
    assert release.index(release_event) < release.index(appear)

    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )
    assert "BurnedTowerB1FCyndaquilScript" not in reference_symbols
    assert "BurnedTowerB1FCyndaquilCallback" not in reference_symbols
    reference_events = _object_events(
        repo_root,
        "pokecrystal11.gbc",
        "pokecrystal11.sym",
        "BurnedTowerB1F_MapEvents",
        phase_4_constants,
    )
    assert len(reference_events) == 9
