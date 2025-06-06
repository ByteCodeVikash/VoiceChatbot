# enhanced_rag_database.py - FIXED VERSION
import os
import json
import logging
import pandas as pd
import sqlite3
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime

# RAG imports
try:
    from langchain_chroma import Chroma
    from langchain_groq import ChatGroq
    from langchain.chains import RetrievalQA
    from langchain.schema import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain.prompts import PromptTemplate
    import warnings
    warnings.filterwarnings("ignore")
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Global variables
working_dir = os.path.dirname(os.path.abspath(__file__))

# Load config
try:
    with open(os.path.join(working_dir, "config.json")) as config_file:
        config_data = json.load(config_file)
        GROQ_API_KEY = config_data.get("GROQ_API_KEY", "")
except Exception as e:
    print(f"Config error: {e}")
    GROQ_API_KEY = ""

if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Initialize models
if RAG_AVAILABLE and GROQ_API_KEY:
    try:
        embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

        llm = ChatGroq(
            model="deepseek-r1-distill-llama-70b",
            temperature=0.1
        )
    except Exception as e:
        print(f"Model initialization error: {e}")
        embedding = None
        llm = None
else:
    embedding = None
    llm = None

def process_csv_to_documents(csv_file_path):
    """Convert CSV to documents"""
    try:
        df = pd.read_csv(csv_file_path)
        print(f"✅ Loaded CSV: {df.shape[0]} rows, {df.shape[1]} columns")
        
        documents = []
        
        for idx, row in df.iterrows():
            scheme_text = f"""
SCHEME INFORMATION:
Department: {row.get('Department', 'N/A')}
Scheme Name: {row.get('Name', 'N/A')}

DETAILS:
{row.get('Details', 'N/A')}

BENEFITS:
{row.get('Benefits', 'N/A')}

ELIGIBILITY CRITERIA:
{row.get('Eligibility', 'N/A')}

APPLICATION PROCESS:
{row.get('Application_Process', 'N/A')}

REQUIRED DOCUMENTS:
{row.get('Document_Required', 'N/A')}

TARGET DEMOGRAPHICS:
Gender: {row.get('Gender', 'N/A')}
Age Range: {row.get('Min Age', 'N/A')} to {row.get('Max Age', 'N/A')} years
Caste: {row.get('Caste', 'N/A')}
Minority: {row.get('Minority', 'N/A')}

OFFICIAL LINK:
{row.get('URL', 'N/A')}
            """
            
            doc = Document(
                page_content=scheme_text.strip(),
                metadata={
                    "scheme_id": idx,
                    "department": str(row.get('Department', '')).lower(),
                    "scheme_name": str(row.get('Name', '')),
                    "gender": str(row.get('Gender', '')).lower(),
                    "caste": str(row.get('Caste', '')).lower(),
                    "source": "government_schemes_csv"
                }
            )
            documents.append(doc)
        
        print(f"✅ Created {len(documents)} scheme documents")
        return documents
        
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        return []

def create_vectorstore(documents):
    """Create vectorstore"""
    try:
        if not embedding:
            return None
            
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
        splits = text_splitter.split_documents(documents)
        print(f"✅ Created {len(splits)} text chunks")
        
        vectorstore_path = os.path.join(working_dir, "schemes_vectorstore")
        
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embedding,
            persist_directory=vectorstore_path
        )
        
        print(f"✅ Vectorstore created")
        return vectorstore
        
    except Exception as e:
        print(f"❌ Error creating vectorstore: {e}")
        return None

def setup_qa_chain():
    """Setup QA chain"""
    
    prompt_template = """
You are a helpful assistant for Indian Government Schemes. Answer questions clearly and concisely in 2-3 sentences maximum. Do not use any special formatting, thinking tags, or markdown.

Context: {context}

Question: {question}

Instructions:
1. Give direct, clear answers suitable for voice output
2. Mention specific scheme names if relevant
3. Keep responses under 100 words
4. Do not use <think> tags or any special formatting
5. Be factual and helpful

Answer:
"""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    vectorstore_path = os.path.join(working_dir, "schemes_vectorstore")
    
    if not os.path.exists(vectorstore_path) or not embedding:
        return None, "❌ Vectorstore or embedding not found"
    
    try:
        vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=embedding
        )
        
        # Fixed retriever
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        return qa_chain, "✅ QA Chain ready"
        
    except Exception as e:
        return None, f"❌ Error: {e}"

def process_government_schemes_csv(csv_file_path):
    """Main function to process CSV"""
    print("🚀 Processing Government Schemes CSV...")
    
    documents = process_csv_to_documents(csv_file_path)
    if not documents:
        return False, "Failed to process CSV"
    
    vectorstore = create_vectorstore(documents)
    if not vectorstore:
        return False, "Failed to create vectorstore"
    
    print("✅ Ready for questions!")
    return True, "Success"

def answer_schemes_question(question):
    """Answer questions about government schemes"""
    try:
        qa_chain, status = setup_qa_chain()
        
        if not qa_chain:
            return status
        
        result = qa_chain.invoke({"query": question})
        answer = result["result"]
        
        # AGGRESSIVE cleaning for voice output
        import re
        
        # Remove <think> tags and ALL their content (most important fix)
        answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove any remaining thinking patterns
        answer = re.sub(r'think.*?(?=\n\n|\.|$)', '', answer, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove special formatting
        answer = re.sub(r'[<>{}*#`_]', '', answer)
        answer = re.sub(r'\*+', '', answer)
        answer = re.sub(r'#+', '', answer)
        
        # Clean up multiple whitespace and newlines
        answer = re.sub(r'\s+', ' ', answer)
        answer = answer.strip()
        
        # If answer is still empty or too short, return error
        if not answer or len(answer) < 10:
            return "Unable to find specific scheme information. Please try a different query."
        
        # Limit length for voice output
        if len(answer) > 250:
            sentences = answer.split('.')
            # Take first 2-3 meaningful sentences
            good_sentences = []
            for sentence in sentences:
                clean_sentence = sentence.strip()
                if clean_sentence and len(clean_sentence) > 10:
                    good_sentences.append(clean_sentence)
                if len(good_sentences) >= 2:
                    break
            
            if good_sentences:
                answer = '. '.join(good_sentences) + '.'
            else:
                answer = sentences[0] + '.' if sentences else answer
        
        return answer.strip()
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

class EnhancedRAGDatabase:
    """Wrapper class for voice assistant compatibility"""
    
    def __init__(self, csv_path: str, groq_api_key: str):
        self.csv_path = csv_path
        self.groq_api_key = groq_api_key
        self.available = RAG_AVAILABLE and groq_api_key and embedding and llm
        
        # Setup environment
        if self.available:
            os.environ["GROQ_API_KEY"] = groq_api_key
            
            # Create config.json if not exists
            config_path = os.path.join(working_dir, "config.json")
            if not os.path.exists(config_path):
                config_data = {"GROQ_API_KEY": groq_api_key}
                with open(config_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                    
            logger.info("✅ Enhanced RAG Database initialized")
    
    def search_by_context(self, query: str, occupation: str = None, 
                         location: str = None, top_k: int = 5) -> List[Dict]:
        """Search using enhanced approach"""
        
        if not self.available:
            logger.warning("⚠️ RAG system not available")
            return []
        
        try:
            # Build enhanced query
            enhanced_query_parts = [query]
            
            if occupation:
                occupation_keywords = {
                    'farmer': 'agriculture farming kisan crop cultivation seeds fertilizers',
                    'fisherman': 'fishing marine boat matsya',
                    'women': 'women female mahila woman',
                    'business': 'business entrepreneur loan mudra',
                    'student': 'education scholarship student vidyarthi'
                }
                if occupation in occupation_keywords:
                    enhanced_query_parts.append(occupation_keywords[occupation])
            
            if location:
                enhanced_query_parts.append(location)
            
            enhanced_query = ' '.join(enhanced_query_parts)
            
            logger.info(f"🔍 Enhanced query: '{enhanced_query}'")
            
            # Use the answer function
            answer = answer_schemes_question(enhanced_query)
            
            logger.info(f"✅ RAG found answer")
            
            # Parse answer into scheme format for voice assistant
            schemes = self._parse_answer_to_schemes(answer, enhanced_query, top_k)
            
            return schemes[:top_k]
            
        except Exception as e:
            logger.error(f"❌ RAG search failed: {e}")
            return []
    
    def _parse_answer_to_schemes(self, answer: str, query: str, top_k: int = 5) -> List[Dict]:
        """Parse answer into scheme format for voice assistant - FIXED"""
        schemes = []
        
        try:
            # Simple scheme creation from answer
            scheme_info = {
                'Name': 'Government Scheme Information',
                'Details': answer[:200] if answer else 'Scheme information available',
                'Benefits': self._extract_section(answer, ['benefit', 'लाभ', 'advantage']),
                'Eligibility': self._extract_section(answer, ['eligibility', 'eligible', 'पात्र']),
                'Document_Required': self._extract_section(answer, ['document', 'paper', 'दस्तावेज']),
                'Application_Process': self._extract_section(answer, ['application', 'apply', 'आवेदन']),
                'Department': self._extract_section(answer, ['department', 'ministry', 'विभाग']),
                'Gender': 'All',
                'Score': 0.7
            }
            schemes.append(scheme_info)
            
            logger.info(f"📋 Parsed 1 scheme from answer")
            return schemes
            
        except Exception as e:
            logger.error(f"❌ Answer parsing failed: {e}")
            return [{
                'Name': 'Government Scheme Information',
                'Details': answer[:150] if answer else 'Scheme information available',
                'Benefits': 'Check scheme details',
                'Eligibility': 'As per guidelines', 
                'Document_Required': 'Standard documents required',
                'Application_Process': 'Apply through official channels',
                'Department': 'Government Department',
                'Gender': 'All',
                'Score': 0.7
            }]
    
    def _extract_section(self, text: str, keywords: List[str]) -> str:
        """Extract specific section from text"""
        if not text:
            return "Information available in scheme details"
            
        sentences = text.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                extracted = sentence.strip()
                return extracted[:100] if len(extracted) > 100 else extracted
        
        return "Information available in scheme details"
    
    def search_schemes(self, query: str, limit: int = 5) -> List[Dict]:
        """Backward compatibility method"""
        return self.search_by_context(query, top_k=limit)
    
    def get_scheme_count(self) -> int:
        """Get total number of schemes"""
        try:
            if os.path.exists(self.csv_path):
                df = pd.read_csv(self.csv_path)
                return len(df)
            return 0
        except:
            return 0
    
    def close(self):
        """Close connections"""
        pass

# Factory function for compatibility
def SchemeDatabase(db_path, csv_path):
    """Factory function for backward compatibility"""
    from config import CONFIG
    groq_api_key = CONFIG.get("GROQ_API_KEY", "")
    
    if not groq_api_key:
        logger.warning("⚠️ No Groq API key found in config")
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            if os.path.exists(config_path):
                with open(config_path) as f:
                    config_data = json.load(f)
                    groq_api_key = config_data.get("GROQ_API_KEY", "")
        except:
            pass
    
    return EnhancedRAGDatabase(csv_path, groq_api_key)

# For testing
if __name__ == "__main__":
    csv_path = "Government_schemes_final_english.csv"
    if os.path.exists(csv_path):
        success, message = process_government_schemes_csv(csv_path)
        if success:
            test_answer = answer_schemes_question("What schemes are available for women?")
            print(f"Test answer: {test_answer}")