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
the one-time Oak handoff. The user has deliberately deferred the remaining
playthrough-dependent checks: progression through Falkner, later Silver and
balance sampling, and the Phase 2 evolution/item/Celebi matrix. Do not describe
v0.1, Phase 2, or the complete project as fully playtest-certified until those
remaining matrices pass. The exact emulator/version was not supplied with this
test report and should be appended if it becomes available.

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

The Chikorita and Totodile objects use their completion events directly.
Cyndaquil's object-event flag stays `-1`; a map callback owns its visibility so
the Pokémon can appear in the same scene as the beast release without mutating
the completion event. The pharmacist adds a discoverability hint after giving
the SecretPotion, but Phase 4 never consumes that item or changes Amphy,
lighthouse, gym, roamer, or downstream Suicune state.

The three overworld identifiers reuse the stock Pokémon-icon loader and add no
graphics assets. Keep every event flag, sprite entry, map object, script, and
hint behind `_CRYSTALLEGENDS`; reference builds must contain none of this
behavior and must continue to reproduce exactly.

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
Its callback controls visibility without mutating saved state, and the
preceding item room retains all four stock item balls.

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
table makes level-20 Mareep, level-24 Vulpix, and level-22 Mankey common; a
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
