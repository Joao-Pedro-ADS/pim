from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Autenticação
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Professor - Atividades
    path('professor/atividades/', views.professor_atividades, name='professor_atividades'),
    path('professor/atividades/criar/', views.atividade_create, name='atividade_create'),
    path('professor/atividades/<int:pk>/editar/', views.atividade_edit, name='atividade_edit'),
    path('professor/atividades/<int:pk>/deletar/', views.atividade_delete, name='atividade_delete'),
    path('professor/atividades/<int:pk>/submissoes/', views.atividade_submissoes, name='atividade_submissoes'),

    # Professor - Submissões
    path('professor/submissoes/<int:pk>/corrigir/', views.submissao_corrigir, name='submissao_corrigir'),

    # Professor - Alunos
    path('professor/alunos/', views.professor_alunos, name='professor_alunos'),

    # Professor - IA
    path('api/gerar-atividade/', views.gerar_com_ia, name='gerar_com_ia'),

    # Aluno - Atividades
    path('aluno/atividades/', views.aluno_atividades, name='aluno_atividades'),
    path('aluno/atividades/<int:pk>/', views.atividade_detail, name='atividade_detail'),
    path('aluno/atividades/<int:pk>/resultado/', views.atividade_resultado, name='atividade_resultado'),
]