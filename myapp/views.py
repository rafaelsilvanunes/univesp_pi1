import json, qrcode
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q, F
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import SalaForm, QuestaoForm
from .models import Sala, Questao, RespostaAluno


def home(request):
    return render(request, 'home.html')


def lgpd(request):
    return render(request, 'lgpd.html')


# LOGIN PROFESSOR
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Preencha Todos os Campos")
            return render(request, 'professor/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                next_url = request.GET.get('next')
                return redirect(next_url or 'salas')
            else:
                messages.error(request, "Usuário Desativado")
        else:
            messages.error(request, "Login Inválido")

    return render(request, 'professor/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


# SALAS
@login_required(login_url='/login/')
def salas(request):
    salas = request.user.salas.all()
    return render(request, 'professor/salas.html', {'salas': salas})


@login_required(login_url='/login/')
def sala_create(request):
    form = SalaForm(request.POST or None)

    if form.is_valid():
        sala = form.save(commit=False)
        sala.professor = request.user
        sala.save()
        messages.success(request, "Sala Criada!")
        return redirect('salas')

    return render(request, 'professor/sala_form.html', {'form': form})


@login_required(login_url='/login/')
def sala_edit(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id, professor=request.user)
    form = SalaForm(request.POST or None, instance=sala)

    if form.is_valid():
        form.save()
        messages.success(request, "Sala Atualizada!")
        return redirect('salas')

    return render(request, 'professor/sala_form.html', {'form': form, 'sala': sala})


@login_required(login_url='/login/')
def sala_delete(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id, professor=request.user)
    sala.delete()
    messages.success(request, "Sala Excluída!")
    return redirect('salas')


# QUESTÕES
@login_required(login_url='/login/')
def questoes(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id, professor=request.user)
    questoes = Questao.objects.filter(sala=sala)
    return render(request, 'professor/questoes.html', {'sala': sala,'questoes': questoes})


@login_required(login_url='/login/')
def questao_create(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id, professor=request.user)

    if request.method == 'POST':
        form = QuestaoForm(request.POST)

        if form.is_valid():
            questao = form.save(commit=False)
            questao.sala = sala

            if questao.tipo == 'aberta':
                questao.alternativa_a = ''
                questao.alternativa_b = ''
                questao.alternativa_c = ''
                questao.alternativa_d = ''
                questao.alternativa_e = ''
                questao.correta_a = False
                questao.correta_b = False
                questao.correta_c = False
                questao.correta_d = False
                questao.correta_e = False

            questao.save()
            messages.success(request,'Questão criada com sucesso')
            return redirect('questoes', sala_id=sala.id)
    else:
        form = QuestaoForm()

    return render(request, 'professor/questao_form.html', {'sala': sala, 'form': form})


@login_required(login_url='/login/')
def questao_edit(request, sala_id, questao_id):
    sala = get_object_or_404(Sala, id=sala_id, professor=request.user)
    questao = get_object_or_404(Questao, id=questao_id, sala=sala)

    if request.method == 'POST':
        form = QuestaoForm(request.POST, instance=questao)

        if form.is_valid():
            questao = form.save(commit=False)

            if questao.tipo == 'aberta':
                questao.alternativa_a = ''
                questao.alternativa_b = ''
                questao.alternativa_c = ''
                questao.alternativa_d = ''
                questao.alternativa_e = ''
                questao.correta_a = False
                questao.correta_b = False
                questao.correta_c = False
                questao.correta_d = False
                questao.correta_e = False

            questao.save()
            messages.success(request, 'Questão editada com sucesso')
            return redirect('questoes', sala_id=sala.id)
    else:
        form = QuestaoForm(instance=questao)

    return render(request, 'professor/questao_form.html', {'form': form, 'questao': questao, 'sala': sala})


@login_required(login_url='/login/')
def questao_delete(request, sala_id, questao_id):
    sala = get_object_or_404(Sala, id=sala_id, professor=request.user)
    questao = get_object_or_404(Questao, id=questao_id, sala=sala)

    questao.delete()
    messages.success(request, 'Questão removida com sucesso')
    return redirect('questoes', sala_id=sala.id)


# QR CODE
@login_required(login_url='/login/')
def qrcode_sala(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id, professor=request.user)
    url = request.build_absolute_uri(reverse('login_aluno') + f'?codigo={sala.codigo}')

    try:
        img = qrcode.make(url)
    except Exception:
        return HttpResponse("Erro ao gerar QR", status=500)

    response = HttpResponse(content_type='image/png')
    img.save(response)
    return response


# ALUNO
def aluno_login(request):
    sala_codigo = request.POST.get('sala') or request.GET.get('codigo', '')

    if request.method == 'POST':
        aluno_raw = request.POST.get('aluno')

        if not aluno_raw or not sala_codigo:
            messages.error(request, "Preencha Todos os Campos")
            return render(request, 'aluno/login.html', {'codigo': sala_codigo})

        aluno = aluno_raw.strip().lower()
        sala = Sala.objects.filter(codigo=sala_codigo, ativa=True).first()

        if not sala:
            messages.error(request, "Sala Não Encontrada ou Inativa")
            return render(request, 'aluno/login.html', {'codigo': sala_codigo})

        ja_respondeu = RespostaAluno.objects.filter(aluno_nome=aluno, questao__sala=sala).exists()
        request.session['aluno_nome'] = aluno
        request.session['sala_codigo'] = sala.codigo

        if ja_respondeu:
            messages.info(request, "Você já respondeu essa sala")
            return redirect('resultado_aluno', codigo=sala.codigo)

        return redirect('responder_aluno', codigo=sala.codigo)
    return render(request, 'aluno/login.html', {'codigo': sala_codigo})


def aluno_responder(request, codigo):
    aluno_nome = request.session.get('aluno_nome')

    if not aluno_nome:
        return redirect(f'/aluno/?codigo={codigo}')

    sala = get_object_or_404(Sala, codigo=codigo, ativa=True)
    ja_respondeu = RespostaAluno.objects.filter(aluno_nome=aluno_nome, questao__sala=sala).exists()

    if ja_respondeu:
        return redirect('resultado_aluno', codigo=codigo)

    questoes = Questao.objects.filter(sala=sala)

    if request.method == 'POST':
        tempo_total = int(request.POST.get('tempo_total', 0))
        total_questoes = questoes.count()
        tempo_por_questao = (
            int(tempo_total / total_questoes)
            if total_questoes > 0 else 0
        )

        for q in questoes:
            if q.tipo == 'aberta':
                resposta_texto = request.POST.get(f'q{q.id}', '').strip()
                RespostaAluno.objects.create(
                    questao=q,
                    aluno_nome=aluno_nome,
                    texto_resposta=resposta_texto,
                    correta=False,
                    nota=0,
                    tempo_resposta=tempo_por_questao
                )
                continue

            marcadas = request.POST.getlist(f'q{q.id}')
            marcadas_set = set(marcadas)
            corretas = set()

            if q.correta_a:
                corretas.add('A')

            if q.correta_b:
                corretas.add('B')

            if q.correta_c:
                corretas.add('C')

            if q.correta_d:
                corretas.add('D')

            if q.correta_e:
                corretas.add('E')

            correta = False
            nota = 0

            if q.tipo_correcao == 'nenhuma':
                correta = False
                nota = 0
            elif q.tipo_correcao == 'unica':
                correta = marcadas_set == corretas
                nota = 1 if correta else 0
            elif q.tipo_correcao == 'multipla':
                correta = marcadas_set == corretas
                nota = 1 if correta else 0

            RespostaAluno.objects.create(
                questao=q,
                aluno_nome=aluno_nome,
                texto_resposta=', '.join(marcadas),
                correta=correta,
                nota=nota,
                tempo_resposta=tempo_por_questao
            )

        return redirect('resultado_aluno', codigo=codigo)
    return render(request, 'aluno/responder.html', {'sala': sala, 'questoes': questoes, 'aluno_nome': aluno_nome})


def aluno_resultado(request, codigo):
    aluno_nome = request.session.get('aluno_nome')

    if not aluno_nome:
        return redirect(f'/aluno/?codigo={codigo}')

    sala = get_object_or_404(Sala, codigo=codigo, ativa=True)
    respostas = RespostaAluno.objects.filter(aluno_nome=aluno_nome, questao__sala=sala).select_related('questao').order_by('questao__id')
    total = 0
    acertos = 0
    erros = 0
    tempo_total = 0

    for r in respostas:
        q = r.questao
        tempo_total += r.tempo_resposta
        r.marcadas = []

        if r.texto_resposta:
            r.marcadas = [
                item.strip()
                for item in r.texto_resposta.split(',')
                if item.strip()
            ]

        r.alternativas = []
        alternativas = [
            ('A', q.alternativa_a, q.correta_a),
            ('B', q.alternativa_b, q.correta_b),
            ('C', q.alternativa_c, q.correta_c),
            ('D', q.alternativa_d, q.correta_d),
            ('E', q.alternativa_e, q.correta_e),
        ]

        for letra, texto, correta_alt in alternativas:
            if not texto:
                continue

            marcada = letra in r.marcadas
            css = ''

            if q.tipo_correcao =='nenhuma':
                css = ''
            else:
                if marcada and correta_alt:
                    css = 'correta'
                elif marcada and not correta_alt:
                    css = 'errada'
                elif correta_alt:
                    css = 'correta'

            r.alternativas.append({
                'letra': letra,
                'texto': texto,
                'correta': correta_alt,
                'marcada': marcada,
                'css': css
            })

        pontua = (q.tipo == 'objetiva' and q.tipo_correcao != 'nenhuma')

        if pontua:
            total += 1

            if r.correta:
                acertos += 1
            else:
                erros += 1

    percentual = 0

    if total > 0:
        percentual = round((acertos / total) * 100, 2)

    return render(request, 'aluno/resultado.html', {
        'sala': sala,
        'respostas': respostas,
        'aluno_nome': aluno_nome,
        'acertos': acertos,
        'erros': erros,
        'total': total,
        'percentual': percentual,
        'tempo_total': tempo_total,
    })


@login_required(login_url='/login/')
def sala_resultado(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id, professor=request.user)
    questoes = Questao.objects.filter(sala=sala).order_by('id')
    respostas = (RespostaAluno.objects.filter(questao__sala=sala).select_related('questao').order_by('questao__id'))

    for r in respostas:
        q = r.questao
        r.avaliavel = (q.tipo == 'objetiva' and q.tipo_correcao != 'nenhuma')
        marcadas = []

        if r.texto_resposta:
            marcadas = [
                x.strip()
                for x in r.texto_resposta.split(',')
                if x.strip()
            ]

        r.respostas_marcadas = []
        r.respostas_corretas = []
        alternativas = [
            ('A', q.alternativa_a, q.correta_a),
            ('B', q.alternativa_b, q.correta_b),
            ('C', q.alternativa_c, q.correta_c),
            ('D', q.alternativa_d, q.correta_d),
            ('E', q.alternativa_e, q.correta_e),
        ]

        for letra, texto, correta in alternativas:
            if not texto:
                continue

            if letra in marcadas:
                r.respostas_marcadas.append({
                    'letra': letra,
                    'texto': texto
                })

            if correta:
                r.respostas_corretas.append({
                    'letra': letra,
                    'texto': texto
                })

    dados_questoes = []
    ranking_questoes = []

    for q in questoes:
        pontua = (q.tipo == 'objetiva' and q.tipo_correcao != 'nenhuma')
        respostas_q = respostas.filter(questao=q)
        total = respostas_q.count()

        if pontua:
            acertos = respostas_q.filter(correta=True).count()
            erros = respostas_q.filter(correta=False).count()
        else:
            acertos = 0
            erros = 0
        percentual = 0

        if pontua and total > 0:
            percentual = round((acertos / total) * 100, 2)

        alternativas_corretas = []
        alternativas = [
            ('A', q.alternativa_a, q.correta_a),
            ('B', q.alternativa_b, q.correta_b),
            ('C', q.alternativa_c, q.correta_c),
            ('D', q.alternativa_d, q.correta_d),
            ('E', q.alternativa_e, q.correta_e),
        ]
        for letra, texto, correta in alternativas:
            if correta and texto:
                alternativas_corretas.append(f'{letra}) {texto}')

        item = {
            'id': q.id,
            'texto': q.texto,
            'total': total,
            'acertos': acertos,
            'erros': erros,
            'percentual': percentual,
            'pontua': pontua,
            'tipo': q.tipo,
            'tipo_correcao': q.tipo_correcao,
            'respostas_corretas': q.respostas_corretas(),
            'corretas_texto': alternativas_corretas,
        }

        dados_questoes.append(item)

        if pontua:
            ranking_questoes.append(item)

    ranking_questoes = sorted(ranking_questoes, key=lambda x: x['percentual'])

    alunos = defaultdict(lambda: {
        'acertos': 0,
        'erros': 0,
        'total': 0,
        'tempo': 0,
        'percentual': 0,
    })

    for r in respostas:
        q = r.questao

        if (q.tipo != 'objetiva' or q.tipo_correcao == 'nenhuma'):
            continue

        nome = r.aluno_nome.title()
        alunos[nome]['total'] += 1
        alunos[nome]['tempo'] += r.tempo_resposta

        if r.correta:
            alunos[nome]['acertos'] += 1
        else:
            alunos[nome]['erros'] += 1

    for nome, dados in alunos.items():
        if dados['total'] > 0:
            dados['percentual'] = round((dados['acertos'] / dados['total']) * 100, 2)

    ranking_alunos = sorted(
        alunos.items(),
        key=lambda item: (
            item[1]['percentual'],
            item[1]['acertos']
        ),
        reverse=True
    )

    return render(request, 'professor/resultado.html', {
        'sala': sala,
        'questoes': questoes,
        'respostas': respostas,
        'dados_questoes': dados_questoes,
        'ranking_questoes': ranking_questoes,
        'ranking_alunos': ranking_alunos,
        'dados_questoes_json': json.dumps(dados_questoes),
        'dados_alunos_json': json.dumps(alunos),
    })