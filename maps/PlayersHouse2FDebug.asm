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
	ifequal 1, .SuppliesMenu
	ifequal 2, .Exit
	ifequal 3, .Exit
	sjump .Exit

.SuppliesMenu:
	loadmenu PlayersHouse2FDebugSuppliesMenuHeader
	verticalmenu
	closewindow
	ifequal 1, .RareCandy
	ifequal 2, .BallsMenu
	ifequal 3, .HealingMenu
	ifequal 4, .EvolutionStonesMenu
	ifequal 5, .TradeItemsMenu
	sjump .MainMenu

.RareCandy:
	verbosegiveitem RARE_CANDY, 10
	sjump .SuppliesMenu

.BallsMenu:
	loadmenu PlayersHouse2FDebugBallsMenuHeader
	verticalmenu
	closewindow
	ifequal 1, .MasterBall
	ifequal 2, .UltraBall
	sjump .SuppliesMenu

.MasterBall:
	verbosegiveitem MASTER_BALL, 10
	sjump .BallsMenu

.UltraBall:
	verbosegiveitem ULTRA_BALL, 10
	sjump .BallsMenu

.HealingMenu:
	loadmenu PlayersHouse2FDebugHealingMenuHeader
	verticalmenu
	closewindow
	ifequal 1, .FullRestore
	ifequal 2, .MaxRevive
	ifequal 3, .MaxElixer
	ifequal 4, .MaxRepel
	ifequal 5, .EscapeRope
	sjump .SuppliesMenu

.FullRestore:
	verbosegiveitem FULL_RESTORE, 10
	sjump .HealingMenu

.MaxRevive:
	verbosegiveitem MAX_REVIVE, 10
	sjump .HealingMenu

.MaxElixer:
	verbosegiveitem MAX_ELIXER, 10
	sjump .HealingMenu

.MaxRepel:
	verbosegiveitem MAX_REPEL, 10
	sjump .HealingMenu

.EscapeRope:
	verbosegiveitem ESCAPE_ROPE, 10
	sjump .HealingMenu

.EvolutionStonesMenu:
	loadmenu PlayersHouse2FDebugEvolutionStonesMenuHeader
	verticalmenu
	closewindow
	ifequal 1, .MoonStone
	ifequal 2, .FireStone
	ifequal 3, .Thunderstone
	ifequal 4, .WaterStone
	ifequal 5, .LeafStone
	ifequal 6, .SunStone
	sjump .SuppliesMenu

.MoonStone:
	verbosegiveitem MOON_STONE, 10
	sjump .EvolutionStonesMenu

.FireStone:
	verbosegiveitem FIRE_STONE, 10
	sjump .EvolutionStonesMenu

.Thunderstone:
	verbosegiveitem THUNDERSTONE, 10
	sjump .EvolutionStonesMenu

.WaterStone:
	verbosegiveitem WATER_STONE, 10
	sjump .EvolutionStonesMenu

.LeafStone:
	verbosegiveitem LEAF_STONE, 10
	sjump .EvolutionStonesMenu

.SunStone:
	verbosegiveitem SUN_STONE, 10
	sjump .EvolutionStonesMenu

.TradeItemsMenu:
	loadmenu PlayersHouse2FDebugTradeItemsMenuHeader
	verticalmenu
	closewindow
	ifequal 1, .KingsRock
	ifequal 2, .MetalCoat
	ifequal 3, .DragonScale
	ifequal 4, .UpGrade
	sjump .SuppliesMenu

.KingsRock:
	verbosegiveitem KINGS_ROCK, 10
	sjump .TradeItemsMenu

.MetalCoat:
	verbosegiveitem METAL_COAT, 10
	sjump .TradeItemsMenu

.DragonScale:
	verbosegiveitem DRAGON_SCALE, 10
	sjump .TradeItemsMenu

.UpGrade:
	verbosegiveitem UP_GRADE, 10
	sjump .TradeItemsMenu

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

PlayersHouse2FDebugSuppliesMenuHeader:
	db MENU_BACKUP_TILES ; flags
	menu_coords 0, 1, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1
	dw .MenuData
	db 1 ; default option

.MenuData:
	db STATICMENU_CURSOR | STATICMENU_WRAP ; flags
	db 6 ; items
	db "RARE CANDY x10@"
	db "BALLS@"
	db "HEALING@"
	db "EVO STONES@"
	db "TRADE ITEMS@"
	db "BACK@"

PlayersHouse2FDebugBallsMenuHeader:
	db MENU_BACKUP_TILES ; flags
	menu_coords 0, 3, SCREEN_WIDTH - 1, 11
	dw .MenuData
	db 1 ; default option

.MenuData:
	db STATICMENU_CURSOR | STATICMENU_WRAP ; flags
	db 3 ; items
	db "MASTER BALL x10@"
	db "ULTRA BALL x10@"
	db "BACK@"

PlayersHouse2FDebugHealingMenuHeader:
	db MENU_BACKUP_TILES ; flags
	menu_coords 0, 1, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1
	dw .MenuData
	db 1 ; default option

.MenuData:
	db STATICMENU_CURSOR | STATICMENU_WRAP ; flags
	db 6 ; items
	db "FULL RESTORE x10@"
	db "MAX REVIVE x10@"
	db "MAX ELIXER x10@"
	db "MAX REPEL x10@"
	db "ESCAPE ROPE x10@"
	db "BACK@"

PlayersHouse2FDebugEvolutionStonesMenuHeader:
	db MENU_BACKUP_TILES ; flags
	menu_coords 0, 0, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1
	dw .MenuData
	db 1 ; default option

.MenuData:
	db STATICMENU_CURSOR | STATICMENU_WRAP ; flags
	db 7 ; items
	db "MOON STONE x10@"
	db "FIRE STONE x10@"
	db "THUNDERSTONE x10@"
	db "WATER STONE x10@"
	db "LEAF STONE x10@"
	db "SUN STONE x10@"
	db "BACK@"

PlayersHouse2FDebugTradeItemsMenuHeader:
	db MENU_BACKUP_TILES ; flags
	menu_coords 0, 2, SCREEN_WIDTH - 1, 14
	dw .MenuData
	db 1 ; default option

.MenuData:
	db STATICMENU_CURSOR | STATICMENU_WRAP ; flags
	db 5 ; items
	db "KING'S ROCK x10@"
	db "METAL COAT x10@"
	db "DRAGON SCALE x10@"
	db "UP-GRADE x10@"
	db "BACK@"

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
