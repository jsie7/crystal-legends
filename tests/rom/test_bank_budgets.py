from pathlib import Path

import pytest

from tests.support.linker_map import (
    load_bank_budgets,
    parse_linker_map,
    validate_bank_budgets,
)


pytestmark = pytest.mark.rom


def test_linker_headroom_matches_reviewed_budgets(repo_root: Path) -> None:
    usage = parse_linker_map((repo_root / "crystallegends.map").read_text())
    budgets = load_bank_budgets(repo_root / "tests/contracts/bank_budgets.json")
    validate_bank_budgets(usage, budgets)
    report = ", ".join(
        f"{budget.domain}#{budget.bank}=${usage[(budget.domain, budget.bank)].free:04x}"
        for budget in budgets
    )
    print(f"Reviewed free-space report: {report}")
