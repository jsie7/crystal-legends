ElmsLabSilverArcScript:
	opentext
	writetext ElmsLabSilverArrivalText
	waitbutton
	closetext
	applymovement ELMSLAB_SILVER, ElmsLabSilverHandoffMovement
	turnobject ELMSLAB_ELM, LEFT
	scall ElmsLabSilverBufferReturnedBird
	opentext
	writetext ElmsLabSilverReturnsBirdText
	waitbutton
	closetext
	scall ElmsLabSilverBufferReturnedBird
	opentext
	writetext ElmsLabElmReleaseDecisionText
	waitbutton
	closetext
	applymovement ELMSLAB_SILVER, ElmsLabSilverFacesBirdMovement
	turnobject ELMSLAB_ELM, DOWN
	scall ElmsLabSilverBufferReturnedBird
	opentext
	writetext ElmsLabElmSetsBirdFreeText
	waitbutton
	closetext
	scall ElmsLabSilverCryReturnedBird
	applymovement ELMSLAB_SILVERS_BIRD, ElmsLabSilverBirdExitMovement
	disappear ELMSLAB_SILVERS_BIRD
	scall ElmsLabSilverSetAvailability
	setevent EVENT_SILVER_BIRD_RELEASED
	turnobject ELMSLAB_SILVER, DOWN
	scall ElmsLabSilverBufferReturnedBird
	opentext
	writetext ElmsLabSilverFarewellText
	waitbutton
	closetext
	applymovement ELMSLAB_SILVER, ElmsLabSilverExitMovement
	disappear ELMSLAB_SILVER
	setscene SCENE_ELMSLAB_NOOP
	end

ElmsLabSilverBufferReturnedBird:
	checkevent EVENT_GOT_ZAPDOS_FROM_ELM
	iftrue .Articuno
	checkevent EVENT_GOT_MOLTRES_FROM_ELM
	iftrue .Zapdos
	getmonname STRING_BUFFER_3, MOLTRES
	end

.Articuno:
	getmonname STRING_BUFFER_3, ARTICUNO
	end

.Zapdos:
	getmonname STRING_BUFFER_3, ZAPDOS
	end

ElmsLabSilverCryReturnedBird:
	checkevent EVENT_GOT_ZAPDOS_FROM_ELM
	iftrue .Articuno
	checkevent EVENT_GOT_MOLTRES_FROM_ELM
	iftrue .Zapdos
	cry MOLTRES
	end

.Articuno:
	cry ARTICUNO
	end

.Zapdos:
	cry ZAPDOS
	end

ElmsLabSilverSetAvailability:
	checkevent EVENT_GOT_ZAPDOS_FROM_ELM
	iftrue .Articuno
	checkevent EVENT_GOT_MOLTRES_FROM_ELM
	iftrue .Zapdos
	setevent EVENT_MOLTRES_AVAILABLE
	end

.Articuno:
	setevent EVENT_ARTICUNO_AVAILABLE
	end

.Zapdos:
	setevent EVENT_ZAPDOS_AVAILABLE
	end

ElmsLabSilverHandoffMovement:
	step UP
	turn_head RIGHT
	step_end

ElmsLabSilverFacesBirdMovement:
	step DOWN
	turn_head RIGHT
	step_end

ElmsLabSilverBirdExitMovement:
	; Pokemon overworld icons only have one facing. Pause for the backward glance
	; without selecting a nonexistent left-facing frame.
	step_sleep 8
	step_sleep 8
	step_sleep 8
	step_sleep 8
	turn_head DOWN
	step DOWN
	step DOWN
	step DOWN
	step DOWN
	step DOWN
	step DOWN
	step DOWN
	step DOWN
	step_end

ElmsLabSilverExitMovement:
	step RIGHT
	step DOWN
	step DOWN
	step DOWN
	step DOWN
	step DOWN
	step DOWN
	step DOWN
	step DOWN
	step_end

ElmsLabSilverArrivalText:
	text "<RIVAL>: …You"
	line "came."

	para "Good. You should"
	line "see this too."
	done

ElmsLabSilverReturnsBirdText:
	text "<RIVAL>: PROF.ELM…"

	para "I brought"
	line "@"
	text_ram wStringBuffer3
	text " back."

	para "It fought beside"
	line "me because it"
	cont "wanted to."

	para "It never ran."
	line "It gave its all."

	para "That's why I came"
	line "back."

	para "I was the one who"
	line "took it."

	para "Getting stronger"
	line "didn't make that"
	cont "right."
	done

ElmsLabElmReleaseDecisionText:
	text "ELM: …<RIVAL>."

	para "You chose to bring"
	line "@"
	text_ram wStringBuffer3
	text " back."

	para "That matters."

	para "But I won't decide"
	line "@"
	text_ram wStringBuffer3
	text "'s future."

	para "This bird has seen"
	line "more of the world"
	cont "than this LAB."

	para "It should choose"
	line "where it belongs."

	para "I'm setting"
	line "@"
	text_ram wStringBuffer3
	text " free."
	done

ElmsLabElmSetsBirdFreeText:
	text "ELM: Go, @"
	text_ram wStringBuffer3
	text "."

	para "Choose where you"
	line "belong."
	done

ElmsLabSilverFarewellText:
	text "<RIVAL>: …"
	line "@"
	text_ram wStringBuffer3
	text " looked"
	line "back."

	para "Heh. Of course"
	line "it did."

	para "I don't regret"
	line "the battles we"
	cont "fought together."

	para "But this was the"
	line "right thing to do."

	para "I'm moving on with"
	line "my other partners."

	para "We'll get stronger"
	line "our own way."

	para "…See you, <PLAYER>."
	done
