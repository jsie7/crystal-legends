	object_const_def
if DEF(_CRYSTALLEGENDS)
	const RUINSOFALPHAERODACTYLWORDROOM_AERODACTYL
endc

RuinsOfAlphAerodactylWordRoom_MapScripts:
	def_scene_scripts

	def_callbacks
if DEF(_CRYSTALLEGENDS)
	callback MAPCALLBACK_OBJECTS, RuinsOfAlphAerodactylWordRoomAerodactylCallback
endc

if DEF(_CRYSTALLEGENDS)
RuinsOfAlphAerodactylWordRoomAerodactylCallback:
	checkevent EVENT_GOT_AERODACTYL_FROM_ALPH
	iftrue .Hide
	checkevent EVENT_SOLVED_AERODACTYL_PUZZLE
	iffalse .Hide
	checkevent EVENT_WALL_OPENED_IN_AERODACTYL_CHAMBER
	iffalse .Hide
	appear RUINSOFALPHAERODACTYLWORDROOM_AERODACTYL
	endcallback

.Hide:
	disappear RUINSOFALPHAERODACTYLWORDROOM_AERODACTYL
	endcallback

RuinsOfAlphAerodactylWordRoomAerodactylScript:
	faceplayer
	opentext
	cry AERODACTYL
	writetext RuinsOfAlphAerodactylWordRoomAerodactylOfferText
	yesorno
	iffalse .Declined
	givepoke AERODACTYL, 23
	ifequal 2, .StorageFull
	setevent EVENT_GOT_AERODACTYL_FROM_ALPH
	writetext RuinsOfAlphAerodactylWordRoomAerodactylJoinedText
	playsound SFX_CAUGHT_MON
	waitsfx
	waitbutton
	closetext
	disappear RUINSOFALPHAERODACTYLWORDROOM_AERODACTYL
	end

.Declined:
	writetext RuinsOfAlphAerodactylWordRoomAerodactylWaitText
	sjump .Wait

.StorageFull:
	writetext RuinsOfAlphAerodactylWordRoomAerodactylStorageFullText
	promptbutton
	writetext RuinsOfAlphAerodactylWordRoomAerodactylWaitText
.Wait:
	waitbutton
	closetext
	end

RuinsOfAlphAerodactylWordRoomAerodactylOfferText:
	text "The completed"
	line "picture awakened"
	cont "AERODACTYL!"

	para "AERODACTYL wants"
	line "to join you."
	done

RuinsOfAlphAerodactylWordRoomAerodactylJoinedText:
	text "AERODACTYL joined"
	line "you!"
	done

RuinsOfAlphAerodactylWordRoomAerodactylWaitText:
	text "AERODACTYL will"
	line "wait in this"
	cont "hidden room."
	done

RuinsOfAlphAerodactylWordRoomAerodactylStorageFullText:
	text "Your party and"
	line "Box are both full!"
	done
endc

RuinsOfAlphAerodactylWordRoom_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event  9,  5, RUINS_OF_ALPH_AERODACTYL_ITEM_ROOM, 3
	warp_event 10,  5, RUINS_OF_ALPH_AERODACTYL_ITEM_ROOM, 4
	warp_event 17, 11, RUINS_OF_ALPH_INNER_CHAMBER, 8

	def_coord_events

	def_bg_events

	def_object_events
if DEF(_CRYSTALLEGENDS)
	object_event 16,  8, SPRITE_AERODACTYL, SPRITEMOVEDATA_POKEMON, 0, 0, -1, -1, PAL_NPC_PINK, OBJECTTYPE_SCRIPT, 0, RuinsOfAlphAerodactylWordRoomAerodactylScript, -1
endc
