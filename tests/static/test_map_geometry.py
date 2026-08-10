from pathlib import Path

import pytest

from tests.support.map_model import (
    EventException,
    MapDimensions,
    MapSource,
    MapValidationError,
    load_event_exceptions,
    map_sources_from_repository,
    parse_map_dimensions,
    validate_map_events,
)


pytestmark = pytest.mark.static


def test_all_literal_map_events_are_in_bounds_and_warps_resolve(
    repo_root: Path,
) -> None:
    dimensions = parse_map_dimensions(
        (repo_root / "constants/map_constants.asm").read_text()
    )
    sources = map_sources_from_repository(repo_root)
    exceptions = load_event_exceptions(
        repo_root / "tests/contracts/map_event_exceptions.json"
    )

    events = validate_map_events(dimensions, sources, exceptions)

    assert len(dimensions) == len(sources)
    assert len(events) > 3_000


@pytest.mark.parametrize(
    ("event_type", "coordinate", "expected"),
    [
        ("bg_event", "8, 1", "valid X range is 0..7"),
        ("bg_event", "1, 6", "valid Y range is 0..5"),
        ("coord_event", "-1, 1", "coordinate (-1, 1)"),
    ],
)
def test_invalid_literal_coordinates_report_the_contract(
    event_type: str, coordinate: str, expected: str
) -> None:
    suffix = (
        "BGEVENT_READ, BrokenScript"
        if event_type == "bg_event"
        else "SCENE_ALWAYS, BrokenScript"
    )
    source = MapSource(
        "SYNTHETIC_ROOM",
        "maps/SyntheticRoom.asm",
        f"{event_type} {coordinate}, {suffix}\n",
    )

    with pytest.raises(MapValidationError) as error:
        validate_map_events(
            {"SYNTHETIC_ROOM": MapDimensions("SYNTHETIC_ROOM", 4, 3)},
            [source],
        )

    message = str(error.value)
    assert "SYNTHETIC_ROOM" in message
    assert event_type in message
    assert "BrokenScript" in message
    assert expected in message


def test_invalid_destination_warp_index_fails() -> None:
    sources = [
        MapSource(
            "START_ROOM",
            "maps/StartRoom.asm",
            "warp_event 1, 1, DESTINATION_ROOM, 2\n",
        ),
        MapSource(
            "DESTINATION_ROOM",
            "maps/DestinationRoom.asm",
            "warp_event 1, 1, START_ROOM, 1\n",
        ),
    ]
    dimensions = {
        name: MapDimensions(name, 2, 2)
        for name in ("START_ROOM", "DESTINATION_ROOM")
    }

    with pytest.raises(MapValidationError, match="valid indices are 1..1"):
        validate_map_events(dimensions, sources)


def test_inactive_conditional_event_is_not_validated() -> None:
    source = MapSource(
        "SYNTHETIC_ROOM",
        "maps/SyntheticRoom.asm",
        """
if DEF(_CRYSTALLEGENDS)
  bg_event 1, 1, BGEVENT_READ, ActiveScript
else
  bg_event 99, 99, BGEVENT_READ, InactiveScript
endc
""",
    )
    events = validate_map_events(
        {"SYNTHETIC_ROOM": MapDimensions("SYNTHETIC_ROOM", 2, 2)},
        [source],
    )
    assert [event.identity for event in events] == ["ActiveScript"]


def test_stale_exception_fails() -> None:
    source = MapSource(
        "SYNTHETIC_ROOM",
        "maps/SyntheticRoom.asm",
        "bg_event 1, 1, BGEVENT_READ, ValidScript\n",
    )
    exception = EventException(
        exception_id="stale",
        map_name="SYNTHETIC_ROOM",
        event_type="bg_event",
        x=9,
        y=9,
        identity="OldScript",
        reason="Synthetic stale exception",
    )

    with pytest.raises(MapValidationError, match="matched 0 events"):
        validate_map_events(
            {"SYNTHETIC_ROOM": MapDimensions("SYNTHETIC_ROOM", 2, 2)},
            [source],
            [exception],
        )
