from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cadastro_paciente', '0018_alter_cadastropaciente_sexo'),  # Substitua pelo nome da última migração aplicada
    ]

    operations = [
        migrations.AddField(
            model_name='cadastropaciente',
            name='celular',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]