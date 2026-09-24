# Phase 12 balance

This page owns the implemented trainer and Kanto encounter rules and their
preservation boundaries. [Project status](status.md) records acceptance;
[manual balance playtests](playtesting/endgame.md#trainer-and-wild-balance-phase-12)
cover the progression curve, including the later Johto Lucky Eggs.

## Implementation status

Completed slices: A–K. All approved gameplay/data changes are implemented and
the clean integration gate passes.

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
bytes. Bank $0e has 826 measured free bytes against the reviewed 768-byte
reserve, leaving 58 bytes of margin.

## Boundaries

All edits remain conditional on `_CRYSTALLEGENDS`. Story progression, gifts,
legendary recruitment levels, save layout, player learnsets, stats, class AI,
DVs and items retain their prior contracts. Ordinary Johto, pre-League Routes
26/27 and shared S.S. Aqua parties remain unchanged. Cal stays once per day.

Trainer moves are approved. Kiyo and Colette are the only automatic-to-authored
format conversions. Wild natural-move questions and revised player-level
forecasts remain separate; optional recruits are not a balance requirement.

## Encounter and XP contracts

The [wild contract](../tests/contracts/phase_12_wild.json) fixes 26 land and
13 surf targets: 545 land and 39 surf level bytes change, with no added data.
Species, habitats, encounter rates, wild movesets, and global learnsets remain
unchanged. Natural moves at the new levels are part of the contract.

One branch-selected clear covers 149 listed battles from 166 source records.
The pooled XP totals are 577,396 / 577,300 / 577,375 for Articuno / Zapdos /
Moltres, versus stock 397,101 / 397,042 / 396,628. They include optional encounters
and Oak's victory reward, exclude additional repeats and wild KOs, and do not
predict readiness for a boss. Player-level forecasts have not been refreshed.

## Validation

Use the [automated profile](../tests/README.md#focused-feature-checks) and
[coverage boundaries](../tests/coverage.md#trainer-and-wild-balance-phase-12).
Run the owning Phase 8–11 checks when changing their numeric targets and the
full gate at integration. Prepared parties and forced outcomes test state
transitions; natural play tests difficulty.

<a id="final-validation--2026-09-15"></a>
<a id="incremental-verification-record"></a>
<a id="johto-gym-evidence"></a>
<a id="league-evidence"></a>
<a id="rocket-evidence"></a>
<a id="other-johto-trials"></a>
<a id="kanto-leader-and-training-evidence"></a>
<a id="cave-and-red-evidence"></a>
<a id="oak-evidence"></a>
<a id="silver-evidence"></a>
<a id="wild-encounter-evidence"></a>
<a id="ordinary-kanto-evidence"></a>

The [September 15 integration and incremental record](history/phase-12-validation-2026-09-15.md)
preserves all slice results, ROM provenance, and bank measurements.
