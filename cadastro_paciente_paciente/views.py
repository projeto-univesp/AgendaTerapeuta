from django.shortcuts import render, redirect, get_object_or_404
from cadastro_paciente.models import CadastroPaciente
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

@login_required(login_url="/auth/login/paciente")
def paciente(request):
    return render(request, "cadastro_paciente_paciente/home_paciente.html")

@login_required
def salvar(request):
    if request.method == 'POST':
        paciente = CadastroPaciente()
        paciente.nome = request.POST.get("nome")
        paciente.data_nascimento = request.POST.get("data_nascimento")
        paciente.sexo = request.POST.get("sexo")
        paciente.email = request.POST.get("email")
        paciente.cpf = request.POST.get("cpf")
        paciente.rg = request.POST.get("rg")
        paciente.celular = request.POST.get("celular")
        paciente.endereco = request.POST.get("endereco")
        paciente.nacionalidade = request.POST.get("nacionalidade")
        paciente.estado_civil = request.POST.get("estado_civil")
        paciente.profissao = request.POST.get("profissao")
        paciente.convenio = request.POST.get("convenio")
        paciente.save()

        paciente.usuario = request.user
        # CadastroPaciente.objects.create(
        #     nome=nome, data_nascimento=data_nascimento, sexo=sexo, email=email, cpf=cpf, rg=rg,
        #     celular=celular, endereco=endereco, nacionalidade=nacionalidade, estado_civil=estado_civil,
        #     profissao=profissao, convenio=convenio, terapeuta=request.user
        # )
        return redirect(paciente)
    return render(request, "cadastro_paciente_paciente/cadastrar.html")

@login_required
def editar(request, idPaciente):
    paciente = get_object_or_404(CadastroPaciente, idPaciente=idPaciente, terapeuta=request.user)
    return render(request, "editar.html", {"paciente": paciente})

@login_required
def atualizar(request, idPaciente):
    paciente = get_object_or_404(CadastroPaciente, id=idPaciente, terapeuta=request.user)
    if request.method == 'POST':
        paciente.nome = request.POST.get("nome")
        paciente.data_nascimento = request.POST.get("data_nascimento")
        paciente.sexo = request.POST.get("sexo")
        paciente.email = request.POST.get("email")
        paciente.cpf = request.POST.get("cpf")
        paciente.rg = request.POST.get("rg")
        paciente.celular = request.POST.get("celular")
        paciente.endereco = request.POST.get("endereco")
        paciente.nacionalidade = request.POST.get("nacionalidade")
        paciente.estado_civil = request.POST.get("estado_civil")
        paciente.profissao = request.POST.get("profissao")
        paciente.convenio = request.POST.get("convenio")
        paciente.save()
        return redirect(paciente)
    return render(request, "editar.html", {"paciente": paciente})


'''@login_required
def pagina_cadastrar(request):
    return render(request, "cadastro_paciente_paciente/cadastrar.html")'''

@login_required()
def pagina_cadastrar(request):
    paciente = CadastroPaciente.objects.filter(usuario=request.user).first()
    
    if request.method == 'POST':
        if paciente is None:
            paciente = CadastroPaciente(usuario=request.user)  # <-- aqui é a correção!
        
        paciente.nome = request.POST.get("nome")
        paciente.data_nascimento = request.POST.get("data_nascimento")
        paciente.sexo = request.POST.get("sexo")
        paciente.email = request.POST.get("email")
        paciente.cpf = request.POST.get("cpf")
        paciente.rg = request.POST.get("rg")
        paciente.celular = request.POST.get("celular")
        paciente.endereco = request.POST.get("endereco")
        paciente.nacionalidade = request.POST.get("nacionalidade")
        paciente.estado_civil = request.POST.get("estado_civil")
        paciente.profissao = request.POST.get("profissao")
        paciente.convenio = request.POST.get("convenio")
        paciente.terapeuta = request.user  # ou setar corretamente aqui se for o terapeuta mesmo
        paciente.save()

        return render(request, "cadastro_paciente_paciente/home_paciente.html")
    
    return render(request, "cadastro_paciente_paciente/cadastrar.html", {"paciente": paciente})

@login_required()
def logout_confirmar(request):
    return render(request, 'cadastro_paciente_paciente/logoutpaciente.html')

def tela_logout(request):
    logout(request)
    return redirect(reverse('login'))  # redireciona para tela de login
