from django.db import models
from empresas.models import Empresa
from campanas.models import Campana


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class ProductoCampana(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    campana = models.ForeignKey(Campana, on_delete=models.CASCADE)

    precio = models.IntegerField()  # 💰 precio de venta
    costo = models.IntegerField(default=0)  # 💸 lo que tú pagas

    def __str__(self):
        return f"{self.producto} - {self.campana} - ${self.precio}"

    class Meta:
        unique_together = ('producto', 'campana')
        verbose_name = "Producto por campaña"
        verbose_name_plural = "Productos por campaña"

    # 💰 Ganancia por unidad
    def ganancia(self):
        return self.precio - self.costo

