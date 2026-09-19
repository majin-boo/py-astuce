"""
py-astuce — Python library for the Astuce transit network API (Rouen Métropole).

Quick start:
    from astuce import AstuceClient

    client = AstuceClient()
    departures = client.get_next_departures(9144)  # Hôtel de Ville
    for d in departures:
        print(d)
"""

from .client import AstuceClient
from .exceptions import AstuceAPIError, AstuceError, AstuceNetworkError, AstuceParseError
from .models import Departure, Direction, Line, Stop, StopDepartures, StopSearchResult

__all__ = [
    "AstuceClient",
    # Modèles
    "Line",
    "Stop",
    "Direction",
    "Departure",
    "StopDepartures",
    "StopSearchResult",
    # Exceptions
    "AstuceError",
    "AstuceAPIError",
    "AstuceNetworkError",
    "AstuceParseError",
]

__version__ = "0.1.0"
