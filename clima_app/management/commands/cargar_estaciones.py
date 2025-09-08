from django.core.management.base import BaseCommand
from clima_app.models import Estacion

class Command(BaseCommand):
    help = "Carga las estaciones de IQAir, OpenAQ y AMDC en la tabla Estacion"

    def handle(self, *args, **options):
        estaciones = [
            # --- IQAir ---
            {"nombre": "Comayagua (IQAir)", "fuente": "IQAir", "lat": 14.45139, "lon": -87.6375},
            {"nombre": "Lamani (IQAir)", "fuente": "IQAir", "lat": 14.2000, "lon": -87.61667},
            {"nombre": "Copan (IQAir)", "fuente": "IQAir", "lat": 14.83333, "lon": -89.15},
            {"nombre": "San Pedro Sula (IQAir)", "fuente": "IQAir", "lat": 15.50417, "lon": -88.025},
            {"nombre": "El Terrero, Francisco Morazán (IQAir)", "fuente": "IQAir", "lat": 14.06667, "lon": -87.06667},
            {"nombre": "Tegucigalpa (IQAir)", "fuente": "IQAir", "lat": 14.0818, "lon": -87.20681},
            {"nombre": "Dulce Nombre de Culmí, Olancho (IQAir)", "fuente": "IQAir", "lat": 15.1, "lon": -85.53333},
            {"nombre": "Agua Blanca Sur, Yoro (IQAir)", "fuente": "IQAir", "lat": 15.25, "lon": -87.88333},
            {"nombre": "El Negrito, Yoro (IQAir)", "fuente": "IQAir", "lat": 15.31667, "lon": -87.7},

            # --- OpenAQ (Sustenta Honduras) ---
            {"nombre": "Lamaní Instituto - Sustenta", "fuente": "OpenAQ", "lat": 14.1982759, "lon": -87.6259912, "external_id": 3293767},
            {"nombre": "Lamaní Tablazón - Sustenta", "fuente": "OpenAQ", "lat": 14.1434025, "lon": -87.6402344, "external_id": 3294183},
            {"nombre": "Dulce Nombre de Culmí, Olancho - Sustenta", "fuente": "OpenAQ", "lat": 15.0842959, "lon": -85.5583524, "external_id": 3459201},
            {"nombre": "El Negrito, Yoro - Sustenta", "fuente": "OpenAQ", "lat": 15.3129054, "lon": -87.6982085, "external_id": 3543965},
            {"nombre": "Santa Rita, Yoro - Sustenta", "fuente": "OpenAQ", "lat": 15.207804, "lon": -87.8769283, "external_id": 3544957},
            {"nombre": "Danlí - Sustenta", "fuente": "OpenAQ", "lat": 14.0363553, "lon": -86.5762886, "external_id": 3789589},
            {"nombre": "Zamorano IAD - Sustenta", "fuente": "OpenAQ", "lat": 14.0150475, "lon": -87.0029999, "external_id": 3801453},
            {"nombre": "El Negrito, Yoro (dup) - Sustenta", "fuente": "OpenAQ", "lat": 15.3128333, "lon": -87.6981111, "external_id": 4773413},
            {"nombre": "Copán Ruinas - Sustenta", "fuente": "OpenAQ", "lat": 14.851743, "lon": -89.150757, "external_id": 4808366},
            {"nombre": "Sambo Creek - Sustenta", "fuente": "OpenAQ", "lat": 15.790178, "lon": -86.630999, "external_id": 4808368},
            {"nombre": "Cantarranas, Francisco Morazán - Sustenta", "fuente": "OpenAQ", "lat": 14.2630112, "lon": -87.0275666, "external_id": 4959160},
            {"nombre": "Roatán RMP - Sustenta", "fuente": "OpenAQ", "lat": 16.3050969, "lon": -86.5934014, "external_id": 5456449},

            # --- AMDC (Scraping, Tegucigalpa) ---
            {"nombre": "AMDC 21 de Octubre", "fuente": "AMDC"},
            {"nombre": "AMDC Bomberos Juana Laínez", "fuente": "AMDC"},
            {"nombre": "AMDC Kennedy", "fuente": "AMDC"},
            {"nombre": "AMDC Planta Concepción", "fuente": "AMDC"},
            {"nombre": "AMDC Planta Laureles", "fuente": "AMDC"},
            {"nombre": "AMDC Planta Picacho", "fuente": "AMDC"},
            {"nombre": "SAT AMDC: UMAPS", "fuente": "AMDC"},
        ]

        for est in estaciones:
            obj, created = Estacion.objects.get_or_create(
                nombre=est["nombre"],
                defaults={
                    "fuente": est.get("fuente"),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Estación agregada: {est['nombre']}"))
            else:
                self.stdout.write(f"… Ya existía: {est['nombre']}")
