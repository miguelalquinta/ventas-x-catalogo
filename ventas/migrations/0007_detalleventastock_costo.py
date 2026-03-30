from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0006_alter_detalleventastock_precio'),
    ]

    operations = [
        migrations.AddField(
            model_name='detalleventastock',
            name='costo',
            field=models.IntegerField(default=0),
        ),
    ]
