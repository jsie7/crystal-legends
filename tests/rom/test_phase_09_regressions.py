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


pytestmark = [pytest.mark.rom, pytest.mark.phase9]


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
            "COLL_WALL",
            "EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION",
            "EVENT_CAUGHT_ARTICUNO_IN_KANTO",
            "EVENT_CAUGHT_MOLTRES_IN_KANTO",
            "EVENT_CAUGHT_ZAPDOS_IN_KANTO",
            "EVENT_GOT_BULBASAUR_FROM_ERIKA",
            "EVENT_GOT_CHARMANDER_FROM_BLAINE",
            "EVENT_GOT_SQUIRTLE_FROM_MISTY",
            "EVENT_HELPED_ERIKA_CLEAN_CELADON_POND",
            "EVENT_MOLTRES_NOT_AT_KANTO_LOCATION",
            "EVENT_POWER_PLANT_ANNEX_AUTHORIZED",
            "EVENT_RECOVERED_BLAINES_LOG",
            "EVENT_SAFARI_ZONE_ACCESSIBLE",
            "EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION",
            "HELD_NONE",
            "ITEMATTR_STRUCT_LENGTH",
            "ITEMMENU_NOUSE",
            "ITEM_NAME_LENGTH",
            "KEY_ITEM",
            "NUM_EVENTS",
            "NUM_ITEMS",
            "OBJECTTYPE_SCRIPT",
            "OBJECT_EVENT_SIZE",
            "BG_EVENT_SIZE",
            "COORD_EVENT_SIZE",
            "SPRITEMOVEDATA_STILL",
            "SPRITE_ROCK",
            "WARP_EVENT_SIZE",
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
    repo_root: Path, phase_9_constants: dict[str, int]
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
