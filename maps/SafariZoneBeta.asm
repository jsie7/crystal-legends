if DEF(_CRYSTALLEGENDS)
	object_const_def
	const SAFARIZONEBETA_ULTRA_BALL
	const SAFARIZONEBETA_MAX_REVIVE
endc

SafariZoneBeta_MapScripts:
	def_scene_scripts

	def_callbacks

if DEF(_CRYSTALLEGENDS)
SafariZoneBetaUnattendedSign:
	farjumptext SafariZoneBetaUnattendedSignText

SafariZoneBetaNormalBattleSign:
	farjumptext SafariZoneBetaNormalBattleSignText

SafariZoneBetaUltraBall:
	itemball ULTRA_BALL

SafariZoneBetaMaxRevive:
	itemball MAX_REVIVE
endc

SafariZoneBeta_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event  9, 23, SAFARI_ZONE_FUCHSIA_GATE_BETA, 1
	warp_event 10, 23, SAFARI_ZONE_FUCHSIA_GATE_BETA, 2

	def_coord_events

	def_bg_events
	if DEF(_CRYSTALLEGENDS)
	bg_event  6, 20, BGEVENT_READ, SafariZoneBetaUnattendedSign
	bg_event 13, 21, BGEVENT_READ, SafariZoneBetaNormalBattleSign
	endc

	def_object_events
	if DEF(_CRYSTALLEGENDS)
	object_event  3, 19, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, SafariZoneBetaUltraBall, EVENT_SAFARI_ZONE_BETA_ULTRA_BALL
	object_event 17,  3, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, SafariZoneBetaMaxRevive, EVENT_SAFARI_ZONE_BETA_MAX_REVIVE
	endc
