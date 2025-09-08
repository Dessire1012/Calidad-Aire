from django.db import models

class Contaminante(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Entidad(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

class Localidad(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

from django.db import models

class Estacion(models.Model):
    FUENTE_CHOICES = [
        ('OpenAQ', 'OpenAQ'),
        ('IQAir', 'IQAir'),
        ('AMDC', 'AMDC'),
    ]

    nombre = models.CharField(max_length=150)
    fuente = models.CharField(max_length=20, choices=FUENTE_CHOICES, default='OpenAQ')

    # Identificador externo (ej. OpenAQ location_id)
    external_id = models.IntegerField(null=True, blank=True)

    # Coordenadas
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.fuente})"


class NivelICA(models.Model):
    # Clasificación de la calidad del aire respecto a la salud
    CLASIFICACION_CHOICES = [
        ('Excelente', 'Excelente'),
        ('Bueno', 'Bueno'),
        ('Regular', 'Regular'),
        ('Malo', 'Malo'),
        ('Muy Malo', 'Muy Malo'),
        ('Crítico', 'Crítico'),
    ]
    
    nivel = models.CharField(max_length=50)
    rango_min = models.FloatField()
    rango_max = models.FloatField()

    color_seleccionado = models.CharField(
        max_length=20,
        choices=[
            ('Verde', 'Verde'),
            ('Amarillo', 'Amarillo'),
            ('Naranja', 'Naranja'),
            ('Rojo', 'Rojo'),
            ('Morado', 'Morado'),
            ('Marrón', 'Marrón'),
        ],
        default='Verde'
    )

    # Color en formato hexadecimal
    color_hex = models.CharField(max_length=7,  default='#FFFFFF')  # Ejemplo: "#FF0000"

    # Clasificación respecto a la salud
    clasificacion_salud = models.CharField(
        max_length=20,
        choices=CLASIFICACION_CHOICES,
        default='Bueno'
    )

    def __str__(self):
        return self.nivel

class Medicion(models.Model):
    estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    fecha = models.DateTimeField() 
    contaminante = models.ForeignKey(Contaminante, on_delete=models.CASCADE)
    valor = models.FloatField()

    def __str__(self):
        return f"{self.estacion.nombre} - {self.fecha} - {self.contaminante.nombre}"

class NivelesContaminantes(models.Model):
    nivel_ica = models.ForeignKey(NivelICA, on_delete=models.CASCADE)
    contaminante = models.ForeignKey(Contaminante, on_delete=models.CASCADE)
    valor_maximo = models.FloatField()

    def __str__(self):
        return f"{self.nivel_ica} - {self.contaminante.nombre}"
