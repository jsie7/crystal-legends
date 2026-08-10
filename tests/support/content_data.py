from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from tests.support.asm_conditions import active_lines


class ContentDataError(ValueError):
    pass


@dataclass(frozen=True)
class AcquisitionRow:
    dex: int
    species: str
    method: str
    location: str
    earliest: str
    availability: str
    renewable: str
    source: str
    source_paths: tuple[str, ...]


@dataclass(frozen=True)
class Evolution:
    method: str
    condition: str
    target: str
    extra_condition: str | None = None


@dataclass(frozen=True)
class EvolutionBlock:
    species: str
    evolutions: tuple[Evolution, ...]
    learnset: tuple[tuple[int, str], ...]


@dataclass(frozen=True)
class TrainerParty:
    group: str
    name: str
    trainer_type: str
    members: tuple[tuple[str, ...], ...]


_LEDGER_ROW = re.compile(r"^\|\s*(\d{3})\s*\|(.*)\|$")
_PATH = re.compile(r"`([^`]+)`")
_EVOLUTION_LABEL = re.compile(r"^([A-Za-z0-9]+)EvosAttacks:$")
_TRAINER_GROUP = re.compile(r"^([A-Za-z0-9]+Group):$")
_TRAINER_HEADER = re.compile(
    r'^db\s+"([^"]*)@",\s*(TRAINERTYPE_(?:NORMAL|MOVES|ITEM|ITEM_MOVES))$'
)


def _code(text: str) -> str:
    return text.split(";", 1)[0].strip()


def _db_values(text: str) -> list[str] | None:
    code = _code(text)
    if not code.startswith("db "):
        return None
    return [value.strip() for value in code[3:].split(",")]


def parse_acquisition_ledger(text: str) -> list[AcquisitionRow]:
    rows: list[AcquisitionRow] = []
    for line in text.splitlines():
        match = _LEDGER_ROW.match(line)
        if match is None:
            continue
        dex, remainder = match.groups()
        cells = [cell.strip() for cell in remainder.split("|")]
        if len(cells) != 7:
            raise ContentDataError(
                f"ledger row {dex} has {len(cells) + 1} columns, expected 8"
            )
        rows.append(
            AcquisitionRow(
                dex=int(dex),
                species=cells[0],
                method=cells[1],
                location=cells[2],
                earliest=cells[3],
                availability=cells[4],
                renewable=cells[5],
                source=cells[6],
                source_paths=tuple(_PATH.findall(cells[6])),
            )
        )
    return rows


def parse_evolution_blocks(text: str) -> list[EvolutionBlock]:
    lines = active_lines(text, {"_CRYSTAL11", "_CRYSTALLEGENDS"})
    blocks: list[EvolutionBlock] = []
    species: str | None = None
    evolutions: list[Evolution] = []
    learnset: list[tuple[int, str]] = []
    phase = "evolutions"

    def finish() -> None:
        nonlocal species, evolutions, learnset, phase
        if species is None:
            return
        if phase != "done":
            raise ContentDataError(f"{species} evolution block is not terminated")
        blocks.append(EvolutionBlock(species, tuple(evolutions), tuple(learnset)))
        species = None
        evolutions = []
        learnset = []
        phase = "evolutions"

    for source_line in lines:
        code = _code(source_line.text)
        label = _EVOLUTION_LABEL.fullmatch(code)
        if label:
            finish()
            species = label.group(1)
            continue
        if species is None:
            continue
        values = _db_values(source_line.text)
        if values is None:
            continue
        if values == ["0"]:
            if phase == "evolutions":
                phase = "learnset"
            elif phase == "learnset":
                phase = "done"
            else:
                raise ContentDataError(f"{species} has an extra terminator")
            continue
        if phase == "evolutions":
            method = values[0]
            expected_width = 4 if method == "EVOLVE_STAT" else 3
            if not method.startswith("EVOLVE_") or len(values) != expected_width:
                raise ContentDataError(
                    f"line {source_line.number}: malformed evolution {values}"
                )
            evolutions.append(
                Evolution(
                    method=method,
                    condition=values[1],
                    target=values[-1],
                    extra_condition=values[2] if expected_width == 4 else None,
                )
            )
        elif phase == "learnset":
            if len(values) != 2 or not values[0].isdigit():
                raise ContentDataError(
                    f"line {source_line.number}: malformed learnset row {values}"
                )
            learnset.append((int(values[0]), values[1]))
        else:
            raise ContentDataError(f"line {source_line.number}: data after block end")
    finish()
    return blocks


def parse_trainer_parties(text: str) -> list[TrainerParty]:
    lines = active_lines(text, {"_CRYSTAL11", "_CRYSTALLEGENDS"})
    parties: list[TrainerParty] = []
    group = ""
    name: str | None = None
    trainer_type = ""
    members: list[tuple[str, ...]] = []

    for source_line in lines:
        code = _code(source_line.text)
        group_match = _TRAINER_GROUP.fullmatch(code)
        if group_match:
            group = group_match.group(1)
            continue
        header_match = _TRAINER_HEADER.fullmatch(code)
        if header_match:
            if name is not None:
                raise ContentDataError(
                    f"line {source_line.number}: new trainer before prior terminator"
                )
            name, trainer_type = header_match.groups()
            members = []
            continue
        if name is None:
            continue
        values = _db_values(source_line.text)
        if values == ["-1"]:
            parties.append(TrainerParty(group, name, trainer_type, tuple(members)))
            name = None
            continue
        if values is not None:
            members.append(tuple(values))
    if name is not None:
        raise ContentDataError(f"unterminated trainer {group}/{name}")
    return parties


def pokemon_constant_names(text: str) -> set[str]:
    return {
        match.group(1)
        for line in text.splitlines()
        if (match := re.match(r"\s*const\s+([A-Z][A-Z0-9_]*)\b", line))
    }


def validate_wild_level_species_rows(
    paths: list[Path], pokemon_names: set[str]
) -> int:
    level_first = re.compile(r"^db\s+(\d+),\s*([A-Z][A-Z0-9_]*)\b")
    checked = 0
    failures: list[str] = []
    for path in paths:
        for source_line in active_lines(
            path.read_text(), {"_CRYSTAL11", "_CRYSTALLEGENDS"}
        ):
            match = level_first.match(_code(source_line.text))
            if match is None:
                continue
            level, species = match.groups()
            if species not in pokemon_names:
                continue
            checked += 1
            if not 1 <= int(level) <= 100:
                failures.append(f"{path}:{source_line.number}: invalid level {level}")
    if failures:
        raise ContentDataError("\n".join(failures))
    return checked
