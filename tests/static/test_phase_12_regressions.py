from collections import Counter

import pytest

from tests.support.phase_12_data import (
    expected_parties, natural_moves, party_key, party_size, source_parties,
    trainer_contract,
)

pytestmark = [pytest.mark.static, pytest.mark.phase12]


@pytest.mark.parametrize('custom', [False, True], ids=['reference', 'custom'])
def test_all_trainer_records_match_targets_and_preservation_baseline(repo_root, custom):
    expected = expected_parties(trainer_contract(repo_root), custom)
    actual = source_parties(repo_root, custom)
    assert actual.keys() == expected.keys()
    for key, party in actual.items():
        record = expected[key]
        assert party.name == record['name'], key
        assert party.trainer_type == record['trainer_type'], key
        assert [list(row) for row in party.members] == record['members'], key


def test_approved_scope_and_exact_serialized_growth(repo_root):
    contract = trainer_contract(repo_root)
    targets = contract['targets']
    assert len(targets) == len({party_key(r) for r in targets}) == 166
    assert Counter(r['category'] for r in targets) == {'named': 73, 'ordinary': 93}
    baseline_contract = {**contract, 'applied_slices': []}
    baseline = expected_parties(baseline_contract)
    assert sum(party_size(r) - party_size(baseline[party_key(r)]) for r in targets) == 252
    assert sum(len(r['members']) - len(baseline[party_key(r)]['members']) for r in targets) == 44
    conversions = [party_key(r) for r in targets
                   if r['trainer_type'] != baseline[party_key(r)]['trainer_type']]
    assert set(conversions) == {('BlackbeltGroup', 6), ('TeacherGroup', 1)}


def test_every_accepted_automatic_moveset_matches_fillmoves(repo_root):
    for record in trainer_contract(repo_root)['targets']:
        if record['trainer_type'] not in ('TRAINERTYPE_NORMAL', 'TRAINERTYPE_ITEM'):
            continue
        for row, moves in zip(record['members'], record['moves'], strict=True):
            assert natural_moves(repo_root, row[1], int(row[0])) == moves, (party_key(record), row)
