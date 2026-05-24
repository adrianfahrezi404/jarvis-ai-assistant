# ============================================================
#  JARVIS v2.0 — Core Logic (Modul 4 & 5)
#  Kelompok Intelligence created by A — JGU Teknik Informatika
# ============================================================

import re
import random
from datetime import datetime
from config import SINGER_POOL

# ── Session State (Modul 5 — Variabel Memori) ───────────────
session_state: dict = {
    "user_name": None,
}


def set_name(name: str) -> None:
    """Simpan nama user ke session state."""
    session_state["user_name"] = name.strip().title()


def get_name() -> str | None:
    """Ambil nama user dari session state."""
    return session_state.get("user_name")


def pick_random_singer() -> str:
    """Pilih satu penyanyi/personil secara acak (Modul 4)."""
    return random.choice(SINGER_POOL)


# ── Intent Patterns ─────────────────────────────────────────

_PATTERN_SET_NAME = re.compile(
    r"""
    (?:
        (?:nama\s*(?:saya|ku|aku|gue|gw)\s*(?:adalah|ialah|yaitu|:)?\s*)  # "nama saya adalah ..."
      | (?:(?:saya|aku|gue|gw)\s*(?:bernama|dipanggil|nama(?:ku|nya)?)\s*)  # "saya bernama ..."
      | (?:my\s+name\s+is\s+)                                               # "my name is ..."
      | (?:panggil\s+(?:saya|aku|gue|gw)\s+)                               # "panggil saya ..."
      | (?:call\s+me\s+)                                                    # "call me ..."
      | (?:i\s+am\s+)                                                       # "i am ..."
      | (?:namaku\s+)                                                        # "namaku ..."
    )
    ([A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ\s\-]*)
    """,
    re.IGNORECASE | re.VERBOSE,
)

_PATTERN_WHO_AM_I = re.compile(
    r"""
    (?:
        siapa\s+(?:saya|aku|gue|gw|nama\s*(?:saya|aku))
      | do\s+you\s+know\s+(?:me|who\s+i\s+am)
      | who\s+am\s+i
      | apakah\s+kamu\s+(?:kenal|tahu|tau)\s+(?:saya|aku|gue|gw)
      | kamu\s+(?:kenal|tahu|tau)\s+(?:saya|aku|gue|gw)
      | nama\s+(?:saya|aku)\s+(?:siapa|apa)
    )
    (?:\s+jarvis)?
    """,
    re.IGNORECASE | re.VERBOSE,
)

_PATTERN_SINGER = re.compile(
    r"""
    siapa\s+(?:penyanyi|musisi|artis|band|personil)\s+
    (?:favorit|kesukaan|fav|idola)\s*(?:ku|saya|aku|gue|gw)?
    |
    (?:penyanyi|musisi|artis|band|personil)\s+
    (?:favorit|kesukaan|fav|idola)\s*(?:ku|saya|aku|gue|gw)?\s+(?:siapa|apa)
    """,
    re.IGNORECASE | re.VERBOSE,
)


def detect_intent(text: str) -> dict:
    """
    Analisis teks input dan kembalikan dict hasil deteksi intent.

    Returns:
        {
          "intent": "set_name" | "who_am_i" | "singer" | "none",
          "name"  : str | None   (hanya untuk set_name)
        }
    """
    # 1. Cek perkenalan nama
    m = _PATTERN_SET_NAME.search(text)
    if m:
        extracted = m.group(1).strip()
        # Buang kata trailing seperti "jarvis", "dong", dsb.
        extracted = re.split(r'\s+(?:jarvis|dong|ya|yah|nih)$', extracted, flags=re.IGNORECASE)[0].strip()
        if extracted:
            return {"intent": "set_name", "name": extracted}

    # 2. Cek "siapa aku / do you know me"
    if _PATTERN_WHO_AM_I.search(text):
        return {"intent": "who_am_i", "name": None}

    # 3. Cek pertanyaan penyanyi favorit
    if _PATTERN_SINGER.search(text):
        return {"intent": "singer", "name": None}

    return {"intent": "none", "name": None}


def handle_local_intent(intent_result: dict) -> str | None:
    """
    Proses intent yang bisa dijawab secara lokal (tanpa Gemini).
    Kembalikan string jawaban, atau None jika harus diteruskan ke Gemini.
    """
    intent = intent_result["intent"]

    if intent == "set_name":
        name = intent_result["name"]
        set_name(name)
        return f"Hallo {get_name()}, nice to meet you! Senang berkenalan denganmu."

    if intent == "who_am_i":
        name = get_name()
        if name:
            return f"Tentu saja, kawan. Kamu adalah {name}. Identitasmu telah tercatat dalam sistemku."
        return (
            "Hmm, sepertinya kamu belum memperkenalkan dirimu kepadaku. "
            "Silakan katakan namamu terlebih dahulu."
        )

    if intent == "singer":
        singer = pick_random_singer()
        return (
            f"Berdasarkan analisis preferensiku, penyanyi favoritmu adalah "
            f"**{singer}**. Pilihan yang luar biasa!"
        )

    return None  # Teruskan ke Gemini


def handle_offline_fallback(text: str) -> str:
    """
    Jawaban sederhana untuk mode offline.
    Gunakan rule-based response dan jawaban umum.
    """
    text = text.strip()
    lower = text.lower()

    if not text:
        return "Silakan ajukan pertanyaan atau perkenalkan dirimu terlebih dahulu."

    # Salam dan sapaan
    if re.search(r"\b(hai|halo|hi|hey|selamat pagi|selamat siang|selamat malam)\b", lower):
        return random.choice([
            "Halo! Saya J.A.R.V.I.S offline, siap membantu sebisa saya.",
            "Hai! Mode offline aktif. Tanyakan sesuatu, saya akan jawab dengan kemampuan lokal."
        ])

    # Identitas asisten
    if re.search(r"\b(kamu siapa|siapa kamu|nama kamu|kenal kamu)\b", lower):
        return "Saya adalah J.A.R.V.I.S v2.0, asisten offline sederhana yang bisa menjawab beberapa pertanyaan."

    # Tanggal dan waktu
    if re.search(r"\b(tanggal|hari ini|hari ini tanggal|tanggal berapa)\b", lower):
        return datetime.now().strftime("Hari ini %A, %d %B %Y.")
    if re.search(r"\b(jam|waktu|sekarang pukul|pukul berapa)\b", lower):
        return datetime.now().strftime("Sekarang pukul %H:%M.")

    # Cuaca dan keadaan umum
    if "cuaca" in lower or "hujan" in lower or "panas" in lower or "dingin" in lower:
        return "Saya offline dan tidak bisa memeriksa cuaca aktual. Semoga harimu cerah meski di luar mungkin berbeda."

    # Perhitungan sederhana
    math_match = re.search(r"(-?\d+)\s*([+\-*/x])\s*(-?\d+)", lower)
    if math_match:
        a = int(math_match.group(1))
        op = math_match.group(2)
        b = int(math_match.group(3))
        try:
            if op == "+":
                result = a + b
            elif op == "-":
                result = a - b
            elif op in ("*", "x"):
                result = a * b
            else:
                result = a / b
            return f"Hasilnya adalah {result}."
        except Exception:
            return "Maaf, saya tidak dapat menghitung itu dengan benar."

    # Jawaban umum offline
    if re.search(r"\b(apa|siapa|di mana|dimana|kapan|mengapa|kenapa|bagaimana)\b", lower):
        return random.choice([
            "Itu pertanyaan bagus. Sebagai mode offline, saya dapat memberikan jawaban umum atau saran sederhana.",
            "Saya offline saat ini, jadi jawaban saya terbatas. Coba pertanyaan yang lebih sederhana atau mengenai nama dan penyanyi favorit."
        ])

    # Fallback random
    return random.choice([
        "Saya offline, namun saya tetap bisa menjawab beberapa hal sederhana.",
        "Mode offline aktif: saya dapat membantu dengan sapaan, tanggal, waktu, dan jawaban umum.",
        "Maaf, saya tidak tahu jawaban spesifiknya. Tapi saya masih siap membantu dengan topik sederhana."
    ])
