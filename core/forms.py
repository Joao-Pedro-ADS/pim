# core/forms.py
from django import forms
from .models import Atividade, Aluno, Submissao


class AtividadeForm(forms.ModelForm):
    """
    Formulário para criar/editar atividades
    """

    class Meta:
        model = Atividade
        fields = ['titulo', 'descricao', 'prazo_entrega']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ex: Exercícios de Matemática - Frações'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 12,
                'placeholder': 'Descreva a atividade ou use a IA para gerar o conteúdo...'
            }),
            'prazo_entrega': forms.DateInput(attrs={
                'type': 'date',
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
        }
        labels = {
            'titulo': 'Título da Atividade',
            'descricao': 'Descrição da Atividade',
            'prazo_entrega': 'Prazo de Entrega'
        }


class AlunoForm(forms.ModelForm):
    """
    Formulário para cadastrar alunos (usado no admin)
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        }),
        label='Senha',
        help_text='Digite a senha do aluno'
    )

    class Meta:
        model = Aluno
        fields = ['nome', 'ra', 'password', 'is_active']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'ra': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SubmissaoForm(forms.ModelForm):
    """
    Formulário para aluno enviar resposta da atividade
    """

    class Meta:
        model = Submissao
        fields = ['resposta']
        widgets = {
            'resposta': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none',
                'rows': 12,
                'placeholder': 'Digite sua resposta aqui...'
            }),
        }
        labels = {
            'resposta': ''
        }


class CorrecaoForm(forms.ModelForm):
    """
    Formulário para professor corrigir submissão
    """

    class Meta:
        model = Submissao
        fields = ['nota', 'observacao']
        widgets = {
            'nota': forms.NumberInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'min': '0',
                'max': '10',
                'placeholder': 'Ex: 8.5'
            }),
            'observacao': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Deixe um feedback para o aluno...'
            }),
        }
        labels = {
            'nota': 'Nota (0 a 10)',
            'observacao': 'Observação / Feedback'
        }