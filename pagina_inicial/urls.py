from django.urls import path, include

from pagina_inicial import views

urlpatterns = [
    path('', views.pagina_inicial, name='pagina_inicial'),
]