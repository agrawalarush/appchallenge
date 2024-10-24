# Generated by Django 4.2.16 on 2024-10-20 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_delete_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20)),
                ('password1', models.CharField(max_length=100)),
                ('password2', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=75)),
                ('location', models.CharField(max_length=50)),
                ('email_verified', models.BooleanField(default=False)),
            ],
        ),
    ]
