from django.db import models
from django.core.exceptions import ValidationError


class ProductoStock(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    cantidad = models.IntegerField(default=0)
    precio_sugerido = models.IntegerField()
    costo = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} (Stock: {self.cantidad})"

    # 💰 Ganancia por unidad
    def ganancia_unitaria(self):
        return self.precio_sugerido - self.costo

    # ➕ Agregar stock (PRO)
    def agregar_stock(self, cantidad):
        if cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0")

        self.cantidad += cantidad
        self.save()

        MovimientoStock.objects.create(
            producto=self,
            tipo='entrada',
            cantidad=cantidad
        )

    # ➖ Descontar stock (PRO)
    def descontar_stock(self, cantidad):
        if cantidad > self.cantidad:
            raise ValidationError("No hay suficiente stock")

        self.cantidad -= cantidad
        self.save()

        MovimientoStock.objects.create(
            producto=self,
            tipo='salida',
            cantidad=cantidad
        )


class MovimientoStock(models.Model):
    TIPO = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    )

    producto = models.ForeignKey(ProductoStock, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.tipo} - {self.cantidad}"