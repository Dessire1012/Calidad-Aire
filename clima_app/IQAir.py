import requests
import time

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("IQAIR_API_KEY")

BASE_URL = "http://api.airvisual.com/v2"
COUNTRY = "Honduras"

states_with_cities = {
    "Comayagua": ["Comayagua", "Lamani"],
    "Copan": ["Copan"],
    "Cortes": ["San Pedro Sula"],
    "Francisco Morazan": ["El Terrero", "Tegucigalpa"],
    "Olancho": ["Dulce Nombre de Culmi"],
    "Yoro": ["Agua Blanca Sur", "El Negrito"]
}

def fetch_city_data():
    for state, cities in states_with_cities.items():
        for city in cities:
            url = f"{BASE_URL}/city"
            params = {
                "city": city,
                "state": state,
                "country": COUNTRY,
                "key": API_KEY
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    pollution = data["data"]["current"]["pollution"]
                    aqi = pollution.get("aqius")
                    main_pollutant = pollution.get("mainus")
                    coords = data["data"]["location"]["coordinates"]

                    print(f"City: {city}, State: {state}, AQI: {aqi}, "
                          f"Main: {main_pollutant}, Coords: {coords}")
                else:
                    print(f"API error for {city}, {state}: {data}")
            else:
                print(f"HTTP {response.status_code} for {city}, {state}")
                print(response.text)

            time.sleep(60)  

fetch_city_data()