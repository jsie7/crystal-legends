from hashlib import sha256
from pathlib import Path
import struct
import subprocess

import pytest

from tests.support.asm_conditions import active_lines


pytestmark = [pytest.mark.static, pytest.mark.phase10]
CUSTOM = {"_CRYSTAL11", "_CRYSTALLEGENDS"}
REFERENCE = {"_CRYSTAL11"}
# First 12 tiles of pret/pokered gfx/sprites/giovanni.png; provenance in workflows.md.
STANDING_SHA256 = "d06c85addab6141e8949c58c27f39072ce3f9f7aab2e14a9a81542daeb1a3795"


def _code(path: Path, definitions: set[str]) -> list[str]:
    return [line.text.split(";", 1)[0].strip()
            for line in active_lines(path.read_text(), definitions)
            if line.text.split(";", 1)[0].strip()]


def test_giovanni_png_has_only_the_three_unmodified_red_standing_frames(
    repo_root: Path, tmp_path: Path,
) -> None:
    source = repo_root / "gfx/sprites/giovanni.png"
    png = source.read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">IIBBBBB", png[16:29]) == (16, 48, 2, 0, 0, 0, 0)
    output = tmp_path / "giovanni.2bpp"
    subprocess.run(["rgbgfx", "--colors", "dmg", "-o", str(output), str(source)],
                   capture_output=True, check=True)
    tiles = output.read_bytes()
    assert len(tiles) == 12 * 16
    assert sha256(tiles).hexdigest() == STANDING_SHA256
    assert len({tiles[start:start + 64] for start in (0, 64, 128)}) == 3


def test_giovanni_id_is_appended_without_shifting_existing_sprites(repo_root: Path) -> None:
    path = repo_root / "constants/sprite_constants.asm"
    custom = _code(path, CUSTOM)
    reference = _code(path, REFERENCE)
    previous = custom.index("const SPRITE_STANDING_YOUNGSTER")
    assert custom[previous + 1:previous + 3] == [
        "const SPRITE_GIOVANNI", "DEF NUM_OVERWORLD_SPRITES EQU const_value - 1",
    ]
    assert "const SPRITE_GIOVANNI" not in reference
    assert custom[:previous + 1] == reference[:previous + 1]
    # The following Pokemon icon range still starts at the original fixed ID.
    assert "const_next $80" in custom[previous + 3:]


def test_giovanni_table_entry_is_standing_brown_and_custom_only(repo_root: Path) -> None:
    path = repo_root / "data/sprites/sprites.asm"
    custom = _code(path, CUSTOM)
    reference = _code(path, REFERENCE)
    entry = "overworld_sprite GiovanniSpriteGFX, 12, STANDING_SPRITE, PAL_OW_BROWN"
    assert custom[-2:] == [entry, "assert_table_length NUM_OVERWORLD_SPRITES"]
    assert [line for line in custom if line != entry] == reference


def test_giovanni_graphics_use_the_reserved_bank_without_relocating_stock_art(
    repo_root: Path,
) -> None:
    path = repo_root / "gfx/sprites.asm"
    custom = _code(path, CUSTOM)
    reference = _code(path, REFERENCE)
    section = 'SECTION "Crystal Legends Sprites", ROMX'
    assert custom[:custom.index(section)] == reference[:reference.index(section)]
    assert reference[-1] == section
    assert 'GiovanniSpriteGFX::            INCBIN "gfx/sprites/giovanni.2bpp"' in custom
    assert "assert GiovanniSpriteGFXEnd - GiovanniSpriteGFX == 12 tiles" in custom
    layout = (repo_root / "layout.link").read_text()
    bank = layout.split("ROMX $2c\n", 1)[1].split("ROMX $2d\n", 1)[0]
    assert [line.strip() for line in bank.splitlines() if line.strip()] == [
        '"Map Blocks 3"', '"Crystal Legends Sprites"',
    ]
