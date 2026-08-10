from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


_CONDITION_RE = re.compile(r"^(!)?DEF\(([A-Za-z_][A-Za-z0-9_]*)\)$")


class ConditionalSyntaxError(ValueError):
    pass


@dataclass(frozen=True)
class SourceLine:
    number: int
    text: str


@dataclass
class _Frame:
    parent_active: bool
    branch_taken: bool
    active: bool
    saw_else: bool = False


def _evaluate(expression: str, definitions: frozenset[str]) -> bool:
    match = _CONDITION_RE.fullmatch(expression.strip())
    if match is None:
        raise ConditionalSyntaxError(f"unsupported RGBDS condition: {expression}")
    negate, name = match.groups()
    value = name in definitions
    return not value if negate else value


def active_lines(text: str, definitions: Iterable[str]) -> list[SourceLine]:
    """Return lines active for a small, explicit RGBDS conditional subset."""

    defined = frozenset(definitions)
    stack: list[_Frame] = []
    output: list[SourceLine] = []

    for number, raw_line in enumerate(text.splitlines(), start=1):
        code = raw_line.split(";", 1)[0].strip()
        directive, _, expression = code.partition(" ")
        directive = directive.lower()

        if directive == "if":
            parent_active = stack[-1].active if stack else True
            condition = _evaluate(expression, defined)
            stack.append(
                _Frame(
                    parent_active=parent_active,
                    branch_taken=condition,
                    active=parent_active and condition,
                )
            )
            continue

        if directive == "elif":
            if not stack:
                raise ConditionalSyntaxError(f"line {number}: elif without if")
            frame = stack[-1]
            if frame.saw_else:
                raise ConditionalSyntaxError(f"line {number}: elif after else")
            condition = _evaluate(expression, defined)
            frame.active = frame.parent_active and not frame.branch_taken and condition
            frame.branch_taken = frame.branch_taken or condition
            continue

        if directive == "else" and not expression:
            if not stack:
                raise ConditionalSyntaxError(f"line {number}: else without if")
            frame = stack[-1]
            if frame.saw_else:
                raise ConditionalSyntaxError(f"line {number}: duplicate else")
            frame.saw_else = True
            frame.active = frame.parent_active and not frame.branch_taken
            frame.branch_taken = True
            continue

        if directive == "endc" and not expression:
            if not stack:
                raise ConditionalSyntaxError(f"line {number}: endc without if")
            stack.pop()
            continue

        if not stack or stack[-1].active:
            output.append(SourceLine(number=number, text=raw_line))

    if stack:
        raise ConditionalSyntaxError("unterminated RGBDS conditional")
    return output
