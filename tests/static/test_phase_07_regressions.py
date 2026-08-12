from __future__ import annotations

from pathlib import Path

import pytest

from tests.support.asm_conditions import active_lines


pytestmark = [pytest.mark.static, pytest.mark.phase7]


CRYSTAL_LEGENDS = {"_CRYSTAL11", "_CRYSTALLEGENDS"}
REFERENCE = {"_CRYSTAL11"}


def _active_code(path: Path, definitions: set[str]) -> list[str]:
    return [
        line.text.split(";", 1)[0].strip()
        for line in active_lines(path.read_text(), definitions)
        if line.text.split(";", 1)[0].strip()
    ]


def _section(lines: list[str], start: str, end: str) -> list[str]:
    first = lines.index(start)
    return lines[first : lines.index(end, first + 1)]


def test_slowpoke_well_foreshadows_research_without_naming_subject(
    repo_root: Path,
) -> None:
    source = repo_root / "maps/SlowpokeWellB1F.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    story = _section(crystal, "GruntM29AfterBattleText:", "GruntM1SeenText:")
    story += _section(crystal, "GruntF1AfterBattleText:", "SlowpokeWellB1FSlowpokeWithMailText:")

    assert 'text "Sure, we\'ve been"' in story
    assert 'para "The lab paid extra"' in story
    assert 'para "The science crew"' in story
    assert 'line "regrowth data."' in story
    assert all("MEW" not in line for line in story)
    assert 'para "The lab paid extra"' not in reference
    assert 'para "The science crew"' not in reference


def test_lake_of_rage_frames_forced_evolution_as_proof_without_replacing_it(
    repo_root: Path,
) -> None:
    source = repo_root / "maps/LakeOfRage.asm"
    crystal = _active_code(source, CRYSTAL_LEGENDS)
    reference = _active_code(source, REFERENCE)
    story = _section(
        crystal, "LakeOfRageLanceRadioSignalText:", "LakeOfRageLanceRefusedText:"
    )

    for row in (
        'para "are being forced"',
        'line "to evolve."',
        'para "A mysterious radio"',
        'para "from MAHOGANY is"',
        'para "The red GYARADOS"',
        'para "signal could force"',
        'cont "far beyond this."',
    ):
        assert row in story
    assert 'para "The red GYARADOS"' not in reference
    assert "loadwildmon GYARADOS, 30" in crystal
    assert "giveitem RED_SCALE" in crystal


def test_mahogany_reveal_uses_existing_people_office_lab_and_transmitter(
    repo_root: Path,
) -> None:
    b3f_source = repo_root / "maps/TeamRocketBaseB3F.asm"
    b2f_source = repo_root / "maps/TeamRocketBaseB2F.asm"
    b3f = _active_code(b3f_source, CRYSTAL_LEGENDS)
    b3f_reference = _active_code(b3f_source, REFERENCE)
    b2f = _active_code(b2f_source, CRYSTAL_LEGENDS)
    b2f_reference = _active_code(b2f_source, REFERENCE)

    for row in (
        "TrainerScientistRoss:",
        "TrainerScientistMitch:",
        'para "The LAKE trial was"',
        'para "The GOLDENROD rig"',
        "TeamRocketBaseB3FProjectMewDossierScript:",
        "TeamRocketBaseB3FProjectMewTestDataScript:",
        'text "PROJECT MEW"',
        'line "MEW, held captive."',
        'line "near CERULEAN."',
        'text "LAKE TRIAL: PROOF"',
        "bg_event  8,  3, BGEVENT_UP, TeamRocketBaseB3FProjectMewDossierScript",
        "bg_event 20,  7, BGEVENT_UP, TeamRocketBaseB3FProjectMewTestDataScript",
    ):
        assert row in b3f
    assert 'para "The PROJECT MEW"' in b3f

    for row in (
        "TeamRocketBaseB2FTransmitterScript:",
        'para "SUBJECT TRANSFER:"',
        'para "PROJECT MEW data"',
        'cont "GOLDENROD TOWER."',
    ):
        assert row in b2f

    for token in (
        "ProjectMewDossier",
        "ProjectMewTestData",
        'text "PROJECT MEW"',
        'para "The PROJECT MEW"',
    ):
        assert not any(token in line for line in b3f_reference)
    for token in ('para "SUBJECT TRANSFER:"', 'para "PROJECT MEW data"'):
        assert token not in b2f_reference


def test_stock_rocket_story_progression_operations_remain_present(
    repo_root: Path,
) -> None:
    lake = _active_code(repo_root / "maps/LakeOfRage.asm", CRYSTAL_LEGENDS)
    b2f = _active_code(repo_root / "maps/TeamRocketBaseB2F.asm", CRYSTAL_LEGENDS)
    radio = _active_code(repo_root / "maps/RadioTower5F.asm", CRYSTAL_LEGENDS)

    for row in (
        "loadwildmon GYARADOS, 30",
        "giveitem RED_SCALE",
        "setmapscene MAHOGANY_MART_1F, SCENE_MAHOGANYMART1F_LANCE_UNCOVERS_STAIRS",
    ):
        assert row in lake
    for row in (
        "setevent EVENT_CLEARED_ROCKET_HIDEOUT",
        "clearflag ENGINE_ROCKET_SIGNAL_ON_CH20",
        "setevent EVENT_MAHOGANY_TOWN_POKEFAN_M_BLOCKS_GYM",
    ):
        assert row in b2f
    for row in (
        "verbosegiveitem BASEMENT_KEY",
        "verbosegiveitem CLEAR_BELL",
        "setevent EVENT_CLEARED_RADIO_TOWER",
        "setevent EVENT_BLACKTHORN_CITY_SUPER_NERD_BLOCKS_GYM",
        "setmapscene ECRUTEAK_TIN_TOWER_ENTRANCE, SCENE_ECRUTEAKTINTOWERENTRANCE_SAGE_BLOCKS",
        "setevent EVENT_TEAM_ROCKET_DISBANDED",
    ):
        assert row in radio
