	object_const_def
	const RUINSOFALPHAERODACTYLITEMROOM_POKE_BALL1
	const RUINSOFALPHAERODACTYLITEMROOM_POKE_BALL2
	const RUINSOFALPHAERODACTYLITEMROOM_POKE_BALL3
	const RUINSOFALPHAERODACTYLITEMROOM_POKE_BALL4
if DEF(_CRYSTALLEGENDS)
	const RUINSOFALPHAERODACTYLITEMROOM_AERODACTYL
endc

RuinsOfAlphAerodactylItemRoom_MapScripts:
	def_scene_scripts

	def_callbacks
if DEF(_CRYSTALLEGENDS)
	callback MAPCALLBACK_OBJECTS, RuinsOfAlphAerodactylItemRoomAerodactylCallback
endc

if DEF(_CRYSTALLEGENDS)
RuinsOfAlphAerodactylItemRoomAerodactylCallback:
	checkevent EVENT_GOT_AERODACTYL_FROM_ALPH
	iftrue .Hide
	checkevent EVENT_SOLVED_AERODACTYL_PUZZLE
	iffalse .Hide
	checkevent EVENT_WALL_OPENED_IN_AERODACTYL_CHAMBER
	iffalse .Hide
	appear RUINSOFALPHAERODACTYLITEMROOM_AERODACTYL
	endcallback

.Hide:
	disappear RUINSOFALPHAERODACTYLITEMROOM_AERODACTYL
	endcallback

RuinsOfAlphAerodactylItemRoomAerodactylScript:
	faceplayer
	opentext
	cry AERODACTYL
	writetext RuinsOfAlphAerodactylItemRoomAerodactylOfferText
	yesorno
	iffalse .Declined
	givepoke AERODACTYL, 23
	ifequal 2, .StorageFull
	setevent EVENT_GOT_AERODACTYL_FROM_ALPH
	writetext RuinsOfAlphAerodactylItemRoomAerodactylJoinedText
	playsound SFX_CAUGHT_MON
	waitsfx
	waitbutton
	closetext
	disappear RUINSOFALPHAERODACTYLITEMROOM_AERODACTYL
	end

.Declined:
	writetext RuinsOfAlphAerodactylItemRoomAerodactylWaitText
	sjump .Wait

.StorageFull:
	writetext RuinsOfAlphAerodactylItemRoomAerodactylStorageFullText
	promptbutton
	writetext RuinsOfAlphAerodactylItemRoomAerodactylWaitText
.Wait:
	waitbutton
	closetext
	end
endc

RuinsOfAlphAerodactylItemRoomGoldBerry:
	itemball GOLD_BERRY

RuinsOfAlphAerodactylItemRoomMoonStone:
	itemball MOON_STONE

RuinsOfAlphAerodactylItemRoomHealPowder:
	itemball HEAL_POWDER

RuinsOfAlphAerodactylItemRoomEnergyRoot:
	itemball ENERGY_ROOT

RuinsOfAlphAerodactylItemRoomAncientReplica:
	jumptext RuinsOfAlphAerodactylItemRoomAncientReplicaText

RuinsOfAlphAerodactylItemRoomAncientReplicaText:
	text "It's a replica of"
	line "an ancient #-"
	cont "MON."
	done

if DEF(_CRYSTALLEGENDS)
RuinsOfAlphAerodactylItemRoomAerodactylOfferText:
	text "The completed"
	line "picture awakened"
	cont "AERODACTYL!"

	para "AERODACTYL wants"
	line "to join you."
	done

RuinsOfAlphAerodactylItemRoomAerodactylJoinedText:
	text "AERODACTYL joined"
	line "you!"
	done

RuinsOfAlphAerodactylItemRoomAerodactylWaitText:
	text "AERODACTYL will"
	line "wait in this"
	cont "hidden room."
	done

RuinsOfAlphAerodactylItemRoomAerodactylStorageFullText:
	text "Your party and"
	line "Box are both full!"
	done
endc

RuinsOfAlphAerodactylItemRoom_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event  3,  9, RUINS_OF_ALPH_AERODACTYL_CHAMBER, 5
	warp_event  4,  9, RUINS_OF_ALPH_AERODACTYL_CHAMBER, 5
	warp_event  3,  1, RUINS_OF_ALPH_AERODACTYL_WORD_ROOM, 1
	warp_event  4,  1, RUINS_OF_ALPH_AERODACTYL_WORD_ROOM, 2

	def_coord_events

	def_bg_events
	bg_event  2,  1, BGEVENT_READ, RuinsOfAlphAerodactylItemRoomAncientReplica
	bg_event  5,  1, BGEVENT_READ, RuinsOfAlphAerodactylItemRoomAncientReplica

	def_object_events
	object_event  2,  6, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, RuinsOfAlphAerodactylItemRoomGoldBerry, EVENT_PICKED_UP_GOLD_BERRY_FROM_AERODACTYL_ITEM_ROOM
	object_event  5,  6, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, RuinsOfAlphAerodactylItemRoomMoonStone, EVENT_PICKED_UP_MOON_STONE_FROM_AERODACTYL_ITEM_ROOM
	object_event  2,  4, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, RuinsOfAlphAerodactylItemRoomHealPowder, EVENT_PICKED_UP_HEAL_POWDER_FROM_AERODACTYL_ITEM_ROOM
	object_event  5,  4, SPRITE_POKE_BALL, SPRITEMOVEDATA_STILL, 0, 0, -1, -1, 0, OBJECTTYPE_ITEMBALL, 0, RuinsOfAlphAerodactylItemRoomEnergyRoot, EVENT_PICKED_UP_ENERGY_ROOT_FROM_AERODACTYL_ITEM_ROOM
if DEF(_CRYSTALLEGENDS)
	object_event  3,  3, SPRITE_AERODACTYL, SPRITEMOVEDATA_POKEMON, 0, 0, -1, -1, PAL_NPC_PINK, OBJECTTYPE_SCRIPT, 0, RuinsOfAlphAerodactylItemRoomAerodactylScript, -1
endc
