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

## 2026-08-09 — Reserve ordinary missing families for the Safari Zone

Mareep, Vulpix, Mankey, Girafarig, and Remoraid and their dependent evolutions
belong to the Phase 9 unattended Safari Zone. The canonical acquisition ledger
must identify the reservation now, but the exact Safari area, level, encounter
rate, and slot remain TBD until Phase 9. Phase 2 must not add substitute Johto
encounters for these families.

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
