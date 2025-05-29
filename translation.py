from typing import Optional

class TranslationModule:
    def __init__(self, model_name: str = "indictrans2"):
        self.model_name = model_name
        self.en_to_hi_translator = None
        self.hi_to_en_translator = None
        self.available = self._load_models()
        self.fallback_dict = self._load_fallback_dict()
    
    def _load_models(self):
        try:
            from indictrans2 import load_indictrans2_model
            self.en_to_hi_translator = load_indictrans2_model(src="eng", tgt="hin")
            self.hi_to_en_translator = load_indictrans2_model(src="hin", tgt="eng")
            return True
        except ImportError:
            return False
        except Exception:
            return False
    
    def _load_fallback_dict(self):
        return {
            "english_to_hindi": {
                "government": "सरकारी",
                "scheme": "योजना",
                "schemes": "योजनाएं",
                "farmer": "किसान",
                "farmers": "किसान",
                "health": "स्वास्थ्य",
                "insurance": "बीमा",
                "benefit": "लाभ",
                "benefits": "लाभ",
                "money": "पैसा",
                "rupees": "रुपये",
                "assistance": "सहायता",
                "help": "मदद",
                "apply": "आवेदन",
                "application": "आवेदन",
                "eligibility": "पात्रता",
                "eligible": "पात्र",
                "thank you": "धन्यवाद",
                "welcome": "स्वागत",
                "hello": "नमस्कार",
                "good": "अच्छा",
                "bad": "बुरा",
                "yes": "हाँ",
                "no": "नहीं",
                "here": "यहाँ",
                "there": "वहाँ",
                "today": "आज",
                "tomorrow": "कल",
                "name": "नाम",
                "occupation": "व्यवसाय",
                "location": "स्थान"
            },
            "hindi_to_english": {
                "सरकारी": "government",
                "योजना": "scheme",
                "योजनाएं": "schemes",
                "किसान": "farmer",
                "स्वास्थ्य": "health",
                "बीमा": "insurance",
                "लाभ": "benefit",
                "पैसा": "money",
                "रुपये": "rupees",
                "सहायता": "assistance",
                "मदद": "help",
                "आवेदन": "application",
                "पात्रता": "eligibility",
                "पात्र": "eligible",
                "धन्यवाद": "thank you",
                "स्वागत": "welcome",
                "नमस्कार": "hello",
                "अच्छा": "good",
                "बुरा": "bad",
                "हाँ": "yes",
                "नहीं": "no",
                "यहाँ": "here",
                "वहाँ": "there",
                "आज": "today",
                "कल": "tomorrow",
                "नाम": "name",
                "व्यवसाय": "occupation",
                "स्थान": "location"
            }
        }
    
    def translate(self, text, source_lang, target_lang):
        if source_lang == target_lang or not text:
            return text
        
        if self.available:
            try:
                if source_lang == "english" and target_lang == "hindi":
                    return self._translate_en_to_hi(text)
                elif source_lang == "hindi" and target_lang == "english":
                    return self._translate_hi_to_en(text)
                elif source_lang == "hinglish" and target_lang == "hindi":
                    return self._translate_hinglish_to_hi(text)
                elif source_lang == "hinglish" and target_lang == "english":
                    return text
                else:
                    return text
            except Exception:
                pass
        
        return self._fallback_translate(text, source_lang, target_lang)
    
    def _translate_en_to_hi(self, text):
        try:
            if self.en_to_hi_translator:
                return self.en_to_hi_translator.translate_paragraph(text)
            return text
        except Exception:
            return text
    
    def _translate_hi_to_en(self, text):
        try:
            if self.hi_to_en_translator:
                return self.hi_to_en_translator.translate_paragraph(text)
            return text
        except Exception:
            return text
            
    def _translate_hinglish_to_hi(self, text):
        try:
            if self.en_to_hi_translator:
                import re
                hindi_pattern = re.compile(r'[ऀ-ॿ]')
                words = text.split()
                result = []
                
                for word in words:
                    if hindi_pattern.search(word):
                        result.append(word)
                    else:
                        try:
                            hindi_word = self.en_to_hi_translator.translate_paragraph(word)
                            result.append(hindi_word)
                        except Exception:
                            result.append(word)
                
                return " ".join(result)
            return text
        except Exception:
            return text
    
    def _fallback_translate(self, text, source_lang, target_lang):
        try:
            words = text.split()
            translated_words = []
            
            for word in words:
                word_lower = word.lower().strip('.,!?')
                translated = word
                
                if source_lang == "english" and target_lang == "hindi":
                    if word_lower in self.fallback_dict["english_to_hindi"]:
                        translated = self.fallback_dict["english_to_hindi"][word_lower]
                elif source_lang == "hindi" and target_lang == "english":
                    if word_lower in self.fallback_dict["hindi_to_english"]:
                        translated = self.fallback_dict["hindi_to_english"][word_lower]
                
                translated_words.append(translated)
            
            return " ".join(translated_words)
            
        except Exception:
            return text