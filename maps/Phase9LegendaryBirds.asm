; The player's starter never appears at a Kanto encounter. In the Articuno
; branches, Silver releases Articuno when the player chose Zapdos, while Oak
; moves Articuno after the Elm handoff when the player chose Moltres.

Phase9RefreshArticunoLocation:
	checkevent EVENT_CAUGHT_ARTICUNO_IN_KANTO
	iftrue .Hide
	checkevent EVENT_GOT_ARTICUNO_FROM_ELM
	iftrue .Hide
	checkevent EVENT_GOT_ZAPDOS_FROM_ELM
	iftrue .SilverSource
	checkevent EVENT_GOT_MOLTRES_FROM_ELM
	iffalse .Hide
	checkevent EVENT_OAK_MOVED_THIRD_BIRD
	iftrue .Show
	sjump .Hide

.SilverSource:
	checkevent EVENT_ARTICUNO_AVAILABLE
	iffalse .Hide

.Show:
	clearevent EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION
	endcallback

.Hide:
	setevent EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION
	endcallback

Phase9ArticunoEncounter:
	faceplayer
	cry ARTICUNO
	opentext
	farwritetext Phase9ArticunoEncounterText
	waitbutton
	closetext
	loadwildmon ARTICUNO, 60
	startbattle
	special CheckCaughtPokemon
	iffalse .NotCaught
	setevent EVENT_CAUGHT_ARTICUNO_IN_KANTO
	setevent EVENT_ARTICUNO_NOT_AT_KANTO_LOCATION
	disappear SEAFOAMISLANDSCAVE_ARTICUNO
.NotCaught:
	reloadmapafterbattle
	end

Phase9LegendaryBirdsEnd:
