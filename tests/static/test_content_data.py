from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

from tests.support.content_data import (
    parse_acquisition_ledger,
    parse_evolution_blocks,
    parse_trainer_parties,
    pokemon_constant_names,
    validate_wild_level_species_rows,
)


pytestmark = pytest.mark.static


@pytest.fixture(scope="module")
def pokemon_names(repo_root: Path) -> set[str]:
    return pokemon_constant_names(
        (repo_root / "constants/pokemon_constants.asm").read_text()
    )


def test_acquisition_ledger_covers_each_dex_number_once(repo_root: Path) -> None:
    rows = parse_acquisition_ledger(
        (repo_root / "docs/pokemon-acquisition.md").read_text()
    )
    assert [row.dex for row in rows] == list(range(1, 252))
    assert len({row.species for row in rows}) == 251
    assert all(
        row.method
        and row.location
        and row.earliest
        and row.availability
        and row.renewable
        and row.source
        for row in rows
    )
    assert all(
        re.fullmatch(
            r"(?:Existing|Phase \d+|Reserved Phase [\d/-]+|"
            r"Existing Phase \d+ / Reserved Phase [\d-]+)",
            row.availability,
        )
        for row in rows
    )
    for row in rows:
        for source_path in row.source_paths:
            assert (repo_root / source_path).is_file(), (
                f"Dex {row.dex:03d} {row.species} cites missing {source_path}"
            )


def test_evolution_and_learnset_tables_are_structurally_valid(
    repo_root: Path, pokemon_names: set[str]
) -> None:
    blocks = parse_evolution_blocks(
        (repo_root / "data/pokemon/evos_attacks.asm").read_text()
    )
    pointers = re.findall(
        r"^\s*dw\s+([A-Za-z0-9]+)EvosAttacks\b",
        (repo_root / "data/pokemon/evos_attacks_pointers.asm").read_text(),
        flags=re.MULTILINE,
    )
    assert len(blocks) == 251
    assert [block.species for block in blocks] == pointers
    exceptions = json.loads(
        (repo_root / "tests/contracts/content_data_exceptions.json").read_text()
    )
    allowed_unsorted = {
        record["species"] for record in exceptions["unsorted_learnsets"]
    }
    observed_unsorted: set[str] = set()
    for block in blocks:
        levels = [level for level, _move in block.learnset]
        if levels != sorted(levels):
            observed_unsorted.add(block.species)
        assert all(1 <= level <= 100 for level in levels)
        assert all(evolution.target in pokemon_names for evolution in block.evolutions)
    assert observed_unsorted == allowed_unsorted


def test_phase_2_single_player_evolution_contracts(repo_root: Path) -> None:
    blocks = {
        block.species: block
        for block in parse_evolution_blocks(
            (repo_root / "data/pokemon/evos_attacks.asm").read_text()
        )
    }
    contracts = json.loads(
        (repo_root / "tests/contracts/phase_02_evolutions.json").read_text()
    )
    for contract in contracts:
        matches = [
            evolution
            for evolution in blocks[contract["source"]].evolutions
            if evolution.method == contract["method"]
            and evolution.condition == contract["condition"]
            and evolution.target == contract["target"]
        ]
        assert len(matches) == 1, contract


def test_wild_levels_and_species_are_valid(
    repo_root: Path, pokemon_names: set[str]
) -> None:
    checked = validate_wild_level_species_rows(
        sorted((repo_root / "data/wild").glob("*.asm")), pokemon_names
    )
    assert checked > 1_000


def test_trainer_parties_have_valid_shapes_levels_and_species(
    repo_root: Path, pokemon_names: set[str]
) -> None:
    parties = parse_trainer_parties(
        (repo_root / "data/trainers/parties.asm").read_text()
    )
    widths = {
        "TRAINERTYPE_NORMAL": 2,
        "TRAINERTYPE_MOVES": 6,
        "TRAINERTYPE_ITEM": 3,
        "TRAINERTYPE_ITEM_MOVES": 7,
    }
    assert len(parties) > 500
    for party in parties:
        assert party.group
        assert 1 <= len(party.members) <= 6, f"{party.group}/{party.name}"
        for member in party.members:
            assert len(member) == widths[party.trainer_type]
            assert member[0].isdigit() and 1 <= int(member[0]) <= 100
            assert member[1] in pokemon_names


def test_legendary_rival_party_slots_match_the_existing_contract(
    repo_root: Path,
) -> None:
    parties = parse_trainer_parties(
        (repo_root / "data/trainers/parties.asm").read_text()
    )
    contracts = json.loads(
        (repo_root / "tests/contracts/legendary_rival_parties.json").read_text()
    )
    legendary_species = {"ARTICUNO", "ZAPDOS", "MOLTRES"}
    for group, records in contracts.items():
        trainer_group = f"{group.title()}Group"
        group_parties = [party for party in parties if party.group == trainer_group]
        assert len(group_parties) == len(records)
        for record in records:
            party = group_parties[record["slot"] - 1]
            legendary_members = [
                member for member in party.members if member[1] in legendary_species
            ]
            if record["legendary"] is None:
                assert legendary_members == []
            else:
                assert [(int(member[0]), member[1]) for member in legendary_members] == [
                    (record["level"], record["legendary"])
                ]
