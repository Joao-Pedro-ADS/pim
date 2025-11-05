# backend/core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Professor(AbstractUser):
    """
    Professor - Único no sistema
    Herda de AbstractUser para ter autenticação completa do Django
    """
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome Completo',
        help_text='Nome completo do professor'
    )

    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'

    def __str__(self):
        return self.nome or self.username


class Aluno(models.Model):
    """
    Aluno - Identificado por RA único
    Autenticação via RA + senha (não usa Django User)
    """
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome Completo',
        help_text='Nome completo do aluno'
    )
    ra = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='RA (Registro Acadêmico)',
        help_text='Registro Acadêmico único do aluno'
    )
    password = models.CharField(
        max_length=128,
        verbose_name='Senha',
        help_text='Senha com hash'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo',
        help_text='Indica se o aluno está ativo no sistema'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Cadastrado em'
    )

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['ra']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.nome} ({self.ra})"

    def set_password(self, raw_password):
        """
        Define a senha do aluno com hash

        Args:
            raw_password (str): Senha em texto puro
        """
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Verifica se a senha fornecida está correta

        Args:
            raw_password (str): Senha em texto puro

        Returns:
            bool: True se a senha está correta
        """
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def total_atividades(self):
        """Retorna o total de atividades disponíveis"""
        return Atividade.objects.count()

    def atividades_enviadas(self):
        """Retorna o total de atividades já enviadas pelo aluno"""
        return self.submissoes.count()

    def atividades_pendentes(self):
        """Retorna o total de atividades pendentes de envio"""
        return self.total_atividades() - self.atividades_enviadas()

    def media_notas(self):
        """Calcula a média das notas do aluno"""
        submissoes_com_nota = self.submissoes.filter(nota__isnull=False)
        if submissoes_com_nota.exists():
            from django.db.models import Avg
            return submissoes_com_nota.aggregate(Avg('nota'))['nota__avg']
        return 0


class Atividade(models.Model):
    """
    Atividade postada pelo professor
    Pode ser gerada com auxílio da IA ou manualmente
    """
    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name='atividades',
        verbose_name='Professor',
        help_text='Professor que criou a atividade'
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título',
        help_text='Título da atividade'
    )
    descricao = models.TextField(
        verbose_name='Descrição',
        help_text='Descrição completa da atividade'
    )
    prazo_entrega = models.DateField(
        verbose_name='Prazo de Entrega',
        help_text='Data limite para entrega'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criada em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizada em'
    )

    class Meta:
        verbose_name = 'Atividade'
        verbose_name_plural = 'Atividades'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['professor', '-created_at']),
            models.Index(fields=['prazo_entrega']),
        ]

    def __str__(self):
        return self.titulo

    def pode_editar(self):
        """
        Verifica se a atividade pode ser editada
        Regra: Só pode editar se não houver submissões

        Returns:
            bool: True se pode editar
        """
        return self.submissoes.count() == 0

    def total_submissoes(self):
        """
        Retorna o total de submissões enviadas

        Returns:
            int: Número de submissões
        """
        return self.submissoes.count()

    def submissoes_pendentes(self):
        """
        Retorna o total de submissões aguardando correção

        Returns:
            int: Número de submissões sem nota
        """
        return self.submissoes.filter(nota__isnull=True).count()

    def submissoes_corrigidas(self):
        """
        Retorna o total de submissões já corrigidas

        Returns:
            int: Número de submissões com nota
        """
        return self.submissoes.filter(nota__isnull=False).count()

    def prazo_vencido(self):
        """
        Verifica se o prazo de entrega já passou

        Returns:
            bool: True se vencido
        """
        return timezone.now().date() > self.prazo_entrega

    def get_status_badge_class(self):
        """
        Retorna a classe CSS para o badge de status

        Returns:
            str: Classes Tailwind CSS
        """
        if self.prazo_vencido():
            return 'bg-red-100 text-red-800'
        return 'bg-green-100 text-green-800'

    def dias_restantes(self):
        """
        Calcula quantos dias faltam para o prazo

        Returns:
            int: Número de dias (negativo se vencido)
        """
        delta = self.prazo_entrega - timezone.now().date()
        return delta.days


class Submissao(models.Model):
    """
    Submissão de atividade por aluno
    Relação: Um aluno pode enviar apenas UMA resposta por atividade
    """
    atividade = models.ForeignKey(
        Atividade,
        on_delete=models.CASCADE,
        related_name='submissoes',
        verbose_name='Atividade',
        help_text='Atividade que está sendo respondida'
    )
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name='submissoes',
        verbose_name='Aluno',
        help_text='Aluno que enviou a resposta'
    )
    resposta = models.TextField(
        verbose_name='Resposta',
        help_text='Resposta do aluno para a atividade'
    )
    nota = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name='Nota (0-10)',
        help_text='Nota atribuída pelo professor'
    )
    observacao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observação do Professor',
        help_text='Feedback do professor para o aluno'
    )
    enviado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Enviado em'
    )
    corrigido_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Corrigido em'
    )

    class Meta:
        verbose_name = 'Submissão'
        verbose_name_plural = 'Submissões'
        unique_together = ['atividade', 'aluno']
        ordering = ['aluno__nome']
        indexes = [
            models.Index(fields=['atividade', 'aluno']),
            models.Index(fields=['nota']),
        ]

    def __str__(self):
        return f"{self.aluno.nome} - {self.atividade.titulo}"

    def get_status(self):
        """
        Retorna o status da submissão

        Returns:
            str: 'pendente', 'aguardando_correcao' ou 'corrigido'
        """
        if self.nota is not None:
            return 'corrigido'
        return 'aguardando_correcao'

    def get_status_display(self):
        """
        Retorna o status formatado para exibição

        Returns:
            str: Status em português
        """
        status_map = {
            'corrigido': 'Corrigido',
            'aguardando_correcao': 'Aguardando Correção'
        }
        return status_map.get(self.get_status(), 'Desconhecido')

    def get_status_badge_class(self):
        """
        Retorna a classe CSS para o badge de status

        Returns:
            str: Classes Tailwind CSS
        """
        if self.get_status() == 'corrigido':
            return 'bg-blue-100 text-blue-800'
        return 'bg-yellow-100 text-yellow-800'

    def get_nota_badge_class(self):
        """
        Retorna a classe CSS baseada na nota

        Returns:
            str: Classes Tailwind CSS
        """
        if self.nota is None:
            return 'bg-gray-100 text-gray-800'
        elif self.nota >= 7:
            return 'bg-green-100 text-green-800'
        elif self.nota >= 5:
            return 'bg-yellow-100 text-yellow-800'
        else:
            return 'bg-red-100 text-red-800'

    def tempo_para_correcao(self):
        """
        Calcula o tempo que levou para corrigir (em horas)

        Returns:
            float: Horas entre envio e correção, ou None
        """
        if self.corrigido_em:
            delta = self.corrigido_em - self.enviado_em
            return delta.total_seconds() / 3600
        return None

    def save(self, *args, **kwargs):
        """
        Override do save para atualizar automaticamente a data de correção
        Quando uma nota é atribuída, define corrigido_em automaticamente
        """
        if self.nota is not None and not self.corrigido_em:
            self.corrigido_em = timezone.now()
        super().save(*args, **kwargs)