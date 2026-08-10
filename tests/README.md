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

Test-created files must use pytest temporary directories or an ignored local
artifact directory. Never mutate an approved fixture in place.
