# ============================================================
#  JARVIS v2.0 — Groq API Handler
#  Kelompok Intelligence created by A — JGU Teknik Informatika
# ============================================================

from groq import Groq

from config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_MAX_OUTPUT_TOKENS,
    GROQ_TEMPERATURE,
    TEAM_NAME,
    UNIVERSITY,
    MEMBERS,
)
from jarvis_core import get_name

# ── System Prompt ────────────────────────────────────────────
_BASE_SYSTEM_PROMPT = (
    f"Kamu adalah J.A.R.V.I.S v2.0, sebuah asisten AI cerdas yang dikembangkan oleh "
    f"tim mahasiswa bernama \"{TEAM_NAME}\" dari jurusan Teknik Informatika, {UNIVERSITY}. "
    f"Anggota tim: {MEMBERS[0]}, {MEMBERS[1]}, {MEMBERS[2]}, dan {MEMBERS[3]}. "
    "Kepribadian & Gaya Bahasa: "
    "Gunakan Bahasa Indonesia yang formal namun ramah, dengan sentuhan futuristik "
    "seperti asisten cerdas dalam film Iron Man. "
    "Jawaban HARUS singkat dan padat, maksimal 2-3 kalimat, agar nyaman didengar saat "
    "dikonversi menjadi suara (TTS). "
    "JANGAN gunakan markdown formatting seperti **, *, atau # karena output dibacakan langsung. "
    "Selalu siap menjelaskan bahwa kamu dibuat oleh tim tersebut jika ditanya penciptamu. "
    "Jika tidak tahu jawaban, akui dengan elegan dan tawarkan bantuan lain."
)


# ── Groq Client ──────────────────────────────────────────────

class GroqHandler:
    """
    Wrapper untuk Groq SDK.
    Menggunakan chat history untuk konteks percakapan.
    """

    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY belum diset! Dapatkan API key di "
                "https://console.groq.com/keys dan isi di file .env"
            )
        # Inisialisasi client
        self._client = Groq(api_key=GROQ_API_KEY)
        self._history: list[dict] = []

    def reset_chat(self):
        """Reset sesi percakapan (bersihkan history)."""
        self._history = []

    def ask(self, user_text: str) -> str:
        """
        Kirim pesan ke Groq dan kembalikan teks jawaban.
        Menyertakan nama user dalam context prefix jika sudah dikenali.
        """
        try:
            # Inject nama user terkini ke dalam context
            name = get_name()
            context_prefix = f"[Context sistem: Nama user adalah {name}] " if name else ""
            full_text = context_prefix + user_text

            # Tambah pesan user ke history
            self._history.append({
                "role": "user",
                "content": full_text
            })

            # Kirim ke Groq dengan system instruction & history
            response = self._client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": _BASE_SYSTEM_PROMPT},
                    *self._history
                ],
                max_tokens=GROQ_MAX_OUTPUT_TOKENS,
                temperature=GROQ_TEMPERATURE,
            )

            # Ambil jawaban — cek None dan empty string
            raw = None
            if response.choices and response.choices[0].message:
                raw = response.choices[0].message.content
            
            if raw and raw.strip():
                answer = raw.strip()
            else:
                print(f"[GROQ WARNING] Response kosong dari model {GROQ_MODEL}", flush=True)
                answer = "Maaf, saya tidak dapat memproses permintaan tersebut. Silakan coba lagi."

            # Simpan jawaban bot ke history
            self._history.append({
                "role": "assistant",
                "content": answer
            })

            # Batasi history agar request tetap ringan (simpan 6 turn terakhir)
            if len(self._history) > 12:
                self._history = self._history[-12:]

            return answer

        except Exception as exc:
            err_str = str(exc)
            
            # Rate limit / quota exceeded
            if "429" in err_str or "rate" in err_str.lower() or "quota" in err_str.lower():
                return (
                    "Maaf, saya sedang dalam antrian. "
                    "Silakan tunggu beberapa saat dan coba lagi."
                )
            
            # Invalid model or unsupported model
            if "model" in err_str.lower() and ("invalid" in err_str.lower() or "not found" in err_str.lower() or "unsupported" in err_str.lower()):
                return (
                    "Maaf, model Groq yang dikonfigurasi tidak valid. "
                    "Periksa nilai GROQ_MODEL di .env dan gunakan model yang didukung."
                )

            # API key issues
            if "api" in err_str.lower() or "401" in err_str or "403" in err_str:
                return (
                    "Maaf, API key tidak valid atau belum diset dengan benar. "
                    "Periksa file .env dan pastikan GROQ_API_KEY sudah diisi."
                )
            
            # Network / connection issues
            if "connection" in err_str.lower() or "network" in err_str.lower():
                return (
                    "Maaf, tidak dapat terhubung ke layanan Groq. "
                    "Periksa koneksi internet Anda dan coba lagi."
                )
            
            # General error
            return (
                f"Maaf, terjadi gangguan pada sistem komunikasi saya. "
                f"Error: {err_str[:80]}"
            )
