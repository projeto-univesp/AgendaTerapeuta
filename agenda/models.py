from django.db import models
from cadastro_paciente.models import CadastroPaciente
from django.contrib.auth.models import User

class Agenda(models.Model):
    _id = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    _idPaciente = models.ForeignKey(CadastroPaciente, on_delete=models.CASCADE)
    terapeuta = models.ForeignKey(User, on_delete=models.CASCADE, null=True)