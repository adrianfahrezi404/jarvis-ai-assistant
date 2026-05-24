# J.A.R.V.I.S v2.0 — README

> **Project B — UTS Artificial Intelligence**  
> Kelompok 1 — *Intelligence created by A*  
> Jurusan Teknik Informatika, Jakarta Global University (JGU)  
> Dosen: Anindya Ananda Hapsari, S.ST., MIT.

---

## 👥 Tim Pengembang

| No | Nama | Peran |
|----|------|-------|
| 1  | Abdul Rosid | Ketua |
| 2  | Andira Septiani | Anggota |
| 3  | Andini Maulidiah | Anggota |
| 4  | Adrian Dwi Fahrezi Rizki | Anggota |

---

## 🚀 Cara Menjalankan

### 1. Install Python
Pastikan Python **3.10+** sudah terinstall.  
Download: https://www.python.org/downloads/

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Catatan PyAudio (Windows):**  
> Jika `pyaudio` gagal install, gunakan cara ini:
> ```bash
>  
> ```
> Atau download file `.whl` dari: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

### 3. Konfigurasi API Key

```bash
# Salin template
copy .env.example .env
```

Buka file `.env` dan isi dengan Gemini API key kamu:
```
GEMINI_API_KEY=AIza...
```
Dapatkan key gratis di: https://aistudio.google.com/app/apikey

### 4. Jalankan Aplikasi

```bash
python main.py
```

---

## 🎯 Fitur Utama

| Fitur | Modul | Cara Uji |
|-------|-------|----------|
| **Memori Nama** | Modul 5 | Ucapkan: *"My name is Adrian"* |
| **Pengenalan Identitas** | Modul 5 | Tanya: *"Do you know me?"* |
| **Penyanyi Acak** | Modul 4 | Tanya: *"Siapa penyanyi favoritku?"* |
| **Speech-to-Text** | Audio | Tekan tombol 🎙 lalu bicara |
| **Text-to-Speech** | Audio | Setiap jawaban bot disuarakan otomatis |
| **GUI Futuristik** | Interface | Tampilan JARVIS dengan animasi arc reactor |

---

## 🗂️ Struktur File

```
UTS AI/
├── main.py            ← GUI utama (Tkinter, arc reactor animation)
├── jarvis_core.py     ← Logika inti (Modul 4 & 5: nama, random, intent)
├── gemini_handler.py  ← Integrasi Gemini API
├── speech_handler.py  ← STT (SpeechRecognition) + TTS (gTTS + pygame)
├── config.py          ← Konfigurasi & konstanta
├── requirements.txt   ← Daftar dependency Python
├── .env.example       ← Template environment variable
└── README.md          ← Dokumentasi ini
```

---

## 💬 Contoh Percakapan

```
User   : My name is Andira
JARVIS : Hallo Andira, nice to meet you! Senang berkenalan denganmu.

User   : Do you know me?
JARVIS : Tentu saja, kawan. Kamu adalah Andira. Identitasmu telah tercatat dalam sistemku.

User   : Siapa penyanyi favoritku?
JARVIS : Berdasarkan analisis preferensiku, penyanyi favoritmu adalah Baskara Putra. Pilihan yang luar biasa!

User   : Siapa yang membuatmu?
JARVIS : Saya dikembangkan oleh tim Intelligence created by A dari Teknik Informatika JGU.
```

---

## ⚙️ Teknologi

- **NLP / Brain**: Google Gemini 1.5 Flash API
- **STT**: `SpeechRecognition` + Google Web Speech API
- **TTS**: `gTTS` (Google Text-to-Speech) + `pygame`
- **GUI**: `Tkinter` (built-in Python)
- **Bahasa**: Python 3.10+
# jarvis-ai-assistant
