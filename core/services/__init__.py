GeminiService = None

def get_gemini_service():
    global GeminiService
    if GeminiService is None:
        from .gemini_service import GeminiService as _GeminiService
        GeminiService = _GeminiService
    return GeminiService
