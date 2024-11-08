from django.shortcuts import render, redirect, get_object_or_404
from cadastro_paciente.models import CadastroPaciente
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

#@login_required(login_url="/auth/login/")
def paciente(request):
    return render(request, "cadastro_paciente_paciente/home_paciente.html")

#@login_required
def salvar(request):
    if request.method == 'POST':
        nome = request.POST.get("nome")
        data_nascimento = request.POST.get("data_nascimento")
        sexo = request.POST.get("sexo")
        email = request.POST.get("email")
        cpf = request.POST.get("cpf")
        rg = request.POST.get("rg")
        celular = request.POST.get("celular")
        endereco = request.POST.get("endereco")
        nacionalidade = request.POST.get("nacionalidade")
        estado_civil = request.POST.get("estado_civil")
        profissao = request.POST.get("profissao")
        convenio = request.POST.get("convenio")
        CadastroPaciente.objects.create(
            nome=nome, data_nascimento=data_nascimento, sexo=sexo, email=email, cpf=cpf, rg=rg,
            celular=celular, endereco=endereco, nacionalidade=nacionalidade, estado_civil=estado_civil,
            profissao=profissao, convenio=convenio, terapeuta=request.user
        )
        return redirect(paciente)
    return render(request, "cadastro_paciente_paciente/cadastrar.html")

'''@login_required
def pagina_cadastrar(request):
    return render(request, "cadastro_paciente_paciente/cadastrar.html")'''

def pagina_cadastrar(request):
    # Verifique se o paciente já está cadastrado para este terapeuta
    paciente_existente = CadastroPaciente.objects.get(email=request.user.email)
    
    # Se o paciente já existir, redirecione para a página de edição com o id do paciente
    if paciente_existente:
        return redirect('editar', idPaciente=paciente_existente.id)
    
    # Caso contrário, renderize a página de cadastro normalmente
    return render(request, "cadastro_paciente_paciente/cadastrar.html")

from django.shortcuts import render, redirect, get_object_or_404
from .models import CadastroPaciente
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required(login_url="/auth/login/")
def homePaciente(request):
    return render(request, "homePaciente.html")

@login_required(login_url="/auth/login/")
def listar(request):
    pacientes = CadastroPaciente.objects.filter(terapeuta=request.user)
    return render(request, "listar.html", {"pacientes": pacientes})

@login_required(login_url="/auth/login/")
def buscar(request):
    return render(request, 'buscar.html')

@login_required(login_url="/auth/login/")
def buscar_resultados(request):
    nome = request.GET.get('nome')
    pacientes = CadastroPaciente.objects.filter(nome__icontains=nome, terapeuta=request.user).exclude(idPaciente=None)
    return render(request, "resultado_busca.html", {"pacientes": pacientes, "nome": nome})

@login_required
def visualizar_paciente(request, idPaciente):
    paciente = get_object_or_404(CadastroPaciente, idPaciente=idPaciente, terapeuta=request.user)
    return render(request, "visualizar_paciente.html", {"paciente": paciente})

@login_required
def salvar(request):
    if request.method == 'POST':
        nome = request.POST.get("nome")
        data_nascimento = request.POST.get("data_nascimento")
        sexo = request.POST.get("sexo")
        email = request.POST.get("email")
        cpf = request.POST.get("cpf")
        rg = request.POST.get("rg")
        celular = request.POST.get("celular")
        endereco = request.POST.get("endereco")
        nacionalidade = request.POST.get("nacionalidade")
        estado_civil = request.POST.get("estado_civil")
        profissao = request.POST.get("profissao")
        convenio = request.POST.get("convenio")

        if CadastroPaciente.objects.filter(cpf=cpf).exists():
            return render(request, 'usuario_existente.html')
        
        CadastroPaciente.objects.create(
            nome=nome, data_nascimento=data_nascimento, sexo=sexo, email=email, cpf=cpf, rg=rg,
            celular=celular, endereco=endereco, nacionalidade=nacionalidade, estado_civil=estado_civil,
            profissao=profissao, convenio=convenio, terapeuta=request.user
        )
        return redirect(homePaciente)
    return render(request, "cadastrar.html")

@login_required
def pagina_cadastrar(request):
    return render(request, "cadastrar.html")

@login_required
def editar(request, idPaciente):
    paciente = get_object_or_404(CadastroPaciente, idPaciente=idPaciente, terapeuta=request.user)
    return render(request, "editar.html", {"paciente": paciente})

@login_required
def atualizar(request, idPaciente):
    # Aqui, estou corrigindo a busca para usar idPaciente em vez de id
    paciente = get_object_or_404(CadastroPaciente, idPaciente=idPaciente, terapeuta=request.user)
    if request.method == 'POST':
        # Atualize os atributos do paciente
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
        
        # Salva as mudanças
        paciente.save()
        
        return redirect(homePaciente)
    return render(request, "editar.html", {"paciente": paciente})

@login_required
def deletar(request, idPaciente):
    paciente = get_object_or_404(CadastroPaciente, idPaciente=idPaciente, terapeuta=request.user)
    paciente.delete()
    return redirect(homePaciente)
