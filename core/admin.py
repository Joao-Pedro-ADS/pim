# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Professor, Aluno, Atividade, Submissao


@admin.register(Professor)
class ProfessorAdmin(UserAdmin):
    """
    Customização do admin para Professor
    """
    list_display = ['username', 'nome', 'email', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'nome', 'email']

    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('nome',)
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': ('nome', 'email')
        }),
    )


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    """
    Customização do admin para Aluno
    """
    list_display = ['nome', 'ra', 'is_active', 'created_at', 'total_submissoes']
    list_filter = ['is_active', 'created_at']
    search_fields = ['nome', 'ra']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'ra')
        }),
        ('Autenticação', {
            'fields': ('password',),
            'description': 'Digite a senha em texto puro. Ela será automaticamente criptografada.'
        }),
        ('Status', {
            'fields': ('is_active', 'created_at')
        }),
    )

    def total_submissoes(self, obj):
        """Mostra o total de submissões do aluno"""
        return obj.submissoes.count()

    total_submissoes.short_description = 'Total de Submissões'

    def save_model(self, request, obj, form, change):
        """
        Ao salvar, faz hash da senha se for novo aluno ou se a senha mudou
        """
        if not change:  # Novo aluno
            raw_password = form.cleaned_data.get('password')
            if raw_password:
                obj.set_password(raw_password)
        else:  # Editando aluno existente
            # Verificar se a senha mudou
            if 'password' in form.changed_data:
                raw_password = form.cleaned_data.get('password')
                if raw_password and not raw_password.startswith('pbkdf2_'):
                    # Se não começar com pbkdf2_, é senha em texto puro
                    obj.set_password(raw_password)

        super().save_model(request, obj, form, change)


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    """
    Customização do admin para Atividade
    """
    list_display = [
        'titulo',
        'professor',
        'prazo_entrega',
        'total_submissoes_display',
        'pendentes_correcao',
        'created_at'
    ]
    list_filter = ['prazo_entrega', 'created_at', 'professor']
    search_fields = ['titulo', 'descricao']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'prazo_entrega'

    fieldsets = (
        ('Informações da Atividade', {
            'fields': ('professor', 'titulo', 'descricao', 'prazo_entrega')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_submissoes_display(self, obj):
        """Mostra total de submissões"""
        total = obj.total_submissoes()
        return f"{total} submissão{'ões' if total != 1 else ''}"

    total_submissoes_display.short_description = 'Submissões'

    def pendentes_correcao(self, obj):
        """Mostra submissões pendentes"""
        pendentes = obj.submissoes_pendentes()
        if pendentes > 0:
            return f"⚠️ {pendentes} pendente{'s' if pendentes != 1 else ''}"
        return "✅ Todas corrigidas"

    pendentes_correcao.short_description = 'Status Correção'


@admin.register(Submissao)
class SubmissaoAdmin(admin.ModelAdmin):
    """
    Customização do admin para Submissão
    """
    list_display = [
        'aluno',
        'atividade',
        'nota',
        'status_display',
        'enviado_em',
        'corrigido_em'
    ]
    list_filter = ['enviado_em', 'corrigido_em', 'atividade']
    search_fields = ['aluno__nome', 'aluno__ra', 'atividade__titulo']
    readonly_fields = ['enviado_em', 'corrigido_em']
    date_hierarchy = 'enviado_em'

    fieldsets = (
        ('Informações', {
            'fields': ('atividade', 'aluno')
        }),
        ('Resposta', {
            'fields': ('resposta',)
        }),
        ('Correção', {
            'fields': ('nota', 'observacao')
        }),
        ('Metadados', {
            'fields': ('enviado_em', 'corrigido_em'),
            'classes': ('collapse',)
        }),
    )

    def status_display(self, obj):
        """Mostra o status da submissão com ícone"""
        status = obj.get_status()
        if status == 'corrigido':
            return f"✅ {obj.get_status_display()}"
        return f"⏳ {obj.get_status_display()}"

    status_display.short_description = 'Status'


# Customização do site admin
admin.site.site_header = "SmartClass - Administração"
admin.site.site_title = "SmartClass Admin"
admin.site.index_title = "Bem-vindo ao Painel Administrativo"