from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
from django.db.models import Count, Sum, Q, Value
from django.db.models.functions import TruncMonth, TruncDate, Coalesce
from .models import Agenda
from cadastro_paciente.models import CadastroPaciente
import logging
import pywhatkit
import time
import json
import traceback

logger = logging.getLogger(__name__)

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
        return redirect(homePaciente)
    return render(request, "editar.html", {"paciente": paciente})

@login_required
def deletar(request, idPaciente):
    paciente = get_object_or_404(CadastroPaciente, idPaciente=idPaciente, terapeuta=request.user)
    paciente.delete()
    return redirect(homePaciente)

@login_required(login_url="/auth/login/")
def agenda(request):
    consultas = Agenda.objects.filter(
        terapeuta=request.user
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
            'horario_lembrete': consulta.horario_lembrete.strftime('%H:%M'),
            'valor_consulta': float(consulta.valor_consulta)
        })

    return render(request, 'agenda.html', {
        'consultas': dados_consultas,
        'pacientes': pacientes
    })

@login_required(login_url="/auth/login/")
def dashboard(request):
    hoje = timezone.now().date()
    
    pacientes = CadastroPaciente.objects.filter(terapeuta=request.user)
    total_pacientes = pacientes.count()
    
    primeiro_dia_mes = hoje.replace(day=1)
    consultas_mes = Agenda.objects.filter(
        terapeuta=request.user,
        date__gte=primeiro_dia_mes
    ).count()
    
    consultas_hoje = Agenda.objects.filter(
        terapeuta=request.user,
        date__date=hoje,
        confirmada=True
    ).count()
    
    faturamento_result = Agenda.objects.filter(
        terapeuta=request.user,
        date__gte=primeiro_dia_mes,
        confirmada=True
    ).aggregate(
        total=Coalesce(Sum('valor_consulta'), Value(Decimal('0.00')))
    )
    
    faturamento_mes = faturamento_result['total'] if faturamento_result['total'] is not None else Decimal('0.00')
    
    meses_para_analise = 6
    data_inicio = hoje - timedelta(days=30*meses_para_analise)
    
    consultas_por_mes = Agenda.objects.filter(
        terapeuta=request.user,
        date__gte=data_inicio
    ).annotate(
        mes=TruncMonth('date')
    ).values('mes').annotate(
        total=Count('id'),
        confirmadas=Count('id', filter=Q(confirmada=True)),
        canceladas=Count('id', filter=Q(confirmada=False)),
        faturamento=Coalesce(Sum('valor_consulta', filter=Q(confirmada=True)), Value(Decimal('0.00')))
    ).order_by('mes')

    meses_completos = []
    for i in range(meses_para_analise):
        mes = (hoje.replace(day=1) - timedelta(days=30*i))
        meses_completos.append(mes.replace(day=1))
    
    labels = []
    consultas_data = []
    confirmadas_data = []
    canceladas_data = []
    faturamento_data = []
    
    for mes in sorted(meses_completos):
        mes_formatado = mes.strftime('%b/%Y')
        labels.append(mes_formatado)
        
        dados_mes = next((item for item in consultas_por_mes 
                         if item['mes'].month == mes.month and item['mes'].year == mes.year), None)
        
        if dados_mes:
            consultas_data.append(int(dados_mes['total']))
            confirmadas_data.append(int(dados_mes['confirmadas']))
            canceladas_data.append(int(dados_mes['canceladas']))
            faturamento_data.append(float(dados_mes['faturamento']))
        else:
            consultas_data.append(0)
            confirmadas_data.append(0)
            canceladas_data.append(0)
            faturamento_data.append(0.0)
    
    return render(request, 'dashboard.html', {
        'total_pacientes': total_pacientes,
        'consultas_mes': consultas_mes,
        'consultas_hoje': consultas_hoje,
        'faturamento_mes': float(faturamento_mes),
        'chart_labels': json.dumps(labels),
        'chart_consultas': json.dumps(consultas_data),
        'chart_confirmadas': json.dumps(confirmadas_data),
        'chart_canceladas': json.dumps(canceladas_data),
        'chart_faturamento': json.dumps(faturamento_data),
        'pacientes': pacientes
    })

@login_required
def dashboard_data(request):
    try:
        hoje = timezone.now().date()
        
        try:
            meses = int(request.GET.get('meses', 6))
            if meses <= 0 or meses > 24:
                meses = 6
                logger.warning(f"Período inválido, usando padrão de 6 meses")
        except ValueError:
            meses = 6
            logger.warning("Valor inválido para meses, usando padrão 6")
        
        paciente_id = request.GET.get('paciente', 'todos')
        
        logger.info(f"Iniciando geração de dados para {meses} meses, paciente: {paciente_id}")

        data_fim = timezone.now()
        data_inicio = data_fim - timedelta(days=30*meses)
        
        total_pacientes = CadastroPaciente.objects.filter(terapeuta=request.user).count()
        logger.info(f"Total de pacientes encontrados: {total_pacientes}")

        consultas_query = Agenda.objects.filter(
            terapeuta=request.user,
            date__range=[data_inicio, data_fim]
        )
        
        if paciente_id != 'todos':
            try:
                paciente_obj = CadastroPaciente.objects.get(
                    pk=paciente_id, 
                    terapeuta=request.user
                )
                consultas_query = consultas_query.filter(paciente=paciente_obj)
                logger.info(f"Filtrando por paciente: {paciente_obj.nome}")
            except CadastroPaciente.DoesNotExist:
                logger.warning(f"Paciente ID {paciente_id} não encontrado, ignorando filtro")
        
        logger.debug(f"Query base: {str(consultas_query.query)}")
        
        consultas = consultas_query.annotate(
            mes=TruncMonth('date')
        ).values('mes').annotate(
            total_consultas=Count('id'),
            confirmadas=Count('id', filter=Q(confirmada=True)),
            canceladas=Count('id', filter=Q(confirmada=False)),
            faturamento=Coalesce(Sum('valor_consulta', filter=Q(confirmada=True)), Value(Decimal('0.00')))
        ).order_by('mes')
        
        logger.debug(f"Consulta por mês (raw): {list(consultas)}")

        primeiro_dia_mes = hoje.replace(day=1)
        
        consultas_mes = consultas_query.filter(date__gte=primeiro_dia_mes).count()
        logger.info(f"Consultas este mês: {consultas_mes}")

        consultas_hoje = consultas_query.filter(
            date__date=hoje,
            confirmada=True
        ).count()
        logger.info(f"Consultas hoje: {consultas_hoje}")

        faturamento_query = consultas_query.filter(
            date__gte=primeiro_dia_mes,
            confirmada=True
        )
        
        faturamento_manual = Decimal('0.00')
        for consulta in faturamento_query:
            valor = consulta.valor_consulta if consulta.valor_consulta is not None else Decimal('0.00')
            faturamento_manual += valor
            logger.debug(f"Consulta ID: {consulta.id}, Valor: {valor}, Tipo: {type(valor)}")
        
        faturamento_mes = faturamento_manual
        logger.info(f"Faturamento calculado: {faturamento_mes}")

        meses_completos = []
        for i in range(meses):
            mes = (data_fim.replace(day=1) - timedelta(days=30*i))
            meses_completos.append(mes.replace(day=1))
        
        dados = []
        for mes in sorted(meses_completos):
            dados_mes = next((item for item in consultas 
                            if item['mes'] and item['mes'].month == mes.month and item['mes'].year == mes.year), None)
            
            if dados_mes:
                faturamento = dados_mes['faturamento'] if dados_mes['faturamento'] is not None else Decimal('0.00')
                valor_faturamento = float(faturamento)
                
                logger.debug(f"Dados para {mes.strftime('%b/%Y')}: "
                            f"Consultas={dados_mes['total_consultas']}, "
                            f"Confirmadas={dados_mes['confirmadas']}, "
                            f"Canceladas={dados_mes['canceladas']}, "
                            f"Faturamento={valor_faturamento}")
                
                dados.append({
                    'mes': mes.strftime('%Y-%m'),
                    'mes_formatado': mes.strftime('%b/%Y'),
                    'consultas': int(dados_mes['total_consultas']),
                    'confirmadas': int(dados_mes['confirmadas']),
                    'canceladas': int(dados_mes['canceladas']),
                    'faturamento': valor_faturamento
                })
            else:
                logger.debug(f"Sem dados para {mes.strftime('%b/%Y')}")
                dados.append({
                    'mes': mes.strftime('%Y-%m'),
                    'mes_formatado': mes.strftime('%b/%Y'),
                    'consultas': 0,
                    'confirmadas': 0,
                    'canceladas': 0,
                    'faturamento': 0.0
                })

        nome_paciente = None
        if paciente_id != 'todos':
            try:
                nome_paciente = CadastroPaciente.objects.get(pk=paciente_id).nome
            except CadastroPaciente.DoesNotExist:
                nome_paciente = None

        resposta = {
            'status': 'success',
            'data': dados,
            'resumo': {
                'total_pacientes': total_pacientes,
                'consultas_mes': consultas_mes,
                'consultas_hoje': consultas_hoje,
                'faturamento_mes': float(faturamento_mes),
                'nome_paciente': nome_paciente
            }
        }
        
        logger.info("Dashboard data gerado com sucesso")
        return JsonResponse(resposta, safe=True)
        
    except Exception as e:
        error_message = f"Erro ao obter dados do dashboard: {e}"
        error_traceback = traceback.format_exc()
        logger.error(f"{error_message}\n{error_traceback}")
        
        return JsonResponse({
            'status': 'error',
            'message': 'Erro ao processar os dados',
            'error_details': str(e),
            'error_type': str(type(e).__name__)
        }, status=500)

@login_required
@require_http_methods(["POST"])
def confirmar_consulta(request):
    try:
        data = json.loads(request.body)
        consulta = Agenda.objects.get(
            pk=data.get('id_agenda'),
            terapeuta=request.user
        )
        consulta.confirmada = not consulta.confirmada
        
        if consulta.confirmada:
            consulta.status_lembrete = "Confirmada pelo paciente"
        
        consulta.save()
        
        return JsonResponse({
            'status': 'success',
            'confirmada': consulta.confirmada,
            'message': 'Status da consulta atualizado com sucesso!'
        })
    except Agenda.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Consulta não encontrada'
        }, status=404)
    except Exception as e:
        logger.error(f"Erro ao confirmar consulta: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required(login_url="/auth/login/")
def criar_consulta(request):
    if request.method == 'POST':
        try:
            data_consulta_str = request.POST.get('date')
            data_consulta = timezone.make_aware(
                timezone.datetime.strptime(data_consulta_str, '%Y-%m-%dT%H:%M')
            )
            
            id_paciente = request.POST.get('paciente')
            paciente = CadastroPaciente.objects.get(pk=id_paciente)
            
            horario_lembrete_str = request.POST.get('horario_lembrete', '16:00')
            horario_lembrete = timezone.datetime.strptime(horario_lembrete_str, '%H:%M').time()
            
            valor_consulta = Decimal(request.POST.get('valor_consulta', '200.00'))
            logger.info(f"Valor da consulta recebido: {valor_consulta}")
            
            nova_consulta = Agenda(
                date=data_consulta, 
                paciente=paciente, 
                terapeuta=request.user,
                status_lembrete="Não enviado",
                horario_lembrete=horario_lembrete,
                valor_consulta=valor_consulta
            )
            nova_consulta.save()
            logger.info(f"Consulta criada com valor: {nova_consulta.valor_consulta}")
            return redirect('agenda')
        except Exception as e:
            logger.error(f"Erro ao criar consulta: {str(e)}\n{traceback.format_exc()}")
            return redirect('agenda')

@login_required(login_url="/auth/login/")
def deletar_consulta(request, id_agenda):
    try:
        agenda = Agenda.objects.get(pk=id_agenda)
        agenda.delete()
    except Agenda.DoesNotExist:
        logger.error(f"Consulta com ID {id_agenda} não encontrada\n{traceback.format_exc()}")
    return redirect('agenda')

@login_required(login_url="/auth/login/")
def atualizar_horario_lembrete(request, id_agenda):
    if request.method == 'POST':
        try:
            consulta = Agenda.objects.get(pk=id_agenda, terapeuta=request.user)
            
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
            logger.error(f"Erro ao atualizar horário de lembrete: {str(e)}\n{traceback.format_exc()}")
            return JsonResponse({
                "status": "error",
                "message": f"Erro ao atualizar: {str(e)}"
            }, status=500)
            
    return JsonResponse({
        "status": "error",
        "message": "Método não permitido"
    }, status=405)

def formatar_telefone(numero):
    if not numero:
        return ""
    telefone = numero.strip()
    if telefone.startswith('0'):
        telefone = telefone[1:]
    if not telefone.startswith('+'):
        telefone = '+55' + telefone
    return ''.join(filter(lambda x: x.isdigit() or x == '+', telefone))

def criar_mensagem(consulta):
    data_formatada = consulta.date.strftime('%d/%m/%Y às %H:%M')
    mensagem = (
        f"Olá {consulta.paciente.nome},\n\n"
        f"Este é um lembrete da sua consulta agendada para {data_formatada}.\n\n"
        f"Para CONFIRMAR sua presença, responda esta mensagem com 'CONFIRMAR'.\n\n"
        f"Se precisar cancelar ou reagendar, responda com 'CANCELAR'.\n\n"
        f"Atenciosamente,\n{consulta.terapeuta.first_name}"
    )
    return mensagem

@login_required(login_url="/auth/login/")
def enviar_lembretes(request):
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
    
    consultas = Agenda.objects.filter(
        date__date=data_alvo.date(),
        terapeuta=request.user,
        confirmada=False
    )
    
    if modo == 'automatico':
        hora_atual = hoje.time()
        
        consultas_para_enviar = []
        
        for consulta in consultas:
            horario_lembrete = consulta.horario_lembrete
            
            hora_atual_minutos = hora_atual.hour * 60 + hora_atual.minute
            lembrete_minutos = horario_lembrete.hour * 60 + horario_lembrete.minute
            
            if abs(hora_atual_minutos - lembrete_minutos) <= 2 and consulta.status_lembrete != 'Enviado':
                consultas_para_enviar.append(consulta)
                
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
        consulta.status_lembrete = "Aguardando confirmação"
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
            logger.error(f"Erro ao enviar WhatsApp: {erro_msg}\n{traceback.format_exc()}")
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
    try:
        agora = timezone.now()
        amanha = agora.date() + timedelta(days=1)
        
        consultas = Agenda.objects.filter(
            date__date=amanha.date(),
            terapeuta=request.user,
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
        
    except Exception as e:
        logger.error(f"Erro na verificação manual de lembretes: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({
            "status": f"Erro: {str(e)}",
            "hora": timezone.now().strftime('%H:%M'),
            "consultasProcessadas": 0,
            "resultados": []
        })