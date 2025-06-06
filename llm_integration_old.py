# ==================== llm_integration.py ====================
import requests
import json
from config import CONFIG

class PhiLLMIntegration:
    def __init__(self):
        self.model = CONFIG["ollama_model"]
        self.base_url = "http://localhost:11434/api/generate"
        self.available = self.check_ollama()
    
    def check_ollama(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, schemes, query, language="english", user_context=None):
        if not self.available or not schemes:
            return self.fallback_response(schemes, language)
        
        try:
            prompt = self.build_prompt(schemes, query, language, user_context)
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 150
                }
            }
            
            response = requests.post(self.base_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                
                if generated_text and len(generated_text) > 10:
                    return self.clean_response(generated_text)
            
        except Exception as e:
            pass
        
        return self.fallback_response(schemes, language)
    
    def build_prompt(self, schemes, query, language, user_context):
        scheme = schemes[0]
        name = scheme.get('Name', '')
        benefits = scheme.get('Benefits', '')
        
        lang_prompts = {
            "english": f"Scheme: {name}. Benefits: {benefits}. Answer briefly in English.",
            "hindi": f"योजना: {name}. लाभ: {benefits}. हिंदी में संक्षेप में उत्तर दें।",
            "hinglish": f"Scheme: {name}. Benefits: {benefits}. Hinglish mein short answer dijiye."
        }
        
        return lang_prompts.get(language, lang_prompts["english"])
    
    def clean_response(self, text):
        import re
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) > 100:
            sentences = text.split('.')
            text = sentences[0] + '.'
        
        return text
    
    def fallback_response(self, schemes, language):
        if not schemes:
            return {
                "english": "No suitable scheme found.",
                "hindi": "कोई उपयुक्त योजना नहीं मिली।",
                "hinglish": "Koi suitable scheme nahi mili।"
            }.get(language, "No scheme found.")
        
        scheme = schemes[0]
        name = scheme.get('Name', '')
        
        return {
            "english": f"{name}. This scheme can help you.",
            "hindi": f"{name}। यह योजना आपकी मदद कर सकती है।",
            "hinglish": f"{name}। Yeh scheme aapki help kar sakti hai।"
        }.get(language, f"{name}.")