from django.contrib import admin
from .models import Contaminante, Entidad, Localidad, Estacion, NivelICA, Medicion, NivelesContaminantes

# Registro de modelos en el admin
admin.site.register(Contaminante)
admin.site.register(Entidad)
admin.site.register(Localidad)
admin.site.register(Estacion)
admin.site.register(NivelICA)
admin.site.register(Medicion)
admin.site.register(NivelesContaminantes)
