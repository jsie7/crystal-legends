from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from tests.support.asm_conditions import active_lines


pytestmark = pytest.mark.static


def _active_code(path: Path) -> list[str]:
    return [
        line.text.split(";", 1)[0].strip()
        for line in active_lines(path.read_text(), {"_CRYSTAL11", "_CRYSTALLEGENDS"})
        if line.text.split(";", 1)[0].strip()
    ]


def _definitions(lines: list[str]) -> dict[str, str]:
    definitions: dict[str, str] = {}
    for line in lines:
        match = re.fullmatch(r"DEF\s+(\w+)\s+EQU\s+(\w+)", line)
        if match:
            definitions[match.group(1)] = match.group(2)
    return definitions


def _assert_contiguous(lines: list[str], expected: list[str]) -> None:
    width = len(expected)
    assert any(lines[index : index + width] == expected for index in range(len(lines)))


def test_legendary_branch_source_contracts(repo_root: Path) -> None:
    contract = json.loads(
        (repo_root / "tests/contracts/legendary_branches.json").read_text()
    )
    elm = _active_code(repo_root / "maps/ElmsLab.asm")
    cherrygrove = _active_code(repo_root / "maps/CherrygroveCity.asm")
    elm_definitions = _definitions(elm)
    rival_definitions = _definitions(cherrygrove)
    rival_definition_by_path = {
        "default": "CHERRYGROVE_RIVAL_DEFAULT_PARTY",
        "second": "CHERRYGROVE_RIVAL_SECOND_PARTY",
        "third": "CHERRYGROVE_RIVAL_THIRD_PARTY",
    }

    for branch in contract["branches"]:
        slot = branch["starter_slot"]
        assert elm_definitions[f"ELMSLAB_{slot}_STARTER_SPECIES"] == branch["player"]
        assert (
            elm_definitions[f"ELMSLAB_{slot}_STARTER_CHOICE_EVENT"]
            == branch["choice_event"]
        )
        assert (
            elm_definitions[f"ELMSLAB_{slot}_STARTER_POKEBALL_EVENT"]
            == branch["pokeball_event"]
        )
        assert (
            rival_definitions[rival_definition_by_path[branch["rival_path"]]]
            == branch["rival_party"]
        )

    _assert_contiguous(
        elm,
        [
            "checkevent EVENT_GOT_ARTICUNO_FROM_ELM",
            "iftrue .OakMovesZapdos",
            "checkevent EVENT_GOT_ZAPDOS_FROM_ELM",
            "iftrue .OakMovesMoltres",
            "getmonname STRING_BUFFER_3, ARTICUNO",
            "sjump .ThirdBirdBuffered",
        ],
    )
    _assert_contiguous(
        elm,
        [
            ".OakMovesZapdos:",
            "getmonname STRING_BUFFER_3, ZAPDOS",
            "sjump .ThirdBirdBuffered",
            ".OakMovesMoltres:",
            "getmonname STRING_BUFFER_3, MOLTRES",
        ],
    )
    _assert_contiguous(
        elm,
        [
            "setevent ELMSLAB_LEFT_STARTER_POKEBALL_EVENT",
            "setevent ELMSLAB_CENTER_STARTER_POKEBALL_EVENT",
            "setevent ELMSLAB_RIGHT_STARTER_POKEBALL_EVENT",
            "setevent EVENT_OAK_MOVED_THIRD_BIRD",
            "end",
        ],
    )


def test_first_silver_source_contract_permits_both_results(repo_root: Path) -> None:
    lines = _active_code(repo_root / "maps/CherrygroveCity.asm")
    assert lines.count("loadvar VAR_BATTLETYPE, BATTLETYPE_CANLOSE") == 3
    assert lines.count("iftrue .AfterVictorious") == 3
    assert lines.count("sjump .AfterYourDefeat") == 3
    assert lines.count("setscene SCENE_CHERRYGROVECITY_NOOP") == 1
