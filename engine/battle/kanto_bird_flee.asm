CheckKantoBirdEnemyFlee:
; Return carry when TryEnemyFlee should take its stock stay path. The call site
; replaces six stock bytes with six custom bytes so every later Battle Core
; routine and flee-table address remains stable.
	ld a, [wBattleMode]
	dec a
	jr nz, .stay
	ld a, [wBattleType]
	cp BATTLETYPE_KANTO_BIRD
	jr z, .stay
	and a
	ret

.stay:
	scf
	ret
