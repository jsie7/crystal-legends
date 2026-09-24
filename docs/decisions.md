# Decisions

This log owns durable policy, rationale, and state-model constraints. Current
acceptance belongs in [status](status.md), repeatable operations in
[workflows](workflows.md), and run evidence in
[history](history/validation.md). Exact acquisition rows and balance targets
have their own linked contracts.

When a decision changes, state which earlier rule it supersedes and preserve
the reason. Earlier Phase 8–11 numeric parties and Phase 9 wild levels are
superseded by Phase 12; their story and acquisition rules still apply.

## Decision index

| Decision | Date |
| --- | --- |
| [Keep Crystal Legends isolated from reference builds](#2026-08-09--keep-crystal-legends-isolated-from-reference-builds) | 2026-08-09 |
| [Use native single-player evolution paths](#2026-08-09--use-native-single-player-evolution-paths) | 2026-08-09 |
| [Reserve four ordinary missing families for the Safari Zone](#2026-08-09--reserve-four-ordinary-missing-families-for-the-safari-zone) | 2026-08-09 |
| [Activate and harden the native Celebi sequence](#2026-08-09--activate-and-harden-the-native-celebi-sequence) | 2026-08-09 |
| [Keep CHEAT MODE temporary and story-safe](#2026-08-10--keep-cheat-mode-temporary-and-story-safe) | 2026-08-10 |
| [Keep the automated harness local and layered](#2026-08-10--keep-the-automated-harness-local-and-layered) | 2026-08-10 |
| [Permit reviewed battery fixtures, not savestates](#2026-08-10--permit-reviewed-battery-fixtures-not-savestates) | 2026-08-10 |
| [Keep automated and manual acceptance separate](#2026-08-10--keep-automated-and-manual-acceptance-separate) | 2026-08-10 |
| [Place the Johto starters in independent world gifts](#2026-08-11--place-the-johto-starters-in-independent-world-gifts) | 2026-08-11 |
| [Reserve graphics independently of Johto gift visibility](#2026-09-23--reserve-graphics-independently-of-johto-gift-visibility) | 2026-09-23 |
| [Gate Ruins gifts on both ancient conditions](#2026-08-11--gate-ruins-gifts-on-both-ancient-conditions) | 2026-08-11 |
| [Preserve stock roamers and fix only the custom Fast Ball scan](#2026-08-12--preserve-stock-roamers-and-fix-only-the-custom-fast-ball-scan) | 2026-08-12 |
| [Resolve Project Mew before Radio Tower cleanup](#2026-08-12--resolve-project-mew-before-radio-tower-cleanup) | 2026-08-12 |
| [End Silver's stolen-bird arc with voluntary release](#2026-08-19--end-silvers-stolen-bird-arc-with-voluntary-release) | 2026-08-19 |
| [Earn all three Kanto starters through independent services](#2026-08-20--earn-all-three-kanto-starters-through-independent-services) | 2026-08-20 |
| [Open one unattended Safari preserve through existing Fuchsia state](#2026-08-20--open-one-unattended-safari-preserve-through-existing-fuchsia-state) | 2026-08-20 |
| [Place branch-safe birds in compact Kanto world locations](#2026-08-20--place-branch-safe-birds-in-compact-kanto-world-locations) | 2026-08-20 |
| [Align Kanto starter-gifting leaders in the Phase 12 balance pass](#2026-08-23--align-kanto-starter-gifting-leaders-in-the-phase-12-balance-pass) | 2026-08-23 |
| [Reuse unused Cave blocks for three lab fixtures](#2026-08-26--reuse-unused-cave-blocks-for-three-lab-fixtures) | 2026-08-26 |
| [Import standing-only Giovanni artwork from Pokémon Red](#2026-08-26--import-standing-only-giovanni-artwork-from-pokémon-red) | 2026-08-26 |
| [Finish Project Mew in one derived-access Cerulean Cave](#2026-09-06--finish-project-mew-in-one-derived-access-cerulean-cave) | 2026-09-06 |
| [Close the endgame with durable Red and one-time Oak victories](#2026-09-07--close-the-endgame-with-durable-red-and-one-time-oak-victories) | 2026-09-07 |
| [Apply fixed Kanto wild levels without changing habitats](#2026-09-15--apply-fixed-kanto-wild-levels-without-changing-habitats) | 2026-09-15 |
| [Implement the accepted Phase 12 trainer package](#2026-09-15--implement-the-accepted-phase-12-trainer-package) | 2026-09-15 |
| [Finalize Elm's starter choice only after delivery](#2026-09-17--finalize-elms-starter-choice-only-after-delivery) | 2026-09-17 |
| [Attach Lucky Eggs to the three Johto world gifts](#2026-09-23--attach-lucky-eggs-to-the-three-johto-world-gifts) | 2026-09-23 |

Historical scheduling and acceptance entries remain below as links to their
[archived records](history/decisions.md).

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
the unattended Safari preserve, implemented in Phase 9. Keep those missing
families as Kanto discoveries rather than adding substitute Johto encounters.
The [acquisition ledger](pokemon-acquisition.md) owns their current methods and
levels.

Girafarig's original Safari reservation was superseded by Phase 5: Kim's Route
14 trade is its canonical source, and the preserve adds no wild Girafarig.

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

This historical scheduling or acceptance record is preserved in
[decision history](history/decisions.md#2026-08-09--defer-the-v01-and-phase-2-emulator-matrices-until-the-cheat-menu). Use [project status](status.md) for the remaining acceptance boundaries.

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

This historical scheduling or acceptance record is preserved in
[decision history](history/decisions.md#2026-08-10--record-partial-manual-acceptance-and-defer-progression). Use [project status](status.md) for the remaining acceptance boundaries.

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

Keep the stock icon allocation stable even while a gift is hidden. Burned Tower
B1F therefore always reserves Cyndaquil's graphics; its object callback
controls visibility. Native Continue and submenu redraws must not move the tile
slots used by Cyndaquil, Eusine, or the beasts.

Cianwood's fixed-length outdoor list replaces the unused Tauros icon with the
same-size Totodile icon. Totodile uses fixed-facing Pokémon animation because
its two frames cannot supply ordinary swimming directions. Both changes remain
custom-only. See [coverage](../tests/coverage.md#johto-starter-gifts-phase-4)
and the
[older-save procedure](playtesting/johto.md#johto-starter-gifts-phase-4).

## 2026-08-11 — Gate Ruins gifts on both ancient conditions

Kabuto, Omanyte, and Aerodactyl hidden rooms require both their picture puzzle
and stock hidden-wall condition. Escape Rope, Water Stone, and Flash may record
the wall event first, but the wall and clue stay closed until the picture is
solved. Apply the same predicate to scenes, tile callbacks, right-wall text,
and Kabuto's scientist; preserve the independent picture-floor drop and all
four preceding item-room rewards. Ho-Oh remains stock.

Each word-room gift sits immediately after its final inscription glyph, acting
as a period. Use independent success events and the stock `givepoke`
party/current-box transaction. Decline or full storage keeps the gift
retryable; success completes it permanently. Completion is the object hide
flag, while the callback derives its sprite before object masks load without
mutating saved state. The interaction independently checks prerequisites and
completion. Omanyte's Water Stone condition consumes nothing and accepts a Bag
or held Stone. Exact species, levels, locations, and renewal paths live in the
[acquisition ledger](pokemon-acquisition.md).

Kim's Route 14 trade changes only the offered species/name to same-level
Girafarig `GIRAFY`; retain the Chansey request, table index, dialogue, DVs,
Gold Berry, OT identity, and gender rule. References retain Aerodactyl `AEROY`. Breeding renews Girafarig; Phase 9 deliberately adds no competing wild
source.

No retained player-progression saves predated this change. Do not add scene
normalization, trade migration, or save-version scaffolding for hypothetical
old progress.

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
Dragon Shrine training hint. Preserve their stock dialogue, weekday checks,
weekly cadence, and every reference-build byte. Phase 12 supersedes the earlier
rematch party data.

Phase 8 sets only Silver's released-bird availability state. Phase 9 owns all
physical Articuno, Zapdos, and Moltres locations, encounter and retry behavior,
Oak's third bird, capture, and hints. Phase 12 owns Silver's full balance pass.
The four event IDs fit the existing 2048-bit event block, so no RAM, SRAM,
scene-layout, or reference-build compatibility boundary changes.

## 2026-08-19 — Accept the complete Phase 8 manual matrix

This historical scheduling or acceptance record is preserved in
[decision history](history/decisions.md#2026-08-19--accept-the-complete-phase-8-manual-matrix). Use [project status](status.md) for the remaining acceptance boundaries.

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
box must not set the gift event or repeat a completed service. The Blaine
return fact is set before the gift attempt so storage failure never repeats the
investigation. See [Kanto map art](assets.md#kanto-map-art) for the cache and
staircase layout.

## 2026-08-20 — Open one unattended Safari preserve through existing Fuchsia state

Reuse `SafariZoneBeta` as one unattended outdoor Park-tileset preserve. The
Warden's granddaughter permanently opens the north maintenance gate after both
her conversation and the Soul Badge, in either order; her first-contact text
states the badge requirement directly.

Use ordinary wild battles, Bag, Poké Balls, experience, and escape rules. There
is no clerk, fee, timer, step counter, Safari Balls, bait/rock system, prize,
or reopening ceremony. Grass and water rates remain 10 percent, with all-time
land slots and Remoraid in both common water slots. The
[acquisition ledger](pokemon-acquisition.md) and
[Phase 12 contract](phase-12-balance.md) own current encounters;
[history](history/decisions.md#superseded-numeric-targets) retains the original
levels. Two visible item balls reward exploration.

Keep the area compact and use the [custom Park art](assets.md#kanto-map-art).
Multi-area ports and official Safari mechanics remain deferred.

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

See [Kanto map art](assets.md#kanto-map-art) for the Seafoam ice lanes and
Generator Annex presentation.

## 2026-08-23 — Align Kanto starter-gifting leaders in the Phase 12 balance pass

Phase 12 adds the final evolution of each gifted Kanto starter to the
corresponding leader's battle party: Venusaur for Erika, Blastoise for Misty,
and Charizard for Blaine. This makes each Phase 9 gift read as a Pokémon line
the leader personally trains rather than an unrelated reward. Phase 12 owns the
exact level, moves, party position, and which existing party member—if any—is
replaced; evaluate future changes with the complete Kanto difficulty curve. Do
not change the Phase 9 service prerequisites, gift level, leader OT assignment,
or retry behavior as part of that roster work.

## 2026-08-26 — Reuse unused Cave blocks for three lab fixtures

Reuse three unused Cave blocks and existing source art for the lab furniture.
Keep the 96-tile graphics sheet and 64-block table dimensions unchanged and
preserve all other blocks and reference assets. Cave and Dark Cave share block,
collision, and palette tables; the furniture is valid only with Cave graphics.
Phase 10 owns its Cerulean Cave placement and interactions.

Reclaiming the retired grass graphic and using optimized compression only for
the custom asset avoids bank relocation. Preserve Victory Road pit block `$3f`. The [asset guide](assets.md#cave-fixture-design-constraints) owns exact block
and tile allocations, artwork, compression, and capacity limits; its
[procedure](assets.md#regenerate-and-validate-the-cave-lab-fixtures) owns
regeneration.

## 2026-08-26 — Import standing-only Giovanni artwork from Pokémon Red

Import Pokémon Red's three standing Giovanni poses unchanged and use the
existing standing-sprite loader. Giovanni may turn, but must never walk or use
automatic trainer approach: the loader's second graphics region has no walking
frames. The cave victory blackout removes the crew without walking
choreography.

Append the custom ID and bank section without changing existing sprite IDs,
stock banks, engine code, or save layout. The
[asset guide](assets.md#giovanni-standing-sprite) owns provenance and
reproduction;
[registration constraints](assets.md#giovanni-sprite-registration) own the
exact allocation, palette, and bank reserve.

## 2026-09-06 — Finish Project Mew in one derived-access Cerulean Cave

Crystal Legends restores Cerulean Cave as custom map group 7, map 19: one
15-by-18-block Cave-tileset floor entered from the ordinary Route 4 warp at
`(38, 3)` and exited at `(21, 33)`. The accepted terrain replaces the unused
beta-cave payload at the same size. Route 4 and Cerulean City use same-size
custom block variants, retain their stock connection, and preserve the hidden
Berserk Gene.

Access requires `EVENT_PROJECT_MEW_RESOLVED`, `EVENT_SILVER_BIRD_RELEASED`,
and at least 14 badges. Do not store a separate cave-open fact. Route 4's
object callback writes the guard map object's sprite to `SPRITE_ROCKET` or zero
before visible object structs are initialized; `appear` /`disappear` cannot
correctly derive an eventless object's initial visibility at that callback
boundary. This keeps eligibility order-independent and reconstructs it on map
load and native Continue.

The cave holds six Rocket remnant trainers with independent defeat flags, but
all six object masks and Giovanni's object mask use `EVENT_BEAT_GIOVANNI` so the
post-boss blackout removes the complete crew even when a remnant was skipped.
Giovanni is a stationary script object and a dedicated custom-only `BOSS`
class with a six-Pokémon party. The displayed `BOSS GIOVANNI` label fits the
18-character battle textbox, including punctuation in loss messages. Set
`EVENT_GIOVANNI_RETURNED` before the first battle; set `EVENT_BEAT_GIOVANNI`
only after victory and the reload, then remove all seven Rocket objects without
walking choreography. A loss therefore preserves a truthful retry state.

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

The [asset guide](assets.md#giovanni-trainer-portrait) owns Giovanni's
portrait, its source hashes, and the custom-only lossless Omastar recompression
that creates pointer space without moving the original picture.

## 2026-09-07 — Close the endgame with durable Red and one-time Oak victories

Crystal Legends keeps Red at Mt. Silver with Pikachu, Espeon, Snorlax,
Venusaur, Charizard, and Blastoise, with max class DVs. His initial numeric
targets were superseded by the
[Phase 12 package](#2026-09-15--implement-the-accepted-phase-12-trainer-package); the current [trainer contract](../tests/contracts/phase_12_trainers.json)
owns levels and moves. `EVENT_RED_IN_MT_SILVER` remains only the current
object-visibility flag so later Hall of Fame clears can restore a Red rematch.
New event 1491, `EVENT_BEAT_RED`, records the first successful victory
permanently and is never cleared by rematch setup.

After Mt. Silver opens, Oak continues to run the stock Pokédex rating before
the new state response. His only live unlock is `EVENT_BEAT_RED` plus at least
240 of 251 caught species; no legendary, starter, Ruins, Giovanni, Project Mew,
or other story fact is an additional requirement. Declining or losing changes
nothing. Oak uses the existing `POKEMON_PROF` presentation with two Full
Restores, full leader-grade AI, max DVs, and Champion music. Three
starter-selected parties use Charizard for an Articuno player, Venusaur for a
Zapdos player, or Blastoise for a Moltres player; all finish with Tyranitar.
Phase 12 owns the exact levels and moves; the identities and branch mapping
remain story locks. [History](history/decisions.md#superseded-numeric-targets)
retains the provisional numbers.

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
clear. Presentation, dialogue, credits pacing, and natural boss difficulty use
the [manual endgame matrix](playtesting/endgame.md); acceptance is recorded in
[project status](status.md).

## 2026-09-15 — Apply fixed Kanto wild levels without changing habitats

Use fixed Kanto encounter levels while preserving species, ordered slots, time
windows, rates, fishing, and encounter mechanics. Preserve Johto, pre-League
routes, oceans, Mt. Silver, Cerulean Cave, scripted encounters, and gift
levels. This raises recruitment levels without changing habitats or
guaranteeing training XP; the edits add no data bytes.

The [acquisition ledger](pokemon-acquisition.md) owns species availability and
current levels. The
[balance guide and wild contract](phase-12-balance.md#encounter-and-xp-contracts)
own exact table targets. These replace the original Phase 9 levels, not its
access or capture rules.

## 2026-09-15 — Implement the accepted Phase 12 trainer package

Apply the accepted fixed trainer package rather than global level boosts or
dynamic badge scaling. Johto leaders retain their stock partners and gain one
each; the four Elite Four teams gain a sixth. Ordinary Kanto gym trainers gain
10 levels and listed routes gain 8, capped one below their geographic gym ace.
Colette is the sole ordinary authored-move exception. Preserve Lance, Blue,
Elder Li, ordinary Johto, pre-League Routes 26/27, and shared S.S. Aqua
parties.

Silver's release scene still precedes the bird-free rematch; Ursaring fills its
sixth slot and Crobat is last and highest-level. Golbat remains through Mt.
Moon. Preserve class items, AI, DVs, rewards logic, story scripts, gifts,
player learnsets, save layout, and all reference artifacts. Only Kiyo and
Colette convert automatic parties to authored moves; Cal remains daily with
natural moves.

The [balance guide](phase-12-balance.md) and linked trainer contract own exact
ordered members, levels, moves, formats, XP totals, and bank reserve. Their
numeric targets supersede the provisional Phase 8–11 parties; story identities,
branches, and cadence remain unchanged. Automated data/state checks and
[natural-play difficulty](playtesting/endgame.md#trainer-and-wild-balance-phase-12)
are separate gates. Optional recruits, unlocks, later victory rewards, and
historical player-level forecasts do not establish readiness.

## 2026-09-17 — Finalize Elm's starter choice only after delivery

All three legendary-bird choices use the native `givepoke` result before
removing their Poké Ball, recording the chosen species, or announcing receipt.
A full party and full current box show a storage refusal and leave every
choice and story gate unchanged, including after native Save/Continue. Party
or current-box delivery proceeds through the existing Elm directions once.
Keep this guard custom-only and preserve reference-ROM bytes.

The
[legendary starter coverage](../tests/coverage.md#legendary-starter-gifts-phase-1)
owns refusal, retry, ordinary delivery, and branch regression coverage.

## 2026-09-23 — Attach Lucky Eggs to the three Johto world gifts

Chikorita, Cyndaquil, and Totodile each arrive holding a Lucky Egg through the
existing `givepoke` item argument. Keep their levels, prerequisites, completion
flags, and party/current-box delivery behavior unchanged. Refusal grants
neither a Pokémon nor an item. The held item persists through native saves
and can be transferred normally, making three early 1.5× EXP items available.

The custom `GivePoke` box path reopens SRAM around the held-item write:
`SendMonIntoBox` has already closed it, so the original write silently lost
scripted held items on direct box delivery. Keep the reference engine unchanged.

Only future gift receipts gain these items; do not retroactively edit already
collected Pokémon or change the save layout. The changes remain custom-only.
The [Phase 4 coverage](../tests/coverage.md#johto-starter-gifts-phase-4) owns
delivery, persistence, and refusal. The
[manual balance matrix](playtesting/endgame.md#trainer-and-wild-balance-phase-12)
covers the earlier EXP boosts.
