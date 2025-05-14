from django.contrib import admin
from django.urls import path, include
from agenda.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('agenda/', include('agenda.urls')),
    path('auth/', include('login_terapeuta.urls')),
    path('auth/', include('login_pacientes.urls')),
    path('paciente/', include('cadastro_paciente.urls')),
    path('home/', include('home.urls')),
    path('pacientehome/', include('cadastro_paciente_paciente.urls')),
    path('agendapaciente/', include('agenda_paciente.urls')),
    path('', include('pagina_inicial.urls')),
    path('dashboard/', dashboard, name='dashboard'),
]