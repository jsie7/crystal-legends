from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage, decode_object_events
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase5]


@pytest.fixture(scope="module")
def phase_5_constants(repo_root: Path, tmp_path_factory) -> dict[str, int]:
    return resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_5_rom_constants"),
        [
            "EVENT_GOT_KABUTO_FROM_ALPH",
            "EVENT_GOT_OMANYTE_FROM_ALPH",
            "EVENT_GOT_AERODACTYL_FROM_ALPH",
            "NUM_EVENTS",
            "SPRITE_KABUTO",
            "SPRITE_OMANYTE",
            "SPRITE_AERODACTYL",
            "NUM_POKEMON_SPRITES",
            "KABUTO",
            "OMANYTE",
            "AERODACTYL",
            "EVENT_SOLVED_KABUTO_PUZZLE",
            "EVENT_SOLVED_OMANYTE_PUZZLE",
            "EVENT_SOLVED_AERODACTYL_PUZZLE",
            "EVENT_WALL_OPENED_IN_KABUTO_CHAMBER",
            "EVENT_WALL_OPENED_IN_OMANYTE_CHAMBER",
            "EVENT_WALL_OPENED_IN_AERODACTYL_CHAMBER",
            "checkevent_command",
            "sdefer_command",
            "WARP_EVENT_SIZE",
            "COORD_EVENT_SIZE",
            "BG_EVENT_SIZE",
            "OBJECT_EVENT_SIZE",
            "SPRITEMOVEDATA_POKEMON",
            "PAL_NPC_BROWN",
            "OBJECTTYPE_SCRIPT",
            "NO_ITEM",
            "FALSE",
            "givepoke_command",
            "ifequal_command",
            "setevent_command",
            "appear_command",
            "disappear_command",
        ],
    )


def test_compiled_phase_5_ids_use_the_reserved_numeric_slots(
    phase_5_constants: dict[str, int],
) -> None:
    assert [
        phase_5_constants["EVENT_GOT_KABUTO_FROM_ALPH"],
        phase_5_constants["EVENT_GOT_OMANYTE_FROM_ALPH"],
        phase_5_constants["EVENT_GOT_AERODACTYL_FROM_ALPH"],
    ] == [2004, 2005, 2006]
    assert phase_5_constants["NUM_EVENTS"] == 2048
    assert [
        phase_5_constants["SPRITE_KABUTO"],
        phase_5_constants["SPRITE_OMANYTE"],
        phase_5_constants["SPRITE_AERODACTYL"],
    ] == [0xA6, 0xA7, 0xA8]
    assert phase_5_constants["NUM_POKEMON_SPRITES"] == 41


def test_compiled_phase_5_sprite_table_extends_only_the_custom_rom(
    repo_root: Path, phase_5_constants: dict[str, int]
) -> None:
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_start = custom_symbols["SpriteMons"].rom_offset
    custom_end = custom_symbols["OutdoorSprites"].rom_offset
    custom_table = custom.slice(custom_start, custom_end - custom_start)
    assert len(custom_table) == phase_5_constants["NUM_POKEMON_SPRITES"]
    assert custom_table[-3:] == bytes(
        phase_5_constants[name] for name in ("KABUTO", "OMANYTE", "AERODACTYL")
    )

    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_start = reference_symbols["SpriteMons"].rom_offset
    reference_end = reference_symbols["OutdoorSprites"].rom_offset
    assert reference_end - reference_start == 35
    assert custom_table[:35] == reference.slice(reference_start, 35)


def test_phase_5_identity_does_not_change_the_save_layout(repo_root: Path) -> None:
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    assert symbols["wEventFlags"].bank == 1
    assert symbols["wEventFlags"].address == 55922
    assert symbols["wCurBox"].address - symbols["wEventFlags"].address == 256


def _event_check(command: int, event: int) -> bytes:
    return bytes([command]) + event.to_bytes(2, "little")


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


@pytest.mark.parametrize(
    ("species", "prefix"),
    [
        ("KABUTO", "RuinsOfAlphKabutoChamber"),
        ("OMANYTE", "RuinsOfAlphOmanyteChamber"),
        ("AERODACTYL", "RuinsOfAlphAerodactylChamber"),
    ],
)
def test_compiled_chamber_gates_check_picture_before_wall(
    repo_root: Path,
    phase_5_constants: dict[str, int],
    species: str,
    prefix: str,
) -> None:
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    picture = _event_check(
        phase_5_constants["checkevent_command"],
        phase_5_constants[f"EVENT_SOLVED_{species}_PUZZLE"],
    )
    wall = _event_check(
        phase_5_constants["checkevent_command"],
        phase_5_constants[f"EVENT_WALL_OPENED_IN_{species}_CHAMBER"],
    )

    ranges = (
        (f"{prefix}CheckWallScene", f"{prefix}NoopScene"),
        (f"{prefix}HiddenDoorsCallback", f"{prefix}WallOpenScript"),
        (f"{prefix}WallPatternRight", f"{prefix}SkyfallTopMovement"),
    )
    for start_label, end_label in ranges:
        start = custom_symbols[start_label].rom_offset
        end = custom_symbols[end_label].rom_offset
        compiled = custom.slice(start, end - start)
        assert compiled.index(picture) < compiled.index(wall)

        reference_start = reference_symbols[start_label].rom_offset
        reference_end = reference_symbols[end_label].rom_offset
        stock = reference.slice(reference_start, reference_end - reference_start)
        assert wall in stock
        if start_label.endswith("CheckWallScene") or start_label.endswith(
            "WallPatternRight"
        ):
            assert picture not in stock
        else:
            assert stock.index(wall) < stock.index(picture)

    scene_start = custom_symbols[f"{prefix}CheckWallScene"].rom_offset
    scene_end = custom_symbols[f"{prefix}NoopScene"].rom_offset
    scene = custom.slice(scene_start, scene_end - scene_start)
    assert bytes([phase_5_constants["sdefer_command"]]) in scene


def test_compiled_kabuto_scientist_checks_picture_before_wall(
    repo_root: Path, phase_5_constants: dict[str, int]
) -> None:
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    start = symbols["RuinsOfAlphKabutoChamberScientistScript"].rom_offset
    end = symbols["RuinsOfAlphKabutoChamberAncientReplica"].rom_offset
    script = rom.slice(start, end - start)
    picture = _event_check(
        phase_5_constants["checkevent_command"],
        phase_5_constants["EVENT_SOLVED_KABUTO_PUZZLE"],
    )
    wall = _event_check(
        phase_5_constants["checkevent_command"],
        phase_5_constants["EVENT_WALL_OPENED_IN_KABUTO_CHAMBER"],
    )
    assert script.index(picture) < script.index(wall)

    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_start = reference_symbols[
        "RuinsOfAlphKabutoChamberScientistScript"
    ].rom_offset
    reference_end = reference_symbols[
        "RuinsOfAlphKabutoChamberAncientReplica"
    ].rom_offset
    stock = reference.slice(reference_start, reference_end - reference_start)
    assert stock.index(wall) < stock.index(picture)


def test_compiled_kabuto_hidden_room_object_and_gift_match_the_contract(
    repo_root: Path, phase_5_constants: dict[str, int]
) -> None:
    custom_events = _object_events(
        repo_root,
        "crystallegends.gbc",
        "crystallegends.sym",
        "RuinsOfAlphKabutoItemRoom_MapEvents",
        phase_5_constants,
    )
    reference_events = _object_events(
        repo_root,
        "pokecrystal11.gbc",
        "pokecrystal11.sym",
        "RuinsOfAlphKabutoItemRoom_MapEvents",
        phase_5_constants,
    )
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference_symbols = SymbolTable.parse(
        (repo_root / "pokecrystal11.sym").read_text()
    )
    assert len(custom_events) == 5
    assert len(reference_events) == 4
    stock_scripts = (
        "RuinsOfAlphKabutoItemRoomBerry",
        "RuinsOfAlphKabutoItemRoomPsncureberry",
        "RuinsOfAlphKabutoItemRoomHealPowder",
        "RuinsOfAlphKabutoItemRoomEnergypowder",
    )
    for custom_event, reference_event, script_label in zip(
        custom_events[:4], reference_events, stock_scripts, strict=True
    ):
        assert custom_event.script_pointer == symbols[script_label].address
        assert reference_event.script_pointer == reference_symbols[script_label].address
        assert (
            custom_event.sprite,
            custom_event.y,
            custom_event.x,
            custom_event.movement,
            custom_event.radius,
            custom_event.hour_1,
            custom_event.hour_2,
            custom_event.palette_and_type,
            custom_event.sight_range,
            custom_event.event_flag,
        ) == (
            reference_event.sprite,
            reference_event.y,
            reference_event.x,
            reference_event.movement,
            reference_event.radius,
            reference_event.hour_1,
            reference_event.hour_2,
            reference_event.palette_and_type,
            reference_event.sight_range,
            reference_event.event_flag,
        )
    event = custom_events[-1]
    assert (event.x, event.y) == (3, 3)
    assert event.sprite == phase_5_constants["SPRITE_KABUTO"]
    assert event.movement == phase_5_constants["SPRITEMOVEDATA_POKEMON"]
    assert event.radius == 0
    assert event.palette_and_type == (
        phase_5_constants["PAL_NPC_BROWN"] << 4
        | phase_5_constants["OBJECTTYPE_SCRIPT"]
    )
    assert event.script_pointer == symbols[
        "RuinsOfAlphKabutoItemRoomKabutoScript"
    ].address
    assert event.event_flag == 0xFFFF

    rom = RomImage.load(repo_root / "crystallegends.gbc")
    script_start = symbols["RuinsOfAlphKabutoItemRoomKabutoScript"].rom_offset
    script_end = symbols["RuinsOfAlphKabutoItemRoomBerry"].rom_offset
    script = rom.slice(script_start, script_end - script_start)
    gift = bytes(
        [
            phase_5_constants["givepoke_command"],
            phase_5_constants["KABUTO"],
            10,
            phase_5_constants["NO_ITEM"],
            phase_5_constants["FALSE"],
        ]
    )
    full = (
        bytes([phase_5_constants["ifequal_command"], 2])
        + symbols[
            "RuinsOfAlphKabutoItemRoomKabutoScript.StorageFull"
        ].address.to_bytes(2, "little")
    )
    complete = bytes([phase_5_constants["setevent_command"]]) + phase_5_constants[
        "EVENT_GOT_KABUTO_FROM_ALPH"
    ].to_bytes(2, "little")
    object_id = len(custom_events) + 1
    disappear = bytes([phase_5_constants["disappear_command"], object_id])
    positions = [
        script.index(pattern) for pattern in (gift, full, complete, disappear)
    ]
    assert positions == sorted(positions)

    callback_start = symbols[
        "RuinsOfAlphKabutoItemRoomKabutoCallback"
    ].rom_offset
    callback_end = symbols["RuinsOfAlphKabutoItemRoomKabutoScript"].rom_offset
    callback = rom.slice(callback_start, callback_end - callback_start)
    checks = [
        _event_check(
            phase_5_constants["checkevent_command"], phase_5_constants[event_name]
        )
        for event_name in (
            "EVENT_GOT_KABUTO_FROM_ALPH",
            "EVENT_SOLVED_KABUTO_PUZZLE",
            "EVENT_WALL_OPENED_IN_KABUTO_CHAMBER",
        )
    ]
    assert [callback.index(check) for check in checks] == sorted(
        callback.index(check) for check in checks
    )
    assert bytes([phase_5_constants["appear_command"], object_id]) in callback
    assert disappear in callback

    assert "RuinsOfAlphKabutoItemRoomKabutoCallback" not in reference_symbols
    assert "RuinsOfAlphKabutoItemRoomKabutoScript" not in reference_symbols
