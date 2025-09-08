import os
import sys
import django
from django.utils import timezone

sys.path.append(r"C:\Users\dessi\ProyectoClima")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyectoClima.settings')

django.setup()

from clima_app.models import Medicion, Estacion, Contaminante

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración del navegador
chrome_options = Options()
chrome_options.binary_location = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

# Headless: no abrir ventana
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-plugins")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--no-default-browser-check")
chrome_options.add_argument("--no-first-run")
chrome_options.add_argument("--disable-background-networking")
chrome_options.add_argument("--disable-sync")
chrome_options.add_argument("--disable-translate")
chrome_options.add_argument("window-size=1920,1080")  

# Service para chromedriver
service = Service(executable_path="C:\\Windows\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Abrir URL
url = "https://estaciones.simet.amdc.hn/public-dashboards/e4d697a0e31647008370b09a592c0129?orgId=1&refresh=1m&from=now%2Fy&to=now"
driver.get(url)

# Zoom: necesario para ver todos los elementos correctamente
driver.execute_script("document.body.style.zoom='40%'")

# Espera general de carga
wait = WebDriverWait(driver, 10)

amdc_stations = [
    "21 de Octubre",
    "Bomberos Juana Lainez",
    "Kennedy",
    "Planta Concepción",
    "Planta Laureles",
    "Planta Picacho",
    "SAT AMDC: UMAPS"
]

stations_data = {}

# PM2.5
try:
    pm2_5_stations = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "section[data-testid*='Panel header Material Particulado 2.5 µg/m³'] div[style*='text-align: center;']")
        )
    )
    pm2_5_values = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "section[data-testid*='Panel header Material Particulado 2.5 µg/m³'] span.flot-temp-elem")
        )
    )

    for station, value in zip(pm2_5_stations, pm2_5_values):
        stations_data[station.text.strip()] = {"PM2.5": value.text.strip()}

except Exception as e:
    print("Error fetching PM2.5 data:", e)

# PM10
try:
    pm10_stations = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "section[data-testid*='Panel header Material Particulado 10 µ/m³'] div[style*='text-align: center;']")
        )
    )
    pm10_values = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "section[data-testid*='Panel header Material Particulado 10 µ/m³'] span.flot-temp-elem")
        )
    )

    for station, value in zip(pm10_stations, pm10_values):
        if station.text.strip() in stations_data:
            stations_data[station.text.strip()]["PM10"] = value.text.strip()
        else:
            stations_data[station.text.strip()] = {"PM10": value.text.strip()}

except Exception as e:
    print("Error fetching PM10 data:", e)

# AQI (Indice de calidad del aire)
try:
    aqi_stations = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div[data-testid='data-testid Bar gauge value'] span")
        )
    )

    # Asociar AQI según el orden de las estaciones
    for idx, station in enumerate(stations_data.keys()):
        try:
            stations_data[station]["AQI"] = int(aqi_stations[idx].text.strip())
        except:
            stations_data[station]["AQI"] = None

except Exception as e:
    print("Error fetching AQI numeric value:", e)

# --- Guardar en Django ---
pm25_obj = Contaminante.objects.get(nombre="PM2.5")
pm10_obj = Contaminante.objects.get(nombre="PM10")
ica_obj = Contaminante.objects.get(nombre="ICA")

for station_name, data in stations_data.items():
    try:
        estacion_obj = Estacion.objects.get(nombre=station_name)

        # Crear cada medición
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

driver.quit()
print("Script completado ✅")