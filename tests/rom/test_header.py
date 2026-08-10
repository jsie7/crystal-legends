from pathlib import Path

import pytest

from tests.support.rom_image import RomImage, validate_header


pytestmark = pytest.mark.rom


def test_crystal_legends_artifact_identity(repo_root: Path) -> None:
    paths = [
        repo_root / "crystallegends.gbc",
        repo_root / "crystallegends.sym",
        repo_root / "crystallegends.map",
    ]
    assert all(path.is_file() and path.stat().st_size for path in paths)
    rom = RomImage.load(paths[0])
    validate_header(rom)
    print(f"Crystal Legends ROM SHA-256: {rom.sha256}")
