# Custom graphics procedures

Run commands from the repository root. The [build workflow](workflows.md)
provides the shared validation gate; these procedures cover specialized asset
reproduction and placement constraints.

## Regenerate and validate the cave lab fixtures

The three Crystal Legends-only Cave fixtures are block `$03` (empty table,
south-side approach), `$16` (computer workbench, north-side approach), and `$17`
(control terminal, south-side approach). Their source-art reuse and
shared-tileset boundaries are recorded in
[decisions.md](decisions.md#2026-08-26--reuse-unused-cave-blocks-for-three-lab-fixtures).
Phase 10 places them only in Cerulean Cave as paired background records; do not
reuse them on a map that loads Dark Cave graphics.

Regenerate the PNG, metatiles, and palette map deterministically from checked-in
source assets; no Python image library or prebuilt graphics are needed:

```bash
python3 tools/generate_cave_lab_tiles.py
python3 tools/generate_cave_lab_tiles.py --check
make crystallegends crystal11
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_cave_lab_tiles.py tests/rom/test_cave_lab_tiles.py
make compare
git diff --check
```

The static tests preserve all non-furniture block definitions, their referenced
graphics and palettes, animation slots, and existing Cave/Dark Cave map usage.
Only the old grass graphic `$04`, unique to replaced block `$03`, is reclaimed
from a previously referenced slot. The empty table must have no papers or
computer, and its base and cave floor must match the terminal.
Compiled-ROM tests check custom/reference graphics, metatiles, palettes and
collision, including unchanged Dark Cave graphics. They also verify exact
decompression, the 1008-byte compressed size, and the original bank `$07` with
52 bytes free. `gfx/lz.mk` selects optimized compression only for the custom
Cave asset; keep all reference-asset matching rules unchanged. Run the normal
bank-budget gate after further edits; Cave bank `$07` has only `$0034` free.
Do not use the new blocks with Dark Cave graphics or add story interactions
without reviewing their map placement separately.

## Giovanni standing sprite

`gfx/sprites/giovanni.png` contains the three standing poses from
[pret/pokered's Giovanni sprite](https://github.com/pret/pokered/blob/master/gfx/sprites/giovanni.png),
retrieved on 2026-08-26. The upstream 16-by-96 PNG has SHA-256
`2ce3cbbd25c04034ee4b65487c754ae9c5a9528ade605b8b43da77c0207ed058`.
The import preserves its first 48 pixel rows exactly and omits the three
walking poses. RGBGFX uses row-major, non-deduplicated 2bpp tiles; this is not
the column-major trainer-portrait format.

To reproduce the source PNG, first obtain that upstream PNG and verify the
hash above. With its local path substituted for `path/to/pokered-giovanni.png`:

```bash
giovanni_tmp=$(mktemp -d)
rgbgfx --colors dmg --slice 0,0:2,6 -o "$giovanni_tmp/standing.2bpp" path/to/pokered-giovanni.png
rgbgfx --reverse 2 --colors dmg -o "$giovanni_tmp/standing.2bpp" gfx/sprites/giovanni.png
make crystallegends crystal11
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_giovanni_sprite.py tests/rom/test_giovanni_sprite.py
make compare
git diff --check
```

RGBGFX's slice dimensions are in 8-by-8 tiles, so `2,6` selects a 16-by-48
sheet. The resulting 192-byte tile stream must have SHA-256
`d06c85addab6141e8949c58c27f39072ce3f9f7aab2e14a9a81542daeb1a3795`.
The PNG is source; `.2bpp`, ROM, `.sym`, `.map`, and preview outputs remain
untracked. The six focused source/ROM tests protect the imported poses,
custom-only ID/table entry, bank/pointer/palette, size, and unchanged stock
sprite banks.

Use `SPRITE_GIOVANNI` with stationary movement such as
`SPRITEMOVEDATA_STANDING_DOWN`, never wandering, trainer approach, or scripted
walking. `faceplayer` may turn him. This follows stock Will/Karen standing
sprites; the stock graphics loader still copies an unused second graphics
region for standing sprites, so changing the movement to walking would display
unrelated data. Do not add a loader change as part of this asset import.
Cerulean Cave now uses the sprite for Giovanni's stationary script object at
`(6, 4)`; his victory blackout removes him without walking choreography.

## Giovanni trainer portrait

The trainer portrait comes from
[pret/pokered's Giovanni portrait](https://github.com/pret/pokered/blob/master/gfx/trainers/giovanni.png).
The adapted 56-by-56 source PNG has SHA-256
`4cf1d940ceeb00e530b361b1a95ea8c31492faf86bb5c20f0ac45c70768b2034`;
its 784-byte column-major 2bpp output has SHA-256
`adbe7da4cb2f5464b425f85def53164dec8f7ba077d7d11e24114dabbb96dfd2`.
The custom LZ stream is 227 bytes. It lives in Pics 18, while Omastar's
custom-only lossless recompression remains 424 bytes and leaves four bytes in
the original trainer-pointer/Pics 3 bank. Source and compiled-ROM tests decode
both assets and compare their pixels.
