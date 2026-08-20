SafariZoneFuchsiaGateBeta_MapScripts:
	def_scene_scripts

	def_callbacks

if DEF(_CRYSTALLEGENDS)
SafariZoneFuchsiaGateBetaSouthNotice:
	farjumptext SafariZoneFuchsiaGateBetaSouthNoticeText

SafariZoneFuchsiaGateBetaNorthNotice:
	farjumptext SafariZoneFuchsiaGateBetaNorthNoticeText
endc

SafariZoneFuchsiaGateBeta_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event  4,  0, SAFARI_ZONE_BETA, 1
	warp_event  5,  0, SAFARI_ZONE_BETA, 2
	warp_event  4,  7, FUCHSIA_CITY, 7
	warp_event  5,  7, FUCHSIA_CITY, 7

	def_coord_events

	def_bg_events
	if DEF(_CRYSTALLEGENDS)
	bg_event  2,  0, BGEVENT_READ, SafariZoneFuchsiaGateBetaSouthNotice
	bg_event  7,  7, BGEVENT_READ, SafariZoneFuchsiaGateBetaNorthNotice
	endc

	def_object_events
