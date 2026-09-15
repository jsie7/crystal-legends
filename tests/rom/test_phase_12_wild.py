import pytest

from tests.support.constant_resolver import assemble_bytes
from tests.support.phase_12_wild import record_assembly, record_size, target_records, wild_contract
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable

pytestmark = [pytest.mark.rom, pytest.mark.phase12]


@pytest.mark.parametrize('custom', [False, True], ids=['reference', 'custom'])
def test_compiled_complete_encounter_tables_and_each_slot(repo_root, tmp_path, custom):
    stem = 'crystallegends' if custom else 'pokecrystal11'
    rom = RomImage.load(repo_root / f'{stem}.gbc')
    symbols = SymbolTable.parse((repo_root / f'{stem}.sym').read_text())
    for table in wild_contract(repo_root)['tables']:
        records = target_records(table) if custom else table['baseline_reference']
        lines = [line for record in records for line in record_assembly(record)] + ['db -1']
        size = sum(record_size(r) for r in records) + 1
        expected = assemble_bytes(repo_root, tmp_path / table['kind'], lines, length=size)
        assert rom.at(symbols[table['label']], size) == expected, table['label']
        offset = 0
        for record in records:
            label = f'{table["label"]}._def_{table["kind"]}_wildmons_{record["map"]}'
            assert symbols[label].rom_offset == symbols[table['label']].rom_offset + offset
            offset += record_size(record)
        if custom:
            baseline = [line for record in table['baseline_custom'] for line in record_assembly(record)] + ['db -1']
            assert sum(record_size(r) for r in table['baseline_custom']) + 1 == size
            original = assemble_bytes(repo_root, tmp_path / f'old-{table["kind"]}', baseline, length=size)
            assert sum(a != b for a, b in zip(expected, original, strict=True)) == (545 if table['kind'] == 'grass' else 39)
