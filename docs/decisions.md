# Decisions

Record durable technical or policy decisions here.

For each entry, capture the decision, the reasoning, and any context that matters later.

## 2026-08-09 — Keep Crystal Legends isolated from reference builds

Crystal Legends uses the dedicated `make crystallegends` target and the
`_CRYSTALLEGENDS` assembly flag on top of `_CRYSTAL11`. Project-specific code,
data, dialogue, and graphics must remain conditional so `make crystal11` and
`make compare` continue to reproduce the upstream reference ROMs exactly.

This keeps regression evidence meaningful and avoids turning intentional fork
changes into unexplained reference-ROM mismatches.

## 2026-08-09 — Use native single-player evolution paths

In Crystal Legends, Kadabra, Machoke, Graveler, and Haunter evolve at level 36.
Poliwhirl, Slowpoke, Onix, Scyther, Seadra, and Porygon evolve by directly using
their canonical trade item. King's Rock, Metal Coat, Dragon Scale, and Up-Grade
remain valid held items and are renewable from Celadon Department Store 4F.

Reuse `EVOLVE_LEVEL`, `EVOLVE_ITEM`, and `EvoStoneEffect`; do not add an
evolution type, parser branch, mart ID, or save field. Keep the stock trade
records and item behavior in every reference build.

## 2026-08-09 — Reserve four ordinary missing families for the Safari Zone

Mareep, Vulpix, Mankey, and Remoraid and their dependent evolutions belong to
the Phase 9 unattended Safari Zone. The canonical acquisition ledger must
identify the reservation until Phase 9 lands; the implemented area, levels,
rates, and slots are recorded in the later Phase 9 decision below. Phase 2 must
not add substitute Johto encounters for these families. Girafarig was
originally included in this reservation; Phase 5 instead makes Kim's Route 14
trade its canonical source, and Phase 9 adds no wild Girafarig.

## 2026-08-09 — Activate and harden the native Celebi sequence

Crystal Legends awards the GS Ball once after Hall of Fame instead of relying
on mobile-event data. It retains Kurt's native inspection and waiting sequence.
A full Key Items pocket must not advance the event, and any non-capture result
at the shrine restores the GS Ball plus both forest-restless states. A capture
finalizes the event and never produces a duplicate Celebi.

Resolve the capture result and restore retry state before `reloadmapafterbattle`:
on a loss, that command transfers control to the blackout script and never
returns to the shrine script. Keep the upstream sequence in reference builds.

## 2026-08-09 — Defer the v0.1 and Phase 2 emulator matrices until the cheat menu

Treat v0.1 as implementation-complete after its clean custom build, static
checks, and reference-ROM comparison pass. Defer the full three-starter
emulator matrix until the optional cheat/debug menu is implemented, then run
the v0.1, Phase 2, and cheat-menu acceptance checks together.

Build and source-level validation are still required while work continues.
Do not describe v0.1 or Phase 2 as playtest-certified or release-ready until the
deferred matrices have passed.

## 2026-08-10 — Keep CHEAT MODE temporary and story-safe

Crystal Legends exposes its optional CHEAT MODE through two consecutive
inspections of the player's bedroom TV. The first inspection
describes a Nintendo 64 connected to the TV; the second clears the sequence,
shows a warning, and requires explicit confirmation. Any other bedroom
interaction or map reload clears the partial sequence. The sequence uses only
`EVENT_TEMPORARY_UNTIL_MAP_RELOAD_2` and is never saved.

CHEAT MODE may renewably grant the enumerated ordinary supplies, add `100000`
to the player's money through the stock capped routine, and give level-5 Eevee,
Dratini, Larvitar, or Porygon through the normal party/current-box path. It must
not expose story Pokémon, legendary Pokémon, badges, key items, story flags, or
generic save editing. Cheat gifts do not count as canonical acquisition paths.

Keep the bedroom hook in `maps/PlayersHouse2F.asm` and the far-jumped menus in
`maps/PlayersHouse2FDebug.asm`, both isolated behind `_CRYSTALLEGENDS`. Do not
change the global TV script, stock bedroom PC behavior, save layout, or
reference builds to extend this testing tool.

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
[manual follow-up](workflows.md#falkner-follow-up--2026-09-16); the original
ROM-specific evidence above remains unchanged.

## 2026-08-10 — Keep the automated harness local and layered

Use locked Python/pytest tooling for source and data validation, symbolic
compiled-ROM contracts for the assembled artifact, and PyBoy 2.6.0 for short
headless production-ROM scenarios. PyBoy is test-only under the LGPL and is not
linked into or distributed with the ROM. Default `make` and GitHub Actions stay
unchanged; `make test-crystallegends` is the focused local gate and
`make test-all` is the complete local handoff gate.

Tests must resolve labels through generated `.sym` files and game constants
through the assembly definitions. Do not duplicate numeric ROM/RAM addresses,
species IDs, item IDs, map IDs, or event IDs in scenario contracts, and do not
add `_TEST` code paths to the shipped ROM. Static checks own exhaustive table
breadth; emulator scenarios own representative stateful behavior.

## 2026-08-10 — Permit reviewed battery fixtures, not savestates

Small, non-personal battery saves may be committed when a late or initialized
state cannot be reached cheaply in every test. Each fixture requires adjacent
provenance, source/ROM/save hashes, expected-state metadata, and reproduction
steps. Tests copy fixtures to temporary storage and verify the canonical file
remains unchanged. Emulator-specific savestates, mutable fixture outputs, ROMs,
screenshots, and traces remain untracked.

Save-layout fingerprint changes require an explicit compatibility decision and
fixture review or regeneration through the normal game save path.

## 2026-08-10 — Keep automated and manual acceptance separate

Automation may prove source structure, assembled bytes, script reachability,
state transitions, capacity behavior, and replay prevention. It does not
certify visuals, audio, dialogue quality, pacing, balance, exploration, a full
no-cheat or 251-species playthrough, another emulator, or physical hardware.
Record automated results and user-run manual evidence separately; neither may
be used to claim the other gate passed.

## 2026-08-11 — Place the Johto starters in independent world gifts

Crystal Legends restores the three ordinary Johto starter families without
reusing Elm's mutually exclusive starter state or adding wild encounters.
Chikorita is a level-14 Ilex Forest shrine gift after Cut, Cyndaquil is a
level-19 Burned Tower B1F gift after the legendary beasts awaken, and Totodile
is a level-24 Cianwood east-shore rescue after SecretPotion receipt. Each uses
its own persistent completion event and the stock `givepoke` party/current-box
path, so a decline or full party and current box leaves the gift retryable.

All three objects use their completion events as permanent hide flags.
Cyndaquil's object callback derives its sprite from the beast-release and
completion events before object masks load; it does not change saved events.
The beast-release scene restores the sprite and graphics before showing the
unclaimed gift. Its interaction script also rejects an already completed gift.
The pharmacist adds a discoverability hint after giving
the SecretPotion, but Phase 4 never consumes that item or changes Amphy,
lighthouse, gym, roamer, or downstream Suicune state.

The three overworld identifiers reuse the stock Pokémon-icon loader and add no
graphics assets. Keep every event flag, sprite entry, map object, script, and
hint behind `_CRYSTALLEGENDS`; reference builds must contain none of this
behavior and must continue to reproduce exactly.

## 2026-09-23 — Reserve graphics independently of Johto gift visibility

Burned Tower B1F always reserves Cyndaquil's graphics, including before the
beast release and after collection. The object callback still controls its
visibility. Keeping the graphics list stable prevents native Continue and
submenu redraws from moving the tile slots used by Cyndaquil, Eusine, and the
beasts. Cianwood's fixed-length outdoor graphics list replaces its unused
Tauros icon with Totodile; both use the same allocation size and sprite type.
Totodile uses the fixed-facing Pokémon animation: its two-frame icon cannot
provide the directional frames selected by ordinary swimming movement.
Both changes are custom-only and leave reference ROM bytes unchanged.

The [Phase 4 workflow](workflows.md#validate-the-phase-4-johto-starter-events)
covers loaded graphics, live object tile references, and event persistence
separately from manual presentation acceptance. Older saves can retain stale
object tile references; one ordinary exit and re-entry rebuilds the map objects
without changing gift progress or the save layout.

## 2026-08-11 — Gate Ruins gifts on both ancient conditions

For the Kabuto, Omanyte, and Aerodactyl chambers, Crystal Legends opens the
hidden room only after both the matching picture puzzle and the chamber's stock
hidden-wall condition are complete. The stock Escape Rope, Water Stone, and
Flash handlers may record their wall event before the picture is solved, but
the chamber must remain visibly closed and continue to show its clue until the
picture event is also set. Ho-Oh remains entirely stock.

Apply this dual predicate consistently to the opening scene, tile callback,
right-wall text, and Kabuto scientist dialogue while preserving the independent
picture-floor drop. There are no retained player-progression saves predating
this behavior, so do not add scene normalization, trade migration, save-version
conversion, or other compatibility scaffolding for hypothetical old progress.

The Kabuto word room beyond the stock item chamber contains a visible level-10
Kabuto once both conditions are complete. It sits at `(10, 8)`, immediately
after the inscription's final glyph, so the sprite acts as the sentence's
period. It uses the stock `givepoke` party/current-box transaction and a
dedicated success event: declining or having both destinations full leaves the
gift waiting, while successful party or box delivery completes it permanently.
Each Ruins gift uses its completion event as its permanent object hide flag.
Its object callback derives the sprite from the prerequisites and completion
before object masks load, without mutating saved state. The interaction script
independently checks both prerequisites and completion before offering a gift.
The preceding item room retains all four stock item balls.

The Omanyte word room uses the same independent transaction for a level-26
Omanyte at `(15, 10)`, immediately after its final inscription glyph. Its Water
Stone condition remains non-consuming and recognizes either the Bag or a party
Pokémon's held item. Once both the picture and remembered wall event are set,
the callback exposes the retry-safe gift without changing either prerequisite
or any stock room reward.

The Aerodactyl word room completes the set with a level-23 Aerodactyl at
`(16, 8)`, immediately after its final inscription glyph, using the same
independent, retry-safe contract. Kim's existing Route 14 trade keeps its
Chansey request, table index, dialog set, DVs, Gold Berry, OT identity, and
gender rule, but Crystal Legends offers a same-level Girafarig named `GIRAFY`.
Reference builds retain the complete stock Aerodactyl `AEROY` row. Girafarig is
renewable through breeding after this one-time trade, and Phase 9 deliberately
adds no wild Safari encounter that would undermine it.

## 2026-08-12 — Preserve stock roamers and fix only the custom Fast Ball scan

Raikou and Entei remain the stock level-40 roamers, and the normal Pokédex Area
screen remains their only route tracker. A flee preserves the roaming slot's HP
and DVs, but not battle status conditions. Defeat and capture both permanently
clear the slot; Crystal Legends does not restore or replace either beast.

Fast Balls retain the stock 4x-with-saturation calculation but, in
`_CRYSTALLEGENDS` builds, scan every species in all three terminated fleeing
groups. This covers the complete stock set of 23 species, including Entei as
the second entry in the always-flee group. Reference builds retain the upstream
branch bug so their ROMs remain exact. Do not expand this change into other
Apricorn Ball fixes, a new tracker, roaming changes, save data, or Suicune and
its unused third roaming slot.

## 2026-08-12 — Resolve Project Mew before Radio Tower cleanup

Project Mew concerns one captive living Mew. Slowpoke Well only hints at
biological research, the Lake of Rage establishes forced evolution as proof of
concept, and Mahogany's existing scientists, two-tile office workstation, four
lab computers, and transmitter reveal the subject and its transfer. The final
Radio Tower Executive records that Giovanni received the research before the
battle begins, so losing cannot rewind that fact.

After the Executive is defeated, a new 5-by-4-block transmitter annex pauses
the stock Director and Clear Bell cleanup. Its terminal requires confirmation
of one permanent outcome: reverse the sequence and retain Mew, or stabilize the
altered Mewtwo form. Store data sent, decision resolved, transformed outcome,
and capture as four independent event facts; do not derive the branch from the
party or Pokédex. The existing Executive victory event owns annex access.

The annex presents the subject in a northern containment chamber behind a
continuous glass wall, with the upload monitor and sequence terminal together
in the southern control bay. After the final Executive falls, the player walks
through the existing 5F corridor to the revealed stairway, enters at `(4, 6)`
facing north, takes one automatic step to `(4, 5)`, and hears the passage seal
behind them. A custom-only scene byte taken from the existing WRAM reserve
preserves that closed state without changing save-layout size. Before
resolution, the center glass can be inspected but not crossed; confirming
either outcome opens its center block and the southern exit together. Returning
places the player back on the revealed stair at `(14, 0)`, then automatically
retraces the walkable corridor to the original post-battle position at
`(14, 5)` before stock Director cleanup resumes.

If cleanup is still pending after a blackout, either ordinary 4F staircase
routes back through the annex without changing the permanent decision. Start
the return choreography only at `(14, 0)`, where its walkable path begins.

The selected subject is a normal level-30 wild battle that remains available
after knockout, escape, or player defeat and starts each retry at full HP with
no status. A single event-masked object represents the subject; its variable
sprite and encounter script follow the permanent Mew/Mewtwo outcome so two
objects never overlap. Capture alone removes it, but capture is not required to
resume the stock Radio Tower resolution. The generic caught-result query is
custom-only; reference builds retain their exact Celebi behavior and bytes. Do
not add pre-Phase-7 save migration or broaden this phase into Rocket-team
balancing.

## 2026-08-19 — End Silver's stolen-bird arc with voluntary release

Mt. Moon is Silver's final battle with the legendary bird he stole from Elm.
After a victory, Silver acknowledges that the bird chose to fight beside him
but returns it because the bond began through theft. The next ordinary entry to
Elm's Lab runs an automatic scene in which Elm releases the bird, the bird
looks back at Silver, and Silver leaves with his other partners.

Store the completed release and the three mutually exclusive species
availability facts as four custom events. Script order makes the return and
release atomic: set exactly the branch-correct availability fact, then the
release fact, then the lab's no-op scene. Never infer this state from party or
Pokédex ownership, and do not add a redundant handoff event.

The two temporary lab actors reuse the permanent initialization event as their
default object mask. Native Continue skips map object callbacks, so a
callback-owned `-1` visibility design would leak the actors after save/reload.
The automatic scene briefly unmasks both actors only after map setup, restores
the initialization fact immediately, and removes both object structs before
completion. This preserves the four-event story model and leaves ordinary Elm
interaction unchanged afterward.

Require the release fact in Crystal Legends before either Monday/Wednesday
Indigo rematch entrance, Silver's Tuesday/Thursday Dragon's Den cameo, or the
Dragon Shrine training hint. Preserve their stock dialogue, party data,
weekday checks, weekly cadence, and every reference-build byte.

Phase 8 sets only Silver's released-bird availability state. Phase 9 owns all
physical Articuno, Zapdos, and Moltres locations, encounter and retry behavior,
Oak's third bird, capture, and hints. Phase 12 owns Silver's full balance pass.
The four event IDs fit the existing 2048-bit event block, so no RAM, SRAM,
scene-layout, or reference-build compatibility boundary changes.

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

## 2026-08-20 — Earn all three Kanto starters through independent services

Erika, Misty, and Blaine each give one retry-safe level-28 starter after their
badge and a separate thematic service. Erika requires the deterministic
Celadon pond Muk task, Misty recognizes completion of the existing Machine
Part and Power Plant arc, and Blaine requires the Cinnabar survivor trail plus
recovery and return of `BLAINE'S LOG`. All three rewards coexist on one save.
Erika's request is recorded separately from task completion; after that
conversation, entering any of the pond's three northern water tiles starts the
Muk encounter directly. Entry remains silent before the request and after
completion.
Blaine's request is likewise recorded when he actually asks for help, so the
Cinnabar survivors retain their stock dialogue until that conversation.
After the player first speaks with Oak in Kanto, Oak's first assistant gives a
repeatable generic hint that Kanto Gym Leaders may entrust Pokémon to trainers
who help their cities. The second assistant remains dedicated to bird tracking.

Use the stock `givepoke` party/current-box transaction and ordinary generated
moves, then assign the gifting leader's OT name and a deterministic OT ID based
on their trainer class and party index. Decline or full party plus full current
box must not set the gift event
or repeat a completed service. The Blaine return fact is set before the gift
attempt so storage failure never repeats the investigation. The hidden cache
uses the stock boulder graphic at `(17, 12)` in the Crystal Legends-only
Cinnabar object list; three noninteractive boulders at `(12, 6)`, `(17, 1)`,
and `(12, 2)` make it part of the surrounding rubble. Its gray shelf staircase
uses a custom block, metatile, collision, and one imported stair-tread tile;
reference assets remain exact. The staircase uses nonzero Kanto metatile `$4b`
because block `$00` is a rendering and collision sentinel, not a usable map
block.

## 2026-08-20 — Open one unattended Safari preserve through existing Fuchsia state

Phase 9 reworks `SafariZoneBeta` as one outdoor Park-tileset preserve. The
existing Warden's granddaughter releases the north maintenance gate only after
the player has spoken with her and owns the Soul Badge; both prerequisite
orders converge in her conversation. Her Crystal Legends first-contact text
states the badge requirement directly instead of chaining the long stock
introduction into a second speech. The access event is permanent.

The preserve uses normal wild battles, the Bag, ordinary Poké Balls, experience,
and escape rules. It has no clerk, fee, timer, step counter, Safari Balls,
bait/rock commands, prize, or reopening ceremony. A 10-percent all-time grass
table initially made level-20 Mareep, level-24 Vulpix, and level-22 Mankey common; a
10-percent water table puts Remoraid in both common slots. Two ordinary visible
item balls reward exploration. The compact northern preserve uses denser grass,
an eight-by-six-tile pond framed by the National Park stone shore, and one
additional tree barrier. A Crystal Legends-only Park graphic duplicates that
shore into a gray-palette tile so it does not render with the orange roof
palette. Its two notices flank the two-tile south exit, whose carpet is limited
to the actual warp tiles. Multi-area ports and official Safari mechanics remain
deferred.

## 2026-08-20 — Place branch-safe birds in compact Kanto world locations

Articuno, Zapdos, and Moltres use explicit starter, Oak-handoff, Silver-release,
location-gate, capture, and object-mask facts. The player's starter species
never appears in the world; Oak's bird and Silver's bird unlock independently.
Only `CheckCaughtPokemon` success sets capture and mask facts, so knockout,
escape, and player loss remain retryable and native Continue cannot respawn a
captured bird. A dedicated Kanto-bird battle type suppresses the species flee
AI for all three encounters while leaving the player's Run command intact.
Oak's second assistant gives the shared habitat hint at most once per
conversation, reports no new sightings when the remaining released bird is
still gated, and confirms when both non-starter birds have been found.

Articuno is level 60 in a compact Ice Path cave off Route 20 built from the
unused `BetaUnionCave` backbone. Zapdos is level 60 in a 4-by-4 Power Plant
Generator Annex after restored power and a later Manager authorization. The
east-edge carpet stays visible while closed, reports the shutter state when
examined, and becomes a permanent directional warp after authorization. Once
open, that permanent fact is authoritative before the power and authorization
checks so legacy or constructed saves cannot report a closed-state message at
an accessible entrance. The two shutter interactions deliberately sit one tile
beyond the map's east edge
so pressing A while facing right from either visible carpet tile works; the
map-event validator records these as two exact reviewed exceptions.
Moltres is level 60 on Victory Road's existing isolated eastern
shelf and always waits for the first Hall of Fame. The shelf's former visible
Full Restore is instead a hidden pickup at `(9, 58)`, while a visible Charcoal
at `(17, 31)` gives Moltres the same type-specific reward treatment as Articuno
and Zapdos. Moltres occupies `(18, 29)` and is approached from `(18, 30)`.
These maps reuse stock sprites and tiles wherever possible. They change no
save-layout dimensions and remain wholly absent from reference builds.

The Seafoam cave uses a visible south exit and several connected ice lanes.
Rock stops frame the entrance, separate the eastern ice field from Articuno,
and turn the route to the bird into a short sliding puzzle. An exposed Ultra
Ball rewards the western branch, while a hidden NeverMeltIce sits in the
northeast ice rock.

Both tiles of the annex's two-tile generator console share one reading. It
reports unsafe output only while Zapdos is physically present and safe output
whenever the location selector hides it, including capture and the
Zapdos-starter branch. A visible Magnet in the southeast corner rewards annex
exploration and gives Zapdos an immediately relevant held item.

## 2026-08-23 — Align Kanto starter-gifting leaders in the Phase 12 balance pass

Phase 12 must add the final evolution of each gifted Kanto starter to the
corresponding leader's battle party: Venusaur for Erika, Blastoise for Misty,
and Charizard for Blaine. This makes each Phase 9 gift read as a Pokémon line
the leader personally trains rather than an unrelated reward. Phase 12 owns
the exact level, moves, party position, and which existing party member—if
any—is replaced; it must evaluate those choices with the complete Kanto
difficulty curve. Do not change the Phase 9 service prerequisites, gift level,
leader OT assignment, or retry behavior as part of that roster work.

## 2026-08-26 — Reuse unused Cave blocks for three lab fixtures

Crystal Legends reserves Cave block `$03` for an empty Facility-style table,
`$16` for the computer workbench from Lab block `$21`, and `$17` for the
Facility `$08` control terminal. The empty table uses Facility `$29` with its
two paper tiles replaced by the plain tabletop graphic `$51`. Approach from
the north for the bench, and from the south for the table and terminal.
Exposed floor tiles use the raised cave ground. The fixtures are scenery only
until map placement and background-event scripts are
approved; this asset preparation does not implement the Phase 10 story or
register Cerulean Cave as a playable map.

Reuse 32 8-by-8 graphic slots without increasing the 96-tile graphics sheet or
64-block table. Of these, 31 were unreferenced by every original block; graphic
`$04` is reclaimed from the retired grass block `$03`. The other blocks, their
graphics, collision, and palettes remain unchanged. Cave and Dark Cave share
block/collision/palette tables, so tests prohibit all three reserved blocks in
their existing maps; the new furniture is intended for Cave graphics, not Dark
Cave. Reference
builds continue to use all original assets and collision rows.

The terminal's whole bottom tile row uses cave ground, replacing both the
Facility patterned-floor tile `$01` and its blank-floor tile `$26`.

Keep the first two fixtures' graphic allocations stable when adding the table.
Reclaiming the grass graphic and selecting the existing compressor's optimized
mode only for `cave_crystallegends.2bpp.lz` keeps the three-fixture graphics at
the same 1008 bytes as the two-fixture version. Original assets retain matching
compression. Do not delete block `$3f`: it is Victory Road's pit block and has
no unique graphics to reclaim.

The custom compressed graphics occupy 1008 bytes versus the original 912,
leaving `$0034` (52) bytes free in ROMX bank `$07`. Keep a reviewed `$0030`
floor there; further growth requires a separate capacity review. No bank
relocation, new tileset ID, map size, object slot, event flag, or save-layout
field is needed.
Reproduction and verification are documented in
[workflows.md](workflows.md#regenerate-and-validate-the-cave-lab-fixtures).

## 2026-08-26 — Import standing-only Giovanni artwork from Pokémon Red

Crystal Legends appends `SPRITE_GIOVANNI` at ordinary sprite ID `$67`, leaving
all existing IDs and the `$80` Pokémon-icon range unchanged. Import Red's three
standing 16-by-16 poses without redrawing pixels: down, up, and left, with the
engine mirroring left for right. The source PNG is 16-by-48; its 12 native 2bpp
tiles occupy 192 bytes. Use `STANDING_SPRITE` and `PAL_OW_BROWN`.

Giovanni may turn but must not walk or use the automatic trainer-approach
sequence. The planned post-victory blackout removes the cave crew without
walking choreography. This asset slice does not implement that scene, his
trainer portrait/class/battle, map registration, or any event flags.

Place the custom-only bytes in `Crystal Legends Sprites`, after `Map Blocks 3`
in bank `$2c`. The section is empty in reference builds. Both original sprite
banks remain unchanged; the custom bank retains `$23da` (9178) free bytes and
its existing `$2000` minimum reserve. No bank relocation, ROM expansion, engine
change, or save-layout change is required. The draft now previews the real
sprite at player coordinate `(06,04)`, facing down. Source provenance and the
repeatable import/check procedure are in
[workflows.md](workflows.md#giovanni-standing-sprite).

## 2026-09-06 — Finish Project Mew in one derived-access Cerulean Cave

Crystal Legends restores Cerulean Cave as custom map group 7, map 19: one
15-by-18-block Cave-tileset floor entered from the ordinary Route 4 warp at
`(38, 3)` and exited at `(21, 33)`. The accepted terrain replaces the unused
beta-cave payload at the same size. Route 4 and Cerulean City use same-size
custom block variants, retain their stock connection, and preserve the hidden
Berserk Gene.

Access requires `EVENT_PROJECT_MEW_RESOLVED`, `EVENT_SILVER_BIRD_RELEASED`, and
at least 14 badges. Do not store a separate cave-open fact. Route 4's object
callback writes the guard map object's sprite to `SPRITE_ROCKET` or zero before
visible object structs are initialized; `appear`/`disappear` cannot correctly
derive an eventless object's initial visibility at that callback boundary.
This keeps eligibility order-independent and reconstructs it on map load and
native Continue.

The cave holds six Rocket remnant trainers with independent defeat flags, but
all six object masks and Giovanni's object mask use `EVENT_BEAT_GIOVANNI` so the
post-boss blackout removes the complete crew even when a remnant was skipped.
Giovanni is a stationary script object and a dedicated custom-only `ROCKET
BOSS` class with a six-Pokémon party. Set `EVENT_GIOVANNI_RETURNED` before the
first battle; set `EVENT_BEAT_GIOVANNI` only after victory and the reload, then
remove all seven Rocket objects without walking choreography. A loss therefore
preserves a truthful retry state.

After Giovanni, the same variable-sprite object exposes the Project Mew
counterpart: the transformed Johto branch gets level-70 Mew, and the restored
branch gets level-70 Mewtwo. Determine this solely from
`EVENT_PROJECT_MEW_TRANSFORMED`, not current ownership. Knockout, escape,
player loss, or full storage leaves a fresh encounter; only
`CheckCaughtPokemon` success sets `EVENT_CAUGHT_CERULEAN_CAVE_COUNTERPART` and
removes the object.

Persistent Kanto event IDs 261–267 store Giovanni returned, counterpart caught,
and the five cave pickups. Trainer IDs 1484–1490 store Giovanni and remnant
victories. The 12 paired lab-record quadrants are repeatable and stateless.
The walking, Surf, and fishing tables are custom-only, as are the map, scripts,
events, trainer data, portrait, and overworld object. `NUM_EVENTS`, WRAM/SRAM,
the save fingerprint, and every reference-build byte remain unchanged.

Giovanni's 56-by-56 portrait adapts the Pokémon Red source linked in
[workflows.md](workflows.md#validate-phase-10-giovanni-and-cerulean-cave). It
occupies Pics 18 in bank `$59`; lossless custom-only Omastar back-picture
compression creates the three pointer bytes while keeping the picture in its
original bank. The finalized bank floors and reproduction commands are owned by
the same workflow.

## 2026-09-07 — Close the endgame with durable Red and one-time Oak victories

Crystal Legends keeps Red at Mt. Silver with Pikachu, Espeon, Snorlax,
Venusaur, Charizard, and Blastoise, but raises his provisional endgame party to
levels 82–85 with max class DVs. `EVENT_RED_IN_MT_SILVER` remains only the
current object-visibility flag so later Hall of Fame clears can restore a Red
rematch. New event 1491, `EVENT_BEAT_RED`, records the first successful victory
permanently and is never cleared by rematch setup.

After Mt. Silver opens, Oak continues to run the stock Pokédex rating before
the new state response. His only live unlock is `EVENT_BEAT_RED` plus at least
240 of 251 caught species; no legendary, starter, Ruins, Giovanni, Project Mew,
or other story fact is an additional requirement. Declining or losing changes
nothing. Oak uses the existing `POKEMON_PROF` presentation with two Full
Restores, full leader-grade AI, max DVs, and Champion music. Three level-94-to-
100 parties select Charizard for an Articuno player, Venusaur for a Zapdos
player, or Blastoise for a Moltres player; all finish with Tyranitar. The exact
levels and moves are provisional inputs to Phase 12, while the identities and
branch mapping are story locks.

Successful Oak victory alone sets event 1492,
`EVENT_BEAT_PROFESSOR_OAK`, then gives completion dialogue, heals the party,
and invokes the existing full credits without adding a Hall of Fame record. A
transient Crystal Legends-only `SPAWN_OAK` selector preserves the Oak ending
through `RedCredits`, returns to the existing Pallet Town spawn, and clears
itself. Later Red rematches still select the Mt. Silver return. Credits do not
autosave; the player resumes in Pallet and may save normally, after which both
victory facts and Oak's permanent completion dialogue persist.

The two events occupy trainer-gap IDs 1491–1492. `NUM_EVENTS`, WRAM, SRAM, the
save-layout fingerprint, map geometry, and all reference builds remain
unchanged. Pre-Phase-11 saves therefore begin with both formerly unused bits
clear. Presentation, dialogue, credits pacing, and provisional boss balance
remain a separate user-owned SameBoy gate; Phase 12 owns final numeric tuning.

## 2026-09-15 — Apply fixed Kanto wild levels without changing habitats

Phase 12 changes 584 level bytes across 26 land and 13 surfing records.
Species, ordered slots, time windows, rates, fishing and encounter mechanics
remain exact. Safari now has Mareep 28, Mankey 32, Vulpix/Exeggcute 34,
Tauros/Scyther/Pinsir 36 and Chansey/Kangaskhan 38. Its surf bases are
Remoraid 25/27 and Octillery 31, with the native +0–4 variation. Route 7
Houndour stays 26 and Diglett's Cave preserves its time-dependent differences.

The [acquisition ledger](pokemon-acquisition.md) records current levels; earlier
Phase 9 evidence describes the original implementation. Preserve Johto, the
pre-League approach, oceans, Mt. Silver, Cerulean Cave, scripted encounters and
gift levels. These fixed tables add no bytes or guaranteed training XP. See
[Phase 12](phase-12-balance.md) for the exact contract and acceptance boundary.

## 2026-09-15 — Implement the accepted Phase 12 trainer package

Crystal Legends uses the complete approved 166-record trainer scope, covering
149 distinct battles when selecting one starter branch and clearing the listed
optional encounters once. Johto leaders retain every stock partner and gain
one each; the four Elite Four teams gain a sixth. Lance, Blue, Elder Li,
ordinary Johto, pre-League Routes 26/27 and shared S.S. Aqua parties remain
stock. Ordinary Kanto gym underlings gain 10 levels and listed routes gain 8,
both capped one below the assigned geographic gym ace. Colette is the sole
ordinary authored-move exception. Cal remains daily with natural level-55 moves.

Silver's bird progression is 5/16/22/32/40/50; supporting additions arrive at
Azalea, Burned Tower and Goldenrod. After the existing release scene, Ursaring
fills the sixth rematch slot and Crobat 52 is last and highest-level. Golbat
remains through Mt. Moon; release prerequisites, branches and weekly cadence
are unchanged. Cave remnants are 54–60, Giovanni is 60–65, Red returns to
stock levels with four softer moves, and all Oak variants are 84/85/85/86/87/90.
These supersede the provisional numeric targets in earlier phase decisions.

The [trainer contract](../tests/contracts/phase_12_trainers.json) owns exact
ordered members, moves, formats and preservation targets. Only Kiyo and Colette
convert automatic parties to authored moves. Preserve existing class items,
AI, DVs, rewards logic, story scripts, gifts, player learnsets and save layout.
Do not add a global level boost or dynamic badge scaling. The 252-byte expansion
leaves 826 bytes in bank $0e; the reviewed 768-byte floor leaves 58 bytes of
margin. All reference artifacts must remain exact.

Automated data/state tests and natural-play difficulty are separate gates.
The [Phase 12 workflow](workflows.md#validate-phase-12-trainer-and-wild-balance)
owns the remaining manual matrix. Do not equate optional recruits, access to
Red/Oak, later victory rewards or historical level forecasts with readiness.

## 2026-09-17 — Finalize Elm's starter choice only after delivery

All three legendary-bird choices use the native `givepoke` result before
removing their Poké Ball, recording the chosen species, or announcing receipt.
A full party and full current box show a storage refusal and leave every
choice and story gate unchanged, including after native Save/Continue. Party
or current-box delivery proceeds through the existing Elm directions once.
Keep this guard custom-only and preserve reference-ROM bytes.

The [legendary starter workflow](workflows.md#validate-elms-legendary-starter-gifts)
owns refusal, retry, ordinary delivery, and branch regression coverage.
