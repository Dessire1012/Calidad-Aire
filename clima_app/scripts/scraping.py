import os
import sys
import django
from playwright.sync_api import sync_playwright
from pathlib import Path

# --- Django setup ---
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "ProyectoClima"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.getenv("DJANGO_SETTINGS_MODULE", "ProyectoClima.settings"))
django.setup()

from clima_app.models import Medicion, Estacion, Contaminante  # noqa: F401

URL = "https://estaciones.simet.amdc.hn/public-dashboards/e4d697a0e31647008370b09a592c0129?orgId=1&from=now-24h&to=now"

def load_grafana_and_grab(page):
    failed_assets = []

    # Monitoreo de respuestas de assets (JS, CSS, etc)
    def on_response(resp):
        url = resp.url
        if "/public/build/" in url:
            try:
                status = resp.status
            except Exception:
                status = "?"
            print(f"[ASSET] {status} {url}")
            if status != 200:
                failed_assets.append((status, url))

    page.on("response", on_response)

    # Intentos de recarga
    for attempt in range(1, 4):
        print(f"[INFO] Navegando (intento {attempt}/3): {URL}")
        page.goto(URL, timeout=300_000, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle", timeout=300_000)

        # Debug inicial
        try:
            title = page.title()
            body_sample = page.inner_text("body")[:300]
        except Exception as e:
            title, body_sample = f"<sin título> ({e})", ""
        print(f"[DEBUG] Título: {title}")
        print(f"[DEBUG] Body(300): {repr(body_sample)}")

        # Si aparece el preloader de fallo, intenta recargar
        if "Grafana has failed to load its application files" in body_sample:
            print("[WARN] Preloader de fallo detectado. Esperando 5s y reintentando…")
            page.wait_for_timeout(5000)
            continue

        # Espera a que se rendericen al menos 6 canvas
        try:
            page.wait_for_function("document.querySelectorAll('canvas').length >= 6", timeout=300_000)
        except Exception as e:
            print(f"[WARN] No se alcanzó el umbral de canvas: {e}. Reintentando…")
            continue

        # Establecer un viewport grande para no cortar nada
        try:
            page.set_viewport_size({"width": 5120, "height": 2880})
        except Exception:
            pass

        # Capturas siempre para debug
        try:
            page.screenshot(path="scraping_test.png", full_page=True)
            html = page.content()
            with open("scraping_dump.html", "w", encoding="utf-8") as f:
                f.write(html[:200000])
            print("[INFO] Screenshot guardado: scraping_test.png")
            print("[INFO] Dump HTML guardado: scraping_dump.html")
        except Exception as e:
            print(f"[WARN] No se pudo guardar screenshot/dump: {e}")

        if failed_assets:
            print("[WARN] Algunos bundles no devolvieron 200. Ejemplos:")
            for st, u in failed_assets[:5]:
                print(f"       - {st} {u}")
        return page

    # Si fallaron todos los intentos
    print("[ERROR] No se pudo cargar Grafana tras 3 intentos. Guardando evidencia final…")
    try:
        page.screenshot(path="scraping_test.png", full_page=True)
        html = page.content()
        with open("scraping_dump.html", "w", encoding="utf-8") as f:
            f.write(html[:200000])
        print("[INFO] Screenshot guardado: scraping_test.png")
        print("[INFO] Dump HTML guardado: scraping_dump.html")
    except Exception as e:
        print(f"[WARN] No se pudo guardar evidencia final: {e}")
    return page

def get_text_safe(el):
    try:
        return el.inner_text().strip()
    except Exception:
        return ""

def run():
    stations_data = {}
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-software-rasterizer",
                ],
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

        # Cargar dashboard y generar evidencias
        load_grafana_and_grab(page)

        # ------- Scraping -------
        # PM2.5
        try:
            pm25_stations = page.query_selector_all("section:has-text('Material Particulado 2.5') div[style*='text-align: center;']")
            pm25_values   = page.query_selector_all("section:has-text('Material Particulado 2.5') span.flot-temp-elem")
            if not pm25_values:
                pm25_values = page.query_selector_all("section:has-text('Material Particulado 2.5') :text-matches('/\\d+/')")
            for s, v in zip(pm25_stations, pm25_values):
                stations_data[get_text_safe(s)] = {"PM2.5": get_text_safe(v)}
        except Exception as e:
            print("PM2.5 no disponible:", e)

        # PM10
        try:
            pm10_stations = page.query_selector_all("section:has-text('Material Particulado 10') div[style*='text-align: center;']")
            pm10_values   = page.query_selector_all("section:has-text('Material Particulado 10') span.flot-temp-elem")
            if not pm10_values:
                pm10_values = page.query_selector_all("section:has-text('Material Particulado 10') :text-matches('/\\d+/')")
            for s, v in zip(pm10_stations, pm10_values):
                name = get_text_safe(s)
                stations_data.setdefault(name, {})
                stations_data[name]["PM10"] = get_text_safe(v)
        except Exception as e:
            print("PM10 no disponible:", e)

        # AQI (opcional y tolerante a fallos; el selector puede variar en CI)
        try:
            # Varias opciones: gauges, roles ARIA, texto cercano a AQI, etc.
            aqi_candidates = page.query_selector_all(
                "div[role='graphics-symbol'] span, "
                "div[data-testid*='gauge'] span, "
                "text=/AQI/i"
            )
            # Asignar por índice si hay igual cantidad; de lo contrario, intenta mapear por orden visible
            station_keys = list(stations_data.keys())
            for idx, key in enumerate(station_keys):
                val = None
                if idx < len(aqi_candidates):
                    txt = get_text_safe(aqi_candidates[idx])
                    # extraer primer número
                    import re
                    m = re.search(r"\d+", txt or "")
                    if m:
                        val = int(m.group(0))
                stations_data[key]["AQI"] = val
        except Exception as e:
            print("AQI no disponible en esta corrida:", e)

        print("Stations scraped:", stations_data)
        browser.close()

if __name__ == "__main__":
    run()
