from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Sequence


_BANK_RE = re.compile(r"^(ROM0|ROMX|SRAM|WRAM0|WRAMX|HRAM) bank #(\d+):$")
_EMPTY_RE = re.compile(r"^\s*TOTAL EMPTY: \$([0-9a-fA-F]+) bytes?$")


class LinkerMapError(ValueError):
    pass


@dataclass(frozen=True)
class BankUsage:
    domain: str
    bank: int
    free: int


@dataclass(frozen=True)
class BankBudget:
    domain: str
    bank: int
    minimum_free: int
    reason: str


def parse_linker_map(text: str) -> dict[tuple[str, int], BankUsage]:
    current: tuple[str, int] | None = None
    result: dict[tuple[str, int], BankUsage] = {}
    for line in text.splitlines():
        bank_match = _BANK_RE.match(line)
        if bank_match:
            domain, bank = bank_match.groups()
            current = (domain, int(bank))
            continue
        empty_match = _EMPTY_RE.match(line)
        if empty_match and current is not None:
            if current in result:
                raise LinkerMapError(f"duplicate bank report for {current}")
            result[current] = BankUsage(*current, int(empty_match.group(1), 16))
            current = None
    if not result:
        raise LinkerMapError("no bank usage records found")
    return result


def load_bank_budgets(path: Path) -> list[BankBudget]:
    return [BankBudget(**record) for record in json.loads(path.read_text())]


def validate_bank_budgets(
    usage: dict[tuple[str, int], BankUsage], budgets: Sequence[BankBudget]
) -> None:
    failures: list[str] = []
    for budget in budgets:
        key = (budget.domain, budget.bank)
        actual = usage.get(key)
        if actual is None:
            failures.append(f"linker map has no {budget.domain} bank {budget.bank}")
        elif actual.free < budget.minimum_free:
            failures.append(
                f"{budget.domain} bank {budget.bank} has ${actual.free:04x} free; "
                f"budget requires at least ${budget.minimum_free:04x}: "
                f"{budget.reason}"
            )
    if failures:
        raise LinkerMapError("\n".join(failures))
