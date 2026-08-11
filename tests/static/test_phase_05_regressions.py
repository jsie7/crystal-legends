from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.asm_conditions import active_lines


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
