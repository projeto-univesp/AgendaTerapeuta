from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from agenda.models import Agenda
from django.contrib.auth.decorators import login_required
from cadastro_paciente.models import CadastroPaciente
from datetime import datetime
from django.contrib import messages

@login_required
def agenda(request):
    # Filtrar consultas pelo paciente associado ao usuário atualmente logado
    paciente = CadastroPaciente.objects.filter(email=request.user.email).first()
    
    if not paciente:
        messages.error(request, "Perfil de paciente não encontrado.")
        return render(request, 'agenda_paciente.html', {'consultas': [] })
    
    # Usando o campo correto 'paciente' em vez de '_idPaciente'
    consultas = Agenda.objects.filter(paciente=paciente).order_by('date')

    dados_consultas = []
    for consulta in consultas:
        dados_consultas.append({
            'id_agenda': consulta.id,  # Usando 'id' em vez de '_id'
            'date': consulta.date,
            'name': paciente.nome,
        })

    return render(request, 'agenda_paciente.html', {'consultas': dados_consultas })

@login_required
def criar_consulta_paciente(request):
    if request.method == 'POST':
        data_consulta_str = request.POST.get('date')
        data_consulta = datetime.strptime(data_consulta_str, '%Y-%m-%dT%H:%M')
        
        # Obtenha o paciente pelo email do usuário logado
        paciente = CadastroPaciente.objects.filter(email=request.user.email).first()
        
        if not paciente:
            messages.error(request, "Perfil de paciente não encontrado.")
            return redirect('agenda_paciente')
        
        # Obter o terapeuta diretamente do paciente, já que está associado
        if not paciente.terapeuta:
            messages.error(request, "Terapeuta não associado ao seu perfil.")
            return redirect('agenda_paciente')
            
        # Cria a nova consulta usando os nomes corretos dos campos
        nova_consulta = Agenda(
            date=data_consulta, 
            paciente=paciente,  # Usando 'paciente' em vez de '_idPaciente'
            terapeuta=paciente.terapeuta
        )
        nova_consulta.save()
        
        messages.success(request, "Consulta agendada com sucesso!")
        return redirect('agenda_paciente')
    
    return redirect('agenda_paciente')

@login_required
def deletar_consulta(request, id_agenda):
    try:
        # Usando o campo 'id' padrão do Django
        agenda = Agenda.objects.get(pk=id_agenda)
        
        # Verificar se a consulta é do paciente logado
        paciente = CadastroPaciente.objects.filter(email=request.user.email).first()
        if agenda.paciente != paciente:
            messages.error(request, "Você não tem permissão para excluir esta consulta.")
            return redirect('agenda_paciente')
            
        agenda.delete()
        messages.success(request, "Consulta removida com sucesso!")
    except Agenda.DoesNotExist:
        messages.error(request, "Consulta não encontrada.")
    
    return redirect('agenda_paciente')