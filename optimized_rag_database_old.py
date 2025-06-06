# optimized_rag_database.py - Fast RAG for Voice Assistant
import os
import json
import sqlite3
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import hashlib

# Optional imports with fallbacks
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

try:
    import requests
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedRAGDatabase:
    """Fast RAG system optimized for voice assistant"""
    
    def __init__(self, csv_path: str, groq_api_key: str = ""):
        self.csv_path = csv_path
        self.groq_api_key = groq_api_key
        self.db_path = "schemes_rag.db"
        
        # Initialize components
        self.embedding_model = None
        self.llm_available = False
        self.available = False
        
        try:
            self._initialize_database()
            self._load_embedding_model()
            self._setup_groq()
            self.available = True
            logger.info("✅ Optimized RAG Database initialized")
        except Exception as e:
            logger.error(f"❌ RAG initialization failed: {e}")
            self.available = False
    
    def _initialize_database(self):
        """Initialize SQLite database with vector support"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create schemes table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS schemes (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            details TEXT,
            benefits TEXT,
            eligibility TEXT,
            documents TEXT,
            application_process TEXT,
            gender TEXT,
            min_age INTEGER,
            max_age INTEGER,
            caste TEXT,
            minority TEXT,
            url TEXT,
            embedding_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create embeddings table (simplified)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheme_embeddings (
            scheme_id INTEGER,
            embedding_vector TEXT,
            chunk_text TEXT,
            chunk_id INTEGER,
            FOREIGN KEY (scheme_id) REFERENCES schemes (id)
        )
        """)
        
        conn.commit()
        conn.close()
        
        # Check if we need to populate database
        if self._needs_data_loading():
            self._load_csv_data()
    
    def _needs_data_loading(self) -> bool:
        """Check if database needs data loading"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM schemes")
        count = cursor.fetchone()[0]
        conn.close()
        return count == 0
    
    def _load_csv_data(self):
        """Load CSV data into database"""
        if not os.path.exists(self.csv_path):
            logger.error(f"CSV file not found: {self.csv_path}")
            return
        
        logger.info("📊 Loading CSV data...")
        df = pd.read_csv(self.csv_path)
        
        conn = sqlite3.connect(self.db_path)
        
        for idx, row in df.iterrows():
            # Create searchable text
            embedding_text = f"""
            {row.get('Name', '')} {row.get('Department', '')} 
            {row.get('Details', '')} {row.get('Benefits', '')} 
            {row.get('Eligibility', '')} {row.get('Caste', '')} 
            {row.get('Gender', '')} {row.get('Minority', '')}
            """.strip()
            
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO schemes (
                name, department, details, benefits, eligibility, 
                documents, application_process, gender, min_age, max_age, 
                caste, minority, url, embedding_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get('Name', ''),
                row.get('Department', ''),
                row.get('Details', ''),
                row.get('Benefits', ''),
                row.get('Eligibility', ''),
                row.get('Document_Required', ''),
                row.get('Application_Process', ''),
                row.get('Gender', ''),
                row.get('Min Age', 0),
                row.get('Max Age', 100),
                row.get('Caste', ''),
                row.get('Minority', ''),
                row.get('URL', ''),
                embedding_text
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Loaded {len(df)} schemes into database")
    
    def _load_embedding_model(self):
        """Load lightweight embedding model"""
        if not EMBEDDING_AVAILABLE:
            logger.warning("⚠️ sentence-transformers not available")
            return
        
        try:
            # Use smaller, faster model
            model_name = "all-MiniLM-L6-v2"
            logger.info(f"📥 Loading embedding model: {model_name}")
            
            self.embedding_model = SentenceTransformer(model_name)
            logger.info("✅ Embedding model loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def _setup_groq(self):
        """Setup Groq LLM"""
        if not GROQ_AVAILABLE or not self.groq_api_key:
            logger.warning("⚠️ Groq API not available")
            return
        
        try:
            # Test Groq connection
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            test_data = {
                "messages": [{"role": "user", "content": "test"}],
                "model": "deepseek-r1-distill-llama-70b",
                "max_tokens": 10
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=test_data,
                timeout=5
            )
            
            if response.status_code == 200:
                self.llm_available = True
                logger.info("✅ Groq LLM available")
            else:
                logger.warning("⚠️ Groq API test failed")
        except Exception as e:
            logger.warning(f"⚠️ Groq setup failed: {e}")
    
    def search_by_context(self, query: str, occupation: str = None, 
                         location: str = None, top_k: int = 5) -> List[Dict]:
        """Search schemes with context"""
        if not self.available:
            return []
        
        try:
            # Build enhanced query
            search_terms = [query.lower()]
            
            if occupation:
                search_terms.append(occupation.lower())
            
            if location:
                search_terms.append(location.lower())
            
            # Use fast text-based search first
            results = self._fast_text_search(search_terms, top_k * 2)
            
            # Re-rank if embedding model available
            if self.embedding_model and results:
                results = self._rerank_with_embeddings(query, results, top_k)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _fast_text_search(self, search_terms: List[str], limit: int) -> List[Dict]:
        """Fast text-based search using SQL"""
        conn = sqlite3.connect(self.db_path)
        
        # Build SQL query with multiple LIKE conditions
        conditions = []
        params = []
        
        for term in search_terms:
            conditions.append("""
            (LOWER(embedding_text) LIKE ? OR 
             LOWER(name) LIKE ? OR 
             LOWER(department) LIKE ?)
            """)
            params.extend([f"%{term}%", f"%{term}%", f"%{term}%"])
        
        sql = f"""
        SELECT DISTINCT 
            id, name, department, details, benefits, eligibility,
            documents, application_process, gender, min_age, max_age,
            caste, minority, url, embedding_text
        FROM schemes 
        WHERE {' OR '.join(conditions)}
        ORDER BY 
            CASE 
                WHEN LOWER(name) LIKE ? THEN 1
                WHEN LOWER(department) LIKE ? THEN 2
                ELSE 3
            END
        LIMIT ?
        """
        
        # Add primary search term for ordering
        primary_term = search_terms[0] if search_terms else ""
        params.extend([f"%{primary_term}%", f"%{primary_term}%", limit])
        
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'Name': row[1],
                'Department': row[2],
                'Details': row[3],
                'Benefits': row[4],
                'Eligibility': row[5],
                'Document_Required': row[6],
                'Application_Process': row[7],
                'Gender': row[8],
                'Min_Age': row[9],
                'Max_Age': row[10],
                'Caste': row[11],
                'Minority': row[12],
                'URL': row[13],
                'Score': 0.8  # Default score for text search
            })
        
        return results
    
    def _rerank_with_embeddings(self, query: str, results: List[Dict], 
                               top_k: int) -> List[Dict]:
        """Re-rank results using embeddings"""
        if not self.embedding_model or not results:
            return results
        
        try:
            # Get query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Calculate similarities
            scored_results = []
            
            for result in results:
                # Create text for similarity
                result_text = f"{result['Name']} {result['Details']} {result['Benefits']}"
                result_embedding = self.embedding_model.encode([result_text])[0]
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, result_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(result_embedding)
                )
                
                result['Score'] = float(similarity)
                scored_results.append(result)
            
            # Sort by similarity score
            scored_results.sort(key=lambda x: x['Score'], reverse=True)
            return scored_results[:top_k]
            
        except Exception as e:
            logger.error(f"Re-ranking error: {e}")
            return results[:top_k]
    
    def generate_voice_response(self, schemes: List[Dict], query: str, 
                              language: str = "english") -> str:
        """Generate voice-optimized response"""
        if not schemes:
            return self._get_no_results_message(language)
        
        # Use Groq if available
        if self.llm_available:
            try:
                return self._generate_groq_response(schemes, query, language)
            except Exception as e:
                logger.error(f"Groq generation failed: {e}")
        
        # Fallback to template response
        return self._generate_template_response(schemes, language)
    
    def _generate_groq_response(self, schemes: List[Dict], query: str, 
                               language: str) -> str:
        """Generate response using Groq"""
        # Prepare schemes summary for Groq
        schemes_text = ""
        for i, scheme in enumerate(schemes[:3], 1):  # Limit to top 3
            schemes_text += f"""
Scheme {i}: {scheme['Name']}
Department: {scheme['Department']}
Benefits: {scheme['Benefits'][:200]}...
Eligibility: {scheme['Eligibility'][:150]}...
"""
        
        # Create prompt based on language
        if language == "hindi":
            prompt = f"""
उपलब्ध योजनाओं के आधार पर हिंदी में एक संक्षिप्त उत्तर दें (150 शब्दों तक):

उपलब्ध योजनाएं:
{schemes_text}

प्रश्न: {query}

केवल मुख्य योजनाओं के नाम और लाभ बताएं। संक्षिप्त रखें।
"""
        elif language == "hinglish":
            prompt = f"""
Available schemes ke basis pe Hinglish mein short answer dije (150 words tak):

Available schemes:
{schemes_text}

Question: {query}

Sirf main schemes ke naam aur benefits batayiye। Short rakhiye।
"""
        else:  # English
            prompt = f"""
Based on available schemes, provide a brief answer in English (max 150 words):

Available schemes:
{schemes_text}

Question: {query}

Only mention main scheme names and benefits. Keep it concise for voice output.
"""
        
        # Call Groq API
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "model": "deepseek-r1-distill-llama-70b",
            "max_tokens": 200,
            "temperature": 0.1
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            raise Exception(f"Groq API error: {response.status_code}")
    
    def _generate_template_response(self, schemes: List[Dict], 
                                  language: str) -> str:
        """Generate template-based response"""
        scheme = schemes[0]
        name = scheme['Name']
        
        if len(name) > 60:
            name = " ".join(name.split()[:8])
        
        if language == "hindi":
            return f"{name}। यह योजना आपके लिए उपयुक्त है।"
        elif language == "hinglish":
            return f"{name}। Yeh scheme aapke liye suitable hai।"
        else:
            return f"{name}। This scheme is suitable for you।"
    
    def _get_no_results_message(self, language: str) -> str:
        """Get no results message"""
        messages = {
            "hindi": "कोई उपयुक्त योजना नहीं मिली। कृपया अधिक विवरण दें।",
            "hinglish": "Koi suitable scheme nahi mili। Please aur details dijiye।",
            "english": "No suitable schemes found। Please provide more details।"
        }
        return messages.get(language, messages["english"])
    
    def get_scheme_count(self) -> int:
        """Get total scheme count"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM schemes")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    def test_system(self):
        """Test the RAG system"""
        test_queries = [
            "farmer schemes",
            "agriculture loans", 
            "women schemes",
            "education scholarship"
        ]
        
        logger.info("🧪 Testing RAG system...")
        for query in test_queries:
            results = self.search_by_context(query, top_k=2)
            logger.info(f"Query '{query}': Found {len(results)} results")
        
        return True

# Backward compatibility
EnhancedRAGDatabase = OptimizedRAGDatabase