# Workflows

Run commands from the repository root. Use the [repository guide](repository-guide.md)
to locate code, the [test guide](../tests/README.md) for automated profiles, and
[manual playtesting](playtesting.md) for presentation and natural-play checks.
[Project status](status.md) owns acceptance and remaining work.

## First-time setup

1. Follow [INSTALL.md](../INSTALL.md) for the host operating system.
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

For documentation-only changes, check local links and anchors, run
`git diff --check`, and run any existing test that parses the changed document.
Record gameplay validation only when that validation was actually performed.

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

Use the narrowest [automated profile](../tests/README.md#setup-and-profiles)
after a focused change and `make test-all` at a milestone handoff. Record the
ROM hash for manual handoffs and keep evidence in a dated report.

## Regenerate and validate the cave lab fixtures

See the [asset procedure](assets.md#regenerate-and-validate-the-cave-lab-fixtures) for reproduction, hashes,
and placement constraints.

## Giovanni standing sprite

See the [asset procedure](assets.md#giovanni-standing-sprite) for reproduction, hashes,
and placement constraints.

## Run the local automated test harness

See the [test guide](../tests/README.md) for installation, profiles, fixtures,
and failure triage. The following links retain earlier workflow entry points.

### Validate Elm's legendary starter gifts

[Automated coverage](../tests/coverage.md#legendary-starter-gifts-phase-1) ·
[Manual checklist](playtesting/johto.md#legendary-starter-gifts-phase-1).

### Validate the Phase 4 Johto starter events

[Automated coverage](../tests/coverage.md#johto-starter-gifts-phase-4) ·
[Manual checklist](playtesting/johto.md#johto-starter-gifts-phase-4).

### Validate the Phase 5 Ruins gifts and Girafarig trade

[Automated coverage](../tests/coverage.md#ruins-gifts-and-girafarig-trade-phase-5) ·
[Manual checklist](playtesting/johto.md#ruins-gifts-and-girafarig-trade-phase-5).

### Validate Phase 6 roaming and Fast Balls

[Automated coverage](../tests/coverage.md#roamers-and-fast-balls-phase-6) ·
[Manual checklist](playtesting/johto.md#roamers-and-fast-balls-phase-6).

### Validate Phase 7 Project Mew

[Automated coverage](../tests/coverage.md#project-mew-phase-7) ·
[Manual checklist](playtesting/johto.md#project-mew-phase-7).

### Validate Phase 8 Silver's Kanto arc

[Automated coverage](../tests/coverage.md#silvers-kanto-arc-phase-8) ·
[Manual checklist](playtesting/kanto.md#silvers-kanto-arc-phase-8).

### Validate Phase 9 Kanto completion

[Automated coverage](../tests/coverage.md#kanto-completion-phase-9) ·
[Manual checklist](playtesting/kanto.md#kanto-completion-phase-9).

### Validate Phase 10 Giovanni and Cerulean Cave

[Automated coverage](../tests/coverage.md#giovanni-and-cerulean-cave-phase-10) ·
[Manual checklist](playtesting/endgame.md#giovanni-and-cerulean-cave-phase-10).

### Validate Phase 11 Red, Oak, and the true ending

[Automated coverage](../tests/coverage.md#red-oak-and-the-true-ending-phase-11) ·
[Manual checklist](playtesting/endgame.md#red-oak-and-the-true-ending-phase-11).

### Validate Phase 12 trainer and wild balance

[Automated coverage](../tests/coverage.md#trainer-and-wild-balance-phase-12) ·
[Manual checklist](playtesting/endgame.md#trainer-and-wild-balance-phase-12).

### Battery-save and scenario fixtures

See the [test guide](../tests/README.md#battery-save-and-scenario-fixtures).

### Failure triage

See the [test guide](../tests/README.md#failure-triage).

## Manual validation record — 2026-08-10

See the [dated record](history/validation.md#manual-validation-record--2026-08-10).

### Falkner follow-up — 2026-09-16

See the [dated record](history/validation.md#falkner-follow-up--2026-09-16).

### Celebi follow-up — 2026-09-23

See the [dated record](history/validation.md#celebi-follow-up--2026-09-23).

### Combined playtest follow-up — 2026-09-23

See the [dated record](history/validation.md#combined-playtest-follow-up--2026-09-23).

## Exercise CHEAT MODE safely

See the [Johto checklist](playtesting/johto.md#cheat-mode-phase-3).

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
