from collections import Counter
import re

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


def _experience_function(root):
    base_exp = {}
    for path in (root / 'data/pokemon/base_stats').glob('*.asm'):
        text = path.read_text()
        species = re.search(r'\bdb\s+([A-Z][A-Z0-9_]*)', text).group(1)
        base_exp[species] = int(re.search(r'\bdb\s+(\d+)\s*; base exp', text).group(1))

    def experience(record):
        # One original-OT participant, trainer bonus, no Lucky Egg.
        # Gen II truncates division by seven before applying the 1.5x bonus.
        return sum((base_exp[row[1]] * int(row[0]) // 7) * 3 // 2 for row in record['members'])
    return experience


def test_johto_subtotal_matches_approved_experience_and_capacity(repo_root):
    contract = trainer_contract(repo_root)
    xp = _experience_function(repo_root)
    reference = expected_parties(contract, False)
    johto = [r for r in contract['targets'] if r['slice'] in 'BCDE']
    assert len(johto) == 31
    assert sum(xp(reference[party_key(r)]) for r in johto) == 91030
    assert sum(xp(r) for r in johto) == 111497
    assert sum(party_size(r) - party_size(reference[party_key(r)]) for r in johto) == 132


@pytest.mark.parametrize('starter,stock_xp,accepted_xp', [
    ('Articuno', 397101, 577396), ('Zapdos', 397042, 577300), ('Moltres', 396628, 577375),
])
def test_combined_branch_selected_battles_and_experience(repo_root, starter, stock_xp, accepted_xp):
    contract = trainer_contract(repo_root)
    targets = {party_key(r): r for r in contract['targets']}
    reference = expected_parties(contract, False)
    named = [r for r in targets.values() if r['category'] == 'named'
             and ('player chose' not in r['title'] or r['title'].endswith(starter))]
    ordinary = [targets[party_key(r)] for r in contract['ordinary_battles']]
    assert len(named) == 57
    assert len(ordinary) == 92
    assert sum(len(r['members']) for r in ordinary) == 205
    selected = named + ordinary
    assert len({party_key(r) for r in selected}) == 149
    xp = _experience_function(repo_root)
    assert sum(xp(r) for r in selected) == accepted_xp
    assert sum(xp(reference[party_key(r)]) for r in selected if party_key(r) in reference) == stock_xp
    assert sum(xp(r) for r in ordinary) == 236498
    assert sum(xp(reference[party_key(r)]) for r in ordinary) == 187154


def test_ordinary_kanto_policy_caps_formats_and_duplicate_battle(repo_root):
    contract = trainer_contract(repo_root)
    reference = expected_parties(contract, False)
    targets = {party_key(r): r for r in contract['targets'] if r['category'] == 'ordinary'}
    policies = {party_key(r): r for r in contract['ordinary_battles']}
    assert set(targets) - set(policies) == {('TwinsGroup', 6)}
    policies['TwinsGroup', 6] = policies['TwinsGroup', 5]
    reduced_increments = 0
    for key, record in targets.items():
        policy = policies[key]
        old = reference[key]
        assert record['trainer_type'] == ('TRAINERTYPE_MOVES' if key == ('TeacherGroup', 1)
                                          else old['trainer_type'])
        assert len(record['members']) == len(old['members'])
        for previous, current in zip(old['members'], record['members'], strict=True):
            assert previous[1] == current[1]
            assert int(current[0]) == min(int(previous[0]) + policy['increment'], policy['cap'])
            if old['trainer_type'] == 'TRAINERTYPE_ITEM':
                assert current[2] == previous[2]
            reduced_increments += int(current[0]) - int(previous[0]) < policy['increment']
    assert reduced_increments == 4
    assert targets['TwinsGroup', 5]['members'] == list(reversed(targets['TwinsGroup', 6]['members']))
