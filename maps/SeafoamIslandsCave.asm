	object_const_def
	const SEAFOAMISLANDSCAVE_ARTICUNO
	const SEAFOAMISLANDSCAVE_ULTRA_BALL

SeafoamIslandsCave_MapScripts:
	def_scene_scripts

	def_callbacks
	callback MAPCALLBACK_TILES, SeafoamIslandsCaveArticunoCallback

SeafoamIslandsCaveArticunoCallback:
	farsjump Phase9RefreshArticunoLocation

SeafoamIslandsCaveArticuno:
	farsjump Phase9ArticunoEncounter

SeafoamIslandsCaveUltraBall:
	itemball ULTRA_BALL

SeafoamIslandsCaveHiddenNevermeltice:
	hiddenitem NEVERMELTICE, EVENT_SEAFOAM_ISLANDS_CAVE_HIDDEN_NEVERMELTICE

SeafoamIslandsCave_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event 10, 17, ROUTE_20, 2

	def_coord_events

	def_bg_events
	bg_event 17,  2, BGEVENT_ITEM, SeafoamIslandsCaveHiddenNevermeltice

	def_object_events
	object_event  8,  4, SPRITE_MOLTRES, SPRITEMOVEDATA_POKEMON, 0, 0, -1, -1, PAL_NPC_BLUE, OBJECTTYPE_SCRIPT, 0, SeafoamIslandsCaveArticuno, EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION
	object_event  2, 15, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, SeafoamIslandsCaveUltraBall, EVENT_SEAFOAM_ISLANDS_CAVE_ULTRA_BALL
