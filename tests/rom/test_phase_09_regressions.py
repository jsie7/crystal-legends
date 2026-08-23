from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import (
    RomImage,
    decode_background_events,
    decode_object_events,
)
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase9]


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (
            repo_root / "tests/fixtures/scenarios/phase_09_kanto_completion.json"
        ).read_text()
    )


@pytest.fixture(scope="module")
def phase_9_constants(repo_root: Path, tmp_path_factory) -> dict[str, int]:
    return resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_9_rom_constants"),
        [
            "BLAINES_LOG",
            "CANT_SELECT",
            "CANT_TOSS",
            "COLL_FLOOR",
            "COLL_HOP_DOWN",
            "COLL_ICE",
            "COLL_DOOR",
            "COLL_WATER",
            "COLL_WATER_21",
            "COLL_WALL",
            "COLL_WARP_CARPET_LEFT",
            "COLL_WARP_CARPET_RIGHT",
            "COLL_WARP_CARPET_DOWN",
            "EVENT_BEAT_ELITE_FOUR",
            "EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION",
            "EVENT_ARTICUNO_AVAILABLE",
            "EVENT_CAUGHT_ARTICUNO_IN_KANTO",
            "EVENT_CAUGHT_MOLTRES_IN_KANTO",
            "EVENT_CAUGHT_ZAPDOS_IN_KANTO",
            "EVENT_GOT_BULBASAUR_FROM_ERIKA",
            "EVENT_GOT_CHARMANDER_FROM_BLAINE",
            "EVENT_GOT_SQUIRTLE_FROM_MISTY",
            "EVENT_HELPED_ERIKA_CLEAN_CELADON_POND",
            "EVENT_ERIKA_REQUESTED_CELADON_POND_HELP",
            "EVENT_BLAINE_REQUESTED_CINNABAR_HELP",
            "EVENT_SEAFOAM_ISLANDS_CAVE_ULTRA_BALL",
            "EVENT_SEAFOAM_ISLANDS_CAVE_HIDDEN_NEVERMELTICE",
            "EVENT_POWER_PLANT_GENERATOR_ANNEX_MAGNET",
            "EVENT_GOT_ARTICUNO_FROM_ELM",
            "EVENT_GOT_MOLTRES_FROM_ELM",
            "EVENT_GOT_ZAPDOS_FROM_ELM",
            "EVENT_MOLTRES_NOT_AT_KANTO_LOCATION",
            "EVENT_MOLTRES_AVAILABLE",
            "EVENT_OAK_MOVED_THIRD_BIRD",
            "EVENT_OPENED_POWER_PLANT_ANNEX",
            "EVENT_POWER_PLANT_ANNEX_AUTHORIZED",
            "EVENT_RECOVERED_BLAINES_LOG",
            "EVENT_SAFARI_ZONE_ACCESSIBLE",
            "EVENT_SAFARI_ZONE_BETA_ULTRA_BALL",
            "EVENT_SAFARI_ZONE_BETA_MAX_REVIVE",
            "EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION",
            "EVENT_ZAPDOS_AVAILABLE",
            "EVENT_RESTORED_POWER_TO_KANTO",
            "GROUP_FUCHSIA_CITY",
            "MAP_FUCHSIA_CITY",
            "GROUP_SAFARI_ZONE_FUCHSIA_GATE_BETA",
            "MAP_SAFARI_ZONE_FUCHSIA_GATE_BETA",
            "GROUP_SAFARI_ZONE_BETA",
            "MAP_SAFARI_ZONE_BETA",
            "GROUP_SEAFOAM_ISLANDS_CAVE",
            "MAP_SEAFOAM_ISLANDS_CAVE",
            "GROUP_RADIO_TOWER_TRANSMITTER_ANNEX",
            "MAP_RADIO_TOWER_TRANSMITTER_ANNEX",
            "GROUP_ROUTE_20",
            "MAP_ROUTE_20",
            "GROUP_SEAFOAM_GYM",
            "MAP_SEAFOAM_GYM",
            "GROUP_POWER_PLANT",
            "MAP_POWER_PLANT",
            "GROUP_POWER_PLANT_GENERATOR_ANNEX",
            "MAP_POWER_PLANT_GENERATOR_ANNEX",
            "GROUP_VICTORY_ROAD",
            "MAP_VICTORY_ROAD",
            "TILESET_PARK",
            "TILESET_ICE_PATH",
            "TILESET_FACILITY",
            "ROUTE",
            "CAVE",
            "INDOOR",
            "LANDMARK_FUCHSIA_CITY",
            "LANDMARK_SEAFOAM_ISLANDS",
            "LANDMARK_POWER_PLANT",
            "MUSIC_NATIONAL_PARK",
            "MUSIC_EVOLUTION",
            "MUSIC_UNION_CAVE",
            "MUSIC_VIRIDIAN_CITY",
            "PALETTE_AUTO",
            "PALETTE_DAY",
            "PALETTE_NITE",
            "FISHGROUP_SHORE",
            "FISHGROUP_OCEAN",
            "TRUE",
            "FALSE",
            "MAP_LENGTH",
            "BGEVENT_READ",
            "BGEVENT_RIGHT",
            "BGEVENT_ITEM",
            "HELD_NONE",
            "SPRITE_BOULDER",
            "ITEMATTR_STRUCT_LENGTH",
            "ITEMMENU_NOUSE",
            "ITEM_NAME_LENGTH",
            "KEY_ITEM",
            "NUM_EVENTS",
            "NUM_ITEMS",
            "OBJECTTYPE_SCRIPT",
            "OBJECTTYPE_ITEMBALL",
            "OBJECT_EVENT_SIZE",
            "BG_EVENT_SIZE",
            "COORD_EVENT_SIZE",
            "SPRITEMOVEDATA_STILL",
            "SPRITEMOVEDATA_POKEMON",
            "SPRITE_LASS",
            "SPRITE_MOLTRES",
            "SPRITE_POKE_BALL",
            "SPRITE_ROCK",
            "PAL_NPC_BLUE",
            "PAL_NPC_BROWN",
            "PAL_NPC_RED",
            "ARTICUNO",
            "ZAPDOS",
            "MOLTRES",
            "MAGNET",
            "ULTRA_BALL",
            "NEVERMELTICE",
            "MANKEY",
            "MAREEP",
            "VULPIX",
            "EXEGGCUTE",
            "TAUROS",
            "SCYTHER",
            "PINSIR",
            "CHANSEY",
            "KANGASKHAN",
            "REMORAID",
            "OCTILLERY",
            "WARP_EVENT_SIZE",
            "farsjump_command",
            "loadwildmon_command",
            "startbattle_command",
            "special_command",
            "setevent_command",
            "disappear_command",
            "reloadmapafterbattle_command",
        ],
    )


def test_compiled_phase_9_ids_do_not_expand_the_save_layout(
    repo_root: Path, phase_9_constants: dict[str, int]
) -> None:
    constants = phase_9_constants
    assert constants["EVENT_HELPED_ERIKA_CLEAN_CELADON_POND"] == 2015
    assert constants["EVENT_GOT_BULBASAUR_FROM_ERIKA"] == 2019
    assert constants["EVENT_GOT_SQUIRTLE_FROM_MISTY"] == 2020
    assert constants["EVENT_GOT_CHARMANDER_FROM_BLAINE"] == 2021
    assert constants["EVENT_SAFARI_ZONE_ACCESSIBLE"] == 2022
    assert constants["EVENT_SAFARI_ZONE_BETA_ULTRA_BALL"] == 2023
    assert constants["EVENT_SAFARI_ZONE_BETA_MAX_REVIVE"] == 2024
    assert constants["EVENT_POWER_PLANT_ANNEX_AUTHORIZED"] == 2025
    assert constants["EVENT_OPENED_POWER_PLANT_ANNEX"] == 2026
    assert constants["EVENT_CAUGHT_ARTICUNO_IN_KANTO"] == 2027
    assert constants["EVENT_CAUGHT_ZAPDOS_IN_KANTO"] == 2028
    assert constants["EVENT_CAUGHT_MOLTRES_IN_KANTO"] == 2029
    assert constants["EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION"] == 2030
    assert constants["EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION"] == 2031
    assert constants["EVENT_MOLTRES_NOT_AT_KANTO_LOCATION"] == 2032
    assert constants["EVENT_ERIKA_REQUESTED_CELADON_POND_HELP"] == 2033
    assert constants["EVENT_BLAINE_REQUESTED_CINNABAR_HELP"] == 2034
    assert constants["EVENT_SEAFOAM_ISLANDS_CAVE_ULTRA_BALL"] == 2035
    assert constants["EVENT_SEAFOAM_ISLANDS_CAVE_HIDDEN_NEVERMELTICE"] == 2036
    assert constants["EVENT_POWER_PLANT_GENERATOR_ANNEX_MAGNET"] == 2037
    assert constants["NUM_EVENTS"] == 2048

    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    assert symbols["wCurBox"].address - symbols["wEventFlags"].address == 256


def test_compiled_blaines_log_occupies_b0_without_shifting_item_tables(
    repo_root: Path, phase_9_constants: dict[str, int]
) -> None:
    constants = phase_9_constants
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())

    item = constants["BLAINES_LOG"]
    assert item == 0xB0
    width = constants["ITEMATTR_STRUCT_LENGTH"]
    attributes = custom.slice(
        custom_symbols["ItemAttributes"].rom_offset + (item - 1) * width, width
    )
    assert int.from_bytes(attributes[:2], "little") == 0
    assert attributes[2] == constants["HELD_NONE"]
    assert attributes[3] == 0
    assert attributes[4] == constants["CANT_SELECT"] | constants["CANT_TOSS"]
    assert attributes[5] == constants["KEY_ITEM"]
    assert attributes[6] >> 4 == constants["ITEMMENU_NOUSE"]
    assert attributes[6] & 0xF == constants["ITEMMENU_NOUSE"]

    description_pointer = custom.u16le(
        custom_symbols["ItemDescriptions"].rom_offset + (item - 1) * 2
    )
    assert description_pointer == custom_symbols["BlainesLogDesc"].address
    effect_pointer = custom.u16le(
        custom_symbols["ItemEffects"].rom_offset + (item - 1) * 2
    )
    assert effect_pointer == custom_symbols["NoEffect"].address

    def item_names(rom: RomImage, symbols: SymbolTable) -> list[bytes]:
        offset = symbols["ItemNames"].rom_offset
        names: list[bytes] = []
        for _ in range(constants["NUM_ITEMS"]):
            end = rom.data.index(0x50, offset)
            names.append(rom.slice(offset, end - offset))
            offset = end + 1
        return names

    custom_names = item_names(custom, custom_symbols)
    reference_names = item_names(reference, reference_symbols)
    slot = item - 1
    assert custom_names[:slot] == reference_names[:slot]
    assert custom_names[slot + 1 :] == reference_names[slot + 1 :]
    assert custom_names[slot] != reference_names[slot]


def test_compiled_cinnabar_assets_are_custom_replacements_only(
    repo_root: Path, phase_9_constants: dict[str, int], scenario: dict
) -> None:
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())

    custom_blocks = (repo_root / "maps/CinnabarIslandCrystalLegends.blk").read_bytes()
    stock_blocks = (repo_root / "maps/CinnabarIsland.blk").read_bytes()
    assert custom.at(custom_symbols["CinnabarIsland_Blocks"], 90) == custom_blocks
    assert reference.at(reference_symbols["CinnabarIsland_Blocks"], 90) == stock_blocks

    custom_meta = (
        repo_root / "data/tilesets/kanto_metatiles_crystallegends.bin"
    ).read_bytes()
    stock_meta = (repo_root / "data/tilesets/kanto_metatiles.bin").read_bytes()
    assert (
        custom.at(custom_symbols["TilesetKantoMeta"], len(custom_meta))
        == custom_meta
    )
    assert (
        reference.at(reference_symbols["TilesetKantoMeta"], len(stock_meta))
        == stock_meta
    )
    assert custom_symbols["TilesetKantoMeta"].rom_offset - custom_symbols[
        "TilesetKantoGFX"
    ].rom_offset == reference_symbols["TilesetKantoMeta"].rom_offset - reference_symbols[
        "TilesetKantoGFX"
    ].rom_offset

    staircase_block = scenario["blaines_log"]["staircase"]["custom_block"]
    assert custom.slice(
        custom_symbols["TilesetKantoColl"].rom_offset + staircase_block * 4,
        4,
    ) == bytes(
        [
            phase_9_constants[f"COLL_{collision}"]
            for collision in scenario["blaines_log"]["staircase"]["collision"]
        ]
    )
    assert reference.slice(
        reference_symbols["TilesetKantoColl"].rom_offset + staircase_block * 4,
        4,
    ) != bytes(
        [
            phase_9_constants[f"COLL_{collision}"]
            for collision in scenario["blaines_log"]["staircase"]["collision"]
        ]
    )
    gate = scenario["safari"]["fuchsia_gate"]
    assert custom.slice(
        custom_symbols["TilesetKantoColl"].rom_offset + gate["open_block"] * 4,
        4,
    ) == bytes(
        [
            phase_9_constants[f"COLL_{collision}"]
            for collision in gate["open_collision"]
        ]
    )
    assert reference.slice(
        reference_symbols["TilesetKantoColl"].rom_offset + gate["open_block"] * 4,
        4,
    ) != bytes(
        [
            phase_9_constants[f"COLL_{collision}"]
            for collision in gate["open_collision"]
        ]
    )


def test_compiled_cinnabar_case_event_matches_the_locked_coordinate(
    repo_root: Path, phase_9_constants: dict[str, int], scenario: dict
) -> None:
    constants = phase_9_constants
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())

    custom_objects = decode_object_events(
        custom,
        custom_symbols,
        "CinnabarIsland_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
        constants["OBJECT_EVENT_SIZE"],
    )
    reference_objects = decode_object_events(
        reference,
        reference_symbols,
        "CinnabarIsland_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
        constants["OBJECT_EVENT_SIZE"],
    )
    assert len(custom_objects) == 5
    assert len(reference_objects) == 1
    boulder = custom_objects[1]
    assert (boulder.x, boulder.y) == tuple(
        scenario["blaines_log"]["case_coordinate"]
    )
    assert boulder.sprite == constants["SPRITE_BOULDER"]
    assert boulder.movement == constants["SPRITEMOVEDATA_STILL"]
    assert boulder.palette_and_type >> 4 == constants["PAL_NPC_BROWN"]
    assert boulder.palette_and_type & 0xF == constants["OBJECTTYPE_SCRIPT"]
    assert (
        boulder.script_pointer
        == custom_symbols["CinnabarIslandBlainesLogRubble"].address
    )
    assert boulder.event_flag == 0xFFFF

    decorative_boulders = custom_objects[2:]
    assert [(rock.x, rock.y) for rock in decorative_boulders] == [
        tuple(coordinate)
        for coordinate in scenario["blaines_log"]["decorative_rock_coordinates"]
    ]
    for rock in decorative_boulders:
        assert rock.sprite == constants["SPRITE_BOULDER"]
        assert rock.movement == constants["SPRITEMOVEDATA_STILL"]
        assert rock.palette_and_type >> 4 == constants["PAL_NPC_BROWN"]
        assert rock.palette_and_type & 0xF == constants["OBJECTTYPE_SCRIPT"]
        assert (
            rock.script_pointer
            == custom_symbols["CinnabarIslandDecorativeBoulder"].address
        )
        assert rock.event_flag == 0xFFFF

    backgrounds = decode_background_events(
        custom,
        custom_symbols,
        "CinnabarIsland_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
    )
    reference_backgrounds = decode_background_events(
        reference,
        reference_symbols,
        "CinnabarIsland_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
    )
    assert [
        (event.x, event.y, event.event_type) for event in backgrounds
    ] == [
        (event.x, event.y, event.event_type) for event in reference_backgrounds
    ]


def test_compiled_phase_9_starter_labels_are_custom_only(repo_root: Path) -> None:
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())
    labels = {
        "BlainesLogDesc",
        "ErikaBulbasaurOfferText",
        "MistySquirtleOfferText",
        "BlaineCharmanderOfferText",
        "CeladonCityMukPondEntry",
        "CeladonCityMukPondEncounter",
        "CinnabarIslandDecorativeBoulder",
        "CinnabarIslandBlainesLogRubble",
        "ErikaStarterOTName",
        "MistyStarterOTName",
        "BlaineStarterOTName",
        "SetLatestStarterOT",
    }
    assert all(label in custom_symbols for label in labels)
    assert all(label not in reference_symbols for label in labels)


def _decode_warps(
    rom: RomImage,
    symbols: SymbolTable,
    map_events_label: str,
    warp_event_size: int,
) -> list[tuple[int, int, int, int, int]]:
    assert warp_event_size == 5
    offset = symbols[map_events_label].rom_offset + 2
    count = rom.u8(offset)
    offset += 1
    return [
        (
            rom.u8(offset + index * warp_event_size + 1),
            rom.u8(offset + index * warp_event_size),
            rom.u8(offset + index * warp_event_size + 2),
            rom.u8(offset + index * warp_event_size + 3),
            rom.u8(offset + index * warp_event_size + 4),
        )
        for index in range(count)
    ]


def test_compiled_safari_blocks_metadata_and_warps_are_variant_safe(
    repo_root: Path, phase_9_constants: dict[str, int], scenario: dict
) -> None:
    constants = phase_9_constants
    safari = scenario["safari"]
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())

    custom_blocks = (repo_root / safari["preserve"]["custom_block_path"]).read_bytes()
    stock_blocks = (repo_root / safari["preserve"]["stock_block_path"]).read_bytes()
    assert custom.at(custom_symbols["SafariZoneBeta_Blocks"], 180) == custom_blocks
    assert reference.at(reference_symbols["SafariZoneBeta_Blocks"], 180) == stock_blocks

    extra_metatiles = (
        repo_root / safari["preserve"]["custom_metatile_path"]
    ).read_bytes()
    assert custom.at(
        custom_symbols["TilesetParkCrystalLegendsExtraMeta"], len(extra_metatiles)
    ) == extra_metatiles
    assert "TilesetParkCrystalLegendsExtraMeta" not in reference_symbols

    water_block = safari["preserve"]["water_collision"]["block"]
    custom_water = constants[
        f'COLL_{safari["preserve"]["water_collision"]["custom"]}'
    ]
    reference_water = constants[
        f'COLL_{safari["preserve"]["water_collision"]["reference"]}'
    ]
    assert custom.slice(
        custom_symbols["TilesetParkColl"].rom_offset + water_block * 4, 4
    ) == bytes([custom_water] * 4)
    assert reference.slice(
        reference_symbols["TilesetParkColl"].rom_offset + water_block * 4, 4
    ) == bytes([reference_water] * 4)

    first_custom, last_custom = safari["preserve"]["custom_metatile_range"]
    assert len(extra_metatiles) == (last_custom - first_custom + 1) * 16
    custom_collision_bytes = custom.slice(
        custom_symbols["TilesetParkColl"].rom_offset + first_custom * 4,
        (last_custom - first_custom + 1) * 4,
    )
    assert custom_collision_bytes[: 8 * 4] == bytes([custom_water] * 8 * 4)
    assert custom_collision_bytes[8 * 4 :] == bytes(
        [
            constants["COLL_FLOOR"],
            constants["COLL_WALL"],
            constants["COLL_FLOOR"],
            constants["COLL_FLOOR"],
            constants["COLL_FLOOR"],
            constants["COLL_FLOOR"],
            constants["COLL_FLOOR"],
            constants["COLL_WARP_CARPET_DOWN"],
            constants["COLL_FLOOR"],
            constants["COLL_FLOOR"],
            constants["COLL_WARP_CARPET_DOWN"],
            constants["COLL_FLOOR"],
        ]
    )

    map_index = constants["MAP_SAFARI_ZONE_BETA"] - 1
    custom_record = custom.slice(
        custom_symbols["MapGroup_Dungeons"].rom_offset
        + map_index * constants["MAP_LENGTH"],
        constants["MAP_LENGTH"],
    )
    reference_record = reference.slice(
        reference_symbols["MapGroup_Dungeons"].rom_offset
        + map_index * constants["MAP_LENGTH"],
        constants["MAP_LENGTH"],
    )
    assert custom_record[1] == reference_record[1] == constants["TILESET_PARK"]
    assert custom_record[2] == constants["ROUTE"]
    assert reference_record[2] == constants["CAVE"]
    assert custom_record[5] == reference_record[5] == constants["LANDMARK_FUCHSIA_CITY"]
    assert custom_record[6] == constants["MUSIC_NATIONAL_PARK"]
    assert reference_record[6] == constants["MUSIC_EVOLUTION"]
    assert custom_record[7] & 0xF == reference_record[7] & 0xF == constants["PALETTE_AUTO"]
    assert custom_record[8] == reference_record[8] == constants["FISHGROUP_SHORE"]

    def expected_warps(records: list[list[int | str]]) -> list[tuple[int, int, int, int, int]]:
        return [
            (
                x,
                y,
                destination_warp,
                constants[f"GROUP_{destination}"],
                constants[f"MAP_{destination}"],
            )
            for x, y, destination, destination_warp in records
        ]

    for rom, symbols in (
        (custom, custom_symbols),
        (reference, reference_symbols),
    ):
        assert _decode_warps(
            rom,
            symbols,
            "SafariZoneFuchsiaGateBeta_MapEvents",
            constants["WARP_EVENT_SIZE"],
        ) == expected_warps(safari["maintenance_gate"]["warps"])
        assert _decode_warps(
            rom,
            symbols,
            "SafariZoneBeta_MapEvents",
            constants["WARP_EVENT_SIZE"],
        ) == expected_warps(safari["preserve"]["warps"])


def test_compiled_safari_events_keep_the_gate_empty_and_only_two_item_objects(
    repo_root: Path, phase_9_constants: dict[str, int], scenario: dict
) -> None:
    constants = phase_9_constants
    safari = scenario["safari"]
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())

    gate_backgrounds = decode_background_events(
        custom,
        symbols,
        "SafariZoneFuchsiaGateBeta_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
    )
    preserve_backgrounds = decode_background_events(
        custom,
        symbols,
        "SafariZoneBeta_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
    )
    assert [(event.x, event.y) for event in gate_backgrounds] == [
        tuple(coordinate) for coordinate in safari["maintenance_gate"]["notice_coordinates"]
    ]
    assert [(event.x, event.y) for event in preserve_backgrounds] == [
        tuple(coordinate) for coordinate in safari["preserve"]["sign_coordinates"]
    ]
    assert all(event.event_type == constants["BGEVENT_READ"] for event in gate_backgrounds)
    assert all(
        event.event_type == constants["BGEVENT_READ"] for event in preserve_backgrounds
    )

    gate_objects = decode_object_events(
        custom,
        symbols,
        "SafariZoneFuchsiaGateBeta_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
        constants["OBJECT_EVENT_SIZE"],
    )
    preserve_objects = decode_object_events(
        custom,
        symbols,
        "SafariZoneBeta_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
        constants["OBJECT_EVENT_SIZE"],
    )
    assert gate_objects == []
    assert len(preserve_objects) == 2
    for event, pickup in zip(preserve_objects, safari["preserve"]["pickups"], strict=True):
        assert (event.x, event.y) == tuple(pickup["coordinate"])
        assert event.sprite == constants["SPRITE_POKE_BALL"]
        assert event.movement == constants["SPRITEMOVEDATA_STILL"]
        assert event.palette_and_type & 0xF == constants["OBJECTTYPE_ITEMBALL"]
        assert event.script_pointer == symbols[pickup["script"]].address
        assert event.event_flag == constants[pickup["event"]]

    for label in (
        "SafariZoneFuchsiaGateBeta_MapEvents",
        "SafariZoneBeta_MapEvents",
    ):
        assert decode_background_events(
            reference,
            reference_symbols,
            label,
            constants["WARP_EVENT_SIZE"],
            constants["COORD_EVENT_SIZE"],
            constants["BG_EVENT_SIZE"],
        ) == []
        assert decode_object_events(
            reference,
            reference_symbols,
            label,
            constants["WARP_EVENT_SIZE"],
            constants["COORD_EVENT_SIZE"],
            constants["BG_EVENT_SIZE"],
            constants["OBJECT_EVENT_SIZE"],
        ) == []

    home_objects = decode_object_events(
        custom,
        symbols,
        "SafariZoneWardensHome_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
        constants["OBJECT_EVENT_SIZE"],
    )
    assert len(home_objects) == 1
    granddaughter = home_objects[0]
    assert (granddaughter.x, granddaughter.y) == tuple(
        safari["quest_owner"]["coordinate"]
    )
    assert granddaughter.sprite == constants["SPRITE_LASS"]
    assert granddaughter.script_pointer == symbols["WardensGranddaughter"].address


def test_compiled_safari_wild_records_match_every_locked_slot(
    repo_root: Path, phase_9_constants: dict[str, int], scenario: dict
) -> None:
    constants = phase_9_constants
    safari = scenario["safari"]
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())

    map_id = bytes(
        [constants["GROUP_SAFARI_ZONE_BETA"], constants["MAP_SAFARI_ZONE_BETA"]]
    )
    grass = map_id + bytes(rate * 255 // 100 for rate in safari["grass"]["rates"])
    grass += bytes(
        value
        for time in ("morning", "day", "night")
        for level, species in safari["grass"][time]
        for value in (level, constants[species])
    )
    grass_label = "KantoGrassWildMons._def_grass_wildmons_SAFARI_ZONE_BETA"
    assert rom.at(symbols[grass_label], len(grass)) == grass

    water = map_id + bytes([safari["water"]["rate"] * 255 // 100])
    water += bytes(
        value
        for level, species in safari["water"]["slots"]
        for value in (level, constants[species])
    )
    water_label = "KantoWaterWildMons._def_water_wildmons_SAFARI_ZONE_BETA"
    assert rom.at(symbols[water_label], len(water)) == water
    assert grass_label not in reference_symbols
    assert water_label not in reference_symbols


def test_compiled_safari_labels_are_custom_only(repo_root: Path) -> None:
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())
    labels = {
        "FuchsiaCitySafariGateCallback",
        "SafariZoneBetaUltraBall",
        "SafariZoneBetaMaxRevive",
        "WardensGranddaughterSoulBadgeText",
        "SafariZoneFuchsiaGateBetaNorthNotice",
    }
    assert all(label in custom_symbols for label in labels)
    assert all(label not in reference_symbols for label in labels)


def test_compiled_seafoam_reuses_the_beta_slot_and_has_custom_only_metadata(
    repo_root: Path, phase_9_constants: dict[str, int], scenario: dict
) -> None:
    constants = phase_9_constants
    seafoam = scenario["seafoam"]
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())

    active = (repo_root / seafoam["active_block_path"]).read_bytes()
    seed = (repo_root / seafoam["seed_block_path"]).read_bytes()
    active_route = (repo_root / seafoam["route20_active_block_path"]).read_bytes()
    stock_route = (repo_root / seafoam["route20_stock_block_path"]).read_bytes()
    assert (
        custom_symbols["SeafoamIslandsCave_Blocks"].bank,
        custom_symbols["SeafoamIslandsCave_Blocks"].address,
    ) == (
        custom_symbols["BetaUnionCave_Blocks"].bank,
        custom_symbols["BetaUnionCave_Blocks"].address,
    )
    assert custom.at(custom_symbols["SeafoamIslandsCave_Blocks"], 90) == active
    assert reference.at(reference_symbols["BetaUnionCave_Blocks"], 90) == seed
    assert custom.at(custom_symbols["Route20_Blocks"], 270) == active_route
    assert reference.at(reference_symbols["Route20_Blocks"], 270) == stock_route

    assert constants["GROUP_SEAFOAM_ISLANDS_CAVE"] == constants[
        "GROUP_RADIO_TOWER_TRANSMITTER_ANNEX"
    ]
    assert constants["MAP_SEAFOAM_ISLANDS_CAVE"] == (
        constants["MAP_RADIO_TOWER_TRANSMITTER_ANNEX"] + 1
    )
    map_record = custom.slice(
        custom_symbols["MapGroup_Dungeons"].rom_offset
        + (constants["MAP_SEAFOAM_ISLANDS_CAVE"] - 1) * constants["MAP_LENGTH"],
        constants["MAP_LENGTH"],
    )
    assert map_record[1] == constants["TILESET_ICE_PATH"]
    assert map_record[2] == constants["CAVE"]
    assert map_record[5] == constants["LANDMARK_SEAFOAM_ISLANDS"]
    assert map_record[6] == constants["MUSIC_UNION_CAVE"]
    assert map_record[7] >> 4 == constants["TRUE"]
    assert map_record[7] & 0xF == constants["PALETTE_NITE"]
    assert map_record[8] == constants["FISHGROUP_OCEAN"]

    stock_metatiles = (
        repo_root / "data/tilesets/ice_path_metatiles.bin"
    ).read_bytes()
    extra_metatiles = bytes(
        [
            0x9A, 0x19, 0x19, 0x9A,
            0x19, 0x9B, 0x19, 0x19,
            0x19, 0x19, 0x19, 0x19,
            0x42, 0x43, 0x19, 0x9B,
            0x9A, 0x19, 0x9A, 0x9A,
            0x19, 0x9A, 0x19, 0x19,
            0xC6, 0xC7, 0xC6, 0xC7,
            0xD6, 0xD7, 0xD6, 0xD7,
        ]
    )
    assert custom.at(
        custom_symbols["TilesetIcePathMeta"],
        len(stock_metatiles) + len(extra_metatiles),
    ) == stock_metatiles + extra_metatiles
    assert reference.at(
        reference_symbols["TilesetIcePathMeta"], len(stock_metatiles)
    ) == stock_metatiles
    custom_collision_size = (
        custom_symbols["TilesetPlayersRoomGFX"].rom_offset
        - custom_symbols["TilesetIcePathColl"].rom_offset
    )
    reference_collision_size = (
        reference_symbols["TilesetPlayersRoomGFX"].rom_offset
        - reference_symbols["TilesetIcePathColl"].rom_offset
    )
    assert custom_collision_size == 66 * 4
    assert reference_collision_size == 64 * 4
    assert custom.at(custom_symbols["TilesetIcePathColl"], custom_collision_size)[
        -8:
    ] == bytes(
        [
            constants["COLL_FLOOR"],
            constants["COLL_FLOOR"],
            constants["COLL_WARP_CARPET_DOWN"],
            constants["COLL_FLOOR"],
            constants["COLL_FLOOR"],
            constants["COLL_FLOOR"],
            constants["COLL_ICE"],
            constants["COLL_ICE"],
        ]
    )

    attributes = custom.at(custom_symbols["SeafoamIslandsCave_MapAttributes"], 12)
    assert attributes[:3] == bytes(
        [seafoam["border_block"], seafoam["dimensions"][1], seafoam["dimensions"][0]]
    )
    assert attributes[3] == custom_symbols["SeafoamIslandsCave_Blocks"].bank
    assert int.from_bytes(attributes[4:6], "little") == custom_symbols[
        "SeafoamIslandsCave_Blocks"
    ].address
    assert attributes[11] == 0

    custom_only = {
        "SeafoamIslandsCave_MapAttributes",
        "SeafoamIslandsCave_Blocks",
        "SeafoamIslandsCave_MapScripts",
        "SeafoamIslandsCave_MapEvents",
        "SeafoamIslandsCaveUltraBall",
        "SeafoamIslandsCaveHiddenNevermeltice",
        "Phase9RefreshArticunoLocation",
        "Phase9ArticunoEncounter",
    }
    assert all(label in custom_symbols for label in custom_only)
    assert all(label not in reference_symbols for label in custom_only)


def test_compiled_seafoam_warps_and_articuno_object_match_the_contract(
    repo_root: Path, phase_9_constants: dict[str, int], scenario: dict
) -> None:
    constants = phase_9_constants
    seafoam = scenario["seafoam"]
    articuno = seafoam["articuno"]
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())

    assert _decode_warps(
        custom, symbols, "Route20_MapEvents", constants["WARP_EVENT_SIZE"]
    ) == [
        (
            38,
            7,
            1,
            constants["GROUP_SEAFOAM_GYM"],
            constants["MAP_SEAFOAM_GYM"],
        ),
        (
            seafoam["route20_warp"][0],
            seafoam["route20_warp"][1],
            seafoam["route20_warp"][3],
            constants["GROUP_SEAFOAM_ISLANDS_CAVE"],
            constants["MAP_SEAFOAM_ISLANDS_CAVE"],
        ),
    ]
    assert len(
        _decode_warps(
            reference,
            reference_symbols,
            "Route20_MapEvents",
            constants["WARP_EVENT_SIZE"],
        )
    ) == 1
    assert _decode_warps(
        custom,
        symbols,
        "SeafoamIslandsCave_MapEvents",
        constants["WARP_EVENT_SIZE"],
    ) == [
        (
            seafoam["return_warp"][0],
            seafoam["return_warp"][1],
            seafoam["return_warp"][3],
            constants["GROUP_ROUTE_20"],
            constants["MAP_ROUTE_20"],
        )
    ]

    objects = decode_object_events(
        custom,
        symbols,
        "SeafoamIslandsCave_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
        constants["OBJECT_EVENT_SIZE"],
    )
    assert len(objects) == 2
    bird = next(
        event
        for event in objects
        if event.script_pointer == symbols["SeafoamIslandsCaveArticuno"].address
    )
    assert (bird.x, bird.y) == tuple(articuno["coordinate"])
    assert bird.sprite == constants[articuno["sprite"]]
    assert bird.movement == constants[articuno["movement"]]
    assert bird.palette_and_type >> 4 == constants[articuno["palette"]]
    assert bird.palette_and_type & 0xF == constants[articuno["object_type"]]
    assert bird.script_pointer == symbols["SeafoamIslandsCaveArticuno"].address
    assert bird.event_flag == constants[articuno["mask_event"]]

    pickup = seafoam["visible_pickup"]
    item_ball = next(
        event
        for event in objects
        if event.script_pointer == symbols[pickup["script"]].address
    )
    assert (item_ball.x, item_ball.y) == tuple(pickup["coordinate"])
    assert item_ball.sprite == constants["SPRITE_POKE_BALL"]
    assert item_ball.movement == constants["SPRITEMOVEDATA_STILL"]
    assert item_ball.palette_and_type & 0xF == constants["OBJECTTYPE_ITEMBALL"]
    assert item_ball.event_flag == constants[pickup["event"]]

    hidden = seafoam["hidden_pickup"]
    backgrounds = decode_background_events(
        custom,
        symbols,
        "SeafoamIslandsCave_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
    )
    assert len(backgrounds) == 1
    assert (backgrounds[0].x, backgrounds[0].y) == tuple(hidden["coordinate"])
    assert backgrounds[0].event_type == constants["BGEVENT_ITEM"]
    assert backgrounds[0].script_pointer == symbols[hidden["script"]].address


def test_compiled_articuno_stubs_and_capture_sequence_are_species_exact(
    repo_root: Path, phase_9_constants: dict[str, int], scenario: dict
) -> None:
    constants = phase_9_constants
    articuno = scenario["seafoam"]["articuno"]
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())

    for stub_label, target_label in (
        ("SeafoamIslandsCaveArticunoCallback", articuno["callback"]),
        ("SeafoamIslandsCaveArticuno", articuno["script"]),
    ):
        target = symbols[target_label]
        expected = bytes([constants["farsjump_command"], target.bank]) + target.address.to_bytes(
            2, "little"
        )
        assert rom.at(symbols[stub_label], len(expected)) == expected
        assert symbols[stub_label].bank != target.bank

    compiled = rom.slice(
        symbols[articuno["script"]].rom_offset,
        symbols["Phase9LegendaryBirdsEnd"].rom_offset
        - symbols[articuno["script"]].rom_offset,
    )
    special_id = (
        symbols["CheckCaughtPokemonSpecial"].address
        - symbols["SpecialsPointers"].address
    ) // 3
    encounter = bytes(
        [
            constants["loadwildmon_command"],
            constants[articuno["species"]],
            articuno["level"],
            constants["startbattle_command"],
            constants["special_command"],
        ]
    ) + special_id.to_bytes(2, "little")
    caught = (
        bytes([constants["setevent_command"]])
        + constants[articuno["capture_event"]].to_bytes(2, "little")
        + bytes([constants["setevent_command"]])
        + constants[articuno["mask_event"]].to_bytes(2, "little")
        + bytes([constants["disappear_command"], articuno["object_id"]])
    )
    assert encounter in compiled
    assert caught in compiled
    assert compiled.index(encounter) < compiled.index(caught)
    assert compiled.index(caught) < compiled.index(
        bytes([constants["reloadmapafterbattle_command"]])
    )


def test_compiled_facility_variant_and_reference_assets_are_exact(
    repo_root: Path, phase_9_constants: dict[str, int], scenario: dict
) -> None:
    constants = phase_9_constants
    facility = scenario["facility_variant"]
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())

    custom_gfx = repo_root / facility["active_gfx_path"].replace(".png", ".2bpp.lz")
    stock_gfx = repo_root / facility["stock_gfx_path"].replace(".png", ".2bpp.lz")
    assert custom.at(custom_symbols["TilesetFacilityGFX"], custom_gfx.stat().st_size) == custom_gfx.read_bytes()
    assert reference.at(reference_symbols["TilesetFacilityGFX"], stock_gfx.stat().st_size) == stock_gfx.read_bytes()

    active_metatiles = (repo_root / facility["active_metatiles_path"]).read_bytes()
    stock_metatiles = (repo_root / facility["stock_metatiles_path"]).read_bytes()
    assert custom.at(custom_symbols["TilesetFacilityMeta"], len(active_metatiles)) == active_metatiles
    assert reference.at(reference_symbols["TilesetFacilityMeta"], len(stock_metatiles)) == stock_metatiles

    custom_collision = custom.slice(
        custom_symbols["TilesetFacilityColl"].rom_offset,
        custom_symbols["TilesetBattleTowerOutsideMeta"].rom_offset
        - custom_symbols["TilesetFacilityColl"].rom_offset,
    )
    reference_collision = reference.slice(
        reference_symbols["TilesetFacilityColl"].rom_offset,
        reference_symbols["TilesetBattleTowerOutsideMeta"].rom_offset
        - reference_symbols["TilesetFacilityColl"].rom_offset,
    )
    assert custom_collision[: len(reference_collision)] == reference_collision
    assert custom_collision[len(reference_collision) :] == bytes(
        constants[f"COLL_{collision}"]
        for block in sorted(facility["collisions"], key=int)
        for collision in facility["collisions"][block]
    )
    assert custom_symbols["TilesetFacilityPalMap"].address == reference_symbols[
        "TilesetFacilityPalMap"
    ].address


def test_compiled_power_plant_annex_and_remaining_bird_objects_match_contract(
    repo_root: Path, phase_9_constants: dict[str, int], scenario: dict
) -> None:
    constants = phase_9_constants
    annex = scenario["power_plant_annex"]
    zapdos = annex["zapdos"]
    victory = scenario["victory_road_bird"]
    moltres = victory["moltres"]
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())

    active_plant = (repo_root / annex["power_plant_active_block_path"]).read_bytes()
    stock_plant = (repo_root / annex["power_plant_stock_block_path"]).read_bytes()
    annex_blocks = (repo_root / annex["block_path"]).read_bytes()
    assert custom.at(symbols["PowerPlant_Blocks"], len(active_plant)) == active_plant
    assert reference.at(reference_symbols["PowerPlant_Blocks"], len(stock_plant)) == stock_plant
    assert custom.at(symbols["PowerPlantGeneratorAnnex_Blocks"], len(annex_blocks)) == annex_blocks

    assert constants["GROUP_POWER_PLANT_GENERATOR_ANNEX"] == constants[
        "GROUP_POWER_PLANT"
    ]
    assert constants["MAP_POWER_PLANT_GENERATOR_ANNEX"] == 18
    map_record = custom.slice(
        symbols["MapGroup_Cerulean"].rom_offset
        + (constants["MAP_POWER_PLANT_GENERATOR_ANNEX"] - 1)
        * constants["MAP_LENGTH"],
        constants["MAP_LENGTH"],
    )
    assert map_record[1] == constants["TILESET_FACILITY"]
    assert map_record[2] == constants["INDOOR"]
    assert map_record[5] == constants["LANDMARK_POWER_PLANT"]
    assert map_record[6] == constants["MUSIC_VIRIDIAN_CITY"]
    assert map_record[7] >> 4 == constants["FALSE"]
    assert map_record[7] & 0xF == constants["PALETTE_DAY"]
    assert map_record[8] == constants["FISHGROUP_SHORE"]

    attributes = custom.at(symbols["PowerPlantGeneratorAnnex_MapAttributes"], 12)
    assert attributes[:3] == bytes([annex["border_block"], 4, 4])
    assert attributes[3] == symbols["PowerPlantGeneratorAnnex_Blocks"].bank
    assert int.from_bytes(attributes[4:6], "little") == symbols[
        "PowerPlantGeneratorAnnex_Blocks"
    ].address
    assert attributes[11] == 0

    plant_warps = _decode_warps(
        custom, symbols, "PowerPlant_MapEvents", constants["WARP_EVENT_SIZE"]
    )
    assert plant_warps[-2:] == [
        (
            warp[0],
            warp[1],
            warp[3],
            constants["GROUP_POWER_PLANT_GENERATOR_ANNEX"],
            constants["MAP_POWER_PLANT_GENERATOR_ANNEX"],
        )
        for warp in annex["power_plant_warps"]
    ]
    assert len(
        _decode_warps(
            reference,
            reference_symbols,
            "PowerPlant_MapEvents",
            constants["WARP_EVENT_SIZE"],
        )
    ) == 2
    assert _decode_warps(
        custom,
        symbols,
        "PowerPlantGeneratorAnnex_MapEvents",
        constants["WARP_EVENT_SIZE"],
    ) == [
        (
            warp[0],
            warp[1],
            warp[3],
            constants["GROUP_POWER_PLANT"],
            constants["MAP_POWER_PLANT"],
        )
        for warp in annex["return_warps"]
    ]

    backgrounds = decode_background_events(
        custom,
        symbols,
        "PowerPlant_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
    )
    assert [
        (event.x, event.y, event.event_type, event.script_pointer)
        for event in backgrounds[-2:]
    ] == [
        (x, y, constants["BGEVENT_RIGHT"], symbols["PowerPlantAnnexShutter"].address)
        for x, y in annex["shutter"]["interaction_event_coordinates"]
    ]

    annex_backgrounds = decode_background_events(
        custom,
        symbols,
        "PowerPlantGeneratorAnnex_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
    )
    assert [
        (event.x, event.y, event.event_type, event.script_pointer)
        for event in annex_backgrounds
    ] == [
        (
            x,
            y,
            constants["BGEVENT_READ"],
            symbols["PowerPlantGeneratorAnnexConsole"].address,
        )
        for x, y in annex["console_coordinates"]
    ]

    annex_objects = decode_object_events(
        custom,
        symbols,
        "PowerPlantGeneratorAnnex_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
        constants["OBJECT_EVENT_SIZE"],
    )
    victory_objects = decode_object_events(
        custom,
        symbols,
        "VictoryRoad_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
        constants["OBJECT_EVENT_SIZE"],
    )
    reference_victory_objects = decode_object_events(
        reference,
        reference_symbols,
        "VictoryRoad_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
        constants["OBJECT_EVENT_SIZE"],
    )
    assert len(annex_objects) == 2
    assert len(victory_objects) == 6
    assert len(reference_victory_objects) == 6
    hidden_full_restore = victory["hidden_full_restore"]
    victory_backgrounds = decode_background_events(
        custom,
        symbols,
        "VictoryRoad_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
    )
    hidden_full_restore_event = next(
        event
        for event in victory_backgrounds
        if event.script_pointer == symbols[hidden_full_restore["script"]].address
    )
    assert (
        hidden_full_restore_event.x,
        hidden_full_restore_event.y,
        hidden_full_restore_event.event_type,
    ) == (
        *hidden_full_restore["coordinate"],
        constants["BGEVENT_ITEM"],
    )
    zapdos_object = next(
        obj
        for obj in annex_objects
        if obj.script_pointer == symbols["PowerPlantGeneratorAnnexZapdos"].address
    )
    pickup = annex["visible_pickup"]
    pickup_object = next(
        obj
        for obj in annex_objects
        if obj.script_pointer == symbols[pickup["script"]].address
    )
    assert (pickup_object.x, pickup_object.y) == tuple(pickup["coordinate"])
    assert pickup_object.sprite == constants["SPRITE_POKE_BALL"]
    assert pickup_object.movement == constants["SPRITEMOVEDATA_STILL"]
    assert pickup_object.palette_and_type & 0xF == constants["OBJECTTYPE_ITEMBALL"]
    assert pickup_object.event_flag == constants[pickup["event"]]

    for bird, obj, stub in (
        (zapdos, zapdos_object, "PowerPlantGeneratorAnnexZapdos"),
        (moltres, victory_objects[-1], "VictoryRoadMoltres"),
    ):
        assert (obj.x, obj.y) == tuple(bird["coordinate"])
        assert obj.sprite == constants[bird["sprite"]]
        assert obj.movement == constants[bird["movement"]]
        assert obj.palette_and_type >> 4 == constants[bird["palette"]]
        assert obj.palette_and_type & 0xF == constants[bird["object_type"]]
        assert obj.script_pointer == symbols[stub].address
        assert obj.event_flag == constants[bird["mask_event"]]

    custom_only = {
        "PowerPlantGeneratorAnnex_MapAttributes",
        "PowerPlantGeneratorAnnex_Blocks",
        "PowerPlantGeneratorAnnex_MapScripts",
        "PowerPlantGeneratorAnnex_MapEvents",
        "PowerPlantGeneratorAnnexMagnet",
        "Phase9RefreshZapdosLocation",
        "Phase9RefreshMoltresLocation",
        "Phase9ZapdosEncounter",
        "Phase9MoltresEncounter",
        "Phase9OaksAssistant2Hints",
        "VictoryRoadMoltres",
        "VictoryRoadHiddenFullRestore",
    }
    assert all(label in symbols for label in custom_only)
    assert all(label not in reference_symbols for label in custom_only)


@pytest.mark.parametrize(
    ("contract_key", "bird_key", "callback_stub", "encounter_stub"),
    [
        (
            "power_plant_annex",
            "zapdos",
            "PowerPlantGeneratorAnnexZapdosCallback",
            "PowerPlantGeneratorAnnexZapdos",
        ),
        (
            "victory_road_bird",
            "moltres",
            "VictoryRoadMoltresCallback",
            "VictoryRoadMoltres",
        ),
    ],
)
def test_compiled_remaining_bird_stubs_and_capture_sequences_are_species_exact(
    repo_root: Path,
    phase_9_constants: dict[str, int],
    scenario: dict,
    contract_key: str,
    bird_key: str,
    callback_stub: str,
    encounter_stub: str,
) -> None:
    constants = phase_9_constants
    bird = scenario[contract_key][bird_key]
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())

    for stub_label, target_label in (
        (callback_stub, bird["callback"]),
        (encounter_stub, bird["script"]),
    ):
        target = symbols[target_label]
        expected = bytes([constants["farsjump_command"], target.bank]) + target.address.to_bytes(2, "little")
        assert rom.at(symbols[stub_label], len(expected)) == expected
        assert symbols[stub_label].bank != target.bank

    compiled = rom.slice(
        symbols[bird["script"]].rom_offset,
        symbols["Phase9LegendaryBirdsEnd"].rom_offset
        - symbols[bird["script"]].rom_offset,
    )
    special_id = (
        symbols["CheckCaughtPokemonSpecial"].address
        - symbols["SpecialsPointers"].address
    ) // 3
    encounter = bytes(
        [
            constants["loadwildmon_command"],
            constants[bird["species"]],
            bird["level"],
            constants["startbattle_command"],
            constants["special_command"],
        ]
    ) + special_id.to_bytes(2, "little")
    caught = (
        bytes([constants["setevent_command"]])
        + constants[bird["capture_event"]].to_bytes(2, "little")
        + bytes([constants["setevent_command"]])
        + constants[bird["mask_event"]].to_bytes(2, "little")
        + bytes([constants["disappear_command"], bird["object_id"]])
    )
    assert encounter in compiled
    assert caught in compiled
    assert compiled.index(encounter) < compiled.index(caught)
    assert compiled.index(caught) < compiled.index(
        bytes([constants["reloadmapafterbattle_command"]])
    )
