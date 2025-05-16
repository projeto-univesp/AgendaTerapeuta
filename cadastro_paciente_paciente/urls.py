from django.urls import path
from . import views

urlpatterns = [
    path('', views.paciente, name='home_paciente'),
    path('cadastrar/', views.pagina_cadastrar, name='pagina_cadastrar'),
    path('salvar/', views.salvar, name='salvar'),
    path('sair/', views.logout_confirmar, name='sair'),        # mostra a tela de confirmação
    path('logout/', views.tela_logout, name='logout_paciente'), # realmente faz o logout
    path('editar/<int:idPaciente>/', views.editar, name='editar'),
    path('atualizar/<int:idPaciente>/', views.atualizar, name='atualizar'),
]