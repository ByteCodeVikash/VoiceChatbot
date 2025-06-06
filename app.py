import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime
import logging
from typing import Dict, List, Any

# Set page config
st.set_page_config(
    page_title="🏛️ Government Schemes Assistant",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #1f77b4;
    }
    .user-message {
        background-color: #e8f4f8;
        border-left-color: #1f77b4;
    }
    .assistant-message {
        background-color: #f0f8e8;
        border-left-color: #28a745;
    }
    .scheme-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stats-card {
        background: linear-gradient(45deg, #1f77b4, #17a2b8);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'name': '',
        'language': 'english',
        'occupation': '',
        'location': '',
        'setup_complete': False
    }
if 'scheme_db' not in st.session_state:
    st.session_state.scheme_db = None

# Import your modules
try:
    from enhanced_rag_database import EnhancedRAGDatabase, answer_schemes_question
    from synonym_dict import enhance_search_query
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    st.error("❌ RAG modules not found. Please ensure all dependencies are installed.")

class StreamlitSchemeAssistant:
    def __init__(self):
        self.setup_database()
    
    def setup_database(self):
        """Initialize the database"""
        if st.session_state.scheme_db is None:
            try:
                # Get API key from secrets or environment
                groq_api_key = st.secrets.get("GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
                
                if not groq_api_key:
                    st.error("❌ Groq API Key not found. Please add it to Streamlit secrets.")
                    return False
                
                csv_path = "Government_schemes_final_english.csv"
                if not os.path.exists(csv_path):
                    st.error(f"❌ CSV file not found: {csv_path}")
                    return False
                
                with st.spinner("🔄 Initializing AI Database..."):
                    st.session_state.scheme_db = EnhancedRAGDatabase(csv_path, groq_api_key)
                
                if st.session_state.scheme_db and st.session_state.scheme_db.available:
                    st.success("✅ AI Database Ready!")
                    return True
                else:
                    st.error("❌ Database initialization failed")
                    return False
                    
            except Exception as e:
                st.error(f"❌ Database setup error: {e}")
                return False
        return True
    
    def search_schemes(self, query: str, occupation: str = None, location: str = None, top_k: int = 5):
        """Search for relevant schemes"""
        if not st.session_state.scheme_db:
            return []
        
        try:
            results = st.session_state.scheme_db.search_by_context(
                query, occupation, location, top_k
            )
            return results
        except Exception as e:
            st.error(f"Search error: {e}")
            return []
    
    def get_ai_response(self, query: str, occupation: str = None, location: str = None):
        """Get AI-powered response"""
        try:
            enhanced_query = query
            if occupation:
                enhanced_query += f" for {occupation}"
            if location:
                enhanced_query += f" in {location}"
            
            # Get AI response
            response = answer_schemes_question(enhanced_query)
            
            # Clean response
            import re
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
            response = re.sub(r'[<>{}*#]', '', response)
            response = re.sub(r'\s+', ' ', response).strip()
            
            return response if response and len(response) > 10 else "I couldn't find specific information. Please try a different query."
            
        except Exception as e:
            return f"Error getting AI response: {e}"

def main():
    # Initialize assistant
    assistant = StreamlitSchemeAssistant()
    
    # Header
    st.markdown('<h1 class="main-header">🏛️ Government Schemes AI Assistant</h1>', unsafe_allow_html=True)
    
    # Sidebar for user profile
    with st.sidebar:
        st.header("👤 User Profile")
        
        # Language selection
        language = st.selectbox(
            "🌐 Select Language",
            ["english", "hindi", "hinglish"],
            index=["english", "hindi", "hinglish"].index(st.session_state.user_profile['language'])
        )
        st.session_state.user_profile['language'] = language
        
        # User details
        name = st.text_input("📝 Your Name", value=st.session_state.user_profile['name'])
        st.session_state.user_profile['name'] = name
        
        occupation = st.selectbox(
            "💼 Occupation",
            ["", "farmer", "fisherman", "women", "business", "student", "teacher", "doctor", "other"],
            index=0 if not st.session_state.user_profile['occupation'] else 
                  ["", "farmer", "fisherman", "women", "business", "student", "teacher", "doctor", "other"].index(st.session_state.user_profile['occupation']) if st.session_state.user_profile['occupation'] in ["", "farmer", "fisherman", "women", "business", "student", "teacher", "doctor", "other"] else 8
        )
        st.session_state.user_profile['occupation'] = occupation
        
        location = st.selectbox(
            "📍 State/Location",
            ["", "andhra pradesh", "gujarat", "goa", "karnataka", "kerala", "tamil nadu", 
             "maharashtra", "uttar pradesh", "rajasthan", "punjab", "haryana", "other"],
            index=0 if not st.session_state.user_profile['location'] else
                  ["", "andhra pradesh", "gujarat", "goa", "karnataka", "kerala", "tamil nadu", 
                   "maharashtra", "uttar pradesh", "rajasthan", "punjab", "haryana", "other"].index(st.session_state.user_profile['location']) if st.session_state.user_profile['location'] in ["", "andhra pradesh", "gujarat", "goa", "karnataka", "kerala", "tamil nadu", "maharashtra", "uttar pradesh", "rajasthan", "punjab", "haryana", "other"] else 12
        )
        st.session_state.user_profile['location'] = location
        
        # Save profile
        if st.button("💾 Save Profile"):
            st.session_state.user_profile['setup_complete'] = True
            st.success("✅ Profile saved!")
        
        # Stats
        if st.session_state.scheme_db:
            total_schemes = st.session_state.scheme_db.get_scheme_count()
            st.markdown(f"""
            <div class="stats-card">
                <h3>📊 Database Stats</h3>
                <p><strong>{total_schemes}</strong> Government Schemes</p>
                <p>🤖 AI-Powered Search</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat with AI Assistant")
        
        # Chat interface
        chat_container = st.container()
        
        # Display chat messages
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 You:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>🤖 Assistant:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        user_input = st.chat_input("Ask about government schemes... (e.g., 'farming subsidies', 'women empowerment schemes')")
        
        if user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get AI response
            with st.spinner("🧠 AI is thinking..."):
                response = assistant.get_ai_response(
                    user_input,
                    st.session_state.user_profile['occupation'],
                    st.session_state.user_profile['location']
                )
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Rerun to update chat
            st.rerun()
    
    with col2:
        st.subheader("🔍 Quick Search")
        
        # Quick search examples
        st.write("**Popular Searches:**")
        
        quick_searches = [
            "🌾 Farmer subsidies",
            "👩 Women empowerment",
            "🎣 Fishing schemes",
            "📚 Education loans",
            "🏠 Housing schemes",
            "💼 Business loans"
        ]
        
        for search in quick_searches:
            if st.button(search, key=search):
                # Trigger search
                query = search.split(" ", 1)[1]  # Remove emoji
                st.session_state.messages.append({"role": "user", "content": query})
                
                with st.spinner("🧠 AI is thinking..."):
                    response = assistant.get_ai_response(
                        query,
                        st.session_state.user_profile['occupation'],
                        st.session_state.user_profile['location']
                    )
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        # Recent schemes display
        st.subheader("📋 Sample Schemes")
        if st.session_state.scheme_db:
            try:
                sample_schemes = assistant.search_schemes("agriculture", top_k=3)
                for scheme in sample_schemes:
                    with st.expander(f"📄 {scheme.get('Name', 'Unknown')[:50]}..."):
                        st.write(f"**Department:** {scheme.get('Department', 'N/A')}")
                        st.write(f"**Benefits:** {scheme.get('Benefits', 'N/A')[:200]}...")
                        st.write(f"**Eligibility:** {scheme.get('Eligibility', 'N/A')[:200]}...")
            except:
                st.write("Sample schemes will load once database is ready.")

if __name__ == "__main__":
    main()