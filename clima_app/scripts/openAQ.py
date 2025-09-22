import os
import sys
import requests
import django
from dotenv import load_dotenv
from datetime import datetime, timezone as dt_timezone
import time

# Configuración de Django
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

# Diccionario de mapeo: API → nombres en tu BD
PARAM_MAP = {
    "pm10": "PM10",
    "pm25": "PM2.5",
    "pm1": "PM1",
    "um003": "UM0.3",
    "temperature": "Temperatura",
    "relativehumidity": "RH",
    "co": "CO",
    "so2": "SO₂",
    "no2": "NO₂",
    "o3": "O₃",
    "aqi": "AQI"
}

def get_location_details(location_id):
    """Devuelve info de la estación (nombre, id externo)."""
    url = f"{BASE_URL}/locations/{location_id}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json().get("results", [])
        if isinstance(data, list) and data:
            return data[0]
        elif isinstance(data, dict):
            return data
    return None

def get_sensor_details(sensor_id):
    """Obtiene detalles de un sensor específico."""
    url = f"{BASE_URL}/sensors/{sensor_id}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json().get("results", [])
        if isinstance(data, list) and data:
            return data[0]
        elif isinstance(data, dict):
            return data
    return {}

def fetch_station_latest(location_id):
    url = f"{BASE_URL}/locations/{location_id}/latest"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Error {resp.status_code} en estación {location_id}: {resp.text}")
        return

    results = resp.json().get("results", [])
    if not results:
        print(f"Estación {location_id} sin resultados en /latest")
        return

    station_info = get_location_details(location_id)
    if not station_info:
        print(f"No se pudo obtener info de la estación {location_id}")
        return

    external_id = station_info.get("id")
    station_name = station_info.get("name", f"Location {location_id}")

    estacion = Estacion.objects.filter(external_id=external_id, fuente="OpenAQ").first()
    if not estacion:
        print(f"Estación no encontrada en BD: {station_name} (ID externo {external_id})")
        return

    print(f"\n=== Estación {station_name} (ID externo {external_id}) ===")

    for entry in results:
        sensor_id = entry.get("sensorsId")
        value = entry.get("value")

        # 1) Trae el parámetro del sensor
        sensor_info = get_sensor_details(sensor_id)
        param_raw = sensor_info.get("parameter", {}).get("name", "").lower()
        units = sensor_info.get("parameter", {}).get("units", "")

        # 2) Mapea al nombre en la BD
        contaminante_name = PARAM_MAP.get(param_raw)
        if not contaminante_name:
            print(f"Parámetro '{param_raw}' no mapeado, se omite")
            continue

        # 3) CONVERSIÓN DE FECHA
        dt_utc_str = entry.get("datetime", {}).get("utc")  # ej: '2025-09-21T23:00:00Z'
        if not dt_utc_str:
            print(f"Sin fecha en la medición, se omite")
            continue

        # Convierte string ISO8601 con 'Z' a datetime aware en UTC
        dt_utc = datetime.fromisoformat(dt_utc_str.replace("Z", "+00:00"))
        dt_utc = dt_utc.astimezone(dt_timezone.utc) 

        # 4) Guarda en BD con fecha UTC
        contaminante, _ = Contaminante.objects.get_or_create(nombre=contaminante_name)
        Medicion.objects.create(
            estacion=estacion,
            contaminante=contaminante,
            valor=value,
            fecha=dt_utc,  
        )

        print(f"{contaminante_name}: {value} {units} @ {dt_utc_str}")
        time.sleep(0.5)

def fetch_all_stations():
    for loc in location_ids:
        fetch_station_latest(loc)
        time.sleep(1)

if __name__ == "__main__":
    fetch_all_stations()
