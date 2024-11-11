from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

def pagina_inicial(request):
    return render(request, 'pagina_inicial/pagina_inicial.html')
