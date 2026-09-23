from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.constant_resolver import resolve_constants
from tests.support.rom_image import RomImage
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.rom, pytest.mark.phase11]


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_11_endgame.json").read_text()
    )


@pytest.fixture(scope="module")
def phase_11_constants(repo_root: Path, tmp_path_factory, scenario: dict) -> dict[str, int]:
    names = {
        "NUM_EVENTS",
        "NUM_TRAINER_ATTRIBUTES",
        "TRAINERTYPE_MOVES",
        "RED",
        "POKEMON_PROF",
        "OAK_ARTICUNO_PLAYER",
        "OAK_ZAPDOS_PLAYER",
        "OAK_MOLTRES_PLAYER",
        "FULL_RESTORE",
        "SPAWN_OAK",
        "SPAWN_PALLET",
        "callasm_command",
        "checkevent_command",
        "credits_command",
        "end_command",
        "farwritetext_command",
        "iffalse_command",
        "ifless_command",
        "iftrue_command",
        "readvar_command",
        "special_command",
        "VAR_DEXCAUGHT",
        "waitbutton_command",
        "winlosstext_command",
        "writetext_command",
        "yesorno_command",
        "EVENT_BEAT_RED",
        "EVENT_BEAT_PROFESSOR_OAK",
    }
    for boss in (scenario["red"],):
        for _, species, moves in boss["party"]:
            names.add(species)
            names.update(moves)
    for level, species, moves in scenario["oak"]["common"]:
        names.add(species)
        names.update(moves)
    ace_level, ace_species, ace_moves = scenario["oak"]["ace"]
    names.add(ace_species)
    names.update(ace_moves)
    for branch in scenario["oak"]["parties"]:
        starter = branch["starter"]
        names.add(starter)
        names.add(branch["trainer"])
        names.update(scenario["oak"]["starter_slot"]["moves"][starter])
    return resolve_constants(
        repo_root, tmp_path_factory.mktemp("phase_11_constants"), sorted(names)
    )


def _decode_moves_party(
    rom: RomImage, offset: int, trainer_type_moves: int
) -> list[tuple[int, ...]]:
    while rom.u8(offset) != 0x50:
        offset += 1
    offset += 1
    assert rom.u8(offset) == trainer_type_moves
    offset += 1
    party = []
    while rom.u8(offset) != 0xFF:
        party.append(tuple(rom.slice(offset, 6)))
        offset += 6
    return party


def test_compiled_phase_11_event_ids_preserve_save_layout(
    repo_root: Path, scenario: dict, phase_11_constants: dict[str, int]
) -> None:
    for name, expected in scenario["events"]:
        assert phase_11_constants[name] == expected
    assert phase_11_constants["NUM_EVENTS"] == 2048
    symbols = SymbolTable.parse((repo_root / scenario["symbols"]).read_text())
    assert symbols["wCurBox"].address - symbols["wEventFlags"].address == 256


def test_compiled_red_party_is_custom_and_reference_red_remains_stock(
    repo_root: Path, scenario: dict, phase_11_constants: dict[str, int]
) -> None:
    custom = RomImage.load(repo_root / scenario["rom"])
    custom_symbols = SymbolTable.parse((repo_root / scenario["symbols"]).read_text())
    custom_party = _decode_moves_party(
        custom,
        custom_symbols["RedGroup"].rom_offset,
        phase_11_constants["TRAINERTYPE_MOVES"],
    )
    expected = [
        tuple(
            [level, phase_11_constants[species]]
            + [phase_11_constants[move] for move in moves]
        )
        for level, species, moves in scenario["red"]["party"]
    ]
    assert custom_party == expected

    reference = RomImage.load(repo_root / scenario["reference_rom"])
    reference_symbols = SymbolTable.parse(
        (repo_root / scenario["reference_symbols"]).read_text()
    )
    reference_party = _decode_moves_party(
        reference,
        reference_symbols["RedGroup"].rom_offset,
        phase_11_constants["TRAINERTYPE_MOVES"],
    )
    assert [member[0] for member in reference_party] == [81, 73, 75, 77, 77, 77]
    assert [member[1] for member in reference_party] == [member[1] for member in expected]


def test_compiled_red_dvs_are_maxed_only_in_crystal_legends(
    repo_root: Path, phase_11_constants: dict[str, int]
) -> None:
    class_index = phase_11_constants["RED"] - 1
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())
    assert custom.slice(custom_symbols["TrainerClassDVs"].rom_offset + class_index * 2, 2) == bytes([0xFF, 0xFF])
    assert reference.slice(reference_symbols["TrainerClassDVs"].rom_offset + class_index * 2, 2) == bytes([0xFD, 0xDE])


def test_compiled_oak_parties_use_the_existing_professor_group(
    repo_root: Path, scenario: dict, phase_11_constants: dict[str, int]
) -> None:
    rom = RomImage.load(repo_root / scenario["rom"])
    symbols = SymbolTable.parse((repo_root / scenario["symbols"]).read_text())
    class_index = phase_11_constants["POKEMON_PROF"] - 1
    pointer = rom.u16le(symbols["TrainerGroups"].rom_offset + class_index * 2)
    assert pointer == symbols["PokemonProfGroup"].address

    offset = symbols["PokemonProfGroup"].rom_offset
    parties = []
    for _ in scenario["oak"]["parties"]:
        party = _decode_moves_party(
            rom, offset, phase_11_constants["TRAINERTYPE_MOVES"]
        )
        parties.append(party)
        offset += 5 + len(party) * 6 + 1

    common = [
        tuple(
            [level, phase_11_constants[species]]
            + [phase_11_constants[move] for move in moves]
        )
        for level, species, moves in scenario["oak"]["common"]
    ]
    ace_level, ace_species, ace_moves = scenario["oak"]["ace"]
    ace = tuple(
        [ace_level, phase_11_constants[ace_species]]
        + [phase_11_constants[move] for move in ace_moves]
    )
    for party, branch in zip(parties, scenario["oak"]["parties"], strict=True):
        starter = branch["starter"]
        expected_starter = tuple(
            [
                scenario["oak"]["starter_slot"]["level"],
                phase_11_constants[starter],
            ]
            + [
                phase_11_constants[move]
                for move in scenario["oak"]["starter_slot"]["moves"][starter]
            ]
        )
        assert party == common + [expected_starter, ace]

    reference_symbols = SymbolTable.parse(
        (repo_root / scenario["reference_symbols"]).read_text()
    )
    assert (
        reference_symbols["PokemonProfGroup"].rom_offset
        == reference_symbols["WillGroup"].rom_offset
    )


def test_compiled_oak_attributes_and_dvs_are_custom_only(
    repo_root: Path, phase_11_constants: dict[str, int]
) -> None:
    class_index = phase_11_constants["POKEMON_PROF"] - 1
    width = phase_11_constants["NUM_TRAINER_ATTRIBUTES"]
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    custom_symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    reference = RomImage.load(repo_root / "pokecrystal11.gbc")
    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())

    custom_attributes = custom.slice(
        custom_symbols["TrainerClassAttributes"].rom_offset + class_index * width,
        width,
    )
    reference_attributes = reference.slice(
        reference_symbols["TrainerClassAttributes"].rom_offset + class_index * width,
        width,
    )
    assert custom_attributes[:3] == bytes(
        [phase_11_constants["FULL_RESTORE"], phase_11_constants["FULL_RESTORE"], 25]
    )
    assert reference_attributes[:3] == bytes([0, 0, 25])
    assert custom.slice(
        custom_symbols["TrainerClassDVs"].rom_offset + class_index * 2, 2
    ) == bytes([0xFF, 0xFF])
    assert reference.slice(
        reference_symbols["TrainerClassDVs"].rom_offset + class_index * 2, 2
    ) == bytes([0x98, 0x88])


def test_compiled_oak_credits_selector_and_script_are_transient(
    repo_root: Path, phase_11_constants: dict[str, int]
) -> None:
    assert phase_11_constants["SPAWN_OAK"] == 3
    custom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    prepare = symbols["Phase11PrepareOakCredits"]
    assert custom.at(prepare, 6) == bytes(
        [
            0x3E,
            phase_11_constants["SPAWN_OAK"],
            0xEA,
            symbols["wSpawnAfterChampion"].address & 0xFF,
            symbols["wSpawnAfterChampion"].address >> 8,
            0xC9,
        ]
    )

    script = custom.slice(
        symbols["Phase11OakEndgameScript"].rom_offset,
        symbols["Phase11OakNeedsRedText"].rom_offset
        - symbols["Phase11OakEndgameScript"].rom_offset,
    )
    call_prepare = bytes(
        [phase_11_constants["callasm_command"], prepare.bank]
    ) + prepare.address.to_bytes(2, "little")
    assert script.count(call_prepare) == 1
    # Count the instruction sequence, not matching bytes inside text pointers.
    assert script.count(call_prepare + bytes([
        phase_11_constants["credits_command"], phase_11_constants["end_command"]
    ])) == 1

    reference_symbols = SymbolTable.parse((repo_root / "pokecrystal11.sym").read_text())
    assert "Phase11PrepareOakCredits" not in reference_symbols
    assert "Phase11OakEndgameScript" not in reference_symbols


def test_compiled_oak_predicate_and_battle_text_banks(
    repo_root: Path, phase_11_constants: dict[str, int]
) -> None:
    constants = phase_11_constants
    rom = RomImage.load(repo_root / "crystallegends.gbc")
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    offset = symbols["Phase11OakEndgameScript"].rom_offset

    assert rom.u8(offset) == constants["checkevent_command"]
    assert rom.u16le(offset + 1) == constants["EVENT_BEAT_PROFESSOR_OAK"]
    offset += 3
    assert rom.u8(offset) == constants["iftrue_command"]
    assert rom.u16le(offset + 1) == symbols[
        "Phase11OakEndgameScript.Complete"
    ].address
    offset += 3
    assert symbols["OakLabDexCheckText"].bank != symbols["Phase11OakEndgameScript"].bank
    assert rom.u8(offset) == constants["farwritetext_command"]
    assert rom.u8(offset + 1) == symbols["OakLabDexCheckText"].bank
    assert rom.u16le(offset + 2) == symbols["OakLabDexCheckText"].address
    offset += 4
    assert rom.u8(offset) == constants["waitbutton_command"]
    offset += 1
    assert rom.u8(offset) == constants["special_command"]
    offset += 3
    assert rom.slice(offset, 2) == bytes(
        [constants["readvar_command"], constants["VAR_DEXCAUGHT"]]
    )
    offset += 2
    assert rom.u8(offset) == constants["ifless_command"]
    assert rom.u8(offset + 1) == 240
    assert rom.u16le(offset + 2) == symbols[
        "Phase11OakEndgameScript.BelowRequirement"
    ].address
    offset += 4
    assert rom.u8(offset) == constants["checkevent_command"]
    assert rom.u16le(offset + 1) == constants["EVENT_BEAT_RED"]
    offset += 3
    assert rom.u8(offset) == constants["iffalse_command"]
    assert rom.u16le(offset + 1) == symbols[
        "Phase11OakEndgameScript.ReadyBeforeRed"
    ].address

    goodbye = symbols["OakLabGoodbyeText"]
    offset = symbols["Phase11OakEndgameScript.OrdinaryGoodbye"].rom_offset
    assert rom.u8(offset) == constants["farwritetext_command"]
    assert rom.u8(offset + 1) == goodbye.bank
    assert rom.u16le(offset + 2) == goodbye.address

    win = symbols["Phase11OakWinText"]
    loss = symbols["Phase11OakLossText"]
    lab = symbols["OaksLab_MapScripts"]
    endgame = symbols["Phase11OakEndgameScript"]
    assert win.bank == loss.bank == lab.bank
    assert win.bank != endgame.bank
    battle_script = rom.slice(
        endgame.rom_offset,
        symbols["Phase11OakNeedsRedText"].rom_offset - endgame.rom_offset,
    )
    win_loss = (
        bytes([constants["winlosstext_command"]])
        + win.address.to_bytes(2, "little")
        + loss.address.to_bytes(2, "little")
    )
    assert battle_script.count(win_loss) == 1
