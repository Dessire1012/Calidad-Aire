import os
import sys
import requests
import django
from dotenv import load_dotenv
from django.utils import timezone
import time

sys.path.append(r'C:\Users\dessi\ProyectoClima')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyectoClima.settings')
django.setup()

from clima_app.models import Estacion, Contaminante, Medicion

load_dotenv()

API_KEY = os.getenv("OPENAQ_API_KEY")
BASE_URL = "https://api.openaq.org/v3"
headers = {"X-API-Key": API_KEY}

location_ids = [
    3293767, 3294183, 3459201, 3543965, 3544957,
    3789589, 3801453, 4773413, 4808366, 4808368,
    4959160, 5456449
]

# Lista de contaminantes
contaminantes = [
    "PM1", "PM10", "PM2.5", "RelativeHumidity", "Temperature", "UM003"
]

def fetch_sensor_measurements(sensor_id, parameter, estacion):
    url = f"{BASE_URL}/sensors/{sensor_id}/measurements"
    params = {"limit": 1}
    resp = requests.get(url, params=params, headers=headers)

    if resp.status_code == 200:
        data = resp.json().get("results", [])
        if not data:
            print(f"    {parameter.upper()}: sin datos")
        for r in data:
            val = r.get("value", "N/A")
            units = r.get("parameter", {}).get("units", "")
            fecha = r.get("date", {}).get("local", "N/A")
            print(f"    {parameter.upper()}: {val} {units} at {fecha}")

            # Guardar medición en la base de datos solo si el valor no es N/A
            if val != "N/A":
                # Obtener o crear el contaminante (si no existe)
                contaminante, _ = Contaminante.objects.get_or_create(nombre=parameter)

                # Guardar la medición en la base de datos
                Medicion.objects.create(
                    estacion=estacion,
                    contaminante=contaminante,
                    valor=val,
                    fecha=timezone.now()
                )

    elif resp.status_code == 404:
        print(f"    {parameter.upper()}: no tiene datos (404)")
    else:
        print(f"    Error {resp.status_code} para {parameter}: {resp.text}")

def fetch_station_sensors(location_id):
    url = f"{BASE_URL}/locations/{location_id}"
    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:
        results = resp.json().get("results", [])
        station = results[0] if isinstance(results, list) else results

        # Buscar la estación en la base de datos por external_id (ID único)
        external_id = station["id"]
        print(f"Buscando estación con ID externo: {external_id}")

        # Buscar la estación en la base de datos por external_id y fuente "OpenAQ"
        estacion = Estacion.objects.filter(external_id=external_id, fuente="OpenAQ").first()

        if estacion:
            print(f"\n=== Estación encontrada: {estacion.nombre} (ID: {estacion.external_id}) ===")
        else:
            print(f"Estación no encontrada con ID externo: {external_id}. Se omite.")
            return

        # Iterar sobre los sensores de la estación
        sensors = station.get("sensors", [])
        for s in sensors:
            sensor_id = s["id"]
            param = s["parameter"]["name"]
            print(f"  Sensor: {s['name']} ({param}) [ID {sensor_id}]")
            fetch_sensor_measurements(sensor_id, param, estacion)
            time.sleep(2)
    else:
        print(f"Error {resp.status_code} en estación {location_id}: {resp.text}")


def fetch_all_stations():
    for loc in location_ids:
        fetch_station_sensors(loc)
        time.sleep(3)

fetch_all_stations()