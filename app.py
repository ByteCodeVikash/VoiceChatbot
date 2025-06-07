#!/usr/bin/env python3
"""
Ultra Simple Government Schemes Assistant
No external dependencies - Pure Python!
"""

import json
import csv
import os
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import socket

# Global data storage
schemes_data = []
server_port = int(os.environ.get("PORT", 8000))

def load_csv_data():
    """Load CSV data without any external libraries"""
    global schemes_data
    csv_path = "Government_schemes_final_english.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        schemes_data = [
            {
                "Name": "Sample Farmer Scheme",
                "Department": "Agriculture Ministry", 
                "Details": "Financial assistance for farmers to purchase equipment and seeds",
                "Benefits": "Up to 50% subsidy on agricultural equipment",
                "Eligibility": "Small and marginal farmers with land ownership documents"
            },
            {
                "Name": "Women Empowerment Loan",
                "Department": "Women & Child Development",
                "Details": "Low interest loans for women entrepreneurs",
                "Benefits": "Interest rate of 4% per annum, no collateral required",
                "Eligibility": "Women aged 18-65 with business plan"
            }
        ]
        return
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            schemes_data = []
            for row in csv_reader:
                schemes_data.append(dict(row))
        print(f"✅ Loaded {len(schemes_data)} schemes from CSV")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        schemes_data = []

def simple_search(query, limit=5):
    """Ultra simple text search without external libraries"""
    if not schemes_data:
        return []
    
    query_lower = query.lower().strip()
    
    # Handle empty query
    if not query_lower:
        return schemes_data[:limit]
    
    query_words = query_lower.split()
    results = []
    
    for scheme in schemes_data:
        score = 0
        
        # Create searchable text from all fields
        searchable_fields = [
            scheme.get('Name', ''),
            scheme.get('Department', ''),
            scheme.get('Details', ''),
            scheme.get('Benefits', ''),
            scheme.get('Eligibility', ''),
            scheme.get('Application_Process', ''),
            scheme.get('Document_Required', ''),
            scheme.get('Gender', ''),
            scheme.get('Caste', ''),
            scheme.get('Minority', '')
        ]
        
        searchable_text = ' '.join(str(field) for field in searchable_fields).lower()
        
        # Simple word matching
        for word in query_words:
            if len(word) > 2:  # Skip very short words
                word_count = searchable_text.count(word)
                score += word_count * len(word)
        
        # Bonus for name matches
        name = str(scheme.get('Name', '')).lower()
        if query_lower in name:
            score += 100
        
        # Bonus for exact phrase matches
        if query_lower in searchable_text:
            score += 50
        
        if score > 0:
            scheme_result = scheme.copy()
            scheme_result['search_score'] = score
            results.append(scheme_result)
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x.get('search_score', 0), reverse=True)
    return results[:limit]

class SchemeRequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.serve_homepage()
        elif self.path == '/health':
            self.serve_health()
        elif self.path == '/stats':
            self.serve_stats()
        else:
            self.send_error(404, "Page not found")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/search':
            self.handle_search()
        else:
            self.send_error(404, "Endpoint not found")
    
    def serve_homepage(self):
        """Serve the main HTML page"""
        total_schemes = len(schemes_data)
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Government Schemes Assistant</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .stats {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #dee2e6;
        }}
        .stats strong {{
            color: #495057;
            font-size: 1.1em;
        }}
        .search-section {{
            padding: 40px;
            text-align: center;
        }}
        .search-box {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        input[type="text"] {{
            width: 100%;
            max-width: 600px;
            padding: 18px 24px;
            font-size: 16px;
            border: 2px solid #dee2e6;
            border-radius: 25px;
            outline: none;
            transition: all 0.3s ease;
        }}
        input[type="text"]:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        button {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 18px 40px;
            font-size: 18px;
            border-radius: 25px;
            cursor: pointer;
            margin: 15px;
            transition: all 0.3s ease;
            font-weight: 600;
        }}
        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }}
        .examples {{
            background: #e8f5e8;
            padding: 25px;
            border-radius: 10px;
            margin: 30px 0;
        }}
        .examples h3 {{
            color: #28a745;
            margin-bottom: 15px;
            text-align: center;
        }}
        .example-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }}
        .tag {{
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 14px;
            font-weight: 500;
        }}
        .tag:hover {{
            background: #5a67d8;
            transform: scale(1.05);
        }}
        .results {{
            padding: 0 40px 40px;
        }}
        .result-item {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }}
        .result-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}
        .result-item h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        .result-item p {{
            margin: 10px 0;
            line-height: 1.6;
        }}
        .result-item strong {{
            color: #495057;
        }}
        .loading {{
            text-align: center;
            padding: 40px;
            color: #6c757d;
            font-size: 1.2em;
        }}
        .error {{
            background: #f8d7da;
            color: #721c24;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }}
        .no-results {{
            background: #fff3cd;
            color: #856404;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }}
        @media (max-width: 768px) {{
            .container {{ margin: 0; border-radius: 0; }}
            .header {{ padding: 30px 20px; }}
            .header h1 {{ font-size: 2em; }}
            .search-section {{ padding: 20px; }}
            .results {{ padding: 0 20px 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ Government Schemes Assistant</h1>
            <p>Find government schemes in Hindi, English, or Hinglish!</p>
        </div>
        
        <div class="stats">
            <strong>📊 Database Status: {total_schemes} government schemes loaded and ready!</strong>
        </div>
        
        <div class="search-section">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Type your question here (e.g., farmer scheme, women loan, मछुआरा योजना)" />
                <br>
                <button onclick="searchSchemes()">🔍 Search Schemes</button>
            </div>
            
            <div class="examples">
                <h3>🎯 Try These Examples:</h3>
                <div class="example-tags">
                    <span class="tag" onclick="searchExample('farmer scheme')">👨‍🌾 Farmer Scheme</span>
                    <span class="tag" onclick="searchExample('महिला योजना')">👩 Women Schemes</span>
                    <span class="tag" onclick="searchExample('fisherman subsidy')">🎣 Fisherman</span>
                    <span class="tag" onclick="searchExample('business loan')">💼 Business Loan</span>
                    <span class="tag" onclick="searchExample('education scholarship')">🎓 Education</span>
                    <span class="tag" onclick="searchExample('rural development')">🏘️ Rural Development</span>
                </div>
            </div>
        </div>
        
        <div class="results" id="results"></div>
    </div>

    <script>
        async function searchSchemes() {{
            const input = document.getElementById('searchInput');
            const query = input.value.trim();
            const resultsDiv = document.getElementById('results');
            
            if (!query) {{
                alert('Please enter a search query! 📝');
                return;
            }}
            
            resultsDiv.innerHTML = '<div class="loading">🔍 Searching through {total_schemes} government schemes...</div>';
            
            try {{
                const response = await fetch('/search', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ query: query }})
                }});
                
                const data = await response.json();
                
                if (data.schemes && data.schemes.length > 0) {{
                    let html = `<h2 style="text-align: center; color: #2c3e50; margin-bottom: 30px;">📋 Found ${{data.schemes.length}} Relevant Schemes for "${{query}}"</h2>`;
                    
                    data.schemes.forEach((scheme, index) => {{
                        const name = scheme.Name || 'Government Scheme';
                        const dept = scheme.Department || 'N/A';
                        const details = scheme.Details || 'Details not available';
                        const benefits = scheme.Benefits || 'Benefits information not available';
                        const eligibility = scheme.Eligibility || 'Eligibility criteria not specified';
                        
                        html += `
                            <div class="result-item">
                                <h3>${{index + 1}}. ${{name}}</h3>
                                <p><strong>🏛️ Department:</strong> ${{dept}}</p>
                                <p><strong>📝 Details:</strong> ${{details.substring(0, 300)}}${{details.length > 300 ? '...' : ''}}</p>
                                <p><strong>💰 Benefits:</strong> ${{benefits.substring(0, 200)}}${{benefits.length > 200 ? '...' : ''}}</p>
                                <p><strong>✅ Eligibility:</strong> ${{eligibility.substring(0, 200)}}${{eligibility.length > 200 ? '...' : ''}}</p>
                            </div>
                        `;
                    }});
                    
                    resultsDiv.innerHTML = html;
                }} else {{
                    resultsDiv.innerHTML = `
                        <div class="no-results">
                            ❌ No schemes found for "${{query}}". 
                            <br><br>
                            <strong>Try keywords like:</strong> farmer, women, fisherman, loan, subsidy, education, rural, business, agriculture
                        </div>
                    `;
                }}
                
            }} catch (error) {{
                resultsDiv.innerHTML = '<div class="error">❌ Error occurred. Please try again.</div>';
                console.error('Search error:', error);
            }}
        }}
        
        function searchExample(query) {{
            document.getElementById('searchInput').value = query;
            searchSchemes();
        }}
        
        document.getElementById('searchInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                searchSchemes();
            }}
        }});
        
        // Load some sample results on page load
        window.onload = function() {{
            searchExample('farmer');
        }};
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def handle_search(self):
        """Handle search requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            query = request_data.get('query', '').strip()
            
            if not query:
                response = {"schemes": [], "message": "Please provide a search query"}
            else:
                schemes = simple_search(query, limit=5)
                response = {
                    "schemes": schemes,
                    "query": query,
                    "count": len(schemes)
                }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            error_response = {"schemes": [], "message": f"Search failed: {str(e)}"}
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def serve_health(self):
        """Health check endpoint"""
        response = {
            "status": "OK",
            "message": "Government Schemes Assistant is running!",
            "total_schemes": len(schemes_data)
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def serve_stats(self):
        """Stats endpoint"""
        response = {
            "total_schemes": len(schemes_data),
            "status": "active",
            "search_ready": len(schemes_data) > 0
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        return

def run_server():
    """Run the HTTP server"""
    print("🚀 Starting Government Schemes Assistant...")
    
    # Load CSV data
    load_csv_data()
    
    # Start server
    server = HTTPServer(('0.0.0.0', server_port), SchemeRequestHandler)
    print(f"✅ Server running on port {server_port}")
    print(f"📊 Loaded {len(schemes_data)} schemes")
    print(f"🌐 Access at: http://localhost:{server_port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\n🛑 Server stopping...")
        server.server_close()

if __name__ == "__main__":
    run_server()