# Generated by Django 5.0.6 on 2024-05-18 20:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0002_agenda_delete_consulta'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agenda',
            name='_idTerapeuta',
        ),
    ]
