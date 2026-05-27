# 🧾 Receipt OCR Dashboard

Aplikasi Streamlit untuk mengekstrak **Store / Merchant**, **Date**, dan
**Total Amount** dari gambar struk / invoice menggunakan **EasyOCR**.

Fitur:
- Upload gambar struk (JPG / JPEG / PNG)
- A/B testing preprocessing (Original vs Grayscale + Adaptive Threshold)
- Auto-pilih hasil OCR terbaik berdasarkan jumlah karakter × confidence
- Ekstraksi otomatis 3 label: 🏪 Store, 📅 Date, 💰 Total Amount

---

## 🧩 Tech Stack

- Python 3.11
- Streamlit
- EasyOCR (PyTorch backend)
- OpenCV (`opencv-python-headless`)
- NumPy
- Pillow

---

## 📁 Struktur Project

```
ocr-receipt-ab-testing/
├── app.py              # aplikasi Streamlit (entrypoint)
├── requirements.txt    # dependency Python
├── packages.txt        # dependency sistem (Streamlit Cloud / Linux)
├── runtime.txt         # versi Python target
├── README.md
└── .gitignore
```

---

## 💻 Run di Lokal (Windows)

### 1. Clone repo

```powershell
git clone https://github.com/chalidaaa/ocr-receipt-ab-testing.git
cd ocr-receipt-ab-testing
```

### 2. Buat virtual environment

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> Kalau muncul error "running scripts is disabled on this system":
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> Build pertama akan men-download PyTorch + model EasyOCR (~500 MB).
> Tidak perlu install Tesseract.

### 4. Jalankan Streamlit

```powershell
streamlit run app.py
```

Buka URL yang muncul di terminal (default `http://localhost:8501`).

> **Setiap kali buka terminal baru**, aktifkan venv-nya dulu sebelum
> menjalankan `streamlit run app.py`:
> ```powershell
> .\.venv\Scripts\Activate.ps1
> ```

---

## 🚀 Push ke GitHub (Pertama Kali)

### 1. Buat repo baru di GitHub

Buka https://github.com/new dan buat repo dengan nama
`ocr-receipt-ab-testing` (boleh public atau private). **Jangan** centang
"Initialize this repository with a README" — repo lokal sudah punya file
sendiri.

### 2. Init git di folder lokal

Jalankan dari folder project (di terminal yang **tidak perlu venv aktif**):

```powershell
git init
git branch -M main
git add .
git commit -m "Initial commit: receipt OCR with EasyOCR"
```

### 3. Hubungkan ke GitHub & push

Ganti `chalidaaa` di bawah dengan username GitHub kamu kalau berbeda:

```powershell
git remote add origin https://github.com/chalidaaa/ocr-receipt-ab-testing.git
git push -u origin main
```

GitHub akan minta login. Pakai **Personal Access Token** sebagai password
(GitHub sudah tidak menerima password biasa). Buat token di:
https://github.com/settings/tokens → "Generate new token (classic)" →
centang scope `repo` → copy token-nya saat push.

### 4. Push perubahan selanjutnya

```powershell
git add .
git commit -m "deskripsi perubahan"
git push
```

---

## ☁️ Deploy ke Streamlit Community Cloud

### 1. Login ke Streamlit Cloud

Buka https://share.streamlit.io dan login dengan akun GitHub.

### 2. Buat app baru

Klik **New app**, lalu isi:
- **Repository**: `chalidaaa/ocr-receipt-ab-testing`
- **Branch**: `main`
- **Main file path**: `app.py`
- (Opsional) **App URL**: pilih custom subdomain, misal
  `chalida-receipt-ocr.streamlit.app`

Klik **Deploy**.

### 3. Tunggu build

Streamlit Cloud akan otomatis:
1. Install system packages dari `packages.txt` (`libgl1`, `libglib2.0-0`)
2. Install Python packages dari `requirements.txt`
3. Menjalankan `streamlit run app.py`

Build pertama biasanya **3–6 menit** karena harus download PyTorch +
EasyOCR. Setelah selesai, app dapat diakses dari URL public.

### 4. Auto-redeploy

Setiap kali kamu `git push` ke branch `main`, Streamlit Cloud akan
otomatis re-deploy. Tidak perlu langkah manual.

### 5. Bagikan ke teman

Cukup kirim link app-nya. Mereka tidak perlu install apapun — langsung
buka di browser, upload gambar struk, dan lihat hasilnya.

---

## 🧪 Cara Pakai

1. Buka aplikasi (lokal atau Streamlit Cloud)
2. Klik **Upload gambar struk / invoice**
3. Pilih file `.jpg` / `.jpeg` / `.png`
4. Tunggu OCR selesai (~3–10 detik)
5. Lihat hasil 3 label:
   - 🏪 **Store**
   - 📅 **Date**
   - 💰 **Total Amount**

---

## 🛠️ Troubleshooting

| Masalah | Solusi |
|---|---|
| `streamlit : The term 'streamlit' is not recognized` | venv belum aktif. Jalankan `.\.venv\Scripts\Activate.ps1` dulu. |
| Build timeout / OOM di Streamlit Cloud | Coba **Reboot app** dari menu app di dashboard. Build pertama memang lambat. |
| `ImportError: libGL.so.1` saat deploy | Pastikan `packages.txt` berisi `libgl1` dan `libglib2.0-0`. |
| Port 8501 sudah dipakai di lokal | `streamlit run app.py --server.port 8502` |
| Hasil OCR ngawur untuk struk tertentu | Foto ulang dengan pencahayaan rata, struk tidak miring/terlipat. |

---

## 👤 Author

[@chalidaaa](https://github.com/chalidaaa)
