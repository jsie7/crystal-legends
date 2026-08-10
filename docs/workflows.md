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

For the current Crystal Legends sequence, the optional CHEAT MODE implementation
is present and the consolidated Phase 3, v0.1, and Phase 2 emulator gate is due.
Continue to run the build and source checks below for every change, and do not
claim playtest certification until the consolidated gate passes.

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

Run the deferred v0.1 emulator matrix with a fresh save for Articuno, Zapdos,
and Moltres. Each branch must cover starter selection and reload, the Mr.
Pokémon visit, Silver's mapped bird, Elm's third-bird handoff, the lab reload
that removes the final ball, and progression through Falkner.

In the same pass, run the deferred Phase 2 matrix:

1. Evolve Kadabra, Machoke, Graveler, and Haunter at level 36; confirm level 35
   does not evolve them.
2. Evolve Poliwhirl, Slowpoke, Onix, Scyther, Seadra, and Porygon by directly
   using their canonical items. Confirm an incompatible target preserves the
   item and a successful evolution consumes exactly one.
3. Confirm King's Rock, Metal Coat, Dragon Scale, and Up-Grade can still be
   given as held items, retain their stock held behavior, and can be purchased
   repeatedly at Celadon Department Store 4F.
4. Confirm Water Stone still produces Poliwrath, King's Rock produces Politoed,
   level 37 still produces Slowbro, and King's Rock produces Slowking.
5. Enter Goldenrod Pokémon Center before Hall of Fame and receive no GS Ball;
   enter afterward and receive exactly one.
6. With a full Key Items pocket, confirm no receipt/Kurt state advances, then
   free a slot and receive the GS Ball normally.
7. Complete Kurt's native handoff and waiting step. At the shrine, test a
   knockout, escape where permitted, and box-full/non-capture result; reload
   and confirm the GS Ball and shrine prompt return after each failure.
8. Catch Celebi, save/reload, and confirm the shrine cannot create a duplicate.

Run the cheat-menu safety checks alongside both deferred matrices. The five
ordinary missing families have no Phase 2 encounter tests; they remain reserved
for the Phase 9 Safari Zone.

## Exercise CHEAT MODE safely

Use a Crystal Legends ROM and a disposable or backed-up save. In the player's
bedroom, inspect either half of the TV twice consecutively. The first inspection
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
6. Both TV tiles work, all other bedroom interactions reset a partial sequence,
   the normal bedroom PC and decorations retain stock behavior, every other TV
   retains stock text, and a reference ROM exposes no CHEAT MODE trigger.

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
