# Workflows

## First-time setup

1. Follow `INSTALL.md` for the host operating system.
2. Install RGBDS 1.0.3, the version pinned by `.rgbds-version` and CI.
3. Confirm `rgbasm`, `rgbgfx`, `rgblink`, `rgbfix`, `make`, and a C17 compiler
   are available on `PATH`.
4. Run `make` from the repository root.

The build compiles the local helpers in `tools/` automatically before scanning
assembly dependencies.

## Build and validate a change

1. Locate the subsystem through [repository-guide.md](repository-guide.md).
2. Read the relevant local command reference and neighboring source entries.
3. Edit source ASM, data, PNG, palette, or map files rather than ignored build
   products.
4. Build the smallest relevant target:

   ```bash
   make
   make crystal11
   make crystallegends
   make crystal_au
   make crystal_debug
   make crystal11_debug
   make crystal11_vc
   ```

5. If the linker reports a bank overflow, inspect the generated `.map` file and
   `layout.link` before moving sections.
6. Exercise the changed behavior in an emulator at its scheduled validation
   gate. Include save/load, map reload, battle transitions, or
   variant-specific paths when the change touches them.
7. Run `git status --short` and inspect the diff. Generated ROM, object, symbol,
   map, palette, tile, compression, and patch outputs must stay untracked.

For the current Crystal Legends sequence, the v0.1 path through Falkner, the
Phase 2 automated matrix, and the Phase 3 CHEAT MODE safety pass are complete.
Phase 4's Johto starter events are source-complete and pass their automated
source, ROM, and headless production-map matrices. Their user-owned presentation
matrix remains pending, so do not call Phase 4 playtest-certified yet.

## Validate the Crystal Legends build

From a clean graphics state:

```bash
make clean
make crystallegends
test -s crystallegends.gbc
test -s crystallegends.sym
test -s crystallegends.map
rgbfix -v crystallegends.gbc
make compare
git status --short
```

`make crystallegends` builds the project ROM from its own object family using
`_CRYSTAL11` and `_CRYSTALLEGENDS`. `make compare` checks only the untouched
reference variants and must continue to pass.

The complete local handoff gate now covers the legendary-bird starter paths,
Phase 2 evolution/item/Celebi behavior, Phase 3 CHEAT MODE, and Phase 4's three
production-map gifts. Rerun the narrower owning profile after a focused change
and `make test-all` at a milestone handoff. Four ordinary Crystal-missing
families remain reserved for the Phase 9 Safari Zone; Phase 5 makes Kim's Route
14 trade Girafarig's canonical source.

## Run the local automated test harness

The automated harness is opt-in and local to the development Mac. It does not
change the default `make` target or `.github/workflows/main.yml`. Install its
locked Python dependencies once, then use the narrowest useful profile:

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
RAM/SRAM state. These layers complement, but do not replace, the manual matrix
below.

### Validate the Phase 4 Johto starter events

Run the focused Phase 4 suites while editing, then the aggregate and clean
handoff gates:

```bash
uv run --frozen --group test pytest tests/static/test_phase_04_regressions.py
uv run --frozen --group test pytest tests/rom/test_phase_04_regressions.py
uv run --frozen --group test pytest tests/emulator/test_phase_04_gifts.py
uv run --frozen --group test pytest -m phase4
make test-crystallegends
make clean
make test-all
rgbfix -v crystallegends.gbc
git diff --check
git status --short
```

Automation owns the exact species, levels, map coordinates, prerequisites,
completion events, object visibility, party/current-box/full-capacity behavior,
retry and duplicate prevention, save/reload persistence, SecretPotion
non-consumption, unrelated story-state preservation, bank floors, and reference
isolation. Source completion means these gates pass; it does not certify the
presentation.

For playtest certification, use a backed-up or disposable save and record the
emulator/version, ROM commit and hash, date, preparation boundary, and result.
Manually confirm:

1. Chikorita's shrine placement, sprite, dialogue wrapping, discovery after Cut,
   and Ilex Forest flow feel natural.
2. Cyndaquil is absent before the beast release, appears cleanly in the same
   scene afterward, and its placement, sprite, dialogue, and choreography fit
   Burned Tower.
3. Totodile's east-shore placement and pharmacist hint are discoverable, its
   medicine story remains coherent before or after curing Amphy, and its sprite,
   dialogue, and Cianwood flow feel natural.
4. All three discoveries and levels feel appropriate in one normal Johto run,
   and a reference ROM shows none of the new objects, hint, or behavior.

Any presentation failure must be fixed and retested or explicitly assigned
before Phase 4 is described as playtest-certified or release-ready.

### Battery-save and scenario fixtures

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

### Failure triage

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

PyBoy 2.6.0 is locked as a test-only dependency and is not linked into or
distributed with the ROM. Any upgrade must pass boot, fixture-load, and runtime
smoke scenarios before `uv.lock` changes.

## Manual validation record — 2026-08-10

The user manually tested the Crystal Legends ROM at commit `5ec915ce1`
(SHA-256 `7c47f8352e3f4ca17a48857d8da4a03ffdd0e81ca88be63215e22b72a9acb55b`).
The exact emulator/version was not supplied. Three independent starter paths
were exercised through Elm's post-break-in dialogue.

Passed:

- Crystal Legends title presentation;
- Articuno, Zapdos, and Moltres starter details and player learnsets;
- the correct Cherrygrove Silver bird in all three branches;
- both the permitted loss and win outcomes of the first Silver battle;
- the correct, one-time Elm/Oak third-bird handoff and remaining-ball behavior;
- CHEAT MODE entry, navigation, grants, reset/cancel behavior, capacity and
  failure variants, and story-state isolation.

Deferred by the user:

- the rest of the v0.1 path through Falkner and its save/reload smoke test;
- later player-bird balance and Silver encounters through the Indigo rematch;
- the complete Phase 2 evolution/item/Celebi matrix;
- full-game and no-cheat playthrough certification.

This is a partial consolidated-gate pass, not a full-game certification.

## Exercise CHEAT MODE safely

Use a Crystal Legends ROM and a disposable or backed-up save. In the player's
bedroom, inspect the TV twice consecutively. The first inspection
must say that a Nintendo 64 is connected to the TV; the second must show the
CHEAT MODE warning. Declining, exiting, another bedroom interaction, or a map
reload must restart the sequence without changing saved state.

After accepting the warning, verify these boundaries:

1. Every B press and explicit `BACK`/`EXIT` row returns safely without an
   unintended grant, stale window, freeze, music loss, or warp.
2. Every item label includes `x10`; each action grants exactly ten of only that
   item, reaches the correct pocket, persists after reload, and fails cleanly at
   pocket or stack capacity.
3. `MONEY` adds `100000`, saturates at `999999` without wrapping, persists after
   reload, and never changes Mom's savings.
4. Eevee, Dratini, Larvitar, and Porygon arrive at level 5 with no held item,
   normal generated data, Pokédex registration, and nickname handling. A full
   party sends the gift to the current box; a full party and current box grants
   nothing and reports the failure.
5. Starter, badge, Hall of Fame, GS Ball/Celebi, legendary, and key-item state
   is identical before and after the complete menu pass. No story Pokémon,
   badge, key item, or generic selector may appear.
6. The bedroom TV works, all other bedroom interactions reset a partial
   sequence, the normal bedroom PC and decorations retain stock behavior, every
   other TV retains stock text, and a reference ROM exposes no CHEAT MODE
   trigger.

Record the emulator/version, ROM commit, date, save boundary, actions used, and
pass/fail result. Run this safety pass first, then the v0.1 and Phase 2 matrices
above. A CHEAT MODE gift must never substitute for a starter, rival, evolution,
or canonical acquisition test.

## Verify the upstream baseline

Use this to verify that the reference variants still reproduce the original
ROMs exactly:

```bash
make compare
```

This builds all reference ROMs and the Virtual Console patch, then checks the
outputs against `roms.sha1`. Crystal Legends changes are isolated behind their
own build flag, so they must not make this target fail.

## Build only the local helper tools

```bash
make tools
```

The tools are C17 programs for include scanning, palette normalization,
graphics transforms, LZ compression, Pokémon animation data, PNG dimensions,
Virtual Console patch generation, and Stadium 2 checksums.

## Clean build outputs

Remove ROMs, symbols, maps, patches, objects, and compiled helper programs:

```bash
make tidy
```

Also remove generated graphics intermediates:

```bash
make clean
```

Both targets preserve the hand-written ASM/data, source PNGs, palettes, and map
layouts.

## Evaluate an upstream tutorial or branch

1. Record the tutorial URL and its expected base revision.
2. Find each referenced path locally; do not assume upstream `master` still
   matches the tutorial.
3. Read the defining constants/macros, data table, engine consumer, and bank
   placement around the proposed change.
4. Reimplement the behavior as a focused local change.
5. Build and test before combining it with another tutorial or branch.

Avoid pulling feature branches directly into the working branch unless their
history and compatibility have been reviewed.
