# Documentation

Start with [repository-guide.md](repository-guide.md) for the architecture,
directory map, build boundaries, task-to-file routing, and external resource
guide.

## Current milestone

Crystal Legends v0.1, the Phase 2 completion foundation, Phase 3 CHEAT MODE,
the Phase 4 Johto starter events, the Phase 5 Ruins gifts, Phase 6 roamer
quality-of-life, Phase 7 Project Mew, Phase 8 Silver arc, Phase 9 Kanto
completion, Phase 10 Giovanni/Cerulean Cave finale, and Phase 11 Red/Oak
endgame are source-complete.
Chikorita is a
level-14 gift at the Ilex Forest shrine after Cut, Cyndaquil is a level-19 gift
in Burned Tower after the legendary beasts awaken, and Totodile is a level-24
rescue on Cianwood's east shore after SecretPotion receipt. Their independent,
retry-safe gift paths pass the static, compiled-ROM, and production-ROM PyBoy
matrices, including storage failure, save/reload, and duplicate prevention.
Phase 5 adds level-10 Kabuto, level-26 Omanyte, and level-23 Aerodactyl gifts
after their picture and hidden-wall conditions, plus Kim's same-level
Girafarig trade. These paths have the same automated retry and persistence
ownership; their presentation remains user-owned.
Phase 6 preserves the stock Raikou and Entei hunt, permanent removal after
defeat or capture, and Pokédex Area route tracking. Its custom-only Fast Ball
correction now applies the intended multiplier to all 23 stock fleeing-list
species. The static, compiled-ROM, and production-ROM matrices pass without a
save-layout change or any Suicune behavior change.
Phase 7 builds Project Mew from subtle Slowpoke Well research hints through the
Lake of Rage proof and Mahogany reveal, then resolves it in a compact Radio
Tower transmitter annex. Its one-step north-facing entry seals behind the
player and reveals a southern two-console control bay facing a continuous glass
wall and northern containment chamber. The permanent terminal decision opens
the center glass and exit together, leaving the single level-30 subject as Mew
or stabilizing it as Mewtwo. Capture is optional for Johto progression, and any
knockout, escape, or player defeat leaves a fresh retry available.
Phase 8 closes Silver's stolen-bird arc after the Mt. Moon battle. Silver
returns the branch-correct legendary bird to Elm, Elm releases it after a final
look back, and the completed scene records only that species' availability for
Phase 9. The release also becomes the chronology gate for Silver's bird-free
Monday/Wednesday Indigo rematch, Tuesday/Thursday Dragon's Den training cameo,
and the Dragon Shrine elder hint. Phase 8 adds no physical bird encounter or
Oak handoff; Phase 9 now consumes those branch facts without changing the
release sequence.
Phase 9 makes Bulbasaur, Squirtle, and Charmander independent level-28 service
rewards; opens one Soul Badge-gated unattended Safari preserve with renewable
Mareep, Vulpix, Mankey, and Remoraid; and places the two non-starter legendary
birds in Seafoam, the Power Plant Generator Annex, and Victory Road according
to the existing branch. Only capture finalizes a bird. Phase 10 closes the
remaining main-story acquisition gap. Its Route 4 entrance derives access from
Project Mew resolution, Silver's released bird, and 14 badges without a saved
open flag. The single-floor cave contains six independent Rocket remnants,
five one-time rewards, repeatable lab records, custom encounters, and
Giovanni's six-Pokémon final team. Defeating Giovanni removes the cave crew and
reveals the opposite level-70 Project Mew species; only capture removes that
counterpart, so knockout, escape, player loss, and full storage remain retryable.
Phase 11 strengthens Red while preserving his six-species identity and rematch
behavior, records his first defeat independently of his current visibility,
and unlocks Professor Oak's one-time final challenge after Red plus at least
240 caught species. Oak selects one of three teams from the original legendary
starter branch, uses level-100 Tyranitar as his ace, and awards the true ending
through completion dialogue, a party heal, the full credits, and a return to
Pallet Town. The completed state persists through an ordinary save without a
Hall of Fame mutation or save-layout change.

The earlier manual pass confirmed the title screen, all three legendary-bird
starter branches, the first Silver battle, the Elm/Oak handoff, player-bird
learnsets, CHEAT MODE, and progression through Falkner. Phase 4 still needs the
user-owned presentation matrix for sprite appearance, dialogue, discoverability,
scene choreography, and story feel. Phase 5 also needs its user-owned Ruins and
Route 14 presentation matrix. Phase 6 still needs its user-owned tracker,
hunt-feel, and Fast Ball presentation review. Phase 7 still needs its user-owned
story clarity, annex presentation, pacing, and both-branch review. Phase 8
has passed its complete user-owned manual matrix: all three Mt. Moon/lab
branches, loss/retry and return travel, one natural Indigo rematch, and one
natural Dragon's Den cameo. Silver's full balance pass remains Phase 12 work.
Phase 2 presentation and full-game acceptance also remain deferred. Phase 8 is
playtest-certified, but the overall milestone is not yet release-ready because
the other listed manual gates remain open. Phase 9 passes its static,
compiled-ROM, production-ROM, persistence, and reference-isolation gates but is
not yet playtest-certified: starter presentation, Safari exploration, bird
routes, dialogue, palettes, and provisional balance still require user review
in SameBoy. Phase 10 likewise passes its complete automated and reference
gates, but its entrance, cave presentation, trainer flow, Giovanni battle,
blackout, and both counterpart branches still require user review in SameBoy.
Phase 11 passes its complete automated and reference gates, but Red/Oak battle
balance, dialogue, music, presentation, credits pacing, and the Pallet return
still require user review in SameBoy. Phase 12 full balancing is the next
roadmap phase.
See
[workflows.md](workflows.md) for the validation boundary and
[decisions.md](decisions.md) for the sequencing decision.

## Repository guidance

- [Repository guide](repository-guide.md): what the codebase contains and where
  to make common changes.
- [Workflows](workflows.md): repeatable build and validation procedures.
- [Automated testing workflow](workflows.md#run-the-local-automated-test-harness):
  local source, compiled-ROM, and headless-emulator profiles, fixture policy,
  and failure triage.
- [Decisions](decisions.md): durable technical and policy decisions for this
  fork.
- [Pokémon acquisition ledger](pokemon-acquisition.md): canonical single-save
  method, availability, renewability, and source for all 251 species.
- [Published documentation index](index.md): the original pokecrystal subsystem
  and command-reference table of contents.

## Map and event scripting

- [Map event scripts](map_event_scripts.md)
- [Event commands](event_commands.md)
- [Movement commands](movement_commands.md)
- [Text commands](text_commands.md)
- [Map setup commands](map_setup_scripts.md)

## Other scripting languages and subsystems

- [Battle animation commands](battle_anim_commands.md)
- [Move effect commands](move_effect_commands.md)
- [Music commands](music_commands.md)
- [Picture animations](pic_animations.md)
- [Menu data](menus.md)
- [Nintendo Virtual Console patch](vc_patch.md)

## Original-game issues

- [Bugs and glitches](bugs_and_glitches.md)
- [Design flaws](design_flaws.md)

These issue catalogs document inherited behavior and proposed fixes; they do not
mean every listed fix is already applied or appropriate for this fork.
