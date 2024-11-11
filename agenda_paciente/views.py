from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from agenda.models import Agenda
from django.contrib.auth.decorators import login_required
from cadastro_paciente.models import CadastroPaciente
from datetime import datetime
from django.contrib import messages

from django.contrib.auth.decorators import login_required

#@login_required(login_url="/auth/login/")
def agenda(request):
    # Filtrar consultas pelo paciente associado ao terapeuta atualmente logado
    consultas = Agenda.objects.filter(_idPaciente__terapeuta=request.user).order_by('date')
    
    # Obter os pacientes do terapeuta atualmente logado
    pacientes = CadastroPaciente.objects.filter(terapeuta=request.user)

    dados_consultas = []
    for consulta in consultas:
        paciente = consulta._idPaciente
        dados_consultas.append({
            'id_agenda': consulta._id,
            'date': consulta.date,
            'name': paciente.nome,
        })

    if not consultas:
        consultas = []

    return render(request, 'agenda_paciente.html', {'consultas': dados_consultas, 'pacientes': pacientes})


#@login_required(login_url="/auth/login/")
def criar_consulta(request):
    if request.method == 'POST':
        data_consulta_str = request.POST.get('date')
        data_consulta = datetime.strptime(data_consulta_str, '%Y-%m-%dT%H:%M')
        
        id_paciente = request.POST.get('_idPaciente')

        try:
            paciente = get_object_or_404(CadastroPaciente, pk=id_paciente, terapeuta=request.user)
            messages.success(request, "Paciente salvo.")
        except Http404:
            messages.error(request, "Paciente não encontrado.")
            return redirect('agenda_paciente')
        
        terapeuta = request.user
        
        nova_consulta = Agenda(date=data_consulta, _idPaciente=paciente, terapeuta=terapeuta)
        nova_consulta.save()

        return redirect('agenda_paciente')

#@login_required(login_url="/auth/login/")
def deletar_consulta(request, id_agenda):
    agenda = Agenda.objects.get(pk=id_agenda)
    agenda.delete()
    return redirect('agenda_paciente')
