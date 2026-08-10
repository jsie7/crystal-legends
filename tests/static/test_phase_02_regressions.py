from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from tests.support.asm_conditions import active_lines
from tests.support.content_data import parse_evolution_blocks


pytestmark = pytest.mark.static


def _active_text(path: Path, defines: set[str]) -> str:
    return "\n".join(line.text for line in active_lines(path.read_text(), defines))


def _item_attribute(text: str, item: str) -> tuple[str, ...]:
    match = re.search(
        rf"^; {item}\n\s*item_attribute\s+([^\n]+)$",
        text,
        flags=re.MULTILINE,
    )
    assert match is not None, item
    return tuple(value.strip() for value in match.group(1).split(","))


def test_phase_2_evolution_matrix_and_stock_fallback(repo_root: Path) -> None:
    source = repo_root / "data/pokemon/evos_attacks.asm"
    contracts = json.loads(
        (repo_root / "tests/contracts/phase_02_evolutions.json").read_text()
    )
    crystal = {
        block.species: block
        for block in parse_evolution_blocks(source.read_text())
    }
    stock = {
        block.species: block
        for block in parse_evolution_blocks(
            _active_text(source, {"_CRYSTAL11"})
        )
    }
    for contract in contracts:
        expected = (
            contract["method"],
            contract["condition"],
            contract["target"],
        )
        observed = {
            (evolution.method, evolution.condition, evolution.target)
            for evolution in crystal[contract["source"]].evolutions
        }
        assert expected in observed, contract

        stock_expected = (
            "EVOLVE_TRADE",
            "-1" if contract["method"] == "EVOLVE_LEVEL" else contract["condition"],
            contract["target"],
        )
        stock_observed = {
            (evolution.method, evolution.condition, evolution.target)
            for evolution in stock[contract["source"]].evolutions
        }
        assert stock_expected in stock_observed, contract

    assert {
        (evolution.method, evolution.condition, evolution.target)
        for evolution in crystal["Poliwhirl"].evolutions
    } == {
        ("EVOLVE_ITEM", "WATER_STONE", "POLIWRATH"),
        ("EVOLVE_ITEM", "KINGS_ROCK", "POLITOED"),
    }
    assert {
        (evolution.method, evolution.condition, evolution.target)
        for evolution in crystal["Slowpoke"].evolutions
    } == {
        ("EVOLVE_LEVEL", "37", "SLOWBRO"),
        ("EVOLVE_ITEM", "KINGS_ROCK", "SLOWKING"),
    }


def test_phase_2_item_effect_attribute_and_mart_contracts(repo_root: Path) -> None:
    contract = json.loads(
        (repo_root / "tests/contracts/phase_02_items.json").read_text()
    )
    attributes = _active_text(
        repo_root / "data/items/attributes.asm",
        {"_CRYSTAL11", "_CRYSTALLEGENDS"},
    )
    effects = _active_text(
        repo_root / "engine/items/item_effects.asm",
        {"_CRYSTAL11", "_CRYSTALLEGENDS"},
    )
    marts = _active_text(
        repo_root / "data/items/marts.asm",
        {"_CRYSTAL11", "_CRYSTALLEGENDS"},
    )
    for item in contract["items"]:
        assert re.search(
            rf"^\s*dw EvoStoneEffect\s+; {item['item']}$",
            effects,
            flags=re.MULTILINE,
        )
        values = _item_attribute(attributes, item["item"])
        assert values == (
            str(item["price"]),
            item["held_effect"],
            str(item["held_parameter"]),
            "CANT_SELECT",
            "ITEM",
            "ITEMMENU_PARTY",
            "ITEMMENU_NOUSE",
        )

    mart = re.search(
        rf"^{contract['mart']['label']}:\n(?P<body>.*?)(?=^\S.*:$)",
        marts,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert mart is not None
    rows = [
        row.strip()
        for row in re.findall(
            r"^\s*db\s+([^;\n]+)", mart.group("body"), re.MULTILINE
        )
    ]
    assert rows == [
        str(len(contract["mart"]["items"])),
        *contract["mart"]["items"],
        "-1",
    ]


def test_phase_2_celebi_source_state_machine_is_retry_safe(repo_root: Path) -> None:
    goldenrod = _active_text(
        repo_root / "maps/GoldenrodPokecenter1F.asm",
        {"_CRYSTAL11", "_CRYSTALLEGENDS"},
    )
    for side in ("Left", "Right"):
        end_label = (
            "GoldenrodPokecenter1F_GSBallSceneRight:"
            if side == "Left"
            else "GoldenrodPokecenter1FGameboyKidScript:"
        )
        segment = goldenrod.split(
            f"GoldenrodPokecenter1F_GSBallScene{side}:", 1
        )[1].split(end_label, 1)[0]
        assert "checkevent EVENT_BEAT_ELITE_FOUR" in segment
        assert "checkevent EVENT_GOT_GS_BALL_FROM_GOLDENROD_POKEMON_CENTER" in segment
        assert "verbosegiveitem GS_BALL\n\tiffalse .no_room" in segment
        assert segment.index("verbosegiveitem GS_BALL") < segment.index(
            "setevent EVENT_GOT_GS_BALL_FROM_GOLDENROD_POKEMON_CENTER"
        )
        assert "setevent EVENT_CAN_GIVE_GS_BALL_TO_KURT" in segment

    kurt = _active_text(
        repo_root / "maps/KurtsHouse.asm", {"_CRYSTAL11", "_CRYSTALLEGENDS"}
    )
    handoff = kurt.split(".CanGiveGSBallToKurt:", 1)[1].split(
        ".GaveGSBallToKurt:", 1
    )[0]
    assert "checkitem GS_BALL" in handoff
    assert "setevent EVENT_GAVE_GS_BALL_TO_KURT" in handoff
    assert "takeitem GS_BALL" in handoff
    assert "setflag ENGINE_KURT_MAKING_BALLS" in handoff
    waiting = kurt.split(".GaveGSBallToKurt:", 1)[1].split("Kurt2:", 1)[0]
    assert "checkflag ENGINE_KURT_MAKING_BALLS" in waiting
    assert "setevent EVENT_FOREST_IS_RESTLESS" in waiting
    assert "clearevent EVENT_CAN_GIVE_GS_BALL_TO_KURT" in waiting
    assert "clearevent EVENT_GAVE_GS_BALL_TO_KURT" in waiting

    ilex = _active_text(
        repo_root / "maps/IlexForest.asm", {"_CRYSTAL11", "_CRYSTALLEGENDS"}
    )
    shrine = ilex.split("IlexForestShrineScript:", 1)[1].split(
        "MovementData_Farfetchd_Pos1_Pos2:", 1
    )[0]
    assert "checkevent EVENT_FOREST_IS_RESTLESS" in shrine
    assert "checkitem GS_BALL" in shrine
    assert "loadwildmon CELEBI, 30" in shrine
    assert "special CheckCaughtCelebi\n\tiffalse .DidntCatchCelebi" in shrine
    retry = shrine.split(".DidntCatchCelebi:", 1)[1]
    assert "giveitem GS_BALL" in retry
    assert "setevent EVENT_FOREST_IS_RESTLESS" in retry
    assert "setflag ENGINE_FOREST_IS_RESTLESS" in retry
