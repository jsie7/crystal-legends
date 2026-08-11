from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Iterable


class ConstantResolutionError(RuntimeError):
    pass


def assemble_bytes(
    repo_root: Path,
    work_dir: Path,
    source_lines: Iterable[str],
    *,
    length: int,
) -> bytes:
    requested = list(source_lines)
    if not requested:
        return b""
    if length < 1:
        raise ValueError("assembled byte length must be positive")
    work_dir.mkdir(parents=True, exist_ok=True)
    source = work_dir / "bytes.asm"
    object_file = work_dir / "bytes.o"
    image = work_dir / "bytes.gb"
    source.write_text(
        'INCLUDE "includes.asm"\n'
        'SECTION "Crystal Legends test bytes", ROM0[$0000]\n'
        + "\n".join(requested)
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
                f"failed to assemble {requested!r}\n"
                f"command: {' '.join(command)}\n{result.stderr}"
            )
    data = image.read_bytes()
    if len(data) < length:
        raise ConstantResolutionError(
            f"assembly produced {len(data)} bytes, expected at least {length}"
        )
    return data[:length]


def resolve_constants(
    repo_root: Path,
    work_dir: Path,
    expressions: Iterable[str],
) -> dict[str, int]:
    requested = list(expressions)
    if not requested:
        return {}
    data = assemble_bytes(
        repo_root,
        work_dir,
        (f"dw {expression}" for expression in requested),
        length=len(requested) * 2,
    )
    return {
        expression: int.from_bytes(data[index * 2 : index * 2 + 2], "little")
        for index, expression in enumerate(requested)
    }
