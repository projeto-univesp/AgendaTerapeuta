# Generated by Django 5.1.2 on 2024-11-04 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_terapeuta', '0004_alter_perfil_celular_alter_perfil_cpf'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]