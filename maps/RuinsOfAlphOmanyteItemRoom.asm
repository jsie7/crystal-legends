	object_const_def
	const RUINSOFALPHOMANYTEITEMROOM_POKE_BALL1
	const RUINSOFALPHOMANYTEITEMROOM_POKE_BALL2
	const RUINSOFALPHOMANYTEITEMROOM_POKE_BALL3
	const RUINSOFALPHOMANYTEITEMROOM_POKE_BALL4
if DEF(_CRYSTALLEGENDS)
	const RUINSOFALPHOMANYTEITEMROOM_OMANYTE
endc

RuinsOfAlphOmanyteItemRoom_MapScripts:
	def_scene_scripts

	def_callbacks
if DEF(_CRYSTALLEGENDS)
	callback MAPCALLBACK_OBJECTS, RuinsOfAlphOmanyteItemRoomOmanyteCallback
endc

if DEF(_CRYSTALLEGENDS)
RuinsOfAlphOmanyteItemRoomOmanyteCallback:
	checkevent EVENT_GOT_OMANYTE_FROM_ALPH
	iftrue .Hide
	checkevent EVENT_SOLVED_OMANYTE_PUZZLE
	iffalse .Hide
	checkevent EVENT_WALL_OPENED_IN_OMANYTE_CHAMBER
	iffalse .Hide
	appear RUINSOFALPHOMANYTEITEMROOM_OMANYTE
	endcallback

.Hide:
	disappear RUINSOFALPHOMANYTEITEMROOM_OMANYTE
	endcallback

RuinsOfAlphOmanyteItemRoomOmanyteScript:
	faceplayer
	opentext
	cry OMANYTE
	writetext RuinsOfAlphOmanyteItemRoomOmanyteOfferText
	yesorno
	iffalse .Declined
	givepoke OMANYTE, 26
	ifequal 2, .StorageFull
	setevent EVENT_GOT_OMANYTE_FROM_ALPH
	writetext RuinsOfAlphOmanyteItemRoomOmanyteJoinedText
	playsound SFX_CAUGHT_MON
	waitsfx
	waitbutton
	closetext
	disappear RUINSOFALPHOMANYTEITEMROOM_OMANYTE
	end

.Declined:
	writetext RuinsOfAlphOmanyteItemRoomOmanyteWaitText
	sjump .Wait

.StorageFull:
	writetext RuinsOfAlphOmanyteItemRoomOmanyteStorageFullText
	promptbutton
	writetext RuinsOfAlphOmanyteItemRoomOmanyteWaitText
.Wait:
	waitbutton
	closetext
	end
endc

RuinsOfAlphOmanyteItemRoomMysteryberry:
	itemball MYSTERYBERRY

RuinsOfAlphOmanyteItemRoomMysticWater:
	itemball MYSTIC_WATER

RuinsOfAlphOmanyteItemRoomStardust:
	itemball STARDUST

RuinsOfAlphOmanyteItemRoomStarPiece:
	itemball STAR_PIECE

RuinsOfAlphOmanyteItemRoomAncientReplica:
	jumptext RuinsOfAlphOmanyteItemRoomAncientReplicaText

RuinsOfAlphOmanyteItemRoomAncientReplicaText:
	text "It's a replica of"
	line "an ancient #-"
	cont "MON."
	done

if DEF(_CRYSTALLEGENDS)
RuinsOfAlphOmanyteItemRoomOmanyteOfferText:
	text "The completed"
	line "picture awakened"
	cont "OMANYTE!"

	para "OMANYTE wants to"
	line "join you."
	done

RuinsOfAlphOmanyteItemRoomOmanyteJoinedText:
	text "OMANYTE joined"
	line "you!"
	done

RuinsOfAlphOmanyteItemRoomOmanyteWaitText:
	text "OMANYTE will wait"
	line "in this hidden"
	cont "room."
	done

RuinsOfAlphOmanyteItemRoomOmanyteStorageFullText:
	text "Your party and"
	line "Box are both full!"
	done
endc

RuinsOfAlphOmanyteItemRoom_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event  3,  9, RUINS_OF_ALPH_OMANYTE_CHAMBER, 5
	warp_event  4,  9, RUINS_OF_ALPH_OMANYTE_CHAMBER, 5
	warp_event  3,  1, RUINS_OF_ALPH_OMANYTE_WORD_ROOM, 1
	warp_event  4,  1, RUINS_OF_ALPH_OMANYTE_WORD_ROOM, 2

	def_coord_events

	def_bg_events
	bg_event  2,  1, BGEVENT_READ, RuinsOfAlphOmanyteItemRoomAncientReplica
	bg_event  5,  1, BGEVENT_READ, RuinsOfAlphOmanyteItemRoomAncientReplica

	def_object_events
	object_event  2,  6, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, RuinsOfAlphOmanyteItemRoomMysteryberry, EVENT_PICKED_UP_MYSTERYBERRY_FROM_OMANYTE_ITEM_ROOM
	object_event  5,  6, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, RuinsOfAlphOmanyteItemRoomMysticWater, EVENT_PICKED_UP_MYSTIC_WATER_FROM_OMANYTE_ITEM_ROOM
	object_event  2,  4, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, RuinsOfAlphOmanyteItemRoomStardust, EVENT_PICKED_UP_STARDUST_FROM_OMANYTE_ITEM_ROOM
	object_event  5,  4, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, RuinsOfAlphOmanyteItemRoomStarPiece, EVENT_PICKED_UP_STAR_PIECE_FROM_OMANYTE_ITEM_ROOM
if DEF(_CRYSTALLEGENDS)
	object_event  3,  3, SPRITE_OMANYTE, SPRITEMOVEDATA_POKEMON, 0, 0, -1, -1, PAL_NPC_BLUE, OBJECTTYPE_SCRIPT, 0, RuinsOfAlphOmanyteItemRoomOmanyteScript, -1
endc
