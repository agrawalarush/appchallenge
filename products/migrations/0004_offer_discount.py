# Generated by Django 4.2.16 on 2024-10-03 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_rename_offers_offer'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='discount',
            field=models.FloatField(default=1.0),
            preserve_default=False,
        ),
    ]
