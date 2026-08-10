import json
from pathlib import Path

import pytest


pytestmark = pytest.mark.static


def test_phase_4_gifts_share_the_proven_capacity_contract(repo_root: Path) -> None:
    records = json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_04_johto_gifts.json").read_text()
    )
    assert len(records) == 3
    assert {record["species"] for record in records} == {
        "CHIKORITA",
        "CYNDAQUIL",
        "TOTODILE",
    }
    assert len({record["completion_event"] for record in records}) == 3
    assert all(
        record["delivery_contract"] == "stock_givepoke_0_party_1_box_2_full"
        for record in records
    )
