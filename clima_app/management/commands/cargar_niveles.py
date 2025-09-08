from django.core.management.base import BaseCommand
from clima_app.models import NivelICA

class Command(BaseCommand):
    help = "Carga los niveles oficiales del ICA (Air Quality Index) en la tabla Nivel_ICA"

    def handle(self, *args, **options):
        niveles = [
            {
                "nivel": "Excelente",
                "rango_min": 0,
                "rango_max": 50,
                "color_seleccionado": "Verde",
                "color_hex": "#00E400",
                "clasificacion_salud": "Excelente"
            },
            {
                "nivel": "Bueno",
                "rango_min": 51,
                "rango_max": 100,
                "color_seleccionado": "Amarillo",
                "color_hex": "#FFFF00",
                "clasificacion_salud": "Bueno"
            },
            {
                "nivel": "Regular",
                "rango_min": 101,
                "rango_max": 150,
                "color_seleccionado": "Naranja",
                "color_hex": "#FF7E00",
                "clasificacion_salud": "Regular"
            },
            {
                "nivel": "Malo",
                "rango_min": 151,
                "rango_max": 200,
                "color_seleccionado": "Rojo",
                "color_hex": "#FF0000",
                "clasificacion_salud": "Malo"
            },
            {
                "nivel": "Muy Malo",
                "rango_min": 201,
                "rango_max": 300,
                "color_seleccionado": "Morado",
                "color_hex": "#8F3F97",
                "clasificacion_salud": "Muy Malo"
            },
            {
                "nivel": "Extremadamente Malo",
                "rango_min": 301,
                "rango_max": 500,
                "color_seleccionado": "Marrón",
                "color_hex": "#7E0023",
                "clasificacion_salud": "Muy Malo"
            },
        ]

        for n in niveles:
            obj, created = NivelICA.objects.get_or_create(
                nivel=n["nivel"],
                defaults={
                    "rango_min": n["rango_min"],
                    "rango_max": n["rango_max"],
                    "color_seleccionado": n["color_seleccionado"],
                    "color_hex": n["color_hex"],
                    "clasificacion_salud": n["clasificacion_salud"],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Nivel ICA agregado: {n['nivel']}"))
            else:
                self.stdout.write(f"… Ya existía: {n['nivel']}")
