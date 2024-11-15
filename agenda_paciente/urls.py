from django.urls import path
from .views import agenda, criar_consulta_paciente, deletar_consulta

urlpatterns = [
    path('paciente/', agenda, name='agenda_paciente'),
    path('criarconsulta/', criar_consulta_paciente, name='criar_consulta_paciente'),
    path('deletar_consulta/<int:id_agenda>/', deletar_consulta, name='deletar_consulta_paciente'),
]