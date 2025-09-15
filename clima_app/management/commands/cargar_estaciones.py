from django.core.management.base import BaseCommand
from clima_app.models import Estacion

class Command(BaseCommand):
    help = "Carga las estaciones de AMDC en la tabla Estacion"

    def handle(self, *args, **options):
        estaciones = [
            # --- OpenAQ (Sustenta Honduras) ---
            {"nombre": "Lamaní Instituto - Sustenta", "fuente": "OpenAQ", "Lat": 14.1982759, "Lon": -87.6259912, "external_id": 3293767},
            {"nombre": "Lamaní Tablazón - Sustenta", "fuente": "OpenAQ", "Lat": 14.1434025, "Lon": -87.6402344, "external_id": 3294183},
            {"nombre": "Dulce Nombre de Culmí, Olancho - Sustenta", "fuente": "OpenAQ", "Lat": 15.0842959, "Lon": -85.5583524, "external_id": 3459201},
            {"nombre": "El Negrito, Yoro - Sustenta", "fuente": "OpenAQ", "Lat": 15.3129054, "Lon": -87.6982085, "external_id": 3543965},
            {"nombre": "Santa Rita, Yoro - Sustenta", "fuente": "OpenAQ", "Lat": 15.207804, "Lon": -87.8769283, "external_id": 3544957},
            {"nombre": "Danlí - Sustenta", "fuente": "OpenAQ", "Lat": 14.0363553, "Lon": -86.5762886, "external_id": 3789589},
            {"nombre": "Zamorano IAD - Sustenta", "fuente": "OpenAQ", "Lat": 14.0150475, "Lon": -87.0029999, "external_id": 3801453},
            {"nombre": "Copán Ruinas - Sustenta", "fuente": "OpenAQ", "Lat": 14.851743, "Lon": -89.150757, "external_id": 4808366},
            {"nombre": "Sambo Creek - Sustenta", "fuente": "OpenAQ", "Lat": 15.790178, "Lon": -86.630999, "external_id": 4808368},
            {"nombre": "Cantarranas, Francisco Morazán - Sustenta", "fuente": "OpenAQ", "Lat": 14.2630112, "Lon": -87.0275666, "external_id": 4959160},
            {"nombre": "Roatán RMP - Sustenta", "fuente": "OpenAQ", "Lat": 16.3050969, "Lon": -86.5934014, "external_id": 5456449},

            # --- IQAir (Sin Sustenta) ---
            # Tegucigalpa, Francisco Morazan -> ICA: 17, Coords: [-87.20681, 14.0818]
            # San Pedro Sula, Cortes -> ICA: 14, Coords: [-88.025, 15.50417]
            # Choloma, Cortes -> ICA: 14, Coords: [-87.95302, 15.61444]
            # Comayagua, Comayagua -> ICA: 33, Coords: [-87.6375, 14.45139]
            # Siguatepeque, Comayagua -> ICA: 49, Coords: [-87.84551, 14.63438]

            # --- AMDC ---
            # {"nombre": "21 de Octubre", "fuente": "AMDC"},
            # {"nombre": "Bomberos Juana Laínez", "fuente": "AMDC"},
            # {"nombre": "Kennedy", "fuente": "AMDC"},
            # {"nombre": "Planta Concepción", "fuente": "AMDC"},
            # {"nombre": "Planta Laureles", "fuente": "AMDC"},
            # {"nombre": "Planta Picacho", "fuente": "AMDC"},
            # {"nombre": "SAT AMDC: UMAPS", "fuente": "AMDC"}
        ]

        for est in estaciones:
            obj, created = Estacion.objects.get_or_create(
                nombre=est["nombre"],
                    defaults={
                        "fuente": est.get("fuente"),
                        "lat": est.get("Lat"),
                        "lon": est.get("Lon"),
                        "external_id": est.get("external_id"),
                    }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Estación agregada: {est['nombre']}"))
            else:
                self.stdout.write(f"… Ya existía: {est['nombre']}")
