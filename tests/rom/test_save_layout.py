from pathlib import Path
import json

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.symbol_table import SymbolTable


pytestmark = pytest.mark.rom


def test_save_critical_layout_matches_approved_fingerprint(
    repo_root: Path, tmp_path: Path
) -> None:
    records = json.loads((repo_root / "tests/contracts/save_layout.json").read_text())
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    expressions = sorted(
        {record["size_expression"] for record in records if "size_expression" in record}
    )
    resolved_sizes = resolve_constants(repo_root, tmp_path, expressions)
    failures: list[str] = []
    for record in records:
        symbol = symbols[record["label"]]
        if (symbol.bank, symbol.address) != (record["bank"], record["address"]):
            failures.append(
                f"{record['label']}: expected {record['bank']:02x}:"
                f"{record['address']:04x}, got {symbol.bank:02x}:{symbol.address:04x}"
            )
        if "end_label" in record:
            end = symbols[record["end_label"]]
            actual_size = end.address - symbol.address
            if end.bank != symbol.bank or actual_size != record["size"]:
                failures.append(
                    f"{record['label']}..{record['end_label']}: expected size "
                    f"{record['size']}, got {actual_size}"
                )
        if "size_expression" in record:
            actual_size = resolved_sizes[record["size_expression"]]
            if actual_size != record["size"]:
                failures.append(
                    f"{record['label']} size expression {record['size_expression']} "
                    f"is {actual_size}, expected {record['size']}"
                )
    assert not failures, "\n".join(failures)
