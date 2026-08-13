	object_const_def
	const RADIOTOWERTRANSMITTERANNEX_SUBJECT

RadioTowerTransmitterAnnex_MapScripts:
	def_scene_scripts
	scene_script RadioTowerTransmitterAnnexLockEntryScene
	scene_script RadioTowerTransmitterAnnexNoopScene
	assert _NUM_SCENE_SCRIPTS == SCENE_RADIOTOWERTRANSMITTERANNEX_NOOP + 1

	def_callbacks
	callback MAPCALLBACK_TILES, RadioTowerTransmitterAnnexExitCallback
	callback MAPCALLBACK_OBJECTS, RadioTowerTransmitterAnnexSubjectCallback

RadioTowerTransmitterAnnexLockEntryScene:
	sdefer RadioTowerTransmitterAnnexSealEntryScript
	end

RadioTowerTransmitterAnnexNoopScene:
	end

RadioTowerTransmitterAnnexExitCallback:
	checkevent EVENT_PROJECT_MEW_RESOLVED
	iftrue .Open
	checkscene
	ifequal SCENE_RADIOTOWERTRANSMITTERANNEX_LOCK_ENTRY, .Entering
	changeblock 4, 6, $40 ; sealed return wall
	endcallback

.Entering:
	changeblock 4, 6, $07 ; open while entering
	endcallback

.Open:
	changeblock 4, 2, $01 ; open center glass
	changeblock 4, 6, $07 ; open return stairs
	endcallback

RadioTowerTransmitterAnnexSealEntryScript:
	checkevent EVENT_PROJECT_MEW_RESOLVED
	iftrue .Resolved
	applymovement PLAYER, RadioTowerTransmitterAnnexEntryMovement
	reanchormap
	playsound SFX_ENTER_DOOR
	changeblock 4, 6, $40 ; sealed return wall
	refreshmap
	setscene SCENE_RADIOTOWERTRANSMITTERANNEX_NOOP
	waitsfx
	end

.Resolved:
	setscene SCENE_RADIOTOWERTRANSMITTERANNEX_NOOP
	end

RadioTowerTransmitterAnnexSubjectCallback:
	checkevent EVENT_PROJECT_MEW_RESOLVED
	iffalse .ShowMew
	checkevent EVENT_PROJECT_MEW_TRANSFORMED
	iftrue .ShowMewtwo

.ShowMew:
	variablesprite SPRITE_PROJECT_MEW_SUBJECT, SPRITE_MEW
	endcallback

.ShowMewtwo:
	variablesprite SPRITE_PROJECT_MEW_SUBJECT, SPRITE_MEWTWO
	endcallback

RadioTowerTransmitterAnnexUploadMonitorScript:
	jumptext RadioTowerTransmitterAnnexUploadMonitorText

RadioTowerTransmitterAnnexGlassObservation:
	conditional_event EVENT_PROJECT_MEW_RESOLVED, .Script

.Script:
	cry MEW
	opentext
	writetext RadioTowerTransmitterAnnexUnstableMewText
	waitbutton
	closetext
	end

RadioTowerTransmitterAnnexTerminalScript:
	opentext
	checkevent EVENT_PROJECT_MEW_RESOLVED
	iftrue .Resolved
	writetext RadioTowerTransmitterAnnexTerminalIntroText
	waitbutton

.Menu:
	loadmenu RadioTowerTransmitterAnnexTerminalMenuHeader
	verticalmenu
	closewindow
	ifequal 1, .Reverse
	ifequal 2, .Stabilize
	sjump .Cancel

.Reverse:
	writetext RadioTowerTransmitterAnnexReverseConfirmText
	yesorno
	iffalse .Menu
	setevent EVENT_PROJECT_MEW_RESOLVED
	clearevent EVENT_PROJECT_MEW_TRANSFORMED
	variablesprite SPRITE_PROJECT_MEW_SUBJECT, SPRITE_MEW
	special LoadUsedSpritesGFX
	playsound SFX_WARP_TO
	waitsfx
	changeblock 4, 2, $01 ; open center glass
	changeblock 4, 6, $07 ; open return stairs
	refreshmap
	writetext RadioTowerTransmitterAnnexReverseCompleteText
	waitbutton
	closetext
	end

.Stabilize:
	writetext RadioTowerTransmitterAnnexStabilizeConfirmText
	yesorno
	iffalse .Menu
	setevent EVENT_PROJECT_MEW_RESOLVED
	setevent EVENT_PROJECT_MEW_TRANSFORMED
	variablesprite SPRITE_PROJECT_MEW_SUBJECT, SPRITE_MEWTWO
	special LoadUsedSpritesGFX
	playsound SFX_WARP_TO
	waitsfx
	changeblock 4, 2, $01 ; open center glass
	changeblock 4, 6, $07 ; open return stairs
	refreshmap
	writetext RadioTowerTransmitterAnnexStabilizeCompleteText
	waitbutton
	closetext
	end

.Cancel:
	writetext RadioTowerTransmitterAnnexCancelText
	waitbutton
	closetext
	end

.Resolved:
	checkevent EVENT_PROJECT_MEW_TRANSFORMED
	iftrue .ResolvedMewtwo
	writetext RadioTowerTransmitterAnnexResolvedMewText
	waitbutton
	closetext
	end

.ResolvedMewtwo:
	writetext RadioTowerTransmitterAnnexResolvedMewtwoText
	waitbutton
	closetext
	end

RadioTowerTransmitterAnnexSubjectScript:
	checkevent EVENT_PROJECT_MEW_TRANSFORMED
	iftrue RadioTowerTransmitterAnnexMewtwoScript
	sjump RadioTowerTransmitterAnnexMewScript

RadioTowerTransmitterAnnexMewScript:
	faceplayer
	cry MEW
	opentext
	checkevent EVENT_PROJECT_MEW_RESOLVED
	iftrue .Resolved
	writetext RadioTowerTransmitterAnnexUnstableMewText
	waitbutton
	closetext
	end

.Resolved:
	writetext RadioTowerTransmitterAnnexMewBattleText
	waitbutton
	closetext
	loadwildmon MEW, 30
	startbattle
	special CheckCaughtPokemon
	iffalse .NotCaught
	setevent EVENT_CAUGHT_PROJECT_MEW_SUBJECT
	disappear RADIOTOWERTRANSMITTERANNEX_SUBJECT
.NotCaught:
	reloadmapafterbattle
	end

RadioTowerTransmitterAnnexMewtwoScript:
	faceplayer
	cry MEWTWO
	opentext
	writetext RadioTowerTransmitterAnnexMewtwoBattleText
	waitbutton
	closetext
	loadwildmon MEWTWO, 30
	startbattle
	special CheckCaughtPokemon
	iffalse .NotCaught
	setevent EVENT_CAUGHT_PROJECT_MEW_SUBJECT
	disappear RADIOTOWERTRANSMITTERANNEX_SUBJECT
.NotCaught:
	reloadmapafterbattle
	end

RadioTowerTransmitterAnnexEntryMovement:
	step UP
	step_end

RadioTowerTransmitterAnnexTerminalMenuHeader:
	db MENU_BACKUP_TILES ; flags
	menu_coords 0, 0, SCREEN_WIDTH - 1, TEXTBOX_Y - 1
	dw .MenuData
	db 1 ; default option

.MenuData:
	db STATICMENU_CURSOR ; flags
	db 3 ; items
	db "REVERSE SEQ.@"
	db "STABILIZE@"
	db "CANCEL@"

RadioTowerTransmitterAnnexUploadMonitorText:
	text "UPLOAD COMPLETE"

	para "TO: GIOVANNI"

	para "PROJECT MEW data"
	line "cannot be undone."
	done

RadioTowerTransmitterAnnexTerminalIntroText:
	text "PROJECT MEW CTRL."

	para "The subject is"
	line "mid-change and"
	cont "unstable."

	para "REVERSE SEQUENCE"
	line "restores MEW."

	para "STABILIZE SEQUENCE"
	line "locks in MEWTWO."

	para "Choose a rescue"
	line "procedure."
	done

RadioTowerTransmitterAnnexReverseConfirmText:
	text "Run REVERSE"
	line "SEQUENCE?"

	para "This restores MEW"
	line "permanently."
	done

RadioTowerTransmitterAnnexStabilizeConfirmText:
	text "Run STABILIZE"
	line "SEQUENCE?"

	para "This preserves the"
	line "altered MEWTWO"
	cont "permanently."
	done

RadioTowerTransmitterAnnexReverseCompleteText:
	text "The reverse signal"
	line "takes hold."

	para "The subject is MEW"
	line "once more."

	para "Exit unlocked."
	done

RadioTowerTransmitterAnnexStabilizeCompleteText:
	text "The signal holds"
	line "the altered form."

	para "The subject is now"
	line "MEWTWO."

	para "Exit unlocked."
	done

RadioTowerTransmitterAnnexCancelText:
	text "Sequence canceled."

	para "Subject remains"
	line "unstable."
	done

RadioTowerTransmitterAnnexResolvedMewText:
	text "Sequence complete."

	para "Outcome locked:"
	line "MEW RESTORED."
	done

RadioTowerTransmitterAnnexResolvedMewtwoText:
	text "Sequence complete."

	para "Outcome locked:"
	line "MEWTWO STABILIZED."
	done

RadioTowerTransmitterAnnexUnstableMewText:
	text "The captive MEW"
	line "trembles inside"
	cont "the signal field."

	para "Its body is being"
	line "forced to change."
	done

RadioTowerTransmitterAnnexMewBattleText:
	text "MEW watches you"
	line "beyond the field."

	para "It wants to be"
	line "free!"
	done

RadioTowerTransmitterAnnexMewtwoBattleText:
	text "MEWTWO watches you"
	line "beyond the field."

	para "It wants to be"
	line "free!"
	done

RadioTowerTransmitterAnnex_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event 4, 7, RADIO_TOWER_5F, 4

	def_coord_events

	def_bg_events
	bg_event 2, 5, BGEVENT_READ, RadioTowerTransmitterAnnexUploadMonitorScript
	bg_event 6, 5, BGEVENT_READ, RadioTowerTransmitterAnnexTerminalScript
	bg_event 4, 3, BGEVENT_IFNOTSET, RadioTowerTransmitterAnnexGlassObservation

	def_object_events
	object_event 4, 2, SPRITE_PROJECT_MEW_SUBJECT, SPRITEMOVEDATA_POKEMON, 0, 0, -1, -1, PAL_NPC_PINK, OBJECTTYPE_SCRIPT, 0, RadioTowerTransmitterAnnexSubjectScript, EVENT_CAUGHT_PROJECT_MEW_SUBJECT
