# Generated by Django 4.2.16 on 2024-10-08 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_alter_product_description_alter_product_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='pay_every',
            field=models.CharField(default='per week', max_length=15),
        ),
    ]
