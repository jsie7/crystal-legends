	object_const_def
	const CINNABARPOKECENTER1F_NURSE
	const CINNABARPOKECENTER1F_COOLTRAINER_F
	const CINNABARPOKECENTER1F_FISHER

CinnabarPokecenter1F_MapScripts:
	def_scene_scripts

	def_callbacks

CinnabarPokecenter1FNurseScript:
	jumpstd PokecenterNurseScript

CinnabarPokecenter1FCooltrainerFScript:
	if DEF(_CRYSTALLEGENDS)
	checkevent EVENT_BLAINE_REQUESTED_CINNABAR_HELP
	iftrue .AfterBlaineRequest
	endc
	jumptextfaceplayer CinnabarPokecenter1FCooltrainerFText
	if DEF(_CRYSTALLEGENDS)

.AfterBlaineRequest:
	jumptextfaceplayer CinnabarPokecenter1FCooltrainerFLogText
	endc

CinnabarPokecenter1FFisherScript:
	if DEF(_CRYSTALLEGENDS)
	faceplayer
	opentext
	checkevent EVENT_BLAINE_REQUESTED_CINNABAR_HELP
	iffalse .StockText
	checkevent EVENT_RECOVERED_BLAINES_LOG
	iftrue .Recovered
	checkevent EVENT_LEARNED_LOCATION_OF_BLAINES_LOG
	iftrue .RepeatClue
	writetext CinnabarPokecenter1FFisherLogClueText
	waitbutton
	setevent EVENT_LEARNED_LOCATION_OF_BLAINES_LOG
	closetext
	end

.RepeatClue:
	writetext CinnabarPokecenter1FFisherRepeatClueText
	waitbutton
	closetext
	end

.Recovered:
	writetext CinnabarPokecenter1FFisherRecoveredText
	waitbutton
	closetext
	end

.StockText:
	writetext CinnabarPokecenter1FFisherText
	waitbutton
	closetext
	end
	else
	jumptextfaceplayer CinnabarPokecenter1FFisherText
	endc

CinnabarPokecenter1FCooltrainerFText:
	text "CINNABAR GYM's"
	line "BLAINE apparently"

	para "lives alone in the"
	line "SEAFOAM ISLANDS"
	cont "cave…"
	done

if DEF(_CRYSTALLEGENDS)
CinnabarPokecenter1FCooltrainerFLogText:
	text "The fisherman saw"
	line "the cases moved"
	cont "from the old GYM."
	done

CinnabarPokecenter1FFisherLogClueText:
	text "I saw"
	line "a flame-crested"
	cont "case after the"
	cont "volcano."

	para "It lies somewhere"
	line "in the rubble."

	para "Its clasp has a"
	line "secret mechanism."

	para "Press the crest in"
	cont "and pull the latch"
	cont "sideways."
	done

CinnabarPokecenter1FFisherRepeatClueText:
	text "The"
	line "case rests high,"
	cont "south of the pool."

	para "Press the crest in"
	line "and pull its"
	cont "warped latch."
	done

CinnabarPokecenter1FFisherRecoveredText:
	text "You got the old"
	line "case!"

	para "BLAINE will want"
	line "that log back."
	done
endc

CinnabarPokecenter1FFisherText:
	text "It's been a year"
	line "since the volcano"
	cont "erupted."
	done

CinnabarPokecenter1F_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event  3,  7, CINNABAR_ISLAND, 1
	warp_event  4,  7, CINNABAR_ISLAND, 1
	warp_event  0,  7, POKECENTER_2F, 1

	def_coord_events

	def_bg_events

	def_object_events
	object_event  3,  1, SPRITE_NURSE, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, CinnabarPokecenter1FNurseScript, -1
	object_event  7,  6, SPRITE_COOLTRAINER_F, SPRITEMOVEDATA_WALK_LEFT_RIGHT, 2, 0, -1, -1, PAL_NPC_RED, OBJECTTYPE_SCRIPT, 0, CinnabarPokecenter1FCooltrainerFScript, -1
	object_event  2,  4, SPRITE_FISHER, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, PAL_NPC_GREEN, OBJECTTYPE_SCRIPT, 0, CinnabarPokecenter1FFisherScript, -1
