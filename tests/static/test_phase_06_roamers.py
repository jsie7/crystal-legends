from __future__ import annotations

import json
from pathlib import Path

import pytest


pytestmark = [pytest.mark.static, pytest.mark.phase6]


FLEE_GROUPS = (
    (
        "MAGNEMITE",
        "GRIMER",
        "TANGELA",
        "MR__MIME",
        "EEVEE",
        "PORYGON",
        "DRATINI",
        "DRAGONAIR",
        "TOGETIC",
        "UMBREON",
        "UNOWN",
        "SNUBBULL",
        "HERACROSS",
    ),
    (
        "CUBONE",
        "ARTICUNO",
        "ZAPDOS",
        "MOLTRES",
        "QUAGSIRE",
        "DELIBIRD",
        "PHANPY",
        "TEDDIURSA",
    ),
    ("RAIKOU", "ENTEI"),
)


def _code(path: Path) -> list[str]:
    return [
        line.split(";", 1)[0].strip()
        for line in path.read_text().splitlines()
        if line.split(";", 1)[0].strip()
    ]


def _section(lines: list[str], start: str, end: str) -> list[str]:
    first = lines.index(start)
    return lines[first : lines.index(end, first + 1)]


def _assert_contiguous(lines: list[str], expected: list[str]) -> None:
    width = len(expected)
    assert any(
        lines[index : index + width] == expected for index in range(len(lines))
    )


def test_phase_6_scenario_contract_is_locked(repo_root: Path) -> None:
    contract = json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_06_roamers.json").read_text()
    )
    assert contract["max_frames_per_step"] == 60000
    assert contract["release"] == {
        "map": "BURNED_TOWER_B1F",
        "start": {"x": 10, "y": 7, "facing": "UP"},
        "event": "EVENT_RELEASED_THE_BEASTS",
    }
    assert contract["encounter"] == {
        "map": "ROUTE_37",
        "grass": [[8, 4], [9, 4]],
        "different_route": "ROUTE_38",
    }
    assert contract["water_rejection"] == {
        "map": "ROUTE_42",
        "coordinate": [14, 4],
    }
    assert [row["species"] for row in contract["roamers"]] == ["RAIKOU", "ENTEI"]
    assert [row["slot"] for row in contract["roamers"]] == [
        "wRoamMon1",
        "wRoamMon2",
    ]
    assert all(row["level"] == 40 for row in contract["roamers"])
    assert [row["starting_route"] for row in contract["roamers"]] == [
        "ROUTE_42",
        "ROUTE_37",
    ]
    assert all(row["permanent_after_defeat"] for row in contract["roamers"])
    assert all(row["permanent_after_capture"] for row in contract["roamers"])


def test_stock_release_and_roam_struct_contracts_are_unchanged(repo_root: Path) -> None:
    release = _code(repo_root / "maps/BurnedTowerB1F.asm")
    release = _section(release, "ReleaseTheBeasts:", "BurnedTowerB1FCyndaquilScript:")
    assert release.index("setevent EVENT_RELEASED_THE_BEASTS") < release.index(
        "special InitRoamMons"
    )

    wildmons = _code(repo_root / "engine/overworld/wildmons.asm")
    init = _section(wildmons, "InitRoamMons:", "CheckEncounterRoamMon:")
    _assert_contiguous(
        init,
        [
            "ld a, RAIKOU",
            "ld [wRoamMon1Species], a",
            "ld a, ENTEI",
            "ld [wRoamMon2Species], a",
        ],
    )
    assert init.count("ld a, 40") == 1
    assert "ld [wRoamMon1Level], a" in init
    assert "ld [wRoamMon2Level], a" in init
    assert "ld a, GROUP_ROUTE_42" in init
    assert "ld [wRoamMon1MapGroup], a" in init
    assert "ld a, MAP_ROUTE_42" in init
    assert "ld [wRoamMon1MapNumber], a" in init
    assert "ld a, GROUP_ROUTE_37" in init
    assert "ld [wRoamMon2MapGroup], a" in init
    assert "ld a, MAP_ROUTE_37" in init
    assert "ld [wRoamMon2MapNumber], a" in init
    assert init[-4:] == [
        "xor a",
        "ld [wRoamMon1HP], a",
        "ld [wRoamMon2HP], a",
        "ret",
    ]

    roam_macro = _code(repo_root / "macros/ram.asm")
    roam_macro = _section(roam_macro, "MACRO roam_struct", "ENDM")
    assert roam_macro == [
        "MACRO roam_struct",
        r"\1Species::   db",
        r"\1Level::     db",
        r"\1MapGroup::  db",
        r"\1MapNumber:: db",
        r"\1HP::        db",
        r"\1DVs::       dw",
    ]


def test_stock_route_graph_has_the_exact_16_land_routes(repo_root: Path) -> None:
    source = _code(repo_root / "data/wild/roammon_maps.asm")
    rows = [line for line in source if line.startswith("roam_map ")]
    assert len(rows) == 16
    assert [row.split(",", 1)[0].removeprefix("roam_map ") for row in rows] == [
        "ROUTE_29",
        "ROUTE_30",
        "ROUTE_31",
        "ROUTE_32",
        "ROUTE_33",
        "ROUTE_34",
        "ROUTE_35",
        "ROUTE_36",
        "ROUTE_37",
        "ROUTE_38",
        "ROUTE_39",
        "ROUTE_42",
        "ROUTE_43",
        "ROUTE_44",
        "ROUTE_45",
        "ROUTE_46",
    ]
    route_37 = next(row for row in rows if row.startswith("roam_map ROUTE_37,"))
    assert route_37 == "roam_map ROUTE_37, ROUTE_36, ROUTE_38, ROUTE_42"
    assert "ROUTE_40" not in "\n".join(rows)
    assert "ROUTE_41" not in "\n".join(rows)
    assert "assert __roam_maps__ == NUM_ROAMMON_MAPS, \\" in source


def test_encounter_tracker_and_battle_end_paths_remain_stock(repo_root: Path) -> None:
    wildmons = _code(repo_root / "engine/overworld/wildmons.asm")
    encounter = _section(wildmons, "CheckEncounterRoamMon:", "UpdateRoamMons:")
    assert encounter[:4] == [
        "CheckEncounterRoamMon:",
        "push hl",
        "call CheckOnWater",
        "jr z, .DontEncounterRoamMon",
    ]
    for line in (
        "call CopyCurrMapDE",
        "call Random",
        "cp 100",
        "and %00000011",
        "ld a, 7",
        "ld [wTempWildMonSpecies], a",
        "ld [wCurPartyLevel], a",
        "ld a, BATTLETYPE_ROAMING",
        "ld [wBattleType], a",
    ):
        assert line in encounter

    find_nest = _section(wildmons, "FindNest:", "TryWildEncounter::")
    assert find_nest.index("call .RoamMon1") < find_nest.index("call .RoamMon2")
    for slot in (1, 2):
        start = find_nest.index(f".RoamMon{slot}:")
        end = (
            find_nest.index(f".RoamMon{slot + 1}:")
            if slot == 1
            else len(find_nest)
        )
        branch = find_nest[start:end]
        assert f"ld a, [wRoamMon{slot}Species]" in branch
        assert f"ld a, [wRoamMon{slot}MapGroup]" in branch
        assert f"ld a, [wRoamMon{slot}MapNumber]" in branch
        assert "call .AppendNest" in branch

    battle = _code(repo_root / "engine/battle/core.asm")
    battle_end = _section(
        battle, "BattleEnd_HandleRoamMons:", "GetRoamMonMapGroup:"
    )
    assert battle_end[:4] == [
        "BattleEnd_HandleRoamMons:",
        "ld a, [wBattleType]",
        "cp BATTLETYPE_ROAMING",
        "jr nz, .not_roaming",
    ]
    assert "ld a, [wEnemyMonHP + 1]" in battle_end
    assert "ld [hl], GROUP_N_A" in battle_end
    assert "ld [hl], MAP_N_A" in battle_end
    assert battle_end.count("ld [hl], 0") == 2


def test_phase_6_adds_no_roamer_or_save_state(repo_root: Path) -> None:
    forbidden = (
        "RespawnDefeatedRoamMons",
        "EVENT_RESPAWN",
        "wRoamMonRespawn",
    )
    for path in (
        repo_root / "engine/overworld/wildmons.asm",
        repo_root / "engine/events/halloffame.asm",
        repo_root / "constants/event_flags.asm",
        repo_root / "ram/wram.asm",
    ):
        source = path.read_text()
        assert all(token not in source for token in forbidden)


def test_fast_ball_custom_branch_scans_each_complete_stock_group(
    repo_root: Path,
) -> None:
    item_effects = _code(repo_root / "engine/items/item_effects.asm")
    fast_ball = _section(
        item_effects, "FastBallMultiplier:", "LevelBallMultiplier:"
    )
    mismatch = fast_ball.index("cp c")
    assert fast_ball[mismatch : mismatch + 6] == [
        "cp c",
        "if DEF(_CRYSTALLEGENDS)",
        "jr nz, .loop",
        "else",
        "jr nz, .next",
        "endc",
    ]
    assert "ld d, 3" in fast_ball
    assert fast_ball.count("sla b") == 2
    assert "ld b, $ff" in fast_ball

    flee_mons = _code(repo_root / "data/wild/flee_mons.asm")
    labels = ("SometimesFleeMons:", "OftenFleeMons:", "AlwaysFleeMons:")
    actual_groups: list[tuple[str, ...]] = []
    for index, label in enumerate(labels):
        start = flee_mons.index(label) + 1
        end = (
            flee_mons.index(labels[index + 1])
            if index + 1 < len(labels)
            else len(flee_mons)
        )
        rows = flee_mons[start:end]
        assert rows[-1] == "db -1"
        actual_groups.append(tuple(row.removeprefix("db ") for row in rows[:-1]))
    assert tuple(actual_groups) == FLEE_GROUPS
    assert sum(map(len, actual_groups)) == 23


def test_fast_ball_multiplier_model_covers_all_23_species_and_a_control() -> None:
    def multiplier(species: str, catch_rate: int) -> int:
        for group in FLEE_GROUPS:
            for candidate in group:
                if candidate == species:
                    return min(catch_rate * 4, 0xFF)
        return catch_rate

    for species in (candidate for group in FLEE_GROUPS for candidate in group):
        assert multiplier(species, 50) == 200
        assert multiplier(species, 100) == 0xFF
    assert multiplier("PIDGEY", 50) == 50
