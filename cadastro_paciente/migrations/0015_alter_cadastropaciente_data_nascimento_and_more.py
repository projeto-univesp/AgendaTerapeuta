# Generated by Django 5.1.2 on 2024-11-01 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro_paciente', '0014_alter_cadastropaciente_data_nascimento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cadastropaciente',
            name='data_nascimento',
            field=models.DateField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='cadastropaciente',
            name='sexo',
            field=models.CharField(max_length=100, null=True),
        ),
    ]