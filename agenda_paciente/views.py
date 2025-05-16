from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from agenda.models import Agenda
from django.contrib.auth.decorators import login_required
from cadastro_paciente.models import CadastroPaciente
from login_pacientes.models import PerfilPaciente
from datetime import datetime
from django.contrib import messages

from django.contrib.auth.decorators import login_required

@login_required
def agenda(request):
    try:
        paciente = CadastroPaciente.objects.get(usuario=request.user)
    except CadastroPaciente.DoesNotExist:
        return redirect('completar_cadastro')

    consultas = Agenda.objects.filter(paciente_id=paciente.idPaciente).order_by('date')

    return render(request, 'agenda_paciente.html', {'consultas': consultas})


def completar_cadastro(request):
    return render(request, 'completar-cadastro.html')

#@login_required(login_url="/auth/login/")
def criar_consulta_paciente(request):
    if request.method == 'POST':
        data_consulta_str = request.POST.get('date')
        data_consulta = datetime.strptime(data_consulta_str, '%Y-%m-%dT%H:%M')
        
        id_paciente = request.user.id
        try:
            print(id_paciente, request)
            perfil = PerfilPaciente.objects.filter(usuario_id=id_paciente).first()
            paciente = CadastroPaciente.objects.filter(email=request.user.email).first()
        except Http404:
            return redirect('agenda_paciente')
        
        nova_consulta = Agenda(date=data_consulta, paciente=paciente, terapeuta=perfil.terapeuta)
        nova_consulta.save()

        return redirect('agenda_paciente')

#@login_required(login_url="/auth/login/")
def deletar_consulta(request, id_agenda):
    agenda = Agenda.objects.get(pk=id_agenda)
    agenda.delete()
    return redirect('agenda_paciente')
