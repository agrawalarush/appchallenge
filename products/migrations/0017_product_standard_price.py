# Generated by Django 4.2.16 on 2024-10-12 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_remove_product_in_cart_cartitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='standard_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
            preserve_default=False,
        ),
    ]
