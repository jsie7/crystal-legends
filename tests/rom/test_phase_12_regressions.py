from collections import defaultdict

import pytest

from tests.support.constant_resolver import assemble_bytes
from tests.support.phase_12_data import (
    expected_parties, party_assembly, party_size, trainer_contract,
)
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable
from tests.support.linker_map import parse_linker_map

pytestmark = [pytest.mark.rom, pytest.mark.phase12]


@pytest.mark.parametrize('custom', [False, True], ids=['reference', 'custom'])
def test_complete_compiled_trainer_groups_and_record_boundaries(repo_root, tmp_path, custom):
    """Check every party, including neighbors, names, formats and terminators."""
    records = expected_parties(trainer_contract(repo_root), custom)
    groups = defaultdict(list)
    for record in records.values():
        groups[record['group']].append(record)
    stem = 'crystallegends' if custom else 'pokecrystal11'
    rom = RomImage.load(repo_root / f'{stem}.gbc')
    symbols = SymbolTable.parse((repo_root / f'{stem}.sym').read_text())
    ordered = sorted(groups, key=lambda group: symbols[group].rom_offset)
    rows = []
    sizes = {}
    for group in ordered:
        parties = sorted(groups[group], key=lambda r: r['index'])
        assert [r['index'] for r in parties] == list(range(1, len(parties) + 1))
        sizes[group] = sum(party_size(r) for r in parties)
        for record in parties:
            rows.extend(party_assembly(record))
    expected = assemble_bytes(repo_root, tmp_path, rows, length=sum(sizes.values()))
    cursor = 0
    for index, group in enumerate(ordered):
        size = sizes[group]
        assert rom.at(symbols[group], size) == expected[cursor:cursor + size], group
        if index + 1 < len(ordered):
            assert symbols[group].rom_offset + size == symbols[ordered[index + 1]].rom_offset, group
        cursor += size


def test_final_trainer_bank_growth_and_reserve(repo_root):
    contract = trainer_contract(repo_root)
    assert set(contract['applied_slices']) == set('BCDEFGHIK')
    usage = parse_linker_map((repo_root / 'crystallegends.map').read_text())
    assert usage['ROMX', 14].free == 826
    assert 1078 - usage['ROMX', 14].free == contract['expected_growth'] == 252
    assert usage['ROMX', 14].free - 768 == 58
