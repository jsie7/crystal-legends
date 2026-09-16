# Crystal Legends automated tests

The tests validate the production `crystallegends.gbc` build at three levels:
checked-in source and data, compiled ROM contracts, and short headless emulator
scenarios. They do not replace manual visual, audio, balance, or full-playthrough
acceptance.

The harness requires Python 3.10 or newer (`zip(..., strict=True)` is used by
the validation helpers). Install the locked local test environment:

```bash
uv sync --frozen --group test
```

Run the source-only suite:

```bash
make test-static
```

Run the aggregate source/build/ROM gate:

```bash
make test-crystallegends
```

`make test-crystallegends` includes the short headless emulator smoke profile.
`make test-all` additionally runs every implemented emulator scenario and the
upstream reference comparison.

For the profile matrix, battery-fixture policy, and failure-triage procedure,
see [`docs/workflows.md`](../docs/workflows.md#run-the-local-automated-test-harness).

The headless profile uses the test-only PyBoy 2.6.0 dependency under the LGPL;
it is not linked into or distributed with the ROM. Update its lock only after
the boot smoke and fixture-load scenarios pass.

Test-created files must use pytest temporary directories or an ignored local
artifact directory. Never mutate an approved fixture in place.

The approved `tests/fixtures/saves/bedroom_initialized.sav` fixture was created
through New Game and the in-game Save command. Its adjacent JSON records the
source revision, ROM and save hashes, deterministic player data, expected empty
progression state, and reproduction procedure. Runtime tests copy it beside a
temporary ROM before boot and verify that the canonical file's hash is
unchanged afterward.

The Phase 2 regression profile automates all ten single-player evolution
results, item consumption/rejection, the renewable-item tables, and the
Hall-of-Fame through Celebi state machine, including retry-state persistence
after losing, completing the blackout, and native Save/restart/Continue.
Manual acceptance remains the source of truth for evolution and capture
animation quality, item-menu wording and feel, held-item effects during
representative battles, Celebi presentation, and long-form progression or balance.

The Phase 3 profile exhaustively drives the current CHEAT MODE action allowlist,
both Back mechanisms, pocket and storage capacity, money saturation, duplicate
gifts, story-state isolation, and native save/reload persistence. The retained
user-run manual pass remains separate evidence for text/layout quality, cursor
feel, music and graphics cleanup, and bedroom-PC or decoration presentation.

The Phase 4 profile owns the Chikorita, Cyndaquil, and Totodile production-map
gift state machines. Persistence covers native Continue and fresh map loads
separately, including Cyndaquil's immediate reveal and return through the tower.
Its static, compiled-ROM, capacity, retry, persistence, and
story-isolation checks do not certify placement, dialogue, choreography, or
story feel.

Run the focused Phase 5 profile with:

```bash
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_phase_05_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/rom/test_phase_05_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/emulator/test_phase_05_gifts.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/emulator/test_phase_05_trade.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest -m phase5
```

Phase 5 has 53 focused tests: 14 source contracts, 11 compiled-ROM contracts,
27 production-map gift scenarios, and one production-ROM Route 14 trade
scenario. They own the picture-plus-wall gates, three retry-safe gifts, exact
levels 10/26/23, combined-save behavior, Girafarig trade fields and inherited
level, native Continue and fresh map loads, one-time completion after ordinary
room exit/re-entry, stale-object rejection, bank budgets, and complete
reference isolation. The user-owned manual matrix in
[`docs/workflows.md`](../docs/workflows.md#validate-the-phase-5-ruins-gifts-and-girafarig-trade)
owns natural puzzle/item/field-move flow, sprite and palette appearance,
dialogue wrapping, navigation, pacing, and story feel.

Run the focused Phase 6 profile with:

```bash
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_phase_06_roamers.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/rom/test_phase_06_roamers.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/emulator/test_phase_06_roamers.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest -m phase6
```

Phase 6 has 25 focused tests: seven source contracts, five compiled-ROM
contracts, and 13 production-ROM scenarios. They preserve stock Raikou/Entei
release, routing, Pokédex tracking, flee HP/DVs, and permanent defeat/capture
removal while proving the custom-only Fast Ball correction for all 23 stock
fleeing-list species and an ordinary Route 37 control. They do not add defeat
recovery or preserve battle status conditions. The user-owned manual matrix in
[`docs/workflows.md`](../docs/workflows.md#validate-phase-6-roaming-and-fast-balls)
owns tracker clarity, hunt feel, Fast Ball presentation, and Suicune continuity.

Run the focused Phase 7 profile with:

```bash
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_phase_07_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/rom/test_phase_07_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/emulator/test_phase_07_project_mew.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest -m phase7
```

Phase 7 has 39 focused tests: 16 source contracts, eight compiled-ROM
contracts, and 15 production-ROM scenarios. They own the story ordering,
four-fact state model, custom-only annex layout and boundary, one-step sealed
entry, southern controls, gated glass observation and opening, both permanent
outcomes, retry-until-captured encounter, save/reload behavior, stock Radio
Tower resume, save-layout size stability, and reference isolation. The
user-owned manual matrix in
[`docs/workflows.md`](../docs/workflows.md#validate-phase-7-project-mew) owns the
room's visual hierarchy, sound, dialogue wrapping, pacing, and branch feel.

Run the focused Phase 8 profile with:

```bash
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_phase_08_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/rom/test_phase_08_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/emulator/test_phase_08_silver_arc.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest -m phase8
```

Phase 8 has 41 focused tests: 12 source contracts, six compiled-ROM contracts,
and 23 production-ROM scenarios. They own all three Mt. Moon and lab branches,
loss and pending/completed save-reload behavior, exact release-state isolation,
custom lab objects and cross-bank scene entry, both Indigo entrances and the
five-member bird-free rematch, Champion music and weekly cadence, and the
Dragon's Den cameo and shrine hint across their accepted and excluded days.
Temporary checkpoints are derived from the approved initialized save; no new
committed save is required. The user-owned manual matrix in
[`docs/workflows.md`](../docs/workflows.md#validate-phase-8-silvers-kanto-arc)
owns travel discoverability, visual and audio presentation, dialogue pacing,
look-back readability, and provisional Silver balance.

Run the focused Phase 9 profile with:

```bash
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_phase_09_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/rom/test_phase_09_regressions.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/emulator/test_phase_09_kanto_completion.py
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest -m phase9
```

Phase 9 has 122 focused tests: 20 source contracts, 16 compiled-ROM contracts,
and 86 production-ROM scenarios. They own the three level-28 service gifts,
Cinnabar log flow and asset variants, both Safari access orders, exact wild
tables and normal battles, Seafoam/Power Plant/Victory Road geometry, the full
three-branch bird matrix, retry and native Continue behavior, Oak's tracker,
invalid-state hiding, bank floors, reference isolation, and one evolving-save
flow that obtains all three gifts and both non-starter birds. No new committed
save is required. The user-owned manual matrix in
[`docs/workflows.md`](../docs/workflows.md#validate-phase-9-kanto-completion)
owns visual presentation, dialogue wrapping, natural exploration and routes,
palette/icon readability, pacing, and provisional balance.
