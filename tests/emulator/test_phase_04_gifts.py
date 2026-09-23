from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.bedroom_scenario import (
    dump_battery_ram,
    event_is_set,
    save_game_from_overworld,
    wait_for_idle,
)
from tests.support.constant_resolver import resolve_constants
from tests.support.game_state import read_progress
from tests.support.gift_scenario import (
    assert_completed_gift_is_inert,
    assert_gift_absent,
    clear_current_box,
    cross_map_warp,
    interact_with_gift,
    set_current_box_full,
    set_party_full,
)
from tests.support.legendary_scenario import place_player, walk_steps
from tests.support.phase_04_scenario import (
    loaded_phase_4_checkpoint,
    loaded_phase_4_saved_game,
    retarget_phase_4_save,
)
from tests.support.symbol_table import SymbolTable


pytestmark = [pytest.mark.emulator, pytest.mark.phase4]


@pytest.fixture(scope="module")
def scenarios(repo_root: Path) -> list[dict]:
    return json.loads(
        (repo_root / "tests/fixtures/scenarios/phase_04_johto_gifts.json").read_text()
    )


@pytest.fixture(scope="module")
def phase_4_constants(
    repo_root: Path, tmp_path_factory, scenarios: list[dict]
) -> dict[str, int]:
    names = {
        "SPAWN_N_A",
        "NUM_OBJECTS",
        "NUM_OBJECT_STRUCTS",
        "OBJECT_LENGTH",
        "OBJECT_SPRITE",
        "OBJECT_SPRITE_TILE",
        "OBJECT_FACING",
        "OBJECT_FLAGS2",
        "OFF_SCREEN_F",
        "FACING_STEP_DOWN_0",
        "FACING_STEP_UP_0",
        "TILE_SIZE",
        "SPRITE_SUPER_NERD",
        "OW_UP",
        "OW_RIGHT",
        "OW_DOWN",
        "GROUP_BURNED_TOWER_1F",
        "MAP_BURNED_TOWER_1F",
        "MAPSETUP_WARP",
        "PARTY_LENGTH",
        "PARTYMON_STRUCT_LENGTH",
        "BOXMON_STRUCT_LENGTH",
        "MONS_PER_BOX",
        "EEVEE",
        "LUCKY_EGG",
        "EVENT_GOT_CHIKORITA_FROM_ILEX_FOREST",
        "EVENT_GOT_CYNDAQUIL_FROM_BURNED_TOWER",
        "EVENT_GOT_TOTODILE_FROM_CIANWOOD",
        "EVENT_BURNED_TOWER_B1F_BEASTS_1",
        "EVENT_BURNED_TOWER_B1F_BEASTS_2",
        "EVENT_HOLE_IN_BURNED_TOWER",
        "EVENT_SAW_SUICUNE_AT_CIANWOOD_CITY",
        "RAIKOU",
        "ENTEI",
        "SECRETPOTION",
        "EVENT_JASMINE_RETURNED_TO_GYM",
    }
    for scenario in scenarios:
        names.update(
            {
                scenario["species"],
                scenario["object_sprite"],
                scenario["prerequisite_event"],
                scenario["completion_event"],
                f"GROUP_{scenario['map']}",
                f"MAP_{scenario['map']}",
            }
        )
    constants = resolve_constants(
        repo_root,
        tmp_path_factory.mktemp("phase_4_runtime_constants"),
        sorted(names),
    )
    symbols = SymbolTable.parse((repo_root / "crystallegends.sym").read_text())
    for scene in (
        "SCENE_BURNEDTOWER1F_NOOP",
        "SCENE_BURNEDTOWERB1F_RELEASE_THE_BEASTS",
        "SCENE_BURNEDTOWERB1F_NOOP",
    ):
        constants[scene] = symbols.constant(scene)
    return constants


@pytest.fixture(scope="module")
def chikorita(scenarios: list[dict]) -> dict:
    return next(row for row in scenarios if row["species"] == "CHIKORITA")


@pytest.fixture(scope="module")
def cyndaquil(scenarios: list[dict]) -> dict:
    return next(row for row in scenarios if row["species"] == "CYNDAQUIL")


@pytest.fixture(scope="module")
def totodile(scenarios: list[dict]) -> dict:
    return next(row for row in scenarios if row["species"] == "TOTODILE")


@pytest.fixture(scope="module")
def implemented_gifts(
    chikorita: dict, cyndaquil: dict, totodile: dict
) -> dict[str, dict]:
    return {row["species"]: row for row in (chikorita, cyndaquil, totodile)}


def _sprite_slots(session) -> dict[int, int]:
    table = session.read_symbol_range("wUsedSprites", "wUsedSpritesEnd")
    return {sprite: tile for sprite, tile in zip(table[::2], table[1::2]) if sprite}


def _held_items(session, constants: dict[str, int]) -> tuple[tuple[int, ...], ...]:
    inventories = []
    for count_label, item_label, stride_constant in (
        ("wPartyCount", "wPartyMon1Item", "PARTYMON_STRUCT_LENGTH"),
        ("sBoxCount", "sBoxMon1Item", "BOXMON_STRUCT_LENGTH"),
    ):
        count = session.read_symbol(count_label)
        stride = constants[stride_constant]
        data = (
            session.read_symbol_bytes(item_label, (count - 1) * stride + 1)
            if count else b""
        )
        inventories.append(tuple(data[::stride]))
    return tuple(inventories)


def _assert_live_sprite_slots(session, constants: dict[str, int]) -> None:
    slots = _sprite_slots(session)
    length = constants["OBJECT_LENGTH"]
    objects = session.read_symbol_bytes(
        "wObjectStructs", constants["NUM_OBJECT_STRUCTS"] * length
    )
    for index in range(constants["NUM_OBJECT_STRUCTS"]):
        row = objects[index * length : (index + 1) * length]
        sprite = row[constants["OBJECT_SPRITE"]]
        if sprite:
            assert sprite in slots, f"object {index}: unloaded sprite {sprite}"
            assert row[constants["OBJECT_SPRITE_TILE"]] == slots[sprite], (
                f"object {index}: stale graphics slot for sprite {sprite}"
            )


def _assert_loaded_graphics(session, constants, sprite, graphics, tiles) -> None:
    slots = _sprite_slots(session)
    assert sprite in slots, f"sprite {sprite} is missing from the graphics list"
    tile = slots[sprite]
    # The high bit selects the second sprite table in VRAM bank 0.
    bank = 0 if tile & 0x80 else 1
    address = session.symbols["vTiles0"].address + (tile & 0x7F) * constants["TILE_SIZE"]
    length = tiles * constants["TILE_SIZE"]
    actual = bytes(session.pyboy.memory[bank, address + i] for i in range(length))
    offset = session.symbols[graphics].rom_offset
    expected = session.prepared.rom.read_bytes()[offset : offset + length]
    assert actual == expected, f"incorrect loaded graphics for {graphics}"


def _assert_gift_graphics(session, constants, scenario) -> dict[int, int]:
    icons = {"CHIKORITA": "OddishIcon", "CYNDAQUIL": "FoxIcon", "TOTODILE": "MonsterIcon"}
    _assert_loaded_graphics(
        session, constants, constants[scenario["object_sprite"]],
        icons[scenario["species"]], 8,
    )
    _assert_live_sprite_slots(session, constants)
    length = constants["OBJECT_LENGTH"]
    objects = session.read_symbol_bytes(
        "wObjectStructs", constants["NUM_OBJECT_STRUCTS"] * length
    )
    for index in range(constants["NUM_OBJECT_STRUCTS"]):
        row = objects[index * length : (index + 1) * length]
        if row[constants["OBJECT_SPRITE"]] != constants[scenario["object_sprite"]]:
            continue
        if row[constants["OBJECT_FLAGS2"]] & (1 << constants["OFF_SCREEN_F"]):
            continue
        # Icons contain two four-tile frames, not the human directional frames.
        assert row[constants["OBJECT_FACING"]] in {
            constants["FACING_STEP_DOWN_0"], constants["FACING_STEP_UP_0"],
        }, f"{scenario['species']} is drawing outside its icon frames"
    return _sprite_slots(session)


def _open_and_close_options(session, max_frames: int) -> None:
    # Options always sits two UP presses from the first Start-menu entry,
    # including checkpoints with no party. Returning reloads overworld graphics.
    session.register_hook("_Option.joypad_loop")
    session.register_hook("ReloadTilesetAndPalettes")
    options_count = session.hook_history.count("_Option.joypad_loop") + 1
    reload_count = session.hook_history.count("ReloadTilesetAndPalettes") + 1
    session.write_symbol("wBattleMenuCursorPosition", 1)
    session.tap("start", 10, 30)
    session.tap("up", 10, 10)
    session.tap("up", 10, 10)
    session.tap("a", 10, 10)
    session.wait_for_hook_count("_Option.joypad_loop", options_count, max_frames)
    session.tap("b", 10, 120)
    session.wait_for_hook_count("ReloadTilesetAndPalettes", reload_count, max_frames)
    session.tap("b", 10, 120)
    wait_for_idle(session, max_frames)


@pytest.mark.parametrize("species_name", ["CHIKORITA", "CYNDAQUIL", "TOTODILE"])
@pytest.mark.parametrize("prerequisite", [False, True], ids=["not-ready", "ready"])
def test_phase_4_graphics_survive_menu_and_continue(
    repo_root, tmp_path, phase_4_constants, implemented_gifts, species_name, prerequisite
) -> None:
    scenario = implemented_gifts[species_name]
    limit = scenario["max_frames_per_step"]
    with loaded_phase_4_checkpoint(
        repo_root, tmp_path / "initial", phase_4_constants, scenario,
        prerequisite=prerequisite,
    ) as session:
        slots = _assert_gift_graphics(session, phase_4_constants, scenario)
        _open_and_close_options(session, limit)
        assert _assert_gift_graphics(session, phase_4_constants, scenario) == slots
        if species_name != "CYNDAQUIL" or prerequisite:
            interact_with_gift(session, scenario, accept=False if prerequisite else None)
            assert _assert_gift_graphics(session, phase_4_constants, scenario) == slots
        save_game_from_overworld(session, limit)
        pending = dump_battery_ram(session, tmp_path / "pending.sav")

    with loaded_phase_4_saved_game(
        repo_root, tmp_path / "continue", phase_4_constants, scenario, pending,
    ) as session:
        assert _assert_gift_graphics(session, phase_4_constants, scenario) == slots
        _open_and_close_options(session, limit)
        assert _assert_gift_graphics(session, phase_4_constants, scenario) == slots


def test_chikorita_requires_cut_and_decline_remains_retryable(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    chikorita: dict,
) -> None:
    completion = phase_4_constants[chikorita["completion_event"]]
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "not-ready",
        phase_4_constants,
        chikorita,
        prerequisite=False,
    ) as session:
        before = read_progress(session)
        yes_no_count = session.hook_history.count("_YesNoBox")
        assert interact_with_gift(session, chikorita, accept=None) is None
        assert session.hook_history.count("_YesNoBox") == yes_no_count
        assert not event_is_set(session, completion)
        assert read_progress(session) == before

    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "decline",
        phase_4_constants,
        chikorita,
        prerequisite=True,
    ) as session:
        assert interact_with_gift(session, chikorita, accept=False) is None
        assert not event_is_set(session, completion)
        assert read_progress(session).party.count == 0
        assert interact_with_gift(session, chikorita, accept=False) is None
        assert session.script_history.count(chikorita["script"]) == 2


@pytest.mark.parametrize("species_name", ["CHIKORITA", "CYNDAQUIL", "TOTODILE"])
@pytest.mark.parametrize("destination", ["party", "current-box"])
def test_phase_4_party_and_box_delivery_finalize_once(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    implemented_gifts: dict[str, dict],
    species_name: str,
    destination: str,
) -> None:
    scenario = implemented_gifts[species_name]
    completion = phase_4_constants[scenario["completion_event"]]
    species = phase_4_constants[scenario["species"]]
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path,
        phase_4_constants,
        scenario,
        prerequisite=True,
    ) as session:
        if destination == "current-box":
            set_party_full(
                session,
                phase_4_constants["EEVEE"],
                phase_4_constants["PARTY_LENGTH"],
            )
        expected_outcome = 0 if destination == "party" else 1
        assert (
            interact_with_gift(session, scenario, accept=True)
            == expected_outcome
        )
        progress = read_progress(session)
        assert event_is_set(session, completion)
        assert progress.owns(species)
        if destination == "party":
            assert progress.party.species == (species,)
            assert session.read_symbol("wPartyMon1Level") == scenario["level"]
            assert session.read_symbol("wPartyMon1Item") == phase_4_constants["LUCKY_EGG"]
            assert progress.current_box.count == 0
        else:
            assert progress.current_box.species == (species,)
            assert session.read_symbol("sBoxMon1Level") == scenario["level"]
            assert session.read_symbol("sBoxMon1Item") == phase_4_constants["LUCKY_EGG"]

        if species_name == "CYNDAQUIL":
            cross_map_warp(session, phase_4_constants, (7, 14), "down",
                           "BURNED_TOWER_1F", scenario["max_frames_per_step"])
            cross_map_warp(session, phase_4_constants, (10, 10), "up",
                           "BURNED_TOWER_B1F", scenario["max_frames_per_step"])
            place_player(session, scenario["start"]["x"], scenario["start"]["y"])
            session.tick(30)
            assert_gift_absent(session, phase_4_constants, scenario)
            assert read_progress(session).party == progress.party
            assert read_progress(session).current_box == progress.current_box


@pytest.mark.parametrize("species_name", ["CHIKORITA", "CYNDAQUIL", "TOTODILE"])
def test_phase_4_full_storage_is_atomic_and_retryable(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    implemented_gifts: dict[str, dict],
    species_name: str,
) -> None:
    scenario = implemented_gifts[species_name]
    completion = phase_4_constants[scenario["completion_event"]]
    species = phase_4_constants[scenario["species"]]
    filler = phase_4_constants["EEVEE"]
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path,
        phase_4_constants,
        scenario,
        prerequisite=True,
    ) as session:
        set_party_full(session, filler, phase_4_constants["PARTY_LENGTH"])
        set_current_box_full(session, filler, phase_4_constants["MONS_PER_BOX"])
        before = read_progress(session)
        held_before = _held_items(session, phase_4_constants)
        assert interact_with_gift(session, scenario, accept=True) == 2
        assert not event_is_set(session, completion)
        assert read_progress(session) == before
        assert _held_items(session, phase_4_constants) == held_before

        clear_current_box(session)
        assert interact_with_gift(session, scenario, accept=True) == 1
        assert event_is_set(session, completion)
        assert read_progress(session).current_box.species == (species,)
        assert session.read_symbol("sBoxMon1Item") == phase_4_constants["LUCKY_EGG"]


@pytest.mark.parametrize("species_name", ["CHIKORITA", "CYNDAQUIL", "TOTODILE"])
@pytest.mark.parametrize("fresh_map", [False, True], ids=["continue", "fresh-map"])
@pytest.mark.parametrize("destination", ["party", "current-box"])
def test_phase_4_completion_survives_continue_and_fresh_map_load(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    implemented_gifts: dict[str, dict],
    species_name: str,
    fresh_map: bool,
    destination: str,
) -> None:
    scenario = implemented_gifts[species_name]
    completion = phase_4_constants[scenario["completion_event"]]
    species = phase_4_constants[scenario["species"]]
    item_label = "wPartyMon1Item" if destination == "party" else "sBoxMon1Item"
    expected_outcome = 0 if destination == "party" else 1
    persisted = tmp_path / "persisted.sav"
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "initial",
        phase_4_constants,
        scenario,
        prerequisite=True,
    ) as session:
        slots = _assert_gift_graphics(session, phase_4_constants, scenario)
        if destination == "current-box":
            set_party_full(
                session, phase_4_constants["EEVEE"], phase_4_constants["PARTY_LENGTH"]
            )
        assert interact_with_gift(session, scenario, accept=True) == expected_outcome
        assert session.read_symbol(item_label) == phase_4_constants["LUCKY_EGG"]
        progress = read_progress(session)
        delivered = progress.party if destination == "party" else progress.current_box
        assert delivered.species == (species,)
        held_items = _held_items(session, phase_4_constants)
        _open_and_close_options(session, scenario["max_frames_per_step"])
        assert _assert_gift_graphics(session, phase_4_constants, scenario) == slots
        save_game_from_overworld(session, scenario["max_frames_per_step"])
        dump_battery_ram(session, persisted)

    with loaded_phase_4_saved_game(
        repo_root,
        tmp_path / "reload",
        phase_4_constants,
        scenario,
        persisted,
        fresh_map=fresh_map,
    ) as session:
        assert event_is_set(session, completion)
        assert read_progress(session) == progress
        assert session.read_symbol(item_label) == phase_4_constants["LUCKY_EGG"]
        for other in implemented_gifts.values():
            if other is not scenario:
                assert not event_is_set(
                    session, phase_4_constants[other["completion_event"]]
                )
        assert_gift_absent(session, phase_4_constants, scenario)
        assert read_progress(session) == progress
        assert _held_items(session, phase_4_constants) == held_items
        _open_and_close_options(session, scenario["max_frames_per_step"])
        assert _assert_gift_graphics(session, phase_4_constants, scenario) == slots


def test_cyndaquil_script_refuses_a_completed_gift_even_if_still_visible(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    cyndaquil: dict,
) -> None:
    with loaded_phase_4_checkpoint(
        repo_root, tmp_path, phase_4_constants, cyndaquil, prerequisite=True
    ) as session:
        assert_completed_gift_is_inert(session, phase_4_constants, cyndaquil)


def test_cyndaquil_is_hidden_before_release_and_after_completion(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    cyndaquil: dict,
) -> None:
    completion = phase_4_constants[cyndaquil["completion_event"]]
    for label, completed in (("before-release", False), ("completed", True)):
        with loaded_phase_4_checkpoint(
            repo_root,
            tmp_path / label,
            phase_4_constants,
            cyndaquil,
            prerequisite=completed,
            completed=completed,
        ) as session:
            assert_gift_absent(session, phase_4_constants, cyndaquil)
            assert event_is_set(session, completion) is completed


def test_cyndaquil_appears_in_release_scene_and_restores_while_pending(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    cyndaquil: dict,
) -> None:
    released = phase_4_constants[cyndaquil["prerequisite_event"]]
    completion = phase_4_constants[cyndaquil["completion_event"]]
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "same-scene",
        phase_4_constants,
        cyndaquil,
        prerequisite=False,
    ) as session:
        place_player(session, 10, 7)
        save_game_from_overworld(session, cyndaquil["max_frames_per_step"])
        before_release = dump_battery_ram(session, tmp_path / "before-release.sav")

    # The manual playtest starts with native Continue while Cyndaquil is hidden.
    with loaded_phase_4_saved_game(
        repo_root, tmp_path / "continue-before-release", phase_4_constants,
        cyndaquil, before_release,
    ) as session:
        slots = _assert_gift_graphics(session, phase_4_constants, cyndaquil)
        session.enable_script_tracing()
        walk_steps(session, "up", "wYCoord", -1, 1, cyndaquil["max_frames_per_step"])
        session.wait_for_script("ReleaseTheBeasts", cyndaquil["max_frames_per_step"])
        session.wait_until(
            lambda current: event_is_set(current, released),
            cyndaquil["max_frames_per_step"],
            "legendary beasts to be released",
        )
        wait_for_idle(session, cyndaquil["max_frames_per_step"])
        assert not event_is_set(session, completion)
        assert session.read_symbol("wRoamMon1Species") == phase_4_constants["RAIKOU"]
        assert session.read_symbol("wRoamMon2Species") == phase_4_constants["ENTEI"]
        assert not event_is_set(
            session, phase_4_constants["EVENT_SAW_SUICUNE_AT_CIANWOOD_CITY"]
        )
        assert _assert_gift_graphics(session, phase_4_constants, cyndaquil) == slots
        walk_steps(session, "down", "wYCoord", 1, 5, cyndaquil["max_frames_per_step"])
        _open_and_close_options(session, cyndaquil["max_frames_per_step"])
        assert _assert_gift_graphics(session, phase_4_constants, cyndaquil) == slots
        assert session.read_symbol("wObject1Sprite") == phase_4_constants["SPRITE_SUPER_NERD"]
        _assert_loaded_graphics(
            session, phase_4_constants, phase_4_constants["SPRITE_SUPER_NERD"],
            "SuperNerdSpriteGFX", 12,
        )
        walk_steps(session, "up", "wYCoord", -1, 5, cyndaquil["max_frames_per_step"])
        walk_steps(session, "up", "wYCoord", -1, 1, cyndaquil["max_frames_per_step"])
        assert interact_with_gift(session, cyndaquil, accept=False) is None
        save_game_from_overworld(session, cyndaquil["max_frames_per_step"])
        pending = dump_battery_ram(session, tmp_path / "pending.sav")

    with loaded_phase_4_saved_game(
        repo_root,
        tmp_path / "reload-pending",
        phase_4_constants,
        cyndaquil,
        pending,
    ) as session:
        assert _assert_gift_graphics(session, phase_4_constants, cyndaquil) == slots
        assert interact_with_gift(session, cyndaquil, accept=False) is None
        assert not event_is_set(session, completion)
        assert interact_with_gift(session, cyndaquil, accept=False) is None


def test_totodile_clue_and_secretpotion_paths_preserve_story_state(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    totodile: dict,
) -> None:
    completion = phase_4_constants[totodile["completion_event"]]
    jasmine = phase_4_constants["EVENT_JASMINE_RETURNED_TO_GYM"]
    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "not-ready",
        phase_4_constants,
        totodile,
        prerequisite=False,
    ) as session:
        before = read_progress(session)
        yes_no_count = session.hook_history.count("_YesNoBox")
        assert interact_with_gift(session, totodile, accept=None) is None
        assert session.hook_history.count("_YesNoBox") == yes_no_count
        assert not event_is_set(session, completion)
        assert read_progress(session) == before

    with loaded_phase_4_checkpoint(
        repo_root,
        tmp_path / "with-potion",
        phase_4_constants,
        totodile,
        prerequisite=True,
    ) as session:
        secretpotion = phase_4_constants["SECRETPOTION"]
        session.write_symbol("wNumKeyItems", 1)
        session.write_symbol_bytes("wKeyItems", bytes([secretpotion, 0xFF]))
        before_inventory = read_progress(session).inventory
        jasmine_before = event_is_set(session, jasmine)
        assert interact_with_gift(session, totodile, accept=True) == 0
        assert event_is_set(session, completion)
        assert read_progress(session).inventory == before_inventory
        assert event_is_set(session, jasmine) is jasmine_before


def test_all_three_johto_starters_are_obtainable_on_one_save(
    repo_root: Path,
    tmp_path: Path,
    phase_4_constants: dict[str, int],
    implemented_gifts: dict[str, dict],
) -> None:
    ordered = [
        implemented_gifts[name]
        for name in ("CHIKORITA", "CYNDAQUIL", "TOTODILE")
    ]
    source_save: Path | None = None
    expected_species: list[int] = []
    for index, scenario in enumerate(ordered):
        if source_save is None:
            context = loaded_phase_4_checkpoint(
                repo_root,
                tmp_path / f"step-{index}",
                phase_4_constants,
                scenario,
                prerequisite=True,
            )
        else:
            retargeted = retarget_phase_4_save(
                repo_root,
                source_save,
                tmp_path / f"retargeted-{index}.sav",
                phase_4_constants,
                scenario,
            )
            context = loaded_phase_4_saved_game(
                repo_root,
                tmp_path / f"step-{index}",
                phase_4_constants,
                scenario,
                retargeted,
                fresh_map=True,
            )
        with context as session:
            assert interact_with_gift(session, scenario, accept=True) == 0
            expected_species.append(phase_4_constants[scenario["species"]])
            assert read_progress(session).party.species == tuple(expected_species)
            for completed in ordered[: index + 1]:
                assert event_is_set(
                    session,
                    phase_4_constants[completed["completion_event"]],
                )
            if index < len(ordered) - 1:
                save_game_from_overworld(session, scenario["max_frames_per_step"])
                source_save = dump_battery_ram(
                    session, tmp_path / f"completed-{index}.sav"
                )
