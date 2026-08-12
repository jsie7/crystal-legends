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
identify the reservation now, but the exact Safari area, level, encounter rate,
and slot remain TBD until Phase 9. Phase 2 must not add substitute Johto
encounters for these families. Girafarig was originally included in this
reservation; Phase 5 instead makes Kim's Route 14 trade its canonical source,
with any future Safari appearance optional.

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
renewable through breeding after this one-time trade, so Phase 9 may add a wild
Safari encounter for flavor but no longer needs one for 251-species completion.

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
concept, and Mahogany's existing scientists, office computers, and transmitter
reveal the subject and its transfer. The final Radio Tower Executive records
that Giovanni received the research before the battle begins, so losing cannot
rewind that fact.

After the Executive is defeated, a new 5-by-4-block transmitter annex pauses
the stock Director and Clear Bell cleanup. Its terminal requires confirmation
of one permanent outcome: reverse the sequence and retain Mew, or stabilize the
altered Mewtwo form. Store data sent, decision resolved, transformed outcome,
and capture as four independent event facts; do not derive the branch from the
party or Pokédex. The existing Executive victory event owns annex access.

The selected subject is a normal level-30 wild battle that remains available
after knockout, escape, or player defeat and starts each retry at full HP with
no status. Capture alone removes it, but capture is not required to resume the
stock Radio Tower resolution. The generic caught-result query is custom-only;
reference builds retain their exact Celebi behavior and bytes. Do not add
pre-Phase-7 save migration or broaden this phase into Rocket-team balancing.
