from django.urls import path
from . import views

urlpatterns = [
    path('', views.agenda, name='agenda'),  # Rota para a página principal da agenda
    path('criar_consulta/', views.criar_consulta, name='criar_consulta'),
    path('deletar_consulta/<int:id_agenda>/', views.deletar_consulta, name='deletar_consulta'),
    path('enviar_lembretes/', views.enviar_lembretes, name='enviar_lembretes'),
]