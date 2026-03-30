from django.db import models
from ventas.models import Venta


class Pago(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    monto = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True, verbose_name="Descripción / Nota")

    def __str__(self):
        return f"Pago ${self.monto} - Venta #{self.venta.id}"


# Proxy model para mostrar ventas pendientes en el módulo de pagos
class VentaPendiente(Venta):
    class Meta:
        proxy = True
        verbose_name = "Venta Pendiente"
        verbose_name_plural = "Ventas Pendientes de Pago"
