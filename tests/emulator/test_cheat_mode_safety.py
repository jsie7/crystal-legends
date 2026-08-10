from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.bedroom_scenario import (
    dump_battery_ram,
    grant_cheat_item,
    grant_cheat_money,
    grant_cheat_pokemon,
    inspect_tv_once,
    loaded_session,
    open_cheat_mode,
    save_game_from_overworld,
    start_saved_game,
    story_snapshot,
    wait_for_idle,
)
from tests.support.constant_resolver import resolve_constants
from tests.support.game_state import read_progress
from tests.support.pyboy_session import PyBoySession, prepare_rom


pytestmark = pytest.mark.emulator


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_03_cheat_mode.json").read_text()
    )


@pytest.fixture(scope="module")
def cheat_contract(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/contracts/phase_03_cheat_actions.json").read_text()
    )


@pytest.fixture(scope="module")
def cheat_constants(
    repo_root: Path, tmp_path_factory, cheat_contract: dict, scenario: dict
) -> dict[str, int]:
    names = {
        scenario["sequence_event"],
        "PARTY_LENGTH",
        "MONS_PER_BOX",
    }
    names.update(row["item"] for row in cheat_contract["items"])
    names.update(row["species"] for row in cheat_contract["pokemon"])
    return resolve_constants(
        repo_root, tmp_path_factory.mktemp("cheat_runtime_constants"), sorted(names)
    )


@pytest.mark.parametrize("row_index", range(18))
def test_every_item_action_is_repeatable_and_story_isolated(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    cheat_contract: dict,
    cheat_constants: dict[str, int],
    row_index: int,
) -> None:
    row = cheat_contract["items"][row_index]
    item = cheat_constants[row["item"]]
    event = cheat_constants[scenario["sequence_event"]]
    with loaded_session(repo_root, tmp_path, scenario) as session:
        before_story = story_snapshot(session)
        assert grant_cheat_item(
            session, scenario, event, item, row["pocket"], row["menu_path"]
        ) == (0, 10)
        assert grant_cheat_item(
            session, scenario, event, item, row["pocket"], row["menu_path"]
        ) == (10, 20)
        assert story_snapshot(session) == before_story


@pytest.mark.parametrize(
    ("pocket", "count_label", "entries_label", "capacity", "row_index"),
    [
        ("items", "wNumItems", "wItems", 20, 0),
        ("balls", "wNumBalls", "wBalls", 12, 1),
    ],
    ids=["items-pocket", "balls-pocket"],
)
def test_distinct_item_capacity_failure_is_atomic(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    cheat_contract: dict,
    cheat_constants: dict[str, int],
    pocket: str,
    count_label: str,
    entries_label: str,
    capacity: int,
    row_index: int,
) -> None:
    row = cheat_contract["items"][row_index]
    item = cheat_constants[row["item"]]
    event = cheat_constants[scenario["sequence_event"]]
    with loaded_session(repo_root, tmp_path, scenario) as session:
        candidates = [value for value in range(1, 0xFF) if value != item][:capacity]
        session.write_symbol(count_label, capacity)
        session.write_symbol_bytes(
            entries_label,
            bytes([value for candidate in candidates for value in (candidate, 1)] + [0xFF]),
        )
        before_story = story_snapshot(session)
        assert grant_cheat_item(
            session, scenario, event, item, pocket, row["menu_path"]
        ) == (0, 0)
        assert story_snapshot(session) == before_story


def test_item_stack_near_99_splits_without_loss_or_wrap(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    cheat_contract: dict,
    cheat_constants: dict[str, int],
) -> None:
    row = cheat_contract["items"][0]
    item = cheat_constants[row["item"]]
    event = cheat_constants[scenario["sequence_event"]]
    with loaded_session(repo_root, tmp_path, scenario) as session:
        session.write_symbol("wNumItems", 1)
        session.write_symbol_bytes("wItems", bytes([item, 95, 0xFF]))
        before, after = grant_cheat_item(
            session, scenario, event, item, row["pocket"], row["menu_path"]
        )
        assert before == 95
        assert after == 105
        assert [
            quantity
            for candidate, quantity in read_progress(session).inventory.items
            if candidate == item
        ] == [99, 6]


@pytest.mark.parametrize(
    ("starting", "expected"),
    [
        (0, 100_000),
        (123_456, 223_456),
        (899_999, 999_999),
        (900_000, 999_999),
        (999_998, 999_999),
        (999_999, 999_999),
    ],
)
def test_money_action_saturates_without_wrap(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    cheat_constants: dict[str, int],
    starting: int,
    expected: int,
) -> None:
    event = cheat_constants[scenario["sequence_event"]]
    with loaded_session(repo_root, tmp_path, scenario) as session:
        session.write_symbol_bytes("wMoney", starting.to_bytes(3, "big"))
        before_story = story_snapshot(session)
        assert grant_cheat_money(session, scenario, event) == (starting, expected)
        assert story_snapshot(session) == before_story


def test_repeated_money_actions_reach_the_stock_cap(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    cheat_constants: dict[str, int],
) -> None:
    event = cheat_constants[scenario["sequence_event"]]
    with loaded_session(repo_root, tmp_path, scenario) as session:
        session.write_symbol_bytes("wMoney", bytes(3))
        for grant in range(1, 11):
            _before, after = grant_cheat_money(session, scenario, event)
            assert after == min(grant * 100_000, 999_999)


def _set_party_full(session, species: int) -> None:
    session.write_symbol("wPartyCount", 6)
    session.write_symbol_bytes("wPartySpecies", bytes([species] * 6 + [0xFF]))


@pytest.mark.parametrize("row_index", range(4), ids=["eevee", "dratini", "larvitar", "porygon"])
def test_every_pokemon_action_covers_party_box_full_retry_and_duplicates(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    cheat_contract: dict,
    cheat_constants: dict[str, int],
    row_index: int,
) -> None:
    row = cheat_contract["pokemon"][row_index]
    species = cheat_constants[row["species"]]
    event = cheat_constants[scenario["sequence_event"]]

    with loaded_session(repo_root, tmp_path / "party", scenario) as session:
        before_story = story_snapshot(session)
        assert grant_cheat_pokemon(session, scenario, event, row["menu_index"]) == 0
        first = read_progress(session)
        assert first.party.species == (species,)
        assert session.read_symbol("wPartyMon1Level") == row["level"]
        assert session.read_symbol("wPartyMon1Item") == 0
        assert first.owns(species)
        assert grant_cheat_pokemon(session, scenario, event, row["menu_index"]) == 0
        assert read_progress(session).party.species == (species, species)
        assert story_snapshot(session) == before_story

    with loaded_session(repo_root, tmp_path / "box", scenario) as session:
        _set_party_full(session, species)
        before_story = story_snapshot(session)
        assert grant_cheat_pokemon(session, scenario, event, row["menu_index"]) == 1
        assert read_progress(session).current_box.species == (species,)
        assert story_snapshot(session) == before_story

    with loaded_session(repo_root, tmp_path / "full", scenario) as session:
        _set_party_full(session, species)
        session.write_symbol("sBoxCount", cheat_constants["MONS_PER_BOX"])
        session.write_symbol_bytes(
            "sBoxSpecies",
            bytes([species] * cheat_constants["MONS_PER_BOX"] + [0xFF]),
        )
        before_story = story_snapshot(session)
        assert grant_cheat_pokemon(session, scenario, event, row["menu_index"]) == 2
        assert read_progress(session).current_box.count == cheat_constants["MONS_PER_BOX"]
        assert story_snapshot(session) == before_story
        session.write_symbol("sBoxCount", 0)
        session.write_symbol("sBoxSpecies", 0xFF)
        assert grant_cheat_pokemon(session, scenario, event, row["menu_index"]) == 1
        assert read_progress(session).current_box.species == (species,)


@pytest.mark.parametrize(
    ("path", "explicit_index"),
    [
        ((1,), 6),
        ((1, 2), 3),
        ((1, 3), 6),
        ((1, 4), 7),
        ((1, 5), 5),
        ((3,), 5),
    ],
    ids=["supplies", "balls", "healing", "stones", "trade-items", "pokemon"],
)
def test_every_submenu_supports_b_and_explicit_back(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    cheat_constants: dict[str, int],
    path: tuple[int, ...],
    explicit_index: int,
) -> None:
    event = cheat_constants[scenario["sequence_event"]]
    max_frames = scenario["max_frames_per_step"]
    for method in ("b", "row"):
        with loaded_session(repo_root, tmp_path / method, scenario) as session:
            before_story = story_snapshot(session)
            inspect_tv_once(session, scenario, event)
            open_cheat_mode(session, scenario, event)
            for index in path:
                next_menu = session.hook_history.count("VerticalMenu") + 1
                session.tick(20)
                for _ in range(index - 1):
                    session.tap("down", 10, 10)
                session.tap("a", 10, 10)
                session.wait_for_hook_count("VerticalMenu", next_menu, max_frames)
            parent_menu = session.hook_history.count("VerticalMenu") + 1
            session.tick(20)
            if method == "b":
                session.tap("b", 10, 10)
            else:
                for _ in range(explicit_index - 1):
                    session.tap("down", 10, 10)
                session.tap("a", 10, 10)
            session.wait_for_hook_count("VerticalMenu", parent_menu, max_frames)
            for _ in range(len(path) - 1):
                next_menu = session.hook_history.count("VerticalMenu") + 1
                session.tick(20)
                session.tap("b", 10, 10)
                session.wait_for_hook_count("VerticalMenu", next_menu, max_frames)
            session.tick(20)
            session.tap("b", 10, 10)
            wait_for_idle(session, max_frames)
            assert story_snapshot(session) == before_story


def test_item_money_party_and_box_changes_survive_native_save_reload(
    repo_root: Path,
    tmp_path: Path,
    scenario: dict,
    cheat_contract: dict,
    cheat_constants: dict[str, int],
) -> None:
    event = cheat_constants[scenario["sequence_event"]]
    item_row = cheat_contract["items"][0]
    party_row = cheat_contract["pokemon"][0]
    box_row = cheat_contract["pokemon"][1]
    item = cheat_constants[item_row["item"]]
    party_species = cheat_constants[party_row["species"]]
    box_species = cheat_constants[box_row["species"]]
    persisted = tmp_path / "persisted.sav"
    max_frames = 20_000

    with loaded_session(repo_root, tmp_path / "before", scenario) as session:
        session.write_symbol_bytes("wMoney", bytes(3))
        before_story = story_snapshot(session)
        assert grant_cheat_item(
            session,
            scenario,
            event,
            item,
            item_row["pocket"],
            item_row["menu_path"],
        ) == (0, 10)
        assert grant_cheat_money(session, scenario, event) == (0, 100_000)
        assert grant_cheat_pokemon(
            session, scenario, event, party_row["menu_index"]
        ) == 0
        _set_party_full(session, party_species)
        assert grant_cheat_pokemon(
            session, scenario, event, box_row["menu_index"]
        ) == 1
        save_game_from_overworld(session, max_frames)
        dump_battery_ram(session, persisted)

    prepared = prepare_rom(
        tmp_path / "after",
        repo_root / scenario["rom"],
        repo_root / scenario["symbols"],
        save_fixture=persisted,
    )
    with PyBoySession(prepared) as session:
        start_saved_game(session, max_frames)
        progress = read_progress(session)
        assert dict(progress.inventory.items)[item] == 10
        assert progress.money == 100_000
        assert progress.party.species == (party_species,) * 6
        assert progress.current_box.species == (box_species,)
        assert story_snapshot(session) == before_story
