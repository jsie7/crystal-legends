# Pokémon Acquisition Ledger

This ledger is the canonical single-save acquisition inventory for Crystal
Legends. It covers National Pokédex numbers 001 through 251 exactly once.

The Phase 2 methods recorded below are implementation-complete but still await
the deferred emulator matrix scheduled after the Phase 3 cheat/debug menu.

`Existing` means the method was inherited from the upstream game. `Phase N`
identifies a method implemented by that Crystal Legends milestone. `Reserved
Phase N` identifies planned content that is not yet
obtainable; its source names the owning phase and intended checked-in
destination. Reserved encounter details may be explicitly `TBD`, but no row may
have a blank method, location, availability, or source.

`Renewable` describes whether another specimen can be acquired in the same save
after the first successful acquisition. A breedable one-time gift is renewable
after it has been received. For one-time encounters, the entry also states what
happens after a failed capture.

The ledger does not count another cartridge, Link Cable, Mystery Gift, mobile
data, an external distribution, or the optional cheat menu.

| Dex | Species | Method | Location / requirement | Earliest point | Availability | Renewable | Source |
|---:|---|---|---|---|---|---|---|
| 001 | Bulbasaur | Gift | Level 28 from Erika after the Rainbow Badge and the retryable Celadon pond Muk task | Kanto | Phase 9 | Yes after the gift through breeding | `maps/CeladonGym.asm`; `maps/CeladonCity.asm` |
| 002 | Ivysaur | Evolution | Level up the Phase 9 Bulbasaur once; it is already above level 16 | Kanto | Phase 9 | Yes | `data/pokemon/evos_attacks.asm`; Phase 9 Bulbasaur source |
| 003 | Venusaur | Evolution | Ivysaur at level 32 | Kanto | Phase 9 | Yes | `data/pokemon/evos_attacks.asm`; Phase 9 Bulbasaur source |
| 004 | Charmander | Gift | Level 28 from Blaine after the Volcano Badge, survivor clue, recovery of `BLAINE'S LOG`, and return of the log | Kanto | Phase 9 | Yes after the gift through breeding | `maps/SeafoamGym.asm`; `maps/CinnabarIsland.asm`; `maps/CinnabarPokecenter1F.asm` |
| 005 | Charmeleon | Evolution | Level up the Phase 9 Charmander once; it is already above level 16 | Kanto | Phase 9 | Yes | `data/pokemon/evos_attacks.asm`; Phase 9 Charmander source |
| 006 | Charizard | Evolution | Charmeleon at level 36 | Kanto | Phase 9 | Yes | `data/pokemon/evos_attacks.asm`; Phase 9 Charmander source |
| 007 | Squirtle | Gift | Level 28 from Misty after the Cascade Badge and restored Kanto power | Kanto | Phase 9 | Yes after the gift through breeding | `maps/CeruleanGym.asm`; existing Machine Part/Power Plant arc |
| 008 | Wartortle | Evolution | Level up the Phase 9 Squirtle once; it is already above level 16 | Kanto | Phase 9 | Yes | `data/pokemon/evos_attacks.asm`; Phase 9 Squirtle source |
| 009 | Blastoise | Evolution | Wartortle at level 36 | Kanto | Phase 9 | Yes | `data/pokemon/evos_attacks.asm`; Phase 9 Squirtle source |
| 010 | Caterpie | Wild | Ilex Forest, morning or day | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 011 | Metapod | Evolution or wild | Caterpie at level 7; Ilex Forest | After Badge 2 | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 012 | Butterfree | Evolution | Metapod at level 10 | After Badge 2 | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 013 | Weedle | Wild | Ilex Forest, morning or day | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 014 | Kakuna | Evolution or wild | Weedle at level 7; Ilex Forest | After Badge 2 | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 015 | Beedrill | Evolution | Kakuna at level 10 | After Badge 2 | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 016 | Pidgey | Wild | National Park or early Johto routes | Early Johto | Existing | Yes | `data/wild/johto_grass.asm` |
| 017 | Pidgeotto | Evolution or wild | Pidgey at level 18; Route 37 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 018 | Pidgeot | Evolution | Pidgeotto at level 36 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 019 | Rattata | Wild | Sprout Tower and early Johto | Before Badge 1 | Existing | Yes | `data/wild/johto_grass.asm` |
| 020 | Raticate | Evolution or wild | Rattata at level 20; Burned Tower | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 021 | Spearow | Wild | Route 33 or Headbutt trees | Before Badge 2 | Existing | Yes | `data/wild/johto_grass.asm`; `data/wild/treemons.asm` |
| 022 | Fearow | Evolution or wild | Spearow at level 20; Route 42 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 023 | Ekans | Wild | Route 32 | Before Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 024 | Arbok | Evolution or wild | Ekans at level 22; Route 42 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 025 | Pikachu | Wild or prize | Route 2; Celadon Game Corner | Kanto | Existing | Yes | `data/wild/kanto_grass.asm`; `maps/CeladonGameCornerPrizeRoom.asm` |
| 026 | Raichu | Evolution | Use Thunder Stone on Pikachu | Kanto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 027 | Sandshrew | Wild | Union Cave 1F | Before Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 028 | Sandslash | Evolution or wild | Sandshrew at level 22; Victory Road | Late Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 029 | Nidoran♀ | Wild | National Park | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 030 | Nidorina | Evolution or wild | Nidoran♀ at level 16; Route 13 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 031 | Nidoqueen | Evolution | Use Moon Stone on Nidorina | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 032 | Nidoran♂ | Wild | National Park | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 033 | Nidorino | Evolution or wild | Nidoran♂ at level 16; Route 13 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 034 | Nidoking | Evolution | Use Moon Stone on Nidorino | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 035 | Clefairy | Wild | Mt. Moon | Kanto | Existing | Yes | `data/wild/kanto_grass.asm` |
| 036 | Clefable | Evolution | Use Moon Stone on Clefairy | Kanto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 037 | Vulpix | Wild | Level 24 in unattended SafariZoneBeta grass; one of the three common slots at morning, day, and night | Kanto | Phase 9 | Yes | `data/wild/kanto_grass.asm`; `maps/SafariZoneBeta.asm` |
| 038 | Ninetales | Evolution | Use Fire Stone on Phase 9 Vulpix | Kanto | Phase 9 | Yes | `data/pokemon/evos_attacks.asm`; Phase 9 Vulpix source |
| 039 | Jigglypuff | Wild | Route 34 | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 040 | Wigglytuff | Evolution | Use Moon Stone on Jigglypuff | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 041 | Zubat | Wild | Burned Tower and many caves | Before Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 042 | Golbat | Evolution or wild | Zubat at level 22; Union Cave B2F | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 043 | Oddish | Wild | Ilex Forest at night | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 044 | Gloom | Evolution or wild | Oddish at level 21; Route 24 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 045 | Vileplume | Evolution | Use Leaf Stone on Gloom | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 046 | Paras | Wild | Ilex Forest | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 047 | Parasect | Evolution or wild | Paras at level 24; Silver Cave | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 048 | Venonat | Wild | National Park or Route 43 at night | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 049 | Venomoth | Evolution or wild | Venonat at level 31; Route 43 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 050 | Diglett | Wild | Diglett's Cave | Kanto | Existing | Yes | `data/wild/kanto_grass.asm` |
| 051 | Dugtrio | Evolution or wild | Diglett at level 26; Diglett's Cave | Kanto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 052 | Meowth | Wild | Route 38 | After Badge 3 | Existing | Yes | `data/wild/johto_grass.asm` |
| 053 | Persian | Evolution or wild | Meowth at level 28; Route 7 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 054 | Psyduck | Wild | National Park or via Surf | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm`; `data/wild/johto_water.asm` |
| 055 | Golduck | Evolution or wild | Psyduck at level 33; Silver Cave | Late Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 056 | Mankey | Wild | Level 22 in unattended SafariZoneBeta grass; one of the three common slots at morning, day, and night | Kanto | Phase 9 | Yes | `data/wild/kanto_grass.asm`; `maps/SafariZoneBeta.asm` |
| 057 | Primeape | Evolution | Mankey at level 28 | Kanto | Phase 9 | Yes | `data/pokemon/evos_attacks.asm`; Phase 9 Mankey source |
| 058 | Growlithe | Wild | Route 35 | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 059 | Arcanine | Evolution | Use Fire Stone on Growlithe | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 060 | Poliwag | Wild or fishing | Route 30 and pond fishing groups | Early Johto | Existing | Yes | `data/wild/johto_grass.asm`; `data/wild/fish.asm` |
| 061 | Poliwhirl | Evolution or wild | Poliwag at level 25; Route 44 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 062 | Poliwrath | Evolution | Use Water Stone on Poliwhirl | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 063 | Abra | Wild or prize | Route 34; Goldenrod Game Corner | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm`; `maps/GoldenrodGameCorner.asm` |
| 064 | Kadabra | Evolution or wild | Abra at level 16; Route 8 | After Badge 2 | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 065 | Alakazam | Evolution | Kadabra at level 36 | Mid-Johto | Phase 2 | Yes | `data/pokemon/evos_attacks.asm` |
| 066 | Machop | NPC trade or wild | Trade Abra in Goldenrod; Mt. Mortar | After Badge 2 | Existing | Yes through breeding or wild capture | `data/events/npc_trades.asm`; `data/wild/johto_grass.asm` |
| 067 | Machoke | Evolution or wild | Machop at level 28; Mt. Mortar | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 068 | Machamp | Evolution | Machoke at level 36 | Mid-Johto | Phase 2 | Yes | `data/pokemon/evos_attacks.asm` |
| 069 | Bellsprout | Wild | Route 31 | Before Badge 1 | Existing | Yes | `data/wild/johto_grass.asm` |
| 070 | Weepinbell | Evolution or wild | Bellsprout at level 21; Route 44 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 071 | Victreebel | Evolution | Use Leaf Stone on Weepinbell | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 072 | Tentacool | Wild | Surf on Johto sea routes | After Surf | Existing | Yes | `data/wild/johto_water.asm` |
| 073 | Tentacruel | Evolution or wild | Tentacool at level 30; Johto sea routes | After Surf | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_water.asm` |
| 074 | Geodude | Wild | Union Cave | Before Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 075 | Graveler | Evolution or wild | Geodude at level 25; Mt. Mortar | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 076 | Golem | Evolution | Graveler at level 36 | Mid-Johto | Phase 2 | Yes | `data/pokemon/evos_attacks.asm` |
| 077 | Ponyta | Wild | Route 22 or Route 28 | Kanto | Existing | Yes | `data/wild/kanto_grass.asm` |
| 078 | Rapidash | Evolution or wild | Ponyta at level 40; Silver Cave outside | Kanto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 079 | Slowpoke | Wild | Slowpoke Well | Before Badge 2 | Existing | Yes | `data/wild/johto_grass.asm`; `data/wild/johto_water.asm` |
| 080 | Slowbro | Evolution or wild | Slowpoke at level 37; Slowpoke Well B2F | Late Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_water.asm` |
| 081 | Magnemite | Wild | Route 38 | After Badge 3 | Existing | Yes | `data/wild/johto_grass.asm` |
| 082 | Magneton | Evolution or NPC trade | Magnemite at level 30; trade Dugtrio | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/events/npc_trades.asm` |
| 083 | Farfetch'd | Wild | Route 43 | Mid-Johto | Existing | Yes | `data/wild/johto_grass.asm` |
| 084 | Doduo | Wild | Route 22 or Route 26 | Kanto | Existing | Yes | `data/wild/kanto_grass.asm` |
| 085 | Dodrio | Evolution or NPC trade | Doduo at level 31; trade female Dragonair | Kanto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/events/npc_trades.asm` |
| 086 | Seel | Wild | Whirl Islands | After Surf | Existing | Yes | `data/wild/johto_grass.asm` |
| 087 | Dewgong | Evolution | Seel at level 34 | Late Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 088 | Grimer | Wild | Route 16 | Kanto | Existing | Yes | `data/wild/kanto_grass.asm` |
| 089 | Muk | Evolution or wild | Grimer at level 38; Route 16 | Kanto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 090 | Shellder | Fishing | Shore and ocean fishing groups | After obtaining a rod | Existing | Yes | `data/wild/fish.asm` |
| 091 | Cloyster | Evolution | Use Water Stone on Shellder | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 092 | Gastly | Wild | Sprout Tower at night | Before Badge 1 | Existing | Yes | `data/wild/johto_grass.asm` |
| 093 | Haunter | Evolution or wild | Gastly at level 25; Rock Tunnel | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 094 | Gengar | Evolution | Haunter at level 36 | Mid-Johto | Phase 2 | Yes | `data/pokemon/evos_attacks.asm` |
| 095 | Onix | NPC trade or wild | Trade Bellsprout in Violet; Union Cave | Before Badge 2 | Existing | Yes | `data/events/npc_trades.asm`; `data/wild/johto_grass.asm` |
| 096 | Drowzee | Wild | Route 34 | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 097 | Hypno | Evolution or wild | Drowzee at level 26; Route 11 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 098 | Krabby | Wild or fishing | Whirl Islands; shore fishing groups | After obtaining a rod | Existing | Yes | `data/wild/johto_grass.asm`; `data/wild/fish.asm` |
| 099 | Kingler | Evolution | Krabby at level 28 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 100 | Voltorb | NPC trade or static | Trade Krabby; Team Rocket Base | Mid-Johto | Existing | Yes through breeding | `data/events/npc_trades.asm`; `maps/TeamRocketBaseB1F.asm` |
| 101 | Electrode | Evolution or static | Voltorb at level 30; Team Rocket Base | Mid-Johto | Existing | Yes through evolution | `data/pokemon/evos_attacks.asm`; `maps/TeamRocketBaseB2F.asm` |
| 102 | Exeggcute | Wild | Headbutt trees | After obtaining Headbutt | Existing | Yes | `data/wild/treemons.asm`; `data/wild/treemon_maps.asm` |
| 103 | Exeggutor | Evolution | Use Leaf Stone on Exeggcute | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 104 | Cubone | Prize or wild | Goldenrod Game Corner; Rock Tunnel | After Badge 2 | Existing | Yes through breeding or wild capture | `maps/GoldenrodGameCorner.asm`; `data/wild/kanto_grass.asm` |
| 105 | Marowak | Evolution or wild | Cubone at level 28; Rock Tunnel | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 106 | Hitmonlee | Evolution | Tyrogue at level 20 with Attack above Defense | Late Johto | Existing | Yes through breeding Tyrogue | `data/pokemon/evos_attacks.asm`; `maps/MountMortarB1F.asm` |
| 107 | Hitmonchan | Evolution | Tyrogue at level 20 with Defense above Attack | Late Johto | Existing | Yes through breeding Tyrogue | `data/pokemon/evos_attacks.asm`; `maps/MountMortarB1F.asm` |
| 108 | Lickitung | Wild | Route 44 | Late Johto | Existing | Yes | `data/wild/johto_grass.asm` |
| 109 | Koffing | Wild or static | Burned Tower; Team Rocket Base | Mid-Johto | Existing | Yes | `data/wild/johto_grass.asm`; `maps/TeamRocketBaseB1F.asm` |
| 110 | Weezing | Evolution or wild | Koffing at level 35; Burned Tower B1F | Late Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 111 | Rhyhorn | Wild | Victory Road | Before League | Existing | Yes | `data/wild/kanto_grass.asm` |
| 112 | Rhydon | Evolution or wild | Rhyhorn at level 42; Victory Road | Before League | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 113 | Chansey | Wild | Route 13 | Kanto | Existing | Yes | `data/wild/kanto_grass.asm` |
| 114 | Tangela | Wild | Route 44 | Late Johto | Existing | Yes | `data/wild/johto_grass.asm` |
| 115 | Kangaskhan | Wild | Rock Tunnel B1F | Kanto | Existing | Yes | `data/wild/kanto_grass.asm` |
| 116 | Horsea | Wild or fishing | Whirl Islands; ocean fishing groups | After Surf | Existing | Yes | `data/wild/johto_water.asm`; `data/wild/fish.asm` |
| 117 | Seadra | Evolution or wild | Horsea at level 32; Whirl Islands | Late Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_water.asm` |
| 118 | Goldeen | Wild or fishing | Mt. Mortar water; lake fishing groups | After Surf | Existing | Yes | `data/wild/johto_water.asm`; `data/wild/fish.asm` |
| 119 | Seaking | Evolution or wild | Goldeen at level 33; Mt. Mortar water | Late Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_water.asm` |
| 120 | Staryu | Fishing | Ocean fishing groups at night | After obtaining the appropriate rod | Existing | Yes | `data/wild/fish.asm` |
| 121 | Starmie | Evolution | Use Water Stone on Staryu | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 122 | Mr. Mime | Wild | Route 21 | Kanto | Existing | Yes | `data/wild/kanto_grass.asm` |
| 123 | Scyther | Wild | Bug-Catching Contest | After Badge 2 | Existing | Yes | `data/wild/bug_contest_mons.asm` |
| 124 | Jynx | Wild | Ice Path | Before Badge 8 | Existing | Yes | `data/wild/johto_grass.asm` |
| 125 | Electabuzz | Wild | Route 10 North | Kanto | Existing | Yes | `data/wild/kanto_grass.asm` |
| 126 | Magmar | Wild | Silver Cave Room 1 | After 16 badges | Existing | Yes | `data/wild/johto_grass.asm` |
| 127 | Pinsir | Wild | Bug-Catching Contest | After Badge 2 | Existing | Yes | `data/wild/bug_contest_mons.asm` |
| 128 | Tauros | Wild | Route 38 | After Badge 3 | Existing | Yes | `data/wild/johto_grass.asm` |
| 129 | Magikarp | Fishing or wild | Any common fishing group | Early Johto | Existing | Yes | `data/wild/fish.asm`; `data/wild/johto_water.asm` |
| 130 | Gyarados | Evolution, wild, or static | Magikarp at level 20; Lake of Rage | Mid-Johto | Existing | Yes through evolution | `data/pokemon/evos_attacks.asm`; `maps/LakeOfRage.asm` |
| 131 | Lapras | Static encounter | Union Cave B2F on Friday | After Surf | Existing | Yes; weekly encounter | `maps/UnionCaveB2F.asm` |
| 132 | Ditto | Wild | Route 34 | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 133 | Eevee | Gift | Bill in Goldenrod City | After meeting Bill | Existing | Yes after gift through breeding | `maps/BillsFamilysHouse.asm` |
| 134 | Vaporeon | Evolution | Use Water Stone on Eevee | Mid-Johto | Existing | Yes through breeding Eevee | `data/pokemon/evos_attacks.asm` |
| 135 | Jolteon | Evolution | Use Thunder Stone on Eevee | Mid-Johto | Existing | Yes through breeding Eevee | `data/pokemon/evos_attacks.asm` |
| 136 | Flareon | Evolution | Use Fire Stone on Eevee | Mid-Johto | Existing | Yes through breeding Eevee | `data/pokemon/evos_attacks.asm` |
| 137 | Porygon | Prize | Celadon Game Corner | Kanto | Existing | Repeatable prize purchase | `maps/CeladonGameCornerPrizeRoom.asm` |
| 138 | Omanyte | World gift | Level 26 after the final glyph in the Omanyte word room, reached after solving the picture and bringing a Water Stone into the chamber | After Badge 4 | Phase 5 | Yes through breeding after the one-time gift | `maps/RuinsOfAlphOmanyteChamber.asm`; `maps/RuinsOfAlphOmanyteWordRoom.asm` |
| 139 | Omastar | Evolution | Omanyte at level 40 | After Badge 4 source; later evolution | Phase 5 | Yes through breeding Omanyte | `data/pokemon/evos_attacks.asm`; Phase 5 Omanyte gift |
| 140 | Kabuto | World gift | Level 10 after the final glyph in the Kabuto word room, reached after solving the picture and using Escape Rope in the chamber | Before Badge 1 | Phase 5 | Yes through breeding after the one-time gift | `maps/RuinsOfAlphKabutoChamber.asm`; `maps/RuinsOfAlphKabutoWordRoom.asm` |
| 141 | Kabutops | Evolution | Kabuto at level 40 | Before Badge 1 source; later evolution | Phase 5 | Yes through breeding Kabuto | `data/pokemon/evos_attacks.asm`; Phase 5 Kabuto gift |
| 142 | Aerodactyl | World gift | Level 23 after the final glyph in the Aerodactyl word room, reached after solving the picture and using Flash in the chamber | After Badge 4 | Phase 5 | Yes through breeding after the one-time gift | `maps/RuinsOfAlphAerodactylChamber.asm`; `maps/RuinsOfAlphAerodactylWordRoom.asm` |
| 143 | Snorlax | Static encounter | Vermilion City after restoring the Pokégear radio | Kanto | Existing | No; stock event ends after battle | `maps/VermilionCity.asm` |
| 144 | Articuno | Starter or one-time encounter | Elm starter if selected; otherwise level 60 in the compact Seafoam cave off Route 20 when it is Oak's handoff bird or Silver's released bird | Start or Kanto | Phase 1 / Phase 8 / Phase 9 | No; exactly one source exists on each starter branch | `maps/ElmsLab.asm`; `maps/ElmsLabSilverArc.asm`; `maps/SeafoamIslandsCave.asm`; `maps/Phase9LegendaryBirds.asm` |
| 145 | Zapdos | Starter or one-time encounter | Elm starter if selected; otherwise level 60 in the Power Plant Generator Annex after power restoration when it is Oak's handoff bird or Silver's released bird | Start or Kanto | Phase 1 / Phase 8 / Phase 9 | No; exactly one source exists on each starter branch | `maps/ElmsLab.asm`; `maps/ElmsLabSilverArc.asm`; `maps/PowerPlantGeneratorAnnex.asm`; `maps/Phase9LegendaryBirds.asm` |
| 146 | Moltres | Starter or one-time encounter | Elm starter if selected; otherwise level 60 on Victory Road's upper east shelf after Hall of Fame when it is Oak's handoff bird or Silver's released bird | Start or Kanto | Phase 1 / Phase 8 / Phase 9 | No; exactly one source exists on each starter branch | `maps/ElmsLab.asm`; `maps/ElmsLabSilverArc.asm`; `maps/VictoryRoad.asm`; `maps/Phase9LegendaryBirds.asm` |
| 147 | Dratini | Gift, wild, or fishing | Dragon's Den gift and encounters | After Badge 8 | Existing | Yes | `maps/DragonShrine.asm`; `data/wild/johto_water.asm`; `data/wild/fish.asm` |
| 148 | Dragonair | Evolution or NPC-trade input | Dratini at level 30; Dragon's Den fishing | After Badge 8 | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/fish.asm` |
| 149 | Dragonite | Evolution | Dragonair at level 55 | Post-League training | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 150 | Mewtwo | Story encounter | Level 30 in the Radio Tower transmitter annex after STABILIZE SEQUENCE; level 70 in Cerulean Cave after defeating Giovanni if REVERSE SEQUENCE was chosen | Late Johto or Kanto | Phase 7 / Phase 10 | No; each branch has one capture-only encounter that retries until captured | `maps/RadioTowerTransmitterAnnex.asm`; `maps/CeruleanCave.asm` |
| 151 | Mew | Story encounter | Level 30 in the Radio Tower transmitter annex after REVERSE SEQUENCE; level 70 in Cerulean Cave after defeating Giovanni if STABILIZE SEQUENCE was chosen | Late Johto or Kanto | Phase 7 / Phase 10 | No; each branch has one capture-only encounter that retries until captured | `maps/RadioTowerTransmitterAnnex.asm`; `maps/CeruleanCave.asm` |
| 152 | Chikorita | Gift event | Level 14 at the Ilex Forest shrine after receiving Cut | After Badge 2 | Phase 4 | Yes after gift through breeding | `maps/IlexForest.asm` |
| 153 | Bayleef | Evolution | Chikorita at level 16 | Johto | Phase 4 | Yes | `data/pokemon/evos_attacks.asm`; `maps/IlexForest.asm` |
| 154 | Meganium | Evolution | Bayleef at level 32 | Johto | Phase 4 | Yes | `data/pokemon/evos_attacks.asm`; `maps/IlexForest.asm` |
| 155 | Cyndaquil | Gift event | Level 19 in Burned Tower B1F after the legendary beasts awaken | Ecruteak City | Phase 4 | Yes after gift through breeding | `maps/BurnedTowerB1F.asm` |
| 156 | Quilava | Evolution | Cyndaquil at level 14 | Johto | Phase 4 | Yes | `data/pokemon/evos_attacks.asm`; `maps/BurnedTowerB1F.asm` |
| 157 | Typhlosion | Evolution | Quilava at level 36 | Johto | Phase 4 | Yes | `data/pokemon/evos_attacks.asm`; `maps/BurnedTowerB1F.asm` |
| 158 | Totodile | Gift event | Level 24 on Cianwood's east shore after receiving the SecretPotion | Cianwood City | Phase 4 | Yes after gift through breeding | `maps/CianwoodCity.asm`; `maps/CianwoodPharmacy.asm` |
| 159 | Croconaw | Evolution | Totodile at level 18 | Johto | Phase 4 | Yes | `data/pokemon/evos_attacks.asm`; `maps/CianwoodCity.asm` |
| 160 | Feraligatr | Evolution | Croconaw at level 30 | Johto | Phase 4 | Yes | `data/pokemon/evos_attacks.asm`; `maps/CianwoodCity.asm` |
| 161 | Sentret | Wild | Route 29, morning or day | Start | Existing | Yes | `data/wild/johto_grass.asm` |
| 162 | Furret | Evolution or wild | Sentret at level 15; Route 43 | Early Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 163 | Hoothoot | Wild | National Park and early routes at night | Early Johto | Existing | Yes | `data/wild/johto_grass.asm` |
| 164 | Noctowl | Evolution or wild | Hoothoot at level 20; Route 37 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 165 | Ledyba | Wild | National Park and Route 30 in the morning | Early Johto | Existing | Yes | `data/wild/johto_grass.asm` |
| 166 | Ledian | Evolution or wild | Ledyba at level 18; Route 37 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 167 | Spinarak | Wild | National Park and early routes at night | Early Johto | Existing | Yes | `data/wild/johto_grass.asm` |
| 168 | Ariados | Evolution or wild | Spinarak at level 22; Route 37 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 169 | Crobat | Evolution | Golbat with high friendship | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 170 | Chinchou | Fishing | Ocean fishing groups | After obtaining the Good Rod | Existing | Yes | `data/wild/fish.asm` |
| 171 | Lanturn | Evolution | Chinchou at level 27 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 172 | Pichu | Breeding or Odd Egg | Breed Pikachu or Raichu; possible Odd Egg result | After reaching Day Care | Existing | Yes through breeding | `engine/pokemon/breeding.asm`; `data/events/odd_eggs.asm`; `maps/DayCare.asm` |
| 173 | Cleffa | Breeding or Odd Egg | Breed Clefairy or Clefable; possible Odd Egg result | After obtaining parent | Existing | Yes through breeding | `engine/pokemon/breeding.asm`; `data/events/odd_eggs.asm`; `maps/DayCare.asm` |
| 174 | Igglybuff | Breeding or Odd Egg | Breed Jigglypuff or Wigglytuff; possible Odd Egg result | After reaching Day Care | Existing | Yes through breeding | `engine/pokemon/breeding.asm`; `data/events/odd_eggs.asm`; `maps/DayCare.asm` |
| 175 | Togepi | Gift Egg | Mr. Pokémon's Egg delivered through Violet Pokémon Center | After Badge 1 | Existing | Yes after gift through breeding | `maps/VioletPokecenter1F.asm` |
| 176 | Togetic | Evolution | Togepi with high friendship | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 177 | Natu | Wild | Ruins of Alph outside | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 178 | Xatu | Evolution or NPC trade | Natu at level 25; trade Haunter | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/events/npc_trades.asm` |
| 179 | Mareep | Wild | Level 20 in unattended SafariZoneBeta grass; one of the three common slots at morning, day, and night | Kanto | Phase 9 | Yes | `data/wild/kanto_grass.asm`; `maps/SafariZoneBeta.asm` |
| 180 | Flaaffy | Evolution | Level up the Phase 9 Mareep once; it is already above level 15 | Kanto | Phase 9 | Yes | `data/pokemon/evos_attacks.asm`; Phase 9 Mareep source |
| 181 | Ampharos | Evolution | Flaaffy at level 30 | Kanto | Phase 9 | Yes | `data/pokemon/evos_attacks.asm`; Phase 9 Mareep source |
| 182 | Bellossom | Evolution | Use Sun Stone on Gloom | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `engine/events/std_scripts.asm` |
| 183 | Marill | Wild | Mt. Mortar | Mid-Johto | Existing | Yes | `data/wild/johto_grass.asm` |
| 184 | Azumarill | Evolution | Marill at level 18 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 185 | Sudowoodo | Static encounter | Route 36 after using SquirtBottle | After Badge 3 | Existing | Yes after capture through breeding; failed stock battle is not retryable | `maps/Route36.asm` |
| 186 | Politoed | Evolution | Use King's Rock on Poliwhirl | Kanto item source | Phase 2 | Yes | `data/pokemon/evos_attacks.asm`; `data/items/marts.asm` |
| 187 | Hoppip | Wild | Route 29 and other Johto routes | Start | Existing | Yes | `data/wild/johto_grass.asm` |
| 188 | Skiploom | Evolution or wild | Hoppip at level 18; Route 14 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 189 | Jumpluff | Evolution | Skiploom at level 27 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 190 | Aipom | Wild | Headbutt trees | After obtaining Headbutt | Existing | Yes | `data/wild/treemons.asm`; `data/wild/treemon_maps.asm` |
| 191 | Sunkern | Wild | National Park | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 192 | Sunflora | Evolution | Use Sun Stone on Sunkern | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `engine/events/std_scripts.asm` |
| 193 | Yanma | Wild | Route 35, including swarm | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 194 | Wooper | Wild | Ruins of Alph outside and Route 32 at night | Before Badge 2 | Existing | Yes | `data/wild/johto_grass.asm`; `data/wild/johto_water.asm` |
| 195 | Quagsire | Evolution or wild | Wooper at level 20; Johto water | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_water.asm` |
| 196 | Espeon | Evolution | Eevee with high friendship during morning or day | Mid-Johto | Existing | Yes through breeding Eevee | `data/pokemon/evos_attacks.asm`; `maps/BillsFamilysHouse.asm` |
| 197 | Umbreon | Evolution | Eevee with high friendship at night | Mid-Johto | Existing | Yes through breeding Eevee | `data/pokemon/evos_attacks.asm`; `maps/BillsFamilysHouse.asm` |
| 198 | Murkrow | Wild | Route 7 at night | Kanto | Existing | Yes | `data/wild/kanto_grass.asm` |
| 199 | Slowking | Evolution | Use King's Rock on Slowpoke | Kanto item source | Phase 2 | Yes | `data/pokemon/evos_attacks.asm`; `data/items/marts.asm` |
| 200 | Misdreavus | Wild | Silver Cave Room 2 at night | After 16 badges | Existing | Yes | `data/wild/johto_grass.asm` |
| 201 | Unown | Wild | Ruins of Alph inner chambers | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 202 | Wobbuffet | Wild or prize | Dark Cave Blackthorn entrance; Goldenrod Game Corner | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm`; `maps/GoldenrodGameCorner.asm` |
| 203 | Girafarig | NPC trade | Trade Chansey to Kim on Route 14 for a same-level Girafarig named `GIRAFY`; Phase 9 deliberately adds no wild Safari source | Kanto | Phase 5 | Yes through breeding after the one-time trade | `data/events/npc_trades.asm`; `maps/Route14.asm` |
| 204 | Pineco | Wild | Headbutt trees | After obtaining Headbutt | Existing | Yes | `data/wild/treemons.asm`; `data/wild/treemon_maps.asm` |
| 205 | Forretress | Evolution | Pineco at level 31 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 206 | Dunsparce | Wild | Dark Cave Violet entrance, including swarm | Before Badge 1 | Existing | Yes | `data/wild/johto_grass.asm` |
| 207 | Gligar | Wild | Route 45 | After Badge 8 | Existing | Yes | `data/wild/johto_grass.asm` |
| 208 | Steelix | Evolution | Use Metal Coat on Onix | Kanto item source | Phase 2 | Yes | `data/pokemon/evos_attacks.asm`; `data/items/marts.asm` |
| 209 | Snubbull | Wild | Route 34, including swarm | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 210 | Granbull | Evolution or wild | Snubbull at level 23; Route 6 | Mid-Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_grass.asm` |
| 211 | Qwilfish | Fishing | Route 32 fishing group, including swarm | After obtaining the appropriate rod | Existing | Yes | `data/wild/fish.asm`; `data/maps/maps.asm` |
| 212 | Scizor | Evolution | Use Metal Coat on Scyther | Kanto item source | Phase 2 | Yes | `data/pokemon/evos_attacks.asm`; `data/items/marts.asm` |
| 213 | Shuckle | Gift or wild | Mania's house in Cianwood; Rock Smash encounters | After Surf | Existing | Yes after gift through breeding; wild encounters renewable | `maps/ManiasHouse.asm`; `data/wild/treemons.asm` |
| 214 | Heracross | Wild | Rare Headbutt trees | After obtaining Headbutt | Existing | Yes | `data/wild/treemons.asm`; `data/wild/treemon_maps.asm` |
| 215 | Sneasel | Wild | Ice Path at night | Before Badge 8 | Existing | Yes | `data/wild/johto_grass.asm` |
| 216 | Teddiursa | Wild | Dark Cave Violet entrance | Before Badge 1 | Existing | Yes | `data/wild/johto_grass.asm` |
| 217 | Ursaring | Evolution or wild | Teddiursa at level 30; Silver Cave | Late Johto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 218 | Slugma | Wild | Routes 16-18 | Kanto | Existing | Yes | `data/wild/kanto_grass.asm` |
| 219 | Magcargo | Evolution | Slugma at level 38 | Kanto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 220 | Swinub | Wild | Ice Path | Before Badge 8 | Existing | Yes | `data/wild/johto_grass.asm` |
| 221 | Piloswine | Evolution | Swinub at level 33 | Before League | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 222 | Corsola | Fishing | Shore and ocean fishing groups during the day | After obtaining the appropriate rod | Existing | Yes | `data/wild/fish.asm` |
| 223 | Remoraid | Wild | Levels 22 and 24 in the two common unattended SafariZoneBeta water slots | Kanto | Phase 9 | Yes | `data/wild/kanto_water.asm`; `maps/SafariZoneBeta.asm` |
| 224 | Octillery | Evolution or wild | Remoraid at level 25; optional level-28 third SafariZoneBeta water slot | Kanto | Phase 9 | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/kanto_water.asm` |
| 225 | Delibird | Wild | Ice Path at night | Before Badge 8 | Existing | Yes | `data/wild/johto_grass.asm` |
| 226 | Mantine | Wild | Surf on Route 41 | After Surf | Existing | Yes | `data/wild/johto_water.asm` |
| 227 | Skarmory | Wild | Route 45 | After Badge 8 | Existing | Yes | `data/wild/johto_grass.asm` |
| 228 | Houndour | Wild | Route 7 at night | Kanto | Existing | Yes | `data/wild/kanto_grass.asm` |
| 229 | Houndoom | Evolution | Houndour at level 24 | Kanto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 230 | Kingdra | Evolution | Use Dragon Scale on Seadra | Kanto item source | Phase 2 | Yes | `data/pokemon/evos_attacks.asm`; `data/items/marts.asm` |
| 231 | Phanpy | Wild | Route 45 | After Badge 8 | Existing | Yes | `data/wild/johto_grass.asm` |
| 232 | Donphan | Evolution or wild | Phanpy at level 25; Route 45 | After Badge 8 | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 233 | Porygon2 | Evolution | Use Up-Grade on Porygon | Kanto | Phase 2 | Repeatable while Porygon remains purchasable | `data/pokemon/evos_attacks.asm`; `data/items/marts.asm` |
| 234 | Stantler | Wild | Route 37 | Mid-Johto | Existing | Yes | `data/wild/johto_grass.asm` |
| 235 | Smeargle | Wild | Ruins of Alph outside | After Badge 2 | Existing | Yes | `data/wild/johto_grass.asm` |
| 236 | Tyrogue | Gift or Odd Egg | Kiyo in Mt. Mortar; possible Odd Egg result | Late Johto | Existing | Yes after gift through breeding | `maps/MountMortarB1F.asm`; `data/events/odd_eggs.asm` |
| 237 | Hitmontop | Evolution | Tyrogue at level 20 with equal Attack and Defense | Late Johto | Existing | Yes through breeding Tyrogue | `data/pokemon/evos_attacks.asm`; `maps/MountMortarB1F.asm` |
| 238 | Smoochum | Breeding or Odd Egg | Breed Jynx; possible Odd Egg result | After obtaining parent | Existing | Yes through breeding | `engine/pokemon/breeding.asm`; `data/events/odd_eggs.asm` |
| 239 | Elekid | Breeding or Odd Egg | Breed Electabuzz; possible Odd Egg result | Kanto or Odd Egg | Existing | Yes through breeding | `engine/pokemon/breeding.asm`; `data/events/odd_eggs.asm` |
| 240 | Magby | Breeding or Odd Egg | Breed Magmar; possible Odd Egg result | After obtaining parent or Odd Egg | Existing | Yes through breeding | `engine/pokemon/breeding.asm`; `data/events/odd_eggs.asm` |
| 241 | Miltank | Wild | Route 38 | After Badge 3 | Existing | Yes | `data/wild/johto_grass.asm` |
| 242 | Blissey | Evolution | Chansey with high friendship | Kanto | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 243 | Raikou | Roaming encounter | Released from Burned Tower, then roams Johto | Mid-Johto | Existing | No; stock knockout or capture removes the roamer | `engine/overworld/wildmons.asm`; `data/wild/roammon_maps.asm` |
| 244 | Entei | Roaming encounter | Released from Burned Tower, then roams Johto | Mid-Johto | Existing | No; stock knockout or capture removes the roamer | `engine/overworld/wildmons.asm`; `data/wild/roammon_maps.asm` |
| 245 | Suicune | Static encounter | Tin Tower 1F after the Crystal storyline | Late Johto | Existing | No; stock event ends after battle | `maps/TinTower1F.asm` |
| 246 | Larvitar | Prize or wild | Celadon Game Corner; Silver Cave | Kanto | Existing | Yes through repeatable prize purchase or wild capture | `maps/CeladonGameCornerPrizeRoom.asm`; `data/wild/johto_grass.asm` |
| 247 | Pupitar | Evolution or wild | Larvitar at level 30; Silver Cave Room 3 | Kanto | Existing | Yes | `data/pokemon/evos_attacks.asm`; `data/wild/johto_grass.asm` |
| 248 | Tyranitar | Evolution | Pupitar at level 55 | Postgame training | Existing | Yes | `data/pokemon/evos_attacks.asm` |
| 249 | Lugia | Static encounter | Whirl Islands chamber with Silver Wing | Kanto | Existing | No; stock event ends after battle | `maps/WhirlIslandLugiaChamber.asm` |
| 250 | Ho-Oh | Static encounter | Tin Tower roof after the required beast quest | Postgame | Existing | No; stock event ends after battle | `maps/TinTowerRoof.asm` |
| 251 | Celebi | Story encounter | Post-Hall-of-Fame GS Ball, Kurt, and Ilex Forest shrine | Post-League | Phase 2 | No duplicates; retryable until captured | `maps/GoldenrodPokecenter1F.asm`; `maps/KurtsHouse.asm`; `maps/IlexForest.asm` |

## Phase 9 Kanto completion details

SafariZoneBeta becomes accessible only after speaking with the Warden's
granddaughter and owning the Soul Badge. It is an unattended ordinary-battle
area: no fee, timer, Safari Balls, bait, rocks, or Safari battle menu. Grass
uses rate 10 at every time; water also uses rate 10. The exact renewable slots
are:

| Slot | Morning | Day | Night |
| ---: | --- | --- | --- |
| 1 | Lv.22 Mankey | Lv.20 Mareep | Lv.24 Vulpix |
| 2 | Lv.20 Mareep | Lv.24 Vulpix | Lv.22 Mankey |
| 3 | Lv.24 Vulpix | Lv.22 Mankey | Lv.20 Mareep |
| 4 | Lv.24 Exeggcute | Lv.24 Exeggcute | Lv.24 Exeggcute |
| 5 | Lv.26 Tauros | Lv.26 Scyther | Lv.26 Pinsir |
| 6 | Lv.28 Chansey | Lv.28 Chansey | Lv.28 Chansey |
| 7 | Lv.28 Kangaskhan | Lv.28 Kangaskhan | Lv.28 Kangaskhan |

| Water slot | Encounter |
| ---: | --- |
| 1 | Lv.22 Remoraid |
| 2 | Lv.24 Remoraid |
| 3 | Lv.28 Octillery |

The classic Safari species are optional late-game alternatives; their earlier
canonical sources remain valid. The bird branch is also explicit and
single-save safe:

| Elm starter | Oak encounter | Silver-release encounter | Never spawns |
| --- | --- | --- | --- |
| Articuno | Zapdos in the Generator Annex | Moltres on Victory Road after Hall of Fame | Seafoam Articuno |
| Zapdos | Moltres on Victory Road after Hall of Fame | Articuno in Seafoam | Generator Annex Zapdos |
| Moltres | Articuno in Seafoam | Zapdos in the Generator Annex | Victory Road Moltres |

Only capture completes a world-bird encounter. Knockout, escape, and player
loss leave a full-HP retry, and native save/reload cannot create a duplicate.

## Maintenance rule

Any change to an encounter, evolution, gift, static battle, NPC trade, prize,
breeding rule, roamer, or special event must update the affected ledger rows in
the same commit. When a reserved phase lands, replace every relevant `TBD` and
planned destination with the implemented location, requirement, availability,
renewability, retry behavior, and authoritative source.
