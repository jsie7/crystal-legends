	object_const_def
	const RADIOTOWERTRANSMITTERANNEX_MEW
	const RADIOTOWERTRANSMITTERANNEX_MEWTWO

RadioTowerTransmitterAnnex_MapScripts:
	def_scene_scripts

	def_callbacks
	callback MAPCALLBACK_TILES, RadioTowerTransmitterAnnexExitCallback
	callback MAPCALLBACK_OBJECTS, RadioTowerTransmitterAnnexSubjectCallback

RadioTowerTransmitterAnnexExitCallback:
	checkevent EVENT_PROJECT_MEW_RESOLVED
	iffalse .Closed
	changeblock 4, 6, $07 ; open return stairs
	endcallback

.Closed:
	changeblock 4, 6, $23 ; sealed return wall
	endcallback

RadioTowerTransmitterAnnexSubjectCallback:
	checkevent EVENT_CAUGHT_PROJECT_MEW_SUBJECT
	iftrue .HideBoth
	checkevent EVENT_PROJECT_MEW_RESOLVED
	iffalse .ShowMew
	checkevent EVENT_PROJECT_MEW_TRANSFORMED
	iftrue .ShowMewtwo

.ShowMew:
	appear RADIOTOWERTRANSMITTERANNEX_MEW
	disappear RADIOTOWERTRANSMITTERANNEX_MEWTWO
	endcallback

.ShowMewtwo:
	disappear RADIOTOWERTRANSMITTERANNEX_MEW
	appear RADIOTOWERTRANSMITTERANNEX_MEWTWO
	endcallback

.HideBoth:
	disappear RADIOTOWERTRANSMITTERANNEX_MEW
	disappear RADIOTOWERTRANSMITTERANNEX_MEWTWO
	endcallback

RadioTowerTransmitterAnnexUploadMonitorScript:
	jumptext RadioTowerTransmitterAnnexUploadMonitorText

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
	disappear RADIOTOWERTRANSMITTERANNEX_MEWTWO
	appear RADIOTOWERTRANSMITTERANNEX_MEW
	playsound SFX_WARP_TO
	waitsfx
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
	disappear RADIOTOWERTRANSMITTERANNEX_MEW
	appear RADIOTOWERTRANSMITTERANNEX_MEWTWO
	playsound SFX_WARP_TO
	waitsfx
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

RadioTowerTransmitterAnnexMewScript:
	faceplayer
	opentext
	cry MEW
	checkevent EVENT_PROJECT_MEW_RESOLVED
	iftrue .Resolved
	writetext RadioTowerTransmitterAnnexUnstableMewText
	waitbutton
	closetext
	end

.Resolved:
	writetext RadioTowerTransmitterAnnexMewReadyText
	waitbutton
	closetext
	end

RadioTowerTransmitterAnnexMewtwoScript:
	faceplayer
	opentext
	cry MEWTWO
	writetext RadioTowerTransmitterAnnexMewtwoReadyText
	waitbutton
	closetext
	end

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

RadioTowerTransmitterAnnexMewReadyText:
	text "MEW waits there"
	line "beyond the field."
	done

RadioTowerTransmitterAnnexMewtwoReadyText:
	text "MEWTWO waits there"
	line "beyond the field."
	done

RadioTowerTransmitterAnnex_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event 4, 7, RADIO_TOWER_5F, 3

	def_coord_events

	def_bg_events
	bg_event 2, 1, BGEVENT_UP, RadioTowerTransmitterAnnexUploadMonitorScript
	bg_event 6, 1, BGEVENT_UP, RadioTowerTransmitterAnnexTerminalScript

	def_object_events
	object_event 4, 4, SPRITE_MEW, SPRITEMOVEDATA_POKEMON, 0, 0, -1, -1, PAL_NPC_PINK, OBJECTTYPE_SCRIPT, 0, RadioTowerTransmitterAnnexMewScript, -1
	object_event 4, 4, SPRITE_MEWTWO, SPRITEMOVEDATA_POKEMON, 0, 0, -1, -1, PAL_NPC_PINK, OBJECTTYPE_SCRIPT, 0, RadioTowerTransmitterAnnexMewtwoScript, -1
