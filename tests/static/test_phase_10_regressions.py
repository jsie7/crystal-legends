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
