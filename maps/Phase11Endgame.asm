DEF OAK_CHALLENGE_CAUGHT_REQUIREMENT EQU 240

Phase11OakEndgameScript:
	checkevent EVENT_BEAT_PROFESSOR_OAK
	iftrue .Complete
	writetext OakLabDexCheckText
	waitbutton
	special ProfOaksPCBoot
	readvar VAR_DEXCAUGHT
	ifless OAK_CHALLENGE_CAUGHT_REQUIREMENT, .BelowRequirement
	checkevent EVENT_BEAT_RED
	iffalse .ReadyBeforeRed

	writetext Phase11OakChallengeText
	yesorno
	iffalse .Declined
	checkevent EVENT_GOT_ARTICUNO_FROM_ELM
	iftrue .ArticunoPlayer
	checkevent EVENT_GOT_ZAPDOS_FROM_ELM
	iftrue .ZapdosPlayer
	checkevent EVENT_GOT_MOLTRES_FROM_ELM
	iftrue .MoltresPlayer
	writetext Phase11OakInvalidStarterText
	waitbutton
	closetext
	end

.ArticunoPlayer:
	loadtrainer POKEMON_PROF, OAK_ARTICUNO_PLAYER
	sjump .BeginBattle

.ZapdosPlayer:
	loadtrainer POKEMON_PROF, OAK_ZAPDOS_PLAYER
	sjump .BeginBattle

.MoltresPlayer:
	loadtrainer POKEMON_PROF, OAK_MOLTRES_PLAYER

.BeginBattle:
	writetext Phase11OakBattleStartText
	waitbutton
	closetext
	winlosstext Phase11OakWinText, Phase11OakLossText
	startbattle
	reloadmapafterbattle
	faceplayer
	opentext
	setevent EVENT_BEAT_PROFESSOR_OAK
	writetext Phase11OakCompletionText
	waitbutton
	closetext
	special HealParty
	reanchormap
	callasm Phase11PrepareOakCredits
	credits
	end

.BelowRequirement:
	checkevent EVENT_BEAT_RED
	iffalse .OrdinaryGoodbye
	writetext Phase11OakNeedsResearchText
	waitbutton
	closetext
	end

.OrdinaryGoodbye:
	writetext OakLabGoodbyeText
	waitbutton
	closetext
	end

.ReadyBeforeRed:
	writetext Phase11OakNeedsRedText
	waitbutton
	closetext
	end

.Declined:
	writetext Phase11OakDeclinedText
	waitbutton
	closetext
	end

.Complete:
	writetext Phase11OakCompleteText
	waitbutton
	closetext
	end

Phase11OakNeedsRedText:
	text "OAK: Remarkable!"
	line "You've recorded"

	para "at least 240"
	line "kinds of #MON."

	para "That dedication"
	line "is extraordinary."

	para "But one trainer"
	line "still waits atop"
	cont "MT.SILVER."

	para "Face RED, then"
	line "return to me."
	done

Phase11OakNeedsResearchText:
	text "OAK: Your victory"
	line "on MT.SILVER was"
	cont "extraordinary!"

	para "Now finish the"
	line "work we began."

	para "Record at least"
	line "240 kinds of"
	cont "#MON."
	done

Phase11OakChallengeText:
	text "OAK: The #DEX"
	line "began as a dream"
	cont "of mine."

	para "You did more than"
	line "record 240 kinds."

	para "You learned to"
	line "care for #MON"
	cont "and battle beside"
	cont "them."

	para "There is one last"
	line "test I can offer."

	para "Will you accept"
	line "my challenge?"
	done

Phase11OakDeclinedText:
	text "Preparation is"
	line "part of mastery."

	para "Return when you"
	line "are ready."
	done

Phase11OakInvalidStarterText:
	text "OAK: Something is"
	line "missing from our"
	cont "first adventure."

	para "I can't begin the"
	line "challenge yet."
	done

Phase11OakBattleStartText:
	text "OAK: Show me what"
	line "your journey has"
	cont "taught you!"
	done

Phase11OakWinText:
	text "OAK: Splendid!"

	para "You surpassed my"
	line "final test."
	done

Phase11OakLossText:
	text "OAK: Knowledge"
	line "grows through"
	cont "every defeat."

	para "Return when you"
	line "are ready."
	done

Phase11OakCompletionText:
	text "OAK: I remember"
	line "when I first asked"

	para "you to complete"
	line "the #DEX."

	para "You crossed two"
	line "regions and stood"
	cont "against TEAM"
	cont "ROCKET."

	para "Recording nearly"
	line "every known"
	cont "#MON was only"
	cont "part of it."

	para "You defeated the"
	line "strongest trainers"

	para "and learned from"
	line "so many #MON."

	para "You have become a"
	line "true #MON"
	cont "MASTER."

	para "This is your"
	line "legend, <PLAYER>."
	done

Phase11OakCompleteText:
	text "OAK: Our #DEX"
	line "work can continue."

	para "Discovery never"
	line "ends."

	para "I'm proud of all"
	line "you accomplished."
	done
