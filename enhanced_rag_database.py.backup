# enhanced_rag_database.py - Direct Fixed Integration
import os
import json
import logging
import pandas as pd
import sqlite3
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime

# RAG imports - EXACT same as fixed_perfect_rag.py
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

logging.basicConfig(level=logging.WARNING)  # Same as fixed_perfect_rag.py
logger = logging.getLogger(__name__)

# DIRECT COPY from fixed_perfect_rag.py - Global variables
working_dir = os.path.dirname(os.path.abspath(__file__))

# Load config
try:
    with open(os.path.join(working_dir, "config.json")) as config_file:
        config_data = json.load(config_file)
        GROQ_API_KEY = config_data.get("GROQ_API_KEY", "")
except Exception as e:
    print(f"Config error: {e}")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Initialize models - EXACT same as fixed_perfect_rag.py
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0.1
)

# DIRECT COPY - All functions from fixed_perfect_rag.py
def process_csv_to_documents(csv_file_path):
    """Convert CSV to documents - EXACT COPY from fixed_perfect_rag.py"""
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
    """Create vectorstore - EXACT COPY from fixed_perfect_rag.py"""
    try:
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
    """Setup QA chain - EXACT COPY from fixed_perfect_rag.py"""
    
    prompt_template = """
You are an expert assistant for Indian Government Schemes. Use the provided context to answer questions accurately.

Context from Government Schemes Database:
{context}

Question: {question}

Instructions:
1. List ALL relevant schemes from the context if multiple schemes match
2. Include specific details: scheme name, department, benefits, eligibility, documents
3. Be factual and comprehensive
4. Format clearly with bullet points for multiple schemes

Answer:
"""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    vectorstore_path = os.path.join(working_dir, "schemes_vectorstore")
    
    if not os.path.exists(vectorstore_path):
        return None, "❌ Vectorstore not found"
    
    try:
        vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=embedding
        )
        
        # Fixed retriever without deprecated parameters
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 6}  # Removed score_threshold
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
    """Main function to process CSV - EXACT COPY from fixed_perfect_rag.py"""
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
    """Answer questions - EXACT COPY from fixed_perfect_rag.py"""
    try:
        qa_chain, status = setup_qa_chain()
        
        if not qa_chain:
            return status
        
        result = qa_chain.invoke({"query": question})
        answer = result["result"]
        
        # Add source info
        source_docs = result.get("source_documents", [])
        if source_docs:
            answer += f"\n\n📚 Information from {len(source_docs)} relevant scheme(s)."
        
        return answer
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

class EnhancedRAGDatabase:
    """Wrapper class for voice assistant compatibility"""
    
    def __init__(self, csv_path: str, groq_api_key: str):
        self.csv_path = csv_path
        self.groq_api_key = groq_api_key
        self.available = RAG_AVAILABLE and groq_api_key
        
        # Setup environment
        if self.available:
            os.environ["GROQ_API_KEY"] = groq_api_key
            
            # Create config.json if not exists
            config_path = os.path.join(working_dir, "config.json")
            if not os.path.exists(config_path):
                config_data = {"GROQ_API_KEY": groq_api_key}
                with open(config_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                    
            logger.info("✅ Enhanced RAG Database initialized (using fixed_perfect_rag approach)")
    
    def search_by_context(self, query: str, occupation: str = None, 
                         location: str = None, top_k: int = 5) -> List[Dict]:
        """Search using fixed_perfect_rag approach"""
        
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
            
            # Use the fixed answer_schemes_question function directly
            answer = answer_schemes_question(enhanced_query)
            
            logger.info(f"✅ RAG found answer")
            
            # Parse answer into scheme format for voice assistant
            schemes = self._parse_answer_to_schemes(answer, enhanced_query)
            
            return schemes[:top_k]
            
        except Exception as e:
            logger.error(f"❌ RAG search failed: {e}")
            return []
    
    def _parse_answer_to_schemes(self, answer: str, query: str) -> List[Dict]:
        """Parse answer into scheme format for voice assistant"""
        schemes = []
        
        try:
            # Extract scheme information from the comprehensive answer
            lines = answer.split('\n')
            current_scheme = {}
            scheme_names = []
            
            # Look for scheme names in the answer
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for scheme patterns
                if any(keyword in line.lower() for keyword in ['scheme', 'yojana', 'mission', 'program', 'programme']):
                    # Clean the line to extract scheme name
                    cleaned_line = line.replace('*', '').replace('#', '').replace('-', '').replace('•', '').strip()
                    
                    # If it looks like a valid scheme name
                    if len(cleaned_line) > 10 and len(cleaned_line) < 200:
                        scheme_names.append(cleaned_line)
            
            # Create scheme objects from extracted names
            for i, scheme_name in enumerate(scheme_names[:top_k]):
                scheme_info = {
                    'Name': scheme_name,
                    'Details': f"Details from CSV database: {answer[:200]}...",
                    'Benefits': self._extract_section(answer, ['benefit', 'लाभ', 'advantage']),
                    'Eligibility': self._extract_section(answer, ['eligibility', 'eligible', 'पात्र']),
                    'Document_Required': self._extract_section(answer, ['document', 'paper', 'दस्तावेज']),
                    'Application_Process': self._extract_section(answer, ['application', 'apply', 'आवेदन']),
                    'Department': self._extract_section(answer, ['department', 'ministry', 'विभाग']),
                    'Gender': 'All',
                    'Score': 0.9 - (i * 0.1)
                }
                schemes.append(scheme_info)
            
            # If no schemes extracted, create a generic one with the answer
            if not schemes:
                schemes = [{
                    'Name': f"Government Scheme Information",
                    'Details': answer[:300],
                    'Benefits': self._extract_section(answer, ['benefit', 'लाभ']),
                    'Eligibility': self._extract_section(answer, ['eligibility', 'पात्र']),
                    'Document_Required': 'Check scheme guidelines',
                    'Application_Process': 'Apply through official channels',
                    'Department': 'Government Department',
                    'Gender': 'All',
                    'Score': 0.8
                }]
            
            logger.info(f"📋 Parsed {len(schemes)} schemes from answer")
            return schemes
            
        except Exception as e:
            logger.error(f"❌ Answer parsing failed: {e}")
            return [{
                'Name': 'Government Scheme Information',
                'Details': answer[:300] if answer else 'Scheme information available',
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
        sentences = text.split('.')
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                extracted = sentence.strip()
                return extracted[:200] if len(extracted) > 200 else extracted
        
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
    
    def test_search(self, test_query: str = "seeds fertilizers krushi mahotsav gujarat"):
        """Test the search functionality"""
        logger.info(f"🧪 Testing search with: '{test_query}'")
        
        if not self.available:
            logger.error("❌ RAG system not available")
            return
        
        results = self.search_by_context(test_query, occupation="farmer", location="gujarat")
        
        if results:
            logger.info(f"✅ Test successful! Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                name = result.get('Name', 'Unknown')
                logger.info(f"  {i}. {name[:80]}...")
        else:
            logger.warning("❌ Test failed - no results found")
    
    def close(self):
        """Close connections"""
        pass

# Factory function for compatibility with existing code
def SchemeDatabase(db_path, csv_path):
    """Factory function for backward compatibility"""
    from config import CONFIG
    groq_api_key = CONFIG.get("GROQ_API_KEY", "")
    
    if not groq_api_key:
        logger.warning("⚠️ No Groq API key found in config")
        # Try to load from config.json
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            if os.path.exists(config_path):
                with open(config_path) as f:
                    config_data = json.load(f)
                    groq_api_key = config_data.get("GROQ_API_KEY", "")
        except:
            pass
    
    return EnhancedRAGDatabase(csv_path, groq_api_key)

# For testing - DIRECT COPY from fixed_perfect_rag.py
if __name__ == "__main__":
    csv_path = "Government_schemes_final_english.csv"
    if os.path.exists(csv_path):
        success, message = process_government_schemes_csv(csv_path)
        if success:
            # Test question
            test_answer = answer_schemes_question("What schemes are available for women?")
            print(f"Test answer: {test_answer}")