from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from cadastro_paciente.models import CadastroPaciente
from django.db.models import Count, Sum, Q, Value
from django.db.models.functions import TruncMonth, Coalesce
from datetime import timedelta

class Agenda(models.Model):
    STATUS_CHOICES = [
        ('Não enviado', 'Não enviado'),
        ('Aguardando envio', 'Aguardando envio'),
        ('Enviado', 'Enviado'),
        ('Aguardando confirmação', 'Aguardando confirmação'),
        ('Falha', 'Falha no envio')
    ]
    
    date = models.DateTimeField("Data e Hora da Consulta")
    paciente = models.ForeignKey(CadastroPaciente, on_delete=models.CASCADE)
    horario_lembrete = models.DateTimeField("Horário do Lembrete", null=True, blank=True)
    terapeuta = models.ForeignKey(User, on_delete=models.CASCADE)
    confirmada = models.BooleanField(default=False)
    status_lembrete = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Não enviado'
    )

    valor_consulta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('200.00')
    )
    
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        return f"{self.paciente.nome} - {self.date.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def get_dashboard_data(cls, terapeuta, meses=6, paciente_id=None):
        data_fim = timezone.now()
        data_inicio = data_fim - timedelta(days=30*meses)
        filters = {
            'terapeuta': terapeuta,
            'date__range': [data_inicio, data_fim]
        }
        if paciente_id and paciente_id != 'todos':
            filters['paciente_id'] = paciente_id
            
        return cls.objects.filter(**filters).annotate(
            mes=TruncMonth('date')
        ).values('mes').annotate(
            total=Count('id'),
            confirmadas=Count('id', filter=Q(confirmada=True)),
            canceladas=Count('id', filter=Q(confirmada=False)),
            faturamento=Coalesce(Sum('valor_consulta', filter=Q(confirmada=True)), Value(0))
        ).order_by('mes')
    
    @classmethod
    def get_summary_data(cls, terapeuta, paciente_id=None):
        hoje = timezone.now().date()
        primeiro_dia_mes = hoje.replace(day=1)
        
        filters = {
            'terapeuta': terapeuta,
            'date__gte': primeiro_dia_mes
        }
        
        if paciente_id and paciente_id != 'todos':
            filters['paciente_id'] = paciente_id
            
        consultas_mes = cls.objects.filter(**filters).count()
        
        consultas_hoje = cls.objects.filter(
            **filters,
            date__date=hoje,
            confirmada=True
        ).count()
        
        faturamento = cls.objects.filter(
            **filters,
            confirmada=True
        ).aggregate(
            total=Coalesce(Sum('valor_consulta'), Value(0))
        )
        
        return {
            'consultas_mes': consultas_mes,
            'consultas_hoje': consultas_hoje,
            'faturamento_mes': faturamento['total']
        }