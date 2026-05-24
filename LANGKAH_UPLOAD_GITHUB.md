# Panduan Upload Project ke GitHub

Berikut adalah langkah-langkah untuk mengunggah project **J.A.R.V.I.S v2.0** ini ke GitHub Anda.

## Persiapan Awal
1. Pastikan Anda sudah memiliki akun [GitHub](https://github.com/).
2. Pastikan program [Git](https://git-scm.com/) sudah terinstall di komputer/laptop Anda.
3. Buka terminal (atau command prompt/Git Bash), lalu arahkan ke folder project ini.
   
   Jika Anda menggunakan VS Code, Anda cukup membuka terminal bawaan VS Code (`Ctrl` + `~`).

## Langkah-langkah Upload

### 1. Inisialisasi Git Repository Lokal
Jalankan perintah ini di dalam folder project Anda untuk membuat repository lokal:
```bash
git init
```

### 2. Tambahkan File ke Staging Area
Tambahkan semua file ke dalam git. (Tenang saja, file sensitif seperti `.env` dan folder `__pycache__` atau `.venv` tidak akan ikut terbawa karena sudah saya buatkan file `.gitignore`).
```bash
git add .
```

### 3. Buat Commit Pertama
Simpan status file Anda saat ini dengan sebuah pesan commit:
```bash
git commit -m "Initial commit: Menambahkan project J.A.R.V.I.S v2.0 UTS AI"
```

### 4. Buat Repository Baru di Akun GitHub Anda
1. Buka [github.com](https://github.com/) dan login.
2. Klik tombol **New** di bagian kiri atas (atau icon `+` di pojok kanan atas lalu pilih **New repository**).
3. Isi **Repository name** (misal: `jarvis-ai-assistant` atau `uts-ai-jarvis`).
4. Isi **Description** (opsional, bisa diambil dari saran deskripsi).
5. Pilih **Public** (jika ingin bisa dilihat publik) atau **Private** (jika untuk sendiri).
6. **Penting:** Biarkan kotak _"Add a README file"_, _"Add .gitignore"_, dan _"Choose a license"_ dalam keadaan **KOSONG/TIDAK DICENTANG**.
7. Klik tombol **Create repository**.

### 5. Hubungkan dan Push ke GitHub
Setelah repository dibuat di GitHub, Anda akan melihat halaman instruksi. Copy perintah yang ada di bagian **"…or push an existing repository from the command line"**. 

Biasanya perintahnya adalah seperti ini (jalankan baris per baris di terminal Anda):
```bash
git branch -M main
git remote add origin https://github.com/USERNAME_ANDA/NAMA_REPO_ANDA.git
git push -u origin main
```
*(Catatan: pastikan URL pada perintah `git remote add origin` sesuai dengan yang ada di GitHub Anda).*

---

🎉 **Selesai!** Jika tidak ada error pada langkah terakhir, Anda bisa me-refresh halaman GitHub Anda dan file-file project J.A.R.V.I.S Anda sudah berhasil terupload!
