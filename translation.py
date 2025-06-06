from typing import Optional
from synonym_dict import SYNONYMS
import re

class ImprovedTranslationModule:
    def __init__(self, model_name="indictrans2"):
        self.model_name = model_name
        self.en_to_hi_translator = None
        self.hi_to_en_translator = None
        self.available = self._load_models()
        self.synonym_dict = self._build_translation_dict()
    
    def _load_models(self):
        try:
            from indictrans2 import load_indictrans2_model
            self.en_to_hi_translator = load_indictrans2_model(src="eng", tgt="hin")
            self.hi_to_en_translator = load_indictrans2_model(src="hin", tgt="eng")
            return True
        except ImportError:
            print("⚠️ IndicTrans2 not available, using synonym fallback")
            return False
        except Exception as e:
            print(f"⚠️ IndicTrans2 failed to load: {e}")
            return False
    
    def _build_translation_dict(self):
        en_to_hi = {}
        hi_to_en = {}
        
        for key, synonyms in SYNONYMS.items():
            en_to_hi[key] = []
            
            for synonym in synonyms:
                if re.search(r'[ऀ-ॿ]', synonym):
                    en_to_hi[key].append(synonym)
                    hi_to_en[synonym] = key
        
        direct_translations = {
            "government": "सरकार",
            "scheme": "योजना", 
            "farmer": "किसान",
            "help": "मदद",
            "benefit": "लाभ",
            "money": "पैसा",
            "application": "आवेदन",
            "documents": "दस्तावेज",
            "eligibility": "पात्रता",
            "how": "कैसे",
            "what": "क्या",
            "where": "कहाँ",
            "when": "कब",
            "why": "क्यों",
            "who": "कौन",
            "name": "नाम",
            "occupation": "व्यवसाय",
            "location": "स्थान",
            "thank you": "धन्यवाद",
            "welcome": "स्वागत",
            "hello": "नमस्कार",
            "good": "अच्छा",
            "yes": "हाँ",
            "no": "नहीं"
        }
        
        for eng, hin in direct_translations.items():
            en_to_hi[eng] = [hin] if eng not in en_to_hi else en_to_hi[eng] + [hin]
            hi_to_en[hin] = eng
        
        return {"en_to_hi": en_to_hi, "hi_to_en": hi_to_en}
    
    def translate(self, text, source_lang, target_lang):
        if source_lang == target_lang or not text:
            return text
        
        text = text.strip()
        
        if self.available:
            try:
                if source_lang == "english" and target_lang == "hindi":
                    return self._translate_en_to_hi(text)
                elif source_lang == "hindi" and target_lang == "english":
                    return self._translate_hi_to_en(text)
                elif source_lang == "hinglish":
                    if target_lang == "hindi":
                        return self._translate_hinglish_to_hi(text)
                    elif target_lang == "english":
                        return self._translate_hinglish_to_en(text)
            except Exception as e:
                print(f"⚠️ Translation failed: {e}")
        
        return self._fallback_translate(text, source_lang, target_lang)
    
    def _translate_en_to_hi(self, text):
        try:
            if self.en_to_hi_translator:
                result = self.en_to_hi_translator.translate_paragraph(text)
                return result if result else text
            return text
        except Exception:
            return text
    
    def _translate_hi_to_en(self, text):
        try:
            if self.hi_to_en_translator:
                result = self.hi_to_en_translator.translate_paragraph(text)
                return result if result else text
            return text
        except Exception:
            return text
    
    def _translate_hinglish_to_hi(self, text):
        words = text.split()
        result = []
        
        for word in words:
            word_clean = word.lower().strip('.,!?')
            
            if re.search(r'[ऀ-ॿ]', word):
                result.append(word)
            elif word_clean in self.synonym_dict["en_to_hi"]:
                hindi_options = self.synonym_dict["en_to_hi"][word_clean]
                hindi_word = next((h for h in hindi_options if re.search(r'[ऀ-ॿ]', h)), word)
                result.append(hindi_word)
            else:
                if self.available and self.en_to_hi_translator:
                    try:
                        translated = self.en_to_hi_translator.translate_paragraph(word)
                        result.append(translated if translated else word)
                    except:
                        result.append(word)
                else:
                    result.append(word)
        
        return " ".join(result)
    
    def _translate_hinglish_to_en(self, text):
        words = text.split()
        result = []
        
        for word in words:
            word_clean = word.lower().strip('.,!?')
            
            if word_clean in self.synonym_dict["hi_to_en"]:
                result.append(self.synonym_dict["hi_to_en"][word_clean])
            elif re.search(r'[ऀ-ॿ]', word):
                if self.available and self.hi_to_en_translator:
                    try:
                        translated = self.hi_to_en_translator.translate_paragraph(word)
                        result.append(translated if translated else word)
                    except:
                        result.append(word)
                else:
                    result.append(word)
            else:
                result.append(word)
        
        return " ".join(result)
    
    def _fallback_translate(self, text, source_lang, target_lang):
        words = text.split()
        translated_words = []
        
        for word in words:
            word_clean = word.lower().strip('.,!?')
            translated = word
            
            if source_lang == "english" and target_lang == "hindi":
                if word_clean in self.synonym_dict["en_to_hi"]:
                    hindi_options = self.synonym_dict["en_to_hi"][word_clean]
                    translated = next((h for h in hindi_options if re.search(r'[ऀ-ॿ]', h)), word)
            
            elif source_lang == "hindi" and target_lang == "english":
                if word_clean in self.synonym_dict["hi_to_en"]:
                    translated = self.synonym_dict["hi_to_en"][word_clean]
            
            elif source_lang == "hinglish":
                if target_lang == "hindi":
                    if word_clean in self.synonym_dict["en_to_hi"]:
                        hindi_options = self.synonym_dict["en_to_hi"][word_clean]
                        translated = next((h for h in hindi_options if re.search(r'[ऀ-ॿ]', h)), word)
                elif target_lang == "english":
                    if word_clean in self.synonym_dict["hi_to_en"]:
                        translated = self.synonym_dict["hi_to_en"][word_clean]
            
            translated_words.append(translated)
        
        return " ".join(translated_words)