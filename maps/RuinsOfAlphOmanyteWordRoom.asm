	object_const_def
if DEF(_CRYSTALLEGENDS)
	const RUINSOFALPHOMANYTEWORDROOM_OMANYTE
endc

RuinsOfAlphOmanyteWordRoom_MapScripts:
	def_scene_scripts

	def_callbacks
if DEF(_CRYSTALLEGENDS)
	callback MAPCALLBACK_OBJECTS, RuinsOfAlphOmanyteWordRoomOmanyteCallback
endc

if DEF(_CRYSTALLEGENDS)
RuinsOfAlphOmanyteWordRoomOmanyteCallback:
	checkevent EVENT_GOT_OMANYTE_FROM_ALPH
	iftrue .Hide
	checkevent EVENT_SOLVED_OMANYTE_PUZZLE
	iffalse .Hide
	checkevent EVENT_WALL_OPENED_IN_OMANYTE_CHAMBER
	iffalse .Hide
	appear RUINSOFALPHOMANYTEWORDROOM_OMANYTE
	endcallback

.Hide:
	disappear RUINSOFALPHOMANYTEWORDROOM_OMANYTE
	endcallback

RuinsOfAlphOmanyteWordRoomOmanyteScript:
	faceplayer
	opentext
	cry OMANYTE
	writetext RuinsOfAlphOmanyteWordRoomOmanyteOfferText
	yesorno
	iffalse .Declined
	givepoke OMANYTE, 26
	ifequal 2, .StorageFull
	setevent EVENT_GOT_OMANYTE_FROM_ALPH
	writetext RuinsOfAlphOmanyteWordRoomOmanyteJoinedText
	playsound SFX_CAUGHT_MON
	waitsfx
	waitbutton
	closetext
	disappear RUINSOFALPHOMANYTEWORDROOM_OMANYTE
	end

.Declined:
	writetext RuinsOfAlphOmanyteWordRoomOmanyteWaitText
	sjump .Wait

.StorageFull:
	writetext RuinsOfAlphOmanyteWordRoomOmanyteStorageFullText
	promptbutton
	writetext RuinsOfAlphOmanyteWordRoomOmanyteWaitText
.Wait:
	waitbutton
	closetext
	end

RuinsOfAlphOmanyteWordRoomOmanyteOfferText:
	text "The completed"
	line "picture awakened"
	cont "OMANYTE!"

	para "OMANYTE wants to"
	line "join you."
	done

RuinsOfAlphOmanyteWordRoomOmanyteJoinedText:
	text "OMANYTE joined"
	line "you!"
	done

RuinsOfAlphOmanyteWordRoomOmanyteWaitText:
	text "OMANYTE will wait"
	line "in this hidden"
	cont "room."
	done

RuinsOfAlphOmanyteWordRoomOmanyteStorageFullText:
	text "Your party and"
	line "Box are both full!"
	done
endc

RuinsOfAlphOmanyteWordRoom_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event  9,  7, RUINS_OF_ALPH_OMANYTE_ITEM_ROOM, 3
	warp_event 10,  7, RUINS_OF_ALPH_OMANYTE_ITEM_ROOM, 4
	warp_event 17, 13, RUINS_OF_ALPH_INNER_CHAMBER, 6

	def_coord_events

	def_bg_events

	def_object_events
if DEF(_CRYSTALLEGENDS)
	object_event 15, 10, SPRITE_OMANYTE, SPRITEMOVEDATA_POKEMON, 0, 0, -1, -1, PAL_NPC_BLUE, OBJECTTYPE_SCRIPT, 0, RuinsOfAlphOmanyteWordRoomOmanyteScript, -1
endc
