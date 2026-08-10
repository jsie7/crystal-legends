from pathlib import Path

import pytest

from tests.support.map_assets import (
    block_paths_for_maps,
    collision_at,
    load_interaction_contracts,
    load_visibility_contracts,
    parse_block_paths,
    parse_map_tilesets,
    validate_block_indices,
    validate_block_sizes,
    validate_event_capacities,
    validate_interaction_contracts,
)
from tests.support.map_model import (
    MapDimensions,
    MapValidationError,
    load_event_exceptions,
    map_sources_from_repository,
    parse_events,
    parse_map_dimensions,
    validate_map_events,
)


pytestmark = pytest.mark.static


@pytest.fixture(scope="module")
def map_data(repo_root: Path):
    dimensions = parse_map_dimensions(
        (repo_root / "constants/map_constants.asm").read_text()
    )
    sources = map_sources_from_repository(repo_root)
    events = validate_map_events(
        dimensions,
        sources,
        load_event_exceptions(repo_root / "tests/contracts/map_event_exceptions.json"),
    )
    block_paths = block_paths_for_maps(
        dimensions,
        parse_block_paths((repo_root / "data/maps/blocks.asm").read_text()),
    )
    tilesets = parse_map_tilesets((repo_root / "data/maps/maps.asm").read_text())
    return dimensions, events, block_paths, tilesets


def test_all_map_block_aliases_resolve_with_exact_sizes(
    repo_root: Path, map_data
) -> None:
    dimensions, _, block_paths, _ = map_data
    validate_block_sizes(repo_root, dimensions, block_paths)


def test_all_map_block_indices_exist_in_their_tilesets(
    repo_root: Path, map_data
) -> None:
    dimensions, _, block_paths, tilesets = map_data
    validate_block_indices(repo_root, dimensions, block_paths, tilesets)


def test_all_event_counts_fit_engine_capacities(repo_root: Path, map_data) -> None:
    _, events, _, _ = map_data
    contracts = load_visibility_contracts(
        repo_root / "tests/contracts/object_visibility_contracts.json"
    )
    validate_event_capacities(events, contracts)


def test_bedroom_tv_interaction_contract(repo_root: Path, map_data) -> None:
    dimensions, events, block_paths, tilesets = map_data
    contracts = load_interaction_contracts(
        repo_root / "tests/contracts/map_interactions.json"
    )
    validate_interaction_contracts(
        repo_root,
        contracts,
        events,
        dimensions,
        block_paths,
        tilesets,
    )
    assert collision_at(
        repo_root,
        "PLAYERS_HOUSE_2F",
        (4, 1),
        dimensions,
        block_paths,
        tilesets,
    ) == "TV"


def test_unresolved_block_alias_fails() -> None:
    with pytest.raises(MapValidationError, match="do not resolve"):
        parse_block_paths("ExampleRoom_Blocks:\n\tdb 1\n")


def test_wrong_block_size_fails(tmp_path: Path) -> None:
    block = tmp_path / "room.blk"
    block.write_bytes(b"\x00\x01")
    dimensions = {"ROOM": MapDimensions("ROOM", 2, 2)}
    with pytest.raises(MapValidationError, match=r"expected 2 \* 2 = 4"):
        validate_block_sizes(tmp_path, dimensions, {"ROOM": "room.blk"})


def test_visibility_contract_must_follow_object_count() -> None:
    source = map_sources_from_text(
        "".join(
            f"object_event {index}, 0, SPRITE_NURSE, SPRITEMOVEDATA_STILL, "
            f"0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, Script{index}, -1\n"
            for index in range(13)
        )
    )
    events = parse_events(source)
    with pytest.raises(MapValidationError, match="without a visibility contract"):
        validate_event_capacities(events, [])


def map_sources_from_text(text: str):
    from tests.support.map_model import MapSource

    return MapSource("ROOM", "maps/Room.asm", text)
