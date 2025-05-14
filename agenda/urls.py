from django.urls import path
from .views import (
    homePaciente, listar, buscar, buscar_resultados, visualizar_paciente,
    salvar, pagina_cadastrar, editar, atualizar, deletar,
    agenda, criar_consulta, deletar_consulta, enviar_lembretes, 
    atualizar_horario_lembrete, verificar_lembretes_manual,
    dashboard, dashboard_data, confirmar_consulta
)

urlpatterns = [
    path('', homePaciente, name='homePaciente'),
    path('listar/', listar, name='listar'),
    path('buscar/', buscar, name='buscar'),
    path('buscar/resultados/', buscar_resultados, name='buscar_resultados'),
    path('visualizar/<int:idPaciente>/', visualizar_paciente, name='visualizar_paciente'),
    path('salvar/', salvar, name='salvar'),
    path('cadastrar/', pagina_cadastrar, name='pagina_cadastrar'),
    path('editar/<int:idPaciente>/', editar, name='editar'),
    path('atualizar/<int:idPaciente>/', atualizar, name='atualizar'),
    path('deletar/<int:idPaciente>/', deletar, name='deletar'),
    
    path('agenda/', agenda, name='agenda'),
    path('agenda/criar_consulta/', criar_consulta, name='criar_consulta'),
    path('agenda/deletar_consulta/<int:id_agenda>/', deletar_consulta, name='deletar_consulta'),
    path('agenda/enviar_lembretes/', enviar_lembretes, name='enviar_lembretes'),
    path('agenda/atualizar_horario_lembrete/<int:id_agenda>/', 
         atualizar_horario_lembrete, name='atualizar_horario_lembrete'),
    path('agenda/verificar_lembretes_manual/', verificar_lembretes_manual, name='verificar_lembretes_manual'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/data/', dashboard_data, name='dashboard_data'),
    path('confirmar_consulta/', confirmar_consulta, name='confirmar_consulta'),
]