from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/paciente/', views.cadastro, name='cadastropaciente'),
    path('login/paciente/', views.login, name="loginpaciente"),
    path('plataforma/', views.plataforma, name="plataforma")
]