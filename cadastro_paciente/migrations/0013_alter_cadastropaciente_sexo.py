# Generated by Django 5.1.1 on 2024-11-07 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro_paciente', '0012_alter_cadastropaciente_estado_civil'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cadastropaciente',
            name='sexo',
            field=models.CharField(choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')], max_length=30, null=True),
        ),
    ]