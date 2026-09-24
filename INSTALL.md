# Build and play Crystal Legends

This guide builds **`crystallegends.gbc`** from this repository's source and
explains how to play it. No original ROM is needed as build input.

1. Install the [platform prerequisites](#platform-setup).
2. Install [RGBDS 1.0.3](#install-rgbds-103).
3. [Build Crystal Legends](#build-crystal-legends), then [open it in an emulator](#play).

## Requirements

- Git, Make, and a C17 compiler for the repository's build helpers.
- **RGBDS 1.0.3**, pinned in [.rgbds-version](.rgbds-version).
- A Game Boy Color emulator with battery-save and real-time-clock support to play.

Building RGBDS from source also needs a C++20 compiler, Bison, libpng, and
pkg-config; the main setup paths below install those prerequisites. Python,
uv, and PyBoy are only needed for the optional [automated tests](tests/README.md).

## Platform setup

<a id="windows-10-11-or-newer"></a>

### Windows with WSL

Use [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install).
If it is not installed, open PowerShell as administrator and run:

```powershell
wsl --install -d Ubuntu
```

Restart if prompted, open Ubuntu, and finish creating your Linux account.
Run the remaining build commands in the **Ubuntu terminal**. Continue with
[Debian or Ubuntu](#debian-or-ubuntu) below.

Keep the checkout in the Linux filesystem, for example `~/src/crystal-legends`.
It is accessible from Windows: run `explorer.exe .` in the project directory
or browse `\\wsl$` in File Explorer. This follows
[Microsoft's filesystem guidance](https://learn.microsoft.com/en-us/windows/wsl/filesystems)
and avoids the slower cross-filesystem build path under `/mnt/c/`.

### macOS

Install Apple's Command Line Tools if they are missing:

```bash
xcode-select --install
```

After that installation finishes, install [Homebrew](https://brew.sh/) if needed,
then run in Terminal:

```bash
brew install bison libpng pkg-config
export PATH="$(brew --prefix bison)/bin:$PATH"
```

The Command Line Tools provide Git, Make, and the compilers. Keep this terminal
open so the Homebrew Bison path is used, then [install RGBDS](#install-rgbds-103).

### Linux

#### Debian or Ubuntu

```bash
sudo apt-get update
sudo apt-get install build-essential git bison libpng-dev pkg-config
```

Then [install RGBDS](#install-rgbds-103). Other distributions can use the
[additional environments](#additional-environments) section.

## Install RGBDS 1.0.3

If all four RGBDS tools already report version 1.0.3, skip to
[building the game](#build-crystal-legends). Otherwise, the following installs
that exact release under your user account on macOS, Linux, or WSL:

```bash
mkdir -p "$HOME/.local/src"
git clone --branch v1.0.3 --depth 1 https://github.com/gbdev/rgbds.git "$HOME/.local/src/rgbds-1.0.3"
make -C "$HOME/.local/src/rgbds-1.0.3"
make -C "$HOME/.local/src/rgbds-1.0.3" install PREFIX="$HOME/.local"
export PATH="$HOME/.local/bin:$PATH"
```

If that source directory already exists, reuse the existing v1.0.3 checkout
instead of cloning over it. Add the final `export PATH` line to your shell's
startup file to make the installed tools available in future terminals.
The [RGBDS v1.0.3 build instructions](https://github.com/gbdev/rgbds/tree/v1.0.3#installing)
also describe alternate installation options.

Verify the version of every tool:

```bash
rgbasm --version
rgblink --version
rgbfix --version
rgbgfx --version
```

Use the pinned version even if a package manager offers a newer one. The
assembly guard accepts 1.0.0 or newer, but 1.0.3 is the project's reproduction
baseline.

<a id="build-pokecrystal"></a>

## Build Crystal Legends

Choose a directory for your source checkout, then run:

```bash
mkdir -p "$HOME/src"
cd "$HOME/src"
git clone https://github.com/jsie7/crystal-legends.git
cd crystal-legends
make crystallegends
```

If you already cloned this repository, run `make crystallegends` from its root.
The build compiles the local C helpers automatically. On systems that provide
Clang without a `gcc` command, use `make CC=clang crystallegends`.

Successful output appears in the repository root:

| File | Purpose |
| --- | --- |
| `crystallegends.gbc` | The playable game |
| `crystallegends.sym` | Symbols for debugging |
| `crystallegends.map` | The linker layout report |

**Use the explicit `crystallegends` target.** Plain `make` builds the original
Pokémon Crystal v1.0; `make crystal11` builds the original v1.1. Those are
reference builds, not the custom game.

### Build with a local rgbds version

To keep multiple RGBDS versions side by side, point `RGBDS` at the directory
containing the four tools. Include the trailing slash:

```bash
make RGBDS="$HOME/.local/bin/" crystallegends
```

A project-local directory works too:

```bash
make RGBDS=rgbds-1.0.3/ crystallegends
```

Use the same override on subsequent builds. Keep local tool binaries untracked.

## Play

Open `crystallegends.gbc` in a Game Boy Color emulator.
[SameBoy](https://sameboy.github.io/) was used for the recorded manual playtests;
those reports do not establish compatibility with every emulator or device.

Start a new game for the full Crystal Legends journey. Keep the emulator's
real-time clock working normally: time of day, weekdays, and daily events are
part of the game.

Use the in-game **SAVE** command and **CONTINUE** after restarting. The emulator
stores a battery-save file separately from the ROM; its name and location
depend on the emulator. Keep that file when moving or updating your game.
Emulator snapshots are separate from normal game saves.

## Update and rebuild

Close the emulator and back up its battery save before changing your ROM.
After committing or otherwise preserving any local source edits, update an
existing checkout from its repository root:

```bash
git pull --ff-only
make clean
make crystallegends
```

If you use `RGBDS=...` or `CC=clang`, add the same override to the build command.
Recheck [.rgbds-version](.rgbds-version) after updating. Replace the ROM in your
emulator's game folder and retain the matching save using that emulator's
naming convention. Read [project status](docs/status.md) for recorded limitations;
updating a ROM does not add held items to Pokémon already received.

`make clean` removes generated build products, including the ROM and graphics
intermediates. It does not remove game saves or hand-written source files.

## Troubleshooting and development

For toolchain errors, missing compilers, or bank overflows, start with the
[FAQ](FAQ.md). When reporting a problem, include the failing command, full error,
operating system, RGBDS version, and source commit (`git rev-parse --short HEAD`).
For gameplay reports, also include the emulator version and starting save state.

- [Automated test setup and profiles](tests/README.md) — optional for building or playing.
- [Build and validation workflows](docs/workflows.md) — including `make compare` for upstream reference ROMs.
- [Repository guide](docs/repository-guide.md) — source layout and variant targets.

The existing GitHub CI builds the reference target on this fork; it does not
run the custom-ROM test harness or publish a playable artifact.

## Additional environments

These are alternatives to the main setup paths; install the same pinned RGBDS
release and use the same `make crystallegends` target.

### OpenSUSE

Install Make, Git, C/C++ compilers, Bison, libpng development headers, and
pkg-config using your distribution's package manager, then follow the
[RGBDS source-install steps](#install-rgbds-103).

### Arch Linux

Install `base-devel`, `git`, and `libpng` with pacman. Check the version before
using a packaged `rgbds`; use the [pinned source build](#install-rgbds-103) if it
differs from 1.0.3.

### Termux

Install `make`, `clang`, `git`, and `sed` with `pkg`. Check whether its `rgbds`
package supplies 1.0.3; otherwise follow the
[upstream build instructions](https://github.com/gbdev/rgbds/tree/v1.0.3#installing)
with the required dependencies and Termux's installation prefix. Build the game
with `make CC=clang crystallegends`.

<a id="windows-8-or-older"></a>

### Cygwin

Use the [current Cygwin installer](https://cygwin.com/install.html), install
`make`, `git`, and `gcc-core`, and obtain the matching Windows/Cygwin tools from
the [RGBDS 1.0.3 release](https://github.com/gbdev/rgbds/releases/tag/v1.0.3).
Run the build in the Cygwin terminal.

### Other distros

Install Git, Make, a C17 compiler, and RGBDS 1.0.3. If building RGBDS from
source, also install a C++20 compiler, Bison, libpng headers, and pkg-config.
Use the [upstream source guide](https://github.com/gbdev/rgbds/tree/v1.0.3#installing)
for platform-specific adjustments.
