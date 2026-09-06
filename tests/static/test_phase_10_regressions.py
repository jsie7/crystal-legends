from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import pytest

from tests.support.asm_conditions import active_lines


pytestmark = [pytest.mark.static, pytest.mark.phase10]

CRYSTAL_LEGENDS = {"_CRYSTAL11", "_CRYSTALLEGENDS"}
REFERENCE = {"_CRYSTAL11"}


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_10_giovanni_cerulean_cave.json").read_text()
    )


def _active_code(path: Path, definitions: set[str]) -> list[str]:
    return [
        line.text.split(";", 1)[0].strip()
        for line in active_lines(path.read_text(), definitions)
        if line.text.split(";", 1)[0].strip()
    ]


def _changed_offsets(stock: bytes, custom: bytes) -> list[list[int]]:
    return [
        [index, left, right]
        for index, (left, right) in enumerate(zip(stock, custom, strict=True))
        if left != right
    ]


def _section(lines: list[str], start: str, end: str) -> list[str]:
    first = lines.index(start)
    return lines[first : lines.index(end, first) + 1]


def _contains_sequence(lines: list[str], expected: list[str]) -> bool:
    normalized = [" ".join(line.split()) for line in lines]
    wanted = [" ".join(line.split()) for line in expected]
    return any(
        normalized[index : index + len(wanted)] == wanted
        for index in range(len(normalized))
    )


def test_phase_10_event_reservations_are_internal_and_reference_safe(
    repo_root: Path, scenario: dict
) -> None:
    source = repo_root / "constants/event_flags.asm"
    custom = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    for group in scenario["events"].values():
        names = [name for name, _ in group]
        indices = [custom.index(f"const {name}") for name in names]
        assert indices == list(range(indices[0], indices[0] + len(names)))
        assert all(not any(name in line for line in reference) for name in names)
    assert "const_skip 7" in reference
    assert all("2039" not in line for line in custom)
    assert "; Unused: next 9 events" in source.read_text()


def test_phase_10_uses_the_approved_map_and_same_size_replacements(
    repo_root: Path, scenario: dict
) -> None:
    cave = repo_root / scenario["map"]["block_path"]
    payload = cave.read_bytes()
    assert len(payload) == 15 * 18
    assert sha256(payload).hexdigest() == scenario["map"]["block_sha256"]
    assert payload == (repo_root / "plan/proposals/CeruleanCave.blk").read_bytes()

    exterior = scenario["exterior"]
    route_stock = (repo_root / exterior["route4_stock"]).read_bytes()
    route_custom = (repo_root / exterior["route4_custom"]).read_bytes()
    city_stock = (repo_root / exterior["cerulean_stock"]).read_bytes()
    city_custom = (repo_root / exterior["cerulean_custom"]).read_bytes()
    assert len(route_stock) == len(route_custom) == 20 * 9
    assert len(city_stock) == len(city_custom) == 20 * 18
    assert _changed_offsets(route_stock, route_custom) == exterior["route4_deltas"]
    assert _changed_offsets(city_stock, city_custom) == exterior["cerulean_deltas"]

    blocks = _active_code(repo_root / "data/maps/blocks.asm", CRYSTAL_LEGENDS)
    reference = _active_code(repo_root / "data/maps/blocks.asm", REFERENCE)
    assert 'INCBIN "maps/CeruleanCave.blk"' in blocks
    assert 'INCBIN "maps/unused/BetaCaveTestMap.blk"' not in blocks
    assert 'INCBIN "maps/unused/BetaCaveTestMap.blk"' in reference
    assert 'INCBIN "maps/CeruleanCave.blk"' not in reference


def test_phase_10_map_registration_and_native_warps_match_the_contract(
    repo_root: Path, scenario: dict
) -> None:
    constants = _active_code(repo_root / "constants/map_constants.asm", CRYSTAL_LEGENDS)
    reference = _active_code(repo_root / "constants/map_constants.asm", REFERENCE)
    assert "map_const CERULEAN_CAVE,                               15, 18" in constants
    assert not any("CERULEAN_CAVE" in line for line in reference)

    maps = _active_code(repo_root / "data/maps/maps.asm", CRYSTAL_LEGENDS)
    expected = "map CeruleanCave, " + ", ".join(scenario["map"]["metadata"][:-1])
    assert any(line.startswith(expected + ", ") for line in maps)

    route = _active_code(repo_root / "maps/Route4.asm", CRYSTAL_LEGENDS)
    cave = _active_code(repo_root / "maps/CeruleanCave.asm", CRYSTAL_LEGENDS)
    assert "warp_event 38,  3, CERULEAN_CAVE, 1" in route
    assert "warp_event 21, 33, ROUTE_4, 2" in cave
    assert not any("CERULEAN_CAVE" in line for line in _active_code(repo_root / "maps/Route4.asm", REFERENCE))


def test_route_4_guard_derives_access_without_a_saved_open_flag(repo_root: Path) -> None:
    route = _active_code(repo_root / "maps/Route4.asm", CRYSTAL_LEGENDS)
    expected = [
        "checkevent EVENT_PROJECT_MEW_RESOLVED",
        "iffalse .ShowGuard",
        "checkevent EVENT_SILVER_BIRD_RELEASED",
        "iffalse .ShowGuard",
        "readvar VAR_BADGES",
        "ifless 14, .ShowGuard",
        "disappear ROUTE4_CERULEAN_CAVE_GUARD",
    ]
    start = route.index("Route4CeruleanCaveGuardCallback:")
    callback = route[start : route.index("Route4CeruleanCaveGuardScript:")]
    position = -1
    for line in expected:
        position = callback.index(line, position + 1)
    assert not any(line.startswith(("setevent ", "clearevent ")) for line in callback)
    assert not any("CERULEAN_CAVE_OPEN" in line for line in route)
    assert (
        "object_event 38,  4, SPRITE_ROCKET, SPRITEMOVEDATA_STANDING_RIGHT, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, Route4CeruleanCaveGuardScript, -1"
        in route
    )


def test_giovanni_trainer_class_art_and_party_are_custom_only(repo_root: Path) -> None:
    portrait = repo_root / "gfx/trainers/giovanni.png"
    assert sha256(portrait.read_bytes()).hexdigest() == (
        "4cf1d940ceeb00e530b361b1a95ea8c31492faf86bb5c20f0ac45c70768b2034"
    )

    constants = _active_code(repo_root / "constants/trainer_constants.asm", CRYSTAL_LEGENDS)
    reference = _active_code(repo_root / "constants/trainer_constants.asm", REFERENCE)
    assert constants[-3:] == ["trainerclass GIOVANNI", "const GIOVANNI1", "DEF NUM_TRAINER_CLASSES EQU __trainer_class__ - 1"]
    assert not any("GIOVANNI" in line for line in reference)

    parties = _active_code(repo_root / "data/trainers/parties.asm", CRYSTAL_LEGENDS)
    start = parties.index("GiovanniGroup:")
    assert parties[start : start + 9] == [
        "GiovanniGroup:",
        'db "GIOVANNI@", TRAINERTYPE_MOVES',
        "db 70, PERSIAN,    SLASH, FAINT_ATTACK, SCREECH, THUNDER",
        "db 71, DUGTRIO,    EARTHQUAKE, SLASH, SANDSTORM, MUD_SLAP",
        "db 72, KANGASKHAN, RETURN, EARTHQUAKE, SHADOW_BALL, REST",
        "db 73, NIDOQUEEN,  EARTHQUAKE, ICE_BEAM, THUNDER, BODY_SLAM",
        "db 74, NIDOKING,   EARTHQUAKE, THUNDER, FIRE_BLAST, SURF",
        "db 75, RHYDON,     EARTHQUAKE, ROCK_SLIDE, MEGAHORN, REST",
        "db -1",
    ]
    assert not any("GiovanniGroup" in line for line in _active_code(repo_root / "data/trainers/parties.asm", REFERENCE))


def test_giovanni_extends_every_applicable_trainer_table(repo_root: Path) -> None:
    expected = {
        "data/trainers/party_pointers.asm": "dw GiovanniGroup",
        "data/trainers/class_names.asm": 'li "ROCKET BOSS"',
        "data/trainers/dvs.asm": "dn 15, 13, 13, 14",
        "data/trainers/encounter_music.asm": "db MUSIC_ROCKET_ENCOUNTER",
        "data/trainers/pic_pointers.asm": "dba_pic GiovanniPic",
        "data/trainers/palettes.asm": 'INCBIN "gfx/trainers/giovanni.gbcpal", middle_colors',
    }
    for relative, row in expected.items():
        custom = _active_code(repo_root / relative, CRYSTAL_LEGENDS)
        reference = _active_code(repo_root / relative, REFERENCE)
        assert any(line.startswith(row) for line in custom)
        assert not any("Giovanni" in line or "GIOVANNI" in line for line in reference)

    attributes = _active_code(repo_root / "data/trainers/attributes.asm", CRYSTAL_LEGENDS)
    giovanni = attributes[attributes.index("db FULL_HEAL, FULL_RESTORE", -12) :]
    assert "dw AI_BASIC | AI_SETUP | AI_SMART | AI_AGGRESSIVE | AI_CAUTIOUS | AI_STATUS | AI_RISKY" in giovanni
    assert "dw CONTEXT_USE | SWITCH_SOMETIMES" in giovanni

    battle = _active_code(repo_root / "engine/battle/start_battle.asm", CRYSTAL_LEGENDS)
    music = battle.index("ld de, MUSIC_KANTO_GYM_LEADER_BATTLE")
    assert battle[music + 1 : music + 3] == ["cp GIOVANNI", "jr z, .done"]


def test_custom_omastar_compression_is_lossless_and_saves_five_bytes(repo_root: Path) -> None:
    original = repo_root / "gfx/pokemon/omastar/back.2bpp.lz"
    custom = repo_root / "gfx/pokemon/omastar/back_crystallegends.lz"
    if custom.exists():
        assert len(original.read_bytes()) == 429
        assert len(custom.read_bytes()) == 424


def test_cerulean_cave_remnant_parties_are_exact_and_custom_only(
    repo_root: Path, scenario: dict
) -> None:
    constants = _active_code(repo_root / "constants/trainer_constants.asm", CRYSTAL_LEGENDS)
    reference_constants = _active_code(repo_root / "constants/trainer_constants.asm", REFERENCE)
    parties = _active_code(repo_root / "data/trainers/parties.asm", CRYSTAL_LEGENDS)
    reference_parties = _active_code(repo_root / "data/trainers/parties.asm", REFERENCE)

    for remnant in scenario["remnants"]:
        assert f'const {remnant["trainer"]}' in constants
        assert f'const {remnant["trainer"]}' not in reference_constants
        expected = [
            f'db "{("ROSS" if remnant["trainer"] == "ROSS2" else "MITCH" if remnant["trainer"] == "MITCH2" else "GRUNT")}@", TRAINERTYPE_MOVES',
            *(
                f'db {level}, {species}, ' + ", ".join(moves)
                for level, species, moves in remnant["party"]
            ),
            "db -1",
        ]
        assert _contains_sequence(parties, expected)
        assert not any(remnant["trainer"] in line for line in reference_constants)
    assert "db 57, RATICATE,   SUPER_FANG, HYPER_FANG, QUICK_ATTACK, PURSUIT" not in reference_parties


def test_cerulean_cave_population_items_and_records_match_contract(
    repo_root: Path, scenario: dict
) -> None:
    cave = _active_code(repo_root / "maps/CeruleanCave.asm", CRYSTAL_LEGENDS)
    for remnant in scenario["remnants"]:
        object_rows = [line for line in cave if line.startswith("object_event ")]
        matching = [
            line
            for line in object_rows
            if f'object_event {remnant["coordinate"][0]:2}, {remnant["coordinate"][1]:2}, {remnant["sprite"]}, {remnant["movement"]}' in line
        ]
        assert len(matching) == 1
        row = matching[0]
        assert f', {remnant["palette"]}, OBJECTTYPE_TRAINER, {remnant["sight"]}, ' in row
        assert row.endswith(", EVENT_BEAT_GIOVANNI")
        assert any(
            line.startswith(f'trainer {remnant["class"]}, {remnant["trainer"]}, {remnant["event"]},')
            for line in cave
        )

    for pickup in scenario["pickups"]:
        script = cave.index(f'{pickup["script"]}:')
        assert cave[script + 1] == f'itemball {pickup["item"]}'
        assert any(
            line.startswith(f'object_event {pickup["coordinate"][0]:2}, {pickup["coordinate"][1]:2}, SPRITE_POKE_BALL')
            and line.endswith(f', {pickup["event"]}')
            for line in cave
        )
    hidden = scenario["hidden_pickup"]
    script = cave.index(f'{hidden["script"]}:')
    assert cave[script + 1] == f'hiddenitem {hidden["item"]}, {hidden["event"]}'
    assert f'bg_event {hidden["coordinate"][0]:2}, {hidden["coordinate"][1]:2}, BGEVENT_ITEM, {hidden["script"]}' in cave

    for record in scenario["lab_records"]:
        for x, y in record["coordinates"]:
            assert f'bg_event {x:2}, {y:2}, BGEVENT_READ, {record["script"]}' in cave
        start = cave.index(f'{record["script"]}:')
        body = cave[start : start + 4]
        assert ("playsound SFX_BOOT_PC" in body) is record["terminal"]


def test_cerulean_cave_wild_and_fishing_tables_match_contract(
    repo_root: Path, scenario: dict
) -> None:
    encounters = scenario["encounters"]
    grass_lines = _active_code(repo_root / "data/wild/kanto_grass.asm", CRYSTAL_LEGENDS)
    grass = _section(grass_lines, "def_grass_wildmons CERULEAN_CAVE", "end_grass_wildmons")
    expected_slots = [
        f"db {level}, {species}" for _ in range(3) for level, species in encounters["grass"]["slots"]
    ]
    assert grass == [
        "def_grass_wildmons CERULEAN_CAVE",
        "db 6 percent, 6 percent, 6 percent",
        *expected_slots,
        "end_grass_wildmons",
    ]

    water_lines = _active_code(repo_root / "data/wild/kanto_water.asm", CRYSTAL_LEGENDS)
    water = _section(water_lines, "def_water_wildmons CERULEAN_CAVE", "end_water_wildmons")
    assert water == [
        "def_water_wildmons CERULEAN_CAVE",
        "db 4 percent",
        *(f"db {level}, {species}" for level, species in encounters["water"]["slots"]),
        "end_water_wildmons",
    ]

    fish = _active_code(repo_root / "data/wild/fish.asm", CRYSTAL_LEGENDS)
    assert "fishgroup 50 percent + 1, .CeruleanCave_Old,     .CeruleanCave_Good,     .CeruleanCave_Super" in fish
    for rod in ("old", "good", "super"):
        label = f'.CeruleanCave_{rod.title()}:'
        start = fish.index(label)
        expected = [
            f"db {chance}, {species}, {level}"
            for chance, species, level in encounters["fishing"][rod]
        ]
        assert [" ".join(line.split()) for line in fish[start + 1 : start + 1 + len(expected)]] == [
            " ".join(line.split()) for line in expected
        ]

    for relative in ("data/wild/kanto_grass.asm", "data/wild/kanto_water.asm", "data/wild/fish.asm"):
        assert not any("CERULEAN_CAVE" in line or "CeruleanCave" in line for line in _active_code(repo_root / relative, REFERENCE))
