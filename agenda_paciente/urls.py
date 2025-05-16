from django.urls import path
from .views import agenda, completar_cadastro, criar_consulta_paciente, deletar_consulta

urlpatterns = [
    path('paciente/', agenda, name='agenda_paciente'),
    path('criarconsulta/', criar_consulta_paciente, name='criar_consulta_paciente'),
    path('deletar_consulta/<int:id_agenda>/', deletar_consulta, name='deletar_consulta_paciente'),
    path('completar-cadastro/', completar_cadastro, name='completar_cadastro')
]