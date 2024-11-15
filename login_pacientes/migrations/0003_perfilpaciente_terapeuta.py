# Generated by Django 5.1.2 on 2024-11-15 17:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_pacientes', '0002_rename_codigoacesso_perfilpaciente_codigo_acesso'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilpaciente',
            name='terapeuta',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='terapeuta_set', to=settings.AUTH_USER_MODEL),
        ),
    ]