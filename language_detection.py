import os
import re
from typing import Tuple

class LanguageDetectionModule:
    def __init__(self, model_path: str = "lid.176.bin"):
        self.model_path = model_path
        self.model = None
        self.available = self._load_model()
        
        self.hindi_pattern = re.compile(r'[ऀ-ॿ]')
        self.hinglish_words = {
            "kya", "haan", "nahi", "mera", "aapka", "humara", "kaise", "hai", "namaskar", 
            "acha", "theek", "chalo", "kitna", "karna", "kuch", "apna", "main", "tum", 
            "aap", "mujhe", "bol", "dekh", "samajh", "jao", "karo", "karein", "hota",
            "kar", "ho", "gaya", "kya", "kaha", "kahan", "kab", "kaun", "kyun", "kyu",
            "matlab", "samajh", "pata", "malum", "accha", "bura", "sahi", "galat",
            "paisa", "rupaye", "scheme", "yojana", "sarkar", "government", "help",
            "madad", "chahiye", "want", "need", "farmer", "kisan", "health", "sehat"
        }
        
        self.english_words = {
            "the", "is", "at", "which", "on", "and", "a", "to", "are", "as", "was",
            "with", "for", "his", "would", "have", "there", "he", "been", "has",
            "scheme", "government", "help", "need", "want", "farmer", "health",
            "money", "benefit", "apply", "eligibility", "how", "what", "when", "where"
        }
    
    def _load_model(self) -> bool:
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
    
    def detect_language(self, text: str, current_language: str = "english") -> Tuple[str, float]:
        if not text or len(text.strip()) < 2:
            return current_language, 1.0
        
        text = text.strip().lower()
        
        if self.hindi_pattern.search(text):
            return "hindi", 0.9
        
        hinglish_score = self._calculate_hinglish_score(text)
        english_score = self._calculate_english_score(text)
        
        if hinglish_score > 0.3:
            return "hinglish", hinglish_score
        elif english_score > 0.5:
            return "english", english_score
        
        if self.available and self.model:
            try:
                labels, probs = self.model.predict(text, k=3)
                
                for label, prob in zip(labels, probs):
                    lang_code = label.replace('__label__', '')
                    
                    if lang_code == 'hi' and prob > 0.3:
                        if hinglish_score > 0.2:
                            return "hinglish", 0.7
                        return "hindi", float(prob)
                    elif lang_code == 'en' and prob > 0.4:
                        if hinglish_score > 0.2:
                            return "hinglish", 0.6
                        return "english", float(prob)
                        
            except Exception:
                pass
        
        if hinglish_score > english_score and hinglish_score > 0.1:
            return "hinglish", hinglish_score
        elif english_score > 0.3:
            return "english", english_score
        else:
            return current_language, 0.5
    
    def _calculate_hinglish_score(self, text: str) -> float:
        words = text.split()
        if not words:
            return 0.0
        
        hinglish_count = sum(1 for word in words if word in self.hinglish_words)
        english_count = sum(1 for word in words if word in self.english_words)
        
        if len(words) == 0:
            return 0.0
        
        hinglish_ratio = hinglish_count / len(words)
        english_ratio = english_count / len(words)
        
        mixed_indicators = [
            "aur", "ya", "hai", "main", "mein", "ke", "ki", "ka", "ko", "se", "me"
        ]
        mixed_count = sum(1 for word in words if word in mixed_indicators)
        mixed_ratio = mixed_count / len(words)
        
        score = hinglish_ratio * 0.6 + english_ratio * 0.3 + mixed_ratio * 0.1
        
        if hinglish_count > 0 and english_count > 0:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_english_score(self, text: str) -> float:
        words = text.split()
        if not words:
            return 0.0
        
        english_count = sum(1 for word in words if word in self.english_words)
        
        common_english_patterns = [
            r'\bi\s+am\b', r'\bi\s+have\b', r'\bi\s+need\b', r'\bi\s+want\b',
            r'\bwhat\s+is\b', r'\bhow\s+to\b', r'\bcan\s+you\b', r'\bdo\s+you\b'
        ]
        
        pattern_matches = sum(1 for pattern in common_english_patterns 
                            if re.search(pattern, text))
        
        base_score = english_count / len(words)
        pattern_bonus = min(pattern_matches * 0.2, 0.4)
        
        return min(base_score + pattern_bonus, 1.0)