from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.linker_map import parse_linker_map
from tests.support.rom_image import RomImage, decode_background_events, decode_object_events
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase10]


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_10_giovanni_cerulean_cave.json").read_text()
    )


@pytest.fixture(scope="module")
def phase_10_constants(repo_root: Path, tmp_path_factory, scenario: dict) -> dict[str, int]:
    names = [name for group in scenario["events"].values() for name, _ in group]
    names.extend(
        [
            "NUM_EVENTS", "GROUP_CERULEAN_CAVE", "MAP_CERULEAN_CAVE",
            "WARP_EVENT_SIZE", "COORD_EVENT_SIZE", "BG_EVENT_SIZE", "OBJECT_EVENT_SIZE",
            "BGEVENT_READ", "BGEVENT_ITEM", "OBJECTTYPE_TRAINER", "OBJECTTYPE_ITEMBALL",
            "SPRITE_POKE_BALL", "FISHGROUP_CERULEAN_CAVE", "FISHGROUP_DATA_LENGTH",
        ]
    )
    names.extend(remnant["trainer"] for remnant in scenario["remnants"])
    names.extend(remnant["sprite"] for remnant in scenario["remnants"])
    names.extend(remnant["movement"] for remnant in scenario["remnants"])
    names.extend(remnant["palette"] for remnant in scenario["remnants"])
    names.extend(pickup["item"] for pickup in scenario["pickups"])
    names.append(scenario["hidden_pickup"]["item"])
    names.extend(
        species
        for remnant in scenario["remnants"]
        for _, species, _ in remnant["party"]
    )
    names.extend(
        move
        for remnant in scenario["remnants"]
        for _, _, moves in remnant["party"]
        for move in moves
    )
    names.extend(species for _, species in scenario["encounters"]["grass"]["slots"])
    names.extend(species for _, species in scenario["encounters"]["water"]["slots"])
    names.extend(
        species
        for rod in ("old", "good", "super")
        for _, species, _ in scenario["encounters"]["fishing"][rod]
    )
    return resolve_constants(repo_root, tmp_path_factory.mktemp("phase_10_constants"), names)


def test_compiled_phase_10_ids_use_the_reviewed_gaps_without_save_growth(
    repo_root: Path, scenario: dict, phase_10_constants: dict[str, int]
) -> None:
    for group in scenario["events"].values():
        for name, expected in group:
            assert phase_10_constants[name] == expected
    assert phase_10_constants["NUM_EVENTS"] == 2048
    assert phase_10_constants["GROUP_CERULEAN_CAVE"] == 7
    assert phase_10_constants["MAP_CERULEAN_CAVE"] == 19

    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    assert symbols["wCurBox"].address - symbols["wEventFlags"].address == 256


def test_compiled_cave_replaces_only_the_unreferenced_beta_payload(
    repo_root: Path, scenario: dict
) -> None:
    custom = RomImage.load(repo_root / scenario["rom"])
    custom_symbols = SymbolTable.parse((repo_root / scenario["symbols"]).read_text())
    cave = (repo_root / scenario["map"]["block_path"]).read_bytes()
    assert custom.at(custom_symbols["CeruleanCave_Blocks"], len(cave)) == cave

    reference = RomImage.load(repo_root / scenario["reference_rom"])
    reference_symbols = SymbolTable.parse(
        (repo_root / scenario["reference_symbols"]).read_text()
    )
    beta = (repo_root / "maps/unused/BetaCaveTestMap.blk").read_bytes()
    assert reference.at(reference_symbols["BetaCaveTestMap_Blocks"], len(beta)) == beta


def test_compiled_cave_attributes_match_the_registered_map(
    repo_root: Path, scenario: dict
) -> None:
    rom = RomImage.load(repo_root / scenario["rom"])
    symbols = SymbolTable.parse((repo_root / scenario["symbols"]).read_text())
    attributes = rom.at(symbols["CeruleanCave_MapAttributes"], 8)
    assert attributes[:3] == bytes([scenario["map"]["border_block"], 18, 15])
    assert attributes[3] == symbols["CeruleanCave_Blocks"].bank
    assert int.from_bytes(attributes[4:6], "little") == symbols["CeruleanCave_Blocks"].address


def test_compiled_giovanni_class_tables_and_portrait(repo_root: Path, tmp_path: Path) -> None:
    constants = resolve_constants(
        repo_root,
        tmp_path,
        [
            "GIOVANNI", "GIOVANNI1", "MYSTICALMAN", "NUM_TRAINER_CLASSES",
            "NUM_TRAINER_ATTRIBUTES", "FULL_HEAL", "FULL_RESTORE",
            "MUSIC_ROCKET_ENCOUNTER", "COLOR_SIZE",
        ],
    )
    assert constants["GIOVANNI"] == constants["MYSTICALMAN"] + 1
    assert constants["NUM_TRAINER_CLASSES"] == constants["GIOVANNI"]
    assert constants["GIOVANNI1"] == 1

    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    class_index = constants["GIOVANNI"] - 1

    group_pointer = rom.u16le(symbols["TrainerGroups"].rom_offset + class_index * 2)
    assert group_pointer == symbols["GiovanniGroup"].address

    pic_row = rom.slice(symbols["TrainerPicPointers"].rom_offset + class_index * 3, 3)
    loader = (repo_root / "engine/gfx/load_pics.asm").read_text()
    pics_fix = int(re.search(r"PICS_FIX EQU \$([0-9a-fA-F]+)", loader).group(1), 16)
    assert pic_row == bytes([symbols["GiovanniPic"].bank - pics_fix]) + symbols["GiovanniPic"].address.to_bytes(2, "little")

    width = constants["NUM_TRAINER_ATTRIBUTES"]
    attributes = rom.slice(symbols["TrainerClassAttributes"].rom_offset + class_index * width, width)
    assert attributes[:3] == bytes([constants["FULL_HEAL"], constants["FULL_RESTORE"], 25])

    encounter = rom.u8(symbols["TrainerEncounterMusic"].rom_offset + constants["GIOVANNI"])
    assert encounter == constants["MUSIC_ROCKET_ENCOUNTER"]

    palette_width = constants["COLOR_SIZE"] * 2
    generated_palette = (repo_root / "gfx/trainers/giovanni.gbcpal").read_bytes()
    assert rom.slice(symbols["TrainerPalettes"].rom_offset + constants["GIOVANNI"] * palette_width, palette_width) == generated_palette[2:6]

    packed = (repo_root / "gfx/trainers/giovanni.2bpp.lz").read_bytes()
    assert rom.at(symbols["GiovanniPic"], len(packed)) == packed
    unpacked = subprocess.run(
        [str(repo_root / "tools/lzcompress"), "--uncompress", "--", "-", "-"],
        input=packed,
        capture_output=True,
        check=True,
    ).stdout
    assert unpacked == (repo_root / "gfx/trainers/giovanni.2bpp").read_bytes()
    assert len(unpacked) == 784
    assert symbols["GiovanniPic"].bank == 0x59


def test_compiled_omastar_recompression_preserves_pixels_and_picture_bank_budget(
    repo_root: Path,
) -> None:
    custom_rom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference_rom = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())

    custom_packed = (repo_root / "gfx/pokemon/omastar/back_crystallegends.lz").read_bytes()
    reference_packed = (repo_root / "gfx/pokemon/omastar/back.2bpp.lz").read_bytes()
    assert len(custom_packed) == 424
    assert len(reference_packed) == 429
    assert custom_rom.at(custom_symbols["OmastarBackpic"], len(custom_packed)) == custom_packed
    assert reference_rom.at(reference_symbols["OmastarBackpic"], len(reference_packed)) == reference_packed

    decoded = []
    for packed in (custom_packed, reference_packed):
        decoded.append(
            subprocess.run(
                [str(repo_root / "tools/lzcompress"), "--uncompress", "--", "-", "-"],
                input=packed,
                capture_output=True,
                check=True,
            ).stdout
        )
    assert decoded[0] == decoded[1] == (repo_root / "gfx/pokemon/omastar/back.2bpp").read_bytes()
    assert custom_symbols["OmastarBackpic"].bank == reference_symbols["OmastarBackpic"].bank == 0x4A

    usage = parse_linker_map((repo_root / "crystallegends.map").read_text())
    assert usage[("ROMX", 0x4A)].free == 4


def test_compiled_cave_population_and_lab_records(
    repo_root: Path, phase_10_constants: dict[str, int], scenario: dict
) -> None:
    constants = phase_10_constants
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    objects = decode_object_events(
        rom,
        symbols,
        "CeruleanCave_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
        constants["OBJECT_EVENT_SIZE"],
    )
    script_labels = {
        "S1": "TrainerCeruleanCaveScientistMitch",
        "S2": "TrainerCeruleanCaveScientistRoss",
        "R1": "TrainerCeruleanCaveGruntM1",
        "R2": "TrainerCeruleanCaveGruntF1",
        "R3": "TrainerCeruleanCaveGruntM2",
        "R4": "TrainerCeruleanCaveGruntF2",
    }
    for remnant in scenario["remnants"]:
        matching = [event for event in objects if (event.x, event.y) == tuple(remnant["coordinate"])]
        assert len(matching) == 1
        event = matching[0]
        assert event.sprite == constants[remnant["sprite"]]
        assert event.movement == constants[remnant["movement"]]
        assert event.palette_and_type >> 4 == constants[remnant["palette"]]
        assert event.palette_and_type & 0xF == constants["OBJECTTYPE_TRAINER"]
        assert event.sight_range == remnant["sight"]
        assert event.script_pointer == symbols[script_labels[remnant["id"]]].address
        assert event.event_flag == constants["EVENT_BEAT_GIOVANNI"]

    for pickup in scenario["pickups"]:
        matching = [event for event in objects if (event.x, event.y) == tuple(pickup["coordinate"])]
        assert len(matching) == 1
        event = matching[0]
        assert event.sprite == constants["SPRITE_POKE_BALL"]
        assert event.palette_and_type & 0xF == constants["OBJECTTYPE_ITEMBALL"]
        assert event.script_pointer == symbols[pickup["script"]].address
        assert event.event_flag == constants[pickup["event"]]

    backgrounds = decode_background_events(
        rom,
        symbols,
        "CeruleanCave_MapEvents",
        constants["WARP_EVENT_SIZE"],
        constants["COORD_EVENT_SIZE"],
        constants["BG_EVENT_SIZE"],
    )
    assert len(backgrounds) == 13
    for record in scenario["lab_records"]:
        for coordinate in record["coordinates"]:
            matching = [event for event in backgrounds if (event.x, event.y) == tuple(coordinate)]
            assert len(matching) == 1
            assert matching[0].event_type == constants["BGEVENT_READ"]
            assert matching[0].script_pointer == symbols[record["script"]].address
    hidden = scenario["hidden_pickup"]
    matching = [event for event in backgrounds if (event.x, event.y) == tuple(hidden["coordinate"])]
    assert len(matching) == 1
    assert matching[0].event_type == constants["BGEVENT_ITEM"]
    assert matching[0].script_pointer == symbols[hidden["script"]].address


def test_compiled_remnant_party_payloads_are_exact(
    repo_root: Path, phase_10_constants: dict[str, int], scenario: dict
) -> None:
    constants = phase_10_constants
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    group_bounds = {
        "SCIENTIST": ("ScientistGroup", "ErikaGroup"),
        "GRUNTM": ("GruntMGroup", "GentlemanGroup"),
        "GRUNTF": ("GruntFGroup", "MysticalmanGroup"),
    }
    for remnant in scenario["remnants"]:
        start_label, end_label = group_bounds[remnant["class"]]
        start = symbols[start_label].rom_offset
        end = symbols[end_label].rom_offset
        payload = bytes(
            value
            for level, species, moves in remnant["party"]
            for value in (level, constants[species], *(constants[move] for move in moves))
        ) + b"\xff"
        assert rom.slice(start, end - start).count(payload) == 1

    assert constants["ROSS2"] == 6
    assert constants["MITCH2"] == 7
    assert constants["GRUNTM_32"] == 32
    assert constants["GRUNTM_33"] == 33
    assert constants["GRUNTF_6"] == 6
    assert constants["GRUNTF_7"] == 7


def test_compiled_cave_encounter_records_and_fishing_group(
    repo_root: Path, phase_10_constants: dict[str, int], scenario: dict
) -> None:
    constants = phase_10_constants
    encounters = scenario["encounters"]
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())
    map_id = bytes([constants["GROUP_CERULEAN_CAVE"], constants["MAP_CERULEAN_CAVE"]])

    grass = map_id + bytes(rate * 255 // 100 for rate in encounters["grass"]["rates"])
    grass += bytes(
        value
        for _ in range(3)
        for level, species in encounters["grass"]["slots"]
        for value in (level, constants[species])
    )
    grass_label = "KantoGrassWildMons._def_grass_wildmons_CERULEAN_CAVE"
    assert rom.at(symbols[grass_label], len(grass)) == grass

    water = map_id + bytes([encounters["water"]["rate"] * 255 // 100])
    water += bytes(
        value
        for level, species in encounters["water"]["slots"]
        for value in (level, constants[species])
    )
    water_label = "KantoWaterWildMons._def_water_wildmons_CERULEAN_CAVE"
    assert rom.at(symbols[water_label], len(water)) == water
    assert grass_label not in reference_symbols
    assert water_label not in reference_symbols

    fish_index = constants["FISHGROUP_CERULEAN_CAVE"] - 1
    fish_row = rom.slice(
        symbols["FishGroups"].rom_offset + fish_index * constants["FISHGROUP_DATA_LENGTH"],
        constants["FISHGROUP_DATA_LENGTH"],
    )
    fish_labels = [
        "FishGroups.CeruleanCave_Old",
        "FishGroups.CeruleanCave_Good",
        "FishGroups.CeruleanCave_Super",
    ]
    assert fish_row[0] == 50 * 255 // 100 + 1
    assert [int.from_bytes(fish_row[index : index + 2], "little") for index in (1, 3, 5)] == [
        symbols[label].address for label in fish_labels
    ]

    for rod, label in zip(("old", "good", "super"), fish_labels, strict=True):
        payload = bytes(
            value
            for chance, species, level in encounters["fishing"][rod]
            for value in (
                int(chance.split()[0]) * 255 // 100 + (1 if chance.endswith("+ 1") else 0),
                constants[species],
                level,
            )
        )
        assert rom.at(symbols[label], len(payload)) == payload
