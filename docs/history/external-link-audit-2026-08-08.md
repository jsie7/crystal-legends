# External-link audit — 2026-08-08

This preserves the repository guide’s original audit notes. Counts and
reachability describe that review, not a new external-link check. Use the
[current resource map](../repository-guide.md#external-documentation-and-wiki-map)
for navigation.

## External-link audit notes

Before this guide was added, the inherited Markdown set contained 282 external
URL occurrences and 202 unique URLs. Most are upstream source links embedded in
the issue catalogs: 126 distinct `pret/pokecrystal/blob/master/...` paths were
checked against this checkout.

Four stale source paths were found and corrected in this documentation change:

- One map-setup link referenced the removed
  `macros/scripts/map_setup.asm`; the encoding macro now lives in
  `data/maps/setup_scripts.asm` and dispatch metadata in
  `data/maps/setup_script_pointers.asm`.
- Three unique links in `design_flaws.md` contained an accidental duplicate
  `/master/` path component.

The central published docs, wiki, Tutorials page, Assembly programming page,
symbols branch, RGBDS release, Polished Map project, and gb-asm-tools project
were reachable at review time. The old Microsoft WSL URL in `INSTALL.md`
redirects to the current Microsoft Learn page, and the Cygwin installer page is
still live.

Most source links in the inherited docs point to the moving upstream `master`
branch. They are useful for browsing upstream, but the same relative file in
this checkout is the source of truth for Crystal Legends. Prefer local relative
links in new fork-specific documentation.
