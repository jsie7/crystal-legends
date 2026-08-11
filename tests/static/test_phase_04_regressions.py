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


pytestmark = [pytest.mark.static, pytest.mark.phase4]


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


def test_phase_4_event_slots_are_reserved_without_changing_num_events(
    repo_root: Path,
) -> None:
    source = repo_root / "constants/event_flags.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    names = [
        "EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST",
        "EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER",
        "EVENT_GOT_TOTODILE_FROM_CIANWOOD",
    ]

    _assert_contiguous(
        crystal,
        ["const EVENT_OAK_MOVED_THIRD_BIRD", *(f"const {name}" for name in names)],
    )
    assert all(not any(name in line for line in reference) for name in names)
    _assert_contiguous(
        reference,
        [
            "const_skip",
            "const_skip 3",
        ],
    )


def test_phase_4_sprite_ids_append_to_the_stock_icon_table(repo_root: Path) -> None:
    constants = repo_root / "constants/sprite_constants.asm"
    table = repo_root / "data/sprites/sprite_mons.asm"
    crystal_constants = _active_code(constants, CRYSTAL_LEGENDS)
    reference_constants = _active_code(constants, REFERENCE)
    crystal_table = _active_code(table, CRYSTAL_LEGENDS)
    reference_table = _active_code(table, REFERENCE)

    _assert_contiguous(
        crystal_constants,
        [
            "const SPRITE_HO_OH",
            "const SPRITE_CHIKORITA",
            "const SPRITE_CYNDAQUIL",
            "const SPRITE_TOTODILE",
        ],
    )
    _assert_contiguous(
        crystal_table,
        [
            "db HO_OH",
            "db CHIKORITA",
            "db CYNDAQUIL",
            "db TOTODILE",
        ],
    )
    assert not any("SPRITE_CHIKORITA" in line for line in reference_constants)
    assert not any("db CHIKORITA" == line for line in reference_table)


def test_ilex_chikorita_source_contract_is_retry_safe_and_isolated(
    repo_root: Path,
) -> None:
    source = repo_root / "maps/IlexForest.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    object_row = (
        "object_event  9, 23, SPRITE_CHIKORITA, SPRITEMOVEDATA_POKEMON, 0, 0, "
        "-1, -1, PAL_NPC_GREEN, OBJECTTYPE_SCRIPT, 0, "
        "IlexForestChikoritaScript, EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST"
    )

    assert object_row in crystal
    assert object_row not in reference
    assert "const ILEXFOREST_CHIKORITA" in crystal
    assert "const ILEXFOREST_CHIKORITA" not in reference
    _assert_contiguous(
        crystal,
        [
            "IlexForestChikoritaScript:",
            "faceplayer",
            "opentext",
            "cry CHIKORITA",
            "checkevent EVENT_GOT_HM01_CUT",
            "iffalse .NotReady",
            "writetext IlexForestChikoritaOfferText",
            "yesorno",
            "iffalse .Declined",
            "givepoke CHIKORITA, 14",
            "ifequal 2, .StorageFull",
            "setevent EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST",
            "writetext IlexForestChikoritaJoinedText",
            "playsound SFX_CAUGHT_MON",
            "waitsfx",
            "waitbutton",
            "closetext",
            "disappear ILEXFOREST_CHIKORITA",
            "end",
        ],
    )
    script_start = crystal.index("IlexForestChikoritaScript:")
    script_end = crystal.index("MovementData_Farfetchd_Pos1_Pos2:")
    script = "\n".join(crystal[script_start:script_end])
    assert "FROM_ELM" not in script
    assert "EVENT_FOREST_IS_RESTLESS" not in script
    assert "GS_BALL" not in script
    assert "IlexForestShrineScript:" in crystal
    assert "bg_event  8, 22, BGEVENT_UP, IlexForestShrineScript" in crystal


def test_burned_tower_cyndaquil_visibility_and_gift_contract(
    repo_root: Path,
) -> None:
    source = repo_root / "maps/BurnedTowerB1F.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    object_row = (
        "object_event 10,  4, SPRITE_CYNDAQUIL, SPRITEMOVEDATA_POKEMON, 0, 0, "
        "-1, -1, PAL_NPC_RED, OBJECTTYPE_SCRIPT, 0, "
        "BurnedTowerB1FCyndaquilScript, -1"
    )

    assert object_row in crystal
    assert object_row not in reference
    assert "const BURNEDTOWERB1F_CYNDAQUIL" in crystal
    assert "const BURNEDTOWERB1F_CYNDAQUIL" not in reference
    _assert_contiguous(
        crystal,
        [
            "BurnedTowerB1FCyndaquilCallback:",
            "checkevent EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER",
            "iftrue .Hide",
            "checkevent EVENT_RELEASED_THE_BEASTS",
            "iffalse .Hide",
            "appear BURNEDTOWERB1F_CYNDAQUIL",
            "endcallback",
            ".Hide:",
            "disappear BURNEDTOWERB1F_CYNDAQUIL",
            "endcallback",
        ],
    )
    _assert_contiguous(
        crystal,
        [
            "BurnedTowerB1FCyndaquilScript:",
            "faceplayer",
            "opentext",
            "checkevent EVENT_RELEASED_THE_BEASTS",
            "iffalse .NotReady",
            "cry CYNDAQUIL",
            "writetext BurnedTowerB1FCyndaquilOfferText",
            "yesorno",
            "iffalse .Declined",
            "givepoke CYNDAQUIL, 19",
            "ifequal 2, .StorageFull",
            "setevent EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER",
            "writetext BurnedTowerB1FCyndaquilJoinedText",
            "playsound SFX_CAUGHT_MON",
            "waitsfx",
            "waitbutton",
            "closetext",
            "disappear BURNEDTOWERB1F_CYNDAQUIL",
            "end",
        ],
    )
    release_start = crystal.index("ReleaseTheBeasts:")
    release_end = crystal.index("BurnedTowerB1FCyndaquilScript:")
    release = crystal[release_start:release_end]
    assert release.index("disappear BURNEDTOWERB1F_SUICUNE1") < release.index(
        "setevent EVENT_RELEASED_THE_BEASTS"
    ) < release.index("appear BURNEDTOWERB1F_CYNDAQUIL")
    assert "special InitRoamMons" in release
    assert "setmapscene CIANWOOD_CITY, SCENE_CIANWOODCITY_SUICUNE_AND_EUSINE" in release
    assert "BurnedTowerB1FCyndaquilCallback:" not in reference
    assert "BurnedTowerB1FCyndaquilScript:" not in reference


def test_cianwood_totodile_rescue_is_event_gated_and_item_neutral(
    repo_root: Path,
) -> None:
    city_source = repo_root / "maps/CianwoodCity.asm"
    pharmacy_source = repo_root / "maps/CianwoodPharmacy.asm"
    city = _active_code(city_source, CRYSTAL_LEGENDS)
    reference_city = _active_code(city_source, REFERENCE)
    pharmacy = _active_code(pharmacy_source, CRYSTAL_LEGENDS)
    reference_pharmacy = _active_code(pharmacy_source, REFERENCE)
    object_row = (
        "object_event 28, 38, SPRITE_TOTODILE, SPRITEMOVEDATA_SWIM_WANDER, 0, "
        "0, -1, -1, PAL_NPC_BLUE, OBJECTTYPE_SCRIPT, 0, "
        "CianwoodCityTotodileScript, EVENT_GOT_TOTODILE_FROM_CIANWOOD"
    )

    assert object_row in city
    assert object_row not in reference_city
    assert "const CIANWOODCITY_TOTODILE" in city
    assert "const CIANWOODCITY_TOTODILE" not in reference_city
    _assert_contiguous(
        city,
        [
            "CianwoodCityTotodileScript:",
            "faceplayer",
            "opentext",
            "cry TOTODILE",
            "checkevent EVENT_GOT_SECRETPOTION_FROM_PHARMACY",
            "iffalse .NotReady",
            "writetext CianwoodCityTotodileOfferText",
            "yesorno",
            "iffalse .Declined",
            "givepoke TOTODILE, 24",
            "ifequal 2, .StorageFull",
            "setevent EVENT_GOT_TOTODILE_FROM_CIANWOOD",
            "writetext CianwoodCityTotodileJoinedText",
            "playsound SFX_CAUGHT_MON",
            "waitsfx",
            "waitbutton",
            "closetext",
            "disappear CIANWOODCITY_TOTODILE",
            "end",
        ],
    )
    script_start = city.index("CianwoodCityTotodileScript:")
    script_end = city.index("CianwoodCityYoungster:")
    script = "\n".join(city[script_start:script_end])
    assert "takeitem" not in script
    assert "EVENT_JASMINE_RETURNED_TO_GYM" not in script
    assert "SECRETPOTION" not in script.replace(
        "EVENT_GOT_SECRETPOTION_FROM_PHARMACY", ""
    )
    assert "PharmacistEastShoreHintText:" in pharmacy
    assert "PharmacistEastShoreHintText:" not in reference_pharmacy
    assert pharmacy.index("giveitem SECRETPOTION") < pharmacy.index(
        "setevent EVENT_GOT_SECRETPOTION_FROM_PHARMACY"
    ) < pharmacy.index("writetext PharmacistEastShoreHintText")
    for stock_line in (
        "giveitem SECRETPOTION",
        "setevent EVENT_GOT_SECRETPOTION_FROM_PHARMACY",
        "pokemart MARTTYPE_PHARMACY, MART_CIANWOOD",
    ):
        assert stock_line in reference_pharmacy


def test_phase_4_object_tiles_match_the_locked_collision_contract(
    repo_root: Path,
) -> None:
    dimensions = parse_map_dimensions(
        (repo_root / "constants/map_constants.asm").read_text()
    )
    block_paths = block_paths_for_maps(
        dimensions,
        parse_block_paths((repo_root / "data/maps/blocks.asm").read_text()),
    )
    tilesets = parse_map_tilesets((repo_root / "data/maps/maps.asm").read_text())
    expected = {
        ("ILEX_FOREST", (9, 23)): "FLOOR",
        ("BURNED_TOWER_B1F", (10, 4)): "FLOOR",
        ("CIANWOOD_CITY", (28, 38)): "WATER",
    }
    for (map_name, coordinate), collision in expected.items():
        assert collision_at(
            repo_root,
            map_name,
            coordinate,
            dimensions,
            block_paths,
            tilesets,
        ) == collision
