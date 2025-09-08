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

from clima_app.models import Medicion, Estacion, Contaminante

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

from clima_app.models import Medicion, Estacion, Contaminante

def load_grafana_and_grab(page):
    url = "https://estaciones.simet.amdc.hn/public-dashboards/e4d697a0e31647008370b09a592c0129?orgId=1&from=now-24h&to=now"
    print("Navegando a:", url)

    page.goto(url, timeout=180_000, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle", timeout=180_000)

    # Esperar a que los valores realmente aparezcan en cada panel
    page.wait_for_selector("div[data-testid='data-testid Bar gauge value'] span", timeout=180_000)

    # viewport grande en vez de zoom
    page.set_viewport_size({"width": 5120, "height": 2880})

    page.screenshot(path="scraping_test.png", full_page=True)
    print("Screenshot guardado: scraping_test.png")

    html = page.content()
    with open("scraping_dump.html", "w", encoding="utf-8") as f:
        f.write(html[:200000])
    print("Dump HTML guardado: scraping_dump.html")
    return page

def run():
    stations_data = {}
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            page = browser.new_page(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36",
                ignore_https_errors=True,
            )
        except Exception as e:
            print("[WARN] Chromium falló:", repr(e))
            browser = p.firefox.launch(headless=True)
            page = browser.new_page(ignore_https_errors=True)

        # cargar y tomar screenshot/dump
        load_grafana_and_grab(page)

        # Scraping PM2.5
        pm25_stations = page.query_selector_all("section[data-testid*='Material Particulado 2.5'] div[style*='text-align: center;']")
        pm25_values = page.query_selector_all("section[data-testid*='Material Particulado 2.5'] span.flot-temp-elem")
        for s, v in zip(pm25_stations, pm25_values):
            stations_data[s.inner_text().strip()] = {"PM2.5": v.inner_text().strip()}

        # Scraping PM10
        pm10_stations = page.query_selector_all("section[data-testid*='Material Particulado 10'] div[style*='text-align: center;']")
        pm10_values = page.query_selector_all("section[data-testid*='Material Particulado 10'] span.flot-temp-elem")
        for s, v in zip(pm10_stations, pm10_values):
            name = s.inner_text().strip()
            stations_data.setdefault(name, {})
            stations_data[name]["PM10"] = v.inner_text().strip()
            
        try:
            aqi_stations = page.query_selector_all("div[data-testid='data-testid Bar gauge value'] span")
            for idx, station in enumerate(stations_data.keys()):
                try:
                    stations_data[station]["AQI"] = int(aqi_stations[idx].inner_text().strip())
                except:
                    stations_data[station]["AQI"] = None
        except Exception as e:
            print("Error AQI:", e)

        print("Stations scraped:", stations_data)

        browser.close()

if __name__ == "__main__":
    run()
