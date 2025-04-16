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
import json

logger = logging.getLogger(__name__)

@login_required(login_url="/auth/login/")
def agenda(request):
    """Exibe a página de agenda com as consultas agendadas."""
    consultas = Agenda.objects.filter(
        paciente__terapeuta=request.user
    ).order_by('date')
    
    pacientes = CadastroPaciente.objects.filter(terapeuta=request.user)

    dados_consultas = []
    for consulta in consultas:
        dados_consultas.append({
            'id_agenda': consulta.id,
            'date': consulta.date,
            'name': consulta.paciente.nome,
            'confirmada': consulta.confirmada,
            'status_lembrete': consulta.status_lembrete,
            'horario_lembrete': consulta.horario_lembrete.strftime('%H:%M')
        })

    return render(request, 'agenda.html', {
        'consultas': dados_consultas,
        'pacientes': pacientes
    })

@login_required(login_url="/auth/login/")
def criar_consulta(request):
    """Cria uma nova consulta com base nos dados enviados pelo formulário."""
    if request.method == 'POST':
        try:
            data_consulta_str = request.POST.get('date')
            data_consulta = timezone.datetime.strptime(data_consulta_str, '%Y-%m-%dT%H:%M')
            
            id_paciente = request.POST.get('paciente')
            paciente = CadastroPaciente.objects.get(pk=id_paciente)
            
            horario_lembrete_str = request.POST.get('horario_lembrete', '16:00')
            horario_lembrete = timezone.datetime.strptime(horario_lembrete_str, '%H:%M').time()
            
            nova_consulta = Agenda(
                date=data_consulta, 
                paciente=paciente, 
                terapeuta=request.user,
                status_lembrete="Não enviado",
                horario_lembrete=horario_lembrete
            )
            nova_consulta.save()
            return redirect('agenda')
        except Exception as e:
            logger.error(f"Erro ao criar consulta: {str(e)}")
            return redirect('agenda')

@login_required(login_url="/auth/login/")
def deletar_consulta(request, id_agenda):
    """Exclui uma consulta com base no ID fornecido."""
    try:
        agenda = Agenda.objects.get(pk=id_agenda)
        agenda.delete()
    except Agenda.DoesNotExist:
        logger.error(f"Consulta com ID {id_agenda} não encontrada")
    return redirect('agenda')

@login_required(login_url="/auth/login/")
def atualizar_horario_lembrete(request, id_agenda):
    """Atualiza o horário do lembrete para uma consulta específica."""
    if request.method == 'POST':
        try:
            consulta = Agenda.objects.get(pk=id_agenda, paciente__terapeuta=request.user)
            
            horario_lembrete_str = request.POST.get('horario_lembrete')
            horario_lembrete = timezone.datetime.strptime(horario_lembrete_str, '%H:%M').time()
            
            consulta.horario_lembrete = horario_lembrete
            
            if consulta.status_lembrete == "Enviado":
                consulta.status_lembrete = "Não enviado"
                
            consulta.save()
            
            return JsonResponse({
                "status": "success",
                "message": f"Horário de lembrete atualizado para {horario_lembrete_str}",
                "horario_formatado": horario_lembrete.strftime('%H:%M')
            })
            
        except Agenda.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Consulta não encontrada"
            }, status=404)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar horário de lembrete: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": f"Erro ao atualizar: {str(e)}"
            }, status=500)
            
    return JsonResponse({
        "status": "error",
        "message": "Método não permitido"
    }, status=405)

def formatar_telefone(numero):
    """Formata o número de telefone para o padrão internacional."""
    if not numero:
        return ""
    telefone = numero.strip()
    if telefone.startswith('0'):
        telefone = telefone[1:]
    if not telefone.startswith('+'):
        telefone = '+55' + telefone
    return ''.join(filter(lambda x: x.isdigit() or x == '+', telefone))

def criar_mensagem(consulta):
    """Cria a mensagem personalizada para o paciente."""
    data_formatada = consulta.date.strftime('%d/%m/%Y às %H:%M')
    mensagem = (
        f"Olá {consulta.paciente.nome}, este é um lembrete da sua consulta "
        f"agendada para {data_formatada}. Por favor, confirme sua presença."
    )
    return mensagem

@login_required(login_url="/auth/login/")
def enviar_lembretes(request):
    """
    Envia lembretes de consulta via WhatsApp.
    Modos:
    - Automático: baseado no horário configurado para cada consulta
    - Manual: envia para consultas conforme seleção de dias
    """
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body)
                dias_antecedencia = int(data.get('dias_antecedencia', 1))
                modo = data.get('modo', 'manual')
            except (json.JSONDecodeError, ValueError):
                dias_antecedencia = 1
                modo = 'manual'
        else:
            dias_antecedencia = int(request.POST.get('dias_antecedencia', 1))
            modo = request.POST.get('modo', 'manual')
    else:
        dias_antecedencia = 1
        modo = 'automatico'
    
    hoje = timezone.now()
    data_alvo = hoje + timedelta(days=dias_antecedencia)
    
    # Consultas para a data alvo que não foram confirmadas
    consultas = Agenda.objects.filter(
        date__date=data_alvo.date(),
        paciente__terapeuta=request.user,
        confirmada=False
    )
    
    if modo == 'automatico':
        hora_atual = hoje.time()
        
        # No modo automático, verifica consultas que tenham o horário de lembrete
        # correspondente ao horário atual com uma margem de 2 minutos
        consultas_para_enviar = []
        
        for consulta in consultas:
            horario_lembrete = consulta.horario_lembrete
            
            # Converter para minutos para comparação
            hora_atual_minutos = hora_atual.hour * 60 + hora_atual.minute
            lembrete_minutos = horario_lembrete.hour * 60 + horario_lembrete.minute
            
            # Verificar se está dentro de uma janela de 2 minutos
            if abs(hora_atual_minutos - lembrete_minutos) <= 2 and consulta.status_lembrete != 'Enviado':
                consultas_para_enviar.append(consulta)
                logger.info(f"Lembrete automático para envio: {consulta.id} - {consulta.paciente.nome} - {horario_lembrete}")
                
        consultas = consultas_para_enviar
    
    if not consultas:
        return JsonResponse({
            "status": f"Nenhuma consulta encontrada para {dias_antecedencia} dia(s) à frente no modo {modo}.",
            "enviados": 0,
            "falhas": 0,
            "detalhes": [],
            "modo": modo
        })

    mensagens_enviadas = 0
    mensagens_falhas = 0
    detalhes_envio = []
    
    for consulta in consultas:
        consulta.status_lembrete = "Aguardando envio"
        consulta.save()
    
    for consulta in consultas:
        telefone = formatar_telefone(consulta.paciente.celular)
        if not telefone:
            mensagens_falhas += 1
            consulta.status_lembrete = "Falha: Sem número cadastrado"
            consulta.save()
            detalhes_envio.append({
                'id_agenda': consulta.id,
                'nome_paciente': consulta.paciente.nome,
                'telefone': '',
                'enviado': False,
                'erro': 'Número de telefone não cadastrado'
            })
            continue
            
        mensagem = criar_mensagem(consulta)
        
        try:
            pywhatkit.sendwhatmsg_instantly(
                phone_no=telefone,
                message=mensagem,
                wait_time=15,
                tab_close=True
            )
            
            logger.info(f"Lembrete enviado para {consulta.paciente.nome}")
            mensagens_enviadas += 1
            consulta.status_lembrete = "Enviado"
            consulta.save()
            
            detalhes_envio.append({
                'id_agenda': consulta.id,
                'nome_paciente': consulta.paciente.nome,
                'telefone': telefone,
                'enviado': True,
                'erro': None
            })
            
            time.sleep(2)
            
        except Exception as e:
            erro_msg = str(e)
            logger.error(f"Erro ao enviar WhatsApp: {erro_msg}")
            mensagens_falhas += 1
            consulta.status_lembrete = f"Falha: {erro_msg[:50]}"
            consulta.save()
            
            detalhes_envio.append({
                'id_agenda': consulta.id,
                'nome_paciente': consulta.paciente.nome,
                'telefone': telefone,
                'enviado': False,
                'erro': erro_msg[:100]
            })

    return JsonResponse({
        "status": f"Processo concluído! {mensagens_enviadas} lembretes enviados, {mensagens_falhas} falhas.",
        "enviados": mensagens_enviadas,
        "falhas": mensagens_falhas,
        "detalhes": detalhes_envio,
        "modo": modo
    })

@login_required(login_url="/auth/login/")
def verificar_lembretes_manual(request):
    """Executar verificação de lembretes manualmente para debugging"""
    try:
        from .tasks import verificar_lembretes_pendentes
        
        # Execute a tarefa diretamente, sem o Celery
        resultado = verificar_lembretes_pendentes()
        
        # Se não encontrou nenhum lembrete para enviar, tente verificar manualmente
        if not resultado.get('consultas'):
            agora = timezone.now()
            amanha = agora.date() + timedelta(days=1)
            
            # Pegar todas as consultas para amanhã que não foram confirmadas
            consultas = Agenda.objects.filter(
                date__date=amanha,
                paciente__terapeuta=request.user,
                confirmada=False
            ).exclude(status_lembrete='Enviado')
            
            resultados = []
            
            for consulta in consultas:
                telefone = formatar_telefone(consulta.paciente.celular)
                resultado = {
                    'id': consulta.id,
                    'paciente': consulta.paciente.nome,
                    'horario_lembrete': consulta.horario_lembrete.strftime('%H:%M')
                }
                
                if not telefone:
                    consulta.status_lembrete = "Falha: Sem número cadastrado"
                    consulta.save()
                    resultado['status'] = "Falha: Sem número cadastrado"
                    resultados.append(resultado)
                    continue
                    
                mensagem = criar_mensagem(consulta)
                
                try:
                    pywhatkit.sendwhatmsg_instantly(
                        phone_no=telefone,
                        message=mensagem,
                        wait_time=15,
                        tab_close=True
                    )
                    
                    consulta.status_lembrete = "Enviado"
                    consulta.save()
                    resultado['status'] = "Enviado com sucesso"
                    
                except Exception as e:
                    erro_msg = str(e)
                    consulta.status_lembrete = f"Falha: {erro_msg[:50]}"
                    consulta.save()
                    resultado['status'] = f"Falha: {erro_msg[:100]}"
                
                resultados.append(resultado)
            
            return JsonResponse({
                "status": f"Verificação manual realizada. {consultas.count()} consultas processadas.",
                "hora": agora.strftime('%H:%M'),
                "consultasProcessadas": consultas.count(),
                "resultados": resultados
            })
        
        # Se encontrou lembretes pela tarefa do Celery, retorne o resultado
        return JsonResponse({
            "status": resultado.get('status', 'Verificação concluída'),
            "hora": resultado.get('hora', timezone.now().strftime('%H:%M')),
            "consultasProcessadas": len(resultado.get('consultas', [])),
            "resultados": []  # Não temos resultados detalhados aqui
        })
        
    except Exception as e:
        logger.error(f"Erro na verificação manual de lembretes: {str(e)}")
        return JsonResponse({
            "status": f"Erro: {str(e)}",
            "hora": timezone.now().strftime('%H:%M'),
            "consultasProcessadas": 0,
            "resultados": []
        })