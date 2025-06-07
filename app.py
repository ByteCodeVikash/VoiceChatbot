from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
import json
import os
import pandas as pd
import sqlite3
from rapidfuzz import fuzz

app = FastAPI(title="Government Schemes Voice Assistant")

# Simple database class without RAG
class SimpleSchemeDatabase:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.schemes = []
        self.load_data()
    
    def load_data(self):
        """Load CSV data"""
        try:
            if os.path.exists(self.csv_path):
                df = pd.read_csv(self.csv_path)
                self.schemes = df.to_dict('records')
                print(f"✅ Loaded {len(self.schemes)} schemes")
            else:
                print(f"❌ CSV file not found: {self.csv_path}")
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
    
    def search_schemes(self, query, limit=5):
        """Simple text search"""
        if not self.schemes:
            return []
        
        query_lower = query.lower()
        results = []
        
        for scheme in self.schemes:
            score = 0
            
            # Search in name
            name = str(scheme.get('Name', '')).lower()
            if query_lower in name:
                score += 3
            
            # Search in details
            details = str(scheme.get('Details', '')).lower()
            if query_lower in details:
                score += 2
            
            # Search in benefits
            benefits = str(scheme.get('Benefits', '')).lower()
            if query_lower in benefits:
                score += 1
            
            # Search in department
            dept = str(scheme.get('Department', '')).lower()
            if query_lower in dept:
                score += 1
            
            if score > 0:
                scheme_copy = scheme.copy()
                scheme_copy['score'] = score
                results.append(scheme_copy)
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

# Global database
db = None

@app.on_event("startup")
async def startup_event():
    global db
    print("🚀 Starting Simple Schemes Assistant...")
    db = SimpleSchemeDatabase("Government_schemes_final_english.csv")
    print("✅ Database ready")

@app.get("/")
async def homepage():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Government Schemes Assistant</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 900px; 
                margin: 0 auto; 
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container { 
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center; 
            }
            h1 { color: #2c3e50; margin-bottom: 10px; }
            .subtitle { color: #7f8c8d; margin-bottom: 30px; }
            input { 
                width: 70%; 
                padding: 15px; 
                margin: 10px; 
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
            }
            button { 
                padding: 15px 25px; 
                margin: 10px; 
                font-size: 16px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            button:hover { background-color: #2980b9; }
            .response { 
                background: #ecf0f1; 
                padding: 20px; 
                margin: 20px 0; 
                border-radius: 8px;
                text-align: left;
                border-left: 4px solid #3498db;
            }
            .scheme { 
                background: white;
                margin: 15px 0;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .scheme h3 { color: #2c3e50; margin-top: 0; }
            .loading { color: #f39c12; }
            .error { color: #e74c3c; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Government Schemes Assistant</h1>
            <p class="subtitle">Ask about government schemes in Hindi, English, or Hinglish!</p>
            
            <div>
                <input type="text" id="questionInput" placeholder="Type your question here (e.g., farmer scheme, women loan, fisherman subsidy)">
                <br>
                <button onclick="askQuestion()">🔍 Search Schemes</button>
            </div>
            
            <div id="response"></div>
            
            <div style="margin-top: 30px; font-size: 14px; color: #7f8c8d;">
                <p><strong>Examples:</strong></p>
                <p>• "farmer scheme" • "महिला योजना" • "kisan subsidy" • "fisherman loan"</p>
            </div>
        </div>

        <script>
            async function askQuestion() {
                const input = document.getElementById('questionInput');
                const question = input.value.trim();
                
                if (!question) {
                    alert('Please enter a question!');
                    return;
                }
                
                document.getElementById('response').innerHTML = 
                    '<p class="loading">🔍 Searching schemes...</p>';
                
                try {
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: question })
                    });
                    
                    const data = await response.json();
                    
                    if (data.schemes && data.schemes.length > 0) {
                        let html = `<div class="response">
                            <h2>📋 Found ${data.schemes.length} Relevant Schemes:</h2>`;
                        
                        data.schemes.forEach((scheme, index) => {
                            html += `
                                <div class="scheme">
                                    <h3>${index + 1}. ${scheme.Name || 'Government Scheme'}</h3>
                                    <p><strong>Department:</strong> ${scheme.Department || 'N/A'}</p>
                                    <p><strong>Details:</strong> ${scheme.Details || 'N/A'}</p>
                                    <p><strong>Benefits:</strong> ${scheme.Benefits || 'N/A'}</p>
                                    <p><strong>Eligibility:</strong> ${scheme.Eligibility || 'N/A'}</p>
                                </div>
                            `;
                        });
                        
                        html += '</div>';
                        document.getElementById('response').innerHTML = html;
                    } else {
                        document.getElementById('response').innerHTML = 
                            '<div class="response error">❌ No schemes found. Try different keywords like "farmer", "women", "fisherman", "loan", "subsidy".</div>';
                    }
                    
                } catch (error) {
                    document.getElementById('response').innerHTML = 
                        '<div class="response error">❌ Error occurred. Please try again.</div>';
                    console.error('Error:', error);
                }
            }
            
            document.getElementById('questionInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') askQuestion();
            });
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
        
        global db
        if not db:
            return {"schemes": [], "message": "Database not ready"}
        
        # Search schemes
        schemes = db.search_schemes(query, limit=5)
        
        return {
            "schemes": schemes,
            "query": query,
            "count": len(schemes)
        }
        
    except Exception as e:
        print(f"Search error: {e}")
        return {"schemes": [], "message": "Search failed"}

@app.get("/health")
async def health():
    return {"status": "OK", "message": "Government Schemes Assistant is running!"}

@app.get("/stats")
async def get_stats():
    global db
    if db:
        return {
            "total_schemes": len(db.schemes),
            "status": "active"
        }
    return {"total_schemes": 0, "status": "inactive"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)