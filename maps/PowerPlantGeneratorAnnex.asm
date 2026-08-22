	object_const_def
	const POWERPLANTGENERATORANNEX_ZAPDOS
	const POWERPLANTGENERATORANNEX_MAGNET

PowerPlantGeneratorAnnex_MapScripts:
	def_scene_scripts

	def_callbacks
	callback MAPCALLBACK_TILES, PowerPlantGeneratorAnnexZapdosCallback

PowerPlantGeneratorAnnexZapdosCallback:
	farsjump Phase9RefreshZapdosLocation

PowerPlantGeneratorAnnexZapdos:
	farsjump Phase9ZapdosEncounter

PowerPlantGeneratorAnnexMagnet:
	itemball MAGNET

PowerPlantGeneratorAnnexConsole:
	checkevent EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION
	iftrue .Stable
	farjumptext Phase9PowerPlantGeneratorAnnexConsoleText

.Stable:
	farjumptext Phase9PowerPlantGeneratorAnnexStableText

PowerPlantGeneratorAnnex_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event 0, 5, POWER_PLANT, 3
	warp_event 0, 6, POWER_PLANT, 4

	def_coord_events

	def_bg_events
	bg_event 2, 4, BGEVENT_READ, PowerPlantGeneratorAnnexConsole
	bg_event 3, 4, BGEVENT_READ, PowerPlantGeneratorAnnexConsole

	def_object_events
	object_event 3, 2, SPRITE_MOLTRES, SPRITEMOVEDATA_POKEMON, 0, 0, -1, -1, PAL_NPC_BROWN, OBJECTTYPE_SCRIPT, 0, PowerPlantGeneratorAnnexZapdos, EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION
	object_event 7, 6, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, PowerPlantGeneratorAnnexMagnet, EVENT_POWER_PLANT_GENERATOR_ANNEX_MAGNET
