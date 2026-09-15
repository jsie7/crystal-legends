from hashlib import sha256

import pytest

from tests.support.phase_12_data import natural_moves
from tests.support.phase_12_wild import parse_wild_records, target_records, wild_contract

pytestmark = [pytest.mark.static, pytest.mark.phase12]


@pytest.mark.parametrize('custom', [False, True], ids=['reference', 'custom'])
def test_complete_kanto_wild_tables_and_preserved_records(repo_root, custom):
    for table in wild_contract(repo_root)['tables']:
        expected = target_records(table) if custom else table['baseline_reference']
        assert parse_wild_records((repo_root / table['path']).read_text(), custom) == expected


def test_only_the_584_approved_level_bytes_change(repo_root):
    totals = []
    changed_records = []
    for table in wild_contract(repo_root)['tables']:
        changed = 0
        for old, new in zip(table['baseline_custom'], target_records(table), strict=True):
            assert old['map'] == new['map']
            assert old['rates'] == new['rates']
            assert [s[1] for s in old['slots']] == [s[1] for s in new['slots']]
            changed += sum(a[0] != b[0] for a, b in zip(old['slots'], new['slots'], strict=True))
        totals.append(changed)
        changed_records.append(len(table['targets']))
    assert totals == [545, 39]
    assert sum(totals) == wild_contract(repo_root)['changed_level_bytes'] == 584
    assert changed_records == [26, 13]


def test_other_habitats_mechanics_and_class_settings_remain_exact(repo_root):
    for record in wild_contract(repo_root)['preserved_files']:
        assert sha256((repo_root / record['path']).read_bytes()).hexdigest() == record['sha256'], record['path']


@pytest.mark.parametrize('species,level,moves', [
    ('HOUNDOUR', 26, ['EMBER', 'ROAR', 'SMOG', 'BITE']),
    ('VULPIX', 34, ['ROAR', 'CONFUSE_RAY', 'SAFEGUARD', 'FLAMETHROWER']),
    ('ABRA', 28, ['TELEPORT', 'NO_MOVE', 'NO_MOVE', 'NO_MOVE']),
])
def test_recruitment_natural_moves(repo_root, species, level, moves):
    assert natural_moves(repo_root, species, level) == moves


@pytest.mark.parametrize('species,level', [('GEODUDE', 25), ('GEODUDE', 26), ('GEODUDE', 28), ('VOLTORB', 29)])
def test_accepted_explosive_wild_sets_keep_selfdestruct(repo_root, species, level):
    assert 'SELFDESTRUCT' in natural_moves(repo_root, species, level)
