from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import redirect
from .models import PerfilPaciente
from login_terapeuta.models import Perfil
from login_terapeuta.views import User

def cadastro(request): #request é uma solicitacao feita por quem está querendo acessar o site
    if request.method == "GET": #Usado para solicitar dados do servidor. Por exemplo, quando você abre uma página, uma requisição GET é enviada para obter o conteúdo.
        return render(request, 'login_pacientes/cadastropacientes.html') 
    # renderizar uma página HTML como resposta a uma requisição. (renderizar: renderizar envolve preencher o HTML com dados dinâmicos para criar uma página completa que possa ser mostrada em um navegador.)
    # render() é uma função do Django usada para carregar um template HTML e enviá-lo como resposta ao cliente (normalmente, o navegador do usuário).
    # Passar o request como parâmetro na função render() é essencial em uma aplicação Django, pois ele contém informações fundamentais sobre a requisição que o servidor precisa para processar e responder corretamente
    # 'cadastropaciente.html': É o nome do arquivo de template HTML que será renderizado
    else:
        name = request.POST.get('name') #Post: Usado para enviar dados ao servidor. Um exemplo é quando você envia um formulário de cadastro ou login. O servidor pode processar esses dados e armazená-los ou responder com uma página de confirmação
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        codigo_acesso = request.POST.get('codigo')

        #terapeuta = User.objects.filter(username=codigo_acesso).first()

        terapeuta = User.objects.filter(username=codigo_acesso).first()

        if not terapeuta:
            # Exibir mensagem de erro se o terapeuta não for encontrado
            return render(request, 'login_pacientes/codigo_invalido.html', {'erro': 'Código de acesso inválido. Terapeuta não encontrado.'})

        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            return render(request, 'usuario_existente.html', {'erro': 'Este email já está cadastrado.'})
        
        user = User.objects.create_user(email=email, password=senha, username=email)
        # User é um modelo padrão do Django para representar usuários no sistema. Ele faz parte do módulo django.contrib.auth.models e contém campos como username, email, password, entre outros.
        # objects é o gerenciador de objetos padrão do Django, fornecendo métodos para consultas e criação de novos registros no banco de dados.
        # create_user() é um método específico para a criação de usuários. Ele simplifica o processo de criar e salvar um usuário, pois já inclui medidas de segurança.
        user.save()

        PerfilPaciente.objects.create(usuario=user, name=name, codigo_acesso=codigo_acesso, terapeuta=terapeuta)
        
        return redirect(login)

def login(request):
    if request.method == "GET":
        return render(request, 'login_pacientes/loginpacientes.html')
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
            return redirect('home_paciente')
        else:
            return render(request, 'invalido.html')

#@login_required(login_url="/auth/login/pacientes/")
def plataforma(request):
    url_home = reverse('home')
    return redirect(url_home)
    #return render(request, 'cadastro_paciente/ca')
    #return HttpResponse('Plataforma')