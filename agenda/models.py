from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cadastro_paciente.models import CadastroPaciente

class Agenda(models.Model):
    STATUS_CHOICES = [
        ('Não enviado', 'Não enviado'),
        ('Aguardando envio', 'Aguardando envio'),
        ('Enviado', 'Enviado'),
        ('Falha', 'Falha no envio')
    ]
    
    date = models.DateTimeField(verbose_name="Data e Hora da Consulta")
    paciente = models.ForeignKey(CadastroPaciente, on_delete=models.CASCADE, verbose_name="Paciente")
    terapeuta = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Terapeuta")
    confirmada = models.BooleanField(default=False, verbose_name="Consulta Confirmada")
    status_lembrete = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Não enviado',
        verbose_name="Status do Lembrete"
    )
    horario_lembrete = models.TimeField(
        verbose_name="Horário do Lembrete",
        help_text="Horário em que o lembrete será enviado no dia anterior à consulta"
    )
    
    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ['date']
    
    def __str__(self):
        return f"{self.paciente.nome} - {self.date.strftime('%d/%m/%Y %H:%M')}"
    
    def get_data_formatada(self):
        return self.date.strftime('%d/%m/%Y às %H:%M')