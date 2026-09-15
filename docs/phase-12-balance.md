# Phase 12 balance

Phase 12 applies the approved trainer and Kanto encounter balance targets. The
implementation is incremental; the completed slices below describe current
behavior. Approval of the design and automated correctness are separate from
natural-play acceptance.

## Implementation status

Completed slices: A–K. All approved gameplay/data changes are implemented;
the clean integration gate is pending.

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

### Rocket evidence

The seven accepted Rocket parties and their exact retained/new moves are
implemented. Fifty focused Phase 7/12 checks pass, including Project Mew upload,
loss, victory, annex and Director cleanup. Two additional normal-map scenarios
verify the Slowpoke Well leader and Radio Tower 4F executive. Growth is 112
bytes so far; bank $0e retains 966 bytes.

### Other Johto trials

The Kimono Girls, Eusine, Kiyo and Wise Trio now use their approved parties;
Elder Li is preserved. Source/ROM checks verify the 31-record Johto subtotal,
132-byte growth and pooled XP increase from 91,030 to 111,497. Kiyo loads all
three authored level-36 Hitmons and still grants level-10 Tyrogue through the
normal reward and nickname flow. Bank $0e retains 946 bytes.

### Kanto leader and training evidence

The seven changed leaders, thief and default Cal use their accepted parties;
Blue remains exact. All 133 focused Phase 9/12 checks pass, preserving starter
services and gifts. Added runtime checks verify Sabrina and Surge, plus Cal
55's exact natural moves, same-day refusal and unchanged saved-opponent bytes.
The trainer-bank increase is 188 bytes, leaving 890 bytes free.

### Cave and Red evidence

Cave remnants use 54–60 and Giovanni uses 60/61/62/63/64/65. Ross's Magneton
uses Screech and Giovanni's Kangaskhan uses Strength. Red returns to
81/73/75/77/77/77 with Swift, Amnesia, Slash and Bite replacing the four
approved moves. All 103 focused Phase 10/11/12 checks pass, including cave
access, crew cleanup, counterpart retries, Red rematches and ending behavior.
These edits add no bytes and preserve the level-70 counterpart.

### Oak evidence

All three Oak teams now use 84/85/85/86/87/90. Their existing moves,
branch mapping, class settings and Tyranitar ace remain intact. The focused
Phase 11/12 gate passes, including Red-plus-240-caught access, decline/loss
retry, one-time victory, credits, Pallet return and later Red rematches.

### Silver evidence

All 21 Silver records now use the approved seven-stage progression. His bird
levels are 5/16/22/32/40/50; Golbat remains through Mt. Moon. The bird-free
rematch is Sneasel 48, Magneton 48, Gengar 49, Alakazam 49, Ursaring 50 and
Crobat 52, with the ace last. All 58 focused checks pass, including all three
release branches, rematch entrances, weekly cadence and Dragon's Den cameo.
Named-trainer growth is exactly 248 bytes, leaving 830 bytes in bank $0e.

### Wild encounter evidence

All 26 land and 13 surf targets are implemented: exactly 545 land and 39 surf
level bytes change, with no added data. The [wild contract](../tests/contracts/phase_12_wild.json)
checks every Kanto record, original reference tables and unchanged habitats.
Forty-two focused wild checks cover source/ROM tables, time-dependent Diglett
slots, rare grass slots, natural moves, all five Safari surf variations, Repel,
and actual capture/evolution of Houndour 26→27 and Mareep 28→29→30 with
Ampharos learning ThunderPunch. Together with existing Phase 2 runtime checks,
59 tests pass. Existing Phase 9 habitat/service checks also retain their gates.

At these levels Chansey naturally has DoubleSlap/Minimize/Sing/Egg Bomb and
Remoraid 25–29 has Lock-On/Psybeam/Aurora Beam/BubbleBeam. No wild movesets
or global learnsets were changed. Further design changes to these sets and
updated player-level forecasts remain outside the accepted implementation.

### Ordinary Kanto evidence

All 93 records implement the fixed +10 gym/+8 route policy with geographic
caps. Species, counts and held items are preserved; Colette alone gains an
authored Clefairy 44 set with DoubleSlap replacing Minimize. Both Jo & Zoe
orders remain present and count as one battle. Twenty-seven focused checks
pass, including all representative trainer scenarios and Colette's normal
battle. The final measured growth is 252 bytes, leaving exactly 826 bytes
free in bank $0e, 58 above the approved reserve.

One branch-selected clear covers 149 listed battles from 166 source records.
The accepted pooled XP totals are 577,396 / 577,300 / 577,375 for Articuno /
Zapdos / Moltres, versus stock 397,101 / 397,042 / 396,628. These include
optional encounters and Oak's victory reward, exclude additional repeats and
wild KOs, and do not predict the player's readiness for those battles.
