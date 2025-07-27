from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import google.generativeai as genai
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY', 'add you secret Key here'))
model = genai.GenerativeModel('models/gemini-1.5-flash')

# Store chat sessions
chat_sessions = {}

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('connect')
def handle_connect():
    session_id = str(uuid.uuid4())
    chat_sessions[request.sid] = {
        'session_id': session_id,
        'chat': model.start_chat(history=[]),
        'messages': []
    }
    emit('connected', {'session_id': session_id})
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in chat_sessions:
        del chat_sessions[request.sid]
    print(f'Client disconnected: {request.sid}')

@socketio.on('send_message')
def handle_message(data):
    try:
        user_message = data['message']
        session = chat_sessions.get(request.sid)
        
        if not session:
            emit('error', {'message': 'Session not found'})
            return
        
        # Add user message to session
        user_msg = {
            'id': str(uuid.uuid4()),
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        }
        session['messages'].append(user_msg)
        
        # Emit user message
        emit('message', user_msg)
        
        # Generate AI response
        chat = session['chat']
        response = chat.send_message(user_message)
        
        # Add AI response to session
        ai_msg = {
            'id': str(uuid.uuid4()),
            'role': 'assistant',
            'content': response.text,
            'timestamp': datetime.now().isoformat()
        }
        session['messages'].append(ai_msg)
        
        # Emit AI response
        emit('message', ai_msg)
        
    except Exception as e:
        emit('error', {'message': f'Error generating response: {str(e)}'})

@socketio.on('get_history')
def handle_get_history():
    session = chat_sessions.get(request.sid)
    if session:
        emit('chat_history', {'messages': session['messages']})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
