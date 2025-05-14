from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as login_
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Perfil

def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    else:
        name = request.POST.get('nome')
        username = request.POST.get('username')
        cpf = request.POST.get('cpf')
        celular = request.POST.get('celular')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        # Verifica se o email, username ou cpf já existem
        if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists() or Perfil.objects.filter(cpf=cpf).exists():
            return render(request, 'usuario_existente.html')
        
        # Cria o usuário e o perfil
        user = User.objects.create_user(email=email, password=senha, username=username)
        user.save()
        Perfil.objects.create(usuario=user, name=name, cpf=cpf, celular=celular).save()
        
        return redirect('login')

def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        # Verifica se existe um usuário com o email fornecido
        try:
            user = User.objects.get(email=email)
            username = user.username  # Obtém o username para autenticação
        except User.DoesNotExist:
            return render(request, 'invalido.html')  # Retorna se o email não existir

        # Autentica com o username e a senha
        user = authenticate(username=username, password=senha)

        if user:
            login_(request, user)
            return redirect('home')
        else:
            return render(request, 'invalido.html')



#@login_required(login_url="/auth/login/")
def plataforma():
    url_home = reverse('home')
    return redirect(url_home)
    #return render(request, 'cadastro_paciente/ca')
    #return HttpResponse('Plataforma')