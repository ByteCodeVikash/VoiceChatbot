# enhanced_database.py - Replace database.py
import os
import json
import logging
import pandas as pd
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
import warnings
from config import CONFIG

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.WARNING)

class EnhancedRAGDatabase:
    def __init__(self, csv_path, groq_api_key):
        self.csv_path = csv_path
        self.groq_api_key = groq_api_key
        self.working_dir = os.path.dirname(os.path.abspath(__file__))
        self.vectorstore_path = os.path.join(self.working_dir, "schemes_vectorstore")
        
        # Set environment variable
        os.environ["GROQ_API_KEY"] = groq_api_key
        
        # Initialize models
        self.embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        self.llm = ChatGroq(
            model="deepseek-r1-distill-llama-70b",
            temperature=0.1
        )
        
        self.qa_chain = None
        self.available = self._initialize_system()
    
    def _initialize_system(self):
        """Initialize RAG system"""
        try:
            # Check if vectorstore exists
            if os.path.exists(self.vectorstore_path):
                logging.info("✅ Loading existing vectorstore")
                return self._setup_qa_chain()
            else:
                logging.info("🔄 Creating new vectorstore from CSV")
                if self._process_csv_to_vectorstore():
                    return self._setup_qa_chain()
                return False
        except Exception as e:
            logging.error(f"❌ RAG initialization failed: {e}")
            return False
    
    def _process_csv_to_vectorstore(self):
        """Process CSV to create vectorstore"""
        try:
            if not os.path.exists(self.csv_path):
                logging.error(f"CSV file not found: {self.csv_path}")
                return False
            
            # Read CSV
            df = pd.read_csv(self.csv_path)
            logging.info(f"📊 Loaded {len(df)} schemes from CSV")
            
            documents = []
            
            # Create documents for each scheme
            for idx, row in df.iterrows():
                scheme_text = f"""
SCHEME: {row.get('Name', 'N/A')}
DEPARTMENT: {row.get('Department', 'N/A')}

DETAILS: {row.get('Details', 'N/A')}

BENEFITS: {row.get('Benefits', 'N/A')}

ELIGIBILITY: {row.get('Eligibility', 'N/A')}

APPLICATION PROCESS: {row.get('Application_Process', 'N/A')}

REQUIRED DOCUMENTS: {row.get('Document_Required', 'N/A')}

DEMOGRAPHICS:
Gender: {row.get('Gender', 'N/A')}
Age: {row.get('Min Age', 'N/A')}-{row.get('Max Age', 'N/A')} years
Caste: {row.get('Caste', 'N/A')}
Minority: {row.get('Minority', 'N/A')}

URL: {row.get('URL', 'N/A')}
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
            
            # Create text chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100
            )
            
            splits = text_splitter.split_documents(documents)
            logging.info(f"📝 Created {len(splits)} text chunks")
            
            # Create vectorstore
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embedding,
                persist_directory=self.vectorstore_path
            )
            
            logging.info("✅ Vectorstore created successfully")
            return True
            
        except Exception as e:
            logging.error(f"❌ CSV processing failed: {e}")
            return False
    
    def _setup_qa_chain(self):
        """Setup QA chain for questions"""
        try:
            # Custom prompt for government schemes
            prompt_template = """
You are an expert assistant for Indian Government Schemes. Answer questions accurately and concisely.

Context: {context}

Question: {question}

Instructions:
- Provide specific scheme names, departments, and key benefits
- Keep responses under 150 words for voice output
- Use simple language suitable for Hindi/English/Hinglish users
- If multiple schemes match, mention top 2-3 schemes
- Be factual based on the provided context

Answer:
"""

            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Load vectorstore
            vectorstore = Chroma(
                persist_directory=self.vectorstore_path,
                embedding_function=self.embedding
            )
            
            # Create retriever
            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
            
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )
            
            logging.info("✅ QA Chain ready")
            return True
            
        except Exception as e:
            logging.error(f"❌ QA Chain setup failed: {e}")
            return False
    
    def search_schemes(self, query, limit=5):
        """Main search function - replaces old database search"""
        if not self.available or not self.qa_chain:
            return []
        
        try:
            # Get answer from RAG system
            result = self.qa_chain.invoke({"query": query})
            answer = result["result"]
            
            # Extract scheme information from answer
            schemes = self._parse_answer_to_schemes(answer, result.get("source_documents", []))
            
            return schemes[:limit]
            
        except Exception as e:
            logging.error(f"❌ Search failed: {e}")
            return []
    
    def search_by_context(self, query, occupation=None, location=None, limit=5):
        """Context-aware search - enhanced for voice assistant"""
        # Build enhanced query with context
        enhanced_query_parts = [query]
        
        if occupation:
            occupation_mapping = {
                'farmer': 'agriculture farming kisan crop cultivation',
                'fisherman': 'fishing marine boat matsya',
                'women': 'women female महिला woman',
                'business': 'business entrepreneur loan mudra'
            }
            if occupation in occupation_mapping:
                enhanced_query_parts.append(occupation_mapping[occupation])
        
        if location:
            enhanced_query_parts.append(location)
        
        enhanced_query = ' '.join(enhanced_query_parts)
        
        return self.search_schemes(enhanced_query, limit)
    
    def _parse_answer_to_schemes(self, answer, source_docs):
        """Parse LLM answer into structured scheme format for voice assistant"""
        schemes = []
        
        # Try to extract scheme names from the answer
        lines = answer.split('\n')
        scheme_info = {}
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('📚'):
                # Look for scheme patterns
                if any(keyword in line.lower() for keyword in ['scheme', 'योजना', 'yojana']):
                    scheme_info = {
                        'Name': line.replace('*', '').replace('#', '').strip()[:100],
                        'Details': answer[:200],
                        'Benefits': self._extract_benefits(answer),
                        'Eligibility': self._extract_eligibility(answer),
                        'Category': 'Government Scheme',
                        'Location': 'India',
                        'Score': 0.9
                    }
                    schemes.append(scheme_info)
                    break
        
        # If no scheme extracted, create generic response
        if not schemes:
            schemes = [{
                'Name': 'Government Scheme Information',
                'Details': answer[:200],
                'Benefits': answer[:150],
                'Eligibility': 'As per scheme guidelines',
                'Category': 'Government Scheme',
                'Location': 'India',
                'Score': 0.8
            }]
        
        return schemes
    
    def _extract_benefits(self, text):
        """Extract benefits from answer text"""
        benefit_keywords = ['benefit', 'लाभ', 'advantage', 'subsidy', '₹', 'rupees']
        
        sentences = text.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in benefit_keywords):
                return sentence.strip()[:100]
        
        return text[:100]
    
    def _extract_eligibility(self, text):
        """Extract eligibility from answer text"""
        eligibility_keywords = ['eligibility', 'eligible', 'पात्र', 'qualify', 'criteria']
        
        sentences = text.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in eligibility_keywords):
                return sentence.strip()[:100]
        
        return "Check scheme guidelines"
    
    def get_scheme_count(self):
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

# Factory function to maintain compatibility
def SchemeDatabase(db_path, csv_path):
    """Factory function for backward compatibility"""
    # Get Groq API key from config
    groq_api_key = CONFIG.get("GROQ_API_KEY", "")
    
    if not groq_api_key:
        # Try to load from config.json
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            with open(config_path) as f:
                config_data = json.load(f)
                groq_api_key = config_data.get("GROQ_API_KEY", "")
        except:
            logging.warning("⚠️ No Groq API key found, using fallback")
            groq_api_key = "fallback"
    
    return EnhancedRAGDatabase(csv_path, groq_api_key)