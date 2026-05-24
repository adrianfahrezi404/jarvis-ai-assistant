from flask import Flask, request, jsonify
import sys
import os

# Menambahkan parent directory ke sys.path agar bisa import module lokal (jarvis_core dkk)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis_core import detect_intent, handle_local_intent, handle_offline_fallback
from config import GROQ_ENABLED, GEMINI_ENABLED

# Load Handler
handler = None
handler_type = None

if GROQ_ENABLED:
    try:
        from groq_handler import GroqHandler
        handler = GroqHandler()
        handler_type = "Groq"
    except Exception as e:
        print("Groq Init Error:", e)

if not handler and GEMINI_ENABLED:
    try:
        from gemini_handler import GeminiHandler
        handler = GeminiHandler()
        handler_type = "Gemini"
    except Exception as e:
        print("Gemini Init Error:", e)

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400

    text = data['message']
    
    try:
        # 1. Cek intent lokal (Modul 4 & 5)
        intent = detect_intent(text)
        answer = handle_local_intent(intent)
        
        # 2. Jika tidak ada intent lokal, gunakan LLM Online
        if answer is None:
            if handler:
                answer = handler.ask(text)
            else:
                answer = handle_offline_fallback(text)
                
        if not answer or not answer.strip():
            answer = "Maaf, saya tidak dapat memahami permintaan Anda saat ini."
            
        return jsonify({
            "reply": answer,
            "handler": handler_type if handler else "Offline"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel membutuhkan object `app` di global scope file ini
