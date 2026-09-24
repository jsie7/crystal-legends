# Historical decisions and acceptance notes

These entries preserve earlier scheduling and acceptance decisions. They do not
set current project status. Use [status](../status.md), the current
[decision log](../decisions.md), and [dated validation](validation.md) for their
successors. Original numeric targets below have been superseded by Phase 12.

## 2026-08-09 — Defer the v0.1 and Phase 2 emulator matrices until the cheat menu

Treat v0.1 as implementation-complete after its clean custom build, static
checks, and reference-ROM comparison pass. Defer the full three-starter
emulator matrix until the optional cheat/debug menu is implemented, then run
the v0.1, Phase 2, and cheat-menu acceptance checks together.

Build and source-level validation are still required while work continues.
Do not describe v0.1 or Phase 2 as playtest-certified or release-ready until the
deferred matrices have passed.

## 2026-08-10 — Record partial manual acceptance and defer progression

A user-run manual pass on the Crystal Legends ROM at commit `5ec915ce1`
confirmed the title screen, all three legendary-bird starter branches through
Elm's post-break-in handoff, the correct first Silver bird for every branch,
both permitted outcomes of that battle, the player-bird learnsets, and CHEAT
MODE entry, navigation, grants, and safety variants.

This closes the Phase 3 feature matrix and the early v0.1 story slice through
the one-time Oak handoff. At the time, the user deliberately deferred the
remaining playthrough-dependent checks: progression through Falkner, later
Silver and balance sampling, and the Phase 2 evolution/item/Celebi matrix.
Do not describe v0.1, Phase 2, or the complete project as fully playtest-certified
until those remaining matrices pass. The exact emulator/version was not supplied
with this test report and should be appended if it becomes available.

On 2026-09-16, the user confirmed that progression through Falkner was completed
manually. That portion of the deferral is superseded by the
[manual follow-up](validation.md#falkner-follow-up--2026-09-16); the original
ROM-specific evidence above remains unchanged.

## 2026-08-19 — Accept the complete Phase 8 manual matrix

The user verified and passed every Phase 8 manual acceptance check in SameBoy
after the final Elm's Lab presentation fixes. This covers all three Mt. Moon
and lab branches, loss/retry behavior, normal return travel, the released
bird's visible look-back, dialogue and exit presentation, one natural Indigo
rematch, one natural Dragon's Den cameo, and the Phase 8/Phase 9 boundary.

The accepted ROM is commit `0e73807d2`, SHA-256
`a5c2b67aaad42b1f3f06290bd40da6204c98279b7a037e0e14549cdd5fcc26f9`.
The exact SameBoy version was not supplied. This evidence makes Phase 8
playtest-certified; it does not certify earlier phases, the Phase 12 Silver
balance pass, the complete project, or release readiness.

## Superseded numeric targets

The initial Phase 9 Safari implementation used level-20 Mareep, level-24 Vulpix,
and level-22 Mankey in its 10-percent all-time grass table. Phase 12 replaced
the levels while preserving habitats and rates.

The September 7 endgame decision provisionally set Red to levels 82–85 and
Oak's teams to levels 94–100. The September 15 trainer package replaced these
numbers: Red returned to stock levels with four softer moves, and Oak's teams
became 84/85/85/86/87/90. Story identities, branch mapping, and unlock predicates
remain intact. See the [current balance rules](../phase-12-balance.md).
