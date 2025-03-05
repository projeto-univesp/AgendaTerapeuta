from django.db import models
from django.contrib.auth.models import User
from cadastro_paciente.models import CadastroPaciente

class Agenda(models.Model):
    date = models.DateTimeField()
    paciente = models.ForeignKey(CadastroPaciente, on_delete=models.CASCADE)
    terapeuta = models.ForeignKey(User, on_delete=models.CASCADE)
    confirmada = models.BooleanField(default=False)
    status_lembrete = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"{self.paciente.nome} - {self.date}"