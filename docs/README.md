# Documentation

Start with [repository-guide.md](repository-guide.md) for the architecture,
directory map, build boundaries, task-to-file routing, and external resource
guide.

## Current milestone

Crystal Legends v0.1, the Phase 2 completion foundation, Phase 3 CHEAT MODE,
the Phase 4 Johto starter events, and the Phase 5 Ruins gifts are
source-complete. Chikorita is a
level-14 gift at the Ilex Forest shrine after Cut, Cyndaquil is a level-19 gift
in Burned Tower after the legendary beasts awaken, and Totodile is a level-24
rescue on Cianwood's east shore after SecretPotion receipt. Their independent,
retry-safe gift paths pass the static, compiled-ROM, and production-ROM PyBoy
matrices, including storage failure, save/reload, and duplicate prevention.
Phase 5 adds level-10 Kabuto, level-26 Omanyte, and level-23 Aerodactyl gifts
after their picture and hidden-wall conditions, plus Kim's same-level
Girafarig trade. These paths have the same automated retry and persistence
ownership; their presentation remains user-owned.

The earlier manual pass confirmed the title screen, all three legendary-bird
starter branches, the first Silver battle, the Elm/Oak handoff, player-bird
learnsets, CHEAT MODE, and progression through Falkner. Phase 4 still needs the
user-owned presentation matrix for sprite appearance, dialogue, discoverability,
scene choreography, and story feel. Phase 5 also needs its user-owned Ruins and
Route 14 presentation matrix. Later Silver/balance checks, Phase 2
presentation, and full-game acceptance also remain deferred. The current
milestone is source-complete but is not yet playtest-certified or release-ready.
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
