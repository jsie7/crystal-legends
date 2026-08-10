from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Iterable, Mapping, Sequence

from tests.support.asm_conditions import SourceLine, active_lines


CRYSTAL_LEGENDS_DEFINITIONS = frozenset({"_CRYSTAL11", "_CRYSTALLEGENDS"})
_MAP_CONST_RE = re.compile(
    r"^\s*map_const\s+([A-Z0-9_]+)\s*,\s*(\d+)\s*,\s*(\d+)"
)
_INCLUDE_RE = re.compile(r'^\s*INCLUDE\s+"(maps/[^"]+\.asm)"')
_EVENT_RE = re.compile(
    r"^\s*(warp_event|coord_event|bg_event|object_event)\s+(.+?)\s*$"
)


class MapValidationError(AssertionError):
    pass


@dataclass(frozen=True)
class MapDimensions:
    name: str
    width_blocks: int
    height_blocks: int

    @property
    def width(self) -> int:
        return self.width_blocks * 2

    @property
    def height(self) -> int:
        return self.height_blocks * 2


@dataclass(frozen=True)
class MapEvent:
    map_name: str
    event_type: str
    args: tuple[str, ...]
    source: str
    line: int

    @property
    def x(self) -> int:
        return _literal_int(self.args[0], self)

    @property
    def y(self) -> int:
        return _literal_int(self.args[1], self)

    @property
    def identity(self) -> str:
        if self.event_type == "object_event" and len(self.args) >= 12:
            return self.args[11]
        return self.args[-1]


@dataclass(frozen=True)
class MapSource:
    map_name: str
    source: str
    text: str


@dataclass(frozen=True)
class EventException:
    exception_id: str
    map_name: str
    event_type: str
    x: int
    y: int
    identity: str
    reason: str

    def matches(self, event: MapEvent) -> bool:
        return (
            self.map_name == event.map_name
            and self.event_type == event.event_type
            and self.x == event.x
            and self.y == event.y
            and self.identity == event.identity
        )


def _literal_int(value: str, event: MapEvent) -> int:
    token = value.strip()
    try:
        if token.startswith("$"):
            return int(token[1:], 16)
        return int(token, 0)
    except ValueError as error:
        raise MapValidationError(
            f"{event.source}:{event.line}: {event.map_name} {event.event_type} "
            f"uses non-literal coordinate {token!r}"
        ) from error


def _normalized_map_name(name: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", name.upper())


def parse_map_dimensions(text: str) -> dict[str, MapDimensions]:
    dimensions: dict[str, MapDimensions] = {}
    for line in text.splitlines():
        match = _MAP_CONST_RE.match(line.split(";", 1)[0])
        if match is None:
            continue
        name, width, height = match.groups()
        if name in dimensions:
            raise MapValidationError(f"duplicate map_const for {name}")
        dimensions[name] = MapDimensions(name, int(width), int(height))
    return dimensions


def map_sources_from_repository(repo_root: Path) -> list[MapSource]:
    scripts_path = repo_root / "data/maps/scripts.asm"
    include_lines = active_lines(
        scripts_path.read_text(), CRYSTAL_LEGENDS_DEFINITIONS
    )
    dimensions = parse_map_dimensions(
        (repo_root / "constants/map_constants.asm").read_text()
    )
    names_by_normalized = {
        _normalized_map_name(name): name for name in dimensions
    }
    sources: list[MapSource] = []
    seen: set[str] = set()

    for line in include_lines:
        match = _INCLUDE_RE.match(line.text)
        if match is None:
            continue
        relative = match.group(1)
        stem = Path(relative).stem
        source_text = (repo_root / relative).read_text()
        map_name = names_by_normalized.get(_normalized_map_name(stem))
        if map_name is None:
            if "_MapEvents:" not in source_text:
                continue
            raise MapValidationError(
                f"{scripts_path}:{line.number}: no map_const matches {relative}"
            )
        if map_name in seen:
            raise MapValidationError(f"duplicate map source include for {map_name}")
        seen.add(map_name)
        sources.append(
            MapSource(
                map_name=map_name,
                source=relative,
                text=source_text,
            )
        )

    missing = sorted(set(dimensions) - seen)
    if missing:
        raise MapValidationError(
            "map constants without active script includes: " + ", ".join(missing)
        )
    return sources


def parse_events(
    source: MapSource,
    definitions: Iterable[str] = CRYSTAL_LEGENDS_DEFINITIONS,
) -> list[MapEvent]:
    events: list[MapEvent] = []
    for line in active_lines(source.text, definitions):
        match = _EVENT_RE.match(line.text.split(";", 1)[0])
        if match is None:
            continue
        event_type, raw_args = match.groups()
        args = tuple(part.strip() for part in raw_args.split(","))
        minimum_args = 4 if event_type != "object_event" else 13
        if len(args) < minimum_args:
            raise MapValidationError(
                f"{source.source}:{line.number}: malformed {event_type}: {raw_args}"
            )
        events.append(
            MapEvent(
                map_name=source.map_name,
                event_type=event_type,
                args=args,
                source=source.source,
                line=line.number,
            )
        )
    return events


def load_event_exceptions(path: Path) -> list[EventException]:
    raw = json.loads(path.read_text())
    return [EventException(**record) for record in raw]


def validate_map_events(
    dimensions: Mapping[str, MapDimensions],
    sources: Sequence[MapSource],
    exceptions: Sequence[EventException] = (),
) -> list[MapEvent]:
    events = [event for source in sources for event in parse_events(source)]
    used_exceptions: Counter[str] = Counter()
    failures: list[str] = []

    events_by_map: dict[str, list[MapEvent]] = {
        source.map_name: [] for source in sources
    }
    for event in events:
        events_by_map[event.map_name].append(event)
        bounds = dimensions[event.map_name]
        if 0 <= event.x < bounds.width and 0 <= event.y < bounds.height:
            continue
        matching = [exception for exception in exceptions if exception.matches(event)]
        if matching:
            used_exceptions[matching[0].exception_id] += 1
            continue
        failures.append(
            f"{event.source}:{event.line}: {event.map_name} {event.event_type} "
            f"{event.identity} has coordinate ({event.x}, {event.y}); valid "
            f"X range is 0..{bounds.width - 1}, valid Y range is "
            f"0..{bounds.height - 1}"
        )

    for event in events:
        if event.event_type != "warp_event":
            continue
        destination = event.args[2]
        destination_event = _literal_int(event.args[3], event)
        if destination not in dimensions:
            failures.append(
                f"{event.source}:{event.line}: {event.map_name} warp destination "
                f"{destination} is not a declared map"
            )
            continue
        if destination_event == -1:
            # Elevators and a few engine-managed transitions fill this from
            # wBackupWarpNumber at runtime.
            continue
        warp_count = sum(
            candidate.event_type == "warp_event"
            for candidate in events_by_map.get(destination, ())
        )
        if not 1 <= destination_event <= warp_count:
            failures.append(
                f"{event.source}:{event.line}: {event.map_name} warp points to "
                f"{destination} warp {destination_event}, but valid indices are "
                f"1..{warp_count}"
            )

    for exception in exceptions:
        count = used_exceptions[exception.exception_id]
        if count != 1:
            failures.append(
                f"exception {exception.exception_id!r} matched {count} events; "
                "expected exactly one (remove stale or ambiguous exception)"
            )

    if failures:
        raise MapValidationError("\n".join(failures))
    return events
