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
from tests.support.map_model import (
    MapDimensions,
    map_sources_from_repository,
    parse_events,
    parse_map_dimensions,
)


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


def _dialogue(lines: list[str], label: str) -> str:
    paragraphs: list[list[str]] = [[]]
    for line in lines[lines.index(label) + 1 :]:
        if line in {"done", "prompt"}:
            break
        match = re.fullmatch(r'(text|line|cont|para) "(.*)"', line)
        if match is None:
            continue
        command, value = match.groups()
        if command == "para":
            paragraphs.append([])
        paragraphs[-1].append(value)

    def join_wrapped_text(paragraph: list[str]) -> str:
        joined = paragraph[0]
        for value in paragraph[1:]:
            joined += ("" if joined.endswith("-") else " ") + value
        return joined

    return " ¶ ".join(join_wrapped_text(paragraph) for paragraph in paragraphs)


def _png_tiles(path: Path, *, expected_height: int = 48) -> tuple[tuple[int, ...], ...]:
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
    assert (width, height, depth, color_type) == (128, expected_height, 2, 0)
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
        for tile_y in range(expected_height // 8)
        for tile_x in range(16)
    )


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_09_kanto_completion.json").read_text()
    )


def test_phase_9_contract_locks_the_three_starter_rewards(scenario: dict) -> None:
    assert scenario["scenario_id"] == "phase-09-kanto-completion"
    assert scenario["events"] == {"first": 2015, "last": 2037, "count": 23}
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
        "entry_coordinates": [[13, 18], [14, 18], [15, 18]],
        "species": "MUK",
        "level": 35,
        "request_event": "EVENT_ERIKA_REQUESTED_CELADON_POND_HELP",
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
        "EVENT_ERIKA_REQUESTED_CELADON_POND_HELP",
        "EVENT_BLAINE_REQUESTED_CINNABAR_HELP",
        "EVENT_SEAFOAM_ISLANDS_CAVE_ULTRA_BALL",
        "EVENT_SEAFOAM_ISLANDS_CAVE_HIDDEN_NEVERMELTICE",
        "EVENT_POWER_PLANT_GENERATOR_ANNEX_MAGNET",
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
    assert "const_skip 23" in reference


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
            "special SetErikaStarterOT",
            "setevent EVENT_GOT_BULBASAUR_FROM_ERIKA",
        ],
    )
    _assert_in_order(
        erika,
        [
            ".RequestPondHelp:",
            "setevent EVENT_ERIKA_REQUESTED_CELADON_POND_HELP",
            "writetext ErikaPondRequestText",
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
            "special SetMistyStarterOT",
            "setevent EVENT_GOT_SQUIRTLE_FROM_MISTY",
        ],
    )
    _assert_in_order(
        blaine,
        [
            "checkevent EVENT_RETURNED_BLAINES_LOG",
            "checkitem BLAINES_LOG",
            "writetext BlaineLogRequestText",
            "waitbutton",
            "setevent EVENT_BLAINE_REQUESTED_CINNABAR_HELP",
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
            "special SetBlaineStarterOT",
            "setevent EVENT_GOT_CHARMANDER_FROM_BLAINE",
        ],
    )
    for lines, prefix in ((erika, "ERIKA:"), (misty, "MISTY:"), (blaine, "BLAINE:")):
        assert any(line.startswith(f'text "{prefix}') for line in lines)

    move_mon = _active_code(
        repo_root / "engine/events/kanto_starter_ot.asm", CRYSTAL_LEGENDS
    )
    _assert_in_order(
        move_mon,
        [
            "SetErikaStarterOT:",
            'db "ERIKA@"',
            'db "MISTY@"',
            'db "BLAINE@"',
        ],
    )
    assert "SetLatestStarterOT:" in move_mon
    reference_main = _active_code(repo_root / "main.asm", REFERENCE)
    assert 'INCLUDE "engine/events/kanto_starter_ot.asm"' not in reference_main


def test_phase_9_review_dialogue_matches_the_approved_copy(repo_root: Path) -> None:
    misty = _active_code(repo_root / "maps/CeruleanGym.asm", CRYSTAL_LEGENDS)
    assert _dialogue(misty, "MistySquirtleOfferText:") == (
        "MISTY: You brought back the power to KANTO. ¶ CERULEAN owes you. ¶ "
        "I want to entrust SQUIRTLE to you. ¶ Will you take it?"
    )

    blaine = _active_code(repo_root / "maps/SeafoamGym.asm", CRYSTAL_LEGENDS)
    assert _dialogue(blaine, "BlaineLogRequestText:") == (
        "BLAINE: I hope something survived my old CINNABAR GYM. ¶ "
        "My early training log was evacuated but never found."
    )

    pokecenter = _active_code(
        repo_root / "maps/CinnabarPokecenter1F.asm", CRYSTAL_LEGENDS
    )
    assert _dialogue(pokecenter, "CinnabarPokecenter1FCooltrainerFLogText:") == (
        "The fisherman saw the cases moved from the old GYM."
    )
    assert _dialogue(pokecenter, "CinnabarPokecenter1FFisherLogClueText:") == (
        "I saw a flame-crested case after the volcano. ¶ "
        "It lies somewhere in the rubble. ¶ Its clasp has a secret mechanism. "
        "¶ Press the crest in and pull the latch sideways."
    )
    assert _dialogue(pokecenter, "CinnabarPokecenter1FFisherRecoveredText:") == (
        "You got the old case! ¶ BLAINE will want that log back."
    )
    assert not any("FISHERMAN:" in line for line in pokecenter)

    wardens_home = _active_code(
        repo_root / "maps/SafariZoneWardensHome.asm", CRYSTAL_LEGENDS
    )
    assert _dialogue(wardens_home, "WardensGranddaughterReleaseGateText:") == (
        "That SOULBADGE proves you're capable. ¶ "
        "Feel free to explore the SAFARI ZONE."
    )
    assert _dialogue(wardens_home, "WardensGranddaughterUnattendedText:") == (
        "The north gate is open at your own risk. ¶ There are no staff, "
        "rescue service or official SAFARI GAME."
    )
    assert not any("GRANDDAUGHTER:" in line for line in wardens_home)

    fuchsia = _active_code(repo_root / "maps/FuchsiaCity.asm", CRYSTAL_LEGENDS)
    assert _dialogue(fuchsia, "FuchsiaCityTeacherGranddaughterText:") == (
        "The SAFARI ZONE is still closed. ¶ The WARDEN'S granddaughter may "
        "know about the old gate."
    )

    celadon = _active_code(repo_root / "maps/CeladonCity.asm", CRYSTAL_LEGENDS)
    assert _dialogue(celadon, "CeladonCityMukPondBattleText:") == (
        "A MUK is churning the polluted pond. ¶ "
        "The MUK surges out of the sludge!"
    )

    cinnabar = _active_code(repo_root / "maps/CinnabarIsland.asm", CRYSTAL_LEGENDS)
    assert _dialogue(cinnabar, "CinnabarIslandBlainesLogStuckText:") == (
        "There's a flame-crested case stuck under the rubble. ¶ "
        "Its clasp won't open."
    )
    assert _dialogue(cinnabar, "CinnabarIslandBlainesLogReleaseText:") == (
        "Press the crest in and pull the latch sideways. ¶ The case opens!"
    )

    common = _active_code(repo_root / "data/text/common_3.asm", CRYSTAL_LEGENDS)
    assert _dialogue(common, "SafariZoneBetaUnattendedSignText::") == (
        "PRESERVE NOTICE ¶ These grounds are unattended. ¶ Explore at your own risk."
    )
    assert _dialogue(common, "SafariZoneBetaNormalBattleSignText::") == (
        "TRAINER NOTICE ¶ Wild #MON use ordinary battles ¶ and capture rules."
    )
    assert _dialogue(common, "Phase9PowerPlantManagerAnnexAuthorizationText::") == (
        "MANAGER: Hey! The auxiliary generator voltage is way too high! ¶ "
        "I'm authorizing you to investigate."
    )


def test_erika_muk_and_blaine_log_retry_only_after_success(
    repo_root: Path, scenario: dict
) -> None:
    celadon = _active_code(repo_root / "maps/CeladonCity.asm", CRYSTAL_LEGENDS)
    entry = _section(
        celadon, "CeladonCityMukPondEntry:", "CeladonCityMukPondEncounter:"
    )
    _assert_in_order(
        entry,
        [
            "checkevent EVENT_ERIKA_REQUESTED_CELADON_POND_HELP",
            "checkevent EVENT_HELPED_ERIKA_CLEAN_CELADON_POND",
            "sjump CeladonCityMukPondEncounter",
        ],
    )
    pond = _section(
        celadon, "CeladonCityMukPondEncounter:", "CeladonCityFisherText:"
    )
    _assert_in_order(
        pond,
        [
            "loadwildmon MUK, 35",
            "startbattle",
            "ifequal LOSE, .Retry",
            "ifequal DRAW, .Retry",
            "setevent EVENT_HELPED_ERIKA_CLEAN_CELADON_POND",
        ],
    )
    for x in (13, 14, 15):
        assert (
            f"coord_event {x}, 18, SCENE_ALWAYS, CeladonCityMukPondEntry"
            in celadon
        )
    assert not any("BGEVENT_READ, CeladonCityMukPond" in line for line in celadon)

    island = _active_code(repo_root / "maps/CinnabarIsland.asm", CRYSTAL_LEGENDS)
    case = _section(
        island, "CinnabarIslandBlainesLogRubble:", "CinnabarIslandBlueTeleport:"
    )
    _assert_in_order(
        case,
        [
            "checkevent EVENT_RECOVERED_BLAINES_LOG",
            "iftrue .Empty",
            "checkevent EVENT_LEARNED_LOCATION_OF_BLAINES_LOG",
            "verbosegiveitem BLAINES_LOG",
            "iffalse .NoRoom",
            "setevent EVENT_RECOVERED_BLAINES_LOG",
        ],
    )
    case_x, case_y = scenario["blaines_log"]["case_coordinate"]
    assert not any(
        line.startswith(f"bg_event {case_x:2}, {case_y:2}") for line in island
    )
    assert any(
        line.startswith(
            f"object_event {case_x:2}, {case_y:2}, "
            "SPRITE_BOULDER, SPRITEMOVEDATA_STILL"
        )
        and "PAL_NPC_BROWN, OBJECTTYPE_SCRIPT, 0, "
        "CinnabarIslandBlainesLogRubble, -1" in line
        for line in island
    )
    decorative = _section(
        island,
        "CinnabarIslandDecorativeBoulder:",
        "CinnabarIslandBlainesLogRubble:",
    )
    assert decorative == ["CinnabarIslandDecorativeBoulder:", "end"]
    for rock_x, rock_y in scenario["blaines_log"][
        "decorative_rock_coordinates"
    ]:
        assert any(
            line.startswith(
                f"object_event {rock_x:2}, {rock_y:2}, "
                "SPRITE_BOULDER, SPRITEMOVEDATA_STILL"
            )
            and "PAL_NPC_BROWN, OBJECTTYPE_SCRIPT, 0, "
            "CinnabarIslandDecorativeBoulder, -1" in line
            for line in island
        )
    assert not any("CinnabarIslandOldGymRemains" in line for line in island)
    assert not any("CinnabarIslandOldLabRemains" in line for line in island)

    pokecenter = _active_code(
        repo_root / "maps/CinnabarPokecenter1F.asm", CRYSTAL_LEGENDS
    )
    cooltrainer = _section(
        pokecenter,
        "CinnabarPokecenter1FCooltrainerFScript:",
        "CinnabarPokecenter1FFisherScript:",
    )
    fisherman = _section(
        pokecenter,
        "CinnabarPokecenter1FFisherScript:",
        "CinnabarPokecenter1FCooltrainerFText:",
    )
    assert "checkevent EVENT_BLAINE_REQUESTED_CINNABAR_HELP" in cooltrainer
    assert "checkevent EVENT_BLAINE_REQUESTED_CINNABAR_HELP" in fisherman
    assert "checkflag ENGINE_VOLCANOBADGE" not in cooltrainer
    assert "checkflag ENGINE_VOLCANOBADGE" not in fisherman


def test_phase_9_kanto_assets_change_only_stairs_and_safari_gate(
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
    ] == [
        (
            scenario["blaines_log"]["staircase"]["block_offset"],
            0x24,
            scenario["blaines_log"]["staircase"]["custom_block"],
        ),
    ]

    stock_meta = (repo_root / "data/tilesets/kanto_metatiles.bin").read_bytes()
    custom_meta = (
        repo_root / "data/tilesets/kanto_metatiles_crystallegends.bin"
    ).read_bytes()
    assert len(stock_meta) == len(custom_meta) == 0x800
    staircase_block = scenario["blaines_log"]["staircase"]["custom_block"]
    assert custom_meta[:16] == stock_meta[:16]
    assert custom_meta[staircase_block * 16 : (staircase_block + 1) * 16] == bytes(
        [0x27, 0x27, 0x11, 0x11]
        + [0x27, 0x27, 0x11, 0x11]
        + [0x27, 0x36, 0x00, 0x00]
        + [0x36, 0x37, 0x00, 0x00]
    )
    changed_metatiles = [
        index
        for index in range(len(stock_meta) // 16)
        if stock_meta[index * 16 : (index + 1) * 16]
        != custom_meta[index * 16 : (index + 1) * 16]
    ]
    assert changed_metatiles == [
        scenario["safari"]["fuchsia_gate"]["open_block"],
        staircase_block,
    ]
    gate = scenario["safari"]["fuchsia_gate"]
    assert custom_meta[0x470:0x480] == bytes(gate["metatile"])

    stock_tiles = _png_tiles(repo_root / "gfx/tilesets/kanto.png")
    custom_tiles = _png_tiles(repo_root / "gfx/tilesets/kanto_crystallegends.png")
    cave_tiles = _png_tiles(repo_root / "gfx/tilesets/cave.png")
    changed = [index for index, pair in enumerate(zip(stock_tiles, custom_tiles)) if pair[0] != pair[1]]
    assert changed == [0x00]
    assert custom_tiles[0x00] == cave_tiles[0x37]

    collision_source = (repo_root / "data/tilesets/kanto_collision.asm").read_text()
    assert parse_collision_rows(collision_source)[0] == (
        "CUT_TREE",
        "CUT_TREE",
        "CUT_TREE",
        "CUT_TREE",
    )
    assert parse_collision_rows(collision_source)[staircase_block] == tuple(
        scenario["blaines_log"]["staircase"]["collision"]
    )
    assert parse_collision_rows(collision_source, REFERENCE)[staircase_block] == (
        "HOP_DOWN_RIGHT",
        "WALL",
        "WALL",
        "WALL",
    )
    assert parse_collision_rows(collision_source)[gate["open_block"]] == tuple(
        gate["open_collision"]
    )
    assert parse_collision_rows(collision_source, REFERENCE)[gate["open_block"]] == (
        "HOP_RIGHT",
        "WALL",
        "HOP_RIGHT",
        "WALL",
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
        repo_root, "CinnabarIsland", (6, 4), dimensions, resolved, tilesets
    ) == "WALL"

    def walk_tile_graphics(coordinate: tuple[int, int]) -> bytes:
        x, y = coordinate
        block = custom_blocks[(y // 2) * 10 + (x // 2)]
        metatile = custom_meta[block * 16 : (block + 1) * 16]
        row = (y % 2) * 2
        column = (x % 2) * 2
        return bytes(
            (
                metatile[row * 4 + column],
                metatile[row * 4 + column + 1],
                metatile[(row + 1) * 4 + column],
                metatile[(row + 1) * 4 + column + 1],
            )
        )

    for target, source in scenario["blaines_log"]["staircase"][
        "appearance_matches"
    ]:
        assert walk_tile_graphics(tuple(target)) == walk_tile_graphics(tuple(source))

    custom_sprites = _active_code(
        repo_root / "data/maps/outdoor_sprites.asm", CRYSTAL_LEGENDS
    )
    reference_sprites = _active_code(
        repo_root / "data/maps/outdoor_sprites.asm", REFERENCE
    )
    custom_group = _section(
        custom_sprites, "CinnabarGroupSprites:", "CeruleanGroupSprites:"
    )
    reference_group = _section(
        reference_sprites, "CinnabarGroupSprites:", "CeruleanGroupSprites:"
    )
    assert "db SPRITE_BOULDER" in custom_group
    assert "db SPRITE_FRUIT_TREE" not in custom_group
    assert "db SPRITE_BOULDER" not in reference_group
    assert "db SPRITE_FRUIT_TREE" in reference_group
    case_coordinate = tuple(scenario["blaines_log"]["case_coordinate"])
    assert collision_at(
        repo_root, "CinnabarIsland", case_coordinate, dimensions, resolved, tilesets
    ) == "FLOOR"  # the visible boulder object owns this coordinate's collision

    reference_tilesets = parse_map_tilesets(
        (repo_root / "data/maps/maps.asm").read_text(), REFERENCE
    )
    reference_paths = parse_block_paths(blocks_source, REFERENCE)
    stock_kanto_maps = [
        map_name
        for map_name, tileset in reference_tilesets.items()
        if tileset == "TILESET_KANTO"
    ]
    assert len(stock_kanto_maps) == 39
    paths_by_normalized = {
        re.sub(r"[^A-Z0-9]", "", map_name.upper()): path
        for map_name, path in reference_paths.items()
    }
    assert all(
        gate["open_block"] not in (repo_root / paths_by_normalized[map_name]).read_bytes()
        for map_name in stock_kanto_maps
    )


def test_safari_access_is_owned_by_the_granddaughter_and_opens_one_door(
    repo_root: Path, scenario: dict
) -> None:
    safari = scenario["safari"]
    owner = safari["quest_owner"]
    home = _active_code(repo_root / "maps/SafariZoneWardensHome.asm", CRYSTAL_LEGENDS)
    script = _section(home, f'{owner["script"]}:', "WardenPhoto:")
    _assert_in_order(
        script,
        [
            f'checkevent {owner["access_event"]}',
            f'checkevent {owner["first_talk_event"]}',
            f'setevent {owner["first_talk_event"]}',
            f'checkflag {owner["badge"]}',
            f'setevent {owner["access_event"]}',
        ],
    )
    assert sum(line == f'setevent {owner["access_event"]}' for line in home) == 1
    assert any(
        line.startswith("object_event  2,  4, SPRITE_LASS")
        and f", {owner['script']}, -1" in line
        for line in home
    )

    mutations: list[str] = []
    for source in (repo_root / "maps").glob("*.asm"):
        if f'setevent {owner["access_event"]}' in _active_code(source, CRYSTAL_LEGENDS):
            mutations.append(source.name)
    assert mutations == ["SafariZoneWardensHome.asm"]

    gate = safari["fuchsia_gate"]
    city = _active_code(repo_root / "maps/FuchsiaCity.asm", CRYSTAL_LEGENDS)
    _assert_contiguous(
        city,
        [
            "FuchsiaCitySafariGateCallback:",
            f'checkevent {owner["access_event"]}',
            "iffalse .Locked",
            f'changeblock {gate["block_coordinate"][0]}, {gate["block_coordinate"][1]}, ${gate["open_block"]:02x}',
            ".Locked:",
            "endcallback",
        ],
    )
    assert (
        f'warp_event {gate["warp"][0]:2}, {gate["warp"][1]:2}, '
        f'{gate["warp"][2]}, {gate["warp"][3]}'
    ) in city
    assert "SAFARI ZONE OFFICE" in "\n".join(city)
    assert "SAFARI GAME" not in "\n".join(city)


def test_safari_beta_maps_preserve_warps_and_add_only_approved_interactions(
    repo_root: Path, scenario: dict
) -> None:
    safari = scenario["safari"]
    dimensions = parse_map_dimensions(
        (repo_root / "constants/map_constants.asm").read_text()
    )
    assert [
        dimensions["SAFARI_ZONE_FUCHSIA_GATE_BETA"].width_blocks,
        dimensions["SAFARI_ZONE_FUCHSIA_GATE_BETA"].height_blocks,
    ] == safari["maintenance_gate"]["dimensions"]
    assert [
        dimensions["SAFARI_ZONE_BETA"].width_blocks,
        dimensions["SAFARI_ZONE_BETA"].height_blocks,
    ] == safari["preserve"]["dimensions"]

    blocks = (repo_root / "data/maps/blocks.asm").read_text()
    assert parse_block_paths(blocks)["SafariZoneFuchsiaGateBeta"] == safari[
        "maintenance_gate"
    ]["block_path"]
    assert parse_block_paths(blocks)["SafariZoneBeta"] == safari["preserve"][
        "custom_block_path"
    ]
    assert parse_block_paths(blocks, REFERENCE)["SafariZoneBeta"] == safari[
        "preserve"
    ]["stock_block_path"]
    custom_blocks = (repo_root / safari["preserve"]["custom_block_path"]).read_bytes()
    stock_blocks = (repo_root / safari["preserve"]["stock_block_path"]).read_bytes()
    assert len(custom_blocks) == len(stock_blocks) == 180
    assert custom_blocks != stock_blocks

    preserve = safari["preserve"]
    first_custom, last_custom = preserve["custom_metatile_range"]
    extra_metatiles = (repo_root / preserve["custom_metatile_path"]).read_bytes()
    assert len(extra_metatiles) == (last_custom - first_custom + 1) * 16
    assert max(custom_blocks) == last_custom
    base_metatiles = (repo_root / "data/tilesets/park_metatiles.bin").read_bytes()
    combined_metatiles = base_metatiles + extra_metatiles

    def metatile(block_id: int) -> bytes:
        return combined_metatiles[block_id * 16 : (block_id + 1) * 16]

    water = 0x14
    gray_shore = preserve["gray_shore_tile"]
    stock_shore = preserve["stock_shore_tile"]

    def with_gray_shore(block_id: int) -> bytes:
        return metatile(block_id).replace(bytes([stock_shore]), bytes([gray_shore]))

    assert gray_shore not in base_metatiles
    assert stock_shore not in extra_metatiles[: 8 * 16]
    assert metatile(0x40) == with_gray_shore(0x08)
    assert metatile(0x41) == bytes([gray_shore] * 4 + [water] * 12)
    assert metatile(0x42) == with_gray_shore(0x09)
    assert metatile(0x43) == bytes([gray_shore, water, water, water] * 4)
    assert metatile(0x44) == bytes([water, water, water, gray_shore] * 4)
    assert metatile(0x45) == with_gray_shore(0x0C)
    assert metatile(0x46) == bytes([water] * 12 + [gray_shore] * 4)
    assert metatile(0x47) == with_gray_shore(0x0D)
    assert metatile(0x48) == bytes(
        [0x00, 0x16, 0x45, 0x46, 0x06, 0x00, 0x55, 0x56,
         0x00, 0x16, 0x00, 0x16, 0x06, 0x00, 0x06, 0x00]
    )
    assert metatile(0x49) == bytes(
        [0x00, 0x16, 0x00, 0x16, 0x06, 0x00, 0x06, 0x00,
         0x00, 0x16, 0x4F, 0x4F, 0x06, 0x00, 0x4F, 0x4F]
    )
    assert metatile(0x4A) == bytes(
        [0x00, 0x16, 0x00, 0x16, 0x06, 0x00, 0x06, 0x00,
         0x4F, 0x4F, 0x00, 0x16, 0x4F, 0x4F, 0x06, 0x00]
    )
    gfx = repo_root / "gfx/tilesets.asm"
    extra_incbin = f'INCBIN "{preserve["custom_metatile_path"]}"'
    assert extra_incbin in _active_code(gfx, CRYSTAL_LEGENDS)
    assert extra_incbin not in _active_code(gfx, REFERENCE)
    assert (
        'INCBIN "gfx/tilesets/park_crystallegends.2bpp.lz"'
        in _active_code(gfx, CRYSTAL_LEGENDS)
    )
    assert (
        'INCBIN "gfx/tilesets/park_crystallegends.2bpp.lz"'
        not in _active_code(gfx, REFERENCE)
    )
    assert (
        'INCBIN "gfx/tilesets/park.2bpp.lz"'
        in _active_code(gfx, REFERENCE)
    )

    stock_tiles = _png_tiles(
        repo_root / "gfx/tilesets/park.png", expected_height=96
    )
    custom_tiles = _png_tiles(
        repo_root / preserve["custom_gfx_path"], expected_height=96
    )
    changed_tiles = [
        index
        for index, (stock, custom) in enumerate(zip(stock_tiles, custom_tiles))
        if stock != custom
    ]
    assert changed_tiles == [gray_shore]
    assert custom_tiles[gray_shore] == stock_tiles[stock_shore]

    collision_source = (repo_root / "data/tilesets/park_collision.asm").read_text()
    custom_collisions = parse_collision_rows(collision_source)
    reference_collisions = parse_collision_rows(collision_source, REFERENCE)
    assert len(custom_collisions) == last_custom + 1
    assert len(reference_collisions) == first_custom
    assert custom_collisions[0x40:0x48] == [("WATER",) * 4] * 8
    assert custom_collisions[0x48] == ("FLOOR", "WALL", "FLOOR", "FLOOR")
    assert custom_collisions[0x49] == (
        "FLOOR",
        "FLOOR",
        "FLOOR",
        "WARP_CARPET_DOWN",
    )
    assert custom_collisions[0x4A] == (
        "FLOOR",
        "FLOOR",
        "WARP_CARPET_DOWN",
        "FLOOR",
    )
    sources = {source.map_name: source for source in map_sources_from_repository(repo_root)}
    gate_events = parse_events(sources["SAFARI_ZONE_FUCHSIA_GATE_BETA"])
    preserve_events = parse_events(sources["SAFARI_ZONE_BETA"])
    reference_gate_events = parse_events(
        sources["SAFARI_ZONE_FUCHSIA_GATE_BETA"], REFERENCE
    )
    reference_preserve_events = parse_events(sources["SAFARI_ZONE_BETA"], REFERENCE)

    def event_args(events, event_type: str) -> list[list[str]]:
        return [list(event.args) for event in events if event.event_type == event_type]

    expected_gate_warps = [
        [str(x), str(y), destination, str(warp)]
        for x, y, destination, warp in safari["maintenance_gate"]["warps"]
    ]
    expected_preserve_warps = [
        [str(x), str(y), destination, str(warp)]
        for x, y, destination, warp in safari["preserve"]["warps"]
    ]
    assert event_args(gate_events, "warp_event") == expected_gate_warps
    assert event_args(reference_gate_events, "warp_event") == expected_gate_warps
    assert event_args(preserve_events, "warp_event") == expected_preserve_warps
    assert event_args(reference_preserve_events, "warp_event") == expected_preserve_warps
    assert event_args(gate_events, "object_event") == []
    assert event_args(reference_gate_events, "object_event") == []
    assert [
        [event.x, event.y]
        for event in gate_events
        if event.event_type == "bg_event"
    ] == safari["maintenance_gate"]["notice_coordinates"]
    assert [
        [event.x, event.y]
        for event in preserve_events
        if event.event_type == "bg_event"
    ] == safari["preserve"]["sign_coordinates"]
    assert event_args(reference_preserve_events, "bg_event") == []

    objects = [event for event in preserve_events if event.event_type == "object_event"]
    assert len(objects) == 2
    assert all(event.args[2] == "SPRITE_POKE_BALL" for event in objects)
    assert all(event.args[9] == "OBJECTTYPE_ITEMBALL" for event in objects)
    assert [
        ([event.x, event.y], event.args[11], event.args[12]) for event in objects
    ] == [
        (pickup["coordinate"], pickup["script"], pickup["event"])
        for pickup in safari["preserve"]["pickups"]
    ]
    assert event_args(reference_preserve_events, "object_event") == []


def test_safari_layout_is_reachable_without_surf_and_metadata_is_conditional(
    repo_root: Path, scenario: dict
) -> None:
    safari = scenario["safari"]
    preserve = safari["preserve"]
    dimensions = {
        "SAFARI_ZONE_BETA": MapDimensions(
            "SAFARI_ZONE_BETA", *preserve["dimensions"]
        )
    }
    resolved = {"SAFARI_ZONE_BETA": preserve["custom_block_path"]}
    maps_source = (repo_root / "data/maps/maps.asm").read_text()
    tilesets = parse_map_tilesets(maps_source)
    blocks = (repo_root / preserve["custom_block_path"]).read_bytes()

    def block_at(x: int, y: int) -> int:
        return blocks[(y // 2) * preserve["dimensions"][0] + x // 2]

    pond = preserve["pond"]
    pond_blocks = [
        [block_at(x, y) for x in range(pond["x_range"][0], pond["x_range"][1] + 1, 2)]
        for y in range(pond["y_range"][0], pond["y_range"][1] + 1, 2)
    ]
    assert pond_blocks == pond["block_ids"]
    for y in range(pond["y_range"][0], pond["y_range"][1] + 1):
        for x in range(pond["x_range"][0], pond["x_range"][1] + 1):
            assert collision_at(
                repo_root,
                "SAFARI_ZONE_BETA",
                (x, y),
                dimensions,
                resolved,
                tilesets,
            ) == pond["collision"]

    for coordinate in preserve["tree_tiles"]:
        assert block_at(*coordinate) == 0x06
        assert collision_at(
            repo_root,
            "SAFARI_ZONE_BETA",
            tuple(coordinate),
            dimensions,
            resolved,
            tilesets,
        ) == "WALL"

    for rectangle in preserve["grass_rectangles"]:
        for y in range(rectangle["y_range"][0], rectangle["y_range"][1] + 1):
            for x in range(rectangle["x_range"][0], rectangle["x_range"][1] + 1):
                assert collision_at(
                    repo_root,
                    "SAFARI_ZONE_BETA",
                    (x, y),
                    dimensions,
                    resolved,
                    tilesets,
                ) == "TALL_GRASS"

    assert [block_at(*coordinate) for coordinate in preserve["sign_coordinates"]] == [
        0x15,
        0x48,
    ]
    assert all(
        collision_at(
            repo_root,
            "SAFARI_ZONE_BETA",
            tuple(coordinate),
            dimensions,
            resolved,
            tilesets,
        )
        == "WALL"
        for coordinate in preserve["sign_coordinates"]
    )
    assert [
        collision_at(
            repo_root,
            "SAFARI_ZONE_BETA",
            tuple(coordinate),
            dimensions,
            resolved,
            tilesets,
        )
        for coordinate in preserve["old_sign_coordinates"]
    ] == preserve["old_sign_collisions"]

    passable = {"FLOOR", "TALL_GRASS", "LONG_GRASS", "WARP_CARPET_DOWN"}
    start = (9, 22)
    seen = {start}
    pending = [start]
    while pending:
        x, y = pending.pop()
        for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if neighbor in seen:
                continue
            nx, ny = neighbor
            if not (0 <= nx < 20 and 0 <= ny < 36):
                continue
            if (
                collision_at(
                    repo_root,
                    "SAFARI_ZONE_BETA",
                    neighbor,
                    dimensions,
                    resolved,
                    tilesets,
                )
                not in passable
            ):
                continue
            seen.add(neighbor)
            pending.append(neighbor)

    for pickup in preserve["pickups"]:
        assert tuple(pickup["coordinate"]) in seen
        assert (
            collision_at(
                repo_root,
                "SAFARI_ZONE_BETA",
                tuple(pickup["coordinate"]),
                dimensions,
                resolved,
                tilesets,
            )
            == pickup["collision"]
        )
    for sign in preserve["sign_coordinates"]:
        x, y = sign
        assert any((x + dx, y + dy) in seen for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)))
    assert (9, 23) in seen and (10, 23) in seen
    assert all(
        collision_at(
            repo_root,
            "SAFARI_ZONE_BETA",
            tuple(warp[:2]),
            dimensions,
            resolved,
            tilesets,
        )
        == "WARP_CARPET_DOWN"
        for warp in preserve["warps"]
    )
    assert all(
        collision_at(
            repo_root,
            "SAFARI_ZONE_BETA",
            tuple(coordinate),
            dimensions,
            resolved,
            tilesets,
        )
        == "FLOOR"
        for coordinate in preserve["exit_floor_coordinates"]
    )
    assert any(
        collision_at(
            repo_root,
            "SAFARI_ZONE_BETA",
            coordinate,
            dimensions,
            resolved,
            tilesets,
        )
        == "TALL_GRASS"
        for coordinate in seen
    )
    assert any(
        collision_at(
            repo_root,
            "SAFARI_ZONE_BETA",
            (x, y),
            dimensions,
            resolved,
            tilesets,
        )
        == preserve["water_collision"]["custom"]
        for y in range(36)
        for x in range(20)
    )
    park_collision = (repo_root / "data/tilesets/park_collision.asm").read_text()
    water_block = preserve["water_collision"]["block"]
    assert parse_collision_rows(park_collision)[water_block] == (
        preserve["water_collision"]["custom"],
    ) * 4
    assert parse_collision_rows(park_collision, REFERENCE)[water_block] == (
        preserve["water_collision"]["reference"],
    ) * 4

    custom_map = next(
        line
        for line in _active_code(repo_root / "data/maps/maps.asm", CRYSTAL_LEGENDS)
        if line.startswith("map SafariZoneBeta,")
    )
    assert custom_map == "map SafariZoneBeta, " + ", ".join(preserve["metadata"])
    reference_map = next(
        line
        for line in _active_code(repo_root / "data/maps/maps.asm", REFERENCE)
        if line.startswith("map SafariZoneBeta,")
    )
    assert reference_map == (
        "map SafariZoneBeta, TILESET_PARK, CAVE, LANDMARK_FUCHSIA_CITY, "
        "MUSIC_EVOLUTION, FALSE, PALETTE_AUTO, FISHGROUP_SHORE"
    )


def test_safari_wild_tables_and_item_scripts_match_the_contract(
    repo_root: Path, scenario: dict
) -> None:
    safari = scenario["safari"]
    grass_lines = _active_code(repo_root / "data/wild/kanto_grass.asm", CRYSTAL_LEGENDS)
    grass = _section(
        grass_lines, "def_grass_wildmons SAFARI_ZONE_BETA", "end_grass_wildmons"
    )
    expected_grass = [
        "def_grass_wildmons SAFARI_ZONE_BETA",
        "db 10 percent, 10 percent, 10 percent",
        *(
            f"db {level}, {species}"
            for time in ("morning", "day", "night")
            for level, species in safari["grass"][time]
        ),
    ]
    assert grass == expected_grass

    water_lines = _active_code(repo_root / "data/wild/kanto_water.asm", CRYSTAL_LEGENDS)
    water = _section(
        water_lines, "def_water_wildmons SAFARI_ZONE_BETA", "end_water_wildmons"
    )
    assert water == [
        "def_water_wildmons SAFARI_ZONE_BETA",
        f'db {safari["water"]["rate"]} percent',
        *(f"db {level}, {species}" for level, species in safari["water"]["slots"]),
    ]
    assert "def_grass_wildmons SAFARI_ZONE_BETA" not in _active_code(
        repo_root / "data/wild/kanto_grass.asm", REFERENCE
    )
    assert "def_water_wildmons SAFARI_ZONE_BETA" not in _active_code(
        repo_root / "data/wild/kanto_water.asm", REFERENCE
    )
    assert not any(
        species == "GIRAFARIG"
        for time in ("morning", "day", "night")
        for _, species in safari["grass"][time]
    )

    source = _active_code(repo_root / "maps/SafariZoneBeta.asm", CRYSTAL_LEGENDS)
    for pickup in safari["preserve"]["pickups"]:
        index = source.index(f'{pickup["script"]}:')
        assert source[index + 1] == f'itemball {pickup["item"]}'
    denylist = ("safarigame", "parkball", "bait", "rock", "stepcount", "takemoney")
    safari_sources = "\n".join(
        "\n".join(_active_code(repo_root / relative, CRYSTAL_LEGENDS)).lower()
        for relative in (
            "maps/SafariZoneWardensHome.asm",
            "maps/FuchsiaCity.asm",
            "maps/SafariZoneFuchsiaGateBeta.asm",
            "maps/SafariZoneBeta.asm",
        )
    )
    assert all(token not in safari_sources for token in denylist)


def test_seafoam_reuses_the_beta_block_slot_and_changes_only_locked_blocks(
    repo_root: Path, scenario: dict
) -> None:
    seafoam = scenario["seafoam"]
    blocks_source = (repo_root / "data/maps/blocks.asm").read_text()
    custom_paths = parse_block_paths(blocks_source)
    reference_paths = parse_block_paths(blocks_source, REFERENCE)
    assert custom_paths["Route20"] == seafoam["route20_active_block_path"]
    assert reference_paths["Route20"] == seafoam["route20_stock_block_path"]
    assert custom_paths["BetaUnionCave"] == seafoam["active_block_path"]
    assert custom_paths["SeafoamIslandsCave"] == seafoam["active_block_path"]
    assert reference_paths["BetaUnionCave"] == seafoam["seed_block_path"]
    assert "SeafoamIslandsCave" not in reference_paths

    seed = (repo_root / seafoam["seed_block_path"]).read_bytes()
    active = (repo_root / seafoam["active_block_path"]).read_bytes()
    assert len(seed) == len(active) == 90
    assert [
        {"offset": offset, "old_block": old, "new_block": new}
        for offset, (old, new) in enumerate(zip(seed, active))
        if old != new
    ] == seafoam["layout_delta"]

    tileset_source = repo_root / "gfx/tilesets.asm"
    custom_tileset = _active_code(tileset_source, CRYSTAL_LEGENDS)
    reference_tileset = _active_code(tileset_source, REFERENCE)
    _assert_contiguous(
        custom_tileset,
        [
            "TilesetIcePathMeta::",
            'INCBIN "data/tilesets/ice_path_metatiles.bin"',
            'INCLUDE "data/tilesets/ice_path_crystallegends_metatiles.asm"',
            "TilesetIcePathColl::",
        ],
    )
    assert (
        'INCLUDE "data/tilesets/ice_path_crystallegends_metatiles.asm"'
        not in reference_tileset
    )
    extra_metatiles = _active_code(
        repo_root / "data/tilesets/ice_path_crystallegends_metatiles.asm",
        CRYSTAL_LEGENDS,
    )
    assert extra_metatiles == [
        "db $9a, $19, $19, $9a",
        "db $19, $9b, $19, $19",
        "db $19, $19, $19, $19",
        "db $42, $43, $19, $9b",
        "db $9a, $19, $9a, $9a",
        "db $19, $9a, $19, $19",
        "db $c6, $c7, $c6, $c7",
        "db $d6, $d7, $d6, $d7",
    ]
    collision_source = (
        repo_root / "data/tilesets/ice_path_collision.asm"
    ).read_text()
    custom_collisions = parse_collision_rows(collision_source, CRYSTAL_LEGENDS)
    reference_collisions = parse_collision_rows(collision_source, REFERENCE)
    assert len(custom_collisions) == 66
    assert len(reference_collisions) == 64
    assert list(custom_collisions[64]) == seafoam["custom_metatiles"][
        "visible_exit"
    ]["collision"]
    assert list(custom_collisions[65]) == seafoam["custom_metatiles"][
        "western_ice_start"
    ]["collision"]

    stock_route = (repo_root / seafoam["route20_stock_block_path"]).read_bytes()
    active_route = (repo_root / seafoam["route20_active_block_path"]).read_bytes()
    assert len(stock_route) == len(active_route) == 270
    assert [
        {"offset": offset, "old_block": old, "new_block": new}
        for offset, (old, new) in enumerate(zip(stock_route, active_route))
        if old != new
    ] == [seafoam["route20_block_delta"]]

    dimensions = parse_map_dimensions(
        (repo_root / "constants/map_constants.asm").read_text()
    )
    assert [
        dimensions[seafoam["map"]].width_blocks,
        dimensions[seafoam["map"]].height_blocks,
    ] == seafoam["dimensions"]

    custom_maps = _active_code(repo_root / "data/maps/maps.asm", CRYSTAL_LEGENDS)
    reference_maps = _active_code(repo_root / "data/maps/maps.asm", REFERENCE)
    declaration = "map SeafoamIslandsCave, " + ", ".join(seafoam["metadata"])
    assert declaration in custom_maps
    assert declaration not in reference_maps
    attributes_source = (repo_root / "data/maps/attributes.asm").read_text()
    assert (
        f'map_attributes SeafoamIslandsCave, {seafoam["map"]}, '
        f'${seafoam["border_block"]:02x}' in attributes_source
    )
    assert "INCLUDE \"maps/SeafoamIslandsCave.asm\"" in _active_code(
        repo_root / "data/maps/scripts.asm", CRYSTAL_LEGENDS
    )
    assert "INCLUDE \"maps/SeafoamIslandsCave.asm\"" not in _active_code(
        repo_root / "data/maps/scripts.asm", REFERENCE
    )


def test_seafoam_warps_object_and_articuno_scripts_match_the_contract(
    repo_root: Path, scenario: dict
) -> None:
    seafoam = scenario["seafoam"]
    articuno = seafoam["articuno"]
    sources = {source.map_name: source for source in map_sources_from_repository(repo_root)}
    cave_events = parse_events(sources[seafoam["map"]])
    route_events = parse_events(sources["ROUTE_20"])
    reference_route_events = parse_events(sources["ROUTE_20"], REFERENCE)

    cave_warps = [event for event in cave_events if event.event_type == "warp_event"]
    assert [list(event.args) for event in cave_warps] == [
        [str(value) for value in seafoam["return_warp"][:2]]
        + [seafoam["return_warp"][2], str(seafoam["return_warp"][3])]
    ]
    route_warps = [event for event in route_events if event.event_type == "warp_event"]
    assert [event.args[2] for event in route_warps] == ["SEAFOAM_GYM", seafoam["map"]]
    assert [event.args[2] for event in reference_route_events if event.event_type == "warp_event"] == [
        "SEAFOAM_GYM"
    ]

    objects = [event for event in cave_events if event.event_type == "object_event"]
    assert len(objects) == 2
    bird = next(
        event for event in objects if event.args[11] == "SeafoamIslandsCaveArticuno"
    )
    assert [bird.x, bird.y] == articuno["coordinate"]
    assert bird.args[2] == articuno["sprite"]
    assert bird.args[3] == articuno["movement"]
    assert bird.args[8] == articuno["palette"]
    assert bird.args[9] == articuno["object_type"]
    assert bird.args[11] == "SeafoamIslandsCaveArticuno"
    assert bird.args[12] == articuno["mask_event"]
    pickup = seafoam["visible_pickup"]
    item_ball = next(event for event in objects if event.args[11] == pickup["script"])
    assert [item_ball.x, item_ball.y] == pickup["coordinate"]
    assert item_ball.args[2] == "SPRITE_POKE_BALL"
    assert item_ball.args[3] == "SPRITEMOVEDATA_STILL"
    assert item_ball.args[9] == "OBJECTTYPE_ITEMBALL"
    assert item_ball.args[12] == pickup["event"]

    hidden = seafoam["hidden_pickup"]
    backgrounds = [
        event for event in cave_events if event.event_type == "bg_event"
    ]
    assert len(backgrounds) == 1
    assert [backgrounds[0].x, backgrounds[0].y] == hidden["coordinate"]
    assert backgrounds[0].args[2:] == ("BGEVENT_ITEM", hidden["script"])
    cave_source = _active_code(
        repo_root / "maps/SeafoamIslandsCave.asm", CRYSTAL_LEGENDS
    )
    assert (
        "callback MAPCALLBACK_TILES, SeafoamIslandsCaveArticunoCallback"
        in cave_source
    )
    assert not any("MAPCALLBACK_OBJECTS" in line for line in cave_source)
    assert cave_source[cave_source.index(f'{pickup["script"]}:') + 1] == (
        f'itemball {pickup["item"]}'
    )
    assert cave_source[cave_source.index(f'{hidden["script"]}:') + 1] == (
        f'hiddenitem {hidden["item"]}, {hidden["event"]}'
    )

    shared = _active_code(
        repo_root / "maps/Phase9LegendaryBirds.asm", CRYSTAL_LEGENDS
    )
    refresh = _section(shared, f'{articuno["callback"]}:', f'{articuno["script"]}:')
    _assert_in_order(
        refresh,
        [
            f'checkevent {articuno["capture_event"]}',
            f'checkevent {articuno["player_choice_event"]}',
            f'checkevent {articuno["silver_choice_event"]}',
            f'checkevent {articuno["oak_choice_event"]}',
            f'checkevent {articuno["oak_handoff_event"]}',
            f'checkevent {articuno["silver_availability_event"]}',
            f'clearevent {articuno["mask_event"]}',
            f'setevent {articuno["mask_event"]}',
        ],
    )
    encounter = _section(shared, f'{articuno["script"]}:', "Phase9LegendaryBirdsEnd:")
    _assert_in_order(
        encounter,
        [
            f'cry {articuno["species"]}',
            "farwritetext Phase9ArticunoEncounterText",
            "loadvar VAR_BATTLETYPE, BATTLETYPE_KANTO_BIRD",
            f'loadwildmon {articuno["species"]}, {articuno["level"]}',
            "startbattle",
            "special CheckCaughtPokemon",
            f'setevent {articuno["capture_event"]}',
            f'setevent {articuno["mask_event"]}',
            "disappear SEAFOAMISLANDSCAVE_ARTICUNO",
            "reloadmapafterbattle",
        ],
    )


def test_seafoam_route_and_forced_ice_slide_reach_the_articuno_approach(
    repo_root: Path, scenario: dict
) -> None:
    seafoam = scenario["seafoam"]
    dimensions = {
        seafoam["map"]: MapDimensions(seafoam["map"], *seafoam["dimensions"]),
        "ROUTE_20": MapDimensions("ROUTE_20", 30, 9),
    }
    resolved = {
        seafoam["map"]: seafoam["active_block_path"],
        "ROUTE_20": seafoam["route20_active_block_path"],
    }
    tilesets = parse_map_tilesets((repo_root / "data/maps/maps.asm").read_text())
    assert collision_at(
        repo_root,
        "ROUTE_20",
        tuple(seafoam["route20_warp"][:2]),
        dimensions,
        resolved,
        tilesets,
    ) == "CAVE"
    assert collision_at(
        repo_root,
        "ROUTE_20",
        tuple(seafoam["route20_approach"]),
        dimensions,
        resolved,
        tilesets,
    ) == "FLOOR"

    active_blocks = (repo_root / seafoam["active_block_path"]).read_bytes()
    entry_x, entry_y = seafoam["return_warp"][:2]
    entry_offset = (entry_y // 2) * seafoam["dimensions"][0] + entry_x // 2
    assert active_blocks[entry_offset] == seafoam["custom_metatiles"][
        "visible_exit"
    ]["block"]

    for coordinate in (
        seafoam["pond_ice_coordinates"]
        + seafoam["western_l_ice_coordinates"]
        + seafoam["eastern_ice_coordinates"]
    ):
        assert collision_at(
            repo_root,
            seafoam["map"],
            tuple(coordinate),
            dimensions,
            resolved,
            tilesets,
        ) == "ICE"
    for coordinate in seafoam["ice_rock_coordinates"]:
        assert collision_at(
            repo_root,
            seafoam["map"],
            tuple(coordinate),
            dimensions,
            resolved,
            tilesets,
        ) == "WALL"
    assert collision_at(
        repo_root,
        seafoam["map"],
        tuple(seafoam["visible_pickup"]["coordinate"]),
        dimensions,
        resolved,
        tilesets,
    ) == "FLOOR"
    for coordinate in ((2, 8), (3, 8)):
        assert collision_at(
            repo_root,
            seafoam["map"],
            coordinate,
            dimensions,
            resolved,
            tilesets,
        ) == "FLOOR"
    for coordinate in seafoam["eastern_return_channel"]:
        assert collision_at(
            repo_root,
            seafoam["map"],
            tuple(coordinate),
            dimensions,
            resolved,
            tilesets,
        ) == "FLOOR"

    passable = {"FLOOR", "ICE", "WARP_CARPET_DOWN"}
    start = tuple(seafoam["return_warp"][:2])
    seen = {start}
    pending = [start]
    while pending:
        x, y = pending.pop()
        for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if neighbor in seen:
                continue
            nx, ny = neighbor
            if not (0 <= nx < 20 and 0 <= ny < 18):
                continue
            if collision_at(
                repo_root,
                seafoam["map"],
                neighbor,
                dimensions,
                resolved,
                tilesets,
            ) not in passable:
                continue
            seen.add(neighbor)
            pending.append(neighbor)

    articuno = seafoam["articuno"]
    assert tuple(articuno["coordinate"]) in seen
    assert tuple(articuno["approach"]) in seen
    assert collision_at(
        repo_root,
        seafoam["map"],
        tuple(articuno["approach"]),
        dimensions,
        resolved,
        tilesets,
    ) == "FLOOR"
    assert collision_at(
        repo_root,
        seafoam["map"],
        start,
        dimensions,
        resolved,
        tilesets,
    ) == "WARP_CARPET_DOWN"

    for slide in seafoam["slides"]:
        x, y = slide["start"]
        dx, dy = slide["direction"]
        x += dx
        y += dy
        assert collision_at(
            repo_root,
            seafoam["map"],
            (x, y),
            dimensions,
            resolved,
            tilesets,
        ) == "ICE"
        player_x, player_y = x, y
        while collision_at(
            repo_root,
            seafoam["map"],
            (x, y),
            dimensions,
            resolved,
            tilesets,
        ) == "ICE":
            player_x, player_y = x, y
            x += dx
            y += dy
        terminal_collision = collision_at(
            repo_root,
            seafoam["map"],
            (x, y),
            dimensions,
            resolved,
            tilesets,
        )
        if terminal_collision == "FLOOR":
            player_x, player_y = x, y
        assert [player_x, player_y] == slide["stop"]
        assert collision_at(
            repo_root,
            seafoam["map"],
            (player_x, player_y),
            dimensions,
            resolved,
            tilesets,
        ) == slide["stop_collision"]
        if "terminal" in slide:
            assert [x, y] == slide["terminal"]
            assert terminal_collision == slide["terminal_collision"]


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


def test_cinnabar_staircase_uses_a_renderable_nonzero_block(
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
            "and a",
            "jr z, .nope",
            "ld l, a",
        ],
    )
    assert custom == reference
    assert "CheckCurrentMapBlockZero" not in (repo_root / "home.asm").read_text()


def test_facility_variant_reuses_only_the_locked_gate_tiles_and_appends_doors(
    repo_root: Path, scenario: dict
) -> None:
    facility = scenario["facility_variant"]
    stock_tiles = _png_tiles(repo_root / facility["stock_gfx_path"])
    active_tiles = _png_tiles(repo_root / facility["active_gfx_path"])
    gate_tiles = _png_tiles(
        repo_root / facility["source_gfx_path"], expected_height=96
    )
    assert [
        index
        for index, (stock, active) in enumerate(zip(stock_tiles, active_tiles))
        if stock != active
    ] == facility["destination_tiles"]
    for source, destination in zip(
        facility["source_tiles"], facility["destination_tiles"]
    ):
        assert active_tiles[destination] == gate_tiles[source]

    stock_metatiles = (repo_root / facility["stock_metatiles_path"]).read_bytes()
    active_metatiles = (repo_root / facility["active_metatiles_path"]).read_bytes()
    assert len(stock_metatiles) == 0x40 * 16
    assert len(active_metatiles) == 0x45 * 16
    assert active_metatiles[: len(stock_metatiles)] == stock_metatiles
    assert all(tile not in stock_metatiles for tile in facility["destination_tiles"])
    for block, expected in facility["metatiles"].items():
        index = int(block)
        assert active_metatiles[index * 16 : (index + 1) * 16] == bytes(expected)

    collision_source = (repo_root / "data/tilesets/facility_collision.asm").read_text()
    custom_rows = parse_collision_rows(collision_source, CRYSTAL_LEGENDS)
    reference_rows = parse_collision_rows(collision_source, REFERENCE)
    assert custom_rows[:0x40] == reference_rows
    assert len(reference_rows) == 0x40
    assert len(custom_rows) == 0x45
    for block, expected in facility["collisions"].items():
        assert custom_rows[int(block)] == tuple(expected)

    tileset_source = _active_code(repo_root / "gfx/tilesets.asm", CRYSTAL_LEGENDS)
    reference_source = _active_code(repo_root / "gfx/tilesets.asm", REFERENCE)
    assert (
        f'INCBIN "{facility["active_gfx_path"].replace(".png", ".2bpp.lz")}"'
        in tileset_source
    )
    assert f'INCBIN "{facility["active_metatiles_path"]}"' in tileset_source
    assert (
        f'INCBIN "{facility["stock_gfx_path"].replace(".png", ".2bpp.lz")}"'
        in reference_source
    )
    assert f'INCBIN "{facility["stock_metatiles_path"]}"' in reference_source
    assert (repo_root / facility["palette_map_path"]).is_file()


def test_power_plant_annex_layout_shutter_warps_and_route_match_the_contract(
    repo_root: Path, scenario: dict
) -> None:
    annex = scenario["power_plant_annex"]
    block_source = (repo_root / "data/maps/blocks.asm").read_text()
    custom_paths = parse_block_paths(block_source, CRYSTAL_LEGENDS)
    reference_paths = parse_block_paths(block_source, REFERENCE)
    assert custom_paths["PowerPlant"] == annex["power_plant_active_block_path"]
    assert reference_paths["PowerPlant"] == annex["power_plant_stock_block_path"]
    assert custom_paths["PowerPlantGeneratorAnnex"] == annex["block_path"]
    assert "PowerPlantGeneratorAnnex" not in reference_paths

    stock = (repo_root / annex["power_plant_stock_block_path"]).read_bytes()
    active = (repo_root / annex["power_plant_active_block_path"]).read_bytes()
    assert len(stock) == len(active) == 90
    assert [
        {"offset": offset, "old_block": old, "new_block": new}
        for offset, (old, new) in enumerate(zip(stock, active))
        if old != new
    ] == [annex["power_plant_block_delta"]]
    assert (repo_root / annex["block_path"]).read_bytes() == bytes(annex["blocks"])

    dimensions = parse_map_dimensions(
        (repo_root / "constants/map_constants.asm").read_text()
    )
    assert [
        dimensions[annex["map"]].width_blocks,
        dimensions[annex["map"]].height_blocks,
    ] == annex["dimensions"]
    declaration = "map PowerPlantGeneratorAnnex, " + ", ".join(annex["metadata"])
    assert declaration in _active_code(repo_root / "data/maps/maps.asm", CRYSTAL_LEGENDS)
    assert declaration not in _active_code(repo_root / "data/maps/maps.asm", REFERENCE)
    assert (
        f'map_attributes PowerPlantGeneratorAnnex, {annex["map"]}, '
        f'${annex["border_block"]:02x}'
        in (repo_root / "data/maps/attributes.asm").read_text()
    )

    sources = {source.map_name: source for source in map_sources_from_repository(repo_root)}
    plant_events = parse_events(sources["POWER_PLANT"])
    reference_plant_events = parse_events(sources["POWER_PLANT"], REFERENCE)
    annex_events = parse_events(sources[annex["map"]])
    assert [
        list(event.args)
        for event in plant_events
        if event.event_type == "warp_event"
    ][-2:] == [[str(value) for value in warp] for warp in annex["power_plant_warps"]]
    assert len(
        [event for event in reference_plant_events if event.event_type == "warp_event"]
    ) == 2
    assert [
        list(event.args)
        for event in annex_events
        if event.event_type == "warp_event"
    ] == [[str(value) for value in warp] for warp in annex["return_warps"]]
    assert [
        [event.x, event.y]
        for event in plant_events
        if event.event_type == "bg_event"
        and event.identity == "PowerPlantAnnexShutter"
    ] == annex["shutter"]["interaction_event_coordinates"]
    assert len([event for event in plant_events if event.event_type == "object_event"]) == 7
    assert [
        [event.x, event.y]
        for event in annex_events
        if event.event_type == "bg_event"
    ] == annex["console_coordinates"]

    annex_source = (repo_root / "maps/PowerPlantGeneratorAnnex.asm").read_text()
    console_script = _section(
        annex_source,
        "PowerPlantGeneratorAnnexConsole:",
        "PowerPlantGeneratorAnnex_MapEvents:",
    )
    _assert_in_order(
        console_script,
        [
            "checkevent EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION",
            "iftrue .Stable",
            "farjumptext Phase9PowerPlantGeneratorAnnexConsoleText",
            ".Stable:",
            "farjumptext Phase9PowerPlantGeneratorAnnexStableText",
        ],
    )

    resolved = {
        "POWER_PLANT": annex["power_plant_active_block_path"],
        annex["map"]: annex["block_path"],
    }
    relevant_dimensions = {
        "POWER_PLANT": dimensions["POWER_PLANT"],
        annex["map"]: dimensions[annex["map"]],
    }
    tilesets = parse_map_tilesets((repo_root / "data/maps/maps.asm").read_text())
    for coordinate in annex["shutter"]["door_coordinates"]:
        assert collision_at(
            repo_root,
            "POWER_PLANT",
            tuple(coordinate),
            relevant_dimensions,
            resolved,
            tilesets,
        ) == "FLOOR"
    for coordinate in [warp[:2] for warp in annex["return_warps"]]:
        assert collision_at(
            repo_root,
            annex["map"],
            tuple(coordinate),
            relevant_dimensions,
            resolved,
            tilesets,
        ) == "WARP_CARPET_LEFT"
    for coordinate in annex["route"]:
        assert collision_at(
            repo_root,
            annex["map"],
            tuple(coordinate),
            relevant_dimensions,
            resolved,
            tilesets,
        ) == "FLOOR"

    plant_source = _active_code(repo_root / "maps/PowerPlant.asm", CRYSTAL_LEGENDS)
    _assert_in_order(
        plant_source,
        [
            f'checkevent {annex["shutter"]["power_event"]}',
            f'checkevent {annex["shutter"]["authorization_event"]}',
            f'checkevent {annex["shutter"]["open_event"]}',
            "playsound SFX_ENTER_DOOR",
            f'changeblock {annex["shutter"]["block_origin"][0]}, {annex["shutter"]["block_origin"][1]}, ${annex["shutter"]["open_block"]:02x}',
            "refreshmap",
            f'setevent {annex["shutter"]["open_event"]}',
            "warpcheck",
            "newloadmap MAPSETUP_DOOR",
        ],
    )


def test_zapdos_moltres_and_oak_tracker_use_the_locked_branch_contract(
    repo_root: Path, scenario: dict
) -> None:
    annex = scenario["power_plant_annex"]
    zapdos = annex["zapdos"]
    victory = scenario["victory_road_bird"]
    moltres = victory["moltres"]
    sources = {source.map_name: source for source in map_sources_from_repository(repo_root)}

    annex_objects = [
        event
        for event in parse_events(sources[annex["map"]])
        if event.event_type == "object_event"
    ]
    assert len(annex_objects) == 2
    zapdos_event = next(
        event
        for event in annex_objects
        if event.args[11] == "PowerPlantGeneratorAnnexZapdos"
    )
    pickup = annex["visible_pickup"]
    pickup_event = next(
        event for event in annex_objects if event.args[11] == pickup["script"]
    )
    assert [pickup_event.x, pickup_event.y] == pickup["coordinate"]
    assert pickup_event.args[2] == "SPRITE_POKE_BALL"
    assert pickup_event.args[3] == "SPRITEMOVEDATA_STILL"
    assert pickup_event.args[9] == "OBJECTTYPE_ITEMBALL"
    assert pickup_event.args[12] == pickup["event"]
    annex_source = _active_code(
        repo_root / "maps/PowerPlantGeneratorAnnex.asm", CRYSTAL_LEGENDS
    )
    assert annex_source[annex_source.index(f'{pickup["script"]}:') + 1] == (
        f'itemball {pickup["item"]}'
    )
    victory_objects = [
        event
        for event in parse_events(sources[victory["map"]])
        if event.event_type == "object_event"
    ]
    reference_victory_objects = [
        event
        for event in parse_events(sources[victory["map"]], REFERENCE)
        if event.event_type == "object_event"
    ]
    assert len(victory_objects) == 7
    assert len(reference_victory_objects) == 6
    victory_warps = [
        [event.x, event.y]
        for event in parse_events(sources[victory["map"]])
        if event.event_type == "warp_event"
    ]
    assert len(victory_warps) == 10
    assert all(coordinate in victory_warps for coordinate in victory["route_warps"])

    dimensions = {victory["map"]: MapDimensions(victory["map"], 10, 36)}
    resolved = {victory["map"]: "maps/VictoryRoad.blk"}
    tilesets = parse_map_tilesets((repo_root / "data/maps/maps.asm").read_text())
    assert collision_at(
        repo_root,
        victory["map"],
        tuple(moltres["coordinate"]),
        dimensions,
        resolved,
        tilesets,
    ) == "FLOOR"
    annex_dimensions = {annex["map"]: MapDimensions(annex["map"], 4, 4)}
    assert collision_at(
        repo_root,
        annex["map"],
        tuple(pickup["coordinate"]),
        annex_dimensions,
        {annex["map"]: annex["block_path"]},
        tilesets,
    ) == "FLOOR"
    assert collision_at(
        repo_root,
        victory["map"],
        tuple(moltres["approach"]),
        dimensions,
        resolved,
        tilesets,
    ) == "FLOOR"
    assert collision_at(
        repo_root,
        victory["map"],
        tuple(victory["full_restore"]),
        dimensions,
        resolved,
        tilesets,
    ) == "FLOOR"
    for coordinate in victory["route_warps"]:
        assert collision_at(
            repo_root,
            victory["map"],
            tuple(coordinate),
            dimensions,
            resolved,
            tilesets,
        ) == "LADDER"
    for coordinate in victory["east_hops"]:
        assert collision_at(
            repo_root,
            victory["map"],
            tuple(coordinate),
            dimensions,
            resolved,
            tilesets,
        ) == "HOP_RIGHT"
    for coordinate in victory["south_hops"]:
        assert collision_at(
            repo_root,
            victory["map"],
            tuple(coordinate),
            dimensions,
            resolved,
            tilesets,
        ) == "HOP_DOWN"

    for bird, event, script_stub in (
        (zapdos, zapdos_event, "PowerPlantGeneratorAnnexZapdos"),
        (moltres, victory_objects[-1], "VictoryRoadMoltres"),
    ):
        assert [event.x, event.y] == bird["coordinate"]
        assert event.args[2] == bird["sprite"]
        assert event.args[3] == bird["movement"]
        assert event.args[8] == bird["palette"]
        assert event.args[9] == bird["object_type"]
        assert event.args[11] == script_stub
        assert event.args[12] == bird["mask_event"]

    shared = _active_code(repo_root / "maps/Phase9LegendaryBirds.asm", CRYSTAL_LEGENDS)
    for bird, refresh_end, encounter_end, disappearance in (
        (
            zapdos,
            f'{moltres["callback"]}:',
            f'{moltres["script"]}:',
            "POWERPLANTGENERATORANNEX_ZAPDOS",
        ),
        (
            moltres,
            "Phase9ArticunoEncounter:",
            "Phase9OaksAssistant2Hints:",
            "VICTORYROAD_MOLTRES",
        ),
    ):
        refresh = _section(shared, f'{bird["callback"]}:', refresh_end)
        _assert_in_order(
            refresh,
            [
                f'checkevent {bird["capture_event"]}',
                f'checkevent {bird["location_gate_event"]}',
                f'checkevent {bird["player_choice_event"]}',
                f'checkevent {bird["silver_choice_event"]}',
                f'checkevent {bird["oak_choice_event"]}',
                f'checkevent {bird["oak_handoff_event"]}',
                f'checkevent {bird["silver_availability_event"]}',
                f'clearevent {bird["mask_event"]}',
                f'setevent {bird["mask_event"]}',
            ],
        )
        encounter = _section(shared, f'{bird["script"]}:', encounter_end)
        _assert_in_order(
            encounter,
            [
                f'cry {bird["species"]}',
                "loadvar VAR_BATTLETYPE, BATTLETYPE_KANTO_BIRD",
                f'loadwildmon {bird["species"]}, {bird["level"]}',
                "startbattle",
                "special CheckCaughtPokemon",
                f'setevent {bird["capture_event"]}',
                f'setevent {bird["mask_event"]}',
                f'disappear {disappearance}',
                "reloadmapafterbattle",
            ],
        )

    flee_logic = _active_code(
        repo_root / "engine/battle/core.asm", CRYSTAL_LEGENDS
    )
    _assert_in_order(
        _section(flee_logic, "TryEnemyFlee:", 'INCLUDE "data/wild/flee_mons.asm"'),
        [
            "call CheckKantoBirdEnemyFlee",
            "jr c, .Stay",
            "nop",
            "ld hl, OftenFleeMons",
        ],
    )
    flee_guard = _active_code(
        repo_root / "engine/battle/kanto_bird_flee.asm", CRYSTAL_LEGENDS
    )
    _assert_in_order(
        flee_guard,
        [
            "CheckKantoBirdEnemyFlee:",
            "ld a, [wBattleMode]",
            "ld a, [wBattleType]",
            "cp BATTLETYPE_KANTO_BIRD",
            "scf",
        ],
    )
    assert 'INCLUDE "engine/battle/kanto_bird_flee.asm"' not in _active_code(
        repo_root / "main.asm", REFERENCE
    )

    oak = _active_code(repo_root / "maps/OaksLab.asm", CRYSTAL_LEGENDS)
    reference_oak = _active_code(repo_root / "maps/OaksLab.asm", REFERENCE)
    assistant = oak.index("OaksAssistant2Script:")
    assert oak[assistant + 1 : assistant + 4] == [
        "checkevent EVENT_OAK_MOVED_THIRD_BIRD",
        "iftrue .LegendaryBirdHints",
        "jumptextfaceplayer OaksAssistant2Text",
    ]
    reference_assistant = reference_oak.index("OaksAssistant2Script:")
    assert (
        reference_oak[reference_assistant + 1]
        == "jumptextfaceplayer OaksAssistant2Text"
    )
    assert "farsjump Phase9OaksAssistant2Hints" in oak
    tracker = _section(
        shared, "Phase9OaksAssistant2Hints:", "Phase9LegendaryBirdsEnd:"
    )
    assert all(
        f"checkevent {event}" in tracker
        for event in (
            "EVENT_CAUGHT_ARTICUNO_IN_KANTO",
            "EVENT_CAUGHT_ZAPDOS_IN_KANTO",
            "EVENT_CAUGHT_MOLTRES_IN_KANTO",
        )
    )
    assert all(
        event not in tracker
        for event in (
            "EVENT_RESTORED_POWER_TO_KANTO",
            "EVENT_POWER_PLANT_ANNEX_AUTHORIZED",
            "EVENT_OPENED_POWER_PLANT_ANNEX",
            "EVENT_BEAT_ELITE_FOUR",
        )
    )
    assert not any("NOT_AT_KANTO_LOCATION" in line for line in tracker)
    assert tracker.count(
        "writetext Phase9OaksAssistantLegendaryHabitatHintText"
    ) == 1
    assert all(
        retired not in tracker
        for retired in (
            "Phase9OaksAssistantArticunoHint:",
            "Phase9OaksAssistantZapdosHint:",
            "Phase9OaksAssistantMoltresHint:",
        )
    )
    assert "Phase9OaksAssistantLegendaryHabitatHintText:" in tracker
    assert 'text "AIDE: Legendary"' in tracker
    assert 'line "birds are drawn to"' in tracker
    assert 'cont "their natural"' in tracker
    assert 'cont "habitat."' in tracker
    for retired in (
        "Phase9OaksAssistantArticunoHintText",
        "Phase9OaksAssistantZapdosRepairHintText",
        "Phase9OaksAssistantZapdosAuthorizationHintText",
        "Phase9OaksAssistantZapdosShutterHintText",
        "Phase9OaksAssistantZapdosOpenHintText",
        "Phase9OaksAssistantMoltresLeagueHintText",
        "Phase9OaksAssistantMoltresOpenHintText",
    ):
        assert retired not in tracker
