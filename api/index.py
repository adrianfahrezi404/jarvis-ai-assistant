from flask import Flask, request, jsonify, send_from_directory
import sys
import os

# Menambahkan parent directory ke sys.path agar bisa import module lokal (jarvis_core dkk)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Path ke folder public (untuk serving file statis saat lokal)
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

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

# ── Halaman utama (serve index.html dari folder public/) ────
@app.route('/')
def serve_index():
    return send_from_directory(PUBLIC_DIR, 'index.html')

# ── Serve file statis lainnya (CSS, JS, dll) ────────────────
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(PUBLIC_DIR, filename)

# ── API Chat Endpoint ───────────────────────────────────────
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

if __name__ == '__main__':
    print(f"✓ Serving frontend dari: {PUBLIC_DIR}")
    print(f"✓ AI Handler: {handler_type or 'Offline'}")
    print(f"→ Buka http://127.0.0.1:5000 di browser Anda")
    app.run(port=5000, debug=True)