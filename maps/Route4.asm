	object_const_def
	const ROUTE4_YOUNGSTER
	const ROUTE4_LASS1
	const ROUTE4_LASS2
	const ROUTE4_POKE_BALL
if DEF(_CRYSTALLEGENDS)
	const ROUTE4_CERULEAN_CAVE_GUARD
endc

Route4_MapScripts:
	def_scene_scripts

	def_callbacks
if DEF(_CRYSTALLEGENDS)
	callback MAPCALLBACK_OBJECTS, Route4CeruleanCaveGuardCallback
endc

if DEF(_CRYSTALLEGENDS)
Route4CeruleanCaveGuardCallback:
	checkevent EVENT_PROJECT_MEW_RESOLVED
	iffalse .ShowGuard
	checkevent EVENT_SILVER_BIRD_RELEASED
	iffalse .ShowGuard
	readvar VAR_BADGES
	ifless 14, .ShowGuard
	loadmem wMap1ObjectSprite + (ROUTE4_CERULEAN_CAVE_GUARD - 2) * MAPOBJECT_LENGTH, 0
	endcallback

.ShowGuard:
	loadmem wMap1ObjectSprite + (ROUTE4_CERULEAN_CAVE_GUARD - 2) * MAPOBJECT_LENGTH, SPRITE_ROCKET
	endcallback

Route4CeruleanCaveGuardScript:
	faceplayer
	opentext
	checkevent EVENT_PROJECT_MEW_RESOLVED
	iffalse .ProjectMewUnresolved
	checkevent EVENT_SILVER_BIRD_RELEASED
	iffalse .SilverBirdUnreleased
	writetext Route4CeruleanCaveGuardBadgesText
	waitbutton
	closetext
	end

.ProjectMewUnresolved:
	writetext Route4CeruleanCaveGuardResearchText
	waitbutton
	closetext
	end

.SilverBirdUnreleased:
	writetext Route4CeruleanCaveGuardBirdText
	waitbutton
	closetext
	end
endc

TrainerBirdKeeperHank:
	trainer BIRD_KEEPER, HANK, EVENT_BEAT_BIRD_KEEPER_HANK, BirdKeeperHankSeenText, BirdKeeperHankBeatenText, 0, .Script

.Script:
	endifjustbattled
	opentext
	writetext BirdKeeperHankAfterBattleText
	waitbutton
	closetext
	end

TrainerPicnickerHope:
	trainer PICNICKER, HOPE, EVENT_BEAT_PICNICKER_HOPE, PicnickerHopeSeenText, PicnickerHopeBeatenText, 0, .Script

.Script:
	endifjustbattled
	opentext
	writetext PicnickerHopeAfterBattleText
	waitbutton
	closetext
	end

TrainerPicnickerSharon:
	trainer PICNICKER, SHARON, EVENT_BEAT_PICNICKER_SHARON, PicnickerSharonSeenText, PicnickerSharonBeatenText, 0, .Script

.Script:
	endifjustbattled
	opentext
	writetext PicnickerSharonAfterBattleText
	waitbutton
	closetext
	end

MtMoonSquareSign:
	jumptext MtMoonSquareSignText

Route4HPUp:
	itemball HP_UP

Route4HiddenUltraBall:
	hiddenitem ULTRA_BALL, EVENT_ROUTE_4_HIDDEN_ULTRA_BALL

if DEF(_CRYSTALLEGENDS)
Route4CeruleanCaveGuardResearchText:
	text "This cave is under"
	line "ROCKET control."

	para "The equipment here"
	line "isn't ready yet."
	done

Route4CeruleanCaveGuardBirdText:
	text "Boss's orders."

	para "Settle your old"
	line "business before"
	cont "coming back here."
	done

Route4CeruleanCaveGuardBadgesText:
	text "The #MON inside"
	line "would crush you."

	para "Win more KANTO"
	line "BADGES, then try"
	cont "your luck."
	done
endc

BirdKeeperHankSeenText:
	text "I'm raising my"
	line "#MON. Want to"
	cont "battle with me?"
	done

BirdKeeperHankBeatenText:
	text "Ack! I lost that"
	line "one…"
	done

BirdKeeperHankAfterBattleText:
	text "If you have a"
	line "specific #MON"

	para "that you want to"
	line "raise, put it out"

	para "first, then switch"
	line "it right away."

	para "That's how to do"
	line "it."
	done

PicnickerHopeSeenText:
	text "I have a feeling"
	line "that I can win."

	para "Let's see if I'm"
	line "right!"
	done

PicnickerHopeBeatenText:
	text "Aww, you are too"
	line "strong."
	done

PicnickerHopeAfterBattleText:
	text "I heard CLEFAIRY"
	line "appear at MT.MOON."

	para "But where could"
	line "they be?"
	done

PicnickerSharonSeenText:
	text "Um…"
	line "I…"
	done

PicnickerSharonBeatenText:
	text "…"
	done

PicnickerSharonAfterBattleText:
	text "……I'll go train"
	line "some more…"
	done

MtMoonSquareSignText:
	text "MT.MOON SQUARE"

	para "Just go up the"
	line "stairs."
	done

Route4_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event  2,  5, MOUNT_MOON, 2
if DEF(_CRYSTALLEGENDS)
	warp_event 38,  3, CERULEAN_CAVE, 1
endc

	def_coord_events

	def_bg_events
	bg_event  3,  7, BGEVENT_READ, MtMoonSquareSign
	bg_event 10,  3, BGEVENT_ITEM, Route4HiddenUltraBall

	def_object_events
	object_event 17,  9, SPRITE_YOUNGSTER, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, PAL_NPC_BLUE, OBJECTTYPE_TRAINER, 3, TrainerBirdKeeperHank, -1
	object_event  9,  8, SPRITE_LASS, SPRITEMOVEDATA_STANDING_LEFT, 0, 0, -1, -1, PAL_NPC_GREEN, OBJECTTYPE_TRAINER, 4, TrainerPicnickerHope, -1
	object_event 21,  6, SPRITE_LASS, SPRITEMOVEDATA_STANDING_RIGHT, 0, 0, -1, -1, PAL_NPC_GREEN, OBJECTTYPE_TRAINER, 4, TrainerPicnickerSharon, -1
	object_event 26,  3, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, Route4HPUp, EVENT_ROUTE_4_HP_UP
if DEF(_CRYSTALLEGENDS)
	object_event 38,  4, SPRITE_ROCKET, SPRITEMOVEDATA_STANDING_RIGHT, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, Route4CeruleanCaveGuardScript, -1
endc
