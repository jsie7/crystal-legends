# Crystal Legends automated tests

The tests validate the production `crystallegends.gbc` build at three levels:
checked-in source and data, compiled ROM contracts, and short headless emulator
scenarios. They do not replace manual visual, audio, balance, or full-playthrough
acceptance.

Install the locked local test environment:

```bash
uv sync --frozen --group test
```

Run the source-only suite:

```bash
make test-static
```

Run the aggregate source/build/ROM gate:

```bash
make test-crystallegends
```

`make test-crystallegends` includes the short headless emulator smoke profile.
`make test-all` additionally runs every implemented emulator scenario and the
upstream reference comparison.

The headless profile uses the test-only PyBoy 2.6.0 dependency under the LGPL;
it is not linked into or distributed with the ROM. Update its lock only after
the boot smoke and fixture-load scenarios pass.

Test-created files must use pytest temporary directories or an ignored local
artifact directory. Never mutate an approved fixture in place.

The approved `tests/fixtures/saves/bedroom_initialized.sav` fixture was created
through New Game and the in-game Save command. Its adjacent JSON records the
source revision, ROM and save hashes, deterministic player data, expected empty
progression state, and reproduction procedure. Runtime tests copy it beside a
temporary ROM before boot and verify that the canonical file's hash is
unchanged afterward.
