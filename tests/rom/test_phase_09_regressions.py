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
            "COLL_DOOR",
            "COLL_WATER",
            "COLL_WATER_21",
            "COLL_WALL",
            "EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION",
            "EVENT_ARTICUNO_AVAILABLE",
            "EVENT_CAUGHT_ARTICUNO_IN_KANTO",
            "EVENT_CAUGHT_MOLTRES_IN_KANTO",
            "EVENT_CAUGHT_ZAPDOS_IN_KANTO",
            "EVENT_GOT_BULBASAUR_FROM_ERIKA",
            "EVENT_GOT_CHARMANDER_FROM_BLAINE",
            "EVENT_GOT_SQUIRTLE_FROM_MISTY",
            "EVENT_HELPED_ERIKA_CLEAN_CELADON_POND",
            "EVENT_GOT_ARTICUNO_FROM_ELM",
            "EVENT_GOT_MOLTRES_FROM_ELM",
            "EVENT_GOT_ZAPDOS_FROM_ELM",
            "EVENT_MOLTRES_NOT_AT_KANTO_LOCATION",
            "EVENT_OAK_MOVED_THIRD_BIRD",
            "EVENT_POWER_PLANT_ANNEX_AUTHORIZED",
            "EVENT_RECOVERED_BLAINES_LOG",
            "EVENT_SAFARI_ZONE_ACCESSIBLE",
            "EVENT_SAFARI_ZONE_BETA_ULTRA_BALL",
            "EVENT_SAFARI_ZONE_BETA_MAX_REVIVE",
            "EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION",
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
            "TILESET_PARK",
            "TILESET_ICE_PATH",
            "ROUTE",
            "CAVE",
            "LANDMARK_FUCHSIA_CITY",
            "LANDMARK_SEAFOAM_ISLANDS",
            "MUSIC_NATIONAL_PARK",
            "MUSIC_EVOLUTION",
            "MUSIC_UNION_CAVE",
            "PALETTE_AUTO",
            "PALETTE_NITE",
            "FISHGROUP_SHORE",
            "FISHGROUP_OCEAN",
            "TRUE",
            "MAP_LENGTH",
            "BGEVENT_READ",
            "HELD_NONE",
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
            "ARTICUNO",
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
    assert constants["EVENT_CAUGHT_ARTICUNO_IN_KANTO"] == 2027
    assert constants["EVENT_CAUGHT_ZAPDOS_IN_KANTO"] == 2028
    assert constants["EVENT_CAUGHT_MOLTRES_IN_KANTO"] == 2029
    assert constants["EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION"] == 2030
    assert constants["EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION"] == 2031
    assert constants["EVENT_MOLTRES_NOT_AT_KANTO_LOCATION"] == 2032
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

    assert custom.at(custom_symbols["TilesetKantoColl"], 4) == bytes(
        [
            phase_9_constants["COLL_HOP_DOWN"],
            phase_9_constants["COLL_FLOOR"],
            phase_9_constants["COLL_WALL"],
            phase_9_constants["COLL_FLOOR"],
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


def test_compiled_cinnabar_case_and_flavor_events_match_the_locked_coordinates(
    repo_root: Path, phase_9_constants: dict[str, int]
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
    assert len(custom_objects) == 2
    assert len(reference_objects) == 1
    rubble = custom_objects[-1]
    assert (rubble.x, rubble.y, rubble.sprite, rubble.movement) == (
        13,
        6,
        constants["SPRITE_ROCK"],
        constants["SPRITEMOVEDATA_STILL"],
    )
    assert rubble.palette_and_type & 0xF == constants["OBJECTTYPE_SCRIPT"]
    assert (
        rubble.script_pointer
        == custom_symbols["CinnabarIslandBlainesLogRubble"].address
    )
    assert rubble.event_flag == constants["EVENT_RECOVERED_BLAINES_LOG"]

    backgrounds = decode_background_events(
        custom,
        custom_symbols,
        "CinnabarIsland_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
    )
    assert [(event.x, event.y) for event in backgrounds[-2:]] == [(15, 5), (19, 8)]


def test_compiled_phase_9_starter_labels_are_custom_only(repo_root: Path) -> None:
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())
    labels = {
        "BlainesLogDesc",
        "ErikaBulbasaurOfferText",
        "MistySquirtleOfferText",
        "BlaineCharmanderOfferText",
        "CeladonCityMukPond",
        "CinnabarIslandBlainesLogRubble",
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
    assert len(objects) == 1
    bird = objects[0]
    assert (bird.x, bird.y) == tuple(articuno["coordinate"])
    assert bird.sprite == constants[articuno["sprite"]]
    assert bird.movement == constants[articuno["movement"]]
    assert bird.palette_and_type >> 4 == constants[articuno["palette"]]
    assert bird.palette_and_type & 0xF == constants[articuno["object_type"]]
    assert bird.script_pointer == symbols["SeafoamIslandsCaveArticuno"].address
    assert bird.event_flag == constants[articuno["mask_event"]]
    assert decode_background_events(
        custom,
        symbols,
        "SeafoamIslandsCave_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
    ) == []


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
