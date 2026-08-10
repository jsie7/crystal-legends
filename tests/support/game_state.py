from __future__ import annotations

from dataclasses import dataclass

from tests.support.pyboy_session import PyBoySession


@dataclass(frozen=True)
class PartyState:
    species: tuple[int, ...]

    @property
    def count(self) -> int:
        return len(self.species)


@dataclass(frozen=True)
class BoxState:
    index: int
    species: tuple[int, ...]

    @property
    def count(self) -> int:
        return len(self.species)


@dataclass(frozen=True)
class InventoryState:
    items: tuple[tuple[int, int], ...]
    key_items: tuple[int, ...]
    balls: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class ProgressState:
    party: PartyState
    current_box: BoxState
    inventory: InventoryState
    money: int
    pokedex_caught: bytes
    pokedex_seen: bytes

    def owns(self, species: int) -> bool:
        if species < 1 or species > len(self.pokedex_caught) * 8:
            raise ValueError(f"species {species} is outside the Pokédex bitfield")
        index = species - 1
        return bool(self.pokedex_caught[index // 8] & (1 << (index % 8)))


def read_party(session: PyBoySession) -> PartyState:
    count = session.read_symbol("wPartyCount")
    species = session.read_symbol_bytes("wPartySpecies", count) if count else b""
    return PartyState(tuple(species))


def read_current_box(session: PyBoySession) -> BoxState:
    count = session.read_symbol("sBoxCount")
    species = session.read_symbol_bytes("sBoxSpecies", count) if count else b""
    return BoxState(
        index=session.read_symbol("wCurBox"),
        species=tuple(species),
    )


def _read_pairs(
    session: PyBoySession, count_label: str, entries_label: str
) -> tuple[tuple[int, int], ...]:
    count = session.read_symbol(count_label)
    values = session.read_symbol_bytes(entries_label, count * 2) if count else b""
    return tuple((values[index], values[index + 1]) for index in range(0, len(values), 2))


def read_inventory(session: PyBoySession) -> InventoryState:
    key_count = session.read_symbol("wNumKeyItems")
    key_items = (
        session.read_symbol_bytes("wKeyItems", key_count) if key_count else b""
    )
    return InventoryState(
        items=_read_pairs(session, "wNumItems", "wItems"),
        key_items=tuple(key_items),
        balls=_read_pairs(session, "wNumBalls", "wBalls"),
    )


def read_progress(session: PyBoySession) -> ProgressState:
    return ProgressState(
        party=read_party(session),
        current_box=read_current_box(session),
        inventory=read_inventory(session),
        money=int.from_bytes(session.read_symbol_bytes("wMoney", 3), "big"),
        pokedex_caught=session.read_symbol_bytes("wPokedexCaught", 32),
        pokedex_seen=session.read_symbol_bytes("wPokedexSeen", 32),
    )
