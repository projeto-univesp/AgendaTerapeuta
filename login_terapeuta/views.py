from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import redirect

def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        user = User.objects.filter(username=username).first()

        if user:
            return render(request, 'usuario_existente.html')
        
        user = User.objects.create_user(username=username, email=email, password=senha)
        user.save()
        return redirect(login)

def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)

        if user:
            login_(request, user)
            return redirect(plataforma)
        else:
            return render(request, 'invalido.html')

@login_required(login_url="/auth/login/")
def plataforma(request):
    url_home = reverse('home')
    return redirect(url_home)
    #return render(request, 'cadastro_paciente/ca')
    #return HttpResponse('Plataforma')