from django.urls import path
from .views import home, salvar, editar, update, deletar, pagina_cadastrar, listar, buscar
urlpatterns = [
    path('cadastropacientes/', home, name='home'),
    path('listar/', listar, name="listar"),
    path('buscar/', buscar, name="buscar"),
    path('visualizar/<int:idPaciente>/', views.visualizar_paciente, name='visualizar_paciente'),
    path('cadastrar/', pagina_cadastrar, name="pagina_cadastrar"),
    path('salvar/', salvar, name="salvar"),
    path('editar/<int:id>', editar, name="editar"),
    path('update/<int:id>', update, name="update"),
    path('deletar/<int:id>', deletar, name="deletar")
]