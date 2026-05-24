# ============================================================
#  JARVIS v2.0 — Gemini API Handler (google-genai SDK baru)
#  Kelompok Intelligence created by A — JGU Teknik Informatika
# ============================================================

from google import genai
from google.genai import errors, types

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_TEMPERATURE,
    GEMINI_TOP_P,
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


# ── Gemini Client ────────────────────────────────────────────

class GeminiHandler:
    """
    Wrapper untuk google-genai SDK (generasi terbaru).
    Menggunakan chat session dengan history untuk konteks percakapan.
    """

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY belum diset! Salin .env.example ke .env "
                "dan isi dengan API key dari https://aistudio.google.com/app/apikey"
            )
        # Inisialisasi client
        self._client = genai.Client(api_key=GEMINI_API_KEY)
        self._history: list[types.Content] = []

    def reset_chat(self):
        """Reset sesi percakapan (bersihkan history)."""
        self._history = []

    def ask(self, user_text: str) -> str:
        """
        Kirim pesan ke Gemini dan kembalikan teks jawaban.
        Menyertakan nama user dalam context prefix jika sudah dikenali.
        """
        try:
            # Inject nama user terkini ke dalam context
            name = get_name()
            context_prefix = f"[Context sistem: Nama user adalah {name}] " if name else ""
            full_text = context_prefix + user_text

            # Tambah pesan user ke history
            self._history.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=full_text)]
                )
            )

            # Kirim ke Gemini dengan system instruction & history
            response = self._client.models.generate_content(
                model=GEMINI_MODEL,
                contents=self._history,
                config=types.GenerateContentConfig(
                    system_instruction=_BASE_SYSTEM_PROMPT,
                    max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
                    temperature=GEMINI_TEMPERATURE,
                    top_p=GEMINI_TOP_P,
                ),
            )

            answer = response.text.strip() if response.text else "Maaf, saya tidak dapat memproses permintaan tersebut."

            # Simpan jawaban bot ke history
            self._history.append(
                types.Content(
                    role="model",
                    parts=[types.Part(text=answer)]
                )
            )

            # Batasi history agar request tetap ringan (simpan 6 turn terakhir)
            if len(self._history) > 12:
                self._history = self._history[-12:]

            return answer

        except errors.ClientError as exc:
            err_str = str(exc)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str.upper():
                return (
                    "Maaf, kuota Gemini API Anda telah habis. "
                    "Periksa plan/billing di Google Cloud dan coba lagi nanti."
                )
            if "API_KEY" in err_str.upper() or "401" in err_str or "403" in err_str:
                return (
                    "Maaf, API key tidak valid atau belum diset dengan benar. "
                    "Periksa file .env dan pastikan GEMINI_API_KEY sudah diisi."
                )
            return (
                "Maaf, terjadi gangguan pada sistem komunikasi saya. "
                "Mohon periksa koneksi internet Anda dan coba lagi."
            )
        except Exception as exc:
            err_str = str(exc)
            if "API_KEY" in err_str.upper() or "401" in err_str or "403" in err_str:
                return (
                    "Maaf, API key tidak valid atau belum diset dengan benar. "
                    "Periksa file .env dan pastikan GEMINI_API_KEY sudah diisi."
                )
            return (
                "Maaf, terjadi gangguan pada sistem komunikasi saya. "
                "Mohon periksa koneksi internet Anda dan coba lagi."
            )
