from django.urls import path, include

from home import views

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    path('logout1/', views.logout_view, name='logout1')
]
