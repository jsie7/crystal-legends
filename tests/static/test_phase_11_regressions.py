from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.asm_conditions import active_lines
from tests.support.content_data import parse_trainer_parties


pytestmark = [pytest.mark.static, pytest.mark.phase11]

CRYSTAL_LEGENDS = {"_CRYSTAL11", "_CRYSTALLEGENDS"}
REFERENCE = {"_CRYSTAL11"}


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_11_endgame.json").read_text()
    )


def _active_code(path: Path, definitions: set[str]) -> list[str]:
    return [
        line.text.split(";", 1)[0].strip()
        for line in active_lines(path.read_text(), definitions)
        if line.text.split(";", 1)[0].strip()
    ]


def test_phase_11_reserves_exact_events_without_save_growth(
    repo_root: Path, scenario: dict
) -> None:
    source = repo_root / "constants/event_flags.asm"
    custom = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    event_names = [name for name, _ in scenario["events"]]
    positions = [custom.index(f"const {name}") for name in event_names]
    assert positions == list(range(positions[0], positions[0] + 2))
    assert all(not any(name in line for line in reference) for name in event_names)
    assert "const_skip 9" in reference
    assert "const_next 1600" in custom
    assert "; Unused: next 107 events" in source.read_text()


def test_red_party_and_dvs_match_the_provisional_contract(
    repo_root: Path, scenario: dict
) -> None:
    parties = parse_trainer_parties((repo_root / "data/trainers/parties.asm").read_text())
    red = [party for party in parties if party.group == "RedGroup"]
    assert len(red) == 1
    assert red[0].name == "RED"
    assert red[0].trainer_type == "TRAINERTYPE_MOVES"
    assert red[0].members == tuple(
        (str(level), species, *moves)
        for level, species, moves in scenario["red"]["party"]
    )

    custom_dvs = _active_code(repo_root / "data/trainers/dvs.asm", CRYSTAL_LEGENDS)
    reference_dvs = _active_code(repo_root / "data/trainers/dvs.asm", REFERENCE)
    assert "dn 15, 15, 15, 15" in custom_dvs
    assert "dn 15, 15, 15, 15" not in reference_dvs
    assert "dn 15, 13, 13, 14" in reference_dvs


def test_red_victory_fact_is_post_battle_and_never_used_for_visibility(
    repo_root: Path,
) -> None:
    room = _active_code(repo_root / "maps/SilverCaveRoom3.asm", CRYSTAL_LEGENDS)
    assert room.index("reloadmapafterbattle") < room.index("setevent EVENT_BEAT_RED")
    assert room.index("setevent EVENT_BEAT_RED") < room.index(
        "disappear SILVERCAVEROOM3_RED"
    )
    assert room.index("setevent EVENT_BEAT_RED") < room.index("credits")
    assert any(
        line.endswith(", EVENT_RED_IN_MT_SILVER")
        for line in room
        if line.startswith("object_event")
    )

    hall = _active_code(repo_root / "maps/HallOfFame.asm", CRYSTAL_LEGENDS)
    assert "clearevent EVENT_RED_IN_MT_SILVER" in hall
    assert "clearevent EVENT_BEAT_RED" not in hall

    clears = []
    for path in repo_root.rglob("*.asm"):
        if "clearevent EVENT_BEAT_RED" in path.read_text():
            clears.append(path)
    assert clears == []
