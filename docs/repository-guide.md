# Repository Guide

This guide explains what is in the repository, how the pieces fit together, and
where to look before changing a subsystem. It reflects the Crystal Legends fork
state as of 2026-08-20.

## Current project state

This repository is a fork of the pret Pokémon Crystal disassembly. It retains
the exact upstream ROM variants and adds Crystal Legends as an isolated custom
build. The v0.1 implementation includes legendary-bird starters, the matching
Silver branches, Oak's third-bird handoff, and minimal title-screen branding.

The Phase 2 completion foundation adds the 251-species acquisition ledger,
single-player replacements for all ten trade evolutions, renewable evolution
items, and the post-League retryable Celebi event. Phase 9 now closes its
reserved Kanto starter, Safari-family, and legendary-bird sources. The ledger
still does not claim all 251 are catchable: Phase 10 owns the opposite Project
Mew species in Cerulean Cave.

Phase 9's production routes are intentionally compact. Leader scripts own the
three level-28 Kanto gifts; the Warden's granddaughter and Fuchsia tile callback
own access to one unattended `SafariZoneBeta`; and shared branch logic in
`maps/Phase9LegendaryBirds.asm` selects the Seafoam Articuno, Generator Annex
Zapdos, and Victory Road Moltres encounters without duplicating the Elm starter.
Conditional Kanto, Park, and Facility assets keep all reference builds exact.

The Phase 3 bedroom-TV CHEAT MODE is also implemented in source. Its renewable
supplies, capped money grants, and four ordinary Pokémon gifts deliberately
exclude story progression. A user-run manual pass confirmed CHEAT MODE and the
three v0.1 branches through Elm's post-break-in handoff, including title,
starter, first-Silver, third-bird, and player-learnset behavior. Progression
through Falkner, later Silver/balance checks, and the Phase 2 matrix remain
deferred, so the project is not yet fully playtest-certified.

Use sources in this order when they disagree:

1. The checked-out source, `Makefile`, and `layout.link`.
2. The local reference documents in `docs/`.
3. The upstream published docs and wiki.
4. Historical or third-party references.

External tutorials are useful recipes, but they may target a different commit
or a modified base. Apply them by understanding the change, not by copying a
patch blindly.

## How the build is assembled

The default build is driven by `Makefile`:

```text
ASM, data, PNG, palette, and map sources
        |
        +-- local C tools in tools/
        +-- RGBDS: rgbasm, rgbgfx, rgblink, rgbfix
        v
object files selected by the requested ROM variant
        |
        +-- layout.link assigns sections to ROM/RAM banks
        v
.gbc ROM + .sym symbol map + .map linker report
        |
        +-- tools/stadium adds Stadium 2 checksums
        +-- roms.sha1 verifies an exact upstream build
```

`includes.asm` is pre-included for every assembly object. It loads the common
charmap, macros, script languages, hardware definitions, and game constants.
The main object aggregators are:

- `home.asm`: code in the always-visible ROM0 bank, including interrupts,
  memory primitives, text, maps, audio, and far-call helpers.
- `main.asm`: most banked engine code and game data, grouped into named
  `SECTION`s.
- `audio.asm`: the sound engine, music, sound effects, and cries.
- `ram.asm`: VRAM, WRAM, SRAM, and HRAM declarations from `ram/`.
- The additional objects listed in `rom_obj` in `Makefile`: large text, map,
  Pokémon, graphics, mobile-library, and credits/event aggregators.

`layout.link` is the final authority for bank placement. When the linker reports
that a section is too large or cannot be placed, inspect the generated `.map`
file and the matching section in `layout.link`; moving code without considering
far calls and data-bank assumptions can introduce runtime bugs.

## Directory and entry-point map

| Path | Responsibility | Start here |
| --- | --- | --- |
| `engine/` | Executable game systems | Choose the subsystem directory, then find its include in `main.asm` or `home.asm`. |
| `data/` | Tables and content consumed by the engine | Prefer the narrowest subject directory such as `data/pokemon/`, `data/moves/`, or `data/maps/`. |
| `maps/` | Per-map event scripts (`.asm`) and block layouts (`.blk`) | Read `docs/map_event_scripts.md`; use Polished Map for `.blk` layouts. |
| `constants/` | IDs, flags, structure offsets, hardware values | `includes.asm` shows the global inclusion order. |
| `macros/` | Reusable assembly and domain-specific script syntax | `macros/scripts/` defines event, movement, text, audio, battle, and animation commands. |
| `home/` | Routines that must remain in fixed ROM bank 0 | `home.asm` is the inclusion map. Treat space here as especially constrained. |
| `ram/` | VRAM, WRAM, SRAM, and HRAM layouts | `ram.asm`, `macros/ram.asm`, and `layout.link`. |
| `gfx/` | Source artwork, palettes, tile data, and graphics aggregators | Edit source PNG or palette files; inspect the relevant rules in `Makefile`. |
| `audio/` | Sound engine data, songs, effects, and samples | `audio.asm`, `audio/engine.asm`, and `docs/music_commands.md`. |
| `mobile/`, `lib/mobile/` | Japanese mobile-adapter and mobile-library code/data retained by the disassembly | Follow inclusions from `main.asm`; do not assume these paths are unused. |
| `vc/` | Nintendo 2DS/3DS Virtual Console patch inputs | `docs/vc_patch.md` and the `crystal11_vc` target. |
| `tools/` | Nine C17 build helpers compiled by `make` | `tools/Makefile` and each tool's `USAGE_OPTS` declaration. |
| `docs/` | Local command references, subsystem notes, known issues, and project guidance | `docs/README.md` and `docs/index.md`. |
| `.github/` | CI, generated-file cleanliness check, issue templates, and upstream webhook behavior | `.github/workflows/main.yml` and `.github/checkdiff.sh`. |
| `tests/` | Static source/data checks, compiled-ROM contracts, immutable fixtures, and headless emulator scenarios | `tests/README.md` and `docs/workflows.md`. |

## Where to make common changes

| Goal | Primary source locations | Read first |
| --- | --- | --- |
| Edit map dialogue, events, warps, objects, or trainers | `maps/<MapName>.asm`, `data/maps/scripts.asm`, map/event constants | `map_event_scripts.md`, `event_commands.md`, `movement_commands.md`, `text_commands.md` |
| Edit a map layout | `maps/<MapName>.blk`, `data/maps/attributes.asm`, `data/maps/blocks.asm`, `gfx/tilesets/` | `map_event_scripts.md`, upstream map tutorial, Polished Map |
| Add or change a Pokémon | `constants/pokemon_constants.asm`, `data/pokemon/base_stats/`, `data/pokemon/evos_attacks.asm`, `data/pokemon/dex_entries/`, related `gfx/pokemon/` files | Upstream Tutorials page; inspect neighboring species entries |
| Change moves or effects | `data/moves/`, `constants/move*_constants.asm`, `engine/battle/effect_commands.asm`, `engine/battle/move_effects/` | `move_effect_commands.md` and upstream move tutorials |
| Change items, shops, or item behavior | `data/items/`, `constants/item*_constants.asm`, `engine/items/` | Upstream item and Mart tutorials |
| Change trainers or battle AI | `data/trainers/`, `data/battle/`, `engine/battle/ai/`, `engine/battle/` | Existing neighboring tables and the upstream wiki |
| Change wild encounters | `data/wild/`, `engine/overworld/wildmons.asm` | Upstream wild-slot tutorials |
| Change Phase 9 Kanto starter services | `maps/CeladonGym.asm`, `maps/CeladonCity.asm`, `maps/CeruleanGym.asm`, `maps/SeafoamGym.asm`, `maps/CinnabarIsland.asm` | `pokemon-acquisition.md`, `workflows.md`, and `decisions.md` |
| Change the unattended Safari preserve | `maps/SafariZoneWardensHome.asm`, `maps/FuchsiaCity.asm`, `maps/SafariZoneFuchsiaGateBeta.asm`, `maps/SafariZoneBeta.asm`, `data/wild/kanto_*.asm` | `pokemon-acquisition.md` and the Phase 9 workflow |
| Change Phase 9 legendary-bird locations or branches | `maps/Phase9LegendaryBirds.asm`, `maps/SeafoamIslandsCave.asm`, `maps/PowerPlant.asm`, `maps/PowerPlantGeneratorAnnex.asm`, `maps/VictoryRoad.asm`, `maps/OaksLab.asm` | `decisions.md`, `pokemon-acquisition.md`, and the Phase 9 scenario contract |
| Change menus or UI behavior | `engine/menus/`, subsystem-specific menu code | `menus.md`; search for the visible label or controlling routine |
| Change Crystal Legends CHEAT MODE | `maps/PlayersHouse2F.asm`, `maps/PlayersHouse2FDebug.asm`, `data/maps/scripts.asm` | `workflows.md`, `decisions.md`, and the neighboring event-script conventions |
| Change battle animations | `data/moves/animations.asm`, `engine/battle_anims/`, `gfx/battle_anims/` | `battle_anim_commands.md` |
| Change Pokémon picture animations | `gfx/pokemon/`, `engine/gfx/pic_animation.asm`, generated frame/bitmask tables | `pic_animations.md` and Pokémon animation rules in `Makefile` |
| Change graphics | Source `.png`/`.pal` files, relevant `gfx/*.asm` aggregator, `Makefile` rule | `FAQ.md` graphics guidance and the RGBGFX documentation |
| Change music or sound | `audio/music/`, `audio/sfx*.asm`, `audio/engine.asm`, audio constants/macros | `music_commands.md` |
| Change text encoding or rendering | `constants/charmap.asm`, `macros/scripts/text.asm`, `home/text.asm`, `data/text/` | `text_commands.md` |
| Change save or runtime memory | `ram/sram.asm`, `ram/wram.asm`, `ram/hram.asm`, `macros/ram.asm` | `layout.link`; inspect all version/debug conditionals |
| Diagnose an original-game bug | The named engine/data path | `bugs_and_glitches.md` and `design_flaws.md` |
| Build a debug ROM | `_DEBUG` conditionals in engine/RAM code | `make crystal_debug` or `make crystal11_debug` |

The large issue catalogs describe behavior inherited from the original game and
often include proposed fixes. A documented fix is not necessarily applied in
this checkout, and applying one may deliberately break the original-ROM hash.

## Build targets and validation

The repository pins RGBDS 1.0.3 in `.rgbds-version`, `INSTALL.md`, and CI. The
assembly guard in `rgbdscheck.asm` accepts RGBDS 1.0.0 or newer, but using the
pinned version is the safest way to reproduce CI and the reference hashes.
`make` and a C17 compiler are also required.

| Command | Result |
| --- | --- |
| `make` or `make crystal` | International Pokémon Crystal v1.0 ROM |
| `make crystal11` | International v1.1 ROM using `_CRYSTAL11` conditionals |
| `make crystal_au` | Australian variant using `_CRYSTAL11` and `_CRYSTAL_AU` |
| `make crystal_debug` | v1.0 ROM with `_DEBUG` menus and behavior |
| `make crystal11_debug` | v1.1 debug ROM |
| `make crystal11_vc` | v1.1 ROM plus Nintendo Virtual Console patch artifacts |
| `make crystallegends` | Crystal Legends ROM, `.sym`, and `.map` using `_CRYSTAL11` plus `_CRYSTALLEGENDS` |
| `make tools` | Only the local C helper programs |
| `make compare` | Build all reference outputs and verify them against `roms.sha1` |
| `make tidy` | Remove ROMs, maps, symbols, patches, objects, and compiled helpers |
| `make clean` | Run `tidy` and also remove generated graphics intermediates |
| `make test-static` | Run source/data contracts without building a ROM |
| `make test-rom` | Build and inspect compiled Crystal Legends/reference contracts |
| `make test-emulator-smoke` | Run the short production-ROM PyBoy smoke profile |
| `make test-emulator` | Run all implemented production-ROM PyBoy scenarios |
| `make test-crystallegends` | Run the focused local static/build/ROM/smoke/cleanliness gate |
| `make test-all` | Run the complete local gate, including all emulator scenarios and reference comparisons |

`make compare` is the strongest upstream-reproduction check. Crystal Legends
changes are gated behind `_CRYSTALLEGENDS`, so the target must still pass after
project changes. Validate the custom ROM separately with `make crystallegends`
and `rgbfix -v crystallegends.gbc`.

The GitHub workflow has an important fork-specific branch: repositories owned
by `pret` run `make ... compare`, while forks run the default `make` target. Both
paths run `.github/checkdiff.sh` to ensure the build did not modify tracked
sources. CI exercises Ubuntu and macOS, but the Python/PyBoy harness remains
local and `.github/workflows/main.yml` does not invoke it.

The local harness has three test layers beneath its aggregate runners:

1. `tests/static/` parses active Crystal Legends source and data for exhaustive
   geometry, collision, acquisition, evolution, encounter, and trainer
   contracts.
2. `tests/rom/` resolves labels from generated symbol files and checks the
   bytes, headers, save-layout fingerprint, variant isolation, and linker
   budgets of the assembled artifact.
3. `tests/emulator/` copies immutable battery fixtures into temporary
   directories, drives the production ROM with PyBoy, and asserts short
   stateful behaviors through symbolic RAM/SRAM views.

Shared parsers, ROM/symbol readers, state views, and scenario drivers live in
`tests/support/`; reviewed expected behavior lives in `tests/contracts/` and
`tests/fixtures/scenarios/`. Manual emulator validation remains separate and
authoritative for presentation, audio, pacing, balance, long progression, and
cross-emulator confidence. See [workflows.md](workflows.md) for commands,
fixture rules, and triage.

## Generated-file and compatibility boundaries

- PNGs and hand-written ASM/data are generally the editable sources. The
  ignored `.1bpp`, `.2bpp`, `.lz`, `.gbcpal`, `.dimensions`, animation tilemap,
  symbol, map, object, ROM, and patch files are build products.
- Some generated-looking assembly files under `gfx/pokemon/` are deliberately
  ignored and rebuilt. Follow the corresponding `Makefile` rule before editing
  one directly.
- The graphics and compression rules contain exact-match exceptions for
  original-ROM quirks. Simplifying those rules can produce a valid but
  non-matching ROM.
- The 2 MiB ROM uses 128 banks numbered `$00` through `$7f`; a `$4000`-byte
  switchable ROM bank is 16 KiB. `FAQ.md` currently calls that 4 KB, which is a
  documentation error.
- Version, Australian, Virtual Console, and debug builds use conditional
  assembly across code and RAM. Search all relevant conditionals before moving
  structures or deleting apparently duplicate paths.
- The `mobile/` and `lib/mobile/` areas preserve behavior that may look obsolete
  but is part of the disassembly and some variant/link paths.
- No top-level license file exists in the reviewed tree. Confirm upstream and
  asset-distribution requirements before publishing derived binaries or assets.

## Local documentation map

Use `docs/index.md` for the published documentation table of contents and this
file for repository orientation.

- Map/event scripting: `map_event_scripts.md`, `event_commands.md`,
  `movement_commands.md`, `text_commands.md`, `map_setup_scripts.md`.
- Battle and other scripting languages: `battle_anim_commands.md`,
  `move_effect_commands.md`, `music_commands.md`.
- Data formats and subsystems: `menus.md`, `pic_animations.md`, `vc_patch.md`.
- Original behavior and repair candidates: `bugs_and_glitches.md`,
  `design_flaws.md`.
- Repository operations: `workflows.md`.
- Durable fork decisions: `decisions.md`.
- Single-save species availability: `pokemon-acquisition.md`.
- Build setup and troubleshooting outside `docs/`: `INSTALL.md`, `FAQ.md`, and
  `STYLE.md`.

The command-reference docs are close to implementation details and usually link
to both the defining macros and the dispatch table. `event_commands.md` still
describes itself as incomplete, and `battle_anim_commands.md` contains open
TODOs, so confirm uncertain behavior in the implementation.

## External documentation and wiki map

These external resources were checked during the 2026-08-08 review:

| Resource | Best use | Boundary |
| --- | --- | --- |
| [Published pokecrystal docs](https://pret.github.io/pokecrystal/) | Rendered versions of the local command and subsystem references | Mirrors upstream `docs/`, not necessarily this fork's current files |
| [pokecrystal wiki](https://github.com/pret/pokecrystal/wiki) | Entry point for tutorials, hard-coded logic, branches, cleanup guidance, and learning links | Community-maintained and may target another source revision |
| [Tutorials](https://github.com/pret/pokecrystal/wiki/Tutorials) | Task recipes for maps, Pokémon, moves, items, graphics, upgrades, removals, and debug features | Check every referenced path and surrounding code before applying |
| [Assembly programming](https://github.com/pret/pokecrystal/wiki/Assembly-programming) | Curated RGBDS, Game Boy CPU, hardware, and optimization learning resources | Use the RGBDS manual version matching the project toolchain |
| [RGBDS v1.0.3](https://github.com/gbdev/rgbds/releases/tag/v1.0.3) and [RGBASM language reference](https://rgbds.gbdev.io/docs/v1.0.0/rgbasm.5) | Required toolchain release and authoritative assembler syntax | Newer RGBDS versions can change warnings or generated output |
| [Pan Docs](https://gbdev.io/pandocs/) | Game Boy hardware, memory map, banking, interrupts, PPU, audio, and cartridge controllers | Hardware reference, not a pokecrystal architecture guide |
| [symbols branch](https://github.com/pret/pokecrystal/tree/symbols) | Upstream `.sym` and `.map` artifacts for reference/debugging | Rebuild local symbols after this fork changes labels or placement |
| [Polished Map](https://github.com/Rangi42/polished-map) | Visual editing of compatible map block layouts and tilesets | Expanded projects may require Polished Map++; inspect its compatibility notes |
| [gb-asm-tools](https://github.com/pret/gb-asm-tools) | Optional scripts shared across Pokémon disassemblies | Separate from the nine C helpers in this repository's `tools/` directory |
| [pret Discord](https://discord.gg/d5dubZ3) | Community support after consulting code and documentation | Share minimal reproducible code and exact build errors |

The legacy G/S Scripting Compendium linked from `event_commands.md` is explicitly
described there as a temporary fallback for Gold/Silver binary hacking and as
not fully accurate for Crystal assembly. Prefer the local macros and dispatcher.

The wiki's Branches page lists feature, base, and fix branches. Treat those as
design references unless their documented base commit matches this fork; direct
`git pull` or patch application can mix unrelated history and create subtle bank
or data-layout conflicts.

## External-link audit notes

Before this guide was added, the inherited Markdown set contained 282 external
URL occurrences and 202 unique URLs. Most are upstream source links embedded in
the issue catalogs: 126 distinct `pret/pokecrystal/blob/master/...` paths were
checked against this checkout.

Four stale source paths were found and corrected in this documentation change:

- One map-setup link referenced the removed
  `macros/scripts/map_setup.asm`; the encoding macro now lives in
  `data/maps/setup_scripts.asm` and dispatch metadata in
  `data/maps/setup_script_pointers.asm`.
- Three unique links in `design_flaws.md` contained an accidental duplicate
  `/master/` path component.

The central published docs, wiki, Tutorials page, Assembly programming page,
symbols branch, RGBDS release, Polished Map project, and gb-asm-tools project
were reachable at review time. The old Microsoft WSL URL in `INSTALL.md`
redirects to the current Microsoft Learn page, and the Cygwin installer page is
still live.

Most source links in the inherited docs point to the moving upstream `master`
branch. They are useful for browsing upstream, but the same relative file in
this checkout is the source of truth for Crystal Legends. Prefer local relative
links in new fork-specific documentation.
