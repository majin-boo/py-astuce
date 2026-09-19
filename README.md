# API pour le réseau Astuce rouenais

## Overview

The **MyAstuce** website ([myastuce.fr](https://www.myastuce.fr)) is the official transit portal for **Réseau Astuce**, the public transportation network in **Rouen Métropole** (Rouen area in Normandy, France).

**Transport modes covered:**
- **Metro** (METRO)
- **TEOR** (Urban Electric Trains: T1, T2, T3, T4)
- **FAST** (Trams)
- **Bus** networks (regular, ELBEUF, AlloBus)
- **Taxi** (t35, t53, t54)

---

## Current Public API (WORKS!) — Mobile Backend

The mobile app uses a public REST API that doesn't require authentication:

```
GET https://api.mrn.cityway.fr/media/api/v1/fr/Schedules/LogicalStop/{ID}/NextDeparture?realTime=true&lineId={lineId}&direction={dir}&userId=API_KEY
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ID` (in path) | int | Yes | Logical stop ID (e.g., 9144 = Hôtel de Ville) |
| `realTime` | boolean | No | Set to `true` for real-time data |
| `lineId` | int | No | Filter by line ID (e.g., 175 for Metro) |
| `direction` | int | No | Filter by direction (1 or 2) |
| `userId` | string | No | **API Key** (any non-empty value works!) |

---

## API Key (Authentication) — PUBLIC API

**The API key is effectively a no-op!** Any non-empty string works:

| Value | Result |
|-------|--------|
| `TSI_MRN` | ✅ Works |
| `CITYWAY` | ✅ Works |
| `ZEN` | ✅ Works |
| `GAT` | ✅ Works |
| `null` | ✅ Works |
| `undefined` | ✅ Works |
| `false` | ✅ Works |
| Any alphanumeric string | ✅ Works |
| **Empty string** | ❌ JSON parse error |
| **Space** | ❌ JSON parse error |

**Conclusion:** The API performs no authentication validation. Simply pass any non-empty value for `userId` (or omit the parameter entirely — the API returns default data).

> **⚠️ Security Note:** This is a trivial authentication bypass — any value works! This might be intentional (public API) or an oversight.

### Example Request

```bash
curl "https://api.mrn.cityway.fr/media/api/v1/fr/Schedules/LogicalStop/9144/NextDeparture?realTime=true&lineId=&direction=&userId=TSI_MRN"
```

### Response (JSON)

```json
[
  {
    "transportMode": "Bus",
    "order": 40,
    "lines": [
      {
        "line": {
          "name": "Plaine de la Ronce <> Stade Diochon",
          "number": "F1",
          "transportMode": "Bus",
          "networkName": "Astuce",
          "color": "E6007E",
          "id": 24099
        },
        "direction": {
          "name": "Stade Diochon PETIT-QUEVILLY",
          "id": 1
        },
        "stop": {
          "id": 11190,
          "code": "HVR1",
          "name": "Hôtel de Ville",
          "latitude": 49.4438235,
          "longitude": 1.0988885,
          "localityName": "Rouen"
        },
        "times": [
          {
            "dateTime": "2026-09-18T23:30:00",
            "timeDifference": 13,
            "restriction": "None",
            "destination": {
              "id": 6819750,
              "vehicleJourneyId": 59900048,
              "name": "Stade Diochon PETIT-QUEVILLY"
            },
            "isCancelled": false,
            "isDisrupted": true,
            "isTimeout": false,
            "trainNumber": null
          }
        ]
      }
    ]
  }
]
```

### Key Fields

| Field | Description |
|-------|-------------|
| `transportMode` | Bus, Metro, TEOR, FAST, Taxi |
| `line.name` | Full line name (e.g., "Plaine de la Ronce <> Stade Diochon") |
| `line.number` | Line number (e.g., "F1", "METRO", "T2") |
| `direction.name` | Terminal destination |
| `stop.name` | Station name |
| `stop.latitude`, `stop.longitude` | Station coordinates |
| `timeDifference` | **Minutes until next departure** |
| `times[].dateTime` | ISO timestamp |
| `isDisrupted` | Service disruption flag |
| `isTimeout` | Vehicle is late |

---

## Station ID Reference

The logical stop ID (e.g., 9144 = Hôtel de Ville) comes from the site's `idContext` parameter:

```
https://www.myastuce.fr/fr/carte-interactive?context=NearbyPopup&idContext=68273&subContext=LOGICAL_STOP
```

Common stops:

| Station | Logical ID | Description |
|---------|-----------|-------------|
| Hôtel de Ville | 9144 | City center |
| Gare Rue Verte | 68273 | Transit hub |
| Palais de Justice | 50000+ | Metro |
| La Jatel | 80000+ | Metro/Bus |

---

## Python Usage Example

```python
import urllib.request
import json
import urllib.parse

def get_next_departures(stop_id, api_key="TSI_MRN"):
    """
    Get next departures from the mobile API
    
    Args:
        stop_id: Logical stop ID (e.g., 9144)
        api_key: API key (TSI_MRN, CITYWAY, ZEN, or any non-empty string)
    
    Returns:
        List of transit departures
    """
    url = f"https://api.mrn.cityway.fr/media/api/v1/fr/Schedules/LogicalStop/{stop_id}/NextDeparture?realTime=true&lineId=&direction=&userId={api_key}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_departure_for_line(stop_id, line_id, api_key="TSI_MRN"):
    """
    Filter departures by line
    """
    url = f"https://api.mrn.cityway.fr/media/api/v1/fr/Schedules/LogicalStop/{stop_id}/NextDeparture?realTime=true&lineId={line_id}&direction=&userId={api_key}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"Error: {e}")
        return None

# Example: Get departures from Hôtel de Ville
result = get_next_departures(9144)
for bus in result:
    for line in bus['lines']:
        print(f"Line: {line['line']['number']} - {line['line']['name']}")
        for time in line['times'][:1]:
            print(f"  Direction: {line['direction']['name']}")
            print(f"  Next: in {time['timeDifference']} minutes")
            print(f"  Time: {time['dateTime']}")
            print()

# Example: Get departures for FAST F1 line only
result = get_departure_for_line(9144, 24099)  # F1 line ID
print(result)
```

---

## Additional APIs

From code analysis, these endpoints exist:

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/fr/Schedules/LogicalStop/{id}/NextDeparture` | Next departures |
| `GET /api/v1/fr/Schedules/LogicalStop/{id}/TimeTable` | Full schedule |
| `GET /api/v1/fr/Stops/Logical/GetByLogicalId/{id}` | Stop info by ID |
| `GET /api/v1/fr/Connectivity/FindNearbyStation?x=&y=&distance=500` | Find nearby station |
| `GET /api/v1/fr/Connections/Connection?type=transport&from=<addr>&to=<addr>` | Connection between two stations |
| `GET /api/v1/fr/Connections/Connection?type=transport&from=<addr>&to=<addr>&structuredLines=<ID>` | Connection with line filter |

---

## Current Status

| API | Status | Notes |
|-----|--------|-------|
| **Mobile API (api.mrn.cityway.fr)** | ✅ WORKS | Public, no auth required (API key only) |
| **Site API (myastuce.fr)** | ✅ Active | Angular SPA, JS-loaded data, no direct access |
| **Legacy API (réseau-astuce.fr)** | ❌ Dead | Redirects to myastuce.fr |
| **Cityway APIs** | ❌ Unavailable | Not resolving |
| **Mobile Apps** | ✅ Same backend | Uses api.mrn.cityway.fr |

**Key Finding:** The mobile app API at `api.mrn.cityway.fr` is public, works without authentication, and provides real-time transit data in clean JSON format.

---

## License

This API documentation was reverse-engineered from:
1. The old Astuce-Java library (Alba0404/Astuce-API)
2. The mobile app's public API at api.mrn.cityway.fr
3. Network traffic analysis of myastuce.fr

Use responsibly and respect the terms of service of myastuce.fr.
