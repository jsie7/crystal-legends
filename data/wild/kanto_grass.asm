; Kanto Pokémon in grass

KantoGrassWildMons:

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons DIGLETTS_CAVE
	db 4 percent, 2 percent, 8 percent ; encounter rates: morn/day/nite
	; morn
	db 22, DIGLETT
	db 24, DIGLETT
	db 26, DIGLETT
	db 30, DIGLETT
	db 32, DUGTRIO
	db 32, DUGTRIO
	db 32, DUGTRIO
	; day
	db 20, DIGLETT
	db 22, DIGLETT
	db 24, DIGLETT
	db 28, DIGLETT
	db 30, DUGTRIO
	db 30, DUGTRIO
	db 30, DUGTRIO
	; nite
	db 24, DIGLETT
	db 26, DIGLETT
	db 28, DIGLETT
	db 32, DIGLETT
	db 35, DUGTRIO
	db 35, DUGTRIO
	db 35, DUGTRIO
	end_grass_wildmons
else
	def_grass_wildmons DIGLETTS_CAVE
	db 4 percent, 2 percent, 8 percent ; encounter rates: morn/day/nite
	; morn
	db 3, DIGLETT
	db 6, DIGLETT
	db 12, DIGLETT
	db 24, DIGLETT
	db 24, DUGTRIO
	db 24, DUGTRIO
	db 24, DUGTRIO
	; day
	db 2, DIGLETT
	db 4, DIGLETT
	db 8, DIGLETT
	db 16, DIGLETT
	db 16, DUGTRIO
	db 16, DUGTRIO
	db 16, DUGTRIO
	; nite
	db 4, DIGLETT
	db 8, DIGLETT
	db 16, DIGLETT
	db 32, DIGLETT
	db 32, DUGTRIO
	db 32, DUGTRIO
	db 32, DUGTRIO
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons MOUNT_MOON
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 24, ZUBAT
	db 26, GEODUDE
	db 26, SANDSHREW
	db 30, PARAS
	db 28, GEODUDE
	db 26, CLEFAIRY
	db 26, CLEFAIRY
	; day
	db 24, ZUBAT
	db 26, GEODUDE
	db 26, SANDSHREW
	db 30, PARAS
	db 28, GEODUDE
	db 26, CLEFAIRY
	db 26, CLEFAIRY
	; nite
	db 24, ZUBAT
	db 26, GEODUDE
	db 26, CLEFAIRY
	db 30, PARAS
	db 28, GEODUDE
	db 30, CLEFAIRY
	db 30, CLEFAIRY
	end_grass_wildmons
else
	def_grass_wildmons MOUNT_MOON
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 6, ZUBAT
	db 8, GEODUDE
	db 8, SANDSHREW
	db 12, PARAS
	db 10, GEODUDE
	db 8, CLEFAIRY
	db 8, CLEFAIRY
	; day
	db 6, ZUBAT
	db 8, GEODUDE
	db 8, SANDSHREW
	db 12, PARAS
	db 10, GEODUDE
	db 8, CLEFAIRY
	db 8, CLEFAIRY
	; nite
	db 6, ZUBAT
	db 8, GEODUDE
	db 8, CLEFAIRY
	db 12, PARAS
	db 10, GEODUDE
	db 12, CLEFAIRY
	db 12, CLEFAIRY
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROCK_TUNNEL_1F
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 24, CUBONE
	db 25, GEODUDE
	db 26, MACHOP
	db 26, ZUBAT
	db 29, MACHOKE
	db 26, MAROWAK
	db 26, MAROWAK
	; day
	db 24, CUBONE
	db 25, GEODUDE
	db 26, MACHOP
	db 26, ZUBAT
	db 29, MACHOKE
	db 26, MAROWAK
	db 26, MAROWAK
	; nite
	db 26, ZUBAT
	db 25, GEODUDE
	db 26, GEODUDE
	db 31, HAUNTER
	db 29, ZUBAT
	db 29, ZUBAT
	db 29, ZUBAT
	end_grass_wildmons
else
	def_grass_wildmons ROCK_TUNNEL_1F
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 10, CUBONE
	db 11, GEODUDE
	db 12, MACHOP
	db 12, ZUBAT
	db 15, MACHOKE
	db 12, MAROWAK
	db 12, MAROWAK
	; day
	db 10, CUBONE
	db 11, GEODUDE
	db 12, MACHOP
	db 12, ZUBAT
	db 15, MACHOKE
	db 12, MAROWAK
	db 12, MAROWAK
	; nite
	db 12, ZUBAT
	db 11, GEODUDE
	db 12, GEODUDE
	db 17, HAUNTER
	db 15, ZUBAT
	db 15, ZUBAT
	db 15, ZUBAT
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROCK_TUNNEL_B1F
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 26, CUBONE
	db 28, GEODUDE
	db 30, ONIX
	db 26, ZUBAT
	db 29, MAROWAK
	db 29, KANGASKHAN
	db 29, KANGASKHAN
	; day
	db 26, CUBONE
	db 28, GEODUDE
	db 30, ONIX
	db 26, ZUBAT
	db 29, MAROWAK
	db 29, KANGASKHAN
	db 29, KANGASKHAN
	; nite
	db 26, ZUBAT
	db 28, GEODUDE
	db 30, ONIX
	db 29, ZUBAT
	db 29, HAUNTER
	db 29, GOLBAT
	db 29, GOLBAT
	end_grass_wildmons
else
	def_grass_wildmons ROCK_TUNNEL_B1F
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 12, CUBONE
	db 14, GEODUDE
	db 16, ONIX
	db 12, ZUBAT
	db 15, MAROWAK
	db 15, KANGASKHAN
	db 15, KANGASKHAN
	; day
	db 12, CUBONE
	db 14, GEODUDE
	db 16, ONIX
	db 12, ZUBAT
	db 15, MAROWAK
	db 15, KANGASKHAN
	db 15, KANGASKHAN
	; nite
	db 12, ZUBAT
	db 14, GEODUDE
	db 16, ONIX
	db 15, ZUBAT
	db 15, HAUNTER
	db 15, GOLBAT
	db 15, GOLBAT
	end_grass_wildmons
endc

	def_grass_wildmons VICTORY_ROAD
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 34, GRAVELER
	db 32, RHYHORN
	db 33, ONIX
	db 34, GOLBAT
	db 35, SANDSLASH
	db 35, RHYDON
	db 35, RHYDON
	; day
	db 34, GRAVELER
	db 32, RHYHORN
	db 33, ONIX
	db 34, GOLBAT
	db 35, SANDSLASH
	db 35, RHYDON
	db 35, RHYDON
	; nite
	db 34, GOLBAT
	db 34, GRAVELER
	db 32, ONIX
	db 36, GRAVELER
	db 38, GRAVELER
	db 40, GRAVELER
	db 40, GRAVELER
	end_grass_wildmons

	def_grass_wildmons TOHJO_FALLS
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 22, ZUBAT
	db 22, RATICATE
	db 24, GOLBAT
	db 21, SLOWPOKE
	db 20, RATTATA
	db 23, SLOWPOKE
	db 23, SLOWPOKE
	; day
	db 22, ZUBAT
	db 22, RATICATE
	db 24, GOLBAT
	db 21, SLOWPOKE
	db 20, RATTATA
	db 23, SLOWPOKE
	db 23, SLOWPOKE
	; nite
	db 22, ZUBAT
	db 22, RATICATE
	db 24, GOLBAT
	db 21, SLOWPOKE
	db 20, RATTATA
	db 23, SLOWPOKE
	db 23, SLOWPOKE
	end_grass_wildmons

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_1
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 22, PIDGEY
	db 22, RATTATA
	db 23, SENTRET
	db 23, PIDGEY
	db 26, FURRET
	db 24, PIDGEY
	db 24, PIDGEY
	; day
	db 22, PIDGEY
	db 22, RATTATA
	db 23, SENTRET
	db 23, PIDGEY
	db 26, FURRET
	db 24, PIDGEY
	db 24, PIDGEY
	; nite
	db 22, HOOTHOOT
	db 22, RATTATA
	db 23, RATTATA
	db 23, HOOTHOOT
	db 26, RATICATE
	db 24, HOOTHOOT
	db 24, HOOTHOOT
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_1
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 2, PIDGEY
	db 2, RATTATA
	db 3, SENTRET
	db 3, PIDGEY
	db 6, FURRET
	db 4, PIDGEY
	db 4, PIDGEY
	; day
	db 2, PIDGEY
	db 2, RATTATA
	db 3, SENTRET
	db 3, PIDGEY
	db 6, FURRET
	db 4, PIDGEY
	db 4, PIDGEY
	; nite
	db 2, HOOTHOOT
	db 2, RATTATA
	db 3, RATTATA
	db 3, HOOTHOOT
	db 6, RATICATE
	db 4, HOOTHOOT
	db 4, HOOTHOOT
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_2
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 23, CATERPIE
	db 23, LEDYBA
	db 25, PIDGEY
	db 27, BUTTERFREE
	db 27, LEDIAN
	db 24, PIKACHU
	db 24, PIKACHU
	; day
	db 23, CATERPIE
	db 23, PIDGEY
	db 25, PIDGEY
	db 27, BUTTERFREE
	db 27, PIDGEOTTO
	db 24, PIKACHU
	db 24, PIKACHU
	; nite
	db 23, HOOTHOOT
	db 23, SPINARAK
	db 25, HOOTHOOT
	db 27, NOCTOWL
	db 27, ARIADOS
	db 24, NOCTOWL
	db 24, NOCTOWL
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_2
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 3, CATERPIE
	db 3, LEDYBA
	db 5, PIDGEY
	db 7, BUTTERFREE
	db 7, LEDIAN
	db 4, PIKACHU
	db 4, PIKACHU
	; day
	db 3, CATERPIE
	db 3, PIDGEY
	db 5, PIDGEY
	db 7, BUTTERFREE
	db 7, PIDGEOTTO
	db 4, PIKACHU
	db 4, PIKACHU
	; nite
	db 3, HOOTHOOT
	db 3, SPINARAK
	db 5, HOOTHOOT
	db 7, NOCTOWL
	db 7, ARIADOS
	db 4, NOCTOWL
	db 4, NOCTOWL
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_3
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 21, SPEAROW
	db 21, RATTATA
	db 24, EKANS
	db 26, RATICATE
	db 26, ARBOK
	db 26, SANDSHREW
	db 26, SANDSHREW
	; day
	db 21, SPEAROW
	db 21, RATTATA
	db 24, EKANS
	db 26, RATICATE
	db 26, ARBOK
	db 26, SANDSHREW
	db 26, SANDSHREW
	; nite
	db 21, RATTATA
	db 26, RATTATA
	db 26, RATICATE
	db 22, ZUBAT
	db 21, RATTATA
	db 22, CLEFAIRY
	db 22, CLEFAIRY
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_3
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 5, SPEAROW
	db 5, RATTATA
	db 8, EKANS
	db 10, RATICATE
	db 10, ARBOK
	db 10, SANDSHREW
	db 10, SANDSHREW
	; day
	db 5, SPEAROW
	db 5, RATTATA
	db 8, EKANS
	db 10, RATICATE
	db 10, ARBOK
	db 10, SANDSHREW
	db 10, SANDSHREW
	; nite
	db 5, RATTATA
	db 10, RATTATA
	db 10, RATICATE
	db 6, ZUBAT
	db 5, RATTATA
	db 6, CLEFAIRY
	db 6, CLEFAIRY
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_4
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 21, SPEAROW
	db 21, RATTATA
	db 24, EKANS
	db 26, RATICATE
	db 26, ARBOK
	db 26, SANDSHREW
	db 26, SANDSHREW
	; day
	db 21, SPEAROW
	db 21, RATTATA
	db 24, EKANS
	db 26, RATICATE
	db 26, ARBOK
	db 26, SANDSHREW
	db 26, SANDSHREW
	; nite
	db 21, RATTATA
	db 26, RATTATA
	db 26, RATICATE
	db 22, ZUBAT
	db 21, RATTATA
	db 22, CLEFAIRY
	db 22, CLEFAIRY
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_4
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 5, SPEAROW
	db 5, RATTATA
	db 8, EKANS
	db 10, RATICATE
	db 10, ARBOK
	db 10, SANDSHREW
	db 10, SANDSHREW
	; day
	db 5, SPEAROW
	db 5, RATTATA
	db 8, EKANS
	db 10, RATICATE
	db 10, ARBOK
	db 10, SANDSHREW
	db 10, SANDSHREW
	; nite
	db 5, RATTATA
	db 10, RATTATA
	db 10, RATICATE
	db 6, ZUBAT
	db 5, RATTATA
	db 6, CLEFAIRY
	db 6, CLEFAIRY
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_5
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 25, PIDGEY
	db 25, SNUBBULL
	db 27, PIDGEOTTO
	db 24, ABRA
	db 26, JIGGLYPUFF
	db 26, ABRA
	db 26, ABRA
	; day
	db 25, PIDGEY
	db 25, SNUBBULL
	db 27, PIDGEOTTO
	db 24, ABRA
	db 26, JIGGLYPUFF
	db 26, ABRA
	db 26, ABRA
	; nite
	db 25, HOOTHOOT
	db 25, MEOWTH
	db 27, NOCTOWL
	db 24, ABRA
	db 26, JIGGLYPUFF
	db 26, ABRA
	db 26, ABRA
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_5
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 13, PIDGEY
	db 13, SNUBBULL
	db 15, PIDGEOTTO
	db 12, ABRA
	db 14, JIGGLYPUFF
	db 14, ABRA
	db 14, ABRA
	; day
	db 13, PIDGEY
	db 13, SNUBBULL
	db 15, PIDGEOTTO
	db 12, ABRA
	db 14, JIGGLYPUFF
	db 14, ABRA
	db 14, ABRA
	; nite
	db 13, HOOTHOOT
	db 13, MEOWTH
	db 15, NOCTOWL
	db 12, ABRA
	db 14, JIGGLYPUFF
	db 14, ABRA
	db 14, ABRA
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_6
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 25, RATTATA
	db 25, SNUBBULL
	db 26, MAGNEMITE
	db 27, RATICATE
	db 24, JIGGLYPUFF
	db 27, GRANBULL
	db 27, GRANBULL
	; day
	db 25, RATTATA
	db 25, SNUBBULL
	db 26, MAGNEMITE
	db 27, RATICATE
	db 24, JIGGLYPUFF
	db 27, GRANBULL
	db 27, GRANBULL
	; nite
	db 25, MEOWTH
	db 25, DROWZEE
	db 26, MAGNEMITE
	db 27, PSYDUCK
	db 24, JIGGLYPUFF
	db 27, RATICATE
	db 27, RATICATE
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_6
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 13, RATTATA
	db 13, SNUBBULL
	db 14, MAGNEMITE
	db 15, RATICATE
	db 12, JIGGLYPUFF
	db 15, GRANBULL
	db 15, GRANBULL
	; day
	db 13, RATTATA
	db 13, SNUBBULL
	db 14, MAGNEMITE
	db 15, RATICATE
	db 12, JIGGLYPUFF
	db 15, GRANBULL
	db 15, GRANBULL
	; nite
	db 13, MEOWTH
	db 13, DROWZEE
	db 14, MAGNEMITE
	db 15, PSYDUCK
	db 12, JIGGLYPUFF
	db 15, RATICATE
	db 15, RATICATE
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_7
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 29, RATTATA
	db 29, SPEAROW
	db 30, SNUBBULL
	db 30, RATICATE
	db 30, JIGGLYPUFF
	db 28, ABRA
	db 28, ABRA
	; day
	db 29, RATTATA
	db 29, SPEAROW
	db 30, SNUBBULL
	db 30, RATICATE
	db 30, JIGGLYPUFF
	db 28, ABRA
	db 28, ABRA
	; nite
	db 29, MEOWTH
	db 29, MURKROW
	db 26, HOUNDOUR
	db 30, PERSIAN
	db 30, JIGGLYPUFF
	db 28, ABRA
	db 28, ABRA
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_7
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 17, RATTATA
	db 17, SPEAROW
	db 18, SNUBBULL
	db 18, RATICATE
	db 18, JIGGLYPUFF
	db 16, ABRA
	db 16, ABRA
	; day
	db 17, RATTATA
	db 17, SPEAROW
	db 18, SNUBBULL
	db 18, RATICATE
	db 18, JIGGLYPUFF
	db 16, ABRA
	db 16, ABRA
	; nite
	db 17, MEOWTH
	db 17, MURKROW
	db 18, HOUNDOUR
	db 18, PERSIAN
	db 18, JIGGLYPUFF
	db 16, ABRA
	db 16, ABRA
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_8
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 29, SNUBBULL
	db 31, PIDGEOTTO
	db 28, ABRA
	db 29, GROWLITHE
	db 28, JIGGLYPUFF
	db 30, KADABRA
	db 30, KADABRA
	; day
	db 29, SNUBBULL
	db 31, PIDGEOTTO
	db 28, ABRA
	db 29, GROWLITHE
	db 28, JIGGLYPUFF
	db 30, KADABRA
	db 30, KADABRA
	; nite
	db 29, MEOWTH
	db 32, NOCTOWL
	db 28, ABRA
	db 29, HAUNTER
	db 28, JIGGLYPUFF
	db 30, KADABRA
	db 30, KADABRA
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_8
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 17, SNUBBULL
	db 19, PIDGEOTTO
	db 16, ABRA
	db 17, GROWLITHE
	db 16, JIGGLYPUFF
	db 18, KADABRA
	db 18, KADABRA
	; day
	db 17, SNUBBULL
	db 19, PIDGEOTTO
	db 16, ABRA
	db 17, GROWLITHE
	db 16, JIGGLYPUFF
	db 18, KADABRA
	db 18, KADABRA
	; nite
	db 17, MEOWTH
	db 20, NOCTOWL
	db 16, ABRA
	db 17, HAUNTER
	db 16, JIGGLYPUFF
	db 18, KADABRA
	db 18, KADABRA
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_9
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 27, RATTATA
	db 27, SPEAROW
	db 27, RATICATE
	db 27, FEAROW
	db 27, FEAROW
	db 30, MAROWAK
	db 30, MAROWAK
	; day
	db 27, RATTATA
	db 27, SPEAROW
	db 27, RATICATE
	db 27, FEAROW
	db 27, FEAROW
	db 30, MAROWAK
	db 30, MAROWAK
	; nite
	db 27, RATTATA
	db 27, VENONAT
	db 27, RATICATE
	db 27, VENOMOTH
	db 27, ZUBAT
	db 30, RATICATE
	db 30, RATICATE
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_9
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 15, RATTATA
	db 15, SPEAROW
	db 15, RATICATE
	db 15, FEAROW
	db 15, FEAROW
	db 18, MAROWAK
	db 18, MAROWAK
	; day
	db 15, RATTATA
	db 15, SPEAROW
	db 15, RATICATE
	db 15, FEAROW
	db 15, FEAROW
	db 18, MAROWAK
	db 18, MAROWAK
	; nite
	db 15, RATTATA
	db 15, VENONAT
	db 15, RATICATE
	db 15, VENOMOTH
	db 15, ZUBAT
	db 18, RATICATE
	db 18, RATICATE
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_10_NORTH
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 27, SPEAROW
	db 29, VOLTORB
	db 27, RATICATE
	db 27, FEAROW
	db 27, MAROWAK
	db 28, ELECTABUZZ
	db 28, ELECTABUZZ
	; day
	db 27, SPEAROW
	db 29, VOLTORB
	db 27, RATICATE
	db 27, FEAROW
	db 27, MAROWAK
	db 30, ELECTABUZZ
	db 30, ELECTABUZZ
	; nite
	db 27, VENONAT
	db 29, VOLTORB
	db 27, RATICATE
	db 27, VENOMOTH
	db 27, ZUBAT
	db 28, ELECTABUZZ
	db 28, ELECTABUZZ
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_10_NORTH
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 15, SPEAROW
	db 17, VOLTORB
	db 15, RATICATE
	db 15, FEAROW
	db 15, MAROWAK
	db 16, ELECTABUZZ
	db 16, ELECTABUZZ
	; day
	db 15, SPEAROW
	db 17, VOLTORB
	db 15, RATICATE
	db 15, FEAROW
	db 15, MAROWAK
	db 18, ELECTABUZZ
	db 18, ELECTABUZZ
	; nite
	db 15, VENONAT
	db 17, VOLTORB
	db 15, RATICATE
	db 15, VENOMOTH
	db 15, ZUBAT
	db 16, ELECTABUZZ
	db 16, ELECTABUZZ
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_11
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 26, HOPPIP
	db 25, RATICATE
	db 27, MAGNEMITE
	db 28, PIDGEOTTO
	db 28, RATTATA
	db 28, HOPPIP
	db 28, HOPPIP
	; day
	db 26, HOPPIP
	db 25, RATICATE
	db 27, MAGNEMITE
	db 28, PIDGEOTTO
	db 28, RATTATA
	db 28, HOPPIP
	db 28, HOPPIP
	; nite
	db 26, DROWZEE
	db 25, MEOWTH
	db 27, MAGNEMITE
	db 28, NOCTOWL
	db 28, RATICATE
	db 28, HYPNO
	db 28, HYPNO
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_11
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 14, HOPPIP
	db 13, RATICATE
	db 15, MAGNEMITE
	db 16, PIDGEOTTO
	db 16, RATTATA
	db 16, HOPPIP
	db 16, HOPPIP
	; day
	db 14, HOPPIP
	db 13, RATICATE
	db 15, MAGNEMITE
	db 16, PIDGEOTTO
	db 16, RATTATA
	db 16, HOPPIP
	db 16, HOPPIP
	; nite
	db 14, DROWZEE
	db 13, MEOWTH
	db 15, MAGNEMITE
	db 16, NOCTOWL
	db 16, RATICATE
	db 16, HYPNO
	db 16, HYPNO
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_13
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 28, NIDORINO
	db 28, NIDORINA
	db 30, PIDGEOTTO
	db 30, HOPPIP
	db 32, HOPPIP
	db 32, HOPPIP
	db 30, CHANSEY
	; day
	db 28, NIDORINO
	db 28, NIDORINA
	db 30, PIDGEOTTO
	db 30, HOPPIP
	db 32, HOPPIP
	db 32, HOPPIP
	db 30, CHANSEY
	; nite
	db 28, VENONAT
	db 28, QUAGSIRE
	db 30, NOCTOWL
	db 30, VENOMOTH
	db 30, QUAGSIRE
	db 30, QUAGSIRE
	db 30, CHANSEY
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_13
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 23, NIDORINO
	db 23, NIDORINA
	db 25, PIDGEOTTO
	db 25, HOPPIP
	db 27, HOPPIP
	db 27, HOPPIP
	db 25, CHANSEY
	; day
	db 23, NIDORINO
	db 23, NIDORINA
	db 25, PIDGEOTTO
	db 25, HOPPIP
	db 27, HOPPIP
	db 27, HOPPIP
	db 25, CHANSEY
	; nite
	db 23, VENONAT
	db 23, QUAGSIRE
	db 25, NOCTOWL
	db 25, VENOMOTH
	db 25, QUAGSIRE
	db 25, QUAGSIRE
	db 25, CHANSEY
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_14
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 31, NIDORINO
	db 31, NIDORINA
	db 33, PIDGEOTTO
	db 33, HOPPIP
	db 35, SKIPLOOM
	db 35, SKIPLOOM
	db 33, CHANSEY
	; day
	db 31, NIDORINO
	db 31, NIDORINA
	db 33, PIDGEOTTO
	db 33, HOPPIP
	db 35, SKIPLOOM
	db 35, SKIPLOOM
	db 33, CHANSEY
	; nite
	db 31, VENONAT
	db 31, QUAGSIRE
	db 33, NOCTOWL
	db 33, VENOMOTH
	db 33, QUAGSIRE
	db 33, QUAGSIRE
	db 33, CHANSEY
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_14
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 26, NIDORINO
	db 26, NIDORINA
	db 28, PIDGEOTTO
	db 28, HOPPIP
	db 30, SKIPLOOM
	db 30, SKIPLOOM
	db 28, CHANSEY
	; day
	db 26, NIDORINO
	db 26, NIDORINA
	db 28, PIDGEOTTO
	db 28, HOPPIP
	db 30, SKIPLOOM
	db 30, SKIPLOOM
	db 28, CHANSEY
	; nite
	db 26, VENONAT
	db 26, QUAGSIRE
	db 28, NOCTOWL
	db 28, VENOMOTH
	db 28, QUAGSIRE
	db 28, QUAGSIRE
	db 28, CHANSEY
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_15
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 28, NIDORINO
	db 28, NIDORINA
	db 30, PIDGEOTTO
	db 30, HOPPIP
	db 32, HOPPIP
	db 32, HOPPIP
	db 30, CHANSEY
	; day
	db 28, NIDORINO
	db 28, NIDORINA
	db 30, PIDGEOTTO
	db 30, HOPPIP
	db 32, HOPPIP
	db 32, HOPPIP
	db 30, CHANSEY
	; nite
	db 28, VENONAT
	db 28, QUAGSIRE
	db 30, NOCTOWL
	db 30, VENOMOTH
	db 30, QUAGSIRE
	db 30, QUAGSIRE
	db 30, CHANSEY
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_15
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 23, NIDORINO
	db 23, NIDORINA
	db 25, PIDGEOTTO
	db 25, HOPPIP
	db 27, HOPPIP
	db 27, HOPPIP
	db 25, CHANSEY
	; day
	db 23, NIDORINO
	db 23, NIDORINA
	db 25, PIDGEOTTO
	db 25, HOPPIP
	db 27, HOPPIP
	db 27, HOPPIP
	db 25, CHANSEY
	; nite
	db 23, VENONAT
	db 23, QUAGSIRE
	db 25, NOCTOWL
	db 25, VENOMOTH
	db 25, QUAGSIRE
	db 25, QUAGSIRE
	db 25, CHANSEY
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_16
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 31, GRIMER
	db 32, FEAROW
	db 33, GRIMER
	db 34, FEAROW
	db 34, FEAROW
	db 35, MUK
	db 35, MUK
	; day
	db 31, GRIMER
	db 32, FEAROW
	db 33, GRIMER
	db 34, FEAROW
	db 34, SLUGMA
	db 35, MUK
	db 35, MUK
	; nite
	db 31, GRIMER
	db 32, GRIMER
	db 33, GRIMER
	db 34, MURKROW
	db 34, MURKROW
	db 35, MUK
	db 35, MUK
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_16
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 26, GRIMER
	db 27, FEAROW
	db 28, GRIMER
	db 29, FEAROW
	db 29, FEAROW
	db 30, MUK
	db 30, MUK
	; day
	db 26, GRIMER
	db 27, FEAROW
	db 28, GRIMER
	db 29, FEAROW
	db 29, SLUGMA
	db 30, MUK
	db 30, MUK
	; nite
	db 26, GRIMER
	db 27, GRIMER
	db 28, GRIMER
	db 29, MURKROW
	db 29, MURKROW
	db 30, MUK
	db 30, MUK
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_17
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 33, FEAROW
	db 32, GRIMER
	db 34, GRIMER
	db 35, FEAROW
	db 36, GRIMER
	db 36, MUK
	db 36, MUK
	; day
	db 33, FEAROW
	db 32, SLUGMA
	db 32, GRIMER
	db 35, FEAROW
	db 35, SLUGMA
	db 36, MUK
	db 36, MUK
	; nite
	db 33, GRIMER
	db 32, GRIMER
	db 34, GRIMER
	db 35, GRIMER
	db 36, GRIMER
	db 36, MUK
	db 36, MUK
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_17
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 30, FEAROW
	db 29, GRIMER
	db 31, GRIMER
	db 32, FEAROW
	db 33, GRIMER
	db 33, MUK
	db 33, MUK
	; day
	db 30, FEAROW
	db 29, SLUGMA
	db 29, GRIMER
	db 32, FEAROW
	db 32, SLUGMA
	db 33, MUK
	db 33, MUK
	; nite
	db 30, GRIMER
	db 29, GRIMER
	db 31, GRIMER
	db 32, GRIMER
	db 33, GRIMER
	db 33, MUK
	db 33, MUK
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_18
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 30, GRIMER
	db 31, FEAROW
	db 32, GRIMER
	db 33, FEAROW
	db 33, FEAROW
	db 34, MUK
	db 34, MUK
	; day
	db 30, GRIMER
	db 31, FEAROW
	db 32, GRIMER
	db 33, FEAROW
	db 33, SLUGMA
	db 34, MUK
	db 34, MUK
	; nite
	db 30, GRIMER
	db 31, GRIMER
	db 32, GRIMER
	db 33, GRIMER
	db 33, GRIMER
	db 34, MUK
	db 34, MUK
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_18
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 26, GRIMER
	db 27, FEAROW
	db 28, GRIMER
	db 29, FEAROW
	db 29, FEAROW
	db 30, MUK
	db 30, MUK
	; day
	db 26, GRIMER
	db 27, FEAROW
	db 28, GRIMER
	db 29, FEAROW
	db 29, SLUGMA
	db 30, MUK
	db 30, MUK
	; nite
	db 26, GRIMER
	db 27, GRIMER
	db 28, GRIMER
	db 29, GRIMER
	db 29, GRIMER
	db 30, MUK
	db 30, MUK
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_21
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 35, TANGELA
	db 30, RATTATA
	db 40, TANGELA
	db 25, RATICATE
	db 35, MR__MIME
	db 33, MR__MIME
	db 33, MR__MIME
	; day
	db 35, TANGELA
	db 30, RATTATA
	db 40, TANGELA
	db 25, RATICATE
	db 33, MR__MIME
	db 35, MR__MIME
	db 35, MR__MIME
	; nite
	db 35, TANGELA
	db 30, RATTATA
	db 40, TANGELA
	db 25, RATICATE
	db 35, TANGELA
	db 33, TANGELA
	db 33, TANGELA
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_21
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 30, TANGELA
	db 25, RATTATA
	db 35, TANGELA
	db 20, RATICATE
	db 30, MR__MIME
	db 28, MR__MIME
	db 28, MR__MIME
	; day
	db 30, TANGELA
	db 25, RATTATA
	db 35, TANGELA
	db 20, RATICATE
	db 28, MR__MIME
	db 30, MR__MIME
	db 30, MR__MIME
	; nite
	db 30, TANGELA
	db 25, RATTATA
	db 35, TANGELA
	db 20, RATICATE
	db 30, TANGELA
	db 28, TANGELA
	db 28, TANGELA
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_22
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 21, RATTATA
	db 21, SPEAROW
	db 23, SPEAROW
	db 22, DODUO
	db 24, PONYTA
	db 25, FEAROW
	db 25, FEAROW
	; day
	db 21, RATTATA
	db 21, SPEAROW
	db 23, SPEAROW
	db 22, DODUO
	db 24, PONYTA
	db 25, FEAROW
	db 25, FEAROW
	; nite
	db 21, RATTATA
	db 21, POLIWAG
	db 23, RATTATA
	db 22, POLIWAG
	db 24, RATTATA
	db 25, RATTATA
	db 25, RATTATA
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_22
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 3, RATTATA
	db 3, SPEAROW
	db 5, SPEAROW
	db 4, DODUO
	db 6, PONYTA
	db 7, FEAROW
	db 7, FEAROW
	; day
	db 3, RATTATA
	db 3, SPEAROW
	db 5, SPEAROW
	db 4, DODUO
	db 6, PONYTA
	db 7, FEAROW
	db 7, FEAROW
	; nite
	db 3, RATTATA
	db 3, POLIWAG
	db 5, RATTATA
	db 4, POLIWAG
	db 6, RATTATA
	db 7, RATTATA
	db 7, RATTATA
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_24
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 23, CATERPIE
	db 25, CATERPIE
	db 27, METAPOD
	db 27, ABRA
	db 25, BELLSPROUT
	db 29, BUTTERFREE
	db 29, BUTTERFREE
	; day
	db 23, CATERPIE
	db 27, SUNKERN
	db 25, CATERPIE
	db 27, ABRA
	db 25, BELLSPROUT
	db 29, BUTTERFREE
	db 29, BUTTERFREE
	; nite
	db 25, VENONAT
	db 25, ODDISH
	db 27, ODDISH
	db 27, ABRA
	db 25, BELLSPROUT
	db 29, GLOOM
	db 29, GLOOM
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_24
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 8, CATERPIE
	db 10, CATERPIE
	db 12, METAPOD
	db 12, ABRA
	db 10, BELLSPROUT
	db 14, BUTTERFREE
	db 14, BUTTERFREE
	; day
	db 8, CATERPIE
	db 12, SUNKERN
	db 10, CATERPIE
	db 12, ABRA
	db 10, BELLSPROUT
	db 14, BUTTERFREE
	db 14, BUTTERFREE
	; nite
	db 10, VENONAT
	db 10, ODDISH
	db 12, ODDISH
	db 12, ABRA
	db 10, BELLSPROUT
	db 14, GLOOM
	db 14, GLOOM
	end_grass_wildmons
endc

if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons ROUTE_25
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 25, CATERPIE
	db 25, PIDGEY
	db 27, PIDGEOTTO
	db 27, METAPOD
	db 25, BELLSPROUT
	db 29, BUTTERFREE
	db 29, BUTTERFREE
	; day
	db 25, CATERPIE
	db 25, PIDGEY
	db 27, PIDGEOTTO
	db 27, METAPOD
	db 25, BELLSPROUT
	db 29, BUTTERFREE
	db 29, BUTTERFREE
	; nite
	db 25, ODDISH
	db 25, HOOTHOOT
	db 25, VENONAT
	db 27, NOCTOWL
	db 25, BELLSPROUT
	db 29, NOCTOWL
	db 29, NOCTOWL
	end_grass_wildmons
else
	def_grass_wildmons ROUTE_25
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 10, CATERPIE
	db 10, PIDGEY
	db 12, PIDGEOTTO
	db 12, METAPOD
	db 10, BELLSPROUT
	db 14, BUTTERFREE
	db 14, BUTTERFREE
	; day
	db 10, CATERPIE
	db 10, PIDGEY
	db 12, PIDGEOTTO
	db 12, METAPOD
	db 10, BELLSPROUT
	db 14, BUTTERFREE
	db 14, BUTTERFREE
	; nite
	db 10, ODDISH
	db 10, HOOTHOOT
	db 10, VENONAT
	db 12, NOCTOWL
	db 10, BELLSPROUT
	db 14, NOCTOWL
	db 14, NOCTOWL
	end_grass_wildmons
endc

	def_grass_wildmons ROUTE_26
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 28, DODUO
	db 28, SANDSLASH
	db 32, PONYTA
	db 30, RATICATE
	db 30, DODUO
	db 30, ARBOK
	db 30, ARBOK
	; day
	db 28, DODUO
	db 28, SANDSLASH
	db 32, PONYTA
	db 30, RATICATE
	db 30, DODUO
	db 30, ARBOK
	db 30, ARBOK
	; nite
	db 28, NOCTOWL
	db 28, RATICATE
	db 32, NOCTOWL
	db 30, RATICATE
	db 30, QUAGSIRE
	db 30, QUAGSIRE
	db 30, QUAGSIRE
	end_grass_wildmons

	def_grass_wildmons ROUTE_27
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 28, DODUO
	db 28, ARBOK
	db 30, RATICATE
	db 30, DODUO
	db 32, PONYTA
	db 30, DODRIO
	db 30, DODRIO
	; day
	db 28, DODUO
	db 28, ARBOK
	db 30, RATICATE
	db 30, DODUO
	db 32, PONYTA
	db 30, DODRIO
	db 30, DODRIO
	; nite
	db 28, QUAGSIRE
	db 28, NOCTOWL
	db 30, RATICATE
	db 30, QUAGSIRE
	db 32, NOCTOWL
	db 32, NOCTOWL
	db 32, NOCTOWL
	end_grass_wildmons

	def_grass_wildmons ROUTE_28
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 39, TANGELA
	db 40, PONYTA
	db 40, RAPIDASH
	db 42, ARBOK
	db 41, DODUO
	db 43, DODRIO
	db 43, DODRIO
	; day
	db 39, TANGELA
	db 40, PONYTA
	db 40, RAPIDASH
	db 42, ARBOK
	db 41, DODUO
	db 43, DODRIO
	db 43, DODRIO
	; nite
	db 39, TANGELA
	db 40, POLIWHIRL
	db 40, GOLBAT
	db 40, POLIWHIRL
	db 42, GOLBAT
	db 42, GOLBAT
	db 42, GOLBAT
	end_grass_wildmons

	if DEF(_CRYSTALLEGENDS)
	def_grass_wildmons SAFARI_ZONE_BETA
	db 10 percent, 10 percent, 10 percent ; encounter rates: morn/day/nite
	; morn
	db 32, MANKEY
	db 28, MAREEP
	db 34, VULPIX
	db 34, EXEGGCUTE
	db 36, TAUROS
	db 38, CHANSEY
	db 38, KANGASKHAN
	; day
	db 28, MAREEP
	db 34, VULPIX
	db 32, MANKEY
	db 34, EXEGGCUTE
	db 36, SCYTHER
	db 38, CHANSEY
	db 38, KANGASKHAN
	; nite
	db 34, VULPIX
	db 32, MANKEY
	db 28, MAREEP
	db 34, EXEGGCUTE
	db 36, PINSIR
	db 38, CHANSEY
	db 38, KANGASKHAN
	end_grass_wildmons

	def_grass_wildmons CERULEAN_CAVE
	db 6 percent, 6 percent, 6 percent ; encounter rates: morn/day/nite
	; morn
	db 52, GOLBAT
	db 52, GRAVELER
	db 54, KADABRA
	db 55, MAGNETON
	db 56, RHYDON
	db 58, DITTO
	db 60, CHANSEY
	; day
	db 52, GOLBAT
	db 52, GRAVELER
	db 54, KADABRA
	db 55, MAGNETON
	db 56, RHYDON
	db 58, DITTO
	db 60, CHANSEY
	; nite
	db 52, GOLBAT
	db 52, GRAVELER
	db 54, KADABRA
	db 55, MAGNETON
	db 56, RHYDON
	db 58, DITTO
	db 60, CHANSEY
	end_grass_wildmons
	endc

	db -1 ; end
