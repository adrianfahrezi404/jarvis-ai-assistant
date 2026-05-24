# ============================================================
#  JARVIS v2.0 — Main GUI Application
#  Kelompok Intelligence created by A — JGU Teknik Informatika
#  Mata Kuliah : Artificial Intelligence
#  Dosen       : Anindya Ananda Hapsari, S.ST., MIT.
# ============================================================

import tkinter as tk
from tkinter import scrolledtext, font as tkfont
import threading
import math
import time

from config import (
    WINDOW_TITLE, WINDOW_SIZE, WINDOW_MIN,
    APP_NAME, TEAM_NAME, UNIVERSITY,
    GEMINI_ENABLED, GROQ_ENABLED,
)
from jarvis_core import detect_intent, handle_local_intent, handle_offline_fallback
from gemini_handler import GeminiHandler
from groq_handler import GroqHandler
from speech_handler import speak, listen, check_microphone

# ── Colour Palette (Iron Man / JARVIS dark theme) ───────────
C_BG          = "#050d1a"   # deep navy black
C_PANEL       = "#071828"   # slightly lighter panel
C_ACCENT      = "#00d4ff"   # electric cyan
C_ACCENT2     = "#0066ff"   # deep blue
C_GOLD        = "#ffc200"   # arc-reactor amber
C_TEXT        = "#cce8ff"   # soft blue-white text
C_TEXT_DIM    = "#4a7fa5"   # dimmed text
C_USER_BG     = "#0a2540"   # user bubble
C_BOT_BG      = "#071d35"   # bot bubble
C_BORDER      = "#0d3a5c"   # border colour
C_GREEN       = "#00ff88"   # status green
C_RED         = "#ff4466"   # status red
C_ORANGE      = "#ff8c00"   # warning orange

FONT_FAMILY   = "Consolas"  # monospace gives a "techy" feel


# ════════════════════════════════════════════════════════════
#  ARC REACTOR CANVAS WIDGET
# ════════════════════════════════════════════════════════════

class ArcReactor(tk.Canvas):
    """Animated arc-reactor style spinning widget."""

    def __init__(self, master, size=110, **kwargs):
        super().__init__(
            master, width=size, height=size,
            bg=C_BG, highlightthickness=0, **kwargs
        )
        self._size   = size
        self._cx     = size / 2
        self._cy     = size / 2
        self._angle  = 0
        self._pulse  = 0.0
        self._pulse_dir = 1
        self._running = True
        self._state   = "idle"   # idle | listening | thinking | speaking
        self._draw()
        self._animate()

    def set_state(self, state: str):
        self._state = state

    def _get_color(self):
        states = {
            "listening" : C_GREEN,
            "thinking"  : C_GOLD,
            "speaking"  : C_ACCENT,
            "idle"      : C_ACCENT2,
        }
        return states.get(self._state, C_ACCENT2)

    def _draw(self):
        self.delete("all")
        cx, cy, r = self._cx, self._cy, self._size / 2 - 4
        col = self._get_color()

        # Outer glow ring
        glow = 4 + 3 * self._pulse
        self.create_oval(
            cx - r - glow, cy - r - glow,
            cx + r + glow, cy + r + glow,
            outline=col, width=1,
            fill=""
        )

        # Main ring
        self.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline=col, width=2, fill=C_BG
        )

        # Spinning arc segments (3 arcs, 120° apart)
        arc_r = r - 10
        for i in range(3):
            start_angle = self._angle + i * 120
            self.create_arc(
                cx - arc_r, cy - arc_r,
                cx + arc_r, cy + arc_r,
                start=start_angle, extent=70,
                outline=col, width=2,
                style=tk.ARC
            )

        # Inner hexagon via lines
        hex_r = r - 22
        points = []
        for i in range(6):
            a = math.radians(60 * i + self._angle * 0.5)
            points.extend([cx + hex_r * math.cos(a), cy + hex_r * math.sin(a)])
        self.create_polygon(
            points, outline=col, fill="", width=1
        )

        # Centre glow dot
        dot_r = 8 + 4 * self._pulse
        self.create_oval(
            cx - dot_r, cy - dot_r,
            cx + dot_r, cy + dot_r,
            fill=col, outline=""
        )

    def _animate(self):
        if not self._running:
            return
        speed = {"idle": 0.8, "listening": 3.0, "thinking": 5.0, "speaking": 2.5}
        self._angle = (self._angle + speed.get(self._state, 1.0)) % 360
        self._pulse += 0.05 * self._pulse_dir
        if self._pulse >= 1.0:
            self._pulse_dir = -1
        elif self._pulse <= 0.0:
            self._pulse_dir = 1
        self._draw()
        self.after(30, self._animate)

    def destroy(self):
        self._running = False
        super().destroy()


# ════════════════════════════════════════════════════════════
#  MAIN APPLICATION WINDOW
# ════════════════════════════════════════════════════════════

class JarvisApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN)
        self.configure(bg=C_BG)
        self.resizable(True, True)

        # Handler setup: Prioritas Groq > Gemini > Offline
        self._handler = None
        self._handler_type = None
        self._handler_ok = False
        self._handler_error = ""

        # Try Groq first (recommended)
        if GROQ_ENABLED:
            try:
                self._handler = GroqHandler()
                self._handler_type = "Groq"
                self._handler_ok = True
            except ValueError as exc:
                self._handler = None
                self._handler_ok = False
                self._handler_error = str(exc)
        
        # Try Gemini as fallback
        if not self._handler_ok and GEMINI_ENABLED:
            try:
                self._handler = GeminiHandler()
                self._handler_type = "Gemini"
                self._handler_ok = True
            except ValueError as exc:
                self._handler = None
                self._handler_ok = False
                self._handler_error = str(exc)
        
        # If no online handler available, use offline mode
        if not self._handler_ok:
            self._handler = None
            self._handler_type = None
            self._handler_error = "Mode offline lokal aktif."

        self._is_busy = False   # prevent overlapping requests

        self._build_fonts()
        self._build_ui()
        self._show_welcome()

        # Check microphone availability
        self.after(500, self._check_mic)

    # ── Fonts ────────────────────────────────────────────────

    def _build_fonts(self):
        self.font_title  = tkfont.Font(family=FONT_FAMILY, size=16, weight="bold")
        self.font_sub    = tkfont.Font(family=FONT_FAMILY, size=9)
        self.font_chat   = tkfont.Font(family=FONT_FAMILY, size=11)
        self.font_label  = tkfont.Font(family=FONT_FAMILY, size=10, weight="bold")
        self.font_status = tkfont.Font(family=FONT_FAMILY, size=9)
        self.font_btn    = tkfont.Font(family=FONT_FAMILY, size=10, weight="bold")
        self.font_input  = tkfont.Font(family=FONT_FAMILY, size=11)

    # ── UI Layout ────────────────────────────────────────────

    def _build_ui(self):
        # ── Top header ──────────────────────────────────────
        header = tk.Frame(self, bg=C_PANEL, pady=0)
        header.pack(fill=tk.X, side=tk.TOP)

        # Thin accent line at very top
        tk.Frame(header, bg=C_ACCENT, height=2).pack(fill=tk.X)

        inner_header = tk.Frame(header, bg=C_PANEL, padx=20, pady=12)
        inner_header.pack(fill=tk.X)

        # Arc reactor (left)
        self._reactor = ArcReactor(inner_header, size=90)
        self._reactor.pack(side=tk.LEFT, padx=(0, 16))

        # Title block (centre)
        title_frame = tk.Frame(inner_header, bg=C_PANEL)
        title_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        tk.Label(
            title_frame, text=APP_NAME,
            font=self.font_title, fg=C_ACCENT, bg=C_PANEL
        ).pack(anchor=tk.W)

        tk.Label(
            title_frame,
            text=f"Just A Rather Very Intelligent System  •  {TEAM_NAME}",
            font=self.font_sub, fg=C_TEXT_DIM, bg=C_PANEL
        ).pack(anchor=tk.W)

        tk.Label(
            title_frame,
            text=f"Teknik Informatika  •  {UNIVERSITY}  •  Project B UTS AI",
            font=self.font_sub, fg=C_TEXT_DIM, bg=C_PANEL
        ).pack(anchor=tk.W)

        # Status indicator (right)
        status_frame = tk.Frame(inner_header, bg=C_PANEL)
        status_frame.pack(side=tk.RIGHT, anchor=tk.N, padx=(0, 4))

        tk.Label(
            status_frame, text="STATUS",
            font=self.font_status, fg=C_TEXT_DIM, bg=C_PANEL
        ).pack()

        self._status_dot = tk.Label(
            status_frame, text="●", font=("Consolas", 22),
            fg=C_GREEN, bg=C_PANEL
        )
        self._status_dot.pack()

        self._status_label = tk.Label(
            status_frame, text="ONLINE",
            font=self.font_status, fg=C_GREEN, bg=C_PANEL
        )
        self._status_label.pack()

        # Thin border bottom of header
        tk.Frame(self, bg=C_BORDER, height=1).pack(fill=tk.X)

        # ── Chat area ───────────────────────────────────────
        chat_frame = tk.Frame(self, bg=C_BG, padx=16, pady=8)
        chat_frame.pack(fill=tk.BOTH, expand=True)

        # Tag-based scrolled text for coloured bubbles
        self._chat = scrolledtext.ScrolledText(
            chat_frame,
            font=self.font_chat,
            bg=C_BG,
            fg=C_TEXT,
            wrap=tk.WORD,
            bd=0,
            highlightthickness=0,
            state=tk.DISABLED,
            padx=6,
            pady=6,
        )
        self._chat.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for styled bubbles
        self._chat.tag_configure(
            "user_label",
            foreground=C_GOLD,
            font=tkfont.Font(family=FONT_FAMILY, size=9, weight="bold"),
            spacing1=10,
        )
        self._chat.tag_configure(
            "user_msg",
            foreground=C_TEXT,
            background=C_USER_BG,
            lmargin1=20, lmargin2=20, rmargin=80,
            spacing3=4,
        )
        self._chat.tag_configure(
            "bot_label",
            foreground=C_ACCENT,
            font=tkfont.Font(family=FONT_FAMILY, size=9, weight="bold"),
            spacing1=10,
        )
        self._chat.tag_configure(
            "bot_msg",
            foreground=C_TEXT,
            background=C_BOT_BG,
            lmargin1=20, lmargin2=20, rmargin=80,
            spacing3=4,
        )
        self._chat.tag_configure(
            "system_msg",
            foreground=C_TEXT_DIM,
            font=tkfont.Font(family=FONT_FAMILY, size=9, slant="italic"),
            justify=tk.CENTER,
            spacing1=6, spacing3=6,
        )
        self._chat.tag_configure(
            "error_msg",
            foreground=C_RED,
            font=tkfont.Font(family=FONT_FAMILY, size=9),
            spacing1=4, spacing3=4,
        )

        # ── Bottom input area ───────────────────────────────
        tk.Frame(self, bg=C_BORDER, height=1).pack(fill=tk.X)

        bottom = tk.Frame(self, bg=C_PANEL, padx=12, pady=10)
        bottom.pack(fill=tk.X, side=tk.BOTTOM)

        # Mic button (left)
        self._mic_btn = tk.Button(
            bottom,
            text="🎙",
            font=("Segoe UI Emoji", 18),
            bg=C_ACCENT2,
            fg="white",
            activebackground=C_ACCENT,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            width=3,
            command=self._on_mic_press,
        )
        self._mic_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Text input
        input_frame = tk.Frame(bottom, bg=C_BORDER, padx=1, pady=1)
        input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._input_var = tk.StringVar()
        self._input_entry = tk.Entry(
            input_frame,
            textvariable=self._input_var,
            font=self.font_input,
            bg=C_PANEL,
            fg=C_TEXT,
            insertbackground=C_ACCENT,
            relief=tk.FLAT,
            bd=6,
        )
        self._input_entry.pack(fill=tk.X)
        self._input_entry.bind("<Return>", self._on_send)
        self._input_entry.bind("<KP_Enter>", self._on_send)

        # Send button (right)
        self._send_btn = tk.Button(
            bottom,
            text="SEND  ▶",
            font=self.font_btn,
            bg=C_ACCENT,
            fg=C_BG,
            activebackground=C_ACCENT2,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=14, pady=6,
            command=self._on_send,
        )
        self._send_btn.pack(side=tk.LEFT, padx=(8, 0))

        # Clear button
        tk.Button(
            bottom,
            text="CLEAR",
            font=self.font_btn,
            bg=C_BG,
            fg=C_TEXT_DIM,
            activebackground=C_BORDER,
            activeforeground=C_TEXT,
            relief=tk.FLAT,
            cursor="hand2",
            padx=10, pady=6,
            command=self._clear_chat,
        ).pack(side=tk.LEFT, padx=(4, 0))

        # ── Bottom thin accent line ──────────────────────────
        tk.Frame(self, bg=C_ACCENT2, height=2).pack(fill=tk.X, side=tk.BOTTOM)

    # ── Welcome message ──────────────────────────────────────

    def _show_welcome(self):
        self._append_system(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        self._append_system(f"  {APP_NAME}  —  SISTEM AKTIF")
        self._append_system(f"  Dikembangkan oleh {TEAM_NAME}  •  {UNIVERSITY}")
        self._append_system(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        if not self._handler_ok:
            self._append_error(
                f"⚠ Mode offline aktif. AI online dinonaktifkan."
            )
            self._append_error(
                "  Saya hanya dapat menjawab intent lokal: nama, siapa aku, penyanyi favorit."
            )
            if self._handler_error:
                self._append_error(f"  Error: {self._handler_error}")
        else:
            self._append_bot(
                f"Selamat datang. Saya J.A.R.V.I.S v2.0 dengan {self._handler_type} AI, "
                f"siap melayani Anda. Silakan perkenalkan diri Anda atau ajukan pertanyaan."
            )

    # ── Mic check ───────────────────────────────────────────

    def _check_mic(self):
        ok, msg = check_microphone()
        if not ok:
            self._append_error(f"⚠ Mikrofon: {msg}")
            self._mic_btn.config(state=tk.DISABLED, bg=C_TEXT_DIM)

    # ── Event Handlers ───────────────────────────────────────

    def _on_send(self, event=None):
        text = self._input_var.get().strip()
        if not text or self._is_busy:
            return
        self._input_var.set("")
        self._process_input(text)

    def _on_mic_press(self):
        if self._is_busy:
            return
        self._set_busy(True)
        self._set_status("LISTENING", C_GREEN)
        self._reactor.set_state("listening")
        self._mic_btn.config(bg=C_GREEN, fg=C_BG)
        self._append_system("🎙 Mendengarkan…")

        listen(
            on_listening  = lambda: None,
            on_processing = self._on_stt_processing,
            on_result     = self._on_stt_result,
            on_error      = self._on_stt_error,
        )

    def _on_stt_processing(self):
        self.after(0, lambda: (
            self._set_status("PROCESSING", C_GOLD),
            self._reactor.set_state("thinking"),
        ))

    def _on_stt_result(self, text: str):
        self.after(0, lambda: self._process_input(text, from_voice=True))

    def _on_stt_error(self, msg: str):
        self.after(0, lambda: (
            self._append_error(f"⚠ STT: {msg}"),
            self._set_busy(False),
            self._set_status("ONLINE", C_GREEN),
            self._reactor.set_state("idle"),
            self._mic_btn.config(bg=C_ACCENT2, fg="white"),
        ))

    # ── Core Processing Pipeline ─────────────────────────────

    def _process_input(self, text: str, from_voice: bool = False):
        self._set_busy(True)
        self._append_user(text)
        self._set_status("THINKING", C_GOLD)
        self._reactor.set_state("thinking")

        def _worker():
            try:
                # 1. Try local intent first (Modul 4 & 5)
                intent = detect_intent(text)
                print(f"[DEBUG] Intent: {intent}", flush=True)
                answer = handle_local_intent(intent)

                # 2. Fall back to online AI handler (Groq or Gemini)
                if answer is None:
                    if self._handler_ok and self._handler:
                        print(f"[DEBUG] Mengirim ke {self._handler_type}: '{text}'", flush=True)
                        answer = self._handler.ask(text)
                        print(f"[DEBUG] Response dari {self._handler_type}: '{answer}'", flush=True)
                    else:
                        print("[DEBUG] Mode offline, gunakan fallback lokal.", flush=True)
                        answer = handle_offline_fallback(text)

                # Ensure answer is never None or empty
                if not answer or not answer.strip():
                    print(f"[DEBUG] Answer kosong, gunakan fallback.", flush=True)
                    answer = "Maaf, saya tidak dapat memahami pertanyaan Anda. Silakan coba lagi."
                    
            except Exception as e:
                answer = f"Terjadi kesalahan: {str(e)[:100]}"
                print(f"[ERROR] Worker thread exception: {e}", flush=True)
            
            # Always deliver response, even if there was an error
            self.after(0, lambda a=answer: self._deliver_response(a))

        threading.Thread(target=_worker, daemon=True).start()

    def _deliver_response(self, answer: str):
        try:
            self._append_bot(answer)
            self._set_status("SPEAKING", C_ACCENT)
            self._reactor.set_state("speaking")
            self._mic_btn.config(bg=C_ACCENT, fg=C_BG)

            def _after_speak():
                try:
                    self.after(0, lambda: (
                        self._set_busy(False),
                        self._set_status("ONLINE", C_GREEN),
                        self._reactor.set_state("idle"),
                        self._mic_btn.config(bg=C_ACCENT2, fg="white"),
                    ))
                except Exception as e:
                    print(f"[ERROR] _after_speak: {e}", flush=True)

            speak(answer, on_done=_after_speak)
        except Exception as e:
            print(f"[ERROR] _deliver_response: {e}", flush=True)
            self._set_busy(False)

    # ── Chat Display Helpers ─────────────────────────────────

    def _append_user(self, text: str):
        self._chat.config(state=tk.NORMAL)
        self._chat.insert(tk.END, "  YOU\n", "user_label")
        self._chat.insert(tk.END, f"  {text}\n", "user_msg")
        self._chat.config(state=tk.DISABLED)
        self._chat.see(tk.END)

    def _append_bot(self, text: str):
        # Strip markdown bold for display (keep it clean)
        clean = text.replace("**", "")
        self._chat.config(state=tk.NORMAL)
        self._chat.insert(tk.END, "  J.A.R.V.I.S\n", "bot_label")
        self._chat.insert(tk.END, f"  {clean}\n", "bot_msg")
        self._chat.config(state=tk.DISABLED)
        self._chat.see(tk.END)

    def _append_system(self, text: str):
        self._chat.config(state=tk.NORMAL)
        self._chat.insert(tk.END, f"{text}\n", "system_msg")
        self._chat.config(state=tk.DISABLED)
        self._chat.see(tk.END)

    def _append_error(self, text: str):
        self._chat.config(state=tk.NORMAL)
        self._chat.insert(tk.END, f"{text}\n", "error_msg")
        self._chat.config(state=tk.DISABLED)
        self._chat.see(tk.END)

    def _clear_chat(self):
        self._chat.config(state=tk.NORMAL)
        self._chat.delete("1.0", tk.END)
        self._chat.config(state=tk.DISABLED)
        self._show_welcome()

    # ── Status Helpers ───────────────────────────────────────

    def _set_status(self, label: str, color: str):
        self._status_dot.config(fg=color)
        self._status_label.config(text=label, fg=color)

    def _set_busy(self, busy: bool):
        self._is_busy = busy
        state = tk.DISABLED if busy else tk.NORMAL
        self._send_btn.config(state=state)
        self._input_entry.config(state=state)
        if not busy:
            self._mic_btn.config(bg=C_ACCENT2, fg="white")


# ════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = JarvisApp()
    app.mainloop()
