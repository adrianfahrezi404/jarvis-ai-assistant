# ============================================================
#  JARVIS v2.0 — Configuration
#  Kelompok Intelligence created by A — JGU Teknik Informatika
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# ── Gemini API ──────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
_gemini_enabled_raw = os.getenv("GEMINI_ENABLED")
if _gemini_enabled_raw is None:
    GEMINI_ENABLED = bool(GEMINI_API_KEY)
else:
    GEMINI_ENABLED = _gemini_enabled_raw.strip().lower() in ("1", "true", "yes")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "120"))
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.4"))
GEMINI_TOP_P = float(os.getenv("GEMINI_TOP_P", "0.95"))

# ── Groq API ────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
_groq_enabled_raw = os.getenv("GROQ_ENABLED")
if _groq_enabled_raw is None:
    GROQ_ENABLED = bool(GROQ_API_KEY)
else:
    GROQ_ENABLED = _groq_enabled_raw.strip().lower() in ("1", "true", "yes")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_MAX_OUTPUT_TOKENS = int(os.getenv("GROQ_MAX_OUTPUT_TOKENS", "256"))
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.4"))

# ── App Identity ────────────────────────────────────────────
APP_NAME    = "J.A.R.V.I.S v2.0"
TEAM_NAME   = "Intelligence created by A"
UNIVERSITY  = "Jakarta Global University (JGU)"
MEMBERS     = [
    "Abdul Rosid (Ketua)",
    "Andira Septiani",
    "Andini Maulidiah",
    "Adrian Dwi Fahrezi Rizki",
]

# ── Random Singer Pool (Modul 4) ────────────────────────────
# Personil Hindia / .Feast + Sheila on 7
SINGER_POOL = [
    # Hindia / .Feast
    "Baskara Putra",
    "Rayhan Noor",
    "Ican Harem",
    "Khomeini Ramli",
    # Sheila on 7
    "Duta",
    "Eross",
    "Adam",
]

# ── TTS / STT ───────────────────────────────────────────────
TTS_LANGUAGE   = "id"          # Bahasa Indonesia
TTS_SLOW       = False
STT_LANGUAGE   = "id-ID"       # Google STT language
STT_TIMEOUT    = 5             # seconds to wait for speech start
STT_PHRASE_TL  = 10            # max seconds for a single phrase

# ── GUI ─────────────────────────────────────────────────────
WINDOW_TITLE  = "J.A.R.V.I.S v2.0 — Intelligence created by A"
WINDOW_SIZE   = "900x680"
WINDOW_MIN    = (720, 560)
