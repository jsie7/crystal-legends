from pathlib import Path

import pytest


@pytest.mark.static
def test_pytest_runs_from_repository_root(repo_root: Path) -> None:
    assert (repo_root / "Makefile").is_file()
    assert (repo_root / "includes.asm").is_file()
