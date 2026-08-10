from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Iterable


class ConstantResolutionError(RuntimeError):
    pass


def resolve_constants(
    repo_root: Path,
    work_dir: Path,
    expressions: Iterable[str],
) -> dict[str, int]:
    requested = list(expressions)
    if not requested:
        return {}
    work_dir.mkdir(parents=True, exist_ok=True)
    source = work_dir / "constants.asm"
    object_file = work_dir / "constants.o"
    image = work_dir / "constants.gb"
    source.write_text(
        'INCLUDE "includes.asm"\n'
        'SECTION "Crystal Legends test constants", ROM0[$0000]\n'
        + "\n".join(f"dw {expression}" for expression in requested)
        + "\n"
    )
    commands = [
        [
            "rgbasm",
            "-I",
            f"{repo_root}/",
            "-D",
            "_CRYSTAL11",
            "-D",
            "_CRYSTALLEGENDS",
            "-o",
            str(object_file),
            str(source),
        ],
        ["rgblink", "-o", str(image), str(object_file)],
    ]
    for command in commands:
        result = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise ConstantResolutionError(
                f"failed to resolve {requested!r}\n"
                f"command: {' '.join(command)}\n{result.stderr}"
            )
    data = image.read_bytes()
    return {
        expression: int.from_bytes(data[index * 2 : index * 2 + 2], "little")
        for index, expression in enumerate(requested)
    }
