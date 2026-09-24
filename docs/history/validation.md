# Validation history

These are dated reports, preserved within their original test and ROM boundaries.
Counts and bank space describe those runs, not the current checkout. See
[project status](../status.md) for current acceptance and [playtesting](../playtesting.md)
for the reporting procedure.

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

Deferred at the time of this report:

- the rest of the v0.1 path through Falkner and its save/reload smoke test;
- later player-bird balance and Silver encounters through the Indigo rematch;
- the complete Phase 2 evolution/item/Celebi matrix;
- full-game and no-cheat playthrough certification.

This is a partial consolidated-gate pass, not a full-game certification.

### Falkner follow-up — 2026-09-16

The user confirmed that progression through Falkner was completed manually.
This supersedes the Falkner progression deferral above. The confirmation did
not identify a ROM revision, emulator/version, or separate save/reload result;
it does not extend the original ROM-specific evidence or certify the later
Phase 12 balance changes. The remaining manual gates retain their own status.

### Celebi follow-up — 2026-09-23

The user reported that Celebi's sequence works perfectly in the repaired
Celebi playtest checkpoint. The supplied ROM was commit `edd1960da` plus the
recorded Oak text-bank patch, SHA-256
`c8d954b4b61b79023d526dd9605846b1063c3fa3fc7f0b7d1759fcc5df00c390`.
The checkpoint targets SameBoy; the exact emulator version was not reported.

Record the sequence presentation as passed. The prepared save's premature
outdoor Kurt was hidden and Kurt's waiting bit was cleared manually before
this confirmation, so natural next-day timing was not validated. Individual
capture-retry and capacity variants were not separately reported, and the
remaining Phase 2 evolution/item and full-game gates stay open.

Chikorita was unclaimed and Cut was already received in this independent save.
Its availability beside the shrine is expected. The supplied ROM predates the
Lucky Egg gift change, so this report does not validate the newer held items.

### Combined playtest follow-up — 2026-09-23

Asked which of Cyndaquil, Totodile, Chikorita with Lucky Egg, Cerulean
Cave/Giovanni, and Oak through the credits passed after the fixes, the user
confirmed: "they all passed". Record each as a successful prepared-checkpoint
playtest alongside Celebi. This includes the retested sprite and Giovanni
label presentation; Chikorita's dedicated Lucky Egg test is distinct from its
appearance in the old Celebi ROM.

The confirmation did not separately enumerate every starter/Project Mew branch,
failure outcome, or post-credits persistence check, and did not supply a final
ROM hash or emulator version for each retest. The
[review and remaining scenarios](../playtest-review-2026-09-23.md) distinguish
these confirmed successes from the remaining integration and natural-play
checks. Its automated review used the current working build, including the
existing Oak bank fix, and passed the complete 642-test gate and six reference
checks. No game code or user save was changed during that review.


## Silver story acceptance — 2026-08-19

Manual acceptance passed on 2026-08-19 after the final Elm's Lab presentation
fixes. The user verified all three Mt. Moon/lab branches, loss/retry and normal
return travel, the natural Indigo rematch, the Dragon's Den cameo, and the
Phase 8/Phase 9 boundary in SameBoy. The exact SameBoy version was not supplied.
Evidence applies to ROM commit `0e73807d2`, SHA-256
`a5c2b67aaad42b1f3f06290bd40da6204c98279b7a037e0e14549cdd5fcc26f9`.
Phase 8's story matrix is therefore playtest-certified. The later Phase 12
party changes pass automation and require their own natural-play balance
review; the earlier manual evidence does not certify those new teams.

## Phase 9 automated validation — 2026-08-22

The accepted automated boundary on 2026-08-22 is:

- Phase 9 implementation and presentation commits from `22a79cb05` through
  state-contract fix `007b8efd1`;
- 122 focused Phase 9 tests: 20 static, 16 compiled-ROM, and 86
  production-ROM emulator cases;
- 425 complete-gate tests: 109 static, 64 compiled-ROM, and 252 emulator cases;
- all six upstream reference artifacts reproduced by `make compare`;
- ROM SHA-256
  `76c64b48cf697c6a062575ae9efb2ecb2d75bd5dca2574e4ae127e2ee97b3960`;
- event IDs 2015 through 2037 with `NUM_EVENTS`, WRAM, SRAM, and the save-layout
  fingerprint unchanged;
- reviewed Phase 9 bank reserves: ROMX `$06=$01da`, `$1c=$06b1`,
  `$1d=$0cce`, `$2c=$249a`, `$62=$0649`, `$65=$0780`, `$66=$052f`,
  `$6a=$02be`, `$6b=$158d`, and `$6c=$160b`.

## Phase 10 automated validation — 2026-09-06

The accepted automated boundary on 2026-09-06 is:

- implementation and hardening commits `457379c48` through `efd589c6c`;
- 73 focused Phase 10 tests: 26 static, 16 compiled-ROM, and 31
  production-ROM emulator cases;
- 498 complete-gate tests: 135 static, 80 compiled-ROM, and 283 emulator cases;
- all six upstream reference artifacts reproduced by `make compare`;
- ROM SHA-256
  `e6485ac763c5c88a767f17df359b4c4e08b9e2ccd77fd79ebe0deeeaae090b64`;
- event IDs 261–267 and 1484–1490 with `NUM_EVENTS`, WRAM, SRAM, and the
  save-layout fingerprint unchanged;
- reviewed Phase 10 bank reserves: ROMX `$05=$0b34`, `$07=$0034`,
  `$0a=$02a6`, `$0e=$04b4`, `$24=$059b`, `$2a=$0055`, `$2b=$00a6`,
  `$2c=$23da`, `$4a=$0004`, `$59=$154a`, `$61=$18d5`, `$66=$04d8`,
  `$6b=$143f`, and `$6c=$0a81`.

## Phase 11 automated validation — 2026-09-07

The accepted automated boundary on 2026-09-07 is:

- implementation and hardening commits `857ccc289` through `0a9e0e9be`;
- 39 focused Phase 11 tests: 10 static, 7 compiled-ROM, and 22
  production-ROM emulator cases;
- 537 complete-gate tests: 145 static, 87 compiled-ROM, and 305 emulator cases;
- all six upstream reference artifacts reproduced by `make compare`;
- ROM SHA-256
  `43e50645d105a5020fd15d6d830304e2f4a59d359148f647face8583c4b9c7be`;
- event IDs 1491–1492 with `NUM_EVENTS`, WRAM, SRAM, and the save-layout
  fingerprint unchanged;
- reviewed Phase 11 bank reserves: ROMX `$0b=$104d`, `$0e=$0436`,
  `$21=$16fc`, `$22=$05dc`, `$63=$0bb0`, `$66=$046d`, `$6b=$1371`, and
  `$6c=$05cf`.

## Oak text-bank correction — 2026-09-19

The 2026-09-19 manual-bundle preparation exposed a bank mismatch in Oak's
introductory Pokédex text and ordinary goodbye. The endgame script is in a
different bank from `OaksLab`; both shared lines now use `farwritetext`.
Compiled-ROM checks verify the command, bank, and pointer, while the normal
Oak interaction and battle scenarios exercise the resulting flow.

See the [September 23 review](../playtest-review-2026-09-23.md#open-findings-and-known-behavior)
for its working-tree boundary and subsequent fix commit.

## Earlier documented profile totals

The test guide at documentation commit `9d3c34afa` reported the following
focused totals. No separate run date or ROM hash accompanied these summaries;
they are preserved as a documentation snapshot, not new validation evidence.

| Profile | Static | ROM | Emulator | Total |
| --- | ---: | ---: | ---: | ---: |
| Phase 5 | 14 | 11 | 28 | 53 |
| Phase 6 | 7 | 5 | 13 | 25 |
| Phase 7 | 17 | 9 | 21 | 47 |
| Phase 8 | 12 | 6 | 23 | 41 |
