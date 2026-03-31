from django.db import models
class InformesConfig(models.Model):
    nombre = models.CharField(max_length=100, default="Informes")
    class Meta:
        app_label = 'informes'
        verbose_name = 'Configuración de Informes'
    def __str__(self):
        return self.nombre
