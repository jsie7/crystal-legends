# Custom graphics procedures

Run commands from the repository root. Use the [build workflow](workflows.md)
for shared validation and [decisions](decisions.md) for design rationale.

- [Cave fixture constraints](#cave-fixture-design-constraints) and [regeneration](#regenerate-and-validate-the-cave-lab-fixtures)
- [Giovanni sprite import](#giovanni-standing-sprite) and [registration](#giovanni-sprite-registration)
- [Giovanni portrait](#giovanni-trainer-portrait)
- [Kanto map art](#kanto-map-art)

## Cave fixture design constraints

Crystal Legends reserves Cave block `$03` for an empty Facility-style table,
`$16` for the computer workbench from Lab block `$21`, and `$17` for the
Facility `$08` control terminal. The empty table uses Facility `$29` with its
two paper tiles replaced by the plain tabletop graphic `$51`. Approach from
the north for the bench, and from the south for the table and terminal. Exposed
floor tiles use the raised cave ground. Phase 10 uses these fixtures for paired
lab-record interactions in Cerulean Cave.

Reuse 32 8-by-8 graphic slots without increasing the 96-tile graphics sheet or
64-block table. Of these, 31 were unreferenced by every original block; graphic
`$04` is reclaimed from the retired grass block `$03`. The other blocks, their
graphics, collision, and palettes remain unchanged. Cave and Dark Cave share
block/collision/palette tables, so tests prohibit all three reserved blocks in
their existing maps; the new furniture is intended for Cave graphics, not Dark
Cave. Reference builds continue to use all original assets and collision rows.

The terminal's whole bottom tile row uses cave ground, replacing both the
Facility patterned-floor tile `$01` and its blank-floor tile `$26`.

Keep the fixtures' graphic allocations stable. Reclaiming the grass graphic and
selecting the existing compressor's optimized mode only for
`cave_crystallegends.2bpp.lz` keeps the three-fixture graphics at the same 1008
bytes as the two-fixture version. Original assets retain matching compression.
Do not delete block `$3f`: it is Victory Road's pit block and has no unique
graphics to reclaim.

The custom compressed graphics occupy 1008 bytes versus the original 912,
leaving `$0034` (52) bytes free in ROMX bank `$07`. Keep a reviewed `$0030`
floor there; further growth requires a separate capacity review. No bank
relocation, new tileset ID, map size, object slot, event flag, or save-layout
field is needed.

## Regenerate and validate the cave lab fixtures

Regenerate the PNG, metatiles, and palette map from checked-in source assets;
no Python image library or prebuilt graphics are needed. Follow the
[design constraints](#cave-fixture-design-constraints) for placement and
capacity.

```bash
python3 tools/generate_cave_lab_tiles.py
python3 tools/generate_cave_lab_tiles.py --check
make crystallegends crystal11
UV_CACHE_DIR=.uv-cache uv run --frozen --group test pytest tests/static/test_cave_lab_tiles.py tests/rom/test_cave_lab_tiles.py
make compare
git diff --check
```

Static checks preserve non-furniture block definitions, referenced graphics and
palettes, animation slots, and existing Cave/Dark Cave map usage. The empty
table must have no papers or computer, and its base and cave floor must match
the terminal. Compiled-ROM checks compare custom/reference graphics, metatiles,
palettes and collision, exact decompression, and the guarded bank reserve.
Review map placement separately when adding story interactions.

## Giovanni standing sprite

`gfx/sprites/giovanni.png` contains the three standing poses from
[pret/pokered's Giovanni sprite](https://github.com/pret/pokered/blob/master/gfx/sprites/giovanni.png), retrieved on 2026-08-26. The upstream 16-by-96 PNG has SHA-256
`2ce3cbbd25c04034ee4b65487c754ae9c5a9528ade605b8b43da77c0207ed058`. The import
preserves its first 48 pixel rows exactly and omits the three walking poses.
RGBGFX uses row-major, non-deduplicated 2bpp tiles; this is not the
column-major trainer-portrait format.

To reproduce the source PNG, first obtain that upstream PNG and verify the hash
above. With its local path substituted for `path/to/pokered-giovanni.png`:

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
`d06c85addab6141e8949c58c27f39072ce3f9f7aab2e14a9a81542daeb1a3795`. The PNG is
source; `.2bpp`, ROM, `.sym`, `.map`, and preview outputs remain untracked.
The six focused source/ROM tests protect the imported poses, custom-only
ID/table entry, bank/pointer/palette, size, and unchanged stock sprite banks.

Follow the
[registration and movement constraints](#giovanni-sprite-registration) when
placing Giovanni.

## Giovanni sprite registration

Crystal Legends appends `SPRITE_GIOVANNI` at ordinary sprite ID `$67`, leaving
all existing IDs and the `$80` Pokémon-icon range unchanged. Import Red's three
standing 16-by-16 poses without redrawing pixels: down, up, and left, with the
engine mirroring left for right. The source PNG is 16-by-48; its 12 native 2bpp
tiles occupy 192 bytes. Use `STANDING_SPRITE` and `PAL_OW_BROWN`.

Use stationary movement such as `SPRITEMOVEDATA_STANDING_DOWN`; `faceplayer`
may turn him. Never use wandering, scripted walking, or automatic trainer
approach. Like stock Will/Karen, the standing loader copies an unused second
graphics region; walking would display unrelated data. Keep the loader
unchanged. The post-victory blackout removes the crew without walking
choreography.

Place the custom-only bytes in `Crystal Legends Sprites`, after `Map Blocks 3`
in bank `$2c`. The section is empty in reference builds. Both original sprite
banks remain unchanged; the custom bank retains `$23da` (9178) free bytes and
its existing `$2000` minimum reserve. No bank relocation, ROM expansion, engine
change, or save-layout change is required. Cerulean Cave places Giovanni at
`(6, 4)`, facing down.

## Giovanni trainer portrait

The trainer portrait comes from
[pret/pokered's Giovanni portrait](https://github.com/pret/pokered/blob/master/gfx/trainers/giovanni.png). The adapted 56-by-56 source PNG has SHA-256
`4cf1d940ceeb00e530b361b1a95ea8c31492faf86bb5c20f0ac45c70768b2034`; its
784-byte column-major 2bpp output has SHA-256
`adbe7da4cb2f5464b425f85def53164dec8f7ba077d7d11e24114dabbb96dfd2`. The custom
LZ stream is 227 bytes. It lives in Pics 18 (bank `$59`), while Omastar's
custom-only lossless recompression remains 424 bytes and leaves four bytes in
the original trainer-pointer/Pics 3 bank. This frees the three pointer bytes
without relocating Omastar's back picture. Source and compiled-ROM tests decode
both assets and compare their pixels.

## Kanto map art

### Cinnabar cache and staircase

The hidden cache uses the stock boulder graphic at `(17, 12)` in the Crystal
Legends-only Cinnabar object list; three noninteractive boulders at `(12, 6)`,
`(17, 1)`, and `(12, 2)` make it part of the surrounding rubble. Its gray
shelf staircase uses a custom block, metatile, collision, and one imported
stair-tread tile; reference assets remain exact. The staircase uses nonzero
Kanto metatile `$4b` because block `$00` is a rendering and collision sentinel,
not a usable map block.

### Safari preserve

The compact northern preserve uses denser grass, an eight-by-six-tile pond
framed by the National Park stone shore, and one additional tree barrier. A
Crystal Legends-only Park graphic duplicates that shore into a gray-palette
tile so it does not render with the orange roof palette. Its two notices flank
the two-tile south exit, whose carpet is limited to the actual warp tiles.

### Seafoam and Generator Annex

The Seafoam cave uses a visible south exit and several connected ice lanes.
Rock stops frame the entrance, separate the eastern ice field from Articuno,
and turn the route to the bird into a short sliding puzzle. An exposed Ultra
Ball rewards the western branch, while a hidden NeverMeltIce sits in the
northeast ice rock.

Both tiles of the annex's two-tile generator console share one reading. It
reports unsafe output only while Zapdos is physically present and safe output
whenever the location selector hides it, including capture and the
Zapdos-starter branch. A visible Magnet in the southeast corner rewards annex
exploration and gives Zapdos an immediately relevant held item.
