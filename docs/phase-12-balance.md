# Phase 12 balance

Phase 12 applies the approved trainer and Kanto encounter balance targets. The
implementation is incremental; the completed slices below describe current
behavior. Approval of the design and automated correctness are separate from
natural-play acceptance.

## Implementation status

Completed slices: A–C (contracts, Johto gyms and League).

| Slice | Scope |
| --- | --- |
| A | Freeze all 166 accepted trainer records and the full preservation baseline. |
| B | Eight Johto gym additions; Falkner's Pidgeotto 10; Morty's Gengar last. |
| C | Six-member Elite Four teams; preserve Lance. |
| D | Seven major Rocket parties. |
| E | Kimono Girls 20, Eusine 24–26, Kiyo 36, Wise Trio 34; preserve Elder Li. |
| F | Kanto gyms, thief 38 and daily Cal 55; preserve Blue. |
| G | Cave remnants 54–60, Giovanni 60–65 and Red's stock levels/softened moves. |
| H | Three Oak variants at 84/85/85/86/87/90. |
| I | Seven Silver stages in three branches; Crobat 52 only in the rematch. |
| J | 26 Kanto land and 13 surf encounter tables. |
| K | 93 ordinary Kanto records: gym +10/route +8 with geographic caps. |

The checked-in [trainer contract](../tests/contracts/phase_12_trainers.json)
contains exact ordered targets, accepted natural moves, the stock baseline,
custom baseline differences and implemented slices. Existing out-of-scope
records and all reference records are checked in source and assembled ROMs.
The complete trainer package adds 44 members across source variants and 252
bytes. The reviewed final bank reserve is 768 bytes, with 826 projected free.

## Boundaries

All edits remain conditional on `_CRYSTALLEGENDS`. Story progression, gifts,
legendary recruitment levels, save layout, player learnsets, stats, class AI,
DVs and items retain their prior contracts. Ordinary Johto, pre-League Routes
26/27 and shared S.S. Aqua parties remain unchanged. Cal stays once per day.

Trainer moves are approved. Kiyo and Colette are the only automatic-to-authored
format conversions. Wild natural-move questions and revised player-level
forecasts remain separate; optional recruits are not a balance requirement.

## Validation

Run focused source/ROM checks after each data slice:

```bash
make crystallegends crystal11
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_phase_12_regressions.py tests/rom/test_phase_12_regressions.py
```

Run the owning Phase 8–11 checks when changing their numeric targets. At final
integration, follow [the full workflow](workflows.md#run-the-local-automated-test-harness),
including `make test-all`, reference comparisons and bank/save-layout checks.
Natural-play review must separately sample all three starters, four- and
six-member parties, consecutive boss fatigue, captures and evolution timing.
No Phase 12 playtest certification has been recorded.

### Johto gym evidence

All 238 source/ROM checks and three production-map battle/reward scenarios
pass. The gym additions use exactly 48 bytes, leaving 1,030 bytes in bank $0e.
Prepared battle outcomes verify victory scripts; natural difficulty remains
a separate playtest gate.

### League evidence

The four six-member teams and their normal entrance, victory and exit-opening
scripts pass production-ROM checks. All seven focused data/bank checks pass;
Lance and reference party bytes remain exact. Combined gym/League growth is
72 bytes, leaving 1,006 bytes in bank $0e. The approved 768-byte final reserve
is now enforced.
