from django.urls import path
from . import views

urlpatterns = [
    path('', views.paciente, name='home_paciente'),
    path('cadastrar/', views.pagina_cadastrar, name='pagina_cadastrar'),
    path('salvar/', views.salvar, name='salvar'),
    path('editar/<int:idPaciente>/', views.editar, name='editar'),
    path('atualizar/<int:idPaciente>/', views.atualizar, name='atualizar'),
]