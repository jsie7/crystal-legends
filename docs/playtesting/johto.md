# Johto playtests

Use the [common preparation and reporting procedure](../playtesting.md) first.
[Project status](../status.md) records which checks have already passed. These
are repeatable checklists, not a declaration that every scenario is untested.

## Legendary starter gifts (Phase 1)

Use independent saves for Articuno, Zapdos, and Moltres. Review the title,
choice text, starter details and player learnsets. Decline once and retry with
normal capacity, full party/current box, and one freed party or box slot.
Refusal must preserve the balls and story state; successful delivery must
prevent a second choice.

For each branch, review the matching Cherrygrove Silver bird, both first-battle
outcomes, and Elm/Oak's one-time third-bird handoff. Continue naturally through
Falkner and check ordinary Save/reset/Continue. Review later starter and rival
balance with the [endgame balance matrix](endgame.md#trainer-and-wild-balance-phase-12).

## Evolutions, items, and Celebi (Phase 2)

Use the [acquisition ledger](../pokemon-acquisition.md) and
[evolution contract](../../tests/contracts/phase_02_evolutions.json) to exercise
all ten replacement evolutions through the normal party/Pack UI. Check item
consumption, incompatible items, a cancelled level evolution, and renewable
purchases in Celadon. Review animation, wording, and held-item effects in
representative battles.

Follow the GS Ball sequence from its natural prerequisites through Kurt and
the shrine. Test same-day waiting and a real RTC day change, including an
apricorn job nearby; do not clear the waiting bit or advance the day with a
helper. Check dialogue, indoor/outdoor Kurt, the forest transition, shrine
presentation, capacity refusal, and capture, knockout, escape, and player-loss
retries. Use ordinary Save/reset/Continue to check persistence. A repaired
checkpoint does not establish natural timing.

## CHEAT MODE (Phase 3)

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

A CHEAT MODE gift must never substitute for a starter, rival, evolution, or
canonical acquisition test. Keep the final no-cheat run independent.

## Johto starter gifts (Phase 4)

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
5. Each gift holds a Lucky Egg. Check the held-item display, taking and giving
   the item, and the effect of the earlier EXP boost on the rest of the party.

Lucky Eggs are attached when the gifts are received. Updating the ROM does not
add items to starters already collected on an older build.

When testing a save created before the 2026-09-23 sprite fix, leave and re-enter
the affected map once to rebuild any already-stale object tile references, or use a fresh
playtest checkpoint. Gift completion and other story progress are preserved.

## Ruins gifts and Girafarig trade (Phase 5)

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

## Roamers and Fast Balls (Phase 6)

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

## Project Mew (Phase 7)

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
