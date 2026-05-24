# ============================================================
#  JARVIS v2.0 — Speech Handler (STT & TTS)
#  Kelompok Intelligence created by A — JGU Teknik Informatika
# ============================================================

import os
import io
import threading
import tempfile
import time

import speech_recognition as sr
from gtts import gTTS

from config import TTS_LANGUAGE, TTS_SLOW, STT_LANGUAGE, STT_TIMEOUT, STT_PHRASE_TL

# ── pygame untuk playback (lebih stabil dari playsound di Windows) ──
try:
    import pygame
    pygame.mixer.init()
    _USE_PYGAME = True
except Exception:
    _USE_PYGAME = False

# ── Recognizer singleton ─────────────────────────────────────
_recognizer = sr.Recognizer()
_recognizer.energy_threshold = 300
_recognizer.dynamic_energy_threshold = True
_recognizer.pause_threshold = 0.8


# ════════════════════════════════════════════════════════════
#  TEXT-TO-SPEECH
# ════════════════════════════════════════════════════════════

def speak(text: str, on_done: callable = None):
    """
    Konversi teks ke suara menggunakan gTTS lalu putar secara async.
    on_done dipanggil setelah audio selesai diputar.
    """
    # Bersihkan teks dari simbol markdown agar TTS terdengar alami
    clean = _strip_markdown(text)

    # Guard: jangan panggil gTTS jika teks kosong
    if not clean or not clean.strip():
        print("[TTS] Teks kosong, skip TTS.", flush=True)
        if on_done:
            on_done()
        return

    def _worker():
        tmp_path = None
        try:
            tts = gTTS(text=clean, lang=TTS_LANGUAGE, slow=TTS_SLOW)
            # Simpan ke file temp
            with tempfile.NamedTemporaryFile(
                suffix=".mp3", delete=False
            ) as tmp:
                tmp_path = tmp.name
            tts.save(tmp_path)
            _play_audio(tmp_path)
        except Exception as exc:
            print(f"[TTS Error] {exc}", flush=True)
        finally:
            # Hapus file temp
            if tmp_path:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            if on_done:
                on_done()

    threading.Thread(target=_worker, daemon=True).start()


def _play_audio(path: str):
    """Putar file audio MP3."""
    if _USE_PYGAME:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)
    else:
        # Fallback: os.startfile (Windows) — tidak blocking
        os.startfile(path)
        time.sleep(3)


def _strip_markdown(text: str) -> str:
    """Hapus karakter markdown agar TTS tidak membacanya."""
    import re
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+\s?', '', text)
    text = re.sub(r'`+', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text.strip()


# ════════════════════════════════════════════════════════════
#  SPEECH-TO-TEXT
# ════════════════════════════════════════════════════════════

def listen(
    on_listening: callable = None,
    on_processing: callable = None,
    on_result: callable = None,
    on_error: callable = None,
):
    """
    Dengarkan mikrofon secara async menggunakan Google Speech Recognition.

    Callbacks:
        on_listening()        — saat mulai merekam
        on_processing()       — saat sedang memproses audio
        on_result(text: str)  — saat berhasil mengenali ucapan
        on_error(msg: str)    — saat terjadi error
    """
    def _worker():
        try:
            with sr.Microphone() as source:
                _recognizer.adjust_for_ambient_noise(source, duration=0.5)
                if on_listening:
                    on_listening()
                audio = _recognizer.listen(
                    source,
                    timeout=STT_TIMEOUT,
                    phrase_time_limit=STT_PHRASE_TL,
                )
            if on_processing:
                on_processing()
            text = _recognizer.recognize_google(audio, language=STT_LANGUAGE)
            if on_result:
                on_result(text)
        except sr.WaitTimeoutError:
            if on_error:
                on_error("Tidak ada suara yang terdeteksi. Coba lagi.")
        except sr.UnknownValueError:
            if on_error:
                on_error("Maaf, ucapanmu tidak dapat dikenali. Coba lagi.")
        except sr.RequestError as exc:
            if on_error:
                on_error(f"Gagal terhubung ke layanan Speech Recognition: {exc}")
        except Exception as exc:
            if on_error:
                on_error(f"Error tidak terduga: {exc}")

    threading.Thread(target=_worker, daemon=True).start()


def check_microphone() -> tuple[bool, str]:
    """
    Cek apakah mikrofon tersedia.
    Returns (ok: bool, message: str)
    """
    try:
        mics = sr.Microphone.list_microphone_names()
        if not mics:
            return False, "Tidak ada mikrofon yang terdeteksi."
        return True, f"Mikrofon tersedia: {mics[0]}"
    except Exception as exc:
        return False, f"Error cek mikrofon: {exc}"
