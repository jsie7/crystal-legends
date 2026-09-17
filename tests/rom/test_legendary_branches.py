from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable


pytestmark = pytest.mark.rom


def _pointer(address: int) -> bytes:
    return address.to_bytes(2, "little")


def _segment(rom: RomImage, symbols: SymbolTable, start: str, end: str) -> bytes:
    first = symbols[start]
    last = symbols[end]
    assert first.bank == last.bank and first.rom_offset < last.rom_offset
    return rom.slice(first.rom_offset, last.rom_offset - first.rom_offset)


@pytest.fixture(scope="module")
def branch_contract(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/contracts/legendary_branches.json").read_text()
    )


@pytest.fixture(scope="module")
def branch_constants(
    repo_root: Path, tmp_path_factory, branch_contract: dict
) -> dict[str, int]:
    names = {
        "givepoke_command",
        "checkevent_command",
        "iftrue_command",
        "ifequal_command",
        "writetext_command",
        "loadtrainer_command",
        "loadvar_command",
        "startbattle_command",
        "reloadmap_command",
        "getmonname_command",
        "setevent_command",
        "RIVAL1",
        "VAR_BATTLETYPE",
        "BATTLETYPE_CANLOSE",
        "BERRY",
        "FALSE",
        "STRING_BUFFER_3",
        "EVENT_OAK_MOVED_THIRD_BIRD",
    }
    for branch in branch_contract["branches"]:
        names.update(
            {
                branch["player"],
                branch["choice_event"],
                branch["pokeball_event"],
                branch["rival_party"],
                branch["oak"],
            }
        )
    return resolve_constants(
        repo_root, tmp_path_factory.mktemp("legendary_rom_constants"), sorted(names)
    )


def test_compiled_starter_gifts_match_all_three_branches(
    repo_root: Path,
    branch_contract: dict,
    branch_constants: dict[str, int],
) -> None:
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    ends = {
        "CyndaquilPokeBallScript": "TotodilePokeBallScript",
        "TotodilePokeBallScript": "ChikoritaPokeBallScript",
        "ChikoritaPokeBallScript": "DidntChooseStarterScript",
    }
    for branch in branch_contract["branches"]:
        segment = _segment(
            rom, symbols, branch["starter_script"], ends[branch["starter_script"]]
        )
        expected = bytes(
            [
                branch_constants["givepoke_command"],
                branch_constants[branch["player"]],
                5,
                branch_constants["BERRY"],
                branch_constants["FALSE"],
            ]
        )
        assert segment.count(expected) == 1, branch["id"]
        delivery = segment.index(expected)
        refusal = (
            bytes([branch_constants["ifequal_command"], 2])
            + _pointer(symbols["ElmStarterStorageFullScript"].address)
        )
        assert segment[delivery + len(expected) :].startswith(refusal)
        choice = (
            bytes([branch_constants["setevent_command"]])
            + _pointer(branch_constants[branch["choice_event"]])
        )
        receipt = (
            bytes([branch_constants["writetext_command"]])
            + _pointer(symbols["ReceivedStarterText"].address)
        )
        assert delivery < segment.index(choice) < segment.index(receipt)


def test_compiled_first_silver_selector_and_can_lose_contract(
    repo_root: Path,
    branch_contract: dict,
    branch_constants: dict[str, int],
) -> None:
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    path_segments = {
        "default": (
            "CherrygroveRivalSceneNorth",
            "CherrygroveRivalSceneNorth.SecondStarter",
        ),
        "second": (
            "CherrygroveRivalSceneNorth.SecondStarter",
            "CherrygroveRivalSceneNorth.ThirdStarter",
        ),
        "third": (
            "CherrygroveRivalSceneNorth.ThirdStarter",
            "CherrygroveRivalSceneNorth.AfterVictorious",
        ),
    }
    root = _segment(
        rom,
        symbols,
        "CherrygroveRivalSceneNorth",
        "CherrygroveRivalSceneNorth.SecondStarter",
    )
    for branch in branch_contract["branches"]:
        segment = _segment(rom, symbols, *path_segments[branch["rival_path"]])
        assert segment.count(
            bytes(
                [
                    branch_constants["loadtrainer_command"],
                    branch_constants["RIVAL1"],
                    branch_constants[branch["rival_party"]],
                ]
            )
        ) == 1
        assert segment.count(
            bytes(
                [
                    branch_constants["loadvar_command"],
                    branch_constants["VAR_BATTLETYPE"],
                    branch_constants["BATTLETYPE_CANLOSE"],
                    branch_constants["startbattle_command"],
                ]
            )
        ) == 1
        assert branch_constants["reloadmap_command"] in segment

    for branch, target in zip(
        branch_contract["branches"][1:],
        (
            "CherrygroveRivalSceneNorth.SecondStarter",
            "CherrygroveRivalSceneNorth.ThirdStarter",
        ),
    ):
        expected = (
            bytes([branch_constants["checkevent_command"]])
            + _pointer(branch_constants[branch["choice_event"]])
            + bytes([branch_constants["iftrue_command"]])
            + _pointer(symbols[target].address)
        )
        assert root.count(expected) == 1


def test_compiled_oak_handoff_mapping_is_one_time(
    repo_root: Path,
    branch_contract: dict,
    branch_constants: dict[str, int],
) -> None:
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    segments = {
        "ElmArrangeThirdBirdTransferScript": _segment(
            rom,
            symbols,
            "ElmArrangeThirdBirdTransferScript",
            "ElmArrangeThirdBirdTransferScript.OakMovesZapdos",
        ),
        "ElmArrangeThirdBirdTransferScript.OakMovesZapdos": _segment(
            rom,
            symbols,
            "ElmArrangeThirdBirdTransferScript.OakMovesZapdos",
            "ElmArrangeThirdBirdTransferScript.OakMovesMoltres",
        ),
        "ElmArrangeThirdBirdTransferScript.OakMovesMoltres": _segment(
            rom,
            symbols,
            "ElmArrangeThirdBirdTransferScript.OakMovesMoltres",
            "ElmArrangeThirdBirdTransferScript.ThirdBirdBuffered",
        ),
    }
    for branch in branch_contract["branches"]:
        expected = bytes(
            [
                branch_constants["getmonname_command"],
                branch_constants[branch["oak"]],
                branch_constants["STRING_BUFFER_3"],
            ]
        )
        assert segments[branch["oak_branch"]].count(expected) == 1

    handoff = rom.slice(
        symbols["ElmArrangeThirdBirdTransferScript.ThirdBirdBuffered"].rom_offset,
        64,
    )
    for event in [
        *(branch["pokeball_event"] for branch in branch_contract["branches"]),
        "EVENT_OAK_MOVED_THIRD_BIRD",
    ]:
        expected = bytes([branch_constants["setevent_command"]]) + _pointer(
            branch_constants[event]
        )
        assert handoff.count(expected) == 1
