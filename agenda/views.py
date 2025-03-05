from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils import timezone
from .models import Agenda
from cadastro_paciente.models import CadastroPaciente
import logging
import pywhatkit
import time
from datetime import datetime

# Configuração do logger
logger = logging.getLogger(__name__)

@login_required(login_url="/auth/login/")
def agenda(request):
    """
    Exibe a página de agenda com as consultas agendadas para o terapeuta logado.
    """
    # Filtrar consultas pelo paciente associado ao terapeuta atualmente logado
    consultas = Agenda.objects.filter(paciente__terapeuta=request.user).order_by('date')
    
    # Obter os pacientes do terapeuta atualmente logado
    pacientes = CadastroPaciente.objects.filter(terapeuta=request.user)

    dados_consultas = []
    for consulta in consultas:
        paciente = consulta.paciente
        dados_consultas.append({
            'id_agenda': consulta.id,
            'date': consulta.date,
            'name': paciente.nome,
            'confirmada': consulta.confirmada,
            'status_lembrete': consulta.status_lembrete if hasattr(consulta, 'status_lembrete') else None
        })

    if not consultas:
        consultas = []

    return render(request, 'agenda.html', {'consultas': dados_consultas, 'pacientes': pacientes})

@login_required(login_url="/auth/login/")
def criar_consulta(request):
    """
    Cria uma nova consulta com base nos dados enviados pelo formulário.
    """
    if request.method == 'POST':
        data_consulta_str = request.POST.get('date')
        data_consulta = timezone.datetime.strptime(data_consulta_str, '%Y-%m-%dT%H:%M')
        
        id_paciente = request.POST.get('paciente')
        paciente = CadastroPaciente.objects.get(pk=id_paciente)
        
        terapeuta = request.user
        
        nova_consulta = Agenda(
            date=data_consulta, 
            paciente=paciente, 
            terapeuta=terapeuta,
            status_lembrete="Não enviado"
        )
        nova_consulta.save()

        return redirect('agenda')

@login_required(login_url="/auth/login/")
def deletar_consulta(request, id_agenda):
    """
    Exclui uma consulta com base no ID fornecido.
    """
    agenda = Agenda.objects.get(pk=id_agenda)
    agenda.delete()
    return redirect('agenda')

# Funções auxiliares para organizar melhor o código
def formatar_telefone(numero):
    """Formata o número de telefone para o padrão internacional"""
    telefone = numero.strip()
    if telefone.startswith('0'):
        telefone = telefone[1:]
    if not telefone.startswith('+'):
        telefone = '+55' + telefone
    
    # Removendo caracteres não numéricos
    telefone = ''.join(filter(lambda x: x.isdigit() or x == '+', telefone))
    return telefone

def criar_mensagem(consulta):
    """Cria a mensagem personalizada para o paciente"""
    # Formatando a data para exibição
    data_formatada = consulta.date.strftime('%d/%m/%Y às %H:%M')
    
    # Montando a mensagem
    mensagem = (
        f"Olá {consulta.paciente.nome}, este é teste de envio de mensagem do nosso PI UNIVESP "
        f"agendada para {data_formatada}. Se você recebeu esta mensagem, é um sinal que estamos avançando "
        f"TESTE FINAL "
    )
    return mensagem

@login_required(login_url="/auth/login/")
def enviar_lembretes(request):
    """
    Envia lembretes de consulta via WhatsApp para os pacientes.
    """
    hoje = timezone.now()
    amanha = hoje + timedelta(days=1)
    
    # Permite filtrar apenas consultas para o dia seguinte (1 dia à frente)
    # Isso melhora a experiência do usuário como solicitado
    consultas = Agenda.objects.filter(
        date__date=amanha.date(),  # Filtra apenas pela data (ignorando hora)
        paciente__terapeuta=request.user,
        confirmada=False
    )

    # Verificar se há consultas para enviar lembretes
    if not consultas.exists():
        return JsonResponse({
            "status": "Nenhuma consulta encontrada para o dia de amanhã.",
            "enviados": 0,
            "falhas": 0,
            "detalhes": []
        })

    mensagens_enviadas = 0
    mensagens_falhas = 0
    detalhes_envio = []  # Lista para armazenar detalhes de cada envio
    
    # Para cada consulta, atualiza o status para "Aguardando envio"
    for consulta in consultas:
        consulta.status_lembrete = "Aguardando envio"
        consulta.save()
    
    for consulta in consultas:
        telefone = formatar_telefone(consulta.paciente.celular)
        mensagem = criar_mensagem(consulta)
        
        try:
            # Obter a hora atual para enviar a mensagem imediatamente
            agora = datetime.now()
            
            # Usando pywhatkit para enviar a mensagem (método compatível com versões atuais)
            pywhatkit.sendwhatmsg_instantly(
                phone_no=telefone,
                message=mensagem,
                wait_time=15,  # Tempo de espera reduzido
                tab_close=True  # Fecha a aba após enviar
            )
            
            logger.info(f"Lembrete WhatsApp enviado para {consulta.paciente.nome} ({telefone})")
            mensagens_enviadas += 1
            
            # Atualiza o status no banco de dados
            consulta.status_lembrete = "Enviado"
            consulta.save()
            
            # Registra o sucesso no envio
            detalhes_envio.append({
                'id_agenda': consulta.id,
                'nome_paciente': consulta.paciente.nome,
                'telefone': telefone,
                'enviado': True,
                'erro': None
            })
            
            # Pequeno delay para garantir que a mensagem foi enviada
            time.sleep(2)
            
        except Exception as e:
            erro_msg = str(e)
            logger.error(f"Erro ao enviar WhatsApp para {consulta.paciente.nome} ({telefone}): {erro_msg}")
            mensagens_falhas += 1
            
            # Atualiza o status no banco de dados
            consulta.status_lembrete = f"Falha: {erro_msg[:50]}"
            consulta.save()
            
            # Registra a falha no envio
            detalhes_envio.append({
                'id_agenda': consulta.id,
                'nome_paciente': consulta.paciente.nome,
                'telefone': telefone,
                'enviado': False,
                'erro': erro_msg[:100]  # Limita o tamanho da mensagem de erro
            })

    return JsonResponse({
        "status": f"Processo concluído! {mensagens_enviadas} lembretes enviados, {mensagens_falhas} falhas.",
        "enviados": mensagens_enviadas,
        "falhas": mensagens_falhas,
        "detalhes": detalhes_envio
    })