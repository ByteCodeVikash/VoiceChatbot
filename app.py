from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json
import os
import csv
import re

app = FastAPI(title="Government Schemes Assistant")

# In-memory storage
schemes_data = []

def load_csv_data():
    """Load CSV without pandas"""
    global schemes_data
    csv_path = "Government_schemes_final_english.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            schemes_data = list(reader)
            print(f"✅ Loaded {len(schemes_data)} schemes")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")

def simple_search(query, limit=5):
    """Ultra simple text search"""
    if not schemes_data:
        return []
    
    query_lower = query.lower()
    query_words = query_lower.split()
    results = []
    
    for scheme in schemes_data:
        score = 0
        
        # Search in all fields
        searchable_text = " ".join([
            str(scheme.get('Name', '')),
            str(scheme.get('Department', '')), 
            str(scheme.get('Details', '')),
            str(scheme.get('Benefits', '')),
            str(scheme.get('Eligibility', ''))
        ]).lower()
        
        # Simple scoring
        for word in query_words:
            if len(word) > 2:  # Skip very short words
                count = searchable_text.count(word)
                score += count * len(word)
        
        # Bonus for exact matches in name
        name = str(scheme.get('Name', '')).lower()
        if query_lower in name:
            score += 50
        
        if score > 0:
            scheme_copy = scheme.copy()
            scheme_copy['search_score'] = score
            results.append(scheme_copy)
    
    # Sort by score
    results.sort(key=lambda x: x.get('search_score', 0), reverse=True)
    return results[:limit]

@app.on_event("startup")
async def startup():
    print("🚀 Starting Government Schemes Assistant...")
    load_csv_data()
    print("✅ Ready!")

@app.get("/")
async def homepage():
    total_schemes = len(schemes_data)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Government Schemes Assistant</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1000px; 
                margin: 0 auto; 
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{ 
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center; 
            }}
            h1 {{ 
                color: #2c3e50; 
                margin-bottom: 10px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }}
            .subtitle {{ 
                color: #7f8c8d; 
                margin-bottom: 30px;
                font-size: 1.2em;
            }}
            .stats {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 4px solid #3498db;
            }}
            .search-box {{
                background: #f8f9fa;
                padding: 30px;
                border-radius: 10px;
                margin: 30px 0;
            }}
            input {{ 
                width: 100%; 
                max-width: 600px;
                padding: 18px; 
                margin: 15px 0; 
                border: 2px solid #ddd;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: all 0.3s ease;
            }}
            input:focus {{
                border-color: #3498db;
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
            }}
            button {{ 
                padding: 18px 40px; 
                margin: 15px; 
                font-size: 18px;
                background: linear-gradient(45deg, #3498db, #2980b9);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: bold;
            }}
            button:hover {{ 
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
            }}
            .response {{ 
                background: #ecf0f1; 
                padding: 25px; 
                margin: 25px 0; 
                border-radius: 10px;
                text-align: left;
                border-left: 5px solid #3498db;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .scheme {{ 
                background: white;
                margin: 20px 0;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 3px 15px rgba(0,0,0,0.1);
                border-left: 4px solid #27ae60;
                transition: transform 0.2s ease;
            }}
            .scheme:hover {{
                transform: translateY(-2px);
            }}
            .scheme h3 {{ 
                color: #2c3e50; 
                margin-top: 0;
                font-size: 1.4em;
            }}
            .loading {{ 
                color: #f39c12;
                font-size: 1.2em;
                padding: 20px;
            }}
            .error {{ 
                color: #e74c3c;
                font-size: 1.1em;
                padding: 20px;
            }}
            .examples {{
                background: #e8f5e8;
                padding: 20px;
                border-radius: 10px;
                margin-top: 30px;
                border-left: 4px solid #27ae60;
            }}
            .examples h3 {{ color: #27ae60; }}
            .example-tags {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                justify-content: center;
                margin-top: 15px;
            }}
            .tag {{
                background: #3498db;
                color: white;
                padding: 8px 15px;
                border-radius: 20px;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            .tag:hover {{
                background: #2980b9;
                transform: scale(1.05);
            }}
            @media (max-width: 768px) {{
                .container {{ padding: 20px; }}
                h1 {{ font-size: 2em; }}
                input {{ font-size: 16px; }}
                button {{ padding: 15px 30px; font-size: 16px; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏛️ Government Schemes Assistant</h1>
            <p class="subtitle">Find government schemes in Hindi, English, or Hinglish!</p>
            
            <div class="stats">
                <strong>📊 Database Status:</strong> {total_schemes} government schemes loaded and ready!
            </div>
            
            <div class="search-box">
                <input type="text" id="questionInput" 
                       placeholder="Type your question here (e.g., farmer scheme, women loan, मछुआरा योजना)">
                <br>
                <button onclick="askQuestion()">🔍 Search Schemes</button>
            </div>
            
            <div id="response"></div>
            
            <div class="examples">
                <h3>🎯 Try These Examples:</h3>
                <div class="example-tags">
                    <span class="tag" onclick="searchExample('farmer scheme')">👨‍🌾 Farmer Scheme</span>
                    <span class="tag" onclick="searchExample('महिला योजना')">👩 Women Schemes</span>
                    <span class="tag" onclick="searchExample('fisherman subsidy')">🎣 Fisherman</span>
                    <span class="tag" onclick="searchExample('business loan')">💼 Business Loan</span>
                    <span class="tag" onclick="searchExample('education scholarship')">🎓 Education</span>
                    <span class="tag" onclick="searchExample('rural development')">🏘️ Rural</span>
                </div>
            </div>
        </div>

        <script>
            async function askQuestion() {{
                const input = document.getElementById('questionInput');
                const question = input.value.trim();
                
                if (!question) {{
                    alert('Please enter a question! 📝');
                    return;
                }}
                
                document.getElementById('response').innerHTML = 
                    '<p class="loading">🔍 Searching through {total_schemes} government schemes...</p>';
                
                try {{
                    const response = await fetch('/search', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ query: question }})
                    }});
                    
                    const data = await response.json();
                    
                    if (data.schemes && data.schemes.length > 0) {{
                        let html = `<div class="response">
                            <h2>📋 Found ${{data.schemes.length}} Relevant Schemes for "${{question}}":</h2>`;
                        
                        data.schemes.forEach((scheme, index) => {{
                            const name = scheme.Name || 'Government Scheme';
                            const dept = scheme.Department || 'N/A';
                            const details = scheme.Details || 'Details not available';
                            const benefits = scheme.Benefits || 'Benefits information not available';
                            const eligibility = scheme.Eligibility || 'Eligibility criteria not specified';
                            
                            html += `
                                <div class="scheme">
                                    <h3>${{index + 1}}. ${{name}}</h3>
                                    <p><strong>🏛️ Department:</strong> ${{dept}}</p>
                                    <p><strong>📝 Details:</strong> ${{details.substring(0, 200)}}${{details.length > 200 ? '...' : ''}}</p>
                                    <p><strong>💰 Benefits:</strong> ${{benefits.substring(0, 150)}}${{benefits.length > 150 ? '...' : ''}}</p>
                                    <p><strong>✅ Eligibility:</strong> ${{eligibility.substring(0, 150)}}${{eligibility.length > 150 ? '...' : ''}}</p>
                                </div>
                            `;
                        }});
                        
                        html += '</div>';
                        document.getElementById('response').innerHTML = html;
                    }} else {{
                        document.getElementById('response').innerHTML = 
                            `<div class="response error">
                                ❌ No schemes found for "${{question}}". 
                                <br><br>Try keywords like: farmer, women, fisherman, loan, subsidy, education, rural, business
                            </div>`;
                    }}
                    
                }} catch (error) {{
                    document.getElementById('response').innerHTML = 
                        '<div class="response error">❌ Error occurred. Please try again.</div>';
                    console.error('Error:', error);
                }}
            }}
            
            function searchExample(query) {{
                document.getElementById('questionInput').value = query;
                askQuestion();
            }}
            
            document.getElementById('questionInput').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') askQuestion();
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/search")
async def search_schemes(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")
        
        if not query:
            return {"schemes": [], "message": "Please provide a search query"}
        
        # Search schemes
        schemes = simple_search(query, limit=5)
        
        return {
            "schemes": schemes,
            "query": query,
            "count": len(schemes)
        }
        
    except Exception as e:
        print(f"Search error: {e}")
        return {"schemes": [], "message": f"Search failed: {str(e)}"}

@app.get("/health")
async def health():
    return {
        "status": "OK", 
        "message": "Government Schemes Assistant is running!",
        "total_schemes": len(schemes_data)
    }

@app.get("/api/stats")
async def get_stats():
    return {
        "total_schemes": len(schemes_data),
        "status": "active",
        "search_ready": len(schemes_data) > 0
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)