"""Data models for the Astuce API (Rouen Métropole transit network)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Line:
    """A transit line (bus, metro, TEOR, FAST…)."""

    id: int
    number: str          # e.g. "F1", "METRO", "T2"
    name: str            # e.g. "Plaine de la Ronce <> Stade Diochon"
    transport_mode: str  # "Bus", "Metro", "TEOR", "FAST", "Taxi"
    network_name: str    # "Astuce"
    color: str           # hex color without '#', e.g. "E6007E"

    def __str__(self) -> str:
        return f"[{self.transport_mode}] {self.number} — {self.name}"

    @classmethod
    def from_api(cls, data: dict) -> "Line":
        return cls(
            id=data["id"],
            number=data["number"],
            name=data["name"],
            transport_mode=data.get("transportMode", ""),
            network_name=data.get("networkName", ""),
            color=data.get("color", ""),
        )


@dataclass
class Stop:
    """A physical stop on the network."""

    id: int
    code: str            # e.g. "HVR1"
    name: str            # e.g. "Hôtel de Ville"
    latitude: float
    longitude: float
    locality: str        # e.g. "Rouen"

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    @classmethod
    def from_api(cls, data: dict) -> "Stop":
        return cls(
            id=data["id"],
            code=data.get("code", ""),
            name=data["name"],
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            locality=data.get("localityName", ""),
        )


@dataclass
class Direction:
    """A line direction / terminus."""

    id: int    # 1 or 2
    name: str  # e.g. "Stade Diochon PETIT-QUEVILLY"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_api(cls, data: dict) -> "Direction":
        return cls(
            id=data["id"],
            name=data["name"],
        )


@dataclass
class Departure:
    """A scheduled (or real-time) vehicle passage at a stop."""

    datetime: datetime
    minutes: int       # timeDifference: minutes until departure
    destination: str   # final destination name of the vehicle
    is_cancelled: bool
    is_disrupted: bool
    is_late: bool      # isTimeout in the API

    def __str__(self) -> str:
        status = ""
        if self.is_cancelled:
            status = " [CANCELLED]"
        elif self.is_disrupted:
            status = " [DISRUPTED]"
        elif self.is_late:
            status = " [LATE]"
        return f"in {self.minutes} min ({self.datetime.strftime('%H:%M')}){status} → {self.destination}"

    @classmethod
    def from_api(cls, data: dict) -> "Departure":
        dt = datetime.fromisoformat(data["dateTime"])
        return cls(
            datetime=dt,
            minutes=data.get("timeDifference", 0),
            destination=data.get("destination", {}).get("name", ""),
            is_cancelled=data.get("isCancelled", False),
            is_disrupted=data.get("isDisrupted", False),
            is_late=data.get("isTimeout", False),
        )


@dataclass
class StopSearchResult:
    """Résultat de recherche d'arrêt (depuis l'API de recherche textuelle)."""

    id: int
    name: str
    city: str
    postal_code: str
    latitude: float
    longitude: float
    transport_modes: List[str]  # ex: ["BUS", "METRO", "TRAIN"]

    def __str__(self) -> str:
        modes = ", ".join(self.transport_modes) if self.transport_modes else "—"
        return f"{self.name} — {self.city} ({self.postal_code})  [ID: {self.id}]  modes: {modes}"

    @classmethod
    def from_api(cls, data: dict) -> "StopSearchResult":
        return cls(
            id=data["Id"],
            name=data["Name"],
            city=data.get("CityName", ""),
            postal_code=data.get("PostalCode", ""),
            latitude=data.get("Latitude", 0.0),
            longitude=data.get("Longitude", 0.0),
            transport_modes=data.get("TransportModes") or [],
        )


@dataclass
class StopDepartures:
    """Upcoming departures for a given (line, direction) pair at a stop."""

    line: Line
    direction: Direction
    stop: Stop
    departures: List[Departure] = field(default_factory=list)

    def __str__(self) -> str:
        lines = [f"{self.line} → {self.direction}  [{self.stop}]"]
        if self.departures:
            for d in self.departures:
                lines.append(f"  • {d}")
        else:
            lines.append("  (no upcoming departures)")
        return "\n".join(lines)

    @classmethod
    def from_api(cls, data: dict) -> "StopDepartures":
        line = Line.from_api(data["line"])
        direction = Direction.from_api(data["direction"])
        stop = Stop.from_api(data["stop"])
        departures = [Departure.from_api(t) for t in data.get("times", [])]
        return cls(line=line, direction=direction, stop=stop, departures=departures)
