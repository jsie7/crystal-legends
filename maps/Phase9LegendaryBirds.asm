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

; Zapdos belongs to Oak when the player chose Articuno, and to Silver when
; the player chose Moltres. The repaired Power Plant is required either way.
Phase9RefreshZapdosLocation:
	checkevent EVENT_CAUGHT_ZAPDOS_IN_KANTO
	iftrue .Hide
	checkevent EVENT_RESTORED_POWER_TO_KANTO
	iffalse .Hide
	checkevent EVENT_GOT_ZAPDOS_FROM_ELM
	iftrue .Hide
	checkevent EVENT_GOT_MOLTRES_FROM_ELM
	iftrue .SilverSource
	checkevent EVENT_GOT_ARTICUNO_FROM_ELM
	iffalse .Hide
	checkevent EVENT_OAK_MOVED_THIRD_BIRD
	iftrue .Show
	sjump .Hide

.SilverSource:
	checkevent EVENT_ZAPDOS_AVAILABLE
	iffalse .Hide

.Show:
	clearevent EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION
	endcallback

.Hide:
	setevent EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION
	endcallback

; Moltres belongs to Oak when the player chose Zapdos, and to Silver when
; the player chose Articuno. Both sources wait until the first Hall of Fame.
Phase9RefreshMoltresLocation:
	checkevent EVENT_CAUGHT_MOLTRES_IN_KANTO
	iftrue .Hide
	checkevent EVENT_BEAT_ELITE_FOUR
	iffalse .Hide
	checkevent EVENT_GOT_MOLTRES_FROM_ELM
	iftrue .Hide
	checkevent EVENT_GOT_ARTICUNO_FROM_ELM
	iftrue .SilverSource
	checkevent EVENT_GOT_ZAPDOS_FROM_ELM
	iffalse .Hide
	checkevent EVENT_OAK_MOVED_THIRD_BIRD
	iftrue .Show
	sjump .Hide

.SilverSource:
	checkevent EVENT_MOLTRES_AVAILABLE
	iffalse .Hide

.Show:
	clearevent EVENT_MOLTRES_NOT_AT_KANTO_LOCATION
	endcallback

.Hide:
	setevent EVENT_MOLTRES_NOT_AT_KANTO_LOCATION
	endcallback

Phase9ArticunoEncounter:
	faceplayer
	cry ARTICUNO
	opentext
	farwritetext Phase9ArticunoEncounterText
	waitbutton
	closetext
	loadvar VAR_BATTLETYPE, BATTLETYPE_KANTO_BIRD
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

Phase9ZapdosEncounter:
	faceplayer
	cry ZAPDOS
	opentext
	farwritetext Phase9ZapdosEncounterText
	waitbutton
	closetext
	loadvar VAR_BATTLETYPE, BATTLETYPE_KANTO_BIRD
	loadwildmon ZAPDOS, 60
	startbattle
	special CheckCaughtPokemon
	iffalse .NotCaught
	setevent EVENT_CAUGHT_ZAPDOS_IN_KANTO
	setevent EVENT_ZAPDOS_NOT_AT_KANTO_LOCATION
	disappear POWERPLANTGENERATORANNEX_ZAPDOS
.NotCaught:
	reloadmapafterbattle
	end

Phase9MoltresEncounter:
	faceplayer
	cry MOLTRES
	opentext
	farwritetext Phase9MoltresEncounterText
	waitbutton
	closetext
	loadvar VAR_BATTLETYPE, BATTLETYPE_KANTO_BIRD
	loadwildmon MOLTRES, 60
	startbattle
	special CheckCaughtPokemon
	iffalse .NotCaught
	setevent EVENT_CAUGHT_MOLTRES_IN_KANTO
	setevent EVENT_MOLTRES_NOT_AT_KANTO_LOCATION
	disappear VICTORYROAD_MOLTRES
.NotCaught:
	reloadmapafterbattle
	end

Phase9OaksAssistant2Hints:
	faceplayer
	opentext
	checkevent EVENT_GOT_ARTICUNO_FROM_ELM
	iftrue .ArticunoStarter
	checkevent EVENT_GOT_ZAPDOS_FROM_ELM
	iftrue .ZapdosStarter
	sjump .MoltresStarter

.ArticunoStarter:
	checkevent EVENT_CAUGHT_ZAPDOS_IN_KANTO
	iffalse .ArticunoOakUncaught
	checkevent EVENT_CAUGHT_MOLTRES_IN_KANTO
	iftrue .BothCaught
	checkevent EVENT_MOLTRES_AVAILABLE
	iffalse .NoNewSighting
	scall Phase9OaksAssistantMoltresHint
	sjump .Finish

.ArticunoOakUncaught:
	scall Phase9OaksAssistantZapdosHint
	checkevent EVENT_CAUGHT_MOLTRES_IN_KANTO
	iftrue .Finish
	checkevent EVENT_MOLTRES_AVAILABLE
	iffalse .Finish
	promptbutton
	scall Phase9OaksAssistantMoltresHint
	sjump .Finish

.ZapdosStarter:
	checkevent EVENT_CAUGHT_MOLTRES_IN_KANTO
	iffalse .ZapdosOakUncaught
	checkevent EVENT_CAUGHT_ARTICUNO_IN_KANTO
	iftrue .BothCaught
	checkevent EVENT_ARTICUNO_AVAILABLE
	iffalse .NoNewSighting
	scall Phase9OaksAssistantArticunoHint
	sjump .Finish

.ZapdosOakUncaught:
	scall Phase9OaksAssistantMoltresHint
	checkevent EVENT_CAUGHT_ARTICUNO_IN_KANTO
	iftrue .Finish
	checkevent EVENT_ARTICUNO_AVAILABLE
	iffalse .Finish
	promptbutton
	scall Phase9OaksAssistantArticunoHint
	sjump .Finish

.MoltresStarter:
	checkevent EVENT_CAUGHT_ARTICUNO_IN_KANTO
	iffalse .MoltresOakUncaught
	checkevent EVENT_CAUGHT_ZAPDOS_IN_KANTO
	iftrue .BothCaught
	checkevent EVENT_ZAPDOS_AVAILABLE
	iffalse .NoNewSighting
	scall Phase9OaksAssistantZapdosHint
	sjump .Finish

.MoltresOakUncaught:
	scall Phase9OaksAssistantArticunoHint
	checkevent EVENT_CAUGHT_ZAPDOS_IN_KANTO
	iftrue .Finish
	checkevent EVENT_ZAPDOS_AVAILABLE
	iffalse .Finish
	promptbutton
	scall Phase9OaksAssistantZapdosHint
	sjump .Finish

.NoNewSighting:
	writetext Phase9OaksAssistantNoNewSightingText
	sjump .Finish

.BothCaught:
	writetext Phase9OaksAssistantBothBirdsCaughtText

.Finish:
	waitbutton
	closetext
	end

Phase9OaksAssistantArticunoHint:
	writetext Phase9OaksAssistantLegendaryHabitatHintText
	return

Phase9OaksAssistantZapdosHint:
	writetext Phase9OaksAssistantLegendaryHabitatHintText
	return

Phase9OaksAssistantMoltresHint:
	writetext Phase9OaksAssistantLegendaryHabitatHintText
	return

Phase9OaksAssistantLegendaryHabitatHintText:
	text "AIDE: Legendary"
	line "birds are drawn to"
	cont "their natural"
	cont "habitat."
	done

Phase9OaksAssistantNoNewSightingText:
	text "AIDE: No new bird"
	line "sightings yet."
	done

Phase9OaksAssistantBothBirdsCaughtText:
	text "AIDE: Excellent!"
	line "You found both of"
	cont "KANTO's lost"
	cont "birds."
	done

Phase9LegendaryBirdsEnd:
