from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.asm_conditions import active_lines
from tests.support.content_data import parse_trainer_parties


pytestmark = [pytest.mark.static, pytest.mark.phase11]

CRYSTAL_LEGENDS = {"_CRYSTAL11", "_CRYSTALLEGENDS"}
REFERENCE = {"_CRYSTAL11"}


@pytest.fixture(scope="module")
def scenario(repo_root: Path) -> dict:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_11_endgame.json").read_text()
    )


def _active_code(path: Path, definitions: set[str]) -> list[str]:
    return [
        line.text.split(";", 1)[0].strip()
        for line in active_lines(path.read_text(), definitions)
        if line.text.split(";", 1)[0].strip()
    ]


def test_phase_11_reserves_exact_events_without_save_growth(
    repo_root: Path, scenario: dict
) -> None:
    source = repo_root / "constants/event_flags.asm"
    custom = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    event_names = [name for name, _ in scenario["events"]]
    positions = [custom.index(f"const {name}") for name in event_names]
    assert positions == list(range(positions[0], positions[0] + 2))
    assert all(not any(name in line for line in reference) for name in event_names)
    assert "const_skip 9" in reference
    assert "const_next 1600" in custom
    assert "; Unused: next 107 events" in source.read_text()


def test_red_party_and_dvs_match_the_provisional_contract(
    repo_root: Path, scenario: dict
) -> None:
    parties = parse_trainer_parties((repo_root / "data/trainers/parties.asm").read_text())
    red = [party for party in parties if party.group == "RedGroup"]
    assert len(red) == 1
    assert red[0].name == "RED"
    assert red[0].trainer_type == "TRAINERTYPE_MOVES"
    assert red[0].members == tuple(
        (str(level), species, *moves)
        for level, species, moves in scenario["red"]["party"]
    )

    custom_dvs = _active_code(repo_root / "data/trainers/dvs.asm", CRYSTAL_LEGENDS)
    reference_dvs = _active_code(repo_root / "data/trainers/dvs.asm", REFERENCE)
    assert "dn 15, 15, 15, 15" in custom_dvs
    assert "dn 15, 15, 15, 15" not in reference_dvs
    assert "dn 15, 13, 13, 14" in reference_dvs


def test_red_victory_fact_is_post_battle_and_never_used_for_visibility(
    repo_root: Path,
) -> None:
    room = _active_code(repo_root / "maps/SilverCaveRoom3.asm", CRYSTAL_LEGENDS)
    assert room.index("reloadmapafterbattle") < room.index("setevent EVENT_BEAT_RED")
    assert room.index("setevent EVENT_BEAT_RED") < room.index(
        "disappear SILVERCAVEROOM3_RED"
    )
    assert room.index("setevent EVENT_BEAT_RED") < room.index("credits")
    assert any(
        line.endswith(", EVENT_RED_IN_MT_SILVER")
        for line in room
        if line.startswith("object_event")
    )

    hall = _active_code(repo_root / "maps/HallOfFame.asm", CRYSTAL_LEGENDS)
    assert "clearevent EVENT_RED_IN_MT_SILVER" in hall
    assert "clearevent EVENT_BEAT_RED" not in hall

    clears = []
    for path in repo_root.rglob("*.asm"):
        if "clearevent EVENT_BEAT_RED" in path.read_text():
            clears.append(path)
    assert clears == []


def test_oak_parties_branch_from_the_legendary_starter_contract(
    repo_root: Path, scenario: dict
) -> None:
    parties = parse_trainer_parties((repo_root / "data/trainers/parties.asm").read_text())
    oak = [party for party in parties if party.group == "PokemonProfGroup"]
    assert len(oak) == 3
    assert all(party.name == "OAK" for party in oak)
    assert all(party.trainer_type == "TRAINERTYPE_MOVES" for party in oak)

    common = [
        (str(level), species, *moves)
        for level, species, moves in scenario["oak"]["common"]
    ]
    ace_level, ace_species, ace_moves = scenario["oak"]["ace"]
    ace = (str(ace_level), ace_species, *ace_moves)
    starter_level = str(scenario["oak"]["starter_slot"]["level"])
    for party, branch in zip(oak, scenario["oak"]["parties"], strict=True):
        starter = branch["starter"]
        assert list(party.members[:4]) == common
        assert party.members[4] == (
            starter_level,
            starter,
            *scenario["oak"]["starter_slot"]["moves"][starter],
        )
        assert party.members[5] == ace
        assert all(member[1] not in {"MEW", "MEWTWO"} for member in party.members)

    reference = _active_code(repo_root / "data/trainers/parties.asm", REFERENCE)
    start = reference.index("PokemonProfGroup:")
    assert reference[start + 1] == "WillGroup:"


def test_oak_constants_attributes_dvs_and_music_are_custom_only(repo_root: Path) -> None:
    constants = _active_code(repo_root / "constants/trainer_constants.asm", CRYSTAL_LEGENDS)
    reference_constants = _active_code(repo_root / "constants/trainer_constants.asm", REFERENCE)
    ids = [
        "OAK_ARTICUNO_PLAYER",
        "OAK_ZAPDOS_PLAYER",
        "OAK_MOLTRES_PLAYER",
    ]
    assert [constants.index(f"const {name}") for name in ids] == list(
        range(constants.index(f"const {ids[0]}"), constants.index(f"const {ids[0]}") + 3)
    )
    assert all(not any(name in line for line in reference_constants) for name in ids)

    attributes = _active_code(repo_root / "data/trainers/attributes.asm", CRYSTAL_LEGENDS)
    reference_attributes = _active_code(repo_root / "data/trainers/attributes.asm", REFERENCE)
    full_ai = "dw AI_BASIC | AI_SETUP | AI_SMART | AI_AGGRESSIVE | AI_CAUTIOUS | AI_STATUS | AI_RISKY"
    class_rows = [line for line in constants if line.startswith("trainerclass ")]
    oak_class_index = class_rows.index("trainerclass POKEMON_PROF") - 1
    oak_index = 2 + oak_class_index * 4
    assert attributes[oak_index : oak_index + 4] == [
        "db FULL_RESTORE, FULL_RESTORE",
        "db 25",
        full_ai,
        "dw CONTEXT_USE | SWITCH_SOMETIMES",
    ]
    assert reference_attributes[oak_index : oak_index + 4] == [
        "db NO_ITEM, NO_ITEM",
        "db 25",
        "dw AI_BASIC | AI_AGGRESSIVE | AI_STATUS",
        "dw CONTEXT_USE | SWITCH_SOMETIMES",
    ]

    custom_dvs = _active_code(repo_root / "data/trainers/dvs.asm", CRYSTAL_LEGENDS)
    reference_dvs = _active_code(repo_root / "data/trainers/dvs.asm", REFERENCE)
    assert custom_dvs.count("dn 15, 15, 15, 15") == 2
    assert reference_dvs.count("dn 15, 15, 15, 15") == 0

    music = _active_code(repo_root / "engine/battle/start_battle.asm", CRYSTAL_LEGENDS)
    reference_music = _active_code(repo_root / "engine/battle/start_battle.asm", REFERENCE)
    champion = music.index("ld de, MUSIC_CHAMPION_BATTLE")
    assert music[champion + 1 : champion + 3] == ["cp POKEMON_PROF", "jr z, .done"]
    assert "cp POKEMON_PROF" not in reference_music


def test_oak_endgame_state_machine_uses_only_red_and_caught_count(
    repo_root: Path, scenario: dict
) -> None:
    lab = _active_code(repo_root / "maps/OaksLab.asm", CRYSTAL_LEGENDS)
    hook = lab.index("farsjump Phase11OakEndgameScript")
    assert lab.index("checkevent EVENT_OPENED_MT_SILVER") < hook
    open_label = lab.index(".OpenMtSilver:")
    assert lab[open_label : open_label + 5] == [
        ".OpenMtSilver:",
        "writetext OakOpenMtSilverText",
        "promptbutton",
        "setevent EVENT_OPENED_MT_SILVER",
        "sjump .CheckPokedex",
    ]
    assert "farsjump Phase11OakEndgameScript" not in _active_code(
        repo_root / "maps/OaksLab.asm", REFERENCE
    )

    endgame = _active_code(repo_root / "maps/Phase11Endgame.asm", CRYSTAL_LEGENDS)
    assert endgame[:2] == [
        "DEF OAK_CHALLENGE_CAUGHT_REQUIREMENT EQU 240",
        "Phase11OakEndgameScript:",
    ]
    assert endgame.index("checkevent EVENT_BEAT_PROFESSOR_OAK") < endgame.index(
        "special ProfOaksPCBoot"
    )
    ordered = [
        "special ProfOaksPCBoot",
        "readvar VAR_DEXCAUGHT",
        "ifless OAK_CHALLENGE_CAUGHT_REQUIREMENT, .BelowRequirement",
        "checkevent EVENT_BEAT_RED",
        "iffalse .ReadyBeforeRed",
        "yesorno",
    ]
    position = -1
    for line in ordered:
        position = endgame.index(line, position + 1)
    forbidden = (
        "EVENT_PROJECT_MEW",
        "EVENT_SILVER_BIRD_RELEASED",
        "EVENT_BEAT_GIOVANNI",
        "EVENT_CAUGHT_",
    )
    assert not any(any(token in line for token in forbidden) for line in endgame)
    assert endgame.index("reloadmapafterbattle") < endgame.index(
        "setevent EVENT_BEAT_PROFESSOR_OAK"
    )
    assert endgame.index("setevent EVENT_BEAT_PROFESSOR_OAK") < endgame.index(
        "writetext Phase11OakCompletionText"
    )
    assert endgame.count("startbattle") == 1
    assert scenario["caught_requirement"] == 240


def test_oak_battle_result_text_stays_in_the_active_map_bank(repo_root: Path) -> None:
    lab = _active_code(repo_root / "maps/OaksLab.asm", CRYSTAL_LEGENDS)
    reference_lab = _active_code(repo_root / "maps/OaksLab.asm", REFERENCE)
    endgame = _active_code(repo_root / "maps/Phase11Endgame.asm", CRYSTAL_LEGENDS)
    for label in ("Phase11OakWinText:", "Phase11OakLossText:"):
        assert label in lab
        assert label not in reference_lab
        assert label not in endgame


def test_oak_true_ending_reuses_credits_and_returns_to_pallet(
    repo_root: Path, scenario: dict
) -> None:
    constants = _active_code(repo_root / "constants/ram_constants.asm", CRYSTAL_LEGENDS)
    reference_constants = _active_code(repo_root / "constants/ram_constants.asm", REFERENCE)
    assert "DEF SPAWN_OAK   EQU 3" in constants
    assert not any("SPAWN_OAK" in line for line in reference_constants)

    hall = _active_code(repo_root / "engine/events/halloffame.asm", CRYSTAL_LEGENDS)
    prepare = hall.index("Phase11PrepareOakCredits::")
    assert hall[prepare : prepare + 4] == [
        "Phase11PrepareOakCredits::",
        "ld a, SPAWN_OAK",
        "ld [wSpawnAfterChampion], a",
        "ret",
    ]
    red = hall.index("RedCredits::")
    ready = hall.index(".spawn_ready", red)
    assert hall[ready - 5 : ready] == [
        "ld a, [wSpawnAfterChampion]",
        "cp SPAWN_OAK",
        "jr z, .spawn_ready",
        "ld a, SPAWN_RED",
        "ld [wSpawnAfterChampion], a",
    ]

    intro = [
        line.split(";", 1)[0].strip()
        for line in (repo_root / "engine/menus/intro_menu.asm").read_text().splitlines()
        if line.split(";", 1)[0].strip()
    ]
    after_oak = intro.index(".AfterOak:")
    assert intro[after_oak : after_oak + 5] == [
        ".AfterOak:",
        "ld a, SPAWN_PALLET",
        "ld [wDefaultSpawnpoint], a",
        "call PostCreditsSpawn",
        "jr .loop",
    ]
    assert intro[after_oak + 6] == ".AfterRed:"

    endgame = _active_code(repo_root / "maps/Phase11Endgame.asm", CRYSTAL_LEGENDS)
    assert "halloffame" not in endgame
    ordered = [
        "setevent EVENT_BEAT_PROFESSOR_OAK",
        "writetext Phase11OakCompletionText",
        "special HealParty",
        "reanchormap",
        "callasm Phase11PrepareOakCredits",
        "credits",
    ]
    position = -1
    for line in ordered:
        position = endgame.index(line, position + 1)
    assert scenario["post_credits"]["spawn"] == "SPAWN_PALLET"


def test_mt_silver_hint_uses_durable_endgame_facts(repo_root: Path) -> None:
    custom = _active_code(
        repo_root / "maps/SilverCavePokecenter1F.asm", CRYSTAL_LEGENDS
    )
    reference = _active_code(repo_root / "maps/SilverCavePokecenter1F.asm", REFERENCE)
    script = custom.index("SilverCavePokecenter1FGrannyScript:")
    assert custom[script + 1 : script + 5] == [
        "checkevent EVENT_BEAT_PROFESSOR_OAK",
        "iftrue .AfterOak",
        "checkevent EVENT_BEAT_RED",
        "iftrue .AfterRed",
    ]
    assert not any("EVENT_RED_IN_MT_SILVER" in line for line in custom)
    assert not any("EVENT_BEAT_RED" in line for line in reference)


def test_phase_11_dialogue_fits_the_standard_text_width(repo_root: Path) -> None:
    lab = _active_code(repo_root / "maps/OaksLab.asm", CRYSTAL_LEGENDS)
    phase_11_text = [
        (
            "maps/OaksLab.asm",
            lab[
                lab.index("Phase11OakWinText:") : lab.index("OakOpenMtSilverText:")
            ],
        ),
        (
            "maps/Phase11Endgame.asm",
            _active_code(repo_root / "maps/Phase11Endgame.asm", CRYSTAL_LEGENDS),
        ),
        (
            "maps/SilverCavePokecenter1F.asm",
            _active_code(
                repo_root / "maps/SilverCavePokecenter1F.asm", CRYSTAL_LEGENDS
            ),
        ),
    ]
    for relative, lines in phase_11_text:
        for line in lines:
            if not line.startswith(("text \"", "line \"", "cont \"", "para \"")):
                continue
            content = line.split('"', 1)[1].rsplit('"', 1)[0]
            assert len(content) <= 18, f"{relative}: overlong text row {content!r}"
