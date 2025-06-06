# scheme_matcher.py - Enhanced with RAG capabilities
import os
import json
import time
from database_backup import EnhancedRAGDatabase
from config import CONFIG

class EnhancedSchemeMatcherModule:
    """Enhanced scheme matcher with RAG capabilities"""
    
    def __init__(self, csv_path, db_path, cache_dir):
        self.csv_path = csv_path
        self.db_path = db_path
        self.cache_dir = cache_dir
        
        # Initialize cache
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, "rag_queries.json")
        self.cache = self._load_cache()
        
        # Get Groq API key
        self.groq_api_key = self._get_groq_api_key()
        
        # Initialize RAG database
        try:
            self.rag_db = EnhancedRAGDatabase(csv_path, self.groq_api_key)
            self.available = self.rag_db.available
            print("✅ Enhanced RAG scheme matcher initialized")
        except Exception as e:
            print(f"❌ RAG initialization failed: {e}")
            self.rag_db = None
            self.available = False
        
        self.user_context = {}
    
    def _get_groq_api_key(self):
        """Get Groq API key from config"""
        try:
            # Try multiple config formats
            if hasattr(CONFIG, 'get'):
                return CONFIG.get("GROQ_API_KEY", "")
            elif isinstance(CONFIG, dict):
                return CONFIG.get("GROQ_API_KEY", "")
            else:
                return getattr(CONFIG, "GROQ_API_KEY", "")
        except:
            return ""
    
    def _load_cache(self):
        """Load query cache"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save query cache"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def set_user_context(self, name, occupation=None, location=None):
        """Set user context for personalized responses"""
        self.user_context = {
            "name": name,
            "occupation": occupation,
            "location": location
        }
        print(f"👤 User context: {name}, {occupation}, {location}")
    
    def find_relevant_schemes(self, query, top_n=3):
        """Find relevant schemes using RAG"""
        if not self.available or not self.rag_db:
            print("⚠️ RAG database not available")
            return []
        
        try:
            # Check cache first
            cache_key = f"{query.lower().strip()}_{top_n}"
            if cache_key in self.cache:
                print("📦 Using cached results")
                return self.cache[cache_key][:top_n]
            
            # Get user context
            occupation = self.user_context.get("occupation")
            location = self.user_context.get("location")
            
            print(f"🔍 RAG Search: '{query}' | Context: {occupation}, {location}")
            
            # Use RAG search
            results = self.rag_db.search_by_context(query, occupation, location, top_n * 2)
            
            # Format results for voice assistant compatibility
            formatted_results = []
            for result in results:
                formatted_result = {
                    'Name': result['Name'],
                    'Details': result['Details'],
                    'Eligibility': result['Eligibility'],
                    'Benefits': result['Benefits'],
                    'Category': result.get('Department', result.get('Category', '')),
                    'Location': result.get('Location', location or 'India'),
                    'similarity_score': result.get('Score', 0.8),
                    'Department': result.get('Department', ''),
                    'Document_Required': result.get('Document_Required', ''),
                    'Application_Process': result.get('Application_Process', ''),
                    'Gender': result.get('Gender', ''),
                    'Min_Age': result.get('Min_Age', 0),
                    'Max_Age': result.get('Max_Age', 100),
                    'Caste': result.get('Caste', ''),
                    'Minority': result.get('Minority', ''),
                    'URL': result.get('URL', '')
                }
                formatted_results.append(formatted_result)
            
            # Cache results
            self.cache[cache_key] = formatted_results
            if len(self.cache) > 100:  # Limit cache size
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            self._save_cache()
            
            print(f"✅ Found {len(formatted_results)} relevant schemes")
            return formatted_results[:top_n]
            
        except Exception as e:
            print(f"❌ RAG search failed: {e}")
            return []
    
    def generate_response(self, schemes, user_query, language="english"):
        """Generate intelligent response using RAG"""
        if not schemes:
            fallback_responses = {
                "english": "No relevant schemes found. Please provide more details about your occupation or needs.",
                "hindi": "कोई संबंधित योजना नहीं मिली। कृपया अपने व्यवसाय या आवश्यकताओं के बारे में अधिक जानकारी दें।",
                "hinglish": "Koi relevant scheme nahi mili. Please apne occupation ya requirements ke baare mein aur details dijiye."
            }
            return fallback_responses.get(language, fallback_responses["english"])
        
        try:
            if self.available and self.rag_db and self.rag_db.llm_available:
                # Use RAG for intelligent response generation
                response = self.rag_db.generate_voice_response(schemes, user_query, language)
                
                # Ensure response is suitable for voice
                if len(response) > 150:
                    sentences = response.split('.')
                    response = sentences[0] + '.'
                
                return response
            else:
                # Fallback to simple response
                return self._generate_simple_response(schemes, language)
                
        except Exception as e:
            print(f"❌ Response generation failed: {e}")
            return self._generate_simple_response(schemes, language)
    
    def _generate_simple_response(self, schemes, language):
        """Generate simple fallback response"""
        if not schemes:
            return "No schemes found."
        
        scheme = schemes[0]
        name = scheme.get('Name', 'Government Scheme')
        benefits = scheme.get('Benefits', '')
        
        # Shorten name for voice
        if len(name) > 60:
            name_words = name.split()
            name = " ".join(name_words[:8])
        
        # Create voice-friendly response
        if language == "hindi":
            if benefits:
                return f"{name}। लाभ: {benefits[:60]}।"
            else:
                return f"{name}। यह योजना आपके लिए उपयुक्त है।"
        elif language == "hinglish":
            if benefits:
                return f"{name}। Benefits: {benefits[:60]}।"
            else:
                return f"{name}। Yeh scheme aapke liye suitable hai।"
        else:  # english
            if benefits:
                return f"{name}। Benefits: {benefits[:60]}।"
            else:
                return f"{name}। This scheme is suitable for you।"
    
    def get_statistics(self):
        """Get system statistics"""
        stats = {
            "rag_available": self.available,
            "cache_size": len(self.cache),
            "groq_available": self.rag_db.llm_available if self.rag_db else False,
            "total_schemes": self.rag_db.get_scheme_count() if self.rag_db else 0,
            "database_type": "Enhanced RAG + Vector Database"
        }
        
        return stats
    
    def test_system(self):
        """Test the RAG system"""
        test_queries = [
            "farmer scheme",
            "women schemes",
            "agriculture loans",
            "fishing boat subsidy"
        ]
        
        print("🧪 Testing RAG system...")
        for query in test_queries:
            print(f"\n🔍 Testing: {query}")
            results = self.find_relevant_schemes(query, 2)
            if results:
                print(f"✅ Found {len(results)} results")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['Name'][:50]}...")
            else:
                print("❌ No results found")
        
        return len(test_queries) > 0

# Backward compatibility - keep the old class name
OllamaSchemeMatcherModule = EnhancedSchemeMatcherModule