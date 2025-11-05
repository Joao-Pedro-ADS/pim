# backend/core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone
from .decorators import professor_required, aluno_required
from .models import Professor, Aluno, Atividade, Submissao
from .forms import AtividadeForm, AlunoForm, SubmissaoForm, CorrecaoForm
from .services import GeminiService
import json


# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

def login_view(request):
    """View de login para Professor e Aluno"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')

        if user_type == 'professor':
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo(a), Professor(a) {user.nome}!')
                return redirect('professor_atividades')
            messages.error(request, 'Usuário ou senha inválidos.')

        elif user_type == 'aluno':
            try:
                aluno = Aluno.objects.get(ra=username, is_active=True)
                if aluno.check_password(password):
                    request.session['aluno_id'] = aluno.id
                    messages.success(request, f'Bem-vindo(a), {aluno.nome}!')
                    return redirect('aluno_atividades')
                messages.error(request, 'RA ou senha inválidos.')
            except Aluno.DoesNotExist:
                messages.error(request, 'Aluno não encontrado ou inativo.')

    return render(request, 'login.html')


def logout_view(request):
    """Logout para Professor e Aluno"""
    if 'aluno_id' in request.session:
        del request.session['aluno_id']
    logout(request)
    messages.info(request, 'Logout realizado com sucesso.')
    return redirect('login')


# ============================================================================
# VIEWS DO PROFESSOR
# ============================================================================

@professor_required
def professor_atividades(request):
    """Lista de atividades do professor"""
    atividades = Atividade.objects.filter(professor=request.user).prefetch_related('submissoes')

    # Adicionar informações de submissões pendentes
    for atividade in atividades:
        atividade.novas_submissoes = atividade.submissoes_pendentes()

    context = {
        'atividades': atividades,
        'total_atividades': atividades.count(),
    }
    return render(request, 'professor/atividades_list.html', context)


@professor_required
def atividade_create(request):
    """Criar nova atividade"""
    if request.method == 'POST':
        form = AtividadeForm(request.POST)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.professor = request.user
            atividade.save()
            messages.success(request, f'Atividade "{atividade.titulo}" criada com sucesso!')
            return redirect('professor_atividades')
        messages.error(request, 'Erro ao criar atividade. Verifique os campos.')
    else:
        form = AtividadeForm()

    context = {'form': form, 'action': 'Criar'}
    return render(request, 'professor/atividade_form.html', context)


@professor_required
def atividade_edit(request, pk):
    """Editar atividade existente"""
    atividade = get_object_or_404(Atividade, pk=pk, professor=request.user)

    if not atividade.pode_editar():
        messages.error(request, 'Não é possível editar atividade com submissões.')
        return redirect('professor_atividades')

    if request.method == 'POST':
        form = AtividadeForm(request.POST, instance=atividade)
        if form.is_valid():
            form.save()
            messages.success(request, f'Atividade "{atividade.titulo}" atualizada!')
            return redirect('professor_atividades')
        messages.error(request, 'Erro ao atualizar atividade.')
    else:
        form = AtividadeForm(instance=atividade)

    context = {
        'form': form,
        'action': 'Editar',
        'atividade': atividade
    }
    return render(request, 'professor/atividade_form.html', context)


@professor_required
def atividade_delete(request, pk):
    """Deletar atividade"""
    atividade = get_object_or_404(Atividade, pk=pk, professor=request.user)

    if request.method == 'POST':
        titulo = atividade.titulo
        total_submissoes = atividade.total_submissoes()
        atividade.delete()
        messages.warning(
            request,
            f'Atividade "{titulo}" deletada (incluindo {total_submissoes} submissões).'
        )
        return redirect('professor_atividades')

    context = {'atividade': atividade}
    return render(request, 'professor/atividade_confirm_delete.html', context)


@professor_required
def atividade_submissoes(request, pk):
    """Visualizar submissões de uma atividade"""
    atividade = get_object_or_404(Atividade, pk=pk, professor=request.user)
    submissoes = atividade.submissoes.select_related('aluno').order_by('aluno__nome')

    # Listar todos os alunos e marcar quem enviou
    todos_alunos = Aluno.objects.filter(is_active=True).order_by('nome')
    alunos_enviaram = submissoes.values_list('aluno_id', flat=True)

    alunos_info = []
    for aluno in todos_alunos:
        submissao = submissoes.filter(aluno=aluno).first()
        alunos_info.append({
            'aluno': aluno,
            'submissao': submissao,
            'status': 'enviado' if submissao else 'pendente'
        })

    context = {
        'atividade': atividade,
        'alunos_info': alunos_info,
        'total_submissoes': submissoes.count(),
        'total_alunos': todos_alunos.count(),
        'submissoes_pendentes': atividade.submissoes_pendentes(),
    }
    return render(request, 'professor/atividade_submissoes.html', context)


@professor_required
@require_POST
def submissao_corrigir(request, pk):
    """Corrigir submissão de aluno"""
    submissao = get_object_or_404(
        Submissao,
        pk=pk,
        atividade__professor=request.user
    )

    try:
        nota = request.POST.get('nota')
        observacao = request.POST.get('observacao', '').strip()

        # Validar nota
        if nota:
            nota = float(nota)
            if nota < 0 or nota > 10:
                return JsonResponse({
                    'success': False,
                    'message': 'Nota deve estar entre 0 e 10.'
                }, status=400)
            submissao.nota = nota

        submissao.observacao = observacao if observacao else None
        submissao.save()

        return JsonResponse({
            'success': True,
            'message': f'Correção salva para {submissao.aluno.nome}!',
            'nota': str(submissao.nota),
            'status': submissao.get_status_display()
        })

    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Nota inválida. Use números de 0 a 10.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao salvar correção: {str(e)}'
        }, status=500)


@professor_required
def professor_alunos(request):
    """Lista de alunos cadastrados"""
    alunos = Aluno.objects.filter(is_active=True).order_by('nome')

    # Estatísticas por aluno
    for aluno in alunos:
        total_atividades = Atividade.objects.count()
        aluno.total_atividades = total_atividades
        aluno.atividades_enviadas = aluno.submissoes.count()
        aluno.atividades_pendentes = total_atividades - aluno.atividades_enviadas
        aluno.media_notas = aluno.submissoes.filter(
            nota__isnull=False
        ).aggregate(models.Avg('nota'))['nota__avg'] or 0

    context = {
        'alunos': alunos,
        'total_alunos': alunos.count(),
    }
    return render(request, 'professor/alunos_list.html', context)


@professor_required
@require_POST
def gerar_com_ia(request):
    """Endpoint AJAX para gerar conteúdo com Gemini"""
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()

        if not prompt:
            return JsonResponse({
                'success': False,
                'message': 'Por favor, forneça um contexto para a IA.'
            }, status=400)

        gemini_service = GeminiService()
        conteudo_gerado = gemini_service.gerar_atividade(prompt)

        return JsonResponse({
            'success': True,
            'conteudo': conteudo_gerado,
            'message': 'Conteúdo gerado com sucesso!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao gerar conteúdo: {str(e)}'
        }, status=500)


# ============================================================================
# VIEWS DO ALUNO
# ============================================================================

@aluno_required
def aluno_atividades(request):
    """Lista de atividades disponíveis para o aluno"""
    aluno = get_object_or_404(Aluno, pk=request.session['aluno_id'])
    atividades = Atividade.objects.all().order_by('-created_at')

    # Verificar status de cada atividade
    atividades_info = []
    for atividade in atividades:
        submissao = Submissao.objects.filter(
            atividade=atividade,
            aluno=aluno
        ).first()

        if submissao:
            if submissao.nota is not None:
                status = 'corrigido'
                status_display = 'Corrigido'
                status_class = 'bg-blue-100 text-blue-800'
            else:
                status = 'aguardando_correcao'
                status_display = 'Aguardando Correção'
                status_class = 'bg-yellow-100 text-yellow-800'
        else:
            status = 'pendente'
            status_display = 'Pendente de Envio'
            status_class = 'bg-gray-100 text-gray-800'

        atividades_info.append({
            'atividade': atividade,
            'submissao': submissao,
            'status': status,
            'status_display': status_display,
            'status_class': status_class,
            'prazo_vencido': atividade.prazo_entrega < timezone.now().date()
        })

    context = {
        'atividades_info': atividades_info,
        'aluno': aluno,
    }
    return render(request, 'aluno/atividades_list.html', context)


@aluno_required
def atividade_detail(request, pk):
    """Visualizar detalhes de uma atividade e enviar resposta"""
    aluno = get_object_or_404(Aluno, pk=request.session['aluno_id'])
    atividade = get_object_or_404(Atividade, pk=pk)

    # Verificar se já existe submissão
    submissao = Submissao.objects.filter(
        atividade=atividade,
        aluno=aluno
    ).first()

    # Se já enviou, redireciona para resultado
    if submissao:
        return redirect('atividade_resultado', pk=pk)

    if request.method == 'POST':
        resposta = request.POST.get('resposta', '').strip()

        if not resposta:
            messages.error(request, 'A resposta não pode estar vazia.')
        else:
            submissao = Submissao.objects.create(
                atividade=atividade,
                aluno=aluno,
                resposta=resposta
            )
            messages.success(request, 'Atividade enviada com sucesso!')
            return redirect('aluno_atividades')

    context = {
        'atividade': atividade,
        'aluno': aluno,
    }
    return render(request, 'aluno/atividade_detail.html', context)


@aluno_required
def atividade_resultado(request, pk):
    """Ver resultado/correção de uma atividade"""
    aluno = get_object_or_404(Aluno, pk=request.session['aluno_id'])
    atividade = get_object_or_404(Atividade, pk=pk)

    submissao = get_object_or_404(
        Submissao,
        atividade=atividade,
        aluno=aluno
    )

    context = {
        'atividade': atividade,
        'submissao': submissao,
        'aluno': aluno,
    }
    return render(request, 'aluno/atividade_resultado.html', context)