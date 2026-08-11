from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.asm_conditions import active_lines
from tests.support.map_assets import (
    block_paths_for_maps,
    collision_at,
    parse_block_paths,
    parse_map_tilesets,
)
from tests.support.map_model import parse_map_dimensions


pytestmark = [pytest.mark.static, pytest.mark.phase5]


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


def test_phase_5_event_slots_are_reserved_without_changing_num_events(
    repo_root: Path,
) -> None:
    source = repo_root / "constants/event_flags.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    names = [
        "EVENT_GOT_KABUTO_FROM_ALPH",
        "EVENT_GOT_OMANYTE_FROM_ALPH",
        "EVENT_GOT_AERODACTYL_FROM_ALPH",
    ]

    _assert_contiguous(
        crystal,
        [
            "const EVENT_GOT_TOTODILE_FROM_CIANWOOD",
            *(f"const {name}" for name in names),
            "const_next 2048",
            "DEF NUM_EVENTS EQU const_value",
        ],
    )
    assert all(not any(name in line for line in reference) for name in names)
    _assert_contiguous(
        reference,
        [
            "const_skip",
            "const_skip 3",
            "const_skip 3",
            "const_next 2048",
            "DEF NUM_EVENTS EQU const_value",
        ],
    )


def test_phase_5_sprite_ids_append_to_the_custom_icon_table(repo_root: Path) -> None:
    constants = repo_root / "constants/sprite_constants.asm"
    table = repo_root / "data/sprites/sprite_mons.asm"
    crystal_constants = _active_code(constants, CRYSTAL_LEGENDS)
    reference_constants = _active_code(constants, REFERENCE)
    crystal_table = _active_code(table, CRYSTAL_LEGENDS)
    reference_table = _active_code(table, REFERENCE)

    _assert_contiguous(
        crystal_constants,
        [
            "const SPRITE_TOTODILE",
            "const SPRITE_KABUTO",
            "const SPRITE_OMANYTE",
            "const SPRITE_AERODACTYL",
            "DEF NUM_POKEMON_SPRITES EQU const_value - SPRITE_POKEMON",
        ],
    )
    _assert_contiguous(
        crystal_table,
        [
            "db TOTODILE",
            "db KABUTO",
            "db OMANYTE",
            "db AERODACTYL",
            "assert_table_length NUM_POKEMON_SPRITES",
        ],
    )
    for name in ("KABUTO", "OMANYTE", "AERODACTYL"):
        assert not any(f"SPRITE_{name}" in line for line in reference_constants)
        assert f"db {name}" not in reference_table


@pytest.mark.parametrize(
    ("species", "prefix", "special"),
    [
        ("KABUTO", "RuinsOfAlphKabutoChamber", None),
        ("OMANYTE", "RuinsOfAlphOmanyteChamber", "special OmanyteChamber"),
        ("AERODACTYL", "RuinsOfAlphAerodactylChamber", None),
    ],
)
def test_phase_5_chamber_source_uses_the_dual_gate_everywhere(
    repo_root: Path, species: str, prefix: str, special: str | None
) -> None:
    source = repo_root / "maps" / f"{prefix}.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    picture = f"EVENT_SOLVED_{species}_PUZZLE"
    wall = f"EVENT_WALL_OPENED_IN_{species}_CHAMBER"

    scene = [f"{prefix}CheckWallScene:"]
    if special:
        scene.append(special)
    _assert_contiguous(
        crystal,
        [
            *scene,
            f"checkevent {picture}",
            "iffalse .WallClosed",
            f"checkevent {wall}",
            "iftrue .OpenWall",
            ".WallClosed:",
            "end",
            ".OpenWall:",
            f"sdefer {prefix}WallOpenScript",
            "end",
        ],
    )
    _assert_contiguous(
        crystal,
        [
            f"{prefix}HiddenDoorsCallback:",
            f"checkevent {picture}",
            "iffalse .WallClosed",
            f"checkevent {wall}",
            "iftrue .WallOpen",
            ".WallClosed:",
            "changeblock 4, 0, $2e",
            ".WallOpen:",
            f"checkevent {picture}",
            "iffalse .FloorClosed",
            "endcallback",
        ],
    )
    _assert_contiguous(
        crystal,
        [
            f"{prefix}WallPatternRight:",
            f"checkevent {picture}",
            "iffalse .WallClosed",
            f"checkevent {wall}",
            "iftrue .WallOpen",
            ".WallClosed:",
            "opentext",
        ],
    )

    reference_scene = [f"{prefix}CheckWallScene:"]
    if special:
        reference_scene.append(special)
    _assert_contiguous(
        reference,
        [
            *reference_scene,
            f"checkevent {wall}",
            "iftrue .OpenWall",
            "end",
        ],
    )
    reference_scene_start = reference.index(f"{prefix}CheckWallScene:")
    reference_scene_end = reference.index(f"{prefix}NoopScene:")
    assert f"checkevent {picture}" not in reference[
        reference_scene_start:reference_scene_end
    ]


def test_kabuto_scientist_requires_the_picture_before_hole_dialogue(
    repo_root: Path,
) -> None:
    source = repo_root / "maps/RuinsOfAlphKabutoChamber.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    _assert_contiguous(
        crystal,
        [
            "ifequal NUM_UNOWN, .AllUnownCaught",
            "checkevent EVENT_SOLVED_KABUTO_PUZZLE",
            "iffalse .PuzzleIncomplete",
            "checkevent EVENT_WALL_OPENED_IN_KABUTO_CHAMBER",
            "iftrue .WallOpen",
        ],
    )
    _assert_contiguous(
        reference,
        [
            "ifequal NUM_UNOWN, .AllUnownCaught",
            "checkevent EVENT_WALL_OPENED_IN_KABUTO_CHAMBER",
            "iftrue .WallOpen",
            "checkevent EVENT_SOLVED_KABUTO_PUZZLE",
        ],
    )


def test_phase_5_preserves_the_stock_hidden_wall_engine(repo_root: Path) -> None:
    source = (repo_root / "engine/events/unown_walls.asm").read_text()
    assert "_CRYSTALLEGENDS" not in source
    for event in (
        "EVENT_WALL_OPENED_IN_KABUTO_CHAMBER",
        "EVENT_WALL_OPENED_IN_OMANYTE_CHAMBER",
        "EVENT_WALL_OPENED_IN_AERODACTYL_CHAMBER",
    ):
        assert event in source
    assert "CheckItem" in source
    assert "MON_ITEM" in source
    assert "WATER_STONE" in source
    assert "takeitem" not in source.lower()


@pytest.mark.parametrize(
    ("species", "prefix", "object_constant", "palette", "level", "first_item"),
    [
        (
            "KABUTO",
            "RuinsOfAlphKabutoItemRoom",
            "RUINSOFALPHKABUTOITEMROOM_KABUTO",
            "PAL_NPC_BROWN",
            10,
            "Berry",
        ),
        (
            "OMANYTE",
            "RuinsOfAlphOmanyteItemRoom",
            "RUINSOFALPHOMANYTEITEMROOM_OMANYTE",
            "PAL_NPC_BLUE",
            26,
            "Mysteryberry",
        ),
        (
            "AERODACTYL",
            "RuinsOfAlphAerodactylItemRoom",
            "RUINSOFALPHAERODACTYLITEMROOM_AERODACTYL",
            "PAL_NPC_PINK",
            23,
            "GoldBerry",
        ),
    ],
)
def test_hidden_room_gift_is_retry_safe_and_preserves_stock_objects(
    repo_root: Path,
    species: str,
    prefix: str,
    object_constant: str,
    palette: str,
    level: int,
    first_item: str,
) -> None:
    source = repo_root / "maps" / f"{prefix}.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    object_row = (
        f"object_event  3,  3, SPRITE_{species}, SPRITEMOVEDATA_POKEMON, 0, 0, "
        f"-1, -1, {palette}, OBJECTTYPE_SCRIPT, 0, "
        f"{prefix}{species.title()}Script, -1"
    )

    assert f"const {object_constant}" in crystal
    assert f"const {object_constant}" not in reference
    assert object_row in crystal
    assert object_row not in reference
    _assert_contiguous(
        crystal,
        [
            f"{prefix}{species.title()}Callback:",
            f"checkevent EVENT_GOT_{species}_FROM_ALPH",
            "iftrue .Hide",
            f"checkevent EVENT_SOLVED_{species}_PUZZLE",
            "iffalse .Hide",
            f"checkevent EVENT_WALL_OPENED_IN_{species}_CHAMBER",
            "iffalse .Hide",
            f"appear {object_constant}",
            "endcallback",
            ".Hide:",
            f"disappear {object_constant}",
            "endcallback",
        ],
    )
    _assert_contiguous(
        crystal,
        [
            f"{prefix}{species.title()}Script:",
            "faceplayer",
            "opentext",
            f"cry {species}",
            f"writetext {prefix}{species.title()}OfferText",
            "yesorno",
            "iffalse .Declined",
            f"givepoke {species}, {level}",
            "ifequal 2, .StorageFull",
            f"setevent EVENT_GOT_{species}_FROM_ALPH",
            f"writetext {prefix}{species.title()}JoinedText",
            "playsound SFX_CAUGHT_MON",
            "waitsfx",
            "waitbutton",
            "closetext",
            f"disappear {object_constant}",
            "end",
        ],
    )
    script_start = crystal.index(f"{prefix}{species.title()}Script:")
    script_end = crystal.index(f"{prefix}{first_item}:")
    script = "\n".join(crystal[script_start:script_end])
    for forbidden in ("loadwildmon", "startbattle", "giveitem", "takeitem"):
        assert forbidden not in script

    custom_stock = [
        line
        for line in crystal
        if line.startswith("object_event") and "SPRITE_POKE_BALL" in line
    ]
    reference_stock = [
        line
        for line in reference
        if line.startswith("object_event") and "SPRITE_POKE_BALL" in line
    ]
    assert len(custom_stock) == len(reference_stock) == 4
    assert custom_stock == reference_stock


@pytest.mark.parametrize(
    "map_name",
    [
        "RUINS_OF_ALPH_KABUTO_ITEM_ROOM",
        "RUINS_OF_ALPH_OMANYTE_ITEM_ROOM",
        "RUINS_OF_ALPH_AERODACTYL_ITEM_ROOM",
    ],
)
def test_gift_coordinate_is_floor(repo_root: Path, map_name: str) -> None:
    dimensions = parse_map_dimensions(
        (repo_root / "constants/map_constants.asm").read_text()
    )
    block_paths = block_paths_for_maps(
        dimensions,
        parse_block_paths((repo_root / "data/maps/blocks.asm").read_text()),
    )
    tilesets = parse_map_tilesets((repo_root / "data/maps/maps.asm").read_text())
    assert collision_at(
        repo_root,
        map_name,
        (3, 3),
        dimensions,
        block_paths,
        tilesets,
    ) == "FLOOR"


def test_kim_trade_replaces_only_the_received_species_and_nickname(
    repo_root: Path,
) -> None:
    trade_source = repo_root / "data/events/npc_trades.asm"
    custom = _active_code(trade_source, CRYSTAL_LEGENDS)
    reference = _active_code(trade_source, REFERENCE)
    custom_rows = [line for line in custom if line.startswith("npctrade ")]
    reference_rows = [line for line in reference if line.startswith("npctrade ")]

    assert len(custom_rows) == len(reference_rows) == 7
    assert custom_rows[:5] == reference_rows[:5]
    assert custom_rows[6:] == reference_rows[6:]
    assert custom_rows[5] == (
        'npctrade TRADE_DIALOGSET_GIRL,      CHANSEY,    GIRAFARIG,  "GIRAFY", '
        '$96, $66, GOLD_BERRY,   26491, "KIM",    TRADE_GENDER_EITHER'
    )
    assert reference_rows[5] == (
        'npctrade TRADE_DIALOGSET_GIRL,      CHANSEY,    AERODACTYL, "AEROY",  '
        '$96, $66, GOLD_BERRY,   26491, "KIM",    TRADE_GENDER_EITHER'
    )

    route_source = repo_root / "maps/Route14.asm"
    expected = [
        "Kim:",
        "faceplayer",
        "opentext",
        "trade NPC_TRADE_KIM",
        "waitbutton",
        "closetext",
        "end",
    ]
    _assert_contiguous(_active_code(route_source, CRYSTAL_LEGENDS), expected)
    _assert_contiguous(_active_code(route_source, REFERENCE), expected)
