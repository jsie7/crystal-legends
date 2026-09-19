	object_const_def
	const SAFARIZONEWARDENSHOME_LASS

SafariZoneWardensHome_MapScripts:
	def_scene_scripts

	def_callbacks

WardensGranddaughter:
	if DEF(_CRYSTALLEGENDS)
	faceplayer
	opentext
	checkevent EVENT_SAFARI_ZONE_ACCESSIBLE
	iftrue .Unattended
	checkevent EVENT_TALKED_TO_WARDENS_GRANDDAUGHTER
	iftrue .CheckBadge
	setevent EVENT_TALKED_TO_WARDENS_GRANDDAUGHTER
.CheckBadge:
	checkflag ENGINE_SOULBADGE
	iftrue .ReleaseGate
	writetext WardensGranddaughterSoulBadgeText
	waitbutton
	closetext
	end
.ReleaseGate:
	writetext WardensGranddaughterReleaseGateText
	waitbutton
	setevent EVENT_SAFARI_ZONE_ACCESSIBLE
	closetext
	end
.Unattended:
	writetext WardensGranddaughterUnattendedText
	waitbutton
	closetext
	end
	else
	faceplayer
	opentext
	checkevent EVENT_TALKED_TO_WARDENS_GRANDDAUGHTER
	iftrue .AlreadyMet
	writetext WardensGranddaughterText1
	waitbutton
	closetext
	setevent EVENT_TALKED_TO_WARDENS_GRANDDAUGHTER
	end
.AlreadyMet:
	writetext WardensGranddaughterText2
	waitbutton
	closetext
	end
	endc

WardenPhoto:
	jumptext WardenPhotoText

SafariZonePhoto:
	jumptext SafariZonePhotoText

WardensHomeBookshelf:
	jumpstd PictureBookshelfScript

if !DEF(_CRYSTALLEGENDS)
WardensGranddaughterText1:
	text "My grandpa is the"
	line "SAFARI ZONE WAR-"
	cont "DEN."

	para "At least he was…"

	para "He decided to go"
	line "on a vacation and"

	para "took off overseas"
	line "all by himself."

	para "He quit running"
	line "SAFARI ZONE just"
	cont "like that."
	done

WardensGranddaughterText2:
	text "Many people were"
	line "disappointed that"

	para "SAFARI ZONE closed"
	line "down, but Grandpa"
	cont "is so stubborn…"
	done
endc

if DEF(_CRYSTALLEGENDS)
WardensGranddaughterSoulBadgeText:
	text "JANINE permits"
	line "only proven"
	cont "TRAINERS to enter."

	para "Earn the SOULBADGE"
	line "and come back."
	done

WardensGranddaughterReleaseGateText:
	text "That SOULBADGE"
	line "proves you're"
	cont "capable."

	para "Feel free to"
	line "explore the SAFARI"
	cont "ZONE."
	done

WardensGranddaughterUnattendedText:
	text "The north gate is"
	line "open at your own"
	cont "risk."

	para "There are no staff"
	line "or rescue service."

	para "No official"
	line "SAFARI GAME."
	done
endc

WardenPhotoText:
	text "It's a photo of a"
	line "grinning old man"

	para "who's surrounded"
	line "by #MON."
	done

SafariZonePhotoText:
	text "It's a photo of a"
	line "huge grassy plain"

	para "with rare #MON"
	line "frolicking in it."
	done

SafariZoneWardensHome_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event  2,  7, FUCHSIA_CITY, 6
	warp_event  3,  7, FUCHSIA_CITY, 6

	def_coord_events

	def_bg_events
	bg_event  0,  1, BGEVENT_READ, WardensHomeBookshelf
	bg_event  1,  1, BGEVENT_READ, WardensHomeBookshelf
	bg_event  7,  0, BGEVENT_READ, WardenPhoto
	bg_event  9,  0, BGEVENT_READ, SafariZonePhoto

	def_object_events
	object_event  2,  4, SPRITE_LASS, SPRITEMOVEDATA_STANDING_RIGHT, 0, 0, -1, -1, PAL_NPC_GREEN, OBJECTTYPE_SCRIPT, 0, WardensGranddaughter, -1
