# core/services/gemini_service.py
import google.generativeai as genai
from django.conf import settings


class GeminiService:
    """
    Service para integração com API do Gemini - SmartClass
    Gera conteúdo educacional com IA
    """

    def __init__(self):
        """
        Inicializa o serviço com a API Key do Gemini
        """
        api_key = settings.GEMINI_API_KEY
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    def gerar_atividade(self, prompt):
        """
        Gera conteúdo de atividade baseado no prompt do professor

        Args:
            prompt (str): Instrução/contexto fornecido pelo professor

        Returns:
            str: Texto da atividade gerada

        Raises:
            Exception: Se houver erro na geração ou API não configurada
        """
        if not self.model:
            raise Exception(
                "Gemini API não configurada. "
                "Por favor, adicione GEMINI_API_KEY no arquivo .env"
            )

        try:
            system_prompt = f"""
            Você é um assistente pedagógico do SmartClass, especializado em criar 
            atividades escolares de alta qualidade.

            Baseado no contexto fornecido pelo professor, crie uma atividade educacional 
            clara, objetiva e adequada ao nível de ensino mencionado.

            Contexto do professor: {prompt}

            IMPORTANTE:
            - Gere apenas o texto da atividade, sem títulos ou formatações extras
            - Seja claro e objetivo
            - Adeque a linguagem ao nível de ensino
            - Se não houver nível especificado, use linguagem intermediária
            - Não use markdown ou formatações especiais
            """

            response = self.model.generate_content(system_prompt)
            return response.text

        except Exception as e:
            raise Exception(f"Erro ao gerar atividade com Gemini: {str(e)}")