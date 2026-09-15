"""Production-script checks; prepared parties prove behavior, not difficulty."""
import pytest

from tests.support.bedroom_scenario import event_is_set, wait_for_idle
from tests.support.constant_resolver import resolve_constants
from tests.support.legendary_scenario import advance_with_a_until, place_player, prepare_battle_party, walk_steps
from tests.support.phase_09_scenario import loaded_phase_9_map_checkpoint
from tests.support.phase_12_data import trainer_contract

pytestmark = [pytest.mark.emulator, pytest.mark.phase12]
SCENARIO = {'rom': 'crystallegends.gbc', 'symbols': 'crystallegends.sym',
            'max_frames_per_step': 60000}
CASES = [
    ('FalknerGroup', 1, 'VIOLET_GYM', 5, 2, 'FALKNER', 'EVENT_GOT_TM31_MUD_SLAP'),
    ('JasmineGroup', 1, 'OLIVINE_GYM', 5, 4, 'JASMINE', 'EVENT_GOT_TM23_IRON_TAIL'),
    ('ClairGroup', 1, 'BLACKTHORN_GYM_1F', 5, 4, 'CLAIR', 'EVENT_BEAT_CLAIR'),
    ('WillGroup', 1, 'WILLS_ROOM', 5, 8, 'WILL', 'EVENT_WILLS_ROOM_EXIT_OPEN'),
    ('KogaGroup', 1, 'KOGAS_ROOM', 5, 8, 'KOGA', 'EVENT_KOGAS_ROOM_EXIT_OPEN'),
    ('BrunoGroup', 1, 'BRUNOS_ROOM', 5, 8, 'BRUNO', 'EVENT_BRUNOS_ROOM_EXIT_OPEN'),
    ('KarenGroup', 1, 'KARENS_ROOM', 5, 8, 'KAREN', 'EVENT_KARENS_ROOM_EXIT_OPEN'),
    ('GruntMGroup', 1, 'SLOWPOKE_WELL_B1F', 5, 3, 'GRUNTM', 'EVENT_BEAT_ROCKET_GRUNTM_1'),
    ('ExecutiveMGroup', 2, 'RADIO_TOWER_4F', 14, 2, 'EXECUTIVEM', 'EVENT_BEAT_ROCKET_EXECUTIVEM_2'),
    ('BlackbeltGroup', 6, 'MOUNT_MORTAR_B1F', 16, 5, 'BLACKBELT_T', 'EVENT_BEAT_BLACKBELT_KIYO'),
    ('SabrinaGroup', 1, 'SAFFRON_GYM', 9, 9, 'SABRINA', 'EVENT_BEAT_SABRINA'),
    ('LtSurgeGroup', 1, 'VERMILION_GYM', 5, 3, 'LT_SURGE', 'EVENT_BEAT_LTSURGE'),
]


@pytest.fixture(scope='module')
def runtime_constants(repo_root, tmp_path_factory):
    names = {'SPAWN_N_A', 'MAPSETUP_WARP', 'OW_UP', 'OW_DOWN', 'ARTICUNO',
             'PARTYMON_STRUCT_LENGTH', 'MON_SPECIES', 'MON_MOVES', 'MON_PP',
             'MON_LEVEL', 'MON_HP', 'MON_MAXHP', 'MON_ATK', 'MON_DEF', 'MON_SPD',
             'MON_SAT', 'MON_SDF', 'TACKLE', 'SURF', 'MON_ITEM',
             'EVENT_OLIVINE_GYM_JASMINE', 'EVENT_SLOWPOKE_WELL_ROCKETS',
             'EVENT_RADIO_TOWER_ROCKET_TAKEOVER', 'EVENT_GOT_TYROGUE_FROM_KIYO', 'TYROGUE'}
    names.update(('GROUP_TRAINER_HOUSE_B1F', 'MAP_TRAINER_HOUSE_B1F', 'CAL', 'CAL3',
                  'DAILYFLAGS1_TRAINER_HOUSE_F'))
    cal = next(r for r in trainer_contract(repo_root)['targets'] if r['title'].startswith('Cal ('))
    for row, moves in zip(cal['members'], cal['moves'], strict=True):
        names.add(row[1])
        names.update(moves)
    for group, index, map_name, x, y, trainer_class, event in CASES:
        names.update((f'GROUP_{map_name}', f'MAP_{map_name}', trainer_class, event))
        if map_name.endswith('S_ROOM'):
            names.add(f'EVENT_{map_name}_ENTRANCE_CLOSED')
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
    if map_name == 'SLOWPOKE_WELL_B1F':
        events['EVENT_SLOWPOKE_WELL_ROCKETS'] = False
    if map_name == 'RADIO_TOWER_4F':
        events['EVENT_RADIO_TOWER_ROCKET_TAKEOVER'] = False
    league_room = map_name.endswith('S_ROOM')
    with loaded_phase_9_map_checkpoint(repo_root, tmp_path, constants, SCENARIO,
                                      map_name=map_name, x=x, y=16 if league_room else y,
                                      events=events) as session:
        if league_room:
            session.wait_until(lambda current: event_is_set(
                current, constants[f'EVENT_{map_name}_ENTRANCE_CLOSED']),
                60000, 'normal League entrance scene')
            wait_for_idle(session, 60000)
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
        if group == 'BlackbeltGroup':
            session.register_hook('GiveANickname_YesNo')
            session.register_hook('VerticalMenu')
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
        if group == 'BlackbeltGroup':
            advance_with_a_until(session, lambda current: 'GiveANickname_YesNo' in current.hook_history,
                                60000, 'Kiyo Tyrogue gift')
            advance_with_a_until(session, lambda current: 'VerticalMenu' in current.hook_history,
                                60000, 'Tyrogue nickname prompt')
            session.tick(20)
            session.tap('b', 2, 10)
            advance_with_a_until(session, lambda current: event_is_set(
                current, constants['EVENT_GOT_TYROGUE_FROM_KIYO']), 60000, 'Kiyo gift completion')
            assert session.read_symbol('wPartyCount') == 2
            assert session.read_symbol('wPartyMon2Species') == constants['TYROGUE']
            assert session.read_symbol('wPartyMon2Level') == 10
        advance_with_a_until(session, lambda current: current.read_symbol('wScriptMode') == 0,
                            60000, f'{group} script completion')
        wait_for_idle(session, 60000)
        assert session.read_symbol('wBattleMode') == 0


def test_default_cal_loads_natural_moves_and_keeps_daily_limit(repo_root, tmp_path, runtime_constants):
    constants = runtime_constants
    cal = next(r for r in trainer_contract(repo_root)['targets'] if r['title'].startswith('Cal ('))
    with loaded_phase_9_map_checkpoint(repo_root, tmp_path, constants, SCENARIO,
                                      map_name='TRAINER_HOUSE_B1F', x=8, y=3) as session:
        prepare_battle_party(session, constants, constants['ARTICUNO'], True)
        session.enable_script_tracing()
        # Read SRAM bank zero explicitly; the CPU bus may have SRAM disabled.
        flag = session.symbols['sMysteryGiftTrainerHouseFlag']
        assert session.pyboy.memory[flag.bank, flag.address] == 0
        opponent = session.symbols['sMysteryGiftTrainer']
        length = (session.symbols['wMysteryGiftTrainerEnd'].address
                  - session.symbols['wMysteryGiftTrainer'].address)

        def saved_trainer():
            return bytes(session.pyboy.memory[opponent.bank, opponent.address + i] for i in range(length))

        saved_opponent = saved_trainer()
        session.register_hook('ReadTrainerParty.done')
        session.register_hook('ExitBattle')
        session.register_hook('HasEnemyFainted',
                              lambda current: current.write_symbol_bytes('wEnemyMonHP', b'\0\0'))
        session.wait_for_hook('CheckMenuOW', 60000)
        walk_steps(session, 'left', 'wXCoord', -1, 1, 60000)
        advance_with_a_until(session, lambda current: 'ReadTrainerParty.done' in current.hook_history,
                            60000, 'default Cal battle')
        assert session.read_symbol('wOtherTrainerClass') == constants['CAL']
        assert session.read_symbol('wOtherTrainerID') == constants['CAL3']
        assert session.read_symbol('wOTPartyCount') == 3
        for i, (row, moves) in enumerate(zip(cal['members'], cal['moves'], strict=True), 1):
            assert session.read_symbol(f'wOTPartyMon{i}Species') == constants[row[1]]
            assert session.read_symbol(f'wOTPartyMon{i}Level') == 55
            assert session.read_symbol_bytes(f'wOTPartyMon{i}Moves', 4) == bytes(constants[m] for m in moves)
        session.write_symbol('wBattleMenuCursorPosition', 1)
        advance_with_a_until(session, lambda current: 'ExitBattle' in current.hook_history,
                            60000, 'Cal victory')
        advance_with_a_until(session, lambda current: current.read_symbol('wScriptMode') == 0
                            and current.read_symbol('wBattleMode') == 0,
                            60000, 'Cal exit movement')
        assert session.read_symbol('wDailyFlags1') & (1 << constants['DAILYFLAGS1_TRAINER_HOUSE_F'])
        session.wait_for_hook('CheckMenuOW', 60000)
        place_player(session, 8, 3)
        walk_steps(session, 'left', 'wXCoord', -1, 1, 60000)
        advance_with_a_until(session, lambda current:
                            'TrainerHouseReceptionistScript.FoughtTooManyTimes' in current.script_history,
                            60000, 'same-day Cal refusal')
        assert session.hook_history.count('ReadTrainerParty.done') == 1
        assert saved_trainer() == saved_opponent
