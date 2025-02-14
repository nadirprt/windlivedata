import requests
import time
import csv
import numpy as np
from datetime import datetime

# URL de l'API
api_url = "https://pubs.diabox.com/dataUpdate.php?dbx_id=105&dataNameList%5B%5D=pacific_temperature&dataNameList%5B%5D=pacific_pressure&dataNameList%5B%5D=pacific_wind_rt&dataNameList%5B%5D=pacific_humidity&dataNameList%5B%5D=pacific_rainRate"

# Fonction pour récupérer les données
def get_wind_data():
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        wind_direction = data.get("pacific_wind_rt", {}).get("dir", 0)  # Direction en degrés
        wind_speed_knots = data.get("pacific_wind_rt", {}).get("force", 0)  # Vitesse en nœuds
        wind_speed_kmh = wind_speed_knots * 1.852  # Conversion nœuds → km/h
        return wind_direction, wind_speed_kmh
    else:
        print("Erreur lors de la récupération des données :", response.status_code)
        return None, None

# Fonction pour calculer la moyenne des directions en tenant compte de la circularité
def moyenne_direction(angles):
    angles_rad = np.radians(angles)  # Convertir en radians
    x = np.cos(angles_rad)
    y = np.sin(angles_rad)

    x_moy = np.mean(x)
    y_moy = np.mean(y)

    angle_moyen_rad = np.arctan2(y_moy, x_moy)
    angle_moyen_deg = np.degrees(angle_moyen_rad)

    return angle_moyen_deg % 360  # Assurer un angle entre 0 et 360°

# Prendre 5 mesures espacées de 6 secondes
directions = []
speeds = []
for i in range(5):
    direction, speed = get_wind_data()
    if direction is not None and speed is not None:
        directions.append(direction)
        speeds.append(speed)
    print(f"Mesure {i + 1} - Direction : {direction}° | Vitesse : {speed} km/h")
    time.sleep(6)  # Pause de 6 secondes entre chaque mesure

# Calcul de la moyenne
if directions and speeds:
    avg_direction = round(moyenne_direction(directions), 2)  # Utilisation de la moyenne vectorielle
    avg_speed = round(sum(speeds) / len(speeds), 2)

    # Enregistrement dans un fichier CSV
    csv_file = "wind_data.csv"
    with open(csv_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), int(avg_direction), int(avg_speed)])

    print(f"\nMoyenne - Direction : {avg_direction}° | Vitesse : {avg_speed} km/h")
else:
    print("Aucune donnée valide récupérée.")
