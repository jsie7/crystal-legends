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
Phase 5's Ruins gifts and Route 14 Girafarig trade are likewise source-complete:
their automated dual-gate, delivery, trade, and persistence matrices pass, while
their user-owned presentation and natural puzzle-flow review remains pending.
Phase 6 is source-complete: preservation tests cover stock Raikou/Entei roaming
and Pokédex route tracking, and the custom Fast Ball scan covers all 23 stock
fleeing-list species. Its user-owned hunt and presentation review remains
pending.
Phase 7 is source-complete: its story buildup, four-fact state model, permanent
Mew/Mewtwo terminal decision, optional level-30 capture, retry paths, and stock
Radio Tower resume pass all automated layers. Its user-owned story, map, pacing,
and branch-feel review remains pending.
Phase 8 is source-complete: all three Mt. Moon-to-Elm release branches,
species-specific availability state, bird-free Indigo rematch, and Dragon's
Den chronology pass every automated layer. Its user-owned presentation,
discoverability, and provisional balance review also passed on 2026-08-19, so
Phase 8 is playtest-certified.
Phase 9 is source-complete: all three level-28 Kanto service gifts, the
Soul Badge-gated unattended Safari preserve, and both branch-correct
non-starter birds pass every automated layer and the combined single-save
flow. Its user-owned starter, Safari, bird-route, dialogue, palette, and
provisional-balance review remains pending.

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
Phase 2 evolution/item/Celebi behavior, Phase 3 CHEAT MODE, Phase 4's three
production-map gifts, Phase 5's three Ruins gifts and Route 14 Girafarig trade,
Phase 6's roamer/Fast Ball contracts, and Phase 7's Project Mew story and
branching encounter, Phase 8's Silver release and post-release chronology, and
Phase 9's Kanto gifts, Safari preserve, and world birds. Rerun the narrower
owning profile after a focused change and `make test-all` at a milestone
handoff. Phase 5 keeps Kim's Route 14 trade as Girafarig's canonical source;
Phase 9 deliberately adds no wild Girafarig.

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

### Validate the Phase 5 Ruins gifts and Girafarig trade

Run the focused Phase 5 suites while editing, then the aggregate and clean
handoff gates:

```bash
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_phase_05_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/rom/test_phase_05_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/emulator/test_phase_05_gifts.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/emulator/test_phase_05_trade.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest -m phase5
make test-crystallegends
make clean
make test-all
rgbfix -v crystallegends.gbc
git diff --check
git status --short
```

Automation owns the exact picture-plus-hidden-condition gates, early-condition
state, species, levels, coordinates, visibility, party/current-box/full-storage
delivery, retry and duplicate prevention, combined-save and save/reload
persistence, stock item independence, Kim trade metadata, bank floors, and
reference isolation. It deliberately does not replay every sliding-tile puzzle,
Bag Escape Rope action, Flash field-move menu, or natural Water Stone pickup.

For playtest certification, use a backed-up or disposable save and record the
emulator/version, ROM commit and hash, date, preparation boundary, and result.
Manually confirm:

1. In the Kabuto chamber, use Escape Rope before solving the picture. Confirm
   the wall and scientist dialogue remain closed/coherent, then solve the
   picture and verify the remembered Rope condition opens the wall without a
   second Rope use. Continue through the stock item room into the word room.
   Confirm Kabuto follows the final Unown glyph at `(10, 8)` like a period,
   then review its palette, bounce, cry, dialogue, and level-10 reward.
2. In the Omanyte chamber, carry a Water Stone before solving the picture.
   Confirm the Stone is retained and the wall stays closed, then solve the
   picture and verify the remembered condition opens the wall. Continue into
   the word room and confirm Omanyte follows the final glyph at `(15, 10)`,
   then review its presentation and level-26 reward. Repeat the prerequisite
   with a Water Stone held by a party Pokémon.
3. In the Aerodactyl chamber, use Flash before solving the picture. Confirm the
   wall stays closed, then solve the picture and verify the remembered Flash
   condition opens it without a second use. Continue into the word room and
   confirm Aerodactyl follows the final glyph at `(16, 8)`, then review its
   presentation and level-23 reward.
4. In every word room, decline once, claim with normal capacity, and re-enter.
   Confirm the Pokémon waits after decline, stays absent after success, never
   blocks the inscription or fall tile, and uses clean non-fossil dialogue.
   Confirm each preceding item room still contains all four stock rewards.
   Judge levels 10/26/23 in a normal run.
5. Confirm the Ho-Oh chamber and hidden room remain stock. On Route 14, trade a
   Chansey to Kim and verify a same-level Girafarig named `GIRAFY` holding a
   Gold Berry arrives. Confirm the trade and Aerodactyl gift do not complete one
   another; in a reference ROM, confirm Kim still offers `AEROY` the Aerodactyl
   and none of the three new room gifts or gates appears.

Any visual, pacing, navigation, or narrative failure must be fixed and retested
or explicitly assigned before Phase 5 is described as playtest-certified or
release-ready.

### Validate Phase 6 roaming and Fast Balls

Run the focused Phase 6 layers while editing, then the clean handoff gate:

```bash
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_phase_06_roamers.py
make crystallegends
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/rom/test_phase_06_roamers.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/emulator/test_phase_06_roamers.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest -m phase6
make compare
make clean
make test-all
rgbfix -v crystallegends.gbc
git diff --check
git status --short
```

Automation owns the stock release slots, seven-byte save state, 16-route graph,
land/water encounter boundary, Pokédex Area route updates, HP/DV persistence on
flee, permanent slot removal after defeat or capture, and native save/reload.
It also proves that the custom Fast Ball branch reaches every one of the 23
stock fleeing-list species with 4x saturation, leaves a Route 37 control
unchanged, remains size-neutral, and does not alter reference ROMs. No battle
status condition is persisted, and no defeat-recovery path exists.

For manual acceptance, use a backed-up or disposable save and record the
emulator/version, ROM commit and hash, date, save boundary, routes used, and
result. Confirm:

1. After seeing each beast, its normal Pokédex Area screen communicates the
   current Johto route clearly enough to support a hunt without another tracker.
2. Same-route grass encounters, fleeing, later re-encounters, and changing route
   indicators feel coherent; water and a different route never imply a false
   encounter.
3. Fast Ball selection, animation, messages, and perceived usefulness feel
   correct against Entei, while an ordinary Route 37 encounter feels unchanged.
4. Defeating or catching either beast removes it permanently with no recovery
   prompt or replacement, including after save/reload and ordinary travel.
5. Suicune's Burned Tower, Cianwood, Eusine, and Tin Tower sequence still feels
   entirely stock.

For a Phase 6 failure, first isolate its owning layer. Static failures usually
mean the guarded branch, exact fleeing table, route graph, or stock preservation
contract changed. ROM failures require checking the decoded `jr nz` target,
the single expected custom/reference byte difference, bank 3 headroom, and
save-layout fingerprint. Emulator failures should be triaged from the last
symbolic hook and current map/battle state; do not add gameplay code to make a
test deterministic.

The automated pass makes Phase 6 source-complete, not playtest-certified or
release-ready. Any tracker clarity, presentation, or hunt-feel issue must be
fixed and retested or explicitly deferred.

### Validate Phase 7 Project Mew

Run the focused Phase 7 layers while editing, then the clean handoff gate:

```bash
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_phase_07_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/rom/test_phase_07_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/emulator/test_phase_07_project_mew.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest -m phase7
make test-crystallegends
make clean
make test-all
rgbfix -v crystallegends.gbc
git diff --check
git status --short
```

Automation owns the Slowpoke Well, Lake of Rage, Mahogany, and Radio Tower
story ordering; reference-build isolation; the annex layout, custom boundary,
and collision; its one-step north-facing entry, one-time seal, unresolved 5F
return, and save/reload persistence; both southern controls; the conditional
glass observation; cancellation keeping the glass and exit closed; both
permanent terminal outcomes opening them together; the data-sent, resolved,
transformed, and caught facts; level-30 encounter identity; successful capture;
fresh retries after knockout or escape; player defeat; and resuming the stock
Director/Clear Bell cleanup without requiring capture.

For manual acceptance, use a backed-up or disposable save and record the
emulator/version, ROM commit and hash, date, preparation boundary, selected
branch, and result. Confirm:

1. Slowpoke Well hints at biological research without prematurely naming Mew,
   and the Lake of Rage extension strengthens rather than replaces its story.
2. Mahogany's scientists, both sides of the office workstation, all four lab
   computers, and the transmitter make the single captive subject and Goldenrod
   transfer understandable without feeling repetitive.
3. Entry faces north and takes only one automatic step before the passage
   audibly seals. In the first settled frame, confirm the complete compact room
   reads clearly: both southern controls, continuous center glass, captive
   subject, and entry. The subject must be visible but unreachable before a
   decision, and cancellation must leave both controls usable without trapping
   the player permanently.
4. REVERSE SEQUENCE and STABILIZE SEQUENCE clearly communicate a permanent
   Mew/Mewtwo decision before confirmation. Confirm the center glass and exit
   open together, the route to the selected subject is obvious, and each
   branch's reveal feels coherent.
5. Capture, knockout, escape, player defeat, save/reload, and leaving without
   capture all feel natural; the resumed Director/Clear Bell sequence occurs
   once and remains recognizably stock.

For a Phase 7 failure, first isolate source ordering and custom guards, then the
compiled scene/map/event tables and bank floors, then the last emulator hook and
current map/script state. Do not add save migration, a second subject, a
capture requirement, or test-only gameplay code to repair a scenario.

The automated pass makes Phase 7 source-complete, not playtest-certified or
release-ready. Dialogue, presentation, pacing, and branch-feel issues must be
fixed and retested or explicitly deferred.

### Validate Phase 8 Silver's Kanto arc

Run the focused Phase 8 layers while editing, then the clean handoff gate:

```bash
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_phase_08_regressions.py
make crystallegends
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/rom/test_phase_08_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/emulator/test_phase_08_silver_arc.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest -m phase8
make test-crystallegends
make clean
make test-all
rgbfix -v crystallegends.gbc
git diff --check
git status --short
```

The scenario helper copies the approved initialized battery save into pytest
temporary storage and edits only symbolically resolved state. Automation owns
all three Mt. Moon selectors, victory and loss, pending native save/reload, the
three automatic lab scenes, branch-correct name and cry, choreography and
walkable paths, availability isolation, mutation order, actor removal, replay
prevention, and ordinary later Elm interaction. It also owns both
Monday/Wednesday Indigo entrances, the five-member bird-free party, Champion
music, weekly lockout and persistence, Tuesday/Thursday Dragon's Den visibility
and repeat dialogue, the Dragon Shrine elder route, save-layout and bank
floors, and complete reference isolation.

For manual acceptance, use a backed-up or disposable save and record the
emulator/version, ROM commit and hash, date, branch, preparation boundary, and
result. Confirm:

1. For each player starter, win and lose at Mt. Moon, verify Silver's matching
   level-60 bird, and judge the provisional roster balance and post-victory
   direction back to Elm.
2. Save while the return is pending, travel naturally to New Bark Town, and
   review the complete lab scene: object placement and palettes, dialogue
   wrapping and voice, branch-correct cry, bird look-back, both exit paths,
   post-scene lab interactions, re-entry, and save/reload.
3. After release, play one natural Monday or Wednesday Indigo rematch. Confirm
   Champion music, five non-legendary Pokémon with Crobat as the ace, coherent
   unchanged dialogue, and the native weekly lockout after victory.
4. Visit Dragon's Den on Tuesday or Thursday, confirm both unchanged training
   lines and the elder hint, then verify Silver is absent on an excluded day.
5. Confirm Phase 8 never places a released bird for capture and does not move
   Oak's third bird; those are Phase 9 boundaries.

For a Phase 8 failure, first isolate exact source dialogue, branch mapping,
custom guards, and geometry; then inspect the compiled scene pointer, object
table, far jump, event bytes, party records, save fingerprint, and bank floors.
For emulator failures, use the last hook plus map, coordinate, script mode,
release/availability facts, weekday, and weekly flag. Do not add test-only
warps, save migration, party-derived state, or a physical bird encounter to
repair a scenario.

Manual acceptance passed on 2026-08-19 after the final Elm's Lab presentation
fixes. The user verified all three Mt. Moon/lab branches, loss/retry and normal
return travel, the natural Indigo rematch, the Dragon's Den cameo, and the
Phase 8/Phase 9 boundary in SameBoy. The exact SameBoy version was not supplied.
Evidence applies to ROM commit `0e73807d2`, SHA-256
`a5c2b67aaad42b1f3f06290bd40da6204c98279b7a037e0e14549cdd5fcc26f9`.
Phase 8 is therefore playtest-certified; Silver's full balance pass remains
separate Phase 12 work.

### Validate Phase 9 Kanto completion

Run the focused Phase 9 layers while editing, then the clean handoff gate:

```bash
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_phase_09_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/rom/test_phase_09_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/emulator/test_phase_09_kanto_completion.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest -m phase9
make test-crystallegends
make clean
make test-all
rgbfix -v crystallegends.gbc
git diff --check
git status --short
shasum -a 256 crystallegends.gbc
```

The accepted automated boundary on 2026-08-20 is:

- implementation commits `22a79cb05`, `561e1e8d4`, `0cabf0395`, and
  `dca936fe9`, followed by hardening commit `4723464c0`;
- 106 focused Phase 9 tests: 19 static, 16 compiled-ROM, and 71
  production-ROM emulator cases;
- 409 complete-gate tests: 108 static, 64 compiled-ROM, and 237 emulator cases;
- all six upstream reference artifacts reproduced by `make compare`;
- ROM SHA-256
  `c136026e9693f025ff4e6919ad781e2942fd7aea05dd726db9519da76289b9de`;
- event IDs 2015 through 2033 with `NUM_EVENTS`, WRAM, SRAM, and the save-layout
  fingerprint unchanged;
- reviewed Phase 9 bank reserves: ROMX `$06=$0202`, `$1c=$06b7`,
  `$1d=$0cce`, `$2c=$249a`, `$62=$0646`, `$65=$0653`, `$66=$052f`,
  `$6a=$01fa`, `$6b=$1310`, and `$6c=$1640`.

Automation owns exact gift prerequisites and level-28 delivery, decline/full
storage retry, service isolation, the Cinnabar log and staircase, both Safari
access orders, visible gate collision, pickups, complete grass/water tables,
normal battle rules, Seafoam sliding and round trip, the Power Plant shutter
and annex round trip, the complete three-branch bird selector, Hall-of-Fame and
power gates, capture-only completion, non-capture retry, native Continue,
Oak-assistant hints, invalid no-choice states, and one evolving save that
collects all three gifts plus both non-starter birds. Static and compiled-ROM
contracts also own conditional asset bytes, geometry, bank floors, save layout,
and reference isolation.

For playtest certification, use SameBoy with a backed-up or disposable save and
record the exact version, ROM commit/hash, date, save boundary, starter branch,
and pass/fail result. Manually confirm:

1. For Erika, Misty, and Blaine, review the service request after the stock
   badge/TM flow; named dialogue and wrapping; confirmation, nickname, party
   and box delivery with the leader shown as OT; decline/full-storage retry;
   and natural repeat dialogue.
   Confirm Erika's request makes Muk trigger when entering each of the pond's
   three northern water tiles, with run/loss retry; Misty's power hint works in
   either order; and the survivor clue, visible gray Cinnabar staircase,
   hidden rubble cache, log recovery, and return form one coherent task without
   an HM requirement. Explicitly judge level-28 Charmander's Ember-to-level-34
   Flamethrower interval.
2. Before and after the two Safari prerequisites, confirm Fuchsia's north
   opening looks closed/open rather than relying on an invisible wall. Review
   the reused empty beta gate, unattended wording, no clerk/fee/timer/Safari
   mechanics, ordinary Fight/Pack/Run behavior, entrance rediscovery, grass and
   water density, both visible item rewards, complete-map collision and escape,
   and morning/day/night readability.
3. On all three starter branches, confirm only Oak's and Silver's species
   appear. Review the recognizable compact Seafoam route and Articuno alcove;
   the Power Plant's red east shutter, permanent opening, industrial
   one-console annex, and brown Zapdos icon; and the complete Victory Road
   higher-floor loop, Full Restore bypass, approach tile, south return hops,
   and red Moltres icon after Hall of Fame. Confirm cry, name, species, level,
   and palette; verify that none of the three birds flees on its own and that
   the player's Run command still leaves a retryable encounter; then review
   capture disappearance, knockout/escape/loss retry, save/reload, and Oak's
   assistant hints.
4. Keep balance review provisional: the three starter rewards should be useful
   without replacing leader teams, level-60 birds should be catchable with
   ordinary late-game resources, and Safari levels should fit Kanto. Phase 12,
   not this review, owns the full Kanto/Silver/Red balance pass.

Phase 9 is source-complete but not playtest-certified until this SameBoy matrix
is reported and any presentation failure is fixed or explicitly assigned. The
automated evidence does not claim all 251 species, Phase 10 completion, a
full-game playthrough, or release readiness.

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
