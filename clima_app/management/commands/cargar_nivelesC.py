import csv
from django.core.management.base import BaseCommand
from clima_app.models import Contaminante, NivelICA, NivelesContaminantes

class Command(BaseCommand):
    help = "Carga los niveles de contaminantes en la tabla NivelesContaminantes desde un archivo CSV."

    def handle(self, *args, **options):
        try:
            # Abre el archivo CSV con la ruta correcta
           with open("niveles_contaminantes.csv", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                
                # Itera sobre cada fila en el archivo CSV
                for row in reader:
                    # Extraer los datos de cada fila
                    contaminante_nombre = row['Contaminante']
                    nivel_ica_nombre = row['Nivel ICA']
                    limite_inferior = float(row['Limite inferior'])
                    limite_superior = float(row['Limite superior'])
                    acciones = row['Acciones']
                    
                    try:
                        # Buscar el objeto NivelICA y Contaminante en la base de datos
                        nivel_ica = NivelICA.objects.get(nivel=nivel_ica_nombre)
                        contaminante = Contaminante.objects.get(nombre=contaminante_nombre)
                        
                        # Crear y guardar el objeto NivelesContaminantes
                        NivelesContaminantes.objects.create(
                            nivel_ica=nivel_ica,
                            contaminante=contaminante,
                            limite_inferior=limite_inferior,
                            limite_superior=limite_superior,
                            acciones=acciones
                        )

                        self.stdout.write(self.style.SUCCESS(f'Dato cargado: {contaminante_nombre} - {nivel_ica_nombre}'))
                    except NivelICA.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Nivel ICA {nivel_ica_nombre} no encontrado"))
                    except Contaminante.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"Contaminante {contaminante_nombre} no encontrado"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("No se pudo encontrar el archivo niveles_contaminantes.csv"))
