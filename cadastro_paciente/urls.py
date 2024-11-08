from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePaciente, name='homePaciente'),
    path('listar/', views.listar, name='listar'),
    path('buscar/', views.buscar, name='buscar'),
    path('resultado/', views.buscar_resultados, name='resultado'),
    path('visualizar/<int:idPaciente>/', views.visualizar_paciente, name='visualizar_paciente'),
    path('cadastrar/', views.pagina_cadastrar, name='cadastrar_pagina'),
    path('salvar/', views.salvar, name='salvar_paciente'),
    path('editar/<int:idPaciente>/', views.editar, name='editar'),
    path('atualizar/<int:idPaciente>/', views.atualizar, name='atualizar'),
    path('deletar/<int:idPaciente>/', views.deletar, name='deletar'),
]