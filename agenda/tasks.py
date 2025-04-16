from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import logging
import pywhatkit
from .models import Agenda

logger = logging.getLogger(__name__)

@shared_task
def verificar_lembretes_pendentes():
    """
    Verifica se há lembretes para enviar com base no horário configurado para cada consulta.
    Esta função é chamada periodicamente pelo Celery.
    """
    try:
        agora = timezone.now()
        amanha = agora.date() + timedelta(days=1)
        
        # Hora atual com minutos
        hora_atual = agora.time()
        hora_atual_minutos = hora_atual.hour * 60 + hora_atual.minute
        
        logger.info(f"Verificando lembretes para consultas no dia {amanha} às {hora_atual}")
        
        # Buscar todas as consultas agendadas para amanhã que ainda não foram confirmadas
        # e que não tiveram o lembrete enviado ainda
        consultas = Agenda.objects.filter(
            date__date=amanha,
            confirmada=False
        ).exclude(status_lembrete='Enviado')
        
        lembretes_para_enviar = []
        
        for consulta in consultas:
            horario_lembrete = consulta.horario_lembrete
            lembrete_minutos = horario_lembrete.hour * 60 + horario_lembrete.minute
            
            # Verificar se está dentro de uma janela de 2 minutos do horário configurado
            if abs(hora_atual_minutos - lembrete_minutos) <= 2:
                lembretes_para_enviar.append(consulta)
                logger.info(f"Lembrete agendado para envio: Consulta ID {consulta.id} - {consulta.paciente.nome} - {horario_lembrete}")
                
                # Atualiza status
                consulta.status_lembrete = "Aguardando envio"
                consulta.save()
                
                # Envia o lembrete imediatamente
                enviar_lembrete_individual.delay(consulta.id)
        
        return {
            "status": f"Verificação concluída. {len(lembretes_para_enviar)} lembretes agendados",
            "hora": hora_atual.strftime('%H:%M'),
            "consultas": [c.id for c in lembretes_para_enviar]
        }
    except Exception as e:
        logger.error(f"Erro na verificação de lembretes: {str(e)}")
        return {
            "status": f"Erro: {str(e)}",
            "hora": timezone.now().strftime('%H:%M')
        }

@shared_task
def enviar_lembrete_individual(consulta_id):
    """
    Envia lembrete para uma consulta específica via WhatsApp.
    """
    try:
        consulta = Agenda.objects.get(pk=consulta_id)
        
        # Verifica novamente se o lembrete já não foi enviado (proteção contra duplicação)
        if consulta.status_lembrete == 'Enviado':
            logger.info(f"Lembrete para consulta {consulta_id} já foi enviado anteriormente. Ignorando.")
            return {
                "status": "Ignorado",
                "consulta_id": consulta_id,
                "motivo": "Lembrete já enviado"
            }
            
        telefone = formatar_telefone(consulta.paciente.celular)
        
        if not telefone:
            consulta.status_lembrete = "Falha: Sem número cadastrado"
            consulta.save()
            logger.error(f"Falha ao enviar lembrete para consulta {consulta_id}: número de telefone não cadastrado")
            return {
                "status": "Falha",
                "erro": "Número de telefone não cadastrado",
                "consulta_id": consulta_id
            }
            
        mensagem = criar_mensagem(consulta)
        
        try:
            # Adicionando logs detalhados para debug
            logger.info(f"Tentando enviar WhatsApp para {telefone} - Consulta ID: {consulta_id}")
            
            pywhatkit.sendwhatmsg_instantly(
                phone_no=telefone,
                message=mensagem,
                wait_time=15,  # Reduzido para minimizar chance de falha
                tab_close=True
            )
            
            consulta.status_lembrete = "Enviado"
            consulta.save()
            
            logger.info(f"Lembrete enviado com sucesso para consulta {consulta_id}")
            return {
                "status": "Sucesso",
                "consulta_id": consulta_id
            }
            
        except Exception as e:
            erro_msg = str(e)
            consulta.status_lembrete = f"Falha: {erro_msg[:50]}"
            consulta.save()
            logger.error(f"Erro ao enviar lembrete para consulta {consulta_id}: {erro_msg}")
            return {
                "status": "Falha",
                "erro": erro_msg,
                "consulta_id": consulta_id
            }
            
    except Agenda.DoesNotExist:
        logger.error(f"Consulta com ID {consulta_id} não encontrada")
        return {
            "status": "Falha",
            "erro": "Consulta não encontrada",
            "consulta_id": consulta_id
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao enviar lembrete: {str(e)}")
        return {
            "status": "Falha",
            "erro": str(e),
            "consulta_id": consulta_id
        }

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