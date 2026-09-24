# Project status

This is the maintained status summary for Crystal Legends. Evidence is current
through 2026-09-23; documentation changes do not constitute a new gameplay test.
Use the [repository guide](repository-guide.md) to locate code, the
[acquisition ledger](pokemon-acquisition.md) for species availability, and the
[balance guide](phase-12-balance.md) for current trainer and encounter rules.

## How to read the status

- **Implemented:** the production source contains the feature.
- **Automated:** source, assembled-ROM, and headless production-ROM contracts
  have passed within the linked evidence boundary.
- **Manual:** a person reported the stated flow on a particular ROM or prepared
  checkpoint. Unreported branches and outcomes remain open.
- **Natural play:** discovery, progression, difficulty, and collection through
  ordinary play. Prepared saves and forced battle outcomes do not establish it.

All Phase 1–12 features below are implemented and have automated coverage.
The latest recorded full gate is the
[2026-09-23 review](playtest-review-2026-09-23.md#code-and-regression-review):
642 tests and six exact upstream reference comparisons. Its ROM hash and
working-source boundary are recorded there; do not attribute older manual
reports to that ROM.

## Feature matrix

| Feature | Recorded manual acceptance | Remaining manual or natural-play work |
| --- | --- | --- |
| Legendary starters, first Silver battle, Elm/Oak handoff (Phase 1 / v0.1) | All three early branches, both first-battle outcomes, title, and player-bird learnsets passed on 2026-08-10; Falkner progression subsequently confirmed. | Later progression and current balance across all three starters; the Falkner follow-up did not separately confirm save/reload. |
| Single-player evolutions, renewable items, Celebi (Phase 2) | Prepared Celebi sequence passed on 2026-09-23. | All ten evolution paths and item presentation; Kurt's natural overnight wait; unreported capacity and capture-retry variants. |
| CHEAT MODE (Phase 3) | Complete feature/safety matrix passed on 2026-08-10. | Full-game acceptance must include an independent no-cheat run. |
| Johto starter gifts (Phase 4) | All three prepared gifts passed on 2026-09-23, including Chikorita with Lucky Egg and the sprite fixes. | Natural discovery, held-item transfer and box retrieval, and Lucky Egg progression impact. The older Cyndaquil checkpoint does not separately establish its Lucky Egg delivery. |
| Ruins gifts and Girafarig trade (Phase 5) | No complete manual matrix reported. | Natural puzzles and hidden-wall conditions, all three gift presentations, and Kim's trade. |
| Roamers and Fast Balls (Phase 6) | No complete manual hunt matrix reported. | Pokédex tracker clarity, hunt feel, Fast Ball presentation, and Suicune continuity. |
| Project Mew (Phase 7) | No complete manual branch matrix reported. | Both choices, annex presentation and retries, Director continuation, and the linked cave counterpart. |
| Silver's release arc (Phase 8) | Complete story matrix passed in SameBoy on 2026-08-19. | Later Phase 12 party changes require separate natural-play balance review. |
| Kanto gifts, Safari preserve, world birds (Phase 9) | No complete manual matrix reported. | All services on one save, both Safari access orders, natural routes, all starter-dependent bird branches, and capture/retry presentation. |
| Giovanni and Cerulean Cave (Phase 10) | Prepared cave/finale flow passed on 2026-09-23 after the label fix. | Unreported access boundaries, both counterparts and failure paths, and natural cave difficulty. |
| Red, Oak, true ending (Phase 11) | Prepared Oak battle through credits passed on 2026-09-23. | Red progression, natural 240-caught unlock, unplayed Oak teams, ending save/Continue, and later Red rematches. |
| Trainer and wild balance (Phase 12) | Prepared boss victories provide flow evidence only. | Four- and six-member teams, all three starters, EXP economy, Lucky Eggs, recruitment, grinding, losses, and healing use. |
| Final polish and full-game acceptance (Phase 13) | Individual fixes and checkpoint successes exist. | Remaining presentation issues, a complete no-cheat story run, and natural single-save collection of all 251 species. |

## Next work

Prioritize unplayed content and integration: both Project Mew choices, all Kanto
starter services, every world-bird branch, and Safari/Ruins discovery. Then close
the focused timing, evolution/item, roamer, and ending-persistence gaps. Finish
with natural progression and 251-species collection.

Use the [playtest scenarios](playtesting.md#recommended-next-playtests)
and [repeatable procedures](workflows.md) to prepare those checks. Successful
checkpoint flows do not need wholesale repetition unless the behavior changes.

## Evidence and maintenance

- [Early manual report and follow-ups](history/validation.md#manual-validation-record--2026-08-10)
- [Silver story acceptance](history/validation.md#silver-story-acceptance--2026-08-19)
- [Phase 12 integration evidence](history/phase-12-validation-2026-09-15.md#final-validation--2026-09-15)
- [September 23 review and manual confirmations](playtest-review-2026-09-23.md)

When results arrive, update this matrix and append a dated evidence record with
the ROM commit/hash, emulator/version, preparation boundary, tested branches,
and outcome. Keep unknown provenance explicitly unknown. Procedures describe
how to test; historical records describe what was tested. Neither should carry
a second independently maintained project-status summary.
