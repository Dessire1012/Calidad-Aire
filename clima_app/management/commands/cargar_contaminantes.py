from django.core.management.base import BaseCommand
from clima_app.models import Contaminante

class Command(BaseCommand):
    help = "Carga contaminantes base en la tabla Contaminante"

    def handle(self, *args, **options):
        contaminantes = [
            {"nombre": "PM1", "descripcion": "Partículas finas menores a 1 µm"},
            {"nombre": "PM2.5", "descripcion": "Partículas finas menores a 2.5 µm"},
            {"nombre": "PM10", "descripcion": "Partículas menores a 10 µm"},
            {"nombre": "O₃", "descripcion": "Ozono"},
            {"nombre": "NO₂", "descripcion": "Dióxido de nitrógeno"},
            {"nombre": "SO₂", "descripcion": "Dióxido de azufre"},
            {"nombre": "CO", "descripcion": "Monóxido de carbono"},
            {"nombre": "RH", "descripcion": "Humedad relativa"},
            {"nombre": "Temperatura", "descripcion": "Temperatura ambiente en °C"},
            {"nombre": "UM0.3", "descripcion": "Conteo de partículas ultrafinas <0.3 µm"},
            {"nombre": "ICA", "descripcion": "Índice de Calidad del Aire"},
        ]

        for c in contaminantes:
            obj, created = Contaminante.objects.get_or_create(
                nombre=c["nombre"],
                defaults={"descripcion": c["descripcion"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Contaminante agregado: {c['nombre']}"))
            else:
                self.stdout.write(f"… Ya existía: {c['nombre']}")
