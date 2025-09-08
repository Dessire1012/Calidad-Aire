import os
import sys
import django
from django.utils import timezone
from playwright.sync_api import sync_playwright
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "ProyectoClima"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.getenv("DJANGO_SETTINGS_MODULE", "ProyectoClima.settings"))

django.setup()

from django.conf import settings
from clima_app.models import Medicion, Estacion, Contaminante

print("=== Django/DB ===")
print("DJANGO_SETTINGS_MODULE:", os.getenv("DJANGO_SETTINGS_MODULE"))
print("DB ENGINE:", settings.DATABASES['default']['ENGINE'])
print("DB NAME:", settings.DATABASES['default']['NAME'])
print("DB HOST:", settings.DATABASES['default'].get('HOST'))
print("USING DATABASE URL:", os.getenv("DATABASE_URL"))
print("=================\n")

def run():
    stations_data = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Usa Chromium headless
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto("https://estaciones.simet.amdc.hn/public-dashboards/e4d697a0e31647008370b09a592c0129?orgId=1&refresh=1m&from=now%2Fy&to=now")

        page.wait_for_timeout(60000)
        page.evaluate("document.body.style.zoom='40%'")

        # Esperar elementos PM2.5
        try:
            pm25_stations = page.query_selector_all("section[data-testid*='Panel header Material Particulado 2.5 µg/m³'] div[style*='text-align: center;']")
            pm25_values = page.query_selector_all("section[data-testid*='Panel header Material Particulado 2.5 µg/m³'] span.flot-temp-elem")

            for s, v in zip(pm25_stations, pm25_values):
                stations_data[s.inner_text().strip()] = {"PM2.5": v.inner_text().strip()}
        except Exception as e:
            print("Error PM2.5:", e)

        # PM10
        try:
            pm10_stations = page.query_selector_all("section[data-testid*='Panel header Material Particulado 10 µ/m³'] div[style*='text-align: center;']")
            pm10_values = page.query_selector_all("section[data-testid*='Panel header Material Particulado 10 µ/m³'] span.flot-temp-elem")

            for s, v in zip(pm10_stations, pm10_values):
                if s.inner_text().strip() in stations_data:
                    stations_data[s.inner_text().strip()]["PM10"] = v.inner_text().strip()
                else:
                    stations_data[s.inner_text().strip()] = {"PM10": v.inner_text().strip()}
        except Exception as e:
            print("Error PM10:", e)

        # AQI
        try:
            aqi_stations = page.query_selector_all("div[data-testid='data-testid Bar gauge value'] span")
            for idx, station in enumerate(stations_data.keys()):
                try:
                    stations_data[station]["AQI"] = int(aqi_stations[idx].inner_text().strip())
                except:
                    stations_data[station]["AQI"] = None
        except Exception as e:
            print("Error AQI:", e)

        browser.close()

    # --- Guardar en Django ---
    pm25_obj = Contaminante.objects.get(nombre="PM2.5")
    pm10_obj = Contaminante.objects.get(nombre="PM10")
    ica_obj = Contaminante.objects.get(nombre="ICA")

    for station_name, data in stations_data.items():
        try:
            estacion_obj = Estacion.objects.get(nombre=station_name)

            for contaminante_nombre, valor in data.items():
                if contaminante_nombre == "PM2.5":
                    contaminante_obj = pm25_obj
                elif contaminante_nombre == "PM10":
                    contaminante_obj = pm10_obj
                else:
                    contaminante_obj = ica_obj

                Medicion.objects.create(
                    estacion=estacion_obj,
                    contaminante=contaminante_obj,
                    valor=valor,
                    fecha=timezone.now()
                )

            print(f"Guardado: {station_name}")
        except Exception as e:
            print(f"Error guardando {station_name}: {e}")

    print("Script completado ✅")


if __name__ == "__main__":
    run()
