# Crystal Legends automated tests

The tests validate the production `crystallegends.gbc` build at three levels:
checked-in source and data, compiled ROM contracts, and short headless emulator
scenarios. They do not replace manual visual, audio, balance, or full-playthrough
acceptance.

Install the locked local test environment:

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
Hall-of-Fame through Celebi state machine. Manual acceptance remains the source
of truth for evolution and capture animation quality, item-menu wording and
feel, held-item effects during representative battles, Celebi presentation,
and long-form progression or balance.

The Phase 3 profile exhaustively drives the current CHEAT MODE action allowlist,
both Back mechanisms, pocket and storage capacity, money saturation, duplicate
gifts, story-state isolation, and native save/reload persistence. The retained
user-run manual pass remains separate evidence for text/layout quality, cursor
feel, music and graphics cleanup, and bedroom-PC or decoration presentation.

The Phase 4 profile owns the Chikorita, Cyndaquil, and Totodile production-map
gift state machines. Its static, compiled-ROM, capacity, retry, persistence, and
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

Phase 5 has 47 focused tests: 14 source contracts, 11 compiled-ROM contracts,
21 production-map gift scenarios, and one production-ROM Route 14 trade
scenario. They own the picture-plus-wall gates, three retry-safe gifts, exact
levels 10/26/23, combined-save behavior, Girafarig trade fields and inherited
level, save/reload persistence, one-time completion, bank budgets, and complete
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
