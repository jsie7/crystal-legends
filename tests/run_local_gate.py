from __future__ import annotations

from pathlib import Path
import subprocess
import sys


PROFILES = {
    "crystallegends": [
        ["make", "test-static"],
        ["make", "crystallegends"],
        ["make", "test-rom"],
        ["make", "test-emulator-smoke"],
    ],
    "all": [
        ["make", "test-static"],
        ["make", "crystallegends"],
        ["make", "test-rom"],
        ["make", "test-emulator"],
        ["make", "compare"],
    ],
}


def _status(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in PROFILES:
        choices = ", ".join(PROFILES)
        print(f"usage: {Path(sys.argv[0]).name} <{choices}>", file=sys.stderr)
        return 2

    repo_root = Path(__file__).resolve().parents[1]
    initial_status = _status(repo_root)
    exit_code = 0
    try:
        for command in PROFILES[sys.argv[1]]:
            print(f"+ {' '.join(command)}", flush=True)
            result = subprocess.run(command, cwd=repo_root, check=False)
            if result.returncode:
                exit_code = result.returncode
                break
    finally:
        final_status = _status(repo_root)
        print("+ git status --short", flush=True)
        if final_status:
            print(final_status, end="")
        if final_status != initial_status:
            print(
                "validation changed the working tree; before/after status differs",
                file=sys.stderr,
            )
            exit_code = exit_code or 1
        elif not initial_status:
            result = subprocess.run(
                [".github/checkdiff.sh"], cwd=repo_root, check=False
            )
            if result.returncode:
                exit_code = exit_code or result.returncode
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
