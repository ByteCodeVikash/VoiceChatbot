# voice_assistant.py - COMPLETE FIXED VERSION with Working gTTS
import os
import datetime
import time
import logging
import tempfile
import subprocess
from typing import Dict, Any, List
from gtts import gTTS

from config import CONFIG, PHRASES
from speech_module import FastSpeechModule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkingTTS:
    """Ultra Reliable gTTS implementation - COMPLETE FIXED VERSION"""
    
    def __init__(self):
        self.available = self._test_gtts()
        print(f"🔊 Working TTS: {'✅ Available' if self.available else '❌ Not Available'}")
    
    def _test_gtts(self):
        """Test if gTTS and audio players work"""
        try:
            # Test gTTS
            tts = gTTS(text="test", lang="en", slow=False)
            
            # Test audio players
            players = ["mpg123", "ffplay", "paplay"]
            for player in players:
                try:
                    result = subprocess.run([player, "--help"], capture_output=True, timeout=2)
                    return True  # If any player responds, we're good
                except:
                    continue
            return False
        except:
            return False
    
    def speak(self, text, language="english"):
        """FIXED: Speak text using gTTS without repetition - COMPLETE VERSION"""
        if not self.available:
            print(f"🔊 {text}")
            time.sleep(len(text) * 0.05)  # Simulate speaking time
            return False
        
        try:
            # Clean text
            clean_text = str(text).strip()
            if not clean_text:
                return False
            
            # Remove problematic characters
            clean_text = clean_text.replace('।', '.').replace('…', '...')
            clean_text = clean_text.replace('\n', ' ').replace('\r', ' ')
            clean_text = ' '.join(clean_text.split())  # Clean whitespace
            
            print(f"🔊 Speaking: {clean_text}")
            
            # Language mapping
            lang_code = "en" if language.lower() == "english" else "hi"
            
            # FIXED: Better chunking strategy - NO REPETITION
            if len(clean_text) > 300:
                print(f"📝 Long text detected ({len(clean_text)} chars), using smart chunking...")
                
                # IMPROVED: Smart sentence-based chunking
                sentences = self._smart_sentence_split(clean_text)
                
                if len(sentences) <= 1:
                    # If no proper sentences, use word-based chunking
                    return self._word_based_chunking(clean_text, lang_code)
                
                # Process sentences in groups
                chunks = []
                current_chunk = ""
                
                for sentence in sentences:
                    # Calculate if adding this sentence exceeds limit
                    potential_chunk = current_chunk + (" " if current_chunk else "") + sentence
                    
                    if len(potential_chunk) <= 280:  # Safe limit for gTTS
                        current_chunk = potential_chunk
                    else:
                        # Save current chunk if it has content
                        if current_chunk.strip():
                            chunks.append(current_chunk.strip())
                        
                        # Start new chunk with current sentence
                        current_chunk = sentence
                
                # Add final chunk
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # CRITICAL: Remove duplicates and ensure no overlap
                unique_chunks = self._remove_duplicate_chunks(chunks)
                
                # Speak each unique chunk
                success_count = 0
                total_chunks = len(unique_chunks)
                
                print(f"🎵 Speaking in {total_chunks} parts...")
                
                for i, chunk in enumerate(unique_chunks):
                    chunk_preview = chunk[:50] + "..." if len(chunk) > 50 else chunk
                    print(f"🔊 Part {i+1}/{total_chunks}: {chunk_preview}")
                    
                    if self._speak_chunk(chunk, lang_code):
                        success_count += 1
                        time.sleep(0.3)  # Short pause between chunks
                    else:
                        print(f"❌ Failed to speak chunk {i+1}")
                
                print(f"✅ Completed speaking {success_count}/{total_chunks} parts")
                return success_count > 0
            else:
                # Short text - speak directly
                return self._speak_chunk(clean_text, lang_code)
                
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            print(f"📄 Fallback text: {text}")
            time.sleep(len(text) * 0.05)
            return False
    
    def _smart_sentence_split(self, text):
        """IMPROVED: Smart sentence splitting"""
        import re
        
        # Handle different sentence endings
        # For Hindi: । and .
        # For English: . ! ?
        sentence_endings = r'[।\.!?]+'
        
        # Split by sentence endings
        raw_sentences = re.split(sentence_endings, text)
        
        # Clean and filter sentences
        sentences = []
        for sentence in raw_sentences:
            sentence = sentence.strip()
            # Only keep sentences with substantial content
            if len(sentence) > 10 and len(sentence.split()) >= 3:
                # Add back the period for proper speech
                if not sentence.endswith('.'):
                    sentence += '.'
                sentences.append(sentence)
        
        return sentences
    
    def _word_based_chunking(self, text, lang_code):
        """Fallback: Word-based chunking for texts without clear sentences"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            
            if current_length + word_length <= 250:  # Conservative limit
                current_chunk.append(word)
                current_length += word_length
            else:
                # Complete current chunk
                if current_chunk:
                    chunk_text = ' '.join(current_chunk) + '.'
                    chunks.append(chunk_text)
                
                # Start new chunk
                current_chunk = [word]
                current_length = word_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk) + '.'
            chunks.append(chunk_text)
        
        # Speak each chunk
        success_count = 0
        for i, chunk in enumerate(chunks):
            print(f"🔊 Word-chunk {i+1}/{len(chunks)}: {chunk[:50]}...")
            if self._speak_chunk(chunk, lang_code):
                success_count += 1
                time.sleep(0.3)
        
        return success_count > 0
    
    def _remove_duplicate_chunks(self, chunks):
        """CRITICAL: Remove duplicate and overlapping chunks"""
        if not chunks:
            return []
        
        unique_chunks = []
        seen_content = set()
        
        for chunk in chunks:
            # Normalize chunk for comparison (lowercase, no punctuation)
            normalized = ''.join(c.lower() for c in chunk if c.isalnum() or c.isspace()).strip()
            normalized_words = set(normalized.split())
            
            # Check if this chunk is too similar to existing ones
            is_duplicate = False
            
            for seen in seen_content:
                seen_words = set(seen.split())
                
                # Calculate overlap percentage
                if len(normalized_words) > 0 and len(seen_words) > 0:
                    overlap = len(normalized_words.intersection(seen_words))
                    overlap_percentage = overlap / min(len(normalized_words), len(seen_words))
                    
                    # If more than 70% overlap, consider duplicate
                    if overlap_percentage > 0.7:
                        is_duplicate = True
                        break
            
            if not is_duplicate and len(chunk.strip()) > 10:
                unique_chunks.append(chunk)
                seen_content.add(normalized)
        
        print(f"🧹 Deduplication: {len(chunks)} → {len(unique_chunks)} chunks")
        return unique_chunks
    
    def _speak_chunk(self, text, lang_code):
        """Speak a single chunk of text - IMPROVED ERROR HANDLING"""
        try:
            if len(text.strip()) < 3:
                return True  # Skip very short texts
            
            # Create TTS with better error handling
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            # Save to temp file with better naming
            temp_filename = f"tts_{int(time.time() * 1000)}.mp3"
            temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
            
            tts.save(temp_path)
            
            # Play with multiple fallback players
            players = [
                ["mpg123", "-q", temp_path],
                ["ffplay", "-nodisp", "-autoexit", "-v", "quiet", temp_path],
                ["paplay", temp_path],
                ["aplay", temp_path]  # Additional fallback
            ]
            
            success = False
            for player_cmd in players:
                try:
                    result = subprocess.run(
                        player_cmd, 
                        capture_output=True, 
                        timeout=30,  # Increased timeout
                        check=False
                    )
                    if result.returncode == 0:
                        success = True
                        break
                except subprocess.TimeoutExpired:
                    print(f"⏰ Player {player_cmd[0]} timed out")
                    continue
                except Exception as e:
                    print(f"❌ Player {player_cmd[0]} failed: {e}")
                    continue
            
            # Cleanup temp file
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except:
                pass
            
            if not success:
                print(f"❌ All audio players failed for chunk: {text[:30]}...")
            
            return success
            
        except Exception as e:
            print(f"❌ Chunk TTS error: {e}")
            return False

class EnhancedVoiceAssistant:
    def __init__(self):
        self.current_language = "english"
        self.user_name = "Customer"
        self.name_collected = False
        
        self.user_context = {
            "name": self.user_name,
            "occupation": None,
            "location": None,
            "last_query_time": datetime.datetime.now()
        }
        
        os.makedirs(CONFIG["cache_dir"], exist_ok=True)
        
        # Use Working gTTS instead of complex TTS
        self.tts = WorkingTTS()
        
        self.speech = FastSpeechModule(
            model_size=CONFIG.get("whisper_model_size", "small"),
            sample_rate=CONFIG.get("sample_rate", 44100)
        )
        
        self.language_detector = None
        self.translator = None
        self.scheme_db = None
        
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize all components with enhanced RAG database"""
        try:
            from language_detection import EnhancedLanguageDetectionModule
            self.language_detector = EnhancedLanguageDetectionModule()
        except Exception:
            self.language_detector = None
        
        try:
            from translation import ImprovedTranslationModule
            self.translator = ImprovedTranslationModule()
        except Exception:
            self.translator = None
        
        # Initialize WORKING Enhanced RAG Database
        try:
            from enhanced_rag_database import EnhancedRAGDatabase
            
            groq_api_key = CONFIG.get("GROQ_API_KEY", "")
            if not groq_api_key:
                try:
                    import json
                    config_path = "config.json"
                    if os.path.exists(config_path):
                        with open(config_path) as f:
                            config_data = json.load(f)
                            groq_api_key = config_data.get("GROQ_API_KEY", "")
                except:
                    pass
            
            if groq_api_key:
                self.scheme_db = EnhancedRAGDatabase(
                    csv_path=CONFIG["schemes_csv_path"],
                    groq_api_key=groq_api_key
                )
                
                if self.scheme_db.available:
                    logger.info("✅ WORKING RAG Database initialized successfully")
                    
                    total_schemes = self.scheme_db.get_scheme_count()
                    if total_schemes > 0:
                        logger.info(f"📊 Database contains {total_schemes} schemes")
                        
                        # Test search
                        logger.info("🧪 Testing WORKING RAG search...")
                        test_results = self.scheme_db.search_by_context(
                            "agriculture schemes", 
                            occupation="farmer", 
                            location="gujarat"
                        )
                        if test_results:
                            logger.info(f"✅ WORKING RAG test successful - found {len(test_results)} results")
                            first_result = test_results[0].get('Details', 'Unknown')
                            logger.info(f"📋 Sample scheme: {first_result[:70]}...")
                        else:
                            logger.warning("⚠️ WORKING RAG test returned no results")
                    else:
                        logger.warning("⚠️ Database appears to be empty")
                else:
                    logger.error("❌ WORKING Enhanced RAG Database failed to initialize")
                    self.scheme_db = None
            else:
                logger.error("❌ No Groq API key found")
                self.scheme_db = None
                
        except Exception as e:
            logger.error(f"❌ Enhanced RAG Database initialization failed: {e}")
            import traceback
            traceback.print_exc()
            self.scheme_db = None
    
    def _validate_components(self):
        """Validate all components"""
        if not self.tts or not self.tts.available:
            logger.warning("TTS not available")
        if not self.scheme_db or not self.scheme_db.available:
            logger.warning("Enhanced RAG Database not available")
            return False
        return True
    
    def speak(self, text, language=None):
        """WORKING: Speak any length text perfectly"""
        if language is None:
            language = self.current_language
        
        # Handle phrase translations
        if text in PHRASES:
            if language in PHRASES[text]:
                text = PHRASES[text][language]
            else:
                text = PHRASES[text].get("english", text)
        
        # Handle name formatting
        if "{}" in text and hasattr(self, "user_name"):
            text = text.format(self.user_name)
        
        # Use working gTTS - handles ANY length
        return self.tts.speak(text, language)
    
    def listen_hybrid(self, prompt, timeout=5, skip_voice=False):
        """Hybrid input: voice attempt + text fallback"""
        print(f"\n{prompt}")
        
        if not skip_voice and self.speech and self.speech.available:
            try:
                print("🎤 Speak now or press Enter for text input...")
                recognized_text, confidence = self.speech.listen(
                    timeout=timeout,
                    language=self.current_language
                )
                
                if recognized_text and len(recognized_text.strip()) > 2 and recognized_text != "exit":
                    print(f"✅ Voice input: '{recognized_text}'")
                    return recognized_text.strip()
                else:
                    print("🔇 Voice unclear, switching to text input...")
            except Exception as e:
                print(f"🔇 Voice failed: {e}")
        
        # Text input fallback
        try:
            user_input = input("✍️ Type: ")
            
            if user_input.lower().strip() in ["exit", "quit", "bye", "band karo", "khatam"]:
                return "exit"
            
            if user_input.strip():
                print(f"📝 Text input: '{user_input.strip()}'")
                return user_input.strip()
            else:
                print("⚠️ Empty input")
                return ""
                
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            return "exit"
        except Exception as e:
            logger.error(f"Input error: {e}")
            return ""
    
    def select_language(self):
        """Language selection with voice support"""
        print("\n🌐 SELECT LANGUAGE / भाषा चुनें:")
        print("1️⃣ हिंदी (Hindi)")
        print("2️⃣ English")
        print("3️⃣ हिंग्लिश (Hinglish)")
        
        self.speak("Language select kariye: Hindi, English, ya Hinglish.", "hinglish")
        
        choice = self.listen_hybrid(
            "Choose language (hindi/english/hinglish or 1/2/3):",
            timeout=8,
            skip_voice=False
        )
        
        if choice == "exit":
            return None
        
        choice_lower = choice.lower().strip()
        
        if choice_lower in ["hindi", "1", "हिंदी", "hin"]:
            print("✅ Selected: Hindi")
            return "hindi"
        elif choice_lower in ["english", "2", "अंग्रेजी", "eng"]:
            print("✅ Selected: English")
            return "english"
        elif choice_lower in ["hinglish", "3", "हिंग्लिश", "mix"]:
            print("✅ Selected: Hinglish")
            return "hinglish"
        else:
            print("⚠️ Invalid choice, defaulting to Hindi")
            return "hindi"
    
    def get_user_name(self):
        """FIXED: Get user name with working TTS"""
        if self.name_collected:
            return self.user_name
        
        prompts = {
            "hindi": "आपका नाम क्या है?",
            "english": "What's your name?",
            "hinglish": "Aapka naam kya hai?"
        }
        
        # WORKING: Name prompt will be spoken clearly
        prompt_text = prompts[self.current_language]
        self.speak(prompt_text)
        
        name = self.listen_hybrid(
            prompt_text,
            timeout=8,
            skip_voice=False
        )
        
        if name and name != "exit" and len(name.strip()) > 1:
            self.name_collected = True
            return name.strip()
        
        self.name_collected = True
        return "Friend"
    
    def parse_user_occupation(self, context_info):
        """Enhanced occupation and location parsing"""
        if not context_info:
            return None, None
        
        context_lower = context_info.lower().strip('"').strip("'")
        
        # Enhanced occupation patterns
        occupation_patterns = {
            "farmer": [
                "farmer", "kisan", "किसान", "किशन", "kheti", "खेती", "agriculture", "कृषि", 
                "crop", "field", "khet", "खेत", "गांव", "gaon", "farming", "कृषक", "krishak",
                "खेतिहर", "khetihar", "cultivation", "उत्पादन", "seeds", "fertilizer", "krushi"
            ],
            "fisherman": [
                "fisherman", "machhuara", "मछुआरा", "fishing", "boat", "marine", "मछली", 
                "machli", "नाव", "nav", "समुद्री", "samudr", "मत्स्य", "matsya"
            ],
            "women": [
                "women", "mahila", "महिला", "female", "woman", "lady", "औरत", "aurat",
                "girl", "लड़की", "ladki", "बेटी", "beti", "womens"
            ],
            "teacher": [
                "teacher", "shikshak", "शिक्षक", "school", "college", "पढ़ाना", "padhana",
                "अध्यापक", "adhyapak", "guru", "गुरु"
            ],
            "doctor": [
                "doctor", "daktar", "डॉक्टर", "medical", "hospital", "चिकित्सक", "chikitsak",
                "वैद्य", "vaidya"
            ],
            "business": [
                "business", "vyavasaya", "व्यवसाय", "shop", "dukan", "दुकान", "udyog", "उद्योग",
                "व्यापार", "vyapar", "entrepreneur", "उद्यमी", "udyami"
            ],
            "student": [
                "student", "vidyarthi", "विद्यार्थी", "college", "school", "पढ़ाई", "padhai",
                "छात्र", "chhatr", "छात्रा", "chhatra"
            ]
        }
        
        detected_occupation = None
        max_score = 0
        
        for occupation, keywords in occupation_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in context_lower:
                    score += len(keyword) * 2
                    if keyword == context_lower or f" {keyword} " in f" {context_lower} ":
                        score += 5
            
            if score > max_score:
                max_score = score
                detected_occupation = occupation
        
        # Enhanced location extraction
        location = None
        
        location_patterns = [
            r"(.+?)\s+से",           # "Gujarat se"
            r"(.+?)\s+में",          # "Gujarat mein"  
            r"(.+?)\s+from",         # "from Gujarat"
            r"(.+?)\s+in",           # "in Gujarat"
            r"(.+?)\s+ka",           # "Gujarat ka"
            r"(.+?)\s+ki",           # "Gujarat ki"
            r"(.+?)\s+state",        # "Gujarat state"
            r"(.+?)\s+प्रदेश",        # "Uttar Pradesh"
        ]
        
        import re
        for pattern in location_patterns:
            match = re.search(pattern, context_info, re.IGNORECASE)
            if match:
                potential_location = match.group(1).strip()
                location_words = potential_location.split()
                if location_words:
                    location = " ".join(location_words[-2:]).strip('।.,!?"')
                    break
        
        # Direct location keyword matching
        if not location:
            location_keywords = {
                "gujarat": ["गुजरात", "gujarat", "guj"],
                "andhra pradesh": ["आंध्र प्रदेश", "andhra pradesh", "andhra", "ap"],
                "goa": ["गोवा", "goa"],
                "karnataka": ["कर्नाटक", "karnataka", "bangalore", "बंगलोर"],
                "kerala": ["केरल", "kerala", "kochi", "कोच्चि"],
                "tamil nadu": ["तमिल नाडु", "tamil nadu", "tn", "chennai", "चेन्नई"],
                "maharashtra": ["महाराष्ट्र", "maharashtra", "mumbai", "मुंबई", "pune", "पुणे"],
                "uttar pradesh": ["उत्तर प्रदेश", "uttar pradesh", "up", "lucknow", "लखनौ"],
                "rajasthan": ["राजस्थान", "rajasthan", "jaipur", "जयपुर"],
                "punjab": ["पंजाब", "punjab"],
                "haryana": ["हरियाणा", "haryana"],
                "north eastern": ["north eastern", "northeast", "उत्तर पूर्वी", "ne"]
            }
            
            for state, keywords in location_keywords.items():
                for keyword in keywords:
                    if keyword in context_lower:
                        location = state
                        break
                if location:
                    break
        
        # Default to farmer if agriculture context exists
        if not detected_occupation and any(word in context_lower for word in ["seeds", "fertilizer", "krushi", "crop", "farming"]):
            detected_occupation = "farmer"
        
        final_occupation = detected_occupation if detected_occupation else "farmer"
        
        logger.info(f"Parsed: '{context_info}' -> Occupation: '{final_occupation}', Location: '{location}'")
        return final_occupation, location
    
    def find_relevant_schemes(self, query, top_n=5):
        """Enhanced scheme search using RAG"""
        if not self.scheme_db or not self.scheme_db.available:
            logger.warning("Enhanced RAG Database not available")
            return []
        
        try:
            occupation = self.user_context.get("occupation")
            location = self.user_context.get("location")
            
            logger.info(f"🔍 WORKING RAG Search for: '{query}' | Occupation: {occupation} | Location: {location}")
            
            # Use RAG-powered search
            results = self.scheme_db.search_by_context(query, occupation, location, top_n)
            
            if results:
                logger.info(f"✅ WORKING RAG found {len(results)} schemes")
                
                # Enhanced logging for debugging
                for i, result in enumerate(results[:3], 1):
                    name = result.get('Name', 'Unknown')[:50]
                    details = result.get('Details', 'No details')[:50]
                    score = result.get('Score', 0)
                    logger.info(f"📋 Scheme: {name}...")
                
                return results
            else:
                logger.warning("❌ No schemes found with WORKING RAG")
                return []
        
        except Exception as e:
            logger.error(f"WORKING RAG search error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def format_scheme_response(self, schemes, query, language):
        """FIXED: Dynamic response from RAG - NO HARDCODED RESPONSES"""
        if not schemes:
            no_scheme_msgs = {
                "hindi": "कोई संबंधित योजना नहीं मिली। कृपया अधिक विवरण दें।",
                "english": "No relevant schemes found. Please provide more details.",
                "hinglish": "Koi relevant scheme nahi mili। Please aur details dijiye।"
            }
            return no_scheme_msgs.get(language, no_scheme_msgs["english"])
        
        try:
            # Get the actual detailed answer from RAG - COMPLETELY DYNAMIC
            from enhanced_rag_database import answer_schemes_question
            
            # Build enhanced query with language preference
            occupation = self.user_context.get("occupation", "")
            location = self.user_context.get("location", "")
            
            enhanced_query = query
            if occupation:
                enhanced_query += f" for {occupation}"
            if location:
                enhanced_query += f" in {location}"
            
            # Add language instruction to query for better responses
            if language == "hindi":
                enhanced_query += " answer in Hindi हिंदी में जवाब दें"
            elif language == "hinglish":
                enhanced_query += " answer in Hinglish हिंग्लिश में जवाब दें"
            
            # Get detailed answer from RAG - COMPLETELY DYNAMIC
            detailed_answer = answer_schemes_question(enhanced_query)
            
            if detailed_answer and len(detailed_answer.strip()) > 20:
                # Clean and format for voice - NO HARDCODING
                import re
                
                # Remove any remaining special chars
                detailed_answer = re.sub(r'[<>{}*#]', '', detailed_answer)
                
                # Basic cleaning for voice output
                detailed_answer = re.sub(r'\s+', ' ', detailed_answer)
                detailed_answer = detailed_answer.strip()
                
                # Return the COMPLETE DYNAMIC response from RAG
                logger.info(f"📋 Using dynamic RAG answer ({language}): {detailed_answer[:80]}...")
                return detailed_answer.strip()
            
        except Exception as e:
            logger.error(f"Error getting detailed answer: {e}")
        
        # Only if RAG completely fails, use basic scheme info (still dynamic)
        scheme = schemes[0]
        name = scheme.get("Name", "Government Scheme")
        details = scheme.get("Details", "")
        benefits = scheme.get("Benefits", "")
        
        # Clean name for voice
        if len(name) > 80:
            name = " ".join(name.split()[:10])
        
        # Create response from actual scheme data (DYNAMIC)
        response_parts = []
        
        if name and name != "Government Scheme Information":
            response_parts.append(f"{name}")
        
        if details and len(details) > 10:
            response_parts.append(details[:150])
        
        if benefits and len(benefits) > 10:
            response_parts.append(f"Benefits: {benefits[:100]}")
        
        # Combine into response
        if response_parts:
            dynamic_response = ". ".join(response_parts)
            
            # Language-specific formatting for dynamic content
            if language == "hindi" and not any(hindi_char in dynamic_response for hindi_char in ['ा', 'ि', 'ी', 'ु', 'ू', 'े', 'ै', 'ो', 'ौ']):
                dynamic_response = f"आपके लिए यह योजना उपलब्ध है: {dynamic_response}"
            elif language == "hinglish":
                dynamic_response = f"Aapke liye yeh scheme available hai: {dynamic_response}"
            
            return dynamic_response
        else:
            # Final fallback - still language aware
            fallback_msgs = {
                "hindi": "आपके लिए सरकारी योजनाएं उपलब्ध हैं। अधिक जानकारी के लिए संपर्क करें।",
                "english": "Government schemes are available for you. Please contact for more information.",
                "hinglish": "Aapke liye government schemes available hain। More info ke liye contact kariye।"
            }
            return fallback_msgs.get(language, fallback_msgs["english"])
    
    def get_time_based_greeting(self):
        """Get greeting based on time"""
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            return "good morning"
        elif 12 <= hour < 17:
            return "good afternoon"
        else:
            return "good evening"

    def run_conversation(self):
        """Main conversation loop with working TTS"""
        print("🤖 Enhanced Government Schemes Voice Assistant with WORKING gTTS")
        print("=" * 70)
        print("💡 Supports VOICE and TEXT input with CSV-powered scheme search")
        print("🔊 Working gTTS system for COMPLETE audio output")
        print("=" * 70)
        
        is_valid = self._validate_components()
        if not is_valid:
            print("❌ Working RAG system not available")
            print("💡 Please check Groq API key and dependencies")
            return
        
        if self.scheme_db and self.scheme_db.available:
            print(f"📊 Working CSV RAG Database: Ready")
            total_schemes = self.scheme_db.get_scheme_count()
            print(f"📈 Total schemes available: {total_schemes}")
            print("✅ CSV-powered search enabled")
            print("🔊 Complete TTS output enabled")
        
        try:
            # Language Selection
            self.current_language = self.select_language()
            if not self.current_language:
                print("👋 Goodbye!")
                return
            
            logger.info(f"🌐 Language: {self.current_language}")
            self.speak("language_selected")
            
            # Greeting
            greeting = self.get_time_based_greeting()
            self.speak(greeting)
            self.speak("welcome")
            
            # WORKING: Get user name with clear TTS
            name = self.get_user_name()
            if name and name != "exit":
                self.user_name = name
                self.user_context["name"] = self.user_name
                logger.info(f"👤 User: {self.user_name}")
                self.speak("thank_you")
            
            # Get occupation/location
            occupation_prompts = {
                "hindi": "अपना व्यवसाय या स्थान बताएं (जैसे: मैं किसान हूँ, गुजरात से)",
                "english": "Tell me your occupation or location (e.g: I am farmer from Gujarat)",
                "hinglish": "Apna occupation ya location batayiye (jaise: main farmer hun, Gujarat se)"
            }
            
            self.speak("ask_occupation")
            
            context_info = self.listen_hybrid(
                occupation_prompts[self.current_language],
                timeout=10,
                skip_voice=False
            )
            
            if context_info and context_info != "exit":
                occupation, location = self.parse_user_occupation(context_info)
                
                if occupation:
                    self.user_context["occupation"] = occupation.strip()
                    logger.info(f"💼 Occupation: {occupation}")
                
                if location:
                    self.user_context["location"] = location.strip()
                    logger.info(f"📍 Location: {location}")
            
            print(f"\n💬 Chat with {self.user_name} ({self.current_language})")
            print(f"👤 Occupation: {self.user_context.get('occupation', 'Not specified')}")
            print(f"📍 Location: {self.user_context.get('location', 'Not specified')}")
            print("-" * 70)
            
            # Main conversation loop
            conversation_count = 0
            max_conversations = 5
            
            while conversation_count < max_conversations:
                print(f"\n{'='*20} Query {conversation_count + 1}/{max_conversations} {'='*20}")
                
                query_prompts = {
                    "hindi": "सरकारी योजनाओं के बारे में क्या जानना चाहते हैं?",
                    "english": "What would you like to know about government schemes?",
                    "hinglish": "Government schemes ke baare mein kya jaanna chahte hain?"
                }
                
                self.speak("ask_query")
                
                query = self.listen_hybrid(
                    query_prompts[self.current_language],
                    timeout=15,
                    skip_voice=False
                )
                
                if not query or query == "exit" or len(query.strip()) < 2:
                    if query == "exit":
                        break
                    print("⚠️ Please enter a valid question")
                    continue
                
                logger.info(f"🗣️ User Query: '{query}' ({self.current_language})")
                conversation_count += 1
                
                # Enhanced RAG search
                user_occupation = self.user_context.get('occupation', 'None')
                user_location = self.user_context.get('location', 'None')
                print(f"\n🧠 WORKING CSV RAG Search for {user_occupation} from {user_location}...")
                
                relevant_schemes = self.find_relevant_schemes(query.strip(), top_n=5)
                
                if relevant_schemes:
                    print(f"✅ WORKING RAG found {len(relevant_schemes)} schemes:")
                    for i, scheme in enumerate(relevant_schemes, 1):
                        name = scheme.get('Name', 'Unknown')
                        score = scheme.get('Score', 0)
                        print(f"  {i}. {name[:70]}... (Score: {score:.3f})")
                else:
                    print("❌ No schemes found")
                
                # WORKING: Generate and speak COMPLETE response
                response = self.format_scheme_response(relevant_schemes, query, self.current_language)
                
                print(f"\n📋 CSV RAG Response ({self.current_language}):")
                print(f"🤖 {response}")
                
                # WORKING: Speak the COMPLETE response using gTTS chunking
                self.speak(response, self.current_language)
                
                if conversation_count >= max_conversations:
                    break
                
                # Ask for more questions
                more_prompts = {
                    "hindi": "और कोई सवाल है? (हाँ/नहीं)",
                    "english": "Any more questions? (yes/no)",
                    "hinglish": "Aur koi question hai? (haan/nahi)"
                }
                
                self.speak("anything_else")
                
                more_questions = self.listen_hybrid(
                    more_prompts[self.current_language],
                    timeout=5,
                    skip_voice=False
                )
                
                if more_questions and any(word in more_questions.lower() for word in 
                                        ["no", "nahi", "nahin", "exit", "quit", "bye", "bas", "khatam", "n"]):
                    # Check if it's actually a new query
                    if len(more_questions.split()) > 2:
                        logger.info("🔄 Processing additional query")
                        query = more_questions
                        conversation_count += 1
                        
                        logger.info(f"🗣️ Additional Query: '{query}' ({self.current_language})")
                        
                        print(f"\n🧠 WORKING CSV RAG Search for additional query...")
                        relevant_schemes = self.find_relevant_schemes(query.strip(), top_n=5)
                        
                        if relevant_schemes:
                            print(f"✅ WORKING RAG found {len(relevant_schemes)} schemes:")
                            for i, scheme in enumerate(relevant_schemes, 1):
                                name = scheme.get('Name', 'Unknown')
                                score = scheme.get('Score', 0)
                                print(f"  {i}. {name[:70]}... (Score: {score:.3f})")
                        else:
                            print("❌ No schemes found")
                        
                        response = self.format_scheme_response(relevant_schemes, query, self.current_language)
                        print(f"\n📋 CSV RAG Response ({self.current_language}):")
                        print(f"🤖 {response}")
                        
                        # WORKING: Speak complete additional response
                        self.speak(response, self.current_language)
                        continue
                    else:
                        logger.info("👋 User wants to exit")
                        break
            
            # Closing
            print("\n🏁 Session ending...")
            self.speak("closing")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user")
        except Exception as e:
            logger.error(f"Error in conversation: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n🤖 Enhanced RAG Voice Assistant session completed!")
        print("Thank you for using the WORKING gTTS Government Schemes Assistant!")

if __name__ == "__main__":
    assistant = EnhancedVoiceAssistant()
    assistant.run_conversation()