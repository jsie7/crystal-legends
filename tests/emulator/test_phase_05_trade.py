from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.bedroom_scenario import (
    dump_battery_ram,
    event_is_set,
    save_game_from_overworld,
    wait_for_idle,
)
from tests.support.constant_resolver import assemble_bytes, resolve_constants
from tests.support.game_state import read_progress
from tests.support.legendary_scenario import advance_with_a_until, place_player
from tests.support.phase_05_scenario import (
    loaded_kim_trade_checkpoint,
    loaded_phase_5_saved_game,
    prepare_level_28_chansey,
)
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.emulator, pytest.mark.phase5]


MAX_FRAMES = 60000


@pytest.fixture(scope="module")
def trade_constants(repo_root: Path, tmp_path_factory) -> dict[str, int]:
    return resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_5_trade_constants"),
        [
            "SPAWN_N_A",
            "MAPSETUP_WARP",
            "GROUP_ROUTE_14",
            "MAP_ROUTE_14",
            "OW_UP",
            "FROZEN",
            "SPRITEMOVEDATA_STANDING_DOWN",
            "STANDING",
            "NPC_TRADE_KIM",
            "EVENT_GOT_AERODACTYL_FROM_ALPH",
            "PARTYMON_STRUCT_LENGTH",
            "MON_SPECIES",
            "MON_ITEM",
            "MON_MOVES",
            "MON_OT_ID",
            "MON_EXP",
            "MON_DVS",
            "MON_PP",
            "MON_HAPPINESS",
            "MON_LEVEL",
            "MON_HP",
            "MON_MAXHP",
            "MON_ATK",
            "MON_DEF",
            "MON_SPD",
            "MON_SAT",
            "MON_SDF",
            "NAME_LENGTH",
            "MON_NAME_LENGTH",
            "CHANSEY",
            "GIRAFARIG",
            "NO_ITEM",
            "TACKLE",
            "NPCTRADE_STRUCT_LENGTH",
            "NPCTRADE_NICKNAME",
            "NPCTRADE_DVS",
            "NPCTRADE_ITEM",
            "NPCTRADE_OT_ID",
            "NPCTRADE_OT_NAME",
        ],
    )


@pytest.fixture(scope="module")
def kim_trade_record(repo_root: Path, trade_constants: dict[str, int]) -> bytes:
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    width = trade_constants["NPCTRADE_STRUCT_LENGTH"]
    offset = (
        symbols["NPCTrades"].rom_offset
        + trade_constants["NPC_TRADE_KIM"] * width
    )
    return rom.slice(offset, width)


def _trade_flag_is_set(session, trade_index: int) -> bool:
    return bool(session.read_symbol("wTradeFlags") & (1 << trade_index))


def _stand_below_kim(session, constants: dict[str, int]) -> None:
    struct_id = session.read_symbol("wMap4ObjectStructID")
    assert 1 <= struct_id <= 12
    flags = bytearray(session.read_symbol_bytes(f"wObject{struct_id}Flags", 2))
    flags[1] |= constants["FROZEN"]
    session.write_symbol_bytes(f"wObject{struct_id}Flags", bytes(flags))
    session.write_symbol(
        f"wObject{struct_id}MovementType",
        constants["SPRITEMOVEDATA_STANDING_DOWN"],
    )
    session.write_symbol(
        f"wObject{struct_id}Walking", constants["STANDING"] & 0xFF
    )
    for field, value in (
        ("MapX", 11),
        ("MapY", 9),
        ("LastMapX", 11),
        ("LastMapY", 9),
        ("InitX", 11),
        ("InitY", 9),
    ):
        session.write_symbol(f"wObject{struct_id}{field}", value)
    session.write_symbol("wMap4ObjectXCoord", 7)
    session.write_symbol("wMap4ObjectYCoord", 5)
    place_player(session, 7, 6)


def _interact_with_kim_and_complete_trade(session, constants: dict[str, int]) -> None:
    for label in (
        "_YesNoBox",
        "VerticalMenu",
        "PartyMenuSelect",
        "DoNPCTrade",
        "TradeAnimation",
        "Script_waitbutton",
    ):
        session.register_hook(label)
    session.enable_script_tracing()
    yes_no_count = session.hook_history.count("_YesNoBox") + 1
    menu_count = session.hook_history.count("VerticalMenu") + 1
    party_menu_count = session.hook_history.count("PartyMenuSelect") + 1
    trade_count = session.hook_history.count("DoNPCTrade") + 1

    _stand_below_kim(session, constants)
    session.tap("up", 2, 10)
    session.tap("a", 2, 10)
    session.wait_for_script("Kim", MAX_FRAMES)
    advance_with_a_until(
        session,
        lambda current: (
            current.hook_history.count("_YesNoBox") >= yes_no_count
            and current.hook_history.count("VerticalMenu") >= menu_count
        ),
        MAX_FRAMES,
        "Kim trade confirmation",
    )
    session.tick(20)
    session.tap("a", 2, 10)
    session.wait_for_hook_count("PartyMenuSelect", party_menu_count, MAX_FRAMES)
    session.tick(20)
    session.tap("a", 2, 10)
    advance_with_a_until(
        session,
        lambda current: current.hook_history.count("DoNPCTrade") >= trade_count,
        MAX_FRAMES,
        "Kim trade execution",
    )
    session.wait_until(
        lambda current: current.read_symbol("wPartyMon1Species")
        == constants["GIRAFARIG"],
        MAX_FRAMES,
        "Girafarig delivery",
    )
    start = session.frames
    while (
        session.read_symbol("wScriptMode") != 0
        and session.frames - start < MAX_FRAMES
    ):
        session.tap("a", 2, 20)
    wait_for_idle(session, 1)


def _finish_completed_trade_dialogue(session, constants: dict[str, int]) -> None:
    trade_count = session.hook_history.count("DoNPCTrade")
    session.register_hook("DoNPCTrade")
    session.enable_script_tracing()
    _stand_below_kim(session, constants)
    session.tap("up", 2, 10)
    session.tap("a", 2, 10)
    session.wait_for_script("Kim", MAX_FRAMES)
    start = session.frames
    while (
        session.read_symbol("wScriptMode") != 0
        and session.frames - start < MAX_FRAMES
    ):
        session.tap("a", 2, 20)
    wait_for_idle(session, 1)
    assert session.hook_history.count("DoNPCTrade") == trade_count


def test_kim_trade_delivers_same_level_girafarig_once_and_persists(
    repo_root: Path,
    tmp_path: Path,
    trade_constants: dict[str, int],
    kim_trade_record: bytes,
) -> None:
    nickname = assemble_bytes(
        repo_root,
        tmp_path / "chansey_name",
        ['dname "CHANSEY", MON_NAME_LENGTH'],
        length=trade_constants["MON_NAME_LENGTH"],
    )
    player_name = assemble_bytes(
        repo_root,
        tmp_path / "player_name",
        ['dname "PLAYER", NAME_LENGTH'],
        length=trade_constants["NAME_LENGTH"],
    )
    persisted = tmp_path / "kim-complete.sav"

    with loaded_kim_trade_checkpoint(
        repo_root,
        tmp_path / "initial",
        trade_constants,
        MAX_FRAMES,
    ) as session:
        prepare_level_28_chansey(
            session,
            trade_constants,
            nickname,
            player_name,
        )
        assert not _trade_flag_is_set(
            session, trade_constants["NPC_TRADE_KIM"]
        )
        assert not event_is_set(
            session, trade_constants["EVENT_GOT_AERODACTYL_FROM_ALPH"]
        )
        _interact_with_kim_and_complete_trade(session, trade_constants)

        progress = read_progress(session)
        assert progress.party.species == (trade_constants["GIRAFARIG"],)
        assert progress.owns(trade_constants["GIRAFARIG"])
        assert session.read_symbol("wPartyMon1Level") == 28
        assert session.read_symbol("wPartyMon1Item") == kim_trade_record[
            trade_constants["NPCTRADE_ITEM"]
        ]
        assert session.read_symbol_bytes("wPartyMon1DVs", 2) == kim_trade_record[
            trade_constants["NPCTRADE_DVS"] : trade_constants["NPCTRADE_DVS"] + 2
        ]
        assert session.read_symbol_bytes("wPartyMon1ID", 2) == int.from_bytes(
            kim_trade_record[
                trade_constants["NPCTRADE_OT_ID"] : trade_constants["NPCTRADE_OT_ID"]
                + 2
            ],
            "little",
        ).to_bytes(2, "big")
        assert session.read_symbol_bytes(
            "wPartyMon1Nickname", trade_constants["MON_NAME_LENGTH"]
        ) == kim_trade_record[
            trade_constants["NPCTRADE_NICKNAME"] : trade_constants[
                "NPCTRADE_NICKNAME"
            ]
            + trade_constants["MON_NAME_LENGTH"]
        ]
        assert session.read_symbol_bytes(
            "wPartyMon1OT", trade_constants["NAME_LENGTH"]
        ) == kim_trade_record[
            trade_constants["NPCTRADE_OT_NAME"] : trade_constants[
                "NPCTRADE_OT_NAME"
            ]
            + trade_constants["NAME_LENGTH"]
        ]
        assert _trade_flag_is_set(session, trade_constants["NPC_TRADE_KIM"])
        assert not event_is_set(
            session, trade_constants["EVENT_GOT_AERODACTYL_FROM_ALPH"]
        )
        save_game_from_overworld(session, MAX_FRAMES)
        dump_battery_ram(session, persisted)

    scenario = {"max_frames_per_step": MAX_FRAMES}
    with loaded_phase_5_saved_game(
        repo_root,
        tmp_path / "reload",
        trade_constants,
        scenario,
        persisted,
    ) as session:
        before = session.read_symbol_range("wPokemonData", "wPokemonDataEnd")
        assert _trade_flag_is_set(session, trade_constants["NPC_TRADE_KIM"])
        assert read_progress(session).party.species == (
            trade_constants["GIRAFARIG"],
        )
        _finish_completed_trade_dialogue(session, trade_constants)
        assert session.read_symbol_range("wPokemonData", "wPokemonDataEnd") == before
        assert not event_is_set(
            session, trade_constants["EVENT_GOT_AERODACTYL_FROM_ALPH"]
        )
