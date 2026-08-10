from __future__ import annotations

import json
from pathlib import Path
import re

import pytest


pytestmark = pytest.mark.static


def test_cheat_mode_action_allowlist_and_quantities(repo_root: Path) -> None:
    contract = json.loads(
        (repo_root / "tests/contracts/phase_03_cheat_actions.json").read_text()
    )
    source = (repo_root / "maps/PlayersHouse2FDebug.asm").read_text()
    observed_items = re.findall(
        r"^\.([A-Za-z0-9]+):\n\s*verbosegiveitem\s+([A-Z0-9_]+),\s*(\d+)",
        source,
        flags=re.MULTILINE,
    )
    assert observed_items == [
        (row["script"], row["item"], "10") for row in contract["items"]
    ]
    observed_pokemon = re.findall(
        r"^\.([A-Za-z0-9]+):\n\s*givepoke\s+([A-Z0-9_]+),\s*(\d+)",
        source,
        flags=re.MULTILINE,
    )
    assert observed_pokemon == [
        (row["script"], row["species"], str(row["level"]))
        for row in contract["pokemon"]
    ]
    assert source.count("givemoney YOUR_MONEY, 100000") == 1
    assert len(re.findall(r'db "[A-Z\' -]+ x10@"', source)) == len(
        contract["items"]
    )


def test_cheat_mode_has_only_explicit_safe_back_and_exit_routes(
    repo_root: Path,
) -> None:
    source = (repo_root / "maps/PlayersHouse2FDebug.asm").read_text()
    expected_menu_counts = {
        "Main": 4,
        "Supplies": 6,
        "Balls": 3,
        "Healing": 6,
        "EvolutionStones": 7,
        "TradeItems": 5,
        "Pokemon": 5,
    }
    for name, count in expected_menu_counts.items():
        header = re.search(
            rf"PlayersHouse2FDebug{name}MenuHeader:.*?\.MenuData:\n"
            rf".*?\n\s*db\s+(\d+)\s*; items(?P<rows>.*?)(?=\n\n)",
            source,
            flags=re.DOTALL,
        )
        assert header is not None, name
        assert int(header.group(1)) == count
        assert len(re.findall(r'^\s*db\s+"', header.group("rows"), re.MULTILINE)) == count
    assert source.count('db "BACK@"') == 6
    assert source.count('db "EXIT@"') == 1
