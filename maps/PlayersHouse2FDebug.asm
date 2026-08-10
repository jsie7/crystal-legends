PlayersHouse2FDebugTVScript:
	checkevent EVENT_TEMPORARY_UNTIL_MAP_RELOAD_2
	iftrue .OpenCheatMode
	setevent EVENT_TEMPORARY_UNTIL_MAP_RELOAD_2
	opentext
	writetext PlayersHouse2FDebugNintendo64Text
	waitbutton
	closetext
	end

.OpenCheatMode:
	clearevent EVENT_TEMPORARY_UNTIL_MAP_RELOAD_2
	opentext
	writetext PlayersHouse2FDebugWarningText
	yesorno
	iffalse .Exit

.MainMenu:
	loadmenu PlayersHouse2FDebugMainMenuHeader
	verticalmenu
	closewindow
	ifequal 1, .Exit
	ifequal 2, .Exit
	ifequal 3, .Exit

.Exit:
	closetext
	end

PlayersHouse2FDebugMainMenuHeader:
	db MENU_BACKUP_TILES ; flags
	menu_coords 7, 2, SCREEN_WIDTH - 1, TEXTBOX_Y - 1
	dw .MenuData
	db 1 ; default option

.MenuData:
	db STATICMENU_CURSOR | STATICMENU_WRAP ; flags
	db 4 ; items
	db "SUPPLIES@"
	db "MONEY@"
	db "POKEMON@"
	db "EXIT@"

PlayersHouse2FDebugNintendo64Text:
	text "It's a NINTENDO 64"
	line "connected to a TV."
	done

PlayersHouse2FDebugWarningText:
	text "CHEAT MODE can add"
	line "items, money, and"
	cont "#MON."

	para "Continue?"
	done
