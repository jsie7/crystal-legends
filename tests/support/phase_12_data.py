"""Frozen balance targets and complete trainer serialization checks."""
from collections import Counter
from functools import lru_cache
import json
from pathlib import Path

from tests.support.asm_conditions import active_lines
from tests.support.content_data import parse_evolution_blocks, parse_trainer_parties


def trainer_contract(root: Path) -> dict:
    return json.loads((root / 'tests/contracts/phase_12_trainers.json').read_text())


def party_key(record: dict) -> tuple[str, int]:
    return record['group'], record['index']


def expected_parties(contract: dict, custom: bool = True) -> dict:
    records = {party_key(r): r for r in contract['baseline_reference']}
    if custom:
        records.update((party_key(r), r) for r in contract['baseline_custom_overrides'])
        records.update((party_key(r), r) for r in contract['targets']
                       if r['slice'] in contract['applied_slices'])
    return records


def source_parties(root: Path, custom: bool = True) -> dict:
    definitions = {'_CRYSTAL11'} | ({'_CRYSTALLEGENDS'} if custom else set())
    text = '\n'.join(line.text for line in active_lines(
        (root / 'data/trainers/parties.asm').read_text(), definitions))
    counters = Counter()
    result = {}
    for party in parse_trainer_parties(text):
        counters[party.group] += 1
        result[party.group, counters[party.group]] = party
    return result


def party_assembly(record: dict) -> list[str]:
    return [f'db "{record["name"]}@", {record["trainer_type"]}'] + [
        'db ' + ', '.join(row) for row in record['members']
    ] + ['db -1']


def party_size(record: dict) -> int:
    # Trainer names in these records use one-byte characters, including '#'.
    return len(record['name']) + 3 + sum(len(row) for row in record['members'])


@lru_cache(maxsize=None)
def learnsets(root: Path) -> dict:
    return {block.species.upper(): block.learnset for block in parse_evolution_blocks(
        (root / 'data/pokemon/evos_attacks.asm').read_text())}


def natural_moves(root: Path, species: str, level: int) -> list[str]:
    moves = []
    for learned_level, move in learnsets(root)[species.replace('_', '')]:
        # FillMoves exits at the first higher-level entry, even in unsorted data.
        if learned_level > level:
            break
        if move not in moves:
            moves = (moves + [move])[-4:]
    return moves + ['NO_MOVE'] * (4 - len(moves))
