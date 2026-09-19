# API pour le réseau Astuce rouennais

## Vue d'ensemble

Le site **MyAstuce** ([myastuce.fr](https://www.myastuce.fr)) est le portail officiel de transport pour le **Réseau Astuce**, le réseau de transports en commun de **Rouen Métropole** (agglomération rouennaise en Normandie, France).

**Modes de transport couverts :**
- **Métro** (METRO)
- **TEOR** (Tramways urbains : T1, T2, T3, T4)
- **FAST** (Bus à haut niveau de service)
- **Bus** (réseau régulier, ELBEUF, AlloBus)
- **Taxi** (t35, t53, t54)

### Correspondance des modes dans l'API

| Mode API | Réseau Astuce | Description |
|----------|--------------|-------------|
| `Metro` | Métro | Ligne de métro |
| `Trolley` | TEOR (T1, T2, T3, T4) | Tramway sur pneus guidé — appelé `TROLLEY` dans l'API de recherche |
| `Bus` | FAST (F1-F9), Bus, ELBEUF | Bus régulier et bus à haut niveau de service — FAST n'a pas de mode dédié |
| `Bus` / `TAD` | AlloBus | Transport à la demande — apparaît comme `TAD` dans l'API de recherche |
| `Bus` / `TAXIBUS` | Taxi (t35, t53, t54) | Lignes de taxi conventionnées |
| `Bus` / `CAR` | Cars interurbains | Cars régionaux (Nomad) desservant certains arrêts du réseau |

---

## Utilisation de la lib Python

```python
from astuce import AstuceClient

client = AstuceClient()
```

**Rechercher un arrêt par nom**

```python
for s in client.search_stops("hôtel de ville"):
    print(s)
# Hôtel de Ville — Rouen (76000)  [ID: 9144]  modes: BUS
# Hôtel de Ville de Sotteville — Sotteville-lès-Rouen (76300)  [ID: 9063]  modes: BUS, TAD, METRO
```

**Prochains passages à un arrêt**

```python
passages = client.get_next_departures(9144)
for p in passages:
    print(p)
# [Bus] F1 — Plaine de la Ronce <> Stade Diochon → Stade Diochon PETIT-QUEVILLY  [Hôtel de Ville (HVR1)]
#   • in 4 min (11:14) [DISRUPTED] → Stade Diochon PETIT-QUEVILLY
#   • in 27 min (11:37) → Stade Diochon PETIT-QUEVILLY
```

**Filtrer par sens**

```python
passages = client.get_next_departures(9144, direction=2)
```

**Lister les lignes et directions disponibles à un arrêt**

```python
for ligne in client.get_lines_at_stop(9144):
    print(ligne)
# [Bus] F1 — Plaine de la Ronce <> Stade Diochon
# [Bus] F2 — Centre commercial de La Vatine <> Tamarelle
# ...

for direction in client.get_directions_at_stop(9144):
    print(direction.id, direction.name)
# 1  Stade Diochon PETIT-QUEVILLY
# 2  Plaine de la Ronce ISNEAUVILLE
```

**Trouver les arrêts à proximité d'un point GPS**

```python
for s in client.find_nearby_stops(49.4438, 1.0989, distance=300):
    print(s)
```

---

## API publique fonctionnelle

L'application mobile et le site web utilisent une API REST publique sans authentification :

```
GET https://api.mrn.cityway.fr/media/api/v1/fr/Schedules/LogicalStop/{ID}/NextDeparture?realTime=true&lineId={lineId}&direction={dir}&userId=API_KEY
```

### Paramètres

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `ID` (dans le chemin) | int | Oui | ID de l'arrêt logique (ex: 9144 = Hôtel de Ville) |
| `realTime` | boolean | Non | Définir à `true` pour les données en temps réel |
| `lineId` | int | Non | Filtrer par ID de ligne (ex: 175 pour le Métro) |
| `direction` | int | Non | Filtrer par direction (1 ou 2) |
| `userId` | string | Non | **Clé API** (n'importe quelle valeur non vide fonctionne !) |

---

## Clé API (Authentification) — API publique

**La clé API ne sert à rien !** N'importe quelle chaîne non vide fonctionne :

| Valeur | Résultat |
|-------|----------|
| `TSI_MRN` | ✅ Fonctionne |
| `CITYWAY` | ✅ Fonctionne |
| `ZEN` | ✅ Fonctionne |
| `GAT` | ✅ Fonctionne |
| `null` | ✅ Fonctionne |
| `undefined` | ✅ Fonctionne |
| `false` | ✅ Fonctionne |
| Toute chaîne alphanumérique | ✅ Fonctionne |
| **Chaîne vide** | ❌ Erreur de parsing JSON |
| **Espace** | ❌ Erreur de parsing JSON |


### Exemple de requête

```bash
curl "https://api.mrn.cityway.fr/media/api/v1/fr/Schedules/LogicalStop/9144/NextDeparture?realTime=true&lineId=&direction=&userId=TSI_MRN"
```

### Réponse (JSON)

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

### Champs principaux

| Champ | Description |
|-------|-------------|
| `transportMode` | Bus, Metro, TEOR, FAST, Taxi |
| `line.name` | Nom complet de la ligne (ex: "Plaine de la Ronce <> Stade Diochon") |
| `line.number` | Numéro de ligne (ex: "F1", "METRO", "T2") |
| `direction.name` | Destination terminus |
| `stop.name` | Nom de la station |
| `stop.latitude`, `stop.longitude` | Coordonnées de la station |
| `timeDifference` | **Minutes avant le prochain départ** |
| `times[].dateTime` | Horodatage ISO |
| `isDisrupted` | Indicateur de perturbation |
| `isTimeout` | Véhicule en retard |

---

## Référence des ID de station

L'ID d'arrêt logique (ex: 9144 = Hôtel de Ville) provient du paramètre `idContext` du site :

```
https://www.myastuce.fr/fr/carte-interactive?context=NearbyPopup&idContext=68273&subContext=LOGICAL_STOP
```

Arrêts courants :

| Station | ID logique | Description |
|---------|-----------|-------------|
| Hôtel de Ville | 9144 | Centre-ville |
| Gare Rue Verte | 68273 | Pôle d'échanges |
| Palais de Justice - Gisèle Halimi | 63169 | Métro |

---

## APIs supplémentaires

D'après l'analyse du code, ces endpoints existent :

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/fr/Schedules/LogicalStop/{id}/NextDeparture` | Prochains départs |
| `GET /api/v1/fr/Schedules/LogicalStop/{id}/TimeTable` | Horaires complets |
| `GET /api/v1/fr/Stops/Logical/GetByLogicalId/{id}` | Infos arrêt par ID |
| `GET /api/v1/fr/Connectivity/FindNearbyStation?x=&y=&distance=500` | Trouver une station proche |
| `GET /api/v1/fr/Connections/Connection?type=transport&from=<addr>&to=<addr>` | Correspondance entre deux stations |
| `GET /api/v1/fr/Connections/Connection?type=transport&from=<addr>&to=<addr>&structuredLines=<ID>` | Correspondance avec filtre de ligne |

---

---

## Licence

Ce projet est distribué sous licence **BSD 2-Clause**. Voir le fichier [LICENSE](LICENSE) pour le texte complet.

Cette documentation API a été reverse-engineered à partir de :
1. L'ancienne bibliothèque Astuce-Java (Alba0404/Astuce-API)
2. L'API publique de l'application mobile à api.mrn.cityway.fr
3. L'analyse du trafic réseau de myastuce.fr

Utilisez de manière responsable et respectez les conditions d'utilisation de myastuce.fr.
