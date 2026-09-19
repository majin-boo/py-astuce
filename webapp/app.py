"""
webapp/app.py — Application d'affichage des prochains passages du réseau Astuce.

La configuration est lue depuis config.json (même dossier) :
  {
    "stop_id": 9144,
    "direction": 1,          // 1 ou 2
    "refresh_seconds": 30    // intervalle de rechargement automatique
  }
"""

import json
import sys
from pathlib import Path

from flask import Flask, render_template

# Permet de lancer l'app depuis n'importe quel répertoire courant
ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "config.json"
sys.path.insert(0, str(ROOT.parent))

from astuce import AstuceClient
from astuce.exceptions import AstuceError

app = Flask(__name__)


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    config = load_config()
    stop_id = config["stop_id"]
    direction = config.get("direction")
    refresh = int(config.get("refresh_seconds", 30))

    client = AstuceClient()
    error = None
    departures = []
    stop_name = f"Arrêt #{stop_id}"
    stop_locality = ""

    try:
        raw = client.get_next_departures(
            stop_id,
            direction=direction,
            real_time=True,
        )
        # Récupérer le nom de l'arrêt depuis le premier résultat
        if raw:
            stop_name = raw[0].stop.name
            stop_locality = raw[0].stop.locality

        # Aplatir en une liste de passages individuels avec les infos de ligne
        for stop_dep in raw:
            for dep in stop_dep.departures:
                departures.append({
                    "line_number": stop_dep.line.number,
                    "line_color": stop_dep.line.color,
                    "transport_mode": stop_dep.line.transport_mode,
                    "direction_name": stop_dep.direction.name,
                    "minutes": dep.minutes,
                    "time": dep.datetime.strftime("%H:%M"),
                    "destination": dep.destination,
                    "is_cancelled": dep.is_cancelled,
                    "is_disrupted": dep.is_disrupted,
                    "is_late": dep.is_late,
                })
        # Trier par ordre d'arrivée
        departures.sort(key=lambda d: d["minutes"])
    except AstuceError as e:
        error = str(e)

    return render_template(
        "index.html",
        stop_name=stop_name,
        stop_locality=stop_locality,
        direction=direction,
        departures=departures,
        refresh=refresh,
        error=error,
    )


if __name__ == "__main__":
    config = load_config()
    debug = config.get("debug", False)
    host = config.get("host", "127.0.0.1")
    port = int(config.get("port", 5000))

    if debug:
        # Serveur de développement Flask (rechargement automatique, debugger)
        app.run(debug=True, host=host, port=port)
    else:
        # Serveur WSGI de production
        from waitress import serve
        print(f"Serveur démarré sur http://{host}:{port}")
        serve(app, host=host, port=port)
