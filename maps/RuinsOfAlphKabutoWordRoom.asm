	object_const_def
if DEF(_CRYSTALLEGENDS)
	const RUINSOFALPHKABUTOWORDROOM_KABUTO
endc

RuinsOfAlphKabutoWordRoom_MapScripts:
	def_scene_scripts

	def_callbacks
if DEF(_CRYSTALLEGENDS)
	callback MAPCALLBACK_OBJECTS, RuinsOfAlphKabutoWordRoomKabutoCallback
endc

if DEF(_CRYSTALLEGENDS)
RuinsOfAlphKabutoWordRoomKabutoCallback:
	checkevent EVENT_GOT_KABUTO_FROM_ALPH
	iftrue .Hide
	checkevent EVENT_SOLVED_KABUTO_PUZZLE
	iffalse .Hide
	checkevent EVENT_WALL_OPENED_IN_KABUTO_CHAMBER
	iffalse .Hide
	loadmem wMap1ObjectSprite + (RUINSOFALPHKABUTOWORDROOM_KABUTO - 2) * MAPOBJECT_LENGTH, SPRITE_KABUTO
	endcallback

.Hide:
	loadmem wMap1ObjectSprite + (RUINSOFALPHKABUTOWORDROOM_KABUTO - 2) * MAPOBJECT_LENGTH, 0
	endcallback

RuinsOfAlphKabutoWordRoomKabutoScript:
	checkevent EVENT_GOT_KABUTO_FROM_ALPH
	iftrue .Done
	checkevent EVENT_SOLVED_KABUTO_PUZZLE
	iffalse .Done
	checkevent EVENT_WALL_OPENED_IN_KABUTO_CHAMBER
	iffalse .Done
	faceplayer
	opentext
	cry KABUTO
	writetext RuinsOfAlphKabutoWordRoomKabutoOfferText
	yesorno
	iffalse .Declined
	givepoke KABUTO, 10
	ifequal 2, .StorageFull
	setevent EVENT_GOT_KABUTO_FROM_ALPH
	writetext RuinsOfAlphKabutoWordRoomKabutoJoinedText
	playsound SFX_CAUGHT_MON
	waitsfx
	waitbutton
	closetext
	disappear RUINSOFALPHKABUTOWORDROOM_KABUTO
	end

.Declined:
	writetext RuinsOfAlphKabutoWordRoomKabutoWaitText
	sjump .Wait

.StorageFull:
	writetext RuinsOfAlphKabutoWordRoomKabutoStorageFullText
	promptbutton
	writetext RuinsOfAlphKabutoWordRoomKabutoWaitText
.Wait:
	waitbutton
	closetext
.Done:
	end

RuinsOfAlphKabutoWordRoomKabutoOfferText:
	text "The completed"
	line "picture awakened"
	cont "KABUTO!"

	para "KABUTO wants to"
	line "join you."
	done

RuinsOfAlphKabutoWordRoomKabutoJoinedText:
	text "KABUTO joined"
	line "you!"
	done

RuinsOfAlphKabutoWordRoomKabutoWaitText:
	text "KABUTO will wait"
	line "in this hidden"
	cont "room."
	done

RuinsOfAlphKabutoWordRoomKabutoStorageFullText:
	text "Your party and"
	line "Box are both full!"
	done
endc

RuinsOfAlphKabutoWordRoom_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event  9,  5, RUINS_OF_ALPH_KABUTO_ITEM_ROOM, 3
	warp_event 10,  5, RUINS_OF_ALPH_KABUTO_ITEM_ROOM, 4
	warp_event 17, 11, RUINS_OF_ALPH_INNER_CHAMBER, 4

	def_coord_events

	def_bg_events

	def_object_events
if DEF(_CRYSTALLEGENDS)
	object_event 10,  8, SPRITE_KABUTO, SPRITEMOVEDATA_POKEMON, 0, 0, -1, -1, PAL_NPC_BROWN, OBJECTTYPE_SCRIPT, 0, RuinsOfAlphKabutoWordRoomKabutoScript, EVENT_GOT_KABUTO_FROM_ALPH
endc
