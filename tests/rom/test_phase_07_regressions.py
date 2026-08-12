from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import (
    RomImage,
    decode_background_events,
    decode_object_events,
)
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase7]


@pytest.fixture(scope="module")
def phase_7_constants(repo_root: Path, tmp_path_factory) -> dict[str, int]:
    return resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_7_rom_constants"),
        [
            "EVENT_PROJECT_MEW_DATA_SENT",
            "EVENT_PROJECT_MEW_RESOLVED",
            "EVENT_PROJECT_MEW_TRANSFORMED",
            "EVENT_CAUGHT_PROJECT_MEW_SUBJECT",
            "NUM_EVENTS",
            "BATTLERESULT_CAUGHT_POKEMON",
            "SPRITE_MEW",
            "SPRITE_MEWTWO",
            "NUM_POKEMON_SPRITES",
            "MEW",
            "MEWTWO",
            "GROUP_RADIO_TOWER_TRANSMITTER_ANNEX",
            "MAP_RADIO_TOWER_TRANSMITTER_ANNEX",
            "GROUP_RADIO_TOWER_5F",
            "MAP_RADIO_TOWER_5F",
            "RADIO_TOWER_TRANSMITTER_ANNEX_WIDTH",
            "RADIO_TOWER_TRANSMITTER_ANNEX_HEIGHT",
            "WARP_EVENT_SIZE",
            "COORD_EVENT_SIZE",
            "BG_EVENT_SIZE",
            "OBJECT_EVENT_SIZE",
            "BGEVENT_UP",
            "SPRITEMOVEDATA_POKEMON",
            "loadwildmon_command",
            "startbattle_command",
            "reloadmapafterbattle_command",
            "special_command",
            "setevent_command",
            "disappear_command",
        ],
    )


def _warp_events(
    rom: RomImage,
    symbols: SymbolTable,
    label: str,
    warp_size: int,
) -> list[tuple[int, int, int, int, int]]:
    assert warp_size == 5
    offset = symbols[label].rom_offset + 2
    count = rom.u8(offset)
    offset += 1
    return [
        tuple(rom.slice(offset + index * warp_size, warp_size))
        for index in range(count)
    ]


def test_compiled_phase_7_ids_append_without_expanding_save_layout(
    repo_root: Path, phase_7_constants: dict[str, int]
) -> None:
    assert [
        phase_7_constants["EVENT_PROJECT_MEW_DATA_SENT"],
        phase_7_constants["EVENT_PROJECT_MEW_RESOLVED"],
        phase_7_constants["EVENT_PROJECT_MEW_TRANSFORMED"],
        phase_7_constants["EVENT_CAUGHT_PROJECT_MEW_SUBJECT"],
    ] == [2007, 2008, 2009, 2010]
    assert phase_7_constants["NUM_EVENTS"] == 2048
    assert phase_7_constants["BATTLERESULT_CAUGHT_POKEMON"] == 6
    assert [
        phase_7_constants["SPRITE_MEW"],
        phase_7_constants["SPRITE_MEWTWO"],
    ] == [0xA9, 0xAA]
    assert phase_7_constants["NUM_POKEMON_SPRITES"] == 43
    assert [
        phase_7_constants["GROUP_RADIO_TOWER_TRANSMITTER_ANNEX"],
        phase_7_constants["MAP_RADIO_TOWER_TRANSMITTER_ANNEX"],
    ] == [3, 92]
    assert [
        phase_7_constants["RADIO_TOWER_TRANSMITTER_ANNEX_WIDTH"],
        phase_7_constants["RADIO_TOWER_TRANSMITTER_ANNEX_HEIGHT"],
    ] == [5, 4]

    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    assert symbols["wCurBox"].address - symbols["wEventFlags"].address == 256


def test_compiled_annex_asset_and_sprite_table_match_source(
    repo_root: Path, phase_7_constants: dict[str, int]
) -> None:
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    block_source = (repo_root / "maps/RadioTowerTransmitterAnnex.blk").read_bytes()
    assert rom.at(symbols["RadioTowerTransmitterAnnex_Blocks"], 20) == block_source

    start = symbols["SpriteMons"].rom_offset
    end = symbols["OutdoorSprites"].rom_offset
    table = rom.slice(start, end - start)
    assert len(table) == phase_7_constants["NUM_POKEMON_SPRITES"]
    assert table[-2:] == bytes(
        [phase_7_constants["MEW"], phase_7_constants["MEWTWO"]]
    )


def test_compiled_5f_and_annex_warps_are_reciprocal(
    repo_root: Path, phase_7_constants: dict[str, int]
) -> None:
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    size = phase_7_constants["WARP_EVENT_SIZE"]
    radio_warps = _warp_events(rom, symbols, "RadioTower5F_MapEvents", size)
    annex_warps = _warp_events(
        rom, symbols, "RadioTowerTransmitterAnnex_MapEvents", size
    )

    assert radio_warps[-1] == (
        0,
        14,
        1,
        phase_7_constants["GROUP_RADIO_TOWER_TRANSMITTER_ANNEX"],
        phase_7_constants["MAP_RADIO_TOWER_TRANSMITTER_ANNEX"],
    )
    assert annex_warps == [
        (
            7,
            4,
            3,
            phase_7_constants["GROUP_RADIO_TOWER_5F"],
            phase_7_constants["MAP_RADIO_TOWER_5F"],
        )
    ]


def test_compiled_annex_terminal_monitor_and_subject_objects(
    repo_root: Path, phase_7_constants: dict[str, int]
) -> None:
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    backgrounds = decode_background_events(
        rom,
        symbols,
        "RadioTowerTransmitterAnnex_MapEvents",
        phase_7_constants["WARP_EVENT_SIZE"],
        phase_7_constants["COORD_EVENT_SIZE"],
        phase_7_constants["BG_EVENT_SIZE"],
    )
    objects = decode_object_events(
        rom,
        symbols,
        "RadioTowerTransmitterAnnex_MapEvents",
        phase_7_constants["WARP_EVENT_SIZE"],
        phase_7_constants["COORD_EVENT_SIZE"],
        phase_7_constants["BG_EVENT_SIZE"],
        phase_7_constants["OBJECT_EVENT_SIZE"],
    )

    assert [
        (event.x, event.y, event.event_type, event.script_pointer)
        for event in backgrounds
    ] == [
        (
            2,
            1,
            phase_7_constants["BGEVENT_UP"],
            symbols["RadioTowerTransmitterAnnexUploadMonitorScript"].address,
        ),
        (
            6,
            1,
            phase_7_constants["BGEVENT_UP"],
            symbols["RadioTowerTransmitterAnnexTerminalScript"].address,
        ),
    ]
    assert [(event.x, event.y) for event in objects] == [(4, 4), (4, 4)]
    assert [event.sprite for event in objects] == [
        phase_7_constants["SPRITE_MEW"],
        phase_7_constants["SPRITE_MEWTWO"],
    ]
    assert [event.movement for event in objects] == [
        phase_7_constants["SPRITEMOVEDATA_POKEMON"],
        phase_7_constants["SPRITEMOVEDATA_POKEMON"],
    ]
    assert [event.script_pointer for event in objects] == [
        symbols["RadioTowerTransmitterAnnexMewScript"].address,
        symbols["RadioTowerTransmitterAnnexMewtwoScript"].address,
    ]
    assert all(event.event_flag == 0xFFFF for event in objects)


def test_reference_rom_exports_no_phase_7_map_or_scripts(repo_root: Path) -> None:
    symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())
    for label in (
        "RadioTowerTransmitterAnnex_MapScripts",
        "RadioTowerTransmitterAnnex_MapEvents",
        "RadioTowerTransmitterAnnex_Blocks",
        "RadioTower5FProjectMewScene",
        "RadioTower5FProjectMewEntranceCallback",
    ):
        assert label not in symbols


def test_compiled_generic_caught_special_is_appended_and_targets_shared_query(
    repo_root: Path,
) -> None:
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    special = custom_symbols["CheckCaughtPokemonSpecial"]
    query = custom_symbols["CheckCaughtPokemon"]

    assert rom.at(special, 3) == bytes(
        [query.bank, query.address & 0xFF, query.address >> 8]
    )
    assert query.address == custom_symbols["CheckCaughtCelebi"].address
    assert "CheckCaughtPokemonSpecial" not in reference_symbols
    assert "CheckCaughtPokemon" not in reference_symbols
    assert custom_symbols["CheckCaughtCelebiSpecial"].address == reference_symbols[
        "CheckCaughtCelebiSpecial"
    ].address


@pytest.mark.parametrize(
    ("species", "script", "end", "object_id"),
    [
        ("MEW", "RadioTowerTransmitterAnnexMewScript.Resolved", "RadioTowerTransmitterAnnexMewScript.NotCaught", 2),
        ("MEWTWO", "RadioTowerTransmitterAnnexMewtwoScript", "RadioTowerTransmitterAnnexMewtwoScript.NotCaught", 3),
    ],
)
def test_compiled_subject_encounters_use_level_30_and_capture_only_removal(
    repo_root: Path,
    phase_7_constants: dict[str, int],
    species: str,
    script: str,
    end: str,
    object_id: int,
) -> None:
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    start_offset = symbols[script].rom_offset
    end_offset = symbols[end].rom_offset
    compiled = rom.slice(start_offset, end_offset - start_offset)
    special_id = (
        symbols["CheckCaughtPokemonSpecial"].address
        - symbols["SpecialsPointers"].address
    ) // 3
    encounter = bytes(
        [
            phase_7_constants["loadwildmon_command"],
            phase_7_constants[species],
            30,
            phase_7_constants["startbattle_command"],
            phase_7_constants["reloadmapafterbattle_command"],
            phase_7_constants["special_command"],
        ]
    ) + special_id.to_bytes(2, "little")
    caught = (
        bytes([phase_7_constants["setevent_command"]])
        + phase_7_constants["EVENT_CAUGHT_PROJECT_MEW_SUBJECT"].to_bytes(
            2, "little"
        )
        + bytes([phase_7_constants["disappear_command"], object_id])
    )

    assert encounter in compiled
    assert caught in compiled
