from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0001_initial'),
        ('ventas', '0008_venta_campana_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='pago',
            name='descripcion',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Descripción / Nota'),
        ),
        migrations.CreateModel(
            name='VentaPendiente',
            fields=[],
            options={
                'verbose_name': 'Venta Pendiente',
                'verbose_name_plural': 'Ventas Pendientes de Pago',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('ventas.venta',),
        ),
    ]
