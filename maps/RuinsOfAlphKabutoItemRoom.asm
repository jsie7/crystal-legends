	object_const_def
	const RUINSOFALPHKABUTOITEMROOM_POKE_BALL1
	const RUINSOFALPHKABUTOITEMROOM_POKE_BALL2
	const RUINSOFALPHKABUTOITEMROOM_POKE_BALL3
	const RUINSOFALPHKABUTOITEMROOM_POKE_BALL4
if DEF(_CRYSTALLEGENDS)
	const RUINSOFALPHKABUTOITEMROOM_KABUTO
endc

RuinsOfAlphKabutoItemRoom_MapScripts:
	def_scene_scripts

	def_callbacks
if DEF(_CRYSTALLEGENDS)
	callback MAPCALLBACK_OBJECTS, RuinsOfAlphKabutoItemRoomKabutoCallback
endc

if DEF(_CRYSTALLEGENDS)
RuinsOfAlphKabutoItemRoomKabutoCallback:
	checkevent EVENT_GOT_KABUTO_FROM_ALPH
	iftrue .Hide
	checkevent EVENT_SOLVED_KABUTO_PUZZLE
	iffalse .Hide
	checkevent EVENT_WALL_OPENED_IN_KABUTO_CHAMBER
	iffalse .Hide
	appear RUINSOFALPHKABUTOITEMROOM_KABUTO
	endcallback

.Hide:
	disappear RUINSOFALPHKABUTOITEMROOM_KABUTO
	endcallback

RuinsOfAlphKabutoItemRoomKabutoScript:
	faceplayer
	opentext
	cry KABUTO
	writetext RuinsOfAlphKabutoItemRoomKabutoOfferText
	yesorno
	iffalse .Declined
	givepoke KABUTO, 10
	ifequal 2, .StorageFull
	setevent EVENT_GOT_KABUTO_FROM_ALPH
	writetext RuinsOfAlphKabutoItemRoomKabutoJoinedText
	playsound SFX_CAUGHT_MON
	waitsfx
	waitbutton
	closetext
	disappear RUINSOFALPHKABUTOITEMROOM_KABUTO
	end

.Declined:
	writetext RuinsOfAlphKabutoItemRoomKabutoWaitText
	sjump .Wait

.StorageFull:
	writetext RuinsOfAlphKabutoItemRoomKabutoStorageFullText
	promptbutton
	writetext RuinsOfAlphKabutoItemRoomKabutoWaitText
.Wait:
	waitbutton
	closetext
	end
endc

RuinsOfAlphKabutoItemRoomBerry:
	itemball BERRY

RuinsOfAlphKabutoItemRoomPsncureberry:
	itemball PSNCUREBERRY

RuinsOfAlphKabutoItemRoomHealPowder:
	itemball HEAL_POWDER

RuinsOfAlphKabutoItemRoomEnergypowder:
	itemball ENERGYPOWDER

RuinsOfAlphKabutoItemRoomAncientReplica:
	jumptext RuinsOfAlphKabutoItemRoomAncientReplicaText

RuinsOfAlphKabutoItemRoomAncientReplicaText:
	text "It's a replica of"
	line "an ancient #-"
	cont "MON."
	done

if DEF(_CRYSTALLEGENDS)
RuinsOfAlphKabutoItemRoomKabutoOfferText:
	text "The completed"
	line "picture awakened"
	cont "KABUTO!"

	para "KABUTO wants to"
	line "join you."
	done

RuinsOfAlphKabutoItemRoomKabutoJoinedText:
	text "KABUTO joined"
	line "you!"
	done

RuinsOfAlphKabutoItemRoomKabutoWaitText:
	text "KABUTO will wait"
	line "in this hidden"
	cont "room."
	done

RuinsOfAlphKabutoItemRoomKabutoStorageFullText:
	text "Your party and"
	line "Box are both full!"
	done
endc

RuinsOfAlphKabutoItemRoom_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event  3,  9, RUINS_OF_ALPH_KABUTO_CHAMBER, 5
	warp_event  4,  9, RUINS_OF_ALPH_KABUTO_CHAMBER, 5
	warp_event  3,  1, RUINS_OF_ALPH_KABUTO_WORD_ROOM, 1
	warp_event  4,  1, RUINS_OF_ALPH_KABUTO_WORD_ROOM, 2

	def_coord_events

	def_bg_events
	bg_event  2,  1, BGEVENT_READ, RuinsOfAlphKabutoItemRoomAncientReplica
	bg_event  5,  1, BGEVENT_READ, RuinsOfAlphKabutoItemRoomAncientReplica

	def_object_events
	object_event  2,  6, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, RuinsOfAlphKabutoItemRoomBerry, EVENT_PICKED_UP_BERRY_FROM_KABUTO_ITEM_ROOM
	object_event  5,  6, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, RuinsOfAlphKabutoItemRoomPsncureberry, EVENT_PICKED_UP_PSNCUREBERRY_FROM_KABUTO_ITEM_ROOM
	object_event  2,  4, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, RuinsOfAlphKabutoItemRoomHealPowder, EVENT_PICKED_UP_HEAL_POWDER_FROM_KABUTO_ITEM_ROOM
	object_event  5,  4, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, RuinsOfAlphKabutoItemRoomEnergypowder, EVENT_PICKED_UP_ENERGYPOWDER_FROM_KABUTO_ITEM_ROOM
if DEF(_CRYSTALLEGENDS)
	object_event  3,  3, SPRITE_KABUTO, SPRITEMOVEDATA_POKEMON, 0, 0, -1, -1, PAL_NPC_BROWN, OBJECTTYPE_SCRIPT, 0, RuinsOfAlphKabutoItemRoomKabutoScript, -1
endc
