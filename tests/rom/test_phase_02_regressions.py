from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable


pytestmark = pytest.mark.rom


@pytest.fixture(scope="module")
def phase_2_contracts(repo_root: Path) -> tuple[list[dict], dict]:
    return (
        json.loads(
            (repo_root / "tests/contracts/phase_02_evolutions.json").read_text()
        ),
        json.loads((repo_root / "tests/contracts/phase_02_items.json").read_text()),
    )


@pytest.fixture(scope="module")
def phase_2_constants(
    repo_root: Path, tmp_path_factory, phase_2_contracts: tuple[list[dict], dict]
) -> dict[str, int]:
    evolutions, items = phase_2_contracts
    names = {
        "EVOLVE_LEVEL",
        "EVOLVE_ITEM",
        "ITEMATTR_STRUCT_LENGTH",
        "ITEMMENU_PARTY",
        "ITEMMENU_NOUSE",
        "CANT_SELECT",
        "ITEM",
        "WATER_STONE",
        "POLIWRATH",
        "SLOWBRO",
    }
    for row in evolutions:
        names.update((row["condition"], row["target"]))
    for row in items["items"]:
        names.update((row["item"], row["held_effect"]))
    names.update(items["mart"]["items"])
    return resolve_constants(
        repo_root, tmp_path_factory.mktemp("phase_2_rom_constants"), sorted(names)
    )


def _decode_evolutions(
    rom: RomImage, symbols: SymbolTable, constants: dict[str, int], source: str
) -> list[tuple[int, int, int]]:
    offset = symbols[f"{source}EvosAttacks"].rom_offset
    rows: list[tuple[int, int, int]] = []
    while rom.u8(offset):
        method = rom.u8(offset)
        width = 4 if method == 5 else 3
        record = tuple(rom.slice(offset, width))
        rows.append((record[0], record[1], record[-1]))
        offset += width
    return rows


def test_compiled_phase_2_evolution_matrix_and_alternates(
    repo_root: Path,
    phase_2_contracts: tuple[list[dict], dict],
    phase_2_constants: dict[str, int],
) -> None:
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    evolutions, _items = phase_2_contracts
    observed: dict[str, list[tuple[int, int, int]]] = {}
    for row in evolutions:
        observed.setdefault(
            row["source"],
            _decode_evolutions(rom, symbols, phase_2_constants, row["source"]),
        )
        expected = (
            phase_2_constants[row["method"]],
            int(row["condition"])
            if row["condition"].isdigit()
            else phase_2_constants[row["condition"]],
            phase_2_constants[row["target"]],
        )
        assert expected in observed[row["source"]], row

    assert (
        phase_2_constants["EVOLVE_ITEM"],
        phase_2_constants["WATER_STONE"],
        phase_2_constants["POLIWRATH"],
    ) in observed["Poliwhirl"]
    assert (
        phase_2_constants["EVOLVE_LEVEL"],
        37,
        phase_2_constants["SLOWBRO"],
    ) in observed["Slowpoke"]


def test_compiled_phase_2_item_attributes_effects_and_mart(
    repo_root: Path,
    phase_2_contracts: tuple[list[dict], dict],
    phase_2_constants: dict[str, int],
) -> None:
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    _evolutions, contract = phase_2_contracts
    attributes = symbols["ItemAttributes"].rom_offset
    effects = symbols["ItemEffects"].rom_offset
    width = phase_2_constants["ITEMATTR_STRUCT_LENGTH"]
    for row in contract["items"]:
        item = phase_2_constants[row["item"]]
        attribute = rom.slice(attributes + (item - 1) * width, width)
        assert int.from_bytes(attribute[:2], "little") == row["price"]
        assert attribute[2] == phase_2_constants[row["held_effect"]]
        assert attribute[3] == row["held_parameter"]
        assert attribute[4] == phase_2_constants["CANT_SELECT"]
        assert attribute[5] == phase_2_constants["ITEM"]
        assert attribute[6] >> 4 == phase_2_constants["ITEMMENU_PARTY"]
        assert attribute[6] & 0xF == phase_2_constants["ITEMMENU_NOUSE"]
        assert rom.u16le(effects + (item - 1) * 2) == symbols[
            "EvoStoneEffect"
        ].address

    mart_items = contract["mart"]["items"]
    mart = symbols[contract["mart"]["label"]].rom_offset
    assert rom.u8(mart) == len(mart_items)
    assert rom.slice(mart + 1, len(mart_items)) == bytes(
        phase_2_constants[item] for item in mart_items
    )
    assert rom.u8(mart + 1 + len(mart_items)) == 0xFF
