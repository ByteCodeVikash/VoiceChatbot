import os
import re
from typing import Tuple
from synonym_dict import SYNONYMS

class EnhancedLanguageDetectionModule:
    def __init__(self, model_path="lid.176.bin"):
        self.model_path = model_path
        self.model = None
        self.available = self._load_model()
        
        self.hindi_pattern = re.compile(r'[ऀ-ॿ]')
        
        self.hinglish_words = set()
        self.english_words = set()
        self.hindi_words = set()
        
        self._build_word_sets()
    
    def _load_model(self):
        if not os.path.exists(self.model_path):
            return False
        
        try:
            import fasttext
            fasttext.FastText.eprint = lambda x: None
            self.model = fasttext.load_model(self.model_path)
            return True
        except ImportError:
            return False
        except Exception:
            return False
    
    def _build_word_sets(self):
        for key, synonyms in SYNONYMS.items():
            self.english_words.add(key)
            
            for synonym in synonyms:
                if self.hindi_pattern.search(synonym):
                    self.hindi_words.add(synonym.lower())
                elif any(char in synonym for char in ['kya', 'hai', 'aap', 'main', 'mein']):
                    self.hinglish_words.add(synonym.lower())
                else:
                    self.english_words.add(synonym.lower())
        
        base_hinglish = {
            "kya", "hai", "haan", "nahi", "mera", "aapka", "main", "mein", "tum", "aap",
            "kaise", "kahan", "kab", "kaun", "kyun", "kyu", "matlab", "samajh", "pata",
            "accha", "theek", "chalo", "bol", "dekh", "jao", "karo", "karein", "ho",
            "scheme", "yojana", "government", "help", "madad", "chahiye", "batao",
            "dijiye", "milega", "kaise", "apply", "documents", "papers", "eligibility"
        }
        
        base_english = {
            "the", "is", "at", "which", "on", "and", "a", "to", "are", "as", "was",
            "with", "for", "his", "would", "have", "there", "he", "been", "has",
            "scheme", "government", "help", "need", "want", "how", "what", "when",
            "where", "farmer", "fisherman", "benefit", "money", "financial"
        }
        
        base_hindi = {
            "क्या", "है", "हूँ", "हूं", "मैं", "आप", "तुम", "कैसे", "कहाँ", "कब",
            "कौन", "क्यों", "अच्छा", "बुरा", "हाँ", "नहीं", "यहाँ", "वहाँ", "आज",
            "कल", "सरकारी", "योजना", "किसान", "लाभ", "मदद", "सहायता"
        }
        
        self.hinglish_words.update(base_hinglish)
        self.english_words.update(base_english)
        self.hindi_words.update(base_hindi)
    
    def detect_language(self, text, current_language="english"):
        if not text or len(text.strip()) < 2:
            return current_language, 1.0
        
        text = text.strip().lower()
        
        if self.hindi_pattern.search(text):
            return "hindi", 0.9
        
        hinglish_score = self._calculate_hinglish_score(text)
        english_score = self._calculate_english_score(text)
        hindi_score = self._calculate_hindi_score(text)
        
        if hinglish_score > 0.3:
            return "hinglish", hinglish_score
        elif english_score > 0.4 and hindi_score < 0.2:
            return "english", english_score
        elif hindi_score > 0.3:
            return "hindi", hindi_score
        
        if self.available and self.model:
            try:
                labels, probs = self.model.predict(text, k=3)
                
                for label, prob in zip(labels, probs):
                    lang_code = label.replace('__label__', '')
                    
                    if lang_code == 'hi' and prob > 0.3:
                        if hinglish_score > 0.2:
                            return "hinglish", 0.6
                        return "hindi", float(prob)
                    elif lang_code == 'en' and prob > 0.3:
                        if hinglish_score > 0.2:
                            return "hinglish", 0.5
                        return "english", float(prob)
            except Exception:
                pass
        
        scores = {
            "hinglish": hinglish_score,
            "english": english_score,
            "hindi": hindi_score
        }
        
        best_lang = max(scores, key=scores.get)
        best_score = scores[best_lang]
        
        if best_score > 0.2:
            return best_lang, best_score
        else:
            return current_language, 0.5
    
    def _calculate_hinglish_score(self, text):
        words = text.split()
        if not words:
            return 0.0
        
        hinglish_count = sum(1 for word in words if word in self.hinglish_words)
        english_count = sum(1 for word in words if word in self.english_words)
        
        hinglish_ratio = hinglish_count / len(words)
        english_ratio = english_count / len(words)
        
        mixed_patterns = [
            r'\b(kya|hai|main|mein|aap)\b.*\b(scheme|government|help)\b',
            r'\b(scheme|help|government)\b.*\b(kaise|kya|chahiye)\b',
            r'\b(farmer|kisan)\b.*\b(yojana|scheme)\b'
        ]
        
        pattern_bonus = 0
        for pattern in mixed_patterns:
            if re.search(pattern, text):
                pattern_bonus += 0.2
        
        score = hinglish_ratio * 0.5 + english_ratio * 0.3 + pattern_bonus
        
        if hinglish_count > 0 and english_count > 0:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_english_score(self, text):
        words = text.split()
        if not words:
            return 0.0
        
        english_count = sum(1 for word in words if word in self.english_words)
        
        english_patterns = [
            r'\bi\s+(am|have|need|want)\b',
            r'\b(what|how|when|where)\s+\w+\b',
            r'\b(can|do|will)\s+you\b',
            r'\b(government|scheme|farmer|fisherman)\s+\w+\b'
        ]
        
        pattern_matches = sum(1 for pattern in english_patterns if re.search(pattern, text))
        
        base_score = english_count / len(words)
        pattern_bonus = min(pattern_matches * 0.2, 0.4)
        
        return min(base_score + pattern_bonus, 1.0)
    
    def _calculate_hindi_score(self, text):
        words = text.split()
        if not words:
            return 0.0
        
        hindi_count = sum(1 for word in words if word in self.hindi_words)
        devanagari_count = sum(1 for word in words if self.hindi_pattern.search(word))
        
        if devanagari_count > 0:
            return min(0.8 + (devanagari_count / len(words)) * 0.2, 1.0)
        
        return hindi_count / len(words)