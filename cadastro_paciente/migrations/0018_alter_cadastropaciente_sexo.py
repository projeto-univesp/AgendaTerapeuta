# Generated by Django 5.1.2 on 2024-11-08 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro_paciente', '0017_merge_20241108_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cadastropaciente',
            name='sexo',
            field=models.CharField(max_length=30, null=True),
        ),
    ]