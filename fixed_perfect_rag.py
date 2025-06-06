# fixed_perfect_rag.py - Chroma compatibility fixed
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

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.WARNING)

# Configuration
working_dir = os.path.dirname(os.path.abspath(__file__))

# Load config
try:
    with open(os.path.join(working_dir, "config.json")) as config_file:
        config_data = json.load(config_file)
        GROQ_API_KEY = config_data.get("GROQ_API_KEY", "")
except Exception as e:
    print(f"Config error: {e}")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Initialize models
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0.1
)

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
    """Create vectorstore without deprecated parameters"""
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
    """Setup QA chain with fixed retriever"""
    
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
        
        # Add source info
        source_docs = result.get("source_documents", [])
        if source_docs:
            answer += f"\n\n📚 Information from {len(source_docs)} relevant scheme(s)."
        
        return answer
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

# For testing
if __name__ == "__main__":
    csv_path = "Government_schemes_final_english.csv"
    if os.path.exists(csv_path):
        success, message = process_government_schemes_csv(csv_path)
        if success:
            # Test question
            test_answer = answer_schemes_question("What schemes are available for women?")
            print(f"Test answer: {test_answer}")