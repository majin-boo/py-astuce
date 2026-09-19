# webapp — Affichage des prochains passages Astuce

Application Flask minimaliste affichant les prochains passages à un arrêt du réseau Astuce (Rouen Métropole).

## Lancement

```bash
# Depuis la racine du projet (première fois)
uv sync --extra webapp

# Démarrer l'application
uv run python webapp/app.py
```

Puis ouvrir [http://localhost:5000](http://localhost:5000). La page se recharge automatiquement.

## Configuration

Copier le fichier d'exemple et l'adapter :

```bash
cp webapp/config.json.example webapp/config.json
```

Éditer `webapp/config.json` :

```json
{
  "stop_id": 9144,
  "direction": 1,
  "refresh_seconds": 30
}
```

| Clé | Description |
|-----|-------------|
| `stop_id` | ID de l'arrêt logique (voir ci-dessous) |
| `direction` | Sens de passage : `1` ou `2` |
| `refresh_seconds` | Intervalle de rechargement en secondes |
| `host` | Adresse d'écoute (défaut : `"127.0.0.1"`, mettre `"0.0.0.0"` pour exposer sur le réseau) |
| `port` | Port d'écoute (défaut : `5000`) |
| `debug` | Mode debug Flask avec rechargement automatique (défaut : `false`) |

## Modes de transport

| Mode (`search_stops`) | Mode (`get_next_departures`) | Réseau Astuce | Description |
|-----------------------|------------------------------|--------------|-------------|
| `METRO` | `Metro` | Métro | Ligne de métro |
| `TROLLEY` | `Trolley` | TEOR (T1, T2, T3, T4) | Tramway sur pneus guidé |
| `BUS` | `Bus` | FAST (F1-F9), Bus, ELBEUF | Bus régulier et BHNS — FAST n'a pas de mode dédié |
| `TAD` | — | AlloBus | Transport à la demande |
| `TAXIBUS` | — | Taxi (t35, t53, t54) | Lignes de taxi conventionnées |
| `CAR` | — | Cars interurbains | Cars régionaux (Nomad) desservant certains arrêts |

## Affichage sur Chromecast

L'application peut être castée sur n'importe quel appareil compatible Chromecast avec [catt](https://github.com/skorokithakis/catt) :

```bash
catt -d "Nom du device Chromecast" cast_site http://$IP:5000
```

> Le serveur doit écouter sur `"host": "IP_Locale"` ou `"host": "0.0.0.0"`  dans `config.json` pour être accessible depuis le Chromecast.

## Trouver l'ID d'un arrêt

### Via le shell Python interactif

```
$ uv run python
```

```python
from astuce import AstuceClient
c = AstuceClient()

# Recherche par nom (retourne l'ID et la ville)
for s in c.search_stops("hôtel de ville"):
    print(s)
# Hôtel de Ville de Sotteville — Sotteville-lès-Rouen (76300)  [ID: 9063]  modes: BUS, TAD, METRO
# Hôtel de Ville — Rouen (76000)  [ID: 9144]  modes: BUS
# ...

# Affiner avec une bounding box (lat_max, lon_max, lat_min, lon_min)
for s in c.search_stops("gare", bbox=(49.49, 1.20, 49.39, 1.00)):
    print(s)
```

### Via la carte interactive MyAstuce

Sur [myastuce.fr](https://www.myastuce.fr), cliquer sur un arrêt : l'URL contient directement l'ID :

```
https://www.myastuce.fr/fr/carte-interactive?context=NearbyPopup&idContext=9144&subContext=LOGICAL_STOP
```

Le paramètre `idContext` est l'ID à utiliser.

### Trouver les arrêts à proximité d'un point GPS

```python
from astuce import AstuceClient
c = AstuceClient()

# Arrêts dans un rayon de 300 m autour d'un point (lat, lon)
stops = c.find_nearby_stops(49.4438, 1.0989, distance=300)
for s in stops:
    print(s.id, s.name, s.locality)
```

### Trouver la bonne direction

À un arrêt avec plusieurs lignes, `get_directions_at_stop` renvoie les deux sens (1 et 2) tous modes confondus. Pour savoir quel terminus correspond à quelle ligne, il faut filtrer par `line_id` ou inspecter les passages directement.

```python
from astuce import AstuceClient
c = AstuceClient()

# Hôtel de Ville : 6 lignes, mais seulement 2 sens
directions = c.get_directions_at_stop(9144)
for d in directions:
    print(d.id, d.name)
# 1  Stade Diochon PETIT-QUEVILLY   ← terminus de la F1, mais aussi F2, F7, 11, 15, 20…
# 2  Plaine de la Ronce ISNEAUVILLE ← terminus de la F1 dans l'autre sens

# Pour connaître le terminus de chaque ligne dans chaque sens,
# inspecter les passages directement :
deps = c.get_next_departures(9144)
for d in deps:
    print(f"ligne {d.line.number:4}  dir {d.direction.id}  → {d.direction.name}")
# ligne F1    dir 1  → Stade Diochon PETIT-QUEVILLY
# ligne F1    dir 2  → Plaine de la Ronce ISNEAUVILLE
# ligne F2    dir 1  → Tamarelle BIHOREL
# ligne F2    dir 2  → La Vatine MONT-SAINT-AIGNAN
# ligne F7    dir 1  → Hôtel de Ville SOTTEVILLE-LÈS-ROUEN
# ligne F7    dir 2  → La Pléiade MONT-SAINT-AIGNAN
# ...
```
