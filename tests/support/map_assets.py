from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Mapping, Sequence

from tests.support.map_model import MapDimensions, MapEvent, MapValidationError


_BLOCK_LABEL_RE = re.compile(r"^([A-Za-z0-9_]+)_Blocks:")
_INCBIN_RE = re.compile(r'^\s*INCBIN\s+"([^"]+\.blk)"')
_MAP_RE = re.compile(r"^\s*map\s+([A-Za-z0-9_]+)\s*,\s*(TILESET_[A-Z0-9_]+)\s*,")
_COLLISION_RE = re.compile(r"^\s*tilecoll\s+([^;]+)")


@dataclass(frozen=True)
class InteractionContract:
    contract_id: str
    map_name: str
    coordinate: tuple[int, int]
    collision: str
    event_type: str
    event_direction: str
    script: str
    variant: str


@dataclass(frozen=True)
class VisibilityContract:
    map_name: str
    declared_objects: int
    reason: str


def _normalized(name: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", name.upper())


def parse_block_paths(text: str) -> dict[str, str]:
    pending: list[str] = []
    paths: dict[str, str] = {}
    for number, raw_line in enumerate(text.splitlines(), start=1):
        code = raw_line.split(";", 1)[0].rstrip()
        label = _BLOCK_LABEL_RE.match(code)
        if label:
            pending.append(label.group(1))
            continue
        incbin = _INCBIN_RE.match(code)
        if incbin:
            if not pending:
                raise MapValidationError(
                    f"data/maps/blocks.asm:{number}: block INCBIN has no labels"
                )
            for name in pending:
                if name in paths:
                    raise MapValidationError(f"duplicate block label {name}_Blocks")
                paths[name] = incbin.group(1)
            pending.clear()
            continue
        if code.strip() and pending:
            raise MapValidationError(
                f"data/maps/blocks.asm:{number}: block aliases "
                f"{', '.join(pending)} do not resolve directly to an INCBIN"
            )
    if pending:
        raise MapValidationError(
            "unresolved block aliases at end of file: " + ", ".join(pending)
        )
    return paths


def block_paths_for_maps(
    dimensions: Mapping[str, MapDimensions], block_paths: Mapping[str, str]
) -> dict[str, str]:
    by_normalized = {_normalized(name): path for name, path in block_paths.items()}
    resolved: dict[str, str] = {}
    for map_name in dimensions:
        path = by_normalized.get(_normalized(map_name))
        if path is None:
            raise MapValidationError(f"{map_name} has no resolved block label")
        resolved[map_name] = path
    return resolved


def validate_block_sizes(
    repo_root: Path,
    dimensions: Mapping[str, MapDimensions],
    resolved_paths: Mapping[str, str],
) -> None:
    failures: list[str] = []
    for map_name, size in dimensions.items():
        path = repo_root / resolved_paths[map_name]
        if not path.is_file():
            failures.append(f"{map_name} block file does not exist: {path}")
            continue
        actual = path.stat().st_size
        expected = size.width_blocks * size.height_blocks
        if actual != expected:
            failures.append(
                f"{map_name} block file {path} is {actual} bytes; expected "
                f"{size.width_blocks} * {size.height_blocks} = {expected}"
            )
    if failures:
        raise MapValidationError("\n".join(failures))


def parse_map_tilesets(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        match = _MAP_RE.match(raw_line.split(";", 1)[0])
        if match:
            name, tileset = match.groups()
            result[_normalized(name)] = tileset
    return result


def parse_collision_rows(text: str) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for number, raw_line in enumerate(text.splitlines(), start=1):
        match = _COLLISION_RE.match(raw_line)
        if match is None:
            continue
        values = tuple(value.strip() for value in match.group(1).split(","))
        if len(values) != 4:
            raise MapValidationError(
                f"collision row {number} has {len(values)} entries, expected 4"
            )
        rows.append(values)  # type: ignore[arg-type]
    return rows


def _collision_path(repo_root: Path, tileset: str) -> Path:
    collision_name = tileset.removeprefix("TILESET_").lower()
    if collision_name == "0":
        collision_name = "johto"
    return repo_root / f"data/tilesets/{collision_name}_collision.asm"


def validate_block_indices(
    repo_root: Path,
    dimensions: Mapping[str, MapDimensions],
    resolved_paths: Mapping[str, str],
    map_tilesets: Mapping[str, str],
) -> None:
    collision_counts: dict[str, int] = {}
    failures: list[str] = []
    for map_name in dimensions:
        tileset = map_tilesets.get(_normalized(map_name))
        if tileset is None:
            failures.append(f"{map_name} has no tileset declaration")
            continue
        if tileset not in collision_counts:
            collision_path = _collision_path(repo_root, tileset)
            if not collision_path.is_file():
                failures.append(
                    f"{map_name} tileset collision file does not exist: "
                    f"{collision_path}"
                )
                continue
            collision_counts[tileset] = len(
                parse_collision_rows(collision_path.read_text())
            )
        row_count = collision_counts[tileset]
        for offset, block_id in enumerate(
            (repo_root / resolved_paths[map_name]).read_bytes()
        ):
            if block_id >= row_count:
                failures.append(
                    f"{map_name} block byte {offset} is ${block_id:02x}; "
                    f"{tileset} only defines blocks 0..{row_count - 1}"
                )
    if failures:
        raise MapValidationError("\n".join(failures))


def collision_at(
    repo_root: Path,
    map_name: str,
    coordinate: tuple[int, int],
    dimensions: Mapping[str, MapDimensions],
    resolved_paths: Mapping[str, str],
    map_tilesets: Mapping[str, str],
) -> str:
    size = dimensions[map_name]
    x, y = coordinate
    if not (0 <= x < size.width and 0 <= y < size.height):
        raise MapValidationError(f"{map_name} coordinate {coordinate} is out of bounds")
    blocks = (repo_root / resolved_paths[map_name]).read_bytes()
    block_index = (y // 2) * size.width_blocks + (x // 2)
    block_id = blocks[block_index]
    tileset = map_tilesets.get(_normalized(map_name))
    if tileset is None:
        raise MapValidationError(f"{map_name} has no tileset declaration")
    collision_path = _collision_path(repo_root, tileset)
    if not collision_path.is_file():
        raise MapValidationError(
            f"{map_name} tileset collision file does not exist: {collision_path}"
        )
    rows = parse_collision_rows(collision_path.read_text())
    if block_id >= len(rows):
        raise MapValidationError(
            f"{map_name} block ${block_id:02x} at {coordinate} exceeds "
            f"{tileset} collision rows 0..{len(rows) - 1}"
        )
    quadrant = (y % 2) * 2 + (x % 2)
    return rows[block_id][quadrant]


def load_interaction_contracts(path: Path) -> list[InteractionContract]:
    records = json.loads(path.read_text())
    return [
        InteractionContract(
            **{**record, "coordinate": tuple(record["coordinate"])}
        )
        for record in records
    ]


def validate_interaction_contracts(
    repo_root: Path,
    contracts: Sequence[InteractionContract],
    events: Sequence[MapEvent],
    dimensions: Mapping[str, MapDimensions],
    resolved_paths: Mapping[str, str],
    map_tilesets: Mapping[str, str],
) -> None:
    failures: list[str] = []
    for contract in contracts:
        actual_collision = collision_at(
            repo_root,
            contract.map_name,
            contract.coordinate,
            dimensions,
            resolved_paths,
            map_tilesets,
        )
        if actual_collision != contract.collision.removeprefix("COLL_"):
            failures.append(
                f"{contract.contract_id}: {contract.map_name} at "
                f"{contract.coordinate} collision is COLL_{actual_collision}, "
                f"expected {contract.collision}"
            )
        matching = [
            event
            for event in events
            if event.map_name == contract.map_name
            and event.event_type == contract.event_type
            and (event.x, event.y) == contract.coordinate
            and event.args[2] == contract.event_direction
            and event.identity == contract.script
        ]
        if len(matching) != 1:
            failures.append(
                f"{contract.contract_id}: expected exactly one {contract.event_type} "
                f"at {contract.coordinate} with {contract.event_direction}, "
                f"{contract.script}; found {len(matching)}"
            )
    if failures:
        raise MapValidationError("\n".join(failures))


def load_visibility_contracts(path: Path) -> list[VisibilityContract]:
    return [VisibilityContract(**record) for record in json.loads(path.read_text())]


def validate_event_capacities(
    events: Sequence[MapEvent],
    visibility_contracts: Sequence[VisibilityContract],
) -> None:
    counts: dict[tuple[str, str], int] = {}
    for event in events:
        key = (event.map_name, event.event_type)
        counts[key] = counts.get(key, 0) + 1
    failures: list[str] = []
    for (map_name, event_type), count in counts.items():
        if count > 255:
            failures.append(f"{map_name} has {count} {event_type} records; max is 255")
        if event_type == "object_event" and count > 16:
            failures.append(f"{map_name} has {count} object events; NUM_OBJECTS is 16")

    actual_over_visible_limit = {
        map_name: count
        for (map_name, event_type), count in counts.items()
        if event_type == "object_event" and count > 12
    }
    contracts = {contract.map_name: contract for contract in visibility_contracts}
    for map_name, count in actual_over_visible_limit.items():
        contract = contracts.get(map_name)
        if contract is None:
            failures.append(
                f"{map_name} declares {count} objects, more than "
                "NUM_OBJECT_STRUCTS - 1 (12), without a visibility contract"
            )
        elif contract.declared_objects != count:
            failures.append(
                f"{map_name} visibility contract records "
                f"{contract.declared_objects} objects, actual count is {count}"
            )
    for map_name in contracts.keys() - actual_over_visible_limit.keys():
        failures.append(f"{map_name} visibility contract is stale")
    if failures:
        raise MapValidationError("\n".join(failures))
