# backend/core/services/gemini_service.py
import google.generativeai as genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    """Serviço para interagir com a API do Google Gemini"""

    def __init__(self):
        """Inicializa o serviço com a chave da API"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY não configurada. Configure no arquivo .env")

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')

    def gerar_atividade(self, tema, disciplina=None, nivel_dificuldade=None, tipo_atividade=None):
        """
        Gera uma atividade baseada nos parâmetros fornecidos

        Args:
            tema (str): Tema principal da atividade
            disciplina (str, optional): Disciplina (ex: Matemática, História)
            nivel_dificuldade (str, optional): Nível (ex: Fácil, Médio, Difícil)
            tipo_atividade (str, optional): Tipo (ex: Dissertativa, Múltipla Escolha)

        Returns:
            dict: Contém 'titulo' e 'descricao' da atividade gerada
        """
        try:
            prompt = self._construir_prompt(tema, disciplina, nivel_dificuldade, tipo_atividade)

            logger.info(f"Gerando atividade com tema: {tema}")
            response = self.model.generate_content(prompt)

            # Processar a resposta
            texto_gerado = response.text.strip()
            resultado = self._processar_resposta(texto_gerado)

            logger.info("Atividade gerada com sucesso")
            return resultado

        except Exception as e:
            logger.error(f"Erro ao gerar atividade: {str(e)}")
            raise Exception(f"Erro ao gerar atividade: {str(e)}")

    def _construir_prompt(self, tema, disciplina, nivel_dificuldade, tipo_atividade):
        """Constrói o prompt para a IA baseado nos parâmetros"""

        prompt = f"""Você é um assistente especializado em criar atividades acadêmicas para professores.

TAREFA: Crie uma atividade educacional completa sobre o tema: "{tema}"

"""

        if disciplina:
            prompt += f"DISCIPLINA: {disciplina}\n"

        if nivel_dificuldade:
            prompt += f"NÍVEL DE DIFICULDADE: {nivel_dificuldade}\n"

        if tipo_atividade:
            prompt += f"TIPO DE ATIVIDADE: {tipo_atividade}\n"

        prompt += """
FORMATO DA RESPOSTA:
- Primeiro, forneça um TÍTULO curto e atrativo para a atividade (máximo 100 caracteres)
- Depois, forneça a DESCRIÇÃO completa da atividade

INSTRUÇÕES:
1. O título deve ser claro, objetivo e despertar interesse
2. A descrição deve conter:
   - Contexto ou introdução ao tema
   - Enunciado claro da atividade/questão
   - Instruções específicas sobre o que o aluno deve fazer
   - Se aplicável, critérios de avaliação
3. Use linguagem clara e adequada ao nível educacional
4. Seja específico e detalhado na descrição
5. A atividade deve ser desafiadora mas realizável

FORMATO DE SAÍDA:
TÍTULO: [título da atividade aqui]

DESCRIÇÃO:
[descrição completa da atividade aqui]
"""

        return prompt

    def _processar_resposta(self, texto):
        """Processa a resposta da IA e extrai título e descrição"""

        linhas = texto.split('\n')
        titulo = ""
        descricao = []
        capturando_descricao = False

        for linha in linhas:
            linha_limpa = linha.strip()

            # Extrair título
            if linha_limpa.startswith('TÍTULO:') or linha_limpa.startswith('Título:'):
                titulo = linha_limpa.split(':', 1)[1].strip()

            # Começar a capturar descrição
            elif linha_limpa.startswith('DESCRIÇÃO:') or linha_limpa.startswith('Descrição:'):
                capturando_descricao = True
                # Verificar se já tem conteúdo na mesma linha
                resto = linha_limpa.split(':', 1)[1].strip()
                if resto:
                    descricao.append(resto)

            # Capturar linhas da descrição
            elif capturando_descricao and linha_limpa:
                descricao.append(linha_limpa)

        # Se não encontrou no formato esperado, usar heurística
        if not titulo or not descricao:
            # Tentar primeira linha como título
            if linhas:
                titulo = linhas[0].strip().replace('TÍTULO:', '').replace('Título:', '').strip()
                descricao = [l.strip() for l in linhas[1:] if l.strip()]

        # Limitar título a 200 caracteres
        titulo = titulo[:200] if titulo else "Atividade Gerada"

        # Juntar descrição
        descricao_final = '\n\n'.join(descricao) if descricao else texto

        return {
            'titulo': titulo,
            'descricao': descricao_final
        }

    def gerar_feedback(self, resposta_aluno, atividade_descricao):
        """
        Gera um feedback personalizado para a resposta do aluno

        Args:
            resposta_aluno (str): Resposta enviada pelo aluno
            atividade_descricao (str): Descrição original da atividade

        Returns:
            str: Feedback gerado
        """
        try:
            prompt = f"""Você é um professor avaliando a resposta de um aluno.

ATIVIDADE PROPOSTA:
{atividade_descricao}

RESPOSTA DO ALUNO:
{resposta_aluno}

TAREFA:
Forneça um feedback construtivo e educacional sobre a resposta do aluno. O feedback deve:
1. Destacar os pontos positivos da resposta
2. Apontar áreas que podem ser melhoradas
3. Ser encorajador e motivacional
4. Ser claro e objetivo
5. Ter entre 100 e 300 palavras

Forneça apenas o feedback, sem prefixos ou títulos.
"""

            response = self.model.generate_content(prompt)
            feedback = response.text.strip()

            logger.info("Feedback gerado com sucesso")
            return feedback

        except Exception as e:
            logger.error(f"Erro ao gerar feedback: {str(e)}")
            raise Exception(f"Erro ao gerar feedback: {str(e)}")


# Instância global do serviço
gemini_service = GeminiService()