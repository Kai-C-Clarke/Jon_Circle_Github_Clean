# chat_routes.py - General Chat with Memory Storage
# Add this to app.py or import as a module

import os
import uuid
from datetime import datetime
from flask import session, request, jsonify, render_template
from openai import OpenAI

# Initialize DeepSeek client
deepseek_client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

def init_chat_db():
    """Initialize chat messages table"""
    db = get_db()
    cursor = db.cursor()
    
    # Read and execute migration
    with open('chat_migration.sql', 'r') as f:
        cursor.executescript(f.read())
    
    db.commit()

def get_chat_session_id():
    """Get or create a chat session ID"""
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())
    return session['chat_session_id']

def save_chat_message(session_id, role, message, tokens_used=0):
    """Save a chat message to database"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        INSERT INTO chat_messages (session_id, role, message, tokens_used)
        VALUES (?, ?, ?, ?)
    """, (session_id, role, message, tokens_used))
    
    db.commit()

def get_chat_history(session_id, limit=50):
    """Retrieve recent chat history for context"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT role, message, timestamp
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (session_id, limit))
    
    # Return in chronological order (oldest first)
    messages = cursor.fetchall()
    return [
        {
            'role': msg[0],
            'content': msg[1],
            'timestamp': msg[2]
        }
        for msg in reversed(messages)
    ]

def search_chat_history(query, limit=10):
    """Search past chat messages"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT role, message, timestamp, session_id
        FROM chat_messages
        WHERE message LIKE ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (f'%{query}%', limit))
    
    return [
        {
            'role': msg[0],
            'message': msg[1],
            'timestamp': msg[2],
            'session_id': msg[3]
        }
        for msg in cursor.fetchall()
    ]

# Flask Routes
@app.route('/chat')
def chat_page():
    """Render chat interface"""
    return render_template('chat.html')

@app.route('/api/chat/send', methods=['POST'])
def chat_send():
    """Send message and get AI response"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        session_id = get_chat_session_id()
        
        # Save user message
        save_chat_message(session_id, 'user', user_message)
        
        # Get conversation history for context
        history = get_chat_history(session_id, limit=20)
        
        # Build messages for DeepSeek
        messages = [
            {
                'role': 'system',
                'content': '''You are a thoughtful AI companion in The Circle, a memory preservation app. 
                
Your role is to:
- Have natural, friendly conversations
- Help users reflect on their experiences
- Ask thoughtful follow-up questions
- Remember context from the conversation
- Gently encourage users to share stories worth preserving

Keep responses conversational and warm, not formal or robotic.'''
            }
        ]
        
        # Add conversation history
        for msg in history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # Call DeepSeek API
        response = deepseek_client.chat.completions.create(
            model='deepseek-chat',
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        ai_message = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # Save AI response
        save_chat_message(session_id, 'assistant', ai_message, tokens_used)
        
        return jsonify({
            'message': ai_message,
            'timestamp': datetime.now().isoformat(),
            'tokens_used': tokens_used
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/history')
def chat_history():
    """Get chat history for current session"""
    session_id = get_chat_session_id()
    history = get_chat_history(session_id, limit=100)
    
    return jsonify({
        'messages': history,
        'session_id': session_id
    })

@app.route('/api/chat/search')
def chat_search():
    """Search chat history"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'results': []})
    
    results = search_chat_history(query, limit=20)
    
    return jsonify({'results': results})

@app.route('/api/chat/new-session', methods=['POST'])
def new_chat_session():
    """Start a new chat session"""
    session['chat_session_id'] = str(uuid.uuid4())
    
    return jsonify({
        'session_id': session['chat_session_id'],
        'message': 'New session started'
    })
