from django.urls import path
from .views import (
    agenda, criar_consulta, deletar_consulta, enviar_lembretes, 
    atualizar_horario_lembrete, verificar_lembretes_manual,
    dashboard, dashboard_data, confirmar_consulta
)

urlpatterns = [
    path('', agenda, name='agenda'),
    path('criar_consulta/', criar_consulta, name='criar_consulta'),
    path('deletar_consulta/<int:id_agenda>/', deletar_consulta, name='deletar_consulta'),
    path('enviar_lembretes/', enviar_lembretes, name='enviar_lembretes'),
    path('atualizar_horario_lembrete/<int:id_agenda>/', 
         atualizar_horario_lembrete, name='atualizar_horario_lembrete'),
    path('verificar_lembretes_manual/', verificar_lembretes_manual, name='verificar_lembretes_manual'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/data/', dashboard_data, name='dashboard_data'),
    path('confirmar_consulta/', confirmar_consulta, name='confirmar_consulta'),
]