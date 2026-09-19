"""
Script d'exemple — py-astuce
Récupère les prochains passages depuis l'arrêt Hôtel de Ville (ID 9144).
"""

from astuce import AstuceClient

client = AstuceClient()

STOP_ID = 9144  # Hôtel de Ville, Rouen

print("=" * 60)
print(f"Arrêt : Hôtel de Ville (ID {STOP_ID})")
print("=" * 60)

# 1. Lignes qui desservent l'arrêt
print("\n── Lignes disponibles ──")
lignes = client.get_lines_at_stop(STOP_ID)
for ligne in lignes:
    print(f"  {ligne}")

# 2. Directions disponibles
print("\n── Directions disponibles ──")
directions = client.get_directions_at_stop(STOP_ID)
for direction in directions:
    print(f"  {direction}")

# 3. Tous les prochains passages
print("\n── Prochains passages (tous sens) ──")
passages = client.get_next_departures(STOP_ID)
for p in passages:
    print(f"\n{p}")

# 4. Filtrer par sens (direction 1)
print("\n── Prochains passages — Sens 1 uniquement ──")
passages_sens1 = client.get_next_departures_by_direction(STOP_ID, direction=1)
for p in passages_sens1:
    print(f"\n{p}")
