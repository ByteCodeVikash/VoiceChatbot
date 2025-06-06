import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime
import logging
from typing import Dict, List, Any
import requests
from dataclasses import dataclass

# Set page config
st.set_page_config(
    page_title="🏛️ Government Schemes Assistant",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .chat-message {
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .user-message {
        background: linear-gradient(135deg, #e8f4f8, #d1ecf1);
        border-left-color: #1f77b4;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f0f8e8, #e2f5d3);
        border-left-color: #28a745;
    }
    .scheme-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .scheme-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    .stats-card {
        background: linear-gradient(135deg, #1f77b4, #17a2b8);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3);
    }
    .quick-btn {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        margin: 0.3rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 3px 8px rgba(40, 167, 69, 0.3);
    }
    .quick-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(40, 167, 69, 0.4);
    }
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem !important;
            margin-bottom: 1rem !important;
        }
        .chat-message {
            padding: 0.8rem !important;
            font-size: 0.9rem !important;
        }
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
if 'schemes_data' not in st.session_state:
    st.session_state.schemes_data = None

@dataclass
class Scheme:
    name: str
    department: str
    details: str
    benefits: str
    eligibility: str
    documents: str
    gender: str
    url: str

class SimplifiedSchemeAssistant:
    def __init__(self):
        self.setup_data()
        
    def setup_data(self):
        """Load CSV data"""
        try:
            csv_path = "Government_schemes_final_english.csv"
            if os.path.exists(csv_path):
                st.session_state.schemes_data = pd.read_csv(csv_path)
                st.success(f"✅ Loaded {len(st.session_state.schemes_data)} schemes from CSV")
            else:
                st.error("❌ CSV file not found. Please upload Government_schemes_final_english.csv")
                # Create sample data for demo
                st.session_state.schemes_data = pd.DataFrame({
                    'Name': ['PM-KISAN Scheme', 'Fisheries Development Scheme'],
                    'Department': ['Agriculture', 'Fisheries'],
                    'Details': ['Direct income support for farmers', 'Financial assistance for fishermen'],
                    'Benefits': ['₹6000 per year', 'Subsidized equipment'],
                    'Eligibility': ['Small farmers', 'Registered fishermen'],
                    'Document_Required': ['Land records', 'Fishing license'],
                    'Gender': ['All', 'All'],
                    'URL': ['example.com', 'example.com']
                })
                st.warning("⚠️ Using demo data. Upload CSV for full functionality.")
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
    
    def search_schemes(self, query: str, occupation: str = None, location: str = None, top_k: int = 5):
        """Simple text-based search"""
        if st.session_state.schemes_data is None:
            return []
        
        try:
            df = st.session_state.schemes_data.copy()
            
            # Convert query to lowercase for matching
            query_lower = query.lower()
            
            # Create search columns
            df['search_text'] = (
                df['Name'].fillna('').astype(str) + ' ' +
                df['Department'].fillna('').astype(str) + ' ' +
                df['Details'].fillna('').astype(str) + ' ' +
                df['Benefits'].fillna('').astype(str) + ' ' +
                df['Eligibility'].fillna('').astype(str)
            ).str.lower()
            
            # Basic keyword matching
            keywords = query_lower.split()
            mask = pd.Series([True] * len(df))
            
            for keyword in keywords:
                if len(keyword) > 2:  # Skip very short words
                    mask &= df['search_text'].str.contains(keyword, na=False)
            
            # Apply occupation filter
            if occupation and occupation != "":
                occupation_keywords = {
                    'farmer': ['farmer', 'agriculture', 'farming', 'crop', 'kisan'],
                    'fisherman': ['fish', 'marine', 'boat', 'matsya'],
                    'women': ['women', 'woman', 'female', 'mahila'],
                    'business': ['business', 'entrepreneur', 'mudra', 'loan'],
                    'student': ['education', 'scholarship', 'student']
                }
                
                if occupation in occupation_keywords:
                    occ_mask = pd.Series([False] * len(df))
                    for keyword in occupation_keywords[occupation]:
                        occ_mask |= df['search_text'].str.contains(keyword, na=False)
                    mask &= occ_mask
            
            # Apply location filter (basic)
            if location and location != "":
                # Simple location matching
                mask &= df['search_text'].str.contains(location.lower(), na=False)
            
            # Get results
            results = df[mask].head(top_k)
            
            # Convert to list of dicts
            schemes = []
            for _, row in results.iterrows():
                schemes.append({
                    'Name': row.get('Name', 'Unknown'),
                    'Department': row.get('Department', 'Unknown'),
                    'Details': row.get('Details', 'No details available'),
                    'Benefits': row.get('Benefits', 'Benefits information available'),
                    'Eligibility': row.get('Eligibility', 'Check eligibility criteria'),
                    'Document_Required': row.get('Document_Required', 'Standard documents required'),
                    'Gender': row.get('Gender', 'All'),
                    'URL': row.get('URL', ''),
                    'Score': 0.8  # Dummy score
                })
            
            return schemes
            
        except Exception as e:
            st.error(f"Search error: {e}")
            return []
    
    def get_groq_response(self, query: str, schemes: List[Dict], occupation: str = None, location: str = None):
        """Get AI response using Groq API"""
        try:
            # Get API key
            groq_api_key = st.secrets.get("GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
            
            if not groq_api_key:
                return self.generate_simple_response(query, schemes, occupation, location)
            
            # Build context from schemes
            context = "Available Government Schemes:\n\n"
            for i, scheme in enumerate(schemes[:3], 1):
                context += f"{i}. {scheme['Name']}\n"
                context += f"   Department: {scheme['Department']}\n"
                context += f"   Details: {scheme['Details'][:200]}...\n"
                context += f"   Benefits: {scheme['Benefits'][:150]}...\n"
                context += f"   Eligibility: {scheme['Eligibility'][:150]}...\n\n"
            
            # Build prompt
            user_context = ""
            if occupation:
                user_context += f"User is a {occupation}. "
            if location:
                user_context += f"User is from {location}. "
            
            prompt = f"""You are a helpful Government Schemes Assistant for India. {user_context}

User Query: {query}

{context}

Please provide a helpful response about the relevant government schemes. Keep it conversational and under 200 words. Focus on the most relevant schemes for the user's query.

Response:"""

            # Make API call
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "model": "mixtral-8x7b-32768",
                "temperature": 0.1,
                "max_tokens": 300
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                return ai_response
            else:
                st.warning(f"API Error: {response.status_code}")
                return self.generate_simple_response(query, schemes, occupation, location)
                
        except Exception as e:
            st.warning(f"AI API failed: {e}")
            return self.generate_simple_response(query, schemes, occupation, location)
    
    def generate_simple_response(self, query: str, schemes: List[Dict], occupation: str = None, location: str = None):
        """Generate simple response without AI"""
        if not schemes:
            return f"I couldn't find specific schemes for '{query}'. Please try different keywords like 'farmer', 'women', 'education', 'business', or 'housing'."
        
        response = f"I found {len(schemes)} relevant government schemes for your query '{query}':\n\n"
        
        for i, scheme in enumerate(schemes[:2], 1):
            response += f"**{i}. {scheme['Name']}**\n"
            response += f"• **Department:** {scheme['Department']}\n"
            response += f"• **Benefits:** {scheme['Benefits'][:100]}...\n"
            response += f"• **Eligibility:** {scheme['Eligibility'][:100]}...\n\n"
        
        if len(schemes) > 2:
            response += f"...and {len(schemes) - 2} more schemes available.\n\n"
        
        response += "Would you like more details about any specific scheme?"
        
        return response

def main():
    # Initialize assistant
    assistant = SimplifiedSchemeAssistant()
    
    # Header
    st.markdown('<h1 class="main-header">🏛️ Government Schemes AI Assistant</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem;'>Discover government schemes tailored for you</p>", unsafe_allow_html=True)
    
    # Sidebar for user profile
    with st.sidebar:
        st.header("👤 User Profile")
        
        # Language selection
        language = st.selectbox(
            "🌐 Language",
            ["english", "hindi", "hinglish"],
            index=["english", "hindi", "hinglish"].index(st.session_state.user_profile['language'])
        )
        st.session_state.user_profile['language'] = language
        
        # User details
        name = st.text_input("📝 Name", value=st.session_state.user_profile['name'])
        st.session_state.user_profile['name'] = name
        
        occupation = st.selectbox(
            "💼 Occupation",
            ["", "farmer", "fisherman", "women", "business", "student", "teacher", "doctor", "other"],
            index=0 if not st.session_state.user_profile['occupation'] else 
                  ["", "farmer", "fisherman", "women", "business", "student", "teacher", "doctor", "other"].index(st.session_state.user_profile['occupation']) if st.session_state.user_profile['occupation'] in ["", "farmer", "fisherman", "women", "business", "student", "teacher", "doctor", "other"] else 8
        )
        st.session_state.user_profile['occupation'] = occupation
        
        location = st.selectbox(
            "📍 State",
            ["", "andhra pradesh", "gujarat", "goa", "karnataka", "kerala", "tamil nadu", 
             "maharashtra", "uttar pradesh", "rajasthan", "punjab", "haryana", "other"],
            index=0
        )
        st.session_state.user_profile['location'] = location
        
        # Save profile
        if st.button("💾 Save Profile", key="save_profile"):
            st.session_state.user_profile['setup_complete'] = True
            st.success("✅ Profile saved!")
        
        # Stats
        if st.session_state.schemes_data is not None:
            total_schemes = len(st.session_state.schemes_data)
            st.markdown(f"""
            <div class="stats-card">
                <h3>📊 Database</h3>
                <p><strong>{total_schemes:,}</strong> Government Schemes</p>
                <p>🔍 Smart Search Enabled</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([2.5, 1.5])
    
    with col1:
        st.subheader("💬 Chat with Assistant")
        
        # Display chat messages
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
        user_input = st.chat_input("Ask about government schemes... (e.g., 'farming subsidies', 'women schemes')")
        
        if user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Search for schemes
            with st.spinner("🔍 Searching schemes..."):
                schemes = assistant.search_schemes(
                    user_input,
                    st.session_state.user_profile['occupation'],
                    st.session_state.user_profile['location'],
                    top_k=5
                )
            
            # Get AI response
            with st.spinner("🤖 Generating response..."):
                response = assistant.get_groq_response(
                    user_input,
                    schemes,
                    st.session_state.user_profile['occupation'],
                    st.session_state.user_profile['location']
                )
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Rerun to update chat
            st.rerun()
    
    with col2:
        st.subheader("🚀 Quick Search")
        
        # Quick search buttons
        quick_searches = [
            ("🌾", "Farmer schemes"),
            ("👩", "Women schemes"),
            ("🎣", "Fisherman schemes"),
            ("📚", "Education schemes"),
            ("🏠", "Housing schemes"),
            ("💼", "Business loans"),
            ("🏥", "Health schemes"),
            ("👵", "Senior citizen schemes")
        ]
        
        for emoji, search_text in quick_searches:
            if st.button(f"{emoji} {search_text}", key=f"quick_{search_text}", use_container_width=True):
                # Add to chat
                st.session_state.messages.append({"role": "user", "content": search_text})
                
                # Search
                schemes = assistant.search_schemes(
                    search_text,
                    st.session_state.user_profile['occupation'],
                    st.session_state.user_profile['location']
                )
                
                # Get response
                response = assistant.get_groq_response(
                    search_text,
                    schemes,
                    st.session_state.user_profile['occupation'],
                    st.session_state.user_profile['location']
                )
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        # Sample schemes display
        st.subheader("📋 Sample Schemes")
        if st.session_state.schemes_data is not None:
            try:
                sample_schemes = assistant.search_schemes("agriculture", top_k=3)
                for scheme in sample_schemes:
                    with st.expander(f"📄 {scheme['Name'][:40]}..."):
                        st.write(f"**Department:** {scheme['Department']}")
                        st.write(f"**Benefits:** {scheme['Benefits'][:150]}...")
                        st.write(f"**Eligibility:** {scheme['Eligibility'][:150]}...")
            except:
                st.write("Loading sample schemes...")

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #888;'>🏛️ Government Schemes Assistant | Made with ❤️ using Streamlit</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()