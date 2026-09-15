"""Production-script checks; prepared parties prove behavior, not difficulty."""
import pytest

from tests.support.bedroom_scenario import event_is_set, wait_for_idle
from tests.support.constant_resolver import resolve_constants
from tests.support.legendary_scenario import advance_with_a_until, place_player, prepare_battle_party
from tests.support.phase_09_scenario import loaded_phase_9_map_checkpoint
from tests.support.phase_12_data import trainer_contract

pytestmark = [pytest.mark.emulator, pytest.mark.phase12]
SCENARIO = {'rom': 'crystallegends.gbc', 'symbols': 'crystallegends.sym',
            'max_frames_per_step': 60000}
CASES = [
    ('FalknerGroup', 1, 'VIOLET_GYM', 5, 2, 'FALKNER', 'EVENT_GOT_TM31_MUD_SLAP'),
    ('JasmineGroup', 1, 'OLIVINE_GYM', 5, 4, 'JASMINE', 'EVENT_GOT_TM23_IRON_TAIL'),
    ('ClairGroup', 1, 'BLACKTHORN_GYM_1F', 5, 4, 'CLAIR', 'EVENT_BEAT_CLAIR'),
]


@pytest.fixture(scope='module')
def runtime_constants(repo_root, tmp_path_factory):
    names = {'SPAWN_N_A', 'MAPSETUP_WARP', 'OW_UP', 'OW_DOWN', 'ARTICUNO',
             'PARTYMON_STRUCT_LENGTH', 'MON_SPECIES', 'MON_MOVES', 'MON_PP',
             'MON_LEVEL', 'MON_HP', 'MON_MAXHP', 'MON_ATK', 'MON_DEF', 'MON_SPD',
             'MON_SAT', 'MON_SDF', 'TACKLE', 'SURF', 'MON_ITEM',
             'EVENT_OLIVINE_GYM_JASMINE'}
    for group, index, map_name, x, y, trainer_class, event in CASES:
        names.update((f'GROUP_{map_name}', f'MAP_{map_name}', trainer_class, event))
        record = next(r for r in trainer_contract(repo_root)['targets']
                      if (r['group'], r['index']) == (group, index))
        for row, moves in zip(record['members'], record['moves'], strict=True):
            names.add(row[1])
            names.update(moves)
    return resolve_constants(repo_root, tmp_path_factory.mktemp('phase12-runtime'), sorted(names))


@pytest.mark.parametrize('case', CASES, ids=[c[0] for c in CASES])
def test_normal_trainer_script_loads_exact_party_and_completes(
    repo_root, tmp_path, runtime_constants, case,
):
    group, index, map_name, x, y, trainer_class, completion = case
    constants = runtime_constants
    record = next(r for r in trainer_contract(repo_root)['targets']
                  if (r['group'], r['index']) == (group, index))
    events = {'EVENT_OLIVINE_GYM_JASMINE': False} if group == 'JasmineGroup' else {}
    with loaded_phase_9_map_checkpoint(repo_root, tmp_path, constants, SCENARIO,
                                      map_name=map_name, x=x, y=y, events=events) as session:
        prepare_battle_party(session, constants, constants['ARTICUNO'], True)
        session.write_symbol('wPartyMon1Moves', constants['SURF'])
        session.write_symbol('wPartyMon1PP', 63)
        place_player(session, x, y)
        session.write_symbol('wPlayerDirection', constants['OW_UP'])
        captured = []

        def capture(current):
            count = current.read_symbol('wOTPartyCount')
            captured.append([
                (current.read_symbol(f'wOTPartyMon{i}Species'),
                 current.read_symbol(f'wOTPartyMon{i}Level'),
                 list(current.read_symbol_bytes(f'wOTPartyMon{i}Moves', 4)))
                for i in range(1, count + 1)
            ])

        session.register_hook('ReadTrainerParty.done', capture)
        session.tap('a', 2, 10)
        advance_with_a_until(session, lambda current: bool(captured), 60000,
                            f'{group} normal party load')
        assert session.read_symbol('wOtherTrainerClass') == constants[trainer_class]
        assert session.read_symbol('wOtherTrainerID') == index
        assert captured == [[(constants[row[1]], int(row[0]), [constants[m] for m in moves])
                             for row, moves in zip(record['members'], record['moves'], strict=True)]]
        # Force only battle outcomes after validating the unmodified loaded party.
        # This exercises production victory/reward scripts, not battle balance.
        session.register_hook('HasEnemyFainted',
                              lambda current: current.write_symbol_bytes('wEnemyMonHP', b'\0\0'))
        session.write_symbol('wBattleMenuCursorPosition', 1)
        advance_with_a_until(session, lambda current: event_is_set(current, constants[completion]),
                            60000, f'{group} victory and reward')
        advance_with_a_until(session, lambda current: current.read_symbol('wScriptMode') == 0,
                            60000, f'{group} script completion')
        wait_for_idle(session, 60000)
        assert session.read_symbol('wBattleMode') == 0
