# Playtest status and review — 2026-09-23

This is a dated evidence record. Use [project status](status.md) for current
acceptance and [manual playtesting](playtesting.md#recommended-next-playtests)
for the maintained priorities. The recommendations below are the September 23
snapshot.

The user confirmed that the Celebi sequence, Cyndaquil gift, Totodile gift,
Chikorita gift with Lucky Egg, Cerulean Cave/Giovanni, and Oak through the credits
all passed their prepared-checkpoint playtests after the reported fixes.
These results supersede the blanket presentation-pending status for those
flows. They do not establish a complete natural playthrough or every alternate
branch and failure case.

## Confirmed manual results

| Flow | Result | Evidence boundary |
|---|---|---|
| Celebi | Passed; the user described the sequence as working perfectly | Repaired checkpoint; Kurt's waiting bit was cleared manually. Natural overnight timing remains untested. |
| Cyndaquil | Passed after the sprite fixes | Gift presentation, including the reported Cyndaquil/Eusine graphics problem. This confirmation does not separately establish Lucky Egg delivery on this older checkpoint. |
| Totodile | Passed after the sprite fixes | Prepared gift encounter; natural discovery through the pharmacist clue is not separately reported. |
| Chikorita | Passed with Lucky Egg | The dedicated updated gift checkpoint, separate from the older Celebi ROM. |
| Cerulean Cave / Giovanni | Passed after the label fix | Tested cave/finale flow. Both Mew/Mewtwo branches, all entrance predicates, and every failure outcome were not individually reported. |
| Professor Oak | Passed through the credits | Prepared final-battle flow. Natural Red/240-caught progression, all three Oak teams, and post-ending save/Continue were not individually reported. |

The confirmation did not identify exact emulator versions or a final ROM hash
for each retest. Keep it as user-reported acceptance of the listed flows;
do not attribute every result to the current build. The earlier
[Celebi record](history/validation.md#celebi-follow-up--2026-09-23) retains its specific
ROM provenance. Earlier title, starter, CHEAT MODE, Falkner, and complete
Phase 8 story acceptance remain valid within their recorded boundaries.

## Code and regression review

Reviewed the fork against upstream commit `8e8f7e200`, using working source at
`98c8a5904` plus the existing, uncommitted Oak text-bank correction. No game
code was changed for this review. The audit covered the changed engine paths,
map/story state machines, gift transactions, acquisition/evolution data,
trainer and wild contracts, graphics-loading changes, and build/save isolation.

The reviewed working build has no additional confirmed defect from this pass.
This is bounded review evidence, not proof that the game contains no bugs.

Validation completed successfully:

- `make test-all`: **642 passed** — 165 static, 93 compiled-ROM, and 384
  production-ROM emulator tests; the gate left the working-tree status unchanged.
- `make compare`, included in that gate: all six upstream reference artifacts
  matched their expected hashes.
- An additional source/symbol audit resolved 1,662 near script, movement, and
  text references across the 55 changed map ASM files with no bank mismatch.
  One generated stock door-loop label was outside this audit's literal-label
  parser; this was not a complete script disassembler.
- An additional dialogue audit checked 899 changed rows, expanding player/rival
  names, `#` and other text tokens, and the custom bird-name buffers. No row
  exceeded the standard 18-column width. Giovanni's current `BOSS GIOVANNI`
  and Oak's expanded `POKéMON PROF. OAK` also fit. This does not replace screen
  review of menus, arbitrary runtime text, or sprite/palette presentation.
- Save-layout contracts, event allocations, trainer record boundaries, map
  geometry, and guarded linker reserves passed in the full suite.

Reviewed ROM SHA-256:
`e62ceca29477cc382bca5d8d78ce81e4b48ac77c28fe352fe01e8c260a202200`.

| Area | Review and automated coverage | Remaining human evidence |
|---|---|---|
| Legendary starters / Silver / Oak handoff | Branch mapping, atomic gift delivery, release chronology, rematches, and persistence | Later natural progression and current balance across all three starters |
| Evolutions / Celebi | All ten replacement evolutions, item consumption, GS Ball gates, capture-only completion, blackout and storage retries | Evolution presentation, real overnight Kurt transition, natural acquisition |
| CHEAT MODE | Navigation, capacity, money saturation, grants and story-state isolation | Earlier manual pass exists; final no-cheat run must remain independent |
| Johto / Ruins / Kanto gifts | Independent flags, party/current-box delivery, storage failure, replay protection and native persistence; Johto held items and Kanto OT data | Natural discovery, Ruins puzzle flow, Kanto service flow, Lucky Egg progression impact |
| Roamers / stationary legends | Fast Ball scan, stock roamer persistence/removal, bird nonflee guard, capture/retry state | Hunt feel, capture difficulty, natural routes and alternate branches |
| Project Mew / Cerulean Cave | Permanent choice, annex return after blackout, Director continuation, derived cave gate, Giovanni outcome order and counterpart retries | Both linked branches played naturally, story clarity, late-game difficulty |
| Red / Oak | Exact unlock predicates, all teams, decline/loss/win, heal, credits routing, ordinary save/Continue and Red rematches | Natural unlock journey, remaining team variants and end-to-end ending persistence |
| Phase 12 balance | All 166 approved trainer records and 39 wild tables, real battle loading, recruitment/evolution checks | Difficulty, EXP economy, item use and team viability in ordinary play |

### Open findings and known behavior

1. **Resolved after review: Oak's existing fix was committed as `f1f94cb8c`.**
   The working build and prepared ROMs include `farwritetext` for
   the Pokédex introduction and ordinary goodbye in
   [Phase11Endgame.asm](../maps/Phase11Endgame.asm). Committed `98c8a5904` still
   uses near pointers to text in a different bank. A clean checkout of that
   revision therefore lacks the fix. The matching regression updates in
   [test_phase_11_regressions.py](../tests/rom/test_phase_11_regressions.py) were
   committed with the correction and its workflow note. At the original
   review boundary this was a known fixed-in-worktree defect, not a new failure
   of the reviewed ROM.
2. **Mew can end an encounter through its moves.** Neither Mew nor Mewtwo is
   on the stock random-flee lists, but the level-30 and level-70 Mew movesets
   contain Metronome. Teleport, Roar, and Whirlwind are not excluded from
   Metronome, and these normal wild battles do not impose a no-escape rule.
   The earlier deterministic emulator investigation reproduced Metronome into
   Teleport in both locations without setting the capture flag. Reinteraction
   remains possible. Mewtwo's authored encounter movesets contain no escape
   move. This is compatible with the current normal-wild/retry contract; making
   Mew unable to escape would be a separate behavior change. See
   [the annex](../maps/RadioTowerTransmitterAnnex.asm),
   [the cave](../maps/CeruleanCave.asm),
   [Metronome exclusions](../data/moves/metronome_exception_moves.asm), and
   [Teleport](../engine/battle/move_effects/teleport.asm).
3. **Older playtest packages are not all the same ROM revision.** The repaired
   Celebi package predates the Lucky Egg change, and the initial cave package
   predates the Giovanni label fix. Replacing a save does not update its ROM;
   updating a ROM does not add held items to already-received Pokémon. The
   premature outdoor Kurt was a prepared-save error, and unclaimed Chikorita
   beside the shrine was expected independent gift state. These observations
   do not establish current production-script defects. Future checkpoints
   should name their source revision/patches and ROM hash explicitly.
4. **Natural balance remains unverified after the Lucky Egg addition.** All
   three Johto gifts now provide transferable EXP-boosting items well before
   the cave reward. Exact-party tests and deliberately strong test teams
   cannot establish the resulting gym, League, or postgame difficulty.

## Recommended next playtests

The following are missing manual evidence, even where automated coverage
already passes. Use the procedures in [workflows.md](workflows.md), a matched
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
