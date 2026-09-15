"""Exercise actual encounter selection, Repel, capture and recruit evolution."""
from contextlib import contextmanager
from functools import lru_cache

import pytest

from tests.emulator.test_phase_02_regressions import _use_first_item_on_first_mon
from tests.support.constant_resolver import resolve_constants
from tests.support.legendary_scenario import advance_with_a_until, prepare_battle_party
from tests.support.map_assets import (
    block_paths_for_maps, collision_at, parse_block_paths, parse_map_tilesets,
)
from tests.support.map_model import parse_map_dimensions
from tests.support.phase_09_scenario import loaded_phase_9_map_checkpoint
from tests.support.phase_12_data import natural_moves
from tests.support.phase_12_wild import target_records, wild_contract

pytestmark = [pytest.mark.emulator, pytest.mark.phase12]
SCENARIO = {'rom': 'crystallegends.gbc', 'symbols': 'crystallegends.sym',
            'max_frames_per_step': 60000}
TIMES = ['MORN', 'DAY', 'NITE']
SELECTIONS = [0, 30, 60, 80, 90, 95, 99]
GRASS_CASES = [
    ('ROUTE_7', 'NITE', 2),
    *[('DIGLETTS_CAVE', time, slot) for time in TIMES for slot in (0, 6)],
    ('ROCK_TUNNEL_1F', 'DAY', 1),
    ('SAFARI_ZONE_BETA', 'DAY', 0),
    ('SAFARI_ZONE_BETA', 'NITE', 0),
    ('SAFARI_ZONE_BETA', 'DAY', 5),
]


def _record(root, kind, map_name):
    table = next(t for t in wild_contract(root)['tables'] if t['kind'] == kind)
    return next(r for r in target_records(table) if r['map'] == map_name)


@lru_cache(maxsize=None)
def _walking_pair(root, map_name):
    dimensions = parse_map_dimensions((root / 'constants/map_constants.asm').read_text())
    paths = block_paths_for_maps(dimensions, parse_block_paths((root / 'data/maps/blocks.asm').read_text()))
    tilesets = parse_map_tilesets((root / 'data/maps/maps.asm').read_text())
    terrain = 'TALL_GRASS' if map_name.startswith('ROUTE_') or map_name == 'SAFARI_ZONE_BETA' else 'FLOOR'
    size = dimensions[map_name]
    for y in range(3, size.height - 2):
        for x in range(3, size.width - 3):
            if all(collision_at(root, map_name, (xx, y), dimensions, paths, tilesets) == terrain
                   for xx in (x, x + 1)):
                return x, y
    raise AssertionError(f'no safe adjacent {terrain} tiles in {map_name}')


def _force_rng_call(session, start_label, end_label, value):
    """Fix one RNG result after its real call; leave selection/level logic intact."""
    start, end = session.symbols[start_label], session.symbols[end_label]
    random = session.symbols['Random']
    code = session.prepared.rom.read_bytes()[start.rom_offset:end.rom_offset]
    instruction = bytes([0xCD, random.address & 255, random.address >> 8])
    assert code.count(instruction) == 1
    address = start.address + code.index(instruction) + len(instruction)

    def set_result(current):
        current.pyboy.register_file.A = value

    session.pyboy.hook_register(start.bank, address, set_result, session)


@pytest.fixture(scope='module')
def constants(repo_root, tmp_path_factory):
    names = {'SPAWN_N_A', 'MAPSETUP_WARP', 'PLAYER_SURF', 'ARTICUNO', 'TACKLE',
             'PARTYMON_STRUCT_LENGTH', 'MON_SPECIES', 'MON_MOVES', 'MON_PP', 'MON_LEVEL',
             'MON_HP', 'MON_MAXHP', 'MON_ATK', 'MON_DEF', 'MON_SPD', 'MON_SAT', 'MON_SDF',
             'WILD_BATTLE', 'BATTLETYPE_NORMAL', 'MASTER_BALL', 'BALL_POCKET', 'ITEM_POCKET',
             'RARE_CANDY', 'STATUSFLAGS_POKEDEX_F', 'HOUNDOOM', 'FLAAFFY', 'AMPHAROS', 'THUNDERPUNCH'}
    for time in TIMES:
        names.add(f'{time}_F')
    for map_name in {case[0] for case in GRASS_CASES}:
        names.update((f'GROUP_{map_name}', f'MAP_{map_name}'))
    for table in wild_contract(repo_root)['tables']:
        for record in target_records(table):
            for level, species in record['slots']:
                names.add(species)
                for bonus in range(5 if table['kind'] == 'water' else 1):
                    names.update(natural_moves(repo_root, species, level + bonus))
    return resolve_constants(repo_root, tmp_path_factory.mktemp('phase12-wild'), sorted(names))


@contextmanager
def _encounter(root, tmp_path, constants, map_name, time, slot, *, water=False, bonus=0, repel=False, capture=False):
    x, y = (12, 4) if water else _walking_pair(root, map_name)
    record = _record(root, 'water' if water else 'grass', map_name)
    level, species = record['slots'][slot if water else TIMES.index(time) * 7 + slot]
    with loaded_phase_9_map_checkpoint(root, tmp_path, constants, SCENARIO,
                                      map_name=map_name, x=x, y=y,
                                      player_state='PLAYER_SURF' if water else None) as session:
        prepare_battle_party(session, constants, constants['ARTICUNO'], True)
        if capture:
            session.write_symbol('wNumBalls', 1)
            session.write_symbol_bytes('wBalls', bytes([constants['MASTER_BALL'], 1, 255]))
            session.write_symbol('wLastPocket', constants['BALL_POCKET'])
        session.register_hook('ChooseWildEncounter', lambda current:
                              current.write_symbol('wTimeOfDay', constants[f'{time}_F']))
        session.register_hook('BattleMenu', lambda current:
                              current.write_symbol('wBattleMenuCursorPosition', 3 if capture else 1))
        session.register_hook('CheckRepelEffect')
        selection = [0, 60, 90][slot] if water else SELECTIONS[slot]
        _force_rng_call(session, 'ChooseWildEncounter.randomloop', 'ChooseWildEncounter.got_it', selection)
        if water:
            _force_rng_call(session, 'ChooseWildEncounter.got_it', 'ChooseWildEncounter.ok',
                            [0, 90, 170, 220, 250][bonus])
        # Frequency itself is verified exhaustively in source/ROM; force attempts
        # here so every scenario remains short and reproducible.
        session.write_symbol_bytes('wMornEncounterRate', b'\xff\xff\xff\xff')
        if repel:
            session.write_symbol('wRepelEffect', 200)
            session.write_symbol('wPartyMon1Level', level + 1)
        session.wait_for_hook('CheckMenuOW', 60000)

        def walk_until(predicate, description):
            start = session.frames
            while not predicate(session) and session.frames - start < 60000:
                if session.read_symbol('wBattleMode') or session.read_symbol('wScriptMode'):
                    session.tap('a', 2, 12)
                else:
                    direction = 'right' if session.read_symbol('wXCoord') == x else 'left'
                    session.tap(direction, 2, 12)
            session.wait_until(predicate, 1, description)

        if repel:
            walk_until(lambda current: current.hook_history.count('CheckRepelEffect') >= 3,
                       'three real Repel checks')
            assert 'BattleMenu' not in session.hook_history
            assert session.read_symbol('wRepelEffect') > 0
            # At equal level, the same active Repel permits this encounter.
            session.write_symbol('wPartyMon1Level', level)
        walk_until(lambda current: 'BattleMenu' in current.hook_history, 'wild battle menu')
        assert session.read_symbol('wBattleMode') == constants['WILD_BATTLE']
        assert session.read_symbol('wBattleType') == constants['BATTLETYPE_NORMAL']
        assert session.read_symbol('wEnemyMonSpecies') == constants[species]
        assert session.read_symbol('wEnemyMonLevel') == level + bonus
        moves = natural_moves(root, species, level + bonus)
        assert session.read_symbol_bytes('wEnemyMonMoves', 4) == bytes(constants[m] for m in moves)
        yield session, level + bonus, species


@pytest.mark.parametrize('map_name,time,slot', GRASS_CASES)
def test_grass_time_slots_and_natural_moves(repo_root, tmp_path, constants, map_name, time, slot):
    with _encounter(repo_root, tmp_path, constants, map_name, time, slot):
        pass


@pytest.mark.parametrize('slot', range(3))
@pytest.mark.parametrize('bonus', range(5))
def test_safari_surf_slots_all_five_level_variants(repo_root, tmp_path, constants, slot, bonus):
    with _encounter(repo_root, tmp_path, constants, 'SAFARI_ZONE_BETA', 'DAY', slot,
                    water=True, bonus=bonus):
        pass


def test_repel_suppresses_lower_levels_and_permits_equal_level(repo_root, tmp_path, constants):
    with _encounter(repo_root, tmp_path, constants, 'SAFARI_ZONE_BETA', 'DAY', 0, repel=True):
        pass


def _return_to_overworld(session):
    target = session.hook_history.count('CheckMenuOW') + 1
    start = session.frames
    while session.hook_history.count('CheckMenuOW') < target and session.frames - start < 60000:
        session.tap('b', 2, 12)
    session.wait_for_hook_count('CheckMenuOW', target, 1)


def _capture_recruit(session, constants, species, level):
    session.write_symbol('wNumBalls', 1)
    session.write_symbol_bytes('wBalls', bytes([constants['MASTER_BALL'], 1, 255]))
    session.write_symbol('wLastPocket', constants['BALL_POCKET'])
    session.write_symbol('wBattleMenuCursorPosition', 3)
    for hook in ('PokeBallEffect.SkipPartyMonFriendBall', 'VerticalMenu', 'ExitBattle', 'PokeBallEffect'):
        session.register_hook(hook)
    advance_with_a_until(session, lambda current: 'PokeBallEffect' in current.hook_history,
                        60000, 'Master Ball use')
    advance_with_a_until(session, lambda current: 'PokeBallEffect.SkipPartyMonFriendBall' in current.hook_history,
                        60000, 'captured recruit nickname prompt')
    nickname_index = session.hook_history.index('PokeBallEffect.SkipPartyMonFriendBall')
    advance_with_a_until(session, lambda current: 'VerticalMenu' in current.hook_history[nickname_index:],
                        60000, 'recruit nickname menu')
    session.tick(20)
    session.tap('b', 2, 10)
    advance_with_a_until(session, lambda current: 'ExitBattle' in current.hook_history,
                        60000, 'capture returns to overworld')
    _return_to_overworld(session)
    assert 'PokeBallEffect' in session.hook_history
    assert session.read_symbol('wPartyCount') == 2
    assert session.read_symbol('wPartyMon2Species') == constants[species]
    assert session.read_symbol('wPartyMon2Level') == level
    # Put the real captured record first to use the existing bag-input helper.
    session.write_symbol_bytes('wPartyMon1', session.read_symbol_bytes(
        'wPartyMon2', constants['PARTYMON_STRUCT_LENGTH']))
    session.write_symbol('wPartyCount', 1)
    session.write_symbol_bytes('wPartySpecies', bytes([constants[species], 255]))
    session.write_symbol('wNumItems', 1)
    session.write_symbol_bytes('wItems', bytes([constants['RARE_CANDY'], 2, 255]))
    session.write_symbol('wLastPocket', constants['ITEM_POCKET'])
    session.write_symbol('wStatusFlags', session.read_symbol('wStatusFlags') |
                         (1 << constants['STATUSFLAGS_POKEDEX_F']))


@pytest.mark.parametrize('map_name,time,slot,evolutions', [
    ('ROUTE_7', 'NITE', 2, [('HOUNDOOM', 27)]),
    ('SAFARI_ZONE_BETA', 'DAY', 0, [('FLAAFFY', 29), ('AMPHAROS', 30)]),
])
def test_caught_recruit_evolves_at_the_approved_next_levels(
    repo_root, tmp_path, constants, map_name, time, slot, evolutions,
):
    with _encounter(repo_root, tmp_path, constants, map_name, time, slot, capture=True) as (session, level, species):
        _capture_recruit(session, constants, species, level)
        for evolved, target_level in evolutions:
            _use_first_item_on_first_mon(session, 60000, 'RareCandyEffect')
            advance_with_a_until(session, lambda current:
                                current.read_symbol('wPartyMon1Species') == constants[evolved],
                                60000, f'{evolved} evolution')
            assert session.read_symbol('wPartyMon1Level') == target_level
            if evolved == 'AMPHAROS':
                advance_with_a_until(session, lambda current: constants['THUNDERPUNCH'] in
                                    current.read_symbol_bytes('wPartyMon1Moves', 4),
                                    60000, 'Ampharos learns ThunderPunch at 30')
            _return_to_overworld(session)
