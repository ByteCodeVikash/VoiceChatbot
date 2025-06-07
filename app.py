import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Government Schemes Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .status { padding: 10px; background: #d4edda; border-radius: 5px; margin: 10px 0; }
            input { padding: 10px; width: 70%; margin: 10px 0; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Government Schemes Voice Assistant</h1>
            <div id="status" class="status">Connecting...</div>
            
            <div>
                <input type="text" id="messageInput" placeholder="Ask about government schemes..." />
                <button onclick="sendMessage()">Send</button>
            </div>
            
            <div id="responses" style="margin-top: 20px;"></div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script>
            const socket = io();
            
            socket.on('connect', function() {
                document.getElementById('status').innerHTML = '✅ Connected to Assistant';
            });
            
            socket.on('response', function(data) {
                const responsesDiv = document.getElementById('responses');
                responsesDiv.innerHTML += '<div style="background: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 5px;"><strong>Bot:</strong> ' + data.message + '</div>';
            });
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (message) {
                    const responsesDiv = document.getElementById('responses');
                    responsesDiv.innerHTML += '<div style="background: #007bff; color: white; padding: 10px; margin: 5px 0; border-radius: 5px;"><strong>You:</strong> ' + message + '</div>';
                    
                    socket.emit('user_message', {message: message});
                    input.value = '';
                }
            }
            
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return {"status": "healthy", "message": "Voice Assistant is running!"}

@socketio.on('connect')
def handle_connect():
    print('🔗 Client connected')
    emit('status', {'msg': 'Connected to Voice Assistant!'})

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Client disconnected')

@socketio.on('user_message')
def handle_message(data):
    message = data.get('message', '')
    print(f'📝 User message: {message}')
    
    # Simple response for now
    response = f"You asked about: {message}. Government schemes information will be provided here!"
    
    emit('response', {'message': response})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting server on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)