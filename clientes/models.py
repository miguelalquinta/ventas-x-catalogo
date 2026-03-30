from django.db import models
from django.db.models import Sum


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    def deuda_total(self):
        from ventas.models import Venta
        from pagos.models import Pago

        total_ventas = Venta.objects.filter(cliente=self).aggregate(total=Sum('total'))['total'] or 0
        total_pagado = Pago.objects.filter(venta__cliente=self).aggregate(total=Sum('monto'))['total'] or 0

        return total_ventas - total_pagado