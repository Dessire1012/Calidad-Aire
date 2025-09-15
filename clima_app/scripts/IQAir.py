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

API_KEY = os.getenv("IQAIR_API_KEY")

BASE_URL = "http://api.airvisual.com/v2"
COUNTRY = "Honduras"

stations = [
    ("Siguatepeque", "Comayagua"),
    ("Comayagua", "Comayagua"),
    ("Tegucigalpa", "Francisco Morazan"),
    ("San Pedro Sula", "Cortes"),
    ("Choloma", "Cortes"),
]

def fetch_and_store_data():
    contaminante_ica, _ = Contaminante.objects.get_or_create(nombre="ICA")
    for city, state in stations:
        url = f"{BASE_URL}/city"
        params = {
            "city": city,
            "state": state,
            "country": COUNTRY,
            "key": API_KEY
        }

        try:
            response = requests.get(url, params=params, timeout=10)
        except requests.RequestException as e:
            print(f"Error al consultar {city}, {state}: {e}")
            continue

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                pollution = data["data"]["current"]["pollution"]
                aqi = pollution.get("aqius")
                coords = data["data"]["location"]["coordinates"]

                if aqi is not None:
                    # Crear o actualizar estación
                    estacion, created = Estacion.objects.get_or_create(
                        nombre=f"----{city}, {state}",
                        fuente="IQAir",  # <- importante
                        defaults={
                            "lat": coords[1],
                            "lon": coords[0]
                        }
                    )

                    # Guardar medición
                    Medicion.objects.create(
                        estacion=estacion,
                        contaminante=contaminante_ica,
                        valor=aqi,
                        fecha=timezone.now()
                    )

                    print(f"{city}, {state} -> ICA: {aqi}, Coords: {coords}")
                else:
                    print(f"{city}, {state} -> Sin ICA, no se guarda nada")
            else:
                print(f"API error para {city}, {state}: {data}")
        else:
            print(f"HTTP {response.status_code} para {city}, {state}: {response.text}")

        time.sleep(15)


if __name__ == "__main__":
    fetch_and_store_data()