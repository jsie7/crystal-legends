from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.asm_conditions import active_lines


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
            "const_next 2048",
            "DEF NUM_EVENTS EQU const_value",
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
            "DEF NUM_POKEMON_SPRITES EQU const_value - SPRITE_POKEMON",
        ],
    )
    _assert_contiguous(
        crystal_table,
        [
            "db HO_OH",
            "db CHIKORITA",
            "db CYNDAQUIL",
            "db TOTODILE",
            "assert_table_length NUM_POKEMON_SPRITES",
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
