from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase10]


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_10_giovanni_cerulean_cave.json").read_text()
    )


@pytest.fixture(scope="module")
def phase_10_constants(repo_root: Path, tmp_path_factory, scenario: dict) -> dict[str, int]:
    names = [name for group in scenario["events"].values() for name, _ in group]
    names.extend(["NUM_EVENTS", "GROUP_CERULEAN_CAVE", "MAP_CERULEAN_CAVE"])
    return resolve_constants(repo_root, tmp_path_factory.mktemp("phase_10_constants"), names)


def test_compiled_phase_10_ids_use_the_reviewed_gaps_without_save_growth(
    repo_root: Path, scenario: dict, phase_10_constants: dict[str, int]
) -> None:
    for group in scenario["events"].values():
        for name, expected in group:
            assert phase_10_constants[name] == expected
    assert phase_10_constants["NUM_EVENTS"] == 2048
    assert phase_10_constants["GROUP_CERULEAN_CAVE"] == 7
    assert phase_10_constants["MAP_CERULEAN_CAVE"] == 19

    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    assert symbols["wCurBox"].address - symbols["wEventFlags"].address == 256


def test_compiled_cave_replaces_only_the_unreferenced_beta_payload(
    repo_root: Path, scenario: dict
) -> None:
    custom = RomImage.load(repo_root / scenario["rom"])
    custom_symbols = SymbolTable.parse((repo_root / scenario["symbols"]).read_text())
    cave = (repo_root / scenario["map"]["block_path"]).read_bytes()
    assert custom.at(custom_symbols["CeruleanCave_Blocks"], len(cave)) == cave

    reference = RomImage.load(repo_root / scenario["reference_rom"])
    reference_symbols = SymbolTable.parse(
        (repo_root / scenario["reference_symbols"]).read_text()
    )
    beta = (repo_root / "maps/unused/BetaCaveTestMap.blk").read_bytes()
    assert reference.at(reference_symbols["BetaCaveTestMap_Blocks"], len(beta)) == beta


def test_compiled_cave_attributes_match_the_registered_map(
    repo_root: Path, scenario: dict
) -> None:
    rom = RomImage.load(repo_root / scenario["rom"])
    symbols = SymbolTable.parse((repo_root / scenario["symbols"]).read_text())
    attributes = rom.at(symbols["CeruleanCave_MapAttributes"], 8)
    assert attributes[:3] == bytes([scenario["map"]["border_block"], 18, 15])
    assert attributes[3] == symbols["CeruleanCave_Blocks"].bank
    assert int.from_bytes(attributes[4:6], "little") == symbols["CeruleanCave_Blocks"].address
