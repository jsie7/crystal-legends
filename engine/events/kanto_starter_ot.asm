SetErikaStarterOT:
	ld de, ErikaStarterOTName
	ld bc, (ERIKA << 8) | ERIKA1
	jr SetLatestStarterOT

SetMistyStarterOT:
	ld de, MistyStarterOTName
	ld bc, (MISTY << 8) | MISTY1
	jr SetLatestStarterOT

SetBlaineStarterOT:
	ld de, BlaineStarterOTName
	ld bc, (BLAINE << 8) | BLAINE1

SetLatestStarterOT:
; givepoke leaves 0 in wScriptVar for a party delivery and 1 for a box
; delivery. Rewrite only the mon it just inserted, retaining its generated
; moves, nickname, caught data, and normal full-storage transaction.
	push bc
	ld a, [wScriptVar]
	and a
	jr nz, .box

	ld a, [wPartyCount]
	dec a
	ld hl, wPartyMonOTs
	call SkipNames
	call CopyName2
	ld a, [wPartyCount]
	dec a
	ld hl, wPartyMon1ID
	ld bc, PARTYMON_STRUCT_LENGTH
	call AddNTimes
	pop bc
	ld a, b
	ld [hli], a
	ld [hl], c
	ret

.box:
	ld a, BANK(sBoxMonOTs)
	call OpenSRAM
	ld hl, sBoxMonOTs
	call CopyName2
	pop bc
	ld hl, sBoxMon1ID
	ld a, b
	ld [hli], a
	ld [hl], c
	call CloseSRAM
	ret

ErikaStarterOTName:
	db "ERIKA@"

MistyStarterOTName:
	db "MISTY@"

BlaineStarterOTName:
	db "BLAINE@"
