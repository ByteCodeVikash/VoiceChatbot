import os
import datetime
import time
from typing import Dict, Any, List

from config import CONFIG, PHRASES
from tts_module import TTSModule
from speech_module import SpeechModule

class VoiceAssistant:
    def __init__(self):
        self.current_language = "english"
        self.user_name = "Customer"
        
        self.user_context = {
            "name": self.user_name,
            "occupation": None,
            "location": None,
            "last_query_time": datetime.datetime.now()
        }
        
        os.makedirs("assets", exist_ok=True)
        
        # Initialize working TTS and Speech modules
        self.tts = TTSModule(
            model_name="gtts",
            voice_rate=CONFIG.get("voice_rate", 0.9),
            voice_volume=CONFIG.get("voice_volume", 1.0)
        )
        
        self.speech = SpeechModule(
            model_size=CONFIG.get("whisper_model_size", "small")
        )
        
        self.language_detector = None
        self.translator = None
        self.scheme_matcher = None
        
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize other components"""
        try:
            from language_detection import LanguageDetectionModule
            self.language_detector = LanguageDetectionModule(
                model_path=CONFIG.get("fasttext_model")
            )
        except Exception:
            self.language_detector = None
        
        try:
            from translation import TranslationModule
            self.translator = TranslationModule(
                model_name=CONFIG.get("indictrans_model")
            )
        except Exception:
            self.translator = None
        
        try:
            from scheme_matcher import SchemeMatcherModule
            self.scheme_matcher = SchemeMatcherModule(
                schemes_csv_path=CONFIG.get("schemes_csv_path"),
                embedding_model=CONFIG.get("embedding_model"),
                rasa_model_path=CONFIG.get("rasa_model_path"),
                confidence_threshold=CONFIG.get("confidence_threshold")
            )
        except Exception:
            self.scheme_matcher = None
    
    def _validate_components(self):
        """Validate if core components are working"""
        if not self.tts or not self.tts.available:
            print("❌ TTS not available")
            return False
        return True
    
    def speak(self, text, language=None):
        """Speak function"""
        if language is None:
            language = self.current_language
            
        # Handle phrase keys
        if text in PHRASES:
            if language in PHRASES[text]:
                text = PHRASES[text][language]
            else:
                text = PHRASES[text].get("english", text)
                
        # Format with user name if needed
        if "{}" in text and hasattr(self, "user_name"):
            text = text.format(self.user_name)
            
        if not self.tts or not self.tts.available:
            print(f"🔊 {text}")
            time.sleep(1)
            return False
            
        return self.tts.speak(text, language)
    
    def listen(self, timeout=None, force_english=False):
        """Listen function with improved settings"""
        if timeout is None:
            timeout = max(CONFIG.get("audio_timeout", 10), 8)  # Minimum 8 seconds
        
        # Try voice input first
        if self.speech and self.speech.available:
            try:
                listen_language = "english" if force_english else self.current_language
                recognized_text, confidence = self.speech.listen(
                    timeout=timeout, 
                    language=listen_language
                )
                
                if recognized_text and len(recognized_text.strip()) > 2:  # Minimum 3 chars
                    # Language detection
                    if not force_english and self.language_detector:
                        detected_language, det_confidence = self.language_detector.detect_language(
                            recognized_text, 
                            current_language=self.current_language
                        )
                        if det_confidence > 0.5:
                            self.current_language = detected_language
                    
                    return recognized_text.strip()
            except Exception as e:
                print(f"Voice recognition failed: {e}")
        
        # Fallback to text input
        print("Voice not detected, using text input...")
        return self.speech.get_text_input() if self.speech else self._get_text_input()
    
    def _get_text_input(self):
        """Basic text input fallback"""
        try:
            user_input = input(f"✍️ Type your message (or 'exit' to quit): ")
            if user_input.lower() in ["exit", "quit", "bye", "band karo"]:
                return "exit"
            if user_input.strip():
                return user_input.strip()
        except KeyboardInterrupt:
            return "exit"
        except Exception as e:
            print(f"Input error: {e}")
        return ""
    
    def select_language(self):
        """Language selection"""
        print("\n🌐 भाषा चुनें / Select Language:")
        print("1️⃣ हिंदी (Hindi)")
        print("2️⃣ English") 
        print("3️⃣ हिंग्लिश (Hinglish)")
        print()
        
        self.speak("Language select kariye: Hindi, English, ya Hinglish.", "hinglish")
        
        for attempt in range(3):
            print(f"\nAttempt {attempt + 1}/3:")
            
            # Try voice input first
            voice_input = self.listen(timeout=8, force_english=True)
            
            choice = voice_input.lower().strip() if voice_input and voice_input != "exit" else None
                
            # Fallback to text input if voice failed
            if not choice:
                choice = input("Type your choice (hindi/english/hinglish or 1/2/3): ").lower().strip()
                
            if choice == "exit":
                return None
                
            # Process choice
            if choice in ["hindi", "1", "हिंदी", "हिन्दी"]:
                print("Selected: Hindi")
                return "hindi"
            elif choice in ["english", "2", "अंग्रेजी"]:
                print("Selected: English")
                return "english"
            elif choice in ["hinglish", "3", "हिंग्लिश"]:
                print("Selected: Hinglish")
                return "hinglish"
            else:
                self.speak("Galat choice. Phir se try kariye.", "hinglish")
        
        # Default fallback
        print("Defaulting to Hinglish")
        return "hinglish"
    
    def get_user_name(self):
        """Get user name"""
        prompts = {
            "hindi": "आपका नाम क्या है?",
            "english": "What's your name?",
            "hinglish": "Aapka naam kya hai?"
        }
        
        self.speak(prompts[self.current_language])
        
        for attempt in range(2):
            name = self.listen(timeout=8)
                
            if name and name != "exit" and len(name.strip()) > 1:
                return name.strip()
                
            self.speak("Naam samajh nahi aaya. Phir boliye.")
        
        return "Friend"
    
    def find_relevant_schemes(self, query, top_n=3):
        """Find relevant schemes"""
        if not self.scheme_matcher or not self.scheme_matcher.available:
            return self._get_fallback_schemes()
        
        try:
            if hasattr(self.scheme_matcher, "set_user_context"):
                self.scheme_matcher.set_user_context(
                    name=self.user_name,
                    occupation=self.user_context.get("occupation"),
                    location=self.user_context.get("location")
                )
            
            schemes = self.scheme_matcher.find_relevant_schemes(query, top_n)
            if not schemes:
                return self._get_fallback_schemes()
            return schemes
        except Exception:
            return self._get_fallback_schemes()
    
    def _get_fallback_schemes(self):
        """Fallback schemes with clean, short descriptions"""
        return [
            {
                "Name": "PM Kisan Samman Nidhi",
                "Details": "Financial assistance to farmers",
                "Eligibility": "All small and marginal farmers",
                "Benefits": "₹6000 per year in three installments",
                "URL": "https://pmkisan.gov.in/",
                "similarity_score": 0.9
            },
            {
                "Name": "Ayushman Bharat",
                "Details": "Health insurance scheme",
                "Eligibility": "Poor and vulnerable families", 
                "Benefits": "Health coverage up to ₹5 lakhs per family per year",
                "URL": "https://pmjay.gov.in/",
                "similarity_score": 0.85
            }
        ]
    
    def _clean_scheme_data(self, scheme):
        """Clean and shorten scheme data for better TTS"""
        import re
        
        # Clean encoding issues
        def clean_text(text):
            if not text or str(text).lower() == "nan":
                return ""
            
            text = str(text)
            # Fix common encoding issues
            text = text.replace("â‚¹", "₹")
            text = text.replace("â€", "")
            text = text.replace("â€™", "'")
            text = text.replace("â€œ", '"')
            text = text.replace("â€", '"')
            text = text.replace("â€¢", "•")
            
            # Remove excessive formatting
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # Limit length for TTS
            if len(text) > 150:
                sentences = text.split('.')
                if len(sentences) > 1:
                    text = sentences[0] + "."
                else:
                    text = text[:150] + "..."
            
            return text
        
        # Clean all scheme fields
        cleaned_scheme = {}
        for key, value in scheme.items():
            cleaned_scheme[key] = clean_text(value)
        
        return cleaned_scheme
    
    def format_scheme_response(self, schemes, language):
        """Format scheme response with better TTS handling"""
        if not schemes:
            return PHRASES["no_schemes"][language]
        
        # Clean the schemes data first
        cleaned_schemes = [self._clean_scheme_data(scheme) for scheme in schemes[:2]]
        
        # Create short, TTS-friendly response
        if language == "hindi":
            response = "आपके लिए दो मुख्य योजनाएं हैं। "
        elif language == "hinglish":
            response = "Aapke liye do main schemes hain। "
        else:
            response = "Here are two main schemes for you। "
        
        for i, scheme in enumerate(cleaned_schemes, 1):
            scheme_name = scheme.get("Name", "Government Scheme")
            benefits = scheme.get("Benefits", "")
            
            # Create very short description
            if language == "hindi":
                scheme_text = f"{i}. {scheme_name}। "
                if benefits:
                    scheme_text += f"लाभ: {benefits}। "
            elif language == "hinglish":
                scheme_text = f"{i}. {scheme_name}। "
                if benefits:
                    scheme_text += f"Benefits: {benefits}। "
            else:
                scheme_text = f"{i}. {scheme_name}। "
                if benefits:
                    scheme_text += f"Benefits: {benefits}। "
            
            response += scheme_text
        
        # Add closing
        if language == "hindi":
            response += "अधिक जानकारी के लिए पूछें।"
        elif language == "hinglish":
            response += "Aur jaankari ke liye poochiye।"
        else:
            response += "Ask for more details if needed।"
        
        return response
    
    def get_time_based_greeting(self):
        """Get time-based greeting"""
        hour = datetime.datetime.now().hour
        
        if 5 <= hour < 12:
            return "good_morning"
        elif 12 <= hour < 17:
            return "good_afternoon"
        else:
            return "good_evening"
    
    def run_conversation(self):
        """Main conversation loop"""
        print("🤖 Government Schemes Voice Assistant Starting...")
        print("=" * 50)
        
        if not self._validate_components():
            print("❌ Some components not available, but continuing...")
        
        try:
            # Language selection
            self.current_language = self.select_language()
            if not self.current_language:
                self.speak("Goodbye!", "english")
                return
            
            self.speak("language_selected")
            
            # Greeting
            greeting = self.get_time_based_greeting()
            self.speak(greeting)
            self.speak("welcome")
            
            # Get user name
            self.speak("ask_name")
            name = self.get_user_name()
            
            if name and name != "exit":
                self.user_name = name
                self.user_context["name"] = self.user_name
                self.speak("thank_you")
            
            # Get occupation/location
            self.speak("ask_occupation")
            context_info = self.listen(timeout=10)
            
            if context_info and context_info != "exit":
                words = context_info.lower().split()
                
                occupation = None
                location = None
                
                location_keywords = ["in", "from", "at"]
                for keyword in location_keywords:
                    if keyword in words:
                        keyword_index = words.index(keyword)
                        if keyword_index < len(words) - 1:
                            location = " ".join(words[keyword_index + 1:])
                            occupation = " ".join(words[:keyword_index])
                            break
                
                if not occupation and not location:
                    occupation = context_info
                
                if occupation and len(occupation.strip()) > 1:
                    self.user_context["occupation"] = occupation.strip()
                if location and len(location.strip()) > 1:
                    self.user_context["location"] = location.strip()
            
            # Main conversation loop
            print(f"\n💬 Chat with {self.user_name} ({self.current_language})")
            print("Say 'exit' to quit")
            print("-" * 40)
            
            conversation_count = 0
            max_conversations = 5
            
            while conversation_count < max_conversations:
                print("\n" + "="*30)
                
                self.speak("ask_query")
                query = self.listen(timeout=15)
                
                if not query or query == "exit" or len(query.strip()) < 2:
                    if query == "exit":
                        break
                    continue
                
                conversation_count += 1
                
                # Find and present schemes
                relevant_schemes = self.find_relevant_schemes(query.strip())
                response = self.format_scheme_response(relevant_schemes, self.current_language)
                
                print(f"\n📋 Response: {response}\n")  # Show what will be spoken
                self.speak(response)
                
                if conversation_count >= max_conversations:
                    break
                
                # Ask for more questions
                self.speak("anything_else")
                more_questions = self.listen(timeout=8)
                
                if more_questions and any(word in more_questions.lower() for word in 
                                         ["no", "nahi", "nahin", "exit", "quit", "stop", "bye", "goodbye"]):
                    break
            
            # Closing
            self.speak("closing")
            
        except KeyboardInterrupt:
            print("\n\n👋 Bye!")
            self.speak("closing")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.speak("closing")

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run_conversation()