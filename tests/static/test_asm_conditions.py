import pytest

from tests.support.asm_conditions import ConditionalSyntaxError, active_lines


pytestmark = pytest.mark.static


def _text(lines: list) -> list[str]:
    return [line.text.strip() for line in lines if line.text.strip()]


def test_nested_custom_and_reference_branches() -> None:
    source = """
always
if DEF(_CRYSTAL11)
crystal11
  if DEF(_CRYSTALLEGENDS)
  legends
  else
  reference11
  endc
else
original
endc
"""

    assert _text(active_lines(source, {"_CRYSTAL11", "_CRYSTALLEGENDS"})) == [
        "always",
        "crystal11",
        "legends",
    ]
    assert _text(active_lines(source, {"_CRYSTAL11"})) == [
        "always",
        "crystal11",
        "reference11",
    ]
    assert _text(active_lines(source, set())) == ["always", "original"]


def test_elif_and_negated_definition() -> None:
    source = """
if !DEF(_CRYSTAL11)
original
elif DEF(_CRYSTALLEGENDS)
legends
else
reference11
endc
"""
    assert _text(active_lines(source, {"_CRYSTAL11", "_CRYSTALLEGENDS"})) == [
        "legends"
    ]


def test_unsupported_condition_fails_loudly() -> None:
    with pytest.raises(ConditionalSyntaxError, match="unsupported RGBDS condition"):
        active_lines("if 1 == 1\nvalue\nendc\n", set())
