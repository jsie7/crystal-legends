# Documentation

Start with [repository-guide.md](repository-guide.md) for the architecture,
directory map, build boundaries, task-to-file routing, and external resource
guide.

## Current milestone

Crystal Legends v0.1, the Phase 2 completion foundation, and the source
implementation of Phase 3 CHEAT MODE are in place. The hidden bedroom-TV menu
provides renewable testing supplies, capped money grants, and four ordinary
bonus Pokémon without advancing story state. The five ordinary Crystal-missing
families remain deliberately reserved for the Phase 9 Safari Zone rather than
being added to Johto.

The user-run manual pass on 2026-08-10 confirmed the title screen, all three
legendary-bird starter branches through Elm's post-break-in handoff, both
outcomes of the first Silver battle, the player-bird learnsets, and the complete
CHEAT MODE surface. The remaining v0.1 progression through Falkner, later Silver
and balance checks, and the Phase 2 evolution/item/Celebi matrix are deliberately
deferred. The current milestone therefore has partial manual acceptance, but is
not yet a fully playtest-certified release. See
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
