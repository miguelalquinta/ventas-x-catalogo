from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum

from clientes.models import Cliente
from campanas.models import Campana
from vendedores.models import Vendedor
from productos.models import ProductoCampana
from stock.models import ProductoStock


# =========================
# 🧾 VENTA
# =========================
class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    campana = models.ForeignKey(
        Campana, on_delete=models.CASCADE,
        null=True, blank=True  # FIX: opcional para ventas de stock sin campaña
    )
    fecha = models.DateTimeField(auto_now_add=True)
    vendedor = models.ForeignKey(
        Vendedor, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    total = models.IntegerField(default=0)

    def __str__(self):
        if self.campana:
            return f"{self.cliente} - {self.campana} - Venta #{self.id}"
        return f"{self.cliente} - Stock - Venta #{self.id}"

    def calcular_total(self):
        total_catalogo = sum(d.subtotal for d in self.detalleventa_set.all())
        total_stock = sum(d.subtotal for d in self.detalleventastock_set.all())
        self.total = total_catalogo + total_stock
        self.save()

    def total_pagado(self):
        from pagos.models import Pago
        return Pago.objects.filter(venta=self).aggregate(total=Sum('monto'))['total'] or 0

    def saldo_pendiente(self):
        return self.total - self.total_pagado()

    def ganancia_total(self):
        total = 0
        for d in self.detalleventa_set.all():
            total += d.ganancia()
        for d in self.detalleventastock_set.all():
            total += d.ganancia()
        return total


# =========================
# 📦 DETALLE VENTA CATÁLOGO
# =========================
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto_campana = models.ForeignKey(ProductoCampana, on_delete=models.CASCADE)

    cantidad = models.IntegerField()
    subtotal = models.IntegerField(default=0)
    costo = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.producto_campana.producto.nombre} x{self.cantidad}"

    def save(self, *args, **kwargs):
        # Validar que la campaña esté activa (solo al crear)
        if not self.pk:
            campana = self.producto_campana.campana
            if not campana.activa:
                raise ValidationError(
                    f"La campaña '{campana.nombre}' está cerrada. No se pueden agregar productos de campañas cerradas."
                )

        # Solo validar campaña si la venta tiene campaña asignada
        if self.venta.campana and self.producto_campana.campana != self.venta.campana:
            raise ValidationError("El producto no pertenece a la campaña")

        # FIX #2: Guardar costo solo al crear (no sobreescribir en ediciones)
        if not self.pk:
            self.costo = self.producto_campana.costo

        self.subtotal = self.producto_campana.precio * self.cantidad

        super().save(*args, **kwargs)
        self.venta.calcular_total()

    def delete(self, *args, **kwargs):
        venta = self.venta
        super().delete(*args, **kwargs)
        venta.calcular_total()

    def ganancia(self):
        return (self.producto_campana.precio - self.costo) * self.cantidad


# =========================
# 🏪 DETALLE VENTA STOCK
# =========================
class DetalleVentaStock(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto_stock = models.ForeignKey(ProductoStock, on_delete=models.CASCADE)

    cantidad = models.IntegerField()
    precio = models.IntegerField(blank=True, null=True)
    subtotal = models.IntegerField(default=0)
    costo = models.IntegerField(default=0)  # FIX: guardar costo histórico

    def __str__(self):
        return f"{self.producto_stock.nombre} x{self.cantidad}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # FIX #1: detectar si es creación o edición

        if not self.precio:
            self.precio = self.producto_stock.precio_sugerido

        if is_new:
            # FIX #1: Solo validar y descontar stock al CREAR (no al editar)
            if self.cantidad > self.producto_stock.cantidad:
                raise ValidationError("No hay suficiente stock disponible")
            # FIX: Guardar costo histórico al crear
            self.costo = self.producto_stock.costo
        else:
            # FIX #5: Al editar, recuperar cantidad anterior para validar correctamente
            cantidad_anterior = DetalleVentaStock.objects.get(pk=self.pk).cantidad
            diferencia = self.cantidad - cantidad_anterior
            if diferencia > 0 and diferencia > self.producto_stock.cantidad:
                raise ValidationError("No hay suficiente stock disponible")

        self.subtotal = self.precio * self.cantidad

        super().save(*args, **kwargs)

        if is_new:
            # FIX #1: Solo descontar stock al CREAR
            self.producto_stock.descontar_stock(self.cantidad)
        else:
            # FIX #5: Al editar, ajustar la diferencia de stock
            diferencia = self.cantidad - cantidad_anterior
            if diferencia > 0:
                self.producto_stock.descontar_stock(diferencia)
            elif diferencia < 0:
                self.producto_stock.agregar_stock(abs(diferencia))

        self.venta.calcular_total()

    def delete(self, *args, **kwargs):
        self.producto_stock.agregar_stock(self.cantidad)

        venta = self.venta
        super().delete(*args, **kwargs)
        venta.calcular_total()

    def ganancia(self):
        return (self.precio - self.costo) * self.cantidad
