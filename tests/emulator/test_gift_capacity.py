from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.bedroom_scenario import grant_cheat_pokemon, loaded_session
from tests.support.constant_resolver import resolve_constants
from tests.support.game_state import ProgressState, read_progress


pytestmark = pytest.mark.emulator


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_03_cheat_mode.json").read_text()
    )


@pytest.fixture(scope="module")
def gift_constants(repo_root: Path, tmp_path_factory) -> dict[str, int]:
    return resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("gift_constants"),
        ["EVENT_TEMPORARY_UNTIL_MAP_RELOAD_2", "EEVEE"],
    )


@pytest.fixture(scope="module")
def capacity_results(
    repo_root: Path,
    tmp_path_factory,
    scenario: dict,
    gift_constants: dict[str, int],
) -> dict[int, tuple[ProgressState, ProgressState]]:
    event_number = gift_constants[scenario["sequence_event"]]
    outcomes: dict[int, tuple[ProgressState, ProgressState]] = {}
    with loaded_session(
        repo_root, tmp_path_factory.mktemp("gift_capacity"), scenario
    ) as session:
        initial = read_progress(session)
        assert initial.party.count == 0
        assert initial.current_box.count == 0
        for gift_number in range(1, 28):
            before = read_progress(session)
            outcome = grant_cheat_pokemon(session, scenario, event_number)
            after = read_progress(session)
            expected = 0 if gift_number <= 6 else 1 if gift_number <= 26 else 2
            assert outcome == expected
            outcomes.setdefault(outcome, (before, after))
        final = read_progress(session)
        assert final.party.species == (gift_constants["EEVEE"],) * 6
        assert final.current_box.species == (gift_constants["EEVEE"],) * 20
        assert final.owns(gift_constants["EEVEE"])
        assert final.inventory == initial.inventory
        assert final.money == initial.money
    return outcomes


@pytest.mark.parametrize(
    ("outcome", "party_delta", "box_delta"),
    [(0, 1, 0), (1, 0, 1), (2, 0, 0)],
    ids=["party", "current-box", "storage-full"],
)
def test_stock_givepoke_capacity_outcomes(
    capacity_results: dict[int, tuple[ProgressState, ProgressState]],
    outcome: int,
    party_delta: int,
    box_delta: int,
) -> None:
    before, after = capacity_results[outcome]
    assert after.party.count - before.party.count == party_delta
    assert after.current_box.count - before.current_box.count == box_delta
    assert after.inventory == before.inventory
    assert after.money == before.money
