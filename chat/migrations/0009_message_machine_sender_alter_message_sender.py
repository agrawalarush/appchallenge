# Generated by Django 4.2.16 on 2024-10-21 21:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0008_alter_chatroomuser_user_alter_message_sender'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='machine_sender',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
