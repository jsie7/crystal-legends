from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable


pytestmark = pytest.mark.rom


@pytest.fixture(scope="module")
def cheat_contract(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/contracts/phase_03_cheat_actions.json").read_text()
    )


@pytest.fixture(scope="module")
def cheat_constants(repo_root: Path, tmp_path_factory, cheat_contract: dict) -> dict[str, int]:
    names = {
        "verbosegiveitem_command",
        "givepoke_command",
        "givemoney_command",
        "YOUR_MONEY",
        "NO_ITEM",
        "FALSE",
    }
    names.update(row["item"] for row in cheat_contract["items"])
    names.update(row["species"] for row in cheat_contract["pokemon"])
    return resolve_constants(
        repo_root, tmp_path_factory.mktemp("cheat_rom_constants"), sorted(names)
    )


def test_compiled_cheat_mode_contains_exact_action_allowlist(
    repo_root: Path, cheat_contract: dict, cheat_constants: dict[str, int]
) -> None:
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    start = symbols["PlayersHouse2FDebugTVScript"].rom_offset
    end = symbols["PlayersHouse2FDebugMainMenuHeader"].rom_offset
    script = rom.slice(start, end - start)
    for row in cheat_contract["items"]:
        pattern = bytes(
            [
                cheat_constants["verbosegiveitem_command"],
                cheat_constants[row["item"]],
                10,
            ]
        )
        assert script.count(pattern) == 1, row
    for row in cheat_contract["pokemon"]:
        pattern = bytes(
            [
                cheat_constants["givepoke_command"],
                cheat_constants[row["species"]],
                row["level"],
                cheat_constants["NO_ITEM"],
                cheat_constants["FALSE"],
            ]
        )
        assert script.count(pattern) == 1, row
    money = bytes(
        [
            cheat_constants["givemoney_command"],
            cheat_constants["YOUR_MONEY"],
            *cheat_contract["money"]["amount"].to_bytes(3, "big"),
        ]
    )
    assert script.count(money) == 1


def test_compiled_cheat_menu_rows_match_the_contract(repo_root: Path) -> None:
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    expected = {
        "PlayersHouse2FDebugMainMenuHeader.MenuData": 4,
        "PlayersHouse2FDebugSuppliesMenuHeader.MenuData": 6,
        "PlayersHouse2FDebugBallsMenuHeader.MenuData": 3,
        "PlayersHouse2FDebugHealingMenuHeader.MenuData": 6,
        "PlayersHouse2FDebugEvolutionStonesMenuHeader.MenuData": 7,
        "PlayersHouse2FDebugTradeItemsMenuHeader.MenuData": 5,
        "PlayersHouse2FDebugPokemonMenuHeader.MenuData": 5,
    }
    for label, count in expected.items():
        data = symbols[label].rom_offset
        assert rom.u8(data + 1) == count
