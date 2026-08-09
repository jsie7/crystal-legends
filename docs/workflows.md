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

For the current Crystal Legends sequence, the v0.1 three-starter emulator
matrix is scheduled after the optional cheat/debug menu lands. Continue to run
the build and source checks below for every intervening change.

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

After the cheat/debug menu lands, run the deferred v0.1 emulator matrix with a
fresh save for Articuno, Zapdos, and Moltres. Each branch must cover starter
selection and reload, the Mr. Pokémon visit, Silver's mapped bird, Elm's
third-bird handoff, the lab reload that removes the final ball, and progression
through Falkner. Run the cheat-menu safety checks in the same pass.

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
