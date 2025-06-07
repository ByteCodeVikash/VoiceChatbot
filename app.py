import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <h1>🤖 Voice Assistant Working!</h1>
    <p>Railway deployment successful!</p>
    <script>console.log("App loaded successfully");</script>
    '''

@app.route('/health')
def health():
    return {"status": "healthy", "message": "App is running"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
