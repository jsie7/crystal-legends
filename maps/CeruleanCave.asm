	object_const_def
	const CERULEANCAVE_SCIENTIST_MITCH
	const CERULEANCAVE_SCIENTIST_ROSS
	const CERULEANCAVE_GRUNT_M_1
	const CERULEANCAVE_GRUNT_F_1
	const CERULEANCAVE_GRUNT_M_2
	const CERULEANCAVE_GRUNT_F_2
	const CERULEANCAVE_TWISTEDSPOON
	const CERULEANCAVE_LUCKY_EGG
	const CERULEANCAVE_SACRED_ASH
	const CERULEANCAVE_MASTER_BALL

CeruleanCave_MapScripts:
	def_scene_scripts

	def_callbacks

TrainerCeruleanCaveScientistMitch:
	trainer SCIENTIST, MITCH2, EVENT_BEAT_CERULEAN_CAVE_SCIENTIST_1, CeruleanCaveScientistMitchSeenText, CeruleanCaveScientistMitchBeatenText, 0, .Script
.Script:
	endifjustbattled
	opentext
	writetext CeruleanCaveScientistMitchAfterText
	waitbutton
	closetext
	end

TrainerCeruleanCaveScientistRoss:
	trainer SCIENTIST, ROSS2, EVENT_BEAT_CERULEAN_CAVE_SCIENTIST_2, CeruleanCaveScientistRossSeenText, CeruleanCaveScientistRossBeatenText, 0, .Script
.Script:
	endifjustbattled
	opentext
	writetext CeruleanCaveScientistRossAfterText
	waitbutton
	closetext
	end

TrainerCeruleanCaveGruntM1:
	trainer GRUNTM, GRUNTM_32, EVENT_BEAT_CERULEAN_CAVE_GRUNT_M_1, CeruleanCaveGruntM1SeenText, CeruleanCaveGruntM1BeatenText, 0, .Script
.Script:
	endifjustbattled
	opentext
	writetext CeruleanCaveGruntM1AfterText
	waitbutton
	closetext
	end

TrainerCeruleanCaveGruntF1:
	trainer GRUNTF, GRUNTF_6, EVENT_BEAT_CERULEAN_CAVE_GRUNT_F_1, CeruleanCaveGruntF1SeenText, CeruleanCaveGruntF1BeatenText, 0, .Script
.Script:
	endifjustbattled
	opentext
	writetext CeruleanCaveGruntF1AfterText
	waitbutton
	closetext
	end

TrainerCeruleanCaveGruntM2:
	trainer GRUNTM, GRUNTM_33, EVENT_BEAT_CERULEAN_CAVE_GRUNT_M_2, CeruleanCaveGruntM2SeenText, CeruleanCaveGruntM2BeatenText, 0, .Script
.Script:
	endifjustbattled
	opentext
	writetext CeruleanCaveGruntM2AfterText
	waitbutton
	closetext
	end

TrainerCeruleanCaveGruntF2:
	trainer GRUNTF, GRUNTF_7, EVENT_BEAT_CERULEAN_CAVE_GRUNT_F_2, CeruleanCaveGruntF2SeenText, CeruleanCaveGruntF2BeatenText, 0, .Script
.Script:
	endifjustbattled
	opentext
	writetext CeruleanCaveGruntF2AfterText
	waitbutton
	closetext
	end

CeruleanCaveTwistedSpoon:
	itemball TWISTEDSPOON

CeruleanCaveLuckyEgg:
	itemball LUCKY_EGG

CeruleanCaveSacredAsh:
	itemball SACRED_ASH

CeruleanCaveMasterBall:
	itemball MASTER_BALL

CeruleanCaveHiddenBrightPowder:
	hiddenitem BRIGHTPOWDER, EVENT_CERULEAN_CAVE_HIDDEN_BRIGHTPOWDER

CeruleanCaveContainmentTerminal:
	playsound SFX_BOOT_PC
	opentext
	checkevent EVENT_CAUGHT_CERULEAN_CAVE_COUNTERPART
	iftrue .Caught
	checkevent EVENT_BEAT_GIOVANNI
	iftrue .Released
	writetext CeruleanCaveContainmentLockedText
	sjump .Done
.Released:
	writetext CeruleanCaveContainmentReleasedText
	sjump .Done
.Caught:
	writetext CeruleanCaveContainmentCaughtText
.Done:
	waitbutton
	closetext
	end

CeruleanCaveEmptyTable:
	opentext
	writetext CeruleanCaveEmptyTableText
	waitbutton
	closetext
	end

CeruleanCaveWestTerminal:
	playsound SFX_BOOT_PC
	opentext
	writetext CeruleanCaveWestTerminalText
	waitbutton
	closetext
	end

CeruleanCaveBrokenSamples:
	opentext
	writetext CeruleanCaveBrokenSamplesText
	waitbutton
	closetext
	end

CeruleanCaveEastTerminal:
	playsound SFX_BOOT_PC
	opentext
	writetext CeruleanCaveEastTerminalText
	waitbutton
	closetext
	end

CeruleanCaveWorkbench:
	playsound SFX_BOOT_PC
	opentext
	writetext CeruleanCaveWorkbenchText
	waitbutton
	closetext
	end

CeruleanCaveScientistMitchSeenText:
	text "There are two"
	line "viable outcomes."

	para "You won't decide"
	line "which one!"
	done

CeruleanCaveScientistMitchBeatenText:
	text "The result defies"
	line "my projection…"
	done

CeruleanCaveScientistMitchAfterText:
	text "We proved either"
	line "outcome can live."

	para "The BOSS only"
	line "cares which obeys."
	done

CeruleanCaveScientistRossSeenText:
	text "This machinery"
	line "works again!"

	para "I'll protect the"
	line "data we recovered!"
	done

CeruleanCaveScientistRossBeatenText:
	text "The system is"
	line "slipping away!"
	done

CeruleanCaveScientistRossAfterText:
	text "We restored these"
	line "abandoned systems."

	para "The PROJECT data"
	line "came from elsewhere."
	done

CeruleanCaveGruntM1SeenText:
	text "This is a closed"
	line "ROCKET operation!"

	para "Turn around!"
	done

CeruleanCaveGruntM1BeatenText:
	text "You broke through"
	line "the perimeter!"
	done

CeruleanCaveGruntM1AfterText:
	text "Nobody outside the"
	line "inner circle knew."

	para "How did you find"
	line "this place?"
	done

CeruleanCaveGruntF1SeenText:
	text "The BOSS came here"
	line "for the subject."

	para "You won't reach"
	line "either of them!"
	done

CeruleanCaveGruntF1BeatenText:
	text "I failed the BOSS…"
	done

CeruleanCaveGruntF1AfterText:
	text "The subject was"
	line "already waiting."

	para "It's as if it knew"
	line "he would return."
	done

CeruleanCaveGruntM2SeenText:
	text "GIOVANNI is ahead."

	para "For you, there is"
	line "no retreat!"
	done

CeruleanCaveGruntM2BeatenText:
	text "Then I have no"
	line "retreat either…"
	done

CeruleanCaveGruntM2AfterText:
	text "Go on, then."

	para "The BOSS never"
	line "needed our faith."
	done

CeruleanCaveGruntF2SeenText:
	text "GIOVANNI will make"
	line "TEAM ROCKET whole!"
	done

CeruleanCaveGruntF2BeatenText:
	text "Our comeback…"
	done

CeruleanCaveGruntF2AfterText:
	text "We waited years"
	line "for his return."

	para "What happens to us"
	line "if he loses?"
	done

CeruleanCaveContainmentLockedText:
	text "CONTAINMENT:"
	line "LOCKED"

	para "SUBJECT STATUS:"
	line "STABLE"
	done

CeruleanCaveContainmentReleasedText:
	text "CONTAINMENT:"
	line "OPEN"

	para "SUBJECT STATUS:"
	line "ACTIVE"
	done

CeruleanCaveContainmentCaughtText:
	text "CONTAINMENT:"
	line "EMPTY"

	para "SUBJECT STATUS:"
	line "TRANSFER COMPLETE"
	done

CeruleanCaveEmptyTableText:
	text "Deep scratches mar"
	line "the empty table."

	para "Heavy equipment was"
	line "removed recently."
	done

CeruleanCaveWestTerminalText:
	text "LOG: GOLDENROD"

	para "The intercepted"
	line "signal carried the"
	cont "complete data set."
	done

CeruleanCaveBrokenSamplesText:
	text "Broken sample trays"
	line "litter the table."

	para "Every label has"
	line "been destroyed."
	done

CeruleanCaveEastTerminalText:
	text "PROJECT MODEL:"

	para "Two viable outcomes"
	line "confirmed."

	para "Neither is marked"
	line "as the original."
	done

CeruleanCaveWorkbenchText:
	text "A work log details"
	line "restored machinery"
	cont "and cave power."

	para "No creation work"
	line "was performed here."
	done

CeruleanCave_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event 21, 33, ROUTE_4, 2

	def_coord_events

	def_bg_events
	bg_event  4,  4, BGEVENT_READ, CeruleanCaveContainmentTerminal
	bg_event  5,  4, BGEVENT_READ, CeruleanCaveContainmentTerminal
	bg_event  4,  8, BGEVENT_READ, CeruleanCaveEmptyTable
	bg_event  5,  8, BGEVENT_READ, CeruleanCaveEmptyTable
	bg_event  4, 20, BGEVENT_READ, CeruleanCaveWestTerminal
	bg_event  5, 20, BGEVENT_READ, CeruleanCaveWestTerminal
	bg_event  6, 24, BGEVENT_READ, CeruleanCaveBrokenSamples
	bg_event  7, 24, BGEVENT_READ, CeruleanCaveBrokenSamples
	bg_event  8, 24, BGEVENT_READ, CeruleanCaveEastTerminal
	bg_event  9, 24, BGEVENT_READ, CeruleanCaveEastTerminal
	bg_event  8, 29, BGEVENT_READ, CeruleanCaveWorkbench
	bg_event  9, 29, BGEVENT_READ, CeruleanCaveWorkbench
	bg_event  2, 30, BGEVENT_ITEM, CeruleanCaveHiddenBrightPowder

	def_object_events
	object_event  5, 21, SPRITE_SCIENTIST, SPRITEMOVEDATA_STANDING_UP, 0, 0, -1, -1, PAL_NPC_BLUE, OBJECTTYPE_TRAINER, 0, TrainerCeruleanCaveScientistMitch, EVENT_BEAT_GIOVANNI
	object_event  6, 28, SPRITE_SCIENTIST, SPRITEMOVEDATA_STANDING_LEFT, 0, 0, -1, -1, PAL_NPC_BLUE, OBJECTTYPE_TRAINER, 2, TrainerCeruleanCaveScientistRoss, EVENT_BEAT_GIOVANNI
	object_event 18, 29, SPRITE_ROCKET, SPRITEMOVEDATA_STANDING_UP, 0, 0, -1, -1, PAL_NPC_BROWN, OBJECTTYPE_TRAINER, 3, TrainerCeruleanCaveGruntM1, EVENT_BEAT_GIOVANNI
	object_event 24, 19, SPRITE_ROCKET_GIRL, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, PAL_NPC_RED, OBJECTTYPE_TRAINER, 3, TrainerCeruleanCaveGruntF1, EVENT_BEAT_GIOVANNI
	object_event 18, 12, SPRITE_ROCKET, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, PAL_NPC_BROWN, OBJECTTYPE_TRAINER, 2, TrainerCeruleanCaveGruntM2, EVENT_BEAT_GIOVANNI
	object_event  5, 16, SPRITE_ROCKET_GIRL, SPRITEMOVEDATA_STANDING_RIGHT, 0, 0, -1, -1, PAL_NPC_RED, OBJECTTYPE_TRAINER, 1, TrainerCeruleanCaveGruntF2, EVENT_BEAT_GIOVANNI
	object_event 24,  2, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, CeruleanCaveTwistedSpoon, EVENT_CERULEAN_CAVE_TWISTEDSPOON
	object_event 20, 13, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, CeruleanCaveLuckyEgg, EVENT_CERULEAN_CAVE_LUCKY_EGG
	object_event 13, 18, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, CeruleanCaveSacredAsh, EVENT_CERULEAN_CAVE_SACRED_ASH
	object_event 13, 31, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, CeruleanCaveMasterBall, EVENT_CERULEAN_CAVE_MASTER_BALL
