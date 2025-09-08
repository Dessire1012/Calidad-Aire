import requests
import time

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAQ_API_KEY")
BASE_URL = "https://api.openaq.org/v3"

headers = {"X-API-Key": API_KEY}

location_ids = [
    3293767, 3294183, 3459201, 3543965, 3544957,
    3789589, 3801453, 4773413, 4808366, 4808368,
    4959160, 5456449
]

def fetch_sensor_measurements(sensor_id, parameter, limit=5):
    url = f"{BASE_URL}/sensors/{sensor_id}/measurements"
    params = {"limit": limit}
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

        print(f"\n=== {station['name']} (ID: {station['id']}) ===")

        sensors = station.get("sensors", [])
        for s in sensors:
            sensor_id = s["id"]
            param = s["parameter"]["name"]
            print(f"  Sensor: {s['name']} ({param}) [ID {sensor_id}]")
            fetch_sensor_measurements(sensor_id, param, limit=5)
            time.sleep(2)  
    else:
        print(f"Error {resp.status_code} en estación {location_id}: {resp.text}")


def fetch_all_stations():
    for loc in location_ids:
        fetch_station_sensors(loc)
        time.sleep(3)  

fetch_all_stations()
