	object_const_def
	const SEAFOAMISLANDSCAVE_ARTICUNO

SeafoamIslandsCave_MapScripts:
	def_scene_scripts

	def_callbacks
	callback MAPCALLBACK_TILES, SeafoamIslandsCaveArticunoCallback

SeafoamIslandsCaveArticunoCallback:
	farsjump Phase9RefreshArticunoLocation

SeafoamIslandsCaveArticuno:
	farsjump Phase9ArticunoEncounter

SeafoamIslandsCave_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event 10, 17, ROUTE_20, 2

	def_coord_events

	def_bg_events

	def_object_events
	object_event 9, 4, SPRITE_MOLTRES, SPRITEMOVEDATA_POKEMON, 0, 0, -1, -1, PAL_NPC_BLUE, OBJECTTYPE_SCRIPT, 0, SeafoamIslandsCaveArticuno, EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION
