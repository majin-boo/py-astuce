"""HTTP client for the Astuce API (api.mrn.cityway.fr)."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional, Tuple

from .exceptions import AstuceAPIError, AstuceNetworkError, AstuceParseError
from .models import Departure, Direction, Line, Stop, StopDepartures, StopSearchResult

_BASE_URL   = "https://api.mrn.cityway.fr/media/api/v1/fr"
_SEARCH_URL = "https://api.mrn.cityway.fr/search/all"

# Type 2 = arrêt logique (avec modes de transport)
# Type 1 = adresse / POI (sans modes de transport)
_TYPE_STOP = 2


class AstuceClient:
    """
    Client for the public Astuce network API (Rouen Métropole).

    Basic usage:
        client = AstuceClient()
        departures = client.get_next_departures(9144)
        for d in departures:
            print(d)

    Args:
        api_key : Any non-empty string (the API performs no real authentication).
        timeout : HTTP timeout in seconds (default: 10).
    """

    def __init__(self, api_key: str = "TSI_MRN", timeout: int = 10) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("api_key must not be empty.")
        self._api_key = api_key
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def get_next_departures(
        self,
        stop_id: int,
        *,
        line_id: Optional[int] = None,
        direction: Optional[int] = None,
        real_time: bool = True,
    ) -> List[StopDepartures]:
        """
        Return the next departures at a logical stop.

        Args:
            stop_id   : Logical stop ID (e.g. 9144 = Hôtel de Ville).
            line_id   : Filter by line ID (optional).
            direction : Filter by direction: 1 or 2 (optional).
            real_time : Use real-time data (default: True).

        Returns:
            List of StopDepartures, one per (line, direction) pair.
        """
        params: dict = {
            "realTime": str(real_time).lower(),
            "lineId": line_id if line_id is not None else "",
            "direction": direction if direction is not None else "",
            "userId": self._api_key,
        }
        url = self._build_url(f"/Schedules/LogicalStop/{stop_id}/NextDeparture", params)
        raw = self._get(url)

        results: List[StopDepartures] = []
        for transport_group in raw:
            for line_data in transport_group.get("lines", []):
                results.append(StopDepartures.from_api(line_data))
        return results

    def get_next_departures_by_direction(
        self,
        stop_id: int,
        direction: int,
        *,
        line_id: Optional[int] = None,
        real_time: bool = True,
    ) -> List[StopDepartures]:
        """
        Return the next departures at a stop filtered by direction (1 or 2).

        Args:
            stop_id   : Logical stop ID.
            direction : Direction 1 or 2.
            line_id   : Filter by line ID (optional).
            real_time : Use real-time data (default: True).
        """
        if direction not in (1, 2):
            raise ValueError("direction must be 1 or 2.")
        return self.get_next_departures(
            stop_id, line_id=line_id, direction=direction, real_time=real_time
        )

    def get_lines_at_stop(self, stop_id: int) -> List[Line]:
        """
        Return all lines serving a given stop.

        Args:
            stop_id : Logical stop ID.
        """
        departures = self.get_next_departures(stop_id)
        seen: dict[int, Line] = {}
        for sd in departures:
            if sd.line.id not in seen:
                seen[sd.line.id] = sd.line
        return list(seen.values())

    def get_directions_at_stop(
        self, stop_id: int, line_id: Optional[int] = None
    ) -> List[Direction]:
        """
        Return all directions available at a stop, optionally filtered by line.

        Args:
            stop_id : Logical stop ID.
            line_id : Filter by line ID (optional).
        """
        departures = self.get_next_departures(stop_id, line_id=line_id)
        seen: dict[int, Direction] = {}
        for sd in departures:
            if sd.direction.id not in seen:
                seen[sd.direction.id] = sd.direction
        return list(seen.values())

    def get_stop_info(self, stop_id: int) -> Optional[Stop]:
        """
        Return information about a logical stop by its ID.

        Args:
            stop_id : Logical stop ID.
        """
        url = self._build_url(
            f"/Stops/Logical/GetByLogicalId/{stop_id}", {"userId": self._api_key}
        )
        raw = self._get(url)
        if not raw:
            return None
        # The API may return either a list or a single object depending on the version.
        data = raw[0] if isinstance(raw, list) else raw
        return Stop.from_api(data)

    def find_nearby_stops(
        self, latitude: float, longitude: float, distance: int = 500
    ) -> List[Stop]:
        """
        Return stops within a given radius of a geographic point.

        Args:
            latitude  : WGS84 latitude.
            longitude : WGS84 longitude.
            distance  : Search radius in metres (default: 500).
        """
        params = {
            "x": longitude,
            "y": latitude,
            "distance": distance,
            "userId": self._api_key,
        }
        url = self._build_url("/Connectivity/FindNearbyStation", params)
        raw = self._get(url)
        if not raw:
            return []
        stops = []
        for item in raw if isinstance(raw, list) else [raw]:
            try:
                stops.append(Stop.from_api(item))
            except (KeyError, TypeError):
                continue
        return stops

    def search_stops(
        self,
        keywords: str,
        *,
        max_results: int = 10,
        bbox: Optional[Tuple[float, float, float, float]] = None,
    ) -> List[StopSearchResult]:
        """
        Search for stops by name using free-text keywords.

        Args:
            keywords    : Search terms (e.g. "hôtel de ville", "gare rue verte").
            max_results : Maximum number of results to return (default: 10).
            bbox        : Optional bounding box to restrict the search area,
                          as (lat_max, lon_max, lat_min, lon_min) — top-left / bottom-right.

        Returns:
            List of StopSearchResult, only logical stops (type 2), sorted by relevance.
        """
        if not keywords.strip():
            raise ValueError("keywords must not be empty.")

        params: dict = {
            "keywords": keywords,
            "maxitems": max_results,
            "lang": "fr",
            "objectTypes": "2",  # type 2 uniquement : arrêts logiques
        }
        if bbox is not None:
            lat_max, lon_max, lat_min, lon_min = bbox
            params["bboxView"] = f"{lat_max};{lon_max};{lat_min};{lon_min}"

        query = urllib.parse.urlencode(params)
        url = f"{_SEARCH_URL}?{query}"
        raw = self._get(url)

        results = []
        for item in raw if isinstance(raw, list) else [raw]:
            if item.get("Type") == _TYPE_STOP:
                try:
                    results.append(StopSearchResult.from_api(item))
                except (KeyError, TypeError):
                    continue
        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_url(self, path: str, params: dict) -> str:
        query = urllib.parse.urlencode(
            {k: v for k, v in params.items() if v != "" or k == "userId"}
        )
        return f"{_BASE_URL}{path}?{query}"

    def _get(self, url: str) -> list | dict:
        try:
            req = urllib.request.Request(
                url,
                headers={"Accept": "application/json", "User-Agent": "py-astuce/1.0"},
            )
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                if resp.status != 200:
                    raise AstuceAPIError(resp.status)
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raise AstuceAPIError(e.code, str(e.reason)) from e
        except urllib.error.URLError as e:
            raise AstuceNetworkError(str(e.reason)) from e
        except TimeoutError as e:
            raise AstuceNetworkError(f"Request timed out after {self._timeout}s") from e
        except OSError as e:
            raise AstuceNetworkError(str(e)) from e

        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise AstuceParseError(f"Invalid response: {e}") from e
