# Automated feature coverage

Use the [test guide](README.md) for setup, profiles, fixtures, and common failure
triage. This page explains what the feature checks prove and their limits;
[manual playtests](../docs/playtesting.md) own presentation and natural play.
Recorded run totals and ROM provenance belong in [validation history](../docs/history/validation.md).

## Legendary starter gifts (Phase 1)

The production-map tests cover all three choices with an empty party, decline,
full party plus full current box, refusal preserved through native
Save/Continue, and retry after freeing one party or current-box slot. Verify
that refusal keeps every ball visible and all choice/story flags unchanged;
successful delivery sets only the chosen branch, advances Elm's directions,
and prevents taking a second starter. Synthetic storage setup skips filling
the destinations through CHEAT MODE; interactions and persistence use normal
game input. Compiled-ROM checks require delivery and its failure branch before
the choice event and receipt text. The profile also verifies the first Silver battle and one-time Elm/Oak
handoff for each branch. Dialogue presentation remains a manual check.

## Evolutions, items, and Celebi (Phase 2)

The Phase 2 regression profile automates all ten single-player evolution
results, item consumption/rejection, the renewable-item tables, and the
Hall-of-Fame through Celebi state machine, including retry-state persistence
after losing, completing the blackout, and native Save/restart/Continue.
Manual acceptance remains the source of truth for evolution and capture
animation quality, item-menu wording and feel, held-item effects during
representative battles, Celebi presentation, and long-form progression or balance.

## CHEAT MODE (Phase 3)

The Phase 3 profile exhaustively drives the current CHEAT MODE action allowlist,
both Back mechanisms, pocket and storage capacity, money saturation, duplicate
gifts, story-state isolation, and native save/reload persistence. The retained
user-run manual pass remains separate evidence for text/layout quality, cursor
feel, music and graphics cleanup, and bedroom-PC or decoration presentation.

## Johto starter gifts (Phase 4)

Automation owns the exact species, levels, map coordinates, prerequisites,
completion events, object visibility, party/current-box/full-capacity behavior,
held Lucky Eggs on all three gifts, retry and duplicate prevention,
save/reload persistence, SecretPotion
non-consumption, unrelated story-state preservation, bank floors, and reference
isolation. Source completion means these gates pass; it does not certify the
presentation.

Gift persistence tests exercise native Save/restart/Continue separately from
forced fresh map loads, for both party and current-box delivery. Both paths
must retain the Lucky Egg; full storage must leave existing held items unchanged.
Negative interactions inspect the live object and face
its position before pressing A. Cyndaquil and the Ruins gifts also cover actual
exit/re-entry warps after party and box delivery, plus a stale visible object's
refusal to grant an already completed gift. Only synthetic retargeted checkpoints
request `fresh_map=True` outside the explicitly named map-load regression cases.

The 2026-09-23 sprite fix reserves Cyndaquil's graphics throughout its hidden,
pending, and collected states, and registers Totodile in Cianwood's outdoor
graphics list. Emulator checks compare the loaded icon bytes with ROM artwork
and verify live object tile references and valid icon animation frames across
submenu redraws, native Save/Continue, collection, and fresh map loads. The
beast-release case begins
with native Continue and checks Eusine's graphics after a menu redraw. The
compiled-ROM contract verifies Cianwood's fixed table length and unchanged
entries, and confirms the replaced Tauros entry is unused by its outdoor maps.
Totodile uses the same fixed-facing Pokémon animation as the other gifts, so
approaching or talking to it cannot select nonexistent directional artwork.
These checks do not replace the [manual sprite/palette review](../docs/playtesting/johto.md#johto-starter-gifts-phase-4).

## Ruins gifts and Girafarig trade (Phase 5)

Automation owns the exact picture-plus-hidden-condition gates, early-condition
state, species, levels, coordinates, visibility, party/current-box/full-storage
delivery, retry and duplicate prevention, combined-save and save/reload
persistence, stock item independence, Kim trade metadata, bank floors, and
reference isolation. It deliberately does not replay every sliding-tile puzzle,
Bag Escape Rope action, Flash field-move menu, or natural Water Stone pickup.

## Roamers and Fast Balls (Phase 6)

Automation owns the stock release slots, seven-byte save state, 16-route graph,
land/water encounter boundary, Pokédex Area route updates, HP/DV persistence on
flee, permanent slot removal after defeat or capture, and native save/reload.
It also proves that the custom Fast Ball branch reaches every one of the 23
stock fleeing-list species with 4x saturation, leaves a Route 37 control
unchanged, remains size-neutral, and does not alter reference ROMs. No battle
status condition is persisted, and no defeat-recovery path exists.

For a Phase 6 failure, first isolate its owning layer. Static failures usually
mean the guarded branch, exact fleeing table, route graph, or stock preservation
contract changed. ROM failures require checking the decoded `jr nz` target,
the single expected custom/reference byte difference, bank 3 headroom, and
save-layout fingerprint. Emulator failures should be triaged from the last
symbolic hook and current map/battle state; do not add gameplay code to make a
test deterministic.

## Project Mew (Phase 7)

Automation owns the Slowpoke Well, Lake of Rage, Mahogany, and Radio Tower
story ordering; reference-build isolation; the annex layout, custom boundary,
and collision; its one-step north-facing entry, one-time seal, unresolved 5F
return, and save/reload persistence; both southern controls; the conditional
glass observation; cancellation keeping the glass and exit closed; both
permanent terminal outcomes opening them together; the data-sent, resolved,
transformed, and caught facts; level-30 encounter identity; successful capture;
fresh retries after knockout or escape; player defeat; and resuming the stock
Director/Clear Bell cleanup without requiring capture. Both ordinary 4F stairs
are covered for each resolved outcome while that cleanup is still pending.

For a Phase 7 failure, first isolate source ordering and custom guards, then the
compiled scene/map/event tables and bank floors, then the last emulator hook and
current map/script state. Do not add save migration, a second subject, a
capture requirement, or test-only gameplay code to repair a scenario.

## Silver's Kanto arc (Phase 8)

The scenario helper copies the approved initialized battery save into pytest
temporary storage and edits only symbolically resolved state. Automation owns
all three Mt. Moon selectors, victory and loss, pending native save/reload, the
three automatic lab scenes, branch-correct name and cry, choreography and
walkable paths, availability isolation, mutation order, actor removal, replay
prevention, and ordinary later Elm interaction. It also owns both
Monday/Wednesday Indigo entrances, the bird-free party (six members since
Phase 12), Champion
music, weekly lockout and persistence, Tuesday/Thursday Dragon's Den visibility
and repeat dialogue, the Dragon Shrine elder route, save-layout and bank
floors, and complete reference isolation.

For a Phase 8 failure, first isolate exact source dialogue, branch mapping,
custom guards, and geometry; then inspect the compiled scene pointer, object
table, far jump, event bytes, party records, save fingerprint, and bank floors.
For emulator failures, use the last hook plus map, coordinate, script mode,
release/availability facts, weekday, and weekly flag. Do not add test-only
warps, save migration, party-derived state, or a physical bird encounter to
repair a scenario.

## Kanto completion (Phase 9)

Automation owns exact gift prerequisites and level-28 delivery, decline/full
storage retry, service isolation, the Cinnabar log and staircase, both Safari
access orders, visible gate collision, pickups, complete grass/water tables,
normal battle rules, Seafoam sliding and round trip, the Power Plant shutter
and annex round trip, the complete three-branch bird selector, Hall-of-Fame and
power gates, capture-only completion, non-capture retry, native Continue,
Oak-assistant hints, invalid no-choice states, and one evolving save that
collects all three gifts plus both non-starter birds. Static and compiled-ROM
contracts also own conditional asset bytes, geometry, bank floors, save layout,
and reference isolation. The annex console matrix additionally owns Zapdos
present, captured, and starter-absent readings on both console tiles, while the
Oak-assistant matrix owns one generic hint when both targets remain.

## Giovanni and Cerulean Cave (Phase 10)

Automation owns exact map registration and blocks, Route 4/Cerulean alignment,
all access and badge boundaries, physical guard blocking, the native cave
round trip, object masks after load and Continue, remnant parties/ranges,
paired lab records, every item and capacity retry, wild/fishing tables,
Giovanni's complete trainer package, loss/victory state order and blackout, and
both counterpart species across knockout, escape, player loss, full storage,
capture, retry, and native Continue. The guard is deliberately derived by
writing its map-object sprite before visible object structs initialize; do not
replace that with `appear`/`disappear` on the eventless object.

## Red, Oak, and the true ending (Phase 11)

Automation owns Red's accepted Phase 12 party, loss/victory state order,
durable completion, rematch visibility, heal, credits, and Mt. Silver return.
It also owns Oak's exact `Red + at least 240 caught` truth table, multiple
240-species omission sets, all three starter-selected teams, invalid-state
protection, decline/loss retry, one-time victory, party heal, unchanged Hall of
Fame count, full credits, Pallet return, ordinary save/reload persistence, and
permanent completed dialogue. Static and compiled-ROM contracts additionally
own event IDs, reference isolation, trainer data, map/object preservation,
bank-local win/loss text, save layout, and linker floors. A short reference-ROM
runtime scenario confirms stock Oak rating and stock Red credits behavior.

Oak’s shared introduction and goodbye use `farwritetext` across banks.
Compiled-ROM checks verify the command, bank, and pointer; normal interaction
and battle scenarios exercise the flow.

## Trainer and wild balance (Phase 12)

The exact implemented scope and evidence are in [phase-12-balance.md](../docs/phase-12-balance.md).
The trainer and wild JSON contracts contain symbolic source IDs, complete
ordered targets and explicit preservation baselines. Update owning Phase 8–11
numeric expectations only when their accepted behavior actually changes.

The clean automated gate verifies all 166 trainer records, 149 branch-selected
battles in XP accounting, 39 changed wild tables, exactly 584 changed wild
level bytes, zero wild-data growth and exactly 252 added trainer bytes. Bank
$0e retains 826 bytes against a 768-byte floor. All six upstream reference
artifacts reproduce exactly and the save-layout fingerprint is unchanged.
Runtime cases use actual map scripts and encounter selection. Some use
prepared parties, RNG inputs or forced battle outcomes to test state changes;
these are correctness checks and provide no natural difficulty certification.
