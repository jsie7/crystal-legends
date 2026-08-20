from __future__ import annotations

import json
from pathlib import Path
import re
import struct
import zlib

import pytest

from tests.support.asm_conditions import active_lines
from tests.support.content_data import parse_evolution_blocks
from tests.support.map_assets import (
    collision_at,
    parse_block_paths,
    parse_collision_rows,
    parse_map_tilesets,
)
from tests.support.map_model import MapDimensions


pytestmark = [pytest.mark.static, pytest.mark.phase9]


CRYSTAL_LEGENDS = {"_CRYSTAL11", "_CRYSTALLEGENDS"}
REFERENCE = {"_CRYSTAL11"}


def _active_code(path: Path, definitions: set[str]) -> list[str]:
    return [
        line.text.split(";", 1)[0].strip()
        for line in active_lines(path.read_text(), definitions)
        if line.text.split(";", 1)[0].strip()
    ]


def _assert_contiguous(lines: list[str], expected: list[str]) -> None:
    width = len(expected)
    assert any(lines[index : index + width] == expected for index in range(len(lines)))


def _section(lines: list[str], start: str, end: str) -> list[str]:
    first = lines.index(start)
    return lines[first : lines.index(end, first + 1)]


def _assert_in_order(lines: list[str], expected: list[str]) -> None:
    position = -1
    for value in expected:
        position = lines.index(value, position + 1)


def _png_tiles(path: Path) -> tuple[tuple[int, ...], ...]:
    raw = path.read_bytes()
    assert raw.startswith(b"\x89PNG\r\n\x1a\n")
    offset = 8
    payload = bytearray()
    width = height = depth = color_type = 0
    while offset < len(raw):
        length = int.from_bytes(raw[offset : offset + 4], "big")
        kind = raw[offset + 4 : offset + 8]
        data = raw[offset + 8 : offset + 8 + length]
        offset += length + 12
        if kind == b"IHDR":
            width, height, depth, color_type = struct.unpack(">IIBB", data[:10])
        elif kind == b"IDAT":
            payload.extend(data)
        elif kind == b"IEND":
            break
    assert (width, height, depth, color_type) == (128, 48, 2, 0)
    packed = zlib.decompress(payload)
    stride = width // 4
    pixels: list[list[int]] = []
    for y in range(height):
        row = packed[y * (stride + 1) : (y + 1) * (stride + 1)]
        assert row[0] == 0
        values: list[int] = []
        for byte in row[1:]:
            values.extend((byte >> 6, (byte >> 4) & 3, (byte >> 2) & 3, byte & 3))
        pixels.append(values)
    return tuple(
        tuple(
            pixels[tile_y * 8 + y][tile_x * 8 + x]
            for y in range(8)
            for x in range(8)
        )
        for tile_y in range(6)
        for tile_x in range(16)
    )


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_09_kanto_completion.json").read_text()
    )


def test_phase_9_contract_locks_the_three_starter_rewards(scenario: dict) -> None:
    assert scenario["scenario_id"] == "phase-09-kanto-completion"
    assert scenario["events"] == {"first": 2015, "last": 2032, "count": 18}
    assert [(gift["species"], gift["level"]) for gift in scenario["gifts"]] == [
        ("BULBASAUR", 28),
        ("SQUIRTLE", 28),
        ("CHARMANDER", 28),
    ]
    assert len({gift["service_event"] for gift in scenario["gifts"]}) == 3
    assert len({gift["completion_event"] for gift in scenario["gifts"]}) == 3
    assert scenario["erika_task"] == {
        "map": "CELADON_CITY",
        "coordinate": [15, 18],
        "species": "MUK",
        "level": 35,
        "completion_event": "EVENT_HELPED_ERIKA_CLEAN_CELADON_POND",
        "success_results": ["knockout", "capture"],
        "retry_results": ["run", "loss"],
    }


def test_phase_9_events_are_contiguous_and_reference_reserved(repo_root: Path) -> None:
    source = repo_root / "constants/event_flags.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    events = [
        "EVENT_HELPED_ERIKA_CLEAN_CELADON_POND",
        "EVENT_LEARNED_LOCATION_OF_BLAINES_LOG",
        "EVENT_RECOVERED_BLAINES_LOG",
        "EVENT_RETURNED_BLAINES_LOG",
        "EVENT_GOT_BULBASAUR_FROM_ERIKA",
        "EVENT_GOT_SQUIRTLE_FROM_MISTY",
        "EVENT_GOT_CHARMANDER_FROM_BLAINE",
        "EVENT_SAFARI_ZONE_ACCESSIBLE",
        "EVENT_SAFARI_ZONE_BETA_ULTRA_BALL",
        "EVENT_SAFARI_ZONE_BETA_MAX_REVIVE",
        "EVENT_POWER_PLANT_ANNEX_AUTHORIZED",
        "EVENT_OPENED_POWER_PLANT_ANNEX",
        "EVENT_CAUGHT_ARTICUNO_IN_KANTO",
        "EVENT_CAUGHT_ZAPDOS_IN_KANTO",
        "EVENT_CAUGHT_MOLTRES_IN_KANTO",
        "EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION",
        "EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION",
        "EVENT_MOLTRES_NOT_AT_KANTO_LOCATION",
    ]
    _assert_contiguous(
        crystal,
        [
            "const EVENT_MOLTRES_AVAILABLE",
            *(f"const {event}" for event in events),
            "const_next 2048",
            "DEF NUM_EVENTS EQU const_value",
        ],
    )
    assert all(not any(event in line for line in reference) for event in events)
    assert "const_skip 18" in reference


def test_blaines_log_reuses_only_item_b0_in_the_custom_build(
    repo_root: Path, scenario: dict
) -> None:
    constants = repo_root / "constants/item_constants.asm"
    custom_constants = _active_code(constants, CRYSTAL_LEGENDS)
    reference_constants = _active_code(constants, REFERENCE)
    assert "const BLAINES_LOG" in custom_constants
    assert "const ITEM_B0" not in custom_constants
    assert "const ITEM_B0" in reference_constants
    assert "const BLAINES_LOG" not in reference_constants

    def names(definitions: set[str]) -> list[str]:
        return [
            match.group(1)
            for line in active_lines(
                (repo_root / "data/items/names.asm").read_text(), definitions
            )
            if (match := re.match(r'\s*li\s+"([^"]+)"', line.text))
        ]

    slot = scenario["blaines_log"]["item_id"] - 1
    assert names(CRYSTAL_LEGENDS)[slot] == "BLAINE'S LOG"
    assert names(REFERENCE)[slot] == "TERU-SAMA"

    custom_attributes = _active_code(
        repo_root / "data/items/attributes.asm", CRYSTAL_LEGENDS
    )
    reference_attributes = _active_code(
        repo_root / "data/items/attributes.asm", REFERENCE
    )
    assert (
        "item_attribute 0, HELD_NONE, 0, CANT_SELECT | CANT_TOSS, KEY_ITEM, "
        "ITEMMENU_NOUSE, ITEMMENU_NOUSE"
        in custom_attributes
    )
    assert (
        "item_attribute $9999, HELD_NONE, 0, NO_LIMITS, ITEM, "
        "ITEMMENU_NOUSE, ITEMMENU_NOUSE"
        in reference_attributes
    )


def test_level_28_gifts_generate_the_locked_moves(
    repo_root: Path, scenario: dict
) -> None:
    blocks = {
        block.species.upper(): block
        for block in parse_evolution_blocks(
            (repo_root / "data/pokemon/evos_attacks.asm").read_text()
        )
    }
    for gift in scenario["gifts"]:
        learned = [move for level, move in blocks[gift["species"]].learnset if level <= 28]
        assert learned[-4:] == gift["generated_moves"]


def test_starter_scripts_keep_service_and_delivery_state_independent(
    repo_root: Path,
) -> None:
    erika = _active_code(repo_root / "maps/CeladonGym.asm", CRYSTAL_LEGENDS)
    misty = _active_code(repo_root / "maps/CeruleanGym.asm", CRYSTAL_LEGENDS)
    blaine = _active_code(repo_root / "maps/SeafoamGym.asm", CRYSTAL_LEGENDS)

    _assert_in_order(
        erika,
        [
            "checkevent EVENT_HELPED_ERIKA_CLEAN_CELADON_POND",
            "writetext ErikaBulbasaurOfferText",
            "yesorno",
            "givepoke BULBASAUR, 28",
            "ifequal 2, .BulbasaurStorageFull",
            "setevent EVENT_GOT_BULBASAUR_FROM_ERIKA",
        ],
    )
    _assert_in_order(
        misty,
        [
            "checkevent EVENT_RESTORED_POWER_TO_KANTO",
            "writetext MistySquirtleOfferText",
            "yesorno",
            "givepoke SQUIRTLE, 28",
            "ifequal 2, .SquirtleStorageFull",
            "setevent EVENT_GOT_SQUIRTLE_FROM_MISTY",
        ],
    )
    _assert_in_order(
        blaine,
        [
            "checkevent EVENT_RETURNED_BLAINES_LOG",
            "checkitem BLAINES_LOG",
            "takeitem BLAINES_LOG",
            "setevent EVENT_RETURNED_BLAINES_LOG",
            "writetext BlaineCharmanderOfferText",
            "yesorno",
            "givepoke CHARMANDER, 28",
            "ifequal 2, .CharmanderStorageFull",
            "setevent EVENT_GOT_CHARMANDER_FROM_BLAINE",
        ],
    )
    for lines, prefix in ((erika, "ERIKA:"), (misty, "MISTY:"), (blaine, "BLAINE:")):
        assert any(line.startswith(f'text "{prefix}') for line in lines)


def test_erika_muk_and_blaine_log_retry_only_after_success(repo_root: Path) -> None:
    celadon = _active_code(repo_root / "maps/CeladonCity.asm", CRYSTAL_LEGENDS)
    pond = _section(celadon, "CeladonCityMukPond:", "CeladonCityFisherText:")
    _assert_in_order(
        pond,
        [
            "checkflag ENGINE_RAINBOWBADGE",
            "loadwildmon MUK, 35",
            "startbattle",
            "ifequal LOSE, .Retry",
            "ifequal DRAW, .Retry",
            "setevent EVENT_HELPED_ERIKA_CLEAN_CELADON_POND",
        ],
    )

    island = _active_code(repo_root / "maps/CinnabarIsland.asm", CRYSTAL_LEGENDS)
    case = _section(
        island, "CinnabarIslandBlainesLogRubble:", "CinnabarIslandBlueTeleport:"
    )
    _assert_in_order(
        case,
        [
            "checkevent EVENT_LEARNED_LOCATION_OF_BLAINES_LOG",
            "verbosegiveitem BLAINES_LOG",
            "iffalse .NoRoom",
            "setevent EVENT_RECOVERED_BLAINES_LOG",
            "disappear CINNABARISLAND_BLAINES_LOG_RUBBLE",
        ],
    )
    assert any(
        line.startswith("object_event 13,  6, SPRITE_ROCK")
        and line.endswith("EVENT_RECOVERED_BLAINES_LOG")
        for line in island
    )
    assert "bg_event 15,  5, BGEVENT_READ, CinnabarIslandOldGymRemains" in island
    assert "bg_event 19,  8, BGEVENT_READ, CinnabarIslandOldLabRemains" in island


def test_cinnabar_staircase_is_the_only_phase_9_kanto_asset_delta_so_far(
    repo_root: Path, scenario: dict
) -> None:
    blocks_source = (repo_root / "data/maps/blocks.asm").read_text()
    assert parse_block_paths(blocks_source)["CinnabarIsland"] == (
        "maps/CinnabarIslandCrystalLegends.blk"
    )
    assert parse_block_paths(blocks_source, REFERENCE)["CinnabarIsland"] == (
        "maps/CinnabarIsland.blk"
    )

    stock_blocks = (repo_root / "maps/CinnabarIsland.blk").read_bytes()
    custom_blocks = (repo_root / "maps/CinnabarIslandCrystalLegends.blk").read_bytes()
    assert len(stock_blocks) == len(custom_blocks) == 90
    assert [
        (index, old, new)
        for index, (old, new) in enumerate(zip(stock_blocks, custom_blocks))
        if old != new
    ] == [(scenario["blaines_log"]["staircase"]["block_offset"], 0x24, 0x00)]
    assert [
        (
            path.name,
            [index for index, block in enumerate(path.read_bytes()) if block == 0],
        )
        for path in sorted((repo_root / "maps").glob("*.blk"))
        if 0 in path.read_bytes()
    ] == [("CinnabarIslandCrystalLegends.blk", [23])]

    stock_meta = (repo_root / "data/tilesets/kanto_metatiles.bin").read_bytes()
    custom_meta = (
        repo_root / "data/tilesets/kanto_metatiles_crystallegends.bin"
    ).read_bytes()
    assert len(stock_meta) == len(custom_meta) == 0x800
    assert custom_meta[:16] == bytes([0x11] * 12 + [0x37, 0x34, 0x00, 0x0D])
    assert custom_meta[16:] == stock_meta[16:]

    stock_tiles = _png_tiles(repo_root / "gfx/tilesets/kanto.png")
    custom_tiles = _png_tiles(repo_root / "gfx/tilesets/kanto_crystallegends.png")
    cave_tiles = _png_tiles(repo_root / "gfx/tilesets/cave.png")
    changed = [index for index, pair in enumerate(zip(stock_tiles, custom_tiles)) if pair[0] != pair[1]]
    assert changed == [0x00, 0x0D]
    assert custom_tiles[0x00] == cave_tiles[0x36]
    assert custom_tiles[0x0D] == cave_tiles[0x37]

    collision_source = (repo_root / "data/tilesets/kanto_collision.asm").read_text()
    assert parse_collision_rows(collision_source)[0] == (
        "HOP_DOWN",
        "FLOOR",
        "WALL",
        "FLOOR",
    )
    assert parse_collision_rows(collision_source, REFERENCE)[0] == (
        "CUT_TREE",
        "CUT_TREE",
        "CUT_TREE",
        "CUT_TREE",
    )

    dimensions = {"CinnabarIsland": MapDimensions("CinnabarIsland", 10, 9)}
    resolved = {"CinnabarIsland": "maps/CinnabarIslandCrystalLegends.blk"}
    tilesets = parse_map_tilesets((repo_root / "data/maps/maps.asm").read_text())
    assert collision_at(
        repo_root, "CinnabarIsland", (7, 5), dimensions, resolved, tilesets
    ) == "FLOOR"
    assert collision_at(
        repo_root, "CinnabarIsland", (7, 4), dimensions, resolved, tilesets
    ) == "FLOOR"
    assert collision_at(
        repo_root, "CinnabarIsland", (13, 6), dimensions, resolved, tilesets
    ) == "FLOOR"


def test_phase_9_starter_source_is_absent_from_reference_builds(repo_root: Path) -> None:
    paths = (
        "maps/CeladonGym.asm",
        "maps/CeladonCity.asm",
        "maps/CeruleanGym.asm",
        "maps/SeafoamGym.asm",
        "maps/CinnabarPokecenter1F.asm",
        "maps/CinnabarIsland.asm",
    )
    forbidden = (
        "BULBASAUR, 28",
        "SQUIRTLE, 28",
        "CHARMANDER, 28",
        "BLAINES_LOG",
        "EVENT_HELPED_ERIKA_CLEAN_CELADON_POND",
    )
    for relative in paths:
        reference = _active_code(repo_root / relative, REFERENCE)
        assert all(not any(value in line for line in reference) for value in forbidden)


def test_custom_block_zero_collision_guard_preserves_reference_lookup(
    repo_root: Path,
) -> None:
    path = repo_root / "home/map.asm"
    custom = _active_code(path, CRYSTAL_LEGENDS)
    reference = _active_code(path, REFERENCE)
    _assert_contiguous(
        custom,
        [
            "GetCoordTileCollision::",
            "call GetBlockLocation",
            "ld a, [hl]",
            "call CheckCurrentMapBlockZero",
            "ld l, a",
        ],
    )
    _assert_contiguous(
        _active_code(repo_root / "home.asm", CRYSTAL_LEGENDS),
        [
            "CheckCurrentMapBlockZero:",
            "and a",
            "ret nz",
            "ld a, [wMapWidth]",
            "cp 4",
            "jr c, .sentinel",
            "ld a, d",
            "and $fe",
            "cp 3 * 2 + 4",
            "jr nz, .sentinel",
            "ld a, e",
            "and $fe",
            "cp 2 * 2 + 4",
            "jr nz, .sentinel",
            "xor a",
            "ret",
            ".sentinel:",
            "pop hl",
            "jp GetCoordTileCollision.nope",
        ],
    )
    _assert_contiguous(
        reference,
        [
            "GetCoordTileCollision::",
            "call GetBlockLocation",
            "ld a, [hl]",
            "and a",
            "jr z, .nope",
            "ld l, a",
        ],
    )
