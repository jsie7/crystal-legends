# Manual playtesting

Use [project status](status.md) to choose outstanding work. These procedures
also support targeted regression checks; an accepted checkpoint flow need not
be repeated wholesale. Automated contracts and their limits are in the
[test guide](../tests/README.md).

## Prepare and record a run

1. Use a disposable or backed-up battery save and a matched production ROM.
   Record date, ROM commit plus any patches, SHA-256, emulator and exact version,
   and whether the save came from natural play or a prepared checkpoint.
2. Name the starter and Project Mew branches, prerequisite flags or story stage,
   badge and caught counts where relevant, and any artificial items, levels,
   RNG controls, or cleared timing bits. Use separate saves for irreversible
   choices or permanent roamer defeat.
3. Follow the applicable checklist. For persistence, use the in-game Save,
   reset/restart, and Continue path; an emulator snapshot is a different boundary.
   Exercise ordinary map exit/re-entry separately where specified.
4. Record each branch and outcome as passed, failed, or untested. Include a
   reproducible starting point and observed/expected behavior for failures;
   retain screenshots/audio when presentation is involved. Fix and retest an
   issue or explicitly assign/defer it before calling that scope accepted.
5. Append a dated record under [history](history/validation.md), then update the
   [status matrix](status.md). Keep missing emulator/ROM provenance explicitly
   unknown. Prepared results do not establish natural timing, discovery,
   difficulty, or full-game acceptance.

Run `shasum -a 256 crystallegends.gbc` from the repository root to record the ROM.
Replacing a save does not update its ROM. Updating a ROM does not retroactively
add held items to Pokémon already received.

## Feature checklists

- [Johto](playtesting/johto.md): legendary starters, evolutions/items/Celebi,
  CHEAT MODE, Johto and Ruins gifts, roamers, and Project Mew.
- [Kanto](playtesting/kanto.md): Silver's release arc, starter services,
  Safari preserve, and world birds.
- [Endgame and balance](playtesting/endgame.md): Cerulean Cave/Giovanni,
  Red/Oak/credits, and natural progression across all three starter branches.

## Recommended next playtests

The following are missing manual evidence, even where automated coverage
already passes. Use the checklists linked above, a matched
ROM/checkpoint pair, and an ordinary in-game save followed by reset/Continue
for persistence checks. Record the starter and Project Mew branches. A native
battery save and an emulator snapshot are different test boundaries.

### Highest priority: unplayed content and integration

1. **Project Mew, both choices from the final Rocket executive onward.** Read
   the Mahogany clues in context; enter the annex, cancel and decline before
   confirming, then try REVERSE and STABILIZE on separate saves. Leave the
   subject uncaught on one path and lose the subject battle on another; return
   through the tower stairs and complete the Director/Clear Bell sequence.
   Expect a permanent choice, usable exit, correct subject, and no story lock.
   Carry each branch forward to the opposite cave counterpart. Include a Mew
   escape/knockout and verify a fresh retry and eventual one-time capture.
2. **All three Kanto starter services on one save.** Do Erika's pond task,
   Misty's power-restoration reward, and Blaine's request → survivor clue →
   log → return. Vary the order of gym victories and services. Decline once;
   test a full party/current box, make room, and retry. Verify correct level-28
   Pokémon and leader OT, no duplicate reward, and no lost log or stuck quest.
3. **The two missing birds for every original starter branch.** Follow the
   hints naturally to Seafoam, the Generator Annex, and Victory Road. Check
   ice traversal, repair/authorization/shutter flow, and the League/Silver
   release gates. Knock out or run from a bird, return, catch it, then
   save/Continue and revisit. Expect exactly the two non-starter birds, no
   autonomous flee, and permanent absence only after capture.
4. **Safari preserve and Ruins rewards.** Unlock the Safari gate through the
   granddaughter and Janine in both visit orders, explore grass and water,
   and catch Mareep, Vulpix, Mankey, and Remoraid using normal battles. Complete
   each of the three Ruins picture/hidden-wall sequences without preset flags;
   collect all three gifts and do Kim's Chansey-for-Girafarig trade. Expect
   understandable clues, reachable rewards, normal exits, and no duplicates.

### Focused follow-ups to successful tests

5. **Kurt across a real day change.** Start before giving him the GS Ball,
   hand it over, check same-day waiting, save and close the emulator, then
   resume after its RTC has advanced to the next day. Expect exactly the
   appropriate indoor/outdoor Kurt, the restless-forest transition, and the
   working shrine sequence. Do not clear the wait bit or use the advance-day
   helper for this test. Include an apricorn job nearby to check the shared
   daily behavior.
6. **Items, evolutions, and real roamer hunting.** Exercise all ten replacement
   evolution paths through the normal party/Pack UI, plus an incompatible
   item and a cancelled level evolution. Buy replacement items in Celadon.
   Receive a Johto gift with a full party, withdraw it from the PC, take/give
   its Lucky Egg, and save/Continue. Hunt Raikou/Entei using Pokédex Area and
   Fast Balls; check retained damage after fleeing and unchanged Suicune
   progression. Stock roamer KO is intentionally permanent, so use a separate
   save if testing that outcome.
7. **Oak boundaries and persistence, without repeating only the winning fight.**
   Compare 239 versus 240 caught, before versus after Red; decline, lose, and
   retry. Review whichever original-starter Oak teams were not played. After
   victory and Pallet return, save normally, reset, and Continue; Oak should
   stay completed. Defeat the League again and rematch Red; his credits should
   return to Mt. Silver. This closes gaps outside the accepted Oak-to-credits
   checkpoint.

### Final acceptance

8. **Natural progression with the new item economy.** Play from New Game
   without CHEAT MODE or artificial levels, collecting the three Johto gifts
   normally. Track four- and six-member team levels, Lucky Egg use, losses,
   healing-item use, and grinding at the later Johto gyms, League, Silver,
   Kanto leaders, Giovanni, Red, and Oak. Use targeted runs for the other bird
   starters. Complete one uninterrupted story save and one natural
   251-species collection, including breeding, evolutions, and time-dependent
   encounters. These remain the strongest checks for interacting story flags,
   sustainable recruitment, and the intended difficulty curve.

Phase 13 polish and full-game acceptance remain open. Successful checkpoint
playtests should not be repeated wholesale; concentrate on the untested
content, branches, real-time behavior, and integration boundaries above.
