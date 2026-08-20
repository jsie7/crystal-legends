SECTION "NULL", ROM0
NULL::

INCLUDE "home/header.asm"

SECTION "Home", ROM0

INCLUDE "home/init.asm"
INCLUDE "home/vblank.asm"
INCLUDE "home/delay.asm"
INCLUDE "home/time_palettes.asm"
INCLUDE "home/fade.asm"
INCLUDE "home/lcd.asm"
INCLUDE "home/time.asm"
INCLUDE "home/serial.asm"
INCLUDE "home/joypad.asm"
INCLUDE "home/decompress.asm"
INCLUDE "home/palettes.asm"
INCLUDE "home/gfx.asm"
INCLUDE "home/text.asm"
INCLUDE "home/video.asm"
INCLUDE "home/map_objects.asm"
INCLUDE "home/sine.asm"
INCLUDE "home/movement.asm"
INCLUDE "home/menu.asm"
INCLUDE "home/printer.asm"
INCLUDE "home/game_time.asm"
INCLUDE "home/map.asm"
INCLUDE "home/farcall.asm"
INCLUDE "home/predef.asm"
INCLUDE "home/window.asm"
INCLUDE "home/flag.asm"
INCLUDE "home/sprite_updates.asm"
INCLUDE "home/string.asm"
INCLUDE "home/region.asm"
INCLUDE "home/item.asm"
INCLUDE "home/random.asm"
INCLUDE "home/sram.asm"
INCLUDE "home/call_regs.asm"
INCLUDE "home/double_speed.asm"
INCLUDE "home/clear_sprites.asm"
INCLUDE "home/copy.asm"
INCLUDE "home/copy_tilemap.asm"
INCLUDE "home/copy_name.asm"
INCLUDE "home/array.asm"
INCLUDE "home/math.asm"
INCLUDE "home/print_text.asm"
INCLUDE "home/queue_script.asm"
INCLUDE "home/compare.asm"
INCLUDE "home/tilemap.asm"
INCLUDE "home/pokedex_flags.asm"
INCLUDE "home/names.asm"
INCLUDE "home/scrolling_menu.asm"
INCLUDE "home/stone_queue.asm"
INCLUDE "home/trainers.asm"
INCLUDE "home/pokemon.asm"
INCLUDE "home/print_bcd.asm"
INCLUDE "home/battle.asm"
INCLUDE "home/sprite_anims.asm"
INCLUDE "home/audio.asm"
INCLUDE "home/mobile.asm"

if DEF(_CRYSTALLEGENDS)
; Stock treats block $00 as the surrounding-map sentinel. Crystal Legends
; uses it once at Cinnabar's locked block coordinate (3, 2), so accept only
; that in-map coordinate; connected-map and void sentinels stay blocked.
CheckCurrentMapBlockZero:
	and a
	ret nz
	ld a, [wMapWidth]
	cp 4
	jr c, .sentinel
	ld a, d
	and $fe
	cp 3 * 2 + 4
	jr nz, .sentinel
	ld a, e
	and $fe
	cp 2 * 2 + 4
	jr nz, .sentinel
	xor a
	ret

.sentinel:
	pop hl
	jp GetCoordTileCollision.nope
endc
