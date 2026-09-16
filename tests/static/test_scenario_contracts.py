import json
from pathlib import Path

import pytest


pytestmark = [pytest.mark.static, pytest.mark.phase4]


def test_phase_4_gifts_match_the_locked_scenario_contract(repo_root: Path) -> None:
    records = json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_04_johto_gifts.json").read_text()
    )
    expected = [
        {
            "scenario_id": "phase_04_ilex_chikorita",
            "species": "CHIKORITA",
            "level": 14,
            "map": "ILEX_FOREST",
            "coordinate": [9, 23],
            "start": {"x": 9, "y": 24, "facing": "UP"},
            "prerequisite_event": "EVENT_GOT_HM01_CUT",
            "completion_event": "EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST",
            "object_constant": "ILEXFOREST_CHIKORITA",
            "object_sprite": "SPRITE_CHIKORITA",
            "object_event_flag": "EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST",
            "script": "IlexForestChikoritaScript",
            "visibility": "completion_event_mask",
            "max_frames_per_step": 60000,
            "delivery_contract": "stock_givepoke_0_party_1_box_2_full",
        },
        {
            "scenario_id": "phase_04_burned_tower_cyndaquil",
            "species": "CYNDAQUIL",
            "level": 19,
            "map": "BURNED_TOWER_B1F",
            "coordinate": [10, 4],
            "start": {"x": 10, "y": 5, "facing": "UP"},
            "prerequisite_event": "EVENT_RELEASED_THE_BEASTS",
            "completion_event": "EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER",
            "object_constant": "BURNEDTOWERB1F_CYNDAQUIL",
            "object_sprite": "SPRITE_CYNDAQUIL",
            "object_event_flag": "EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER",
            "script": "BurnedTowerB1FCyndaquilScript",
            "visibility": "prerequisite_sprite_and_completion_event_mask",
            "max_frames_per_step": 60000,
            "delivery_contract": "stock_givepoke_0_party_1_box_2_full",
        },
        {
            "scenario_id": "phase_04_cianwood_totodile",
            "species": "TOTODILE",
            "level": 24,
            "map": "CIANWOOD_CITY",
            "coordinate": [28, 38],
            "start": {"x": 27, "y": 38, "facing": "RIGHT"},
            "prerequisite_event": "EVENT_GOT_SECRETPOTION_FROM_PHARMACY",
            "completion_event": "EVENT_GOT_TOTODILE_FROM_CIANWOOD",
            "object_constant": "CIANWOODCITY_TOTODILE",
            "object_sprite": "SPRITE_TOTODILE",
            "object_event_flag": "EVENT_GOT_TOTODILE_FROM_CIANWOOD",
            "script": "CianwoodCityTotodileScript",
            "visibility": "completion_event_mask",
            "max_frames_per_step": 60000,
            "delivery_contract": "stock_givepoke_0_party_1_box_2_full",
        },
    ]
    assert records == expected
    assert len({record["completion_event"] for record in records}) == 3
