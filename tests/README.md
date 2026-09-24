# Crystal Legends automated tests

The harness checks production source/data, compiled ROM contracts, and headless
emulator scenarios. Read [feature coverage](coverage.md) for what each profile
proves and [project status](../docs/status.md) for recorded acceptance. Manual
visual, audio, balance, and full-playthrough checks remain separate.

## Setup and profiles

The automated harness is opt-in and local to development. It does not
change the default `make` target or `.github/workflows/main.yml`. It requires
Python 3.10 or newer. Install its locked Python dependencies once, then use the
narrowest useful profile:

```bash
uv sync --frozen --group test
make test-static
make test-rom
make test-emulator-smoke
make test-emulator
make test-crystallegends
make test-all
```

The profiles have distinct responsibilities:

| Command | Coverage |
| --- | --- |
| `make test-static` | Source/data contracts only; no ROM required. |
| `make test-rom` | Build Crystal Legends and the v1.1 reference ROM, then decode compiled headers, labels, events, save layout, and bank budgets. |
| `make test-emulator-smoke` | Build Crystal Legends and run only short boot/fixture smoke scenarios. |
| `make test-emulator` | Build the required ROMs and run every implemented headless PyBoy scenario. |
| `make test-crystallegends` | Recommended focused gate: static checks, custom build, compiled-ROM contracts, emulator smoke, and generated-file cleanliness. |
| `make test-all` | Complete local handoff gate: all of the above, all emulator scenarios, and `make compare` for every upstream reference artifact. |

Use `make test-static` while editing parsers or data contracts,
`make test-crystallegends` before an ordinary Crystal Legends commit, and
`make test-all` at a milestone handoff or after changes that could affect
reference variants. A profile stops at its first failing stage and returns that
stage's exit status.

The tests are layered deliberately. Static checks provide exhaustive breadth
over maps and content records. Compiled-ROM checks use `crystallegends.sym` and
the assembled bytes to catch source/build disagreement. Headless scenarios run
the production `crystallegends.gbc` through normal inputs and inspect symbolic
RAM/SRAM state. These layers complement [manual playtests](../docs/playtesting.md).

## Focused feature checks

Build both required ROMs before running pytest directly. Select the feature
marker from the table, then use a file or pytest node ID for a narrower retry.

```bash
make crystallegends crystal11
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest -m phase4
```

| Feature | Selection | Detailed coverage |
| --- | --- | --- |
| Legendary starter gifts (Phase 1) | `tests/{static,rom,emulator}/test_legendary_branches.py` | [Contracts and limits](coverage.md#legendary-starter-gifts-phase-1) |
| Evolutions, items, and Celebi (Phase 2) | `-m phase2` | [Contracts and limits](coverage.md#evolutions-items-and-celebi-phase-2) |
| CHEAT MODE (Phase 3) | `-m phase3` | [Contracts and limits](coverage.md#cheat-mode-phase-3) |
| Johto starter gifts (Phase 4) | `-m phase4` | [Contracts and limits](coverage.md#johto-starter-gifts-phase-4) |
| Ruins gifts and Girafarig trade (Phase 5) | `-m phase5` | [Contracts and limits](coverage.md#ruins-gifts-and-girafarig-trade-phase-5) |
| Roamers and Fast Balls (Phase 6) | `-m phase6` | [Contracts and limits](coverage.md#roamers-and-fast-balls-phase-6) |
| Project Mew (Phase 7) | `-m phase7` | [Contracts and limits](coverage.md#project-mew-phase-7) |
| Silver's Kanto arc (Phase 8) | `-m phase8` | [Contracts and limits](coverage.md#silvers-kanto-arc-phase-8) |
| Kanto completion (Phase 9) | `-m phase9` | [Contracts and limits](coverage.md#kanto-completion-phase-9) |
| Giovanni and Cerulean Cave (Phase 10) | `-m phase10` | [Contracts and limits](coverage.md#giovanni-and-cerulean-cave-phase-10) |
| Red, Oak, and the true ending (Phase 11) | `-m phase11` | [Contracts and limits](coverage.md#red-oak-and-the-true-ending-phase-11) |
| Trainer and wild balance (Phase 12) | `-m phase12` | [Contracts and limits](coverage.md#trainer-and-wild-balance-phase-12) |

The Phase 1 file selection uses shell brace expansion. Markers are registered
in [pyproject.toml](../pyproject.toml); scenario and exact-data contracts live in
[fixtures/scenarios](fixtures/scenarios/) and [contracts](contracts/). Phases
8–11 retain their story contracts when Phase 12 numeric targets change.

## Battery-save and scenario fixtures

Committed `.sav` files under `tests/fixtures/saves/` are small,
emulator-independent battery saves, never emulator savestates. Each has an
adjacent JSON record with purpose, creation revision, ROM/save hashes,
deterministic player metadata, expected state, and reproduction steps. Runtime
tests copy the fixture and ROM into a pytest temporary directory; they verify
the canonical fixture hash after the run and must never mutate it in place.

Scenario contracts under `tests/fixtures/scenarios/` name production symbols
and constants rather than numeric ROM/RAM addresses. Test-only ROM scripts,
warps, save fields, and `_TEST` assembly paths are forbidden. State preparation
may establish a narrowly typed prerequisite, but the behavior being asserted
must execute production code through ordinary emulator input.

The [approved initialized save metadata](fixtures/saves/bedroom_initialized.json)
records the New Game → in-game Save reproduction procedure and empty progression
state. Test-created files must use pytest temporary directories or ignored
local artifact directories.

## Failure triage

Start with the first failed profile stage and preserve that boundary:

1. For a static failure, read the named source record and any exact exception
   contract. Do not add broad path or wildcard suppressions.
2. For a compiled-ROM failure, rebuild `crystallegends.gbc` and inspect the
   reported symbol, decoded bytes, header field, save-layout label, or linker
   budget. Source text alone is not evidence that the assembled contract is
   correct.
3. For an emulator timeout, use the reported ROM hash, PyBoy version, frame
   count, PC, recent symbolic hooks, map, coordinate, and script state to find
   the last completed boundary. Replace brittle timing with a stronger wait
   predicate when appropriate.
4. Re-run the smallest failing test with pytest's node ID, then its containing
   profile, then the aggregate gate. Keep mutable saves, screenshots, traces,
   ROMs, `.sym`, and `.map` outputs untracked.
5. If an approved battery fixture is genuinely stale, document the save-layout
   or scenario change and regenerate it through the normal game save path;
   never edit the fixture bytes casually.

PyBoy 2.6.0 (LGPL) is locked as a test-only dependency and is not linked into or
distributed with the ROM. Any upgrade must pass boot, fixture-load, and runtime
smoke scenarios before `uv.lock` changes.
