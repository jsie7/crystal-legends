"""Kanto table records, including exact rates and ordered level/species slots."""
import json
import re
from pathlib import Path

from tests.support.asm_conditions import active_lines


def wild_contract(root: Path) -> dict:
    return json.loads((root / 'tests/contracts/phase_12_wild.json').read_text())


def parse_wild_records(text: str, custom: bool = True) -> list[dict]:
    definitions = {'_CRYSTAL11'} | ({'_CRYSTALLEGENDS'} if custom else set())
    records = []
    current = None
    for line in active_lines(text, definitions):
        code = line.text.split(';', 1)[0].strip()
        match = re.fullmatch(r'def_(grass|water)_wildmons (\w+)', code)
        if match:
            assert current is None
            current = {'map': match[2], 'kind': match[1], 'rates': [], 'slots': []}
        elif code.startswith('end_') and code.endswith('_wildmons'):
            assert current is not None
            assert len(current['slots']) == (21 if current['kind'] == 'grass' else 3)
            records.append(current)
            current = None
        elif current is not None and code.startswith('db '):
            values = [v.strip() for v in code[3:].split(',')]
            if not current['rates']:
                current['rates'] = values
            else:
                current['slots'].append([int(values[0]), values[1]])
    assert current is None
    return records


def target_records(table: dict) -> list[dict]:
    levels = {r['map']: r['levels'] for r in table['targets']}
    return [{**r, 'slots': [[level, slot[1]] for level, slot in zip(
        levels.get(r['map'], [s[0] for s in r['slots']]), r['slots'], strict=True)]}
        for r in table['baseline_custom']]


def record_assembly(record: dict) -> list[str]:
    return [f'map_id {record["map"]}', 'db ' + ', '.join(record['rates'])] + [
        f'db {level}, {species}' for level, species in record['slots']]


def record_size(record: dict) -> int:
    return 2 + len(record['rates']) + 2 * len(record['slots'])
