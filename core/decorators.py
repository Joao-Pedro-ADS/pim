# core/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def professor_required(view_func):
    """
    Decorator para views que requerem autenticação de professor

    Usage:
        @professor_required
        def minha_view(request):
            # código da view
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verificar se usuário está autenticado
        if not request.user.is_authenticated:
            messages.warning(request, 'Você precisa estar logado como professor.')
            return redirect('login')

        # Verificar se é um Professor (não um aluno na sessão)
        if 'aluno_id' in request.session:
            messages.error(request, 'Acesso negado. Esta área é restrita a professores.')
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper


def aluno_required(view_func):
    """
    Decorator para views que requerem autenticação de aluno

    Usage:
        @aluno_required
        def minha_view(request):
            # código da view
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verificar se aluno_id está na sessão
        if 'aluno_id' not in request.session:
            messages.warning(request, 'Você precisa estar logado como aluno.')
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper