from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campanas', '0001_initial'),
        ('ventas', '0007_detalleventastock_costo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venta',
            name='campana',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='campanas.campana'
            ),
        ),
    ]
