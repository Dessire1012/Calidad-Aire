import os
import sys
import django
from django.utils import timezone
from asgiref.sync import sync_to_async
from playwright.async_api import async_playwright 

sys.path.append(r'C:\Users\dessi\ProyectoClima')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyectoClima.settings')
django.setup()

from clima_app.models import Medicion, Estacion, Contaminante

async def load_grafana_and_grab(page):
    url = "https://estaciones.simet.amdc.hn/public-dashboards/e4d697a0e31647008370b09a592c0129?orgId=1&from=now-24h&to=now"
    print("Navegando a:", url)

    await page.goto(url, timeout=180_000, wait_until="domcontentloaded")  # Esperar la navegación
    await page.wait_for_load_state("networkidle", timeout=180_000) 

    await page.set_viewport_size({"width": 5120, "height": 2880})

    await page.screenshot(path="scraping_test.png", full_page=True) 
    print("Screenshot guardado: scraping_test.png")

    # Esperar y obtener el contenido de la página
    html = await page.content()
    with open("scraping_dump.html", "w", encoding="utf-8") as f:
        f.write(html[:200000])  # Solo guardar una porción del HTML
    print("Dump HTML guardado: scraping_dump.html")

@sync_to_async
def get_or_create_estacion(station_name):
    return Estacion.objects.get_or_create(nombre=station_name)

@sync_to_async
def get_or_create_contaminante(contaminante_name):
    return Contaminante.objects.get_or_create(nombre=contaminante_name)

@sync_to_async
def create_medicion(estacion, contaminante, contaminante_value):
    Medicion.objects.create(
        estacion=estacion,
        contaminante=contaminante,
        valor=float(contaminante_value),  
        fecha=timezone.now()
    )

def normalize_station_name(name: str) -> str:
    return name.replace("AMDC ", "").strip()

# Función para ejecutar el scraping y guardar en la base de datos
async def run():
    stations_data = {}
    async with async_playwright() as p: 
        try:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = await browser.new_page(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True) 
        except Exception as e:
            print("[WARN] Chromium falló:", repr(e))
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page(ignore_https_errors=True) 

        await load_grafana_and_grab(page)

        # Scraping PM2.5, PM10 y AQI
        pm25_stations = await page.query_selector_all("section[data-testid*='Material Particulado 2.5'] div[style*='text-align: center;']")
        pm25_values = await page.query_selector_all("section[data-testid*='Material Particulado 2.5'] span.flot-temp-elem")
        for s, v in zip(pm25_stations, pm25_values):
            station_name = await s.inner_text()
            pm25_value = await v.inner_text()
            stations_data[station_name] = {"PM2.5": pm25_value}

        # Scraping PM10
        pm10_stations = await page.query_selector_all("section[data-testid*='Material Particulado 10'] div[style*='text-align: center;']")
        pm10_values = await page.query_selector_all("section[data-testid*='Material Particulado 10'] span.flot-temp-elem")
        for s, v in zip(pm10_stations, pm10_values):
            name = await s.inner_text()
            stations_data.setdefault(name, {})  # Crear estación si no existe
            stations_data[name]["PM10"] = await v.inner_text()

        # Scraping AQI
        try:
            aqi_stations = await page.query_selector_all("div[data-testid='data-testid Bar gauge value'] span")
            for idx, station in enumerate(stations_data.keys()):
                try:
                    stations_data[station]["AQI"] = int(await aqi_stations[idx].inner_text())
                except:
                    stations_data[station]["AQI"] = None
        except Exception as e:
            print("Error AQI:", e)

        print("Stations scraped:", stations_data)

        # Guardar los datos en la base de datos
        for station_name, data in stations_data.items():
            normalized_name = normalize_station_name(station_name)

            estacion, created = await get_or_create_estacion(normalized_name)

            for contaminante_name, contaminante_value in data.items():
                contaminante, _ = await get_or_create_contaminante(contaminante_name)

                await create_medicion(estacion, contaminante, contaminante_value)

        await browser.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())