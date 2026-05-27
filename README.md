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

## � Push perubahan ke GitHub

Repo sudah ada di https://github.com/chalidaaa/ocr-receipt-ab-testing.
Setiap kali ada perubahan kode, jalankan dari folder project:

```powershell
git add .
git commit -m "deskripsi perubahan"
git push
```

---

## ☁️ Deploy ke Streamlit Community Cloud

1. Login di https://share.streamlit.io pakai akun GitHub.
2. Klik **New app**, lalu isi:
   - **Repository**: `chalidaaa/ocr-receipt-ab-testing`
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. Klik **Deploy** dan tunggu build (3–6 menit untuk first build karena
   harus download PyTorch + EasyOCR).

Setiap `git push` ke `main` akan otomatis re-deploy. Bagikan URL app ke
teman dan mereka tinggal upload struk lewat browser.

---

## 🛠️ Troubleshooting

| Masalah | Solusi |
|---|---|
| `streamlit : The term 'streamlit' is not recognized` | venv belum aktif. Jalankan `.\.venv\Scripts\Activate.ps1` dulu. |
| `ImportError: libGL.so.1` saat deploy | Pastikan `requirements.txt` pakai `opencv-python-headless` (bukan `opencv-python`). |
| `libglib2.0-0 : Depends: libffi7` saat deploy | Hapus file `packages.txt`. `opencv-python-headless` tidak butuh apt deps di image Streamlit Cloud terbaru. |
| Build timeout di Streamlit Cloud | Klik **Reboot app** dari dashboard. Build pertama memang lambat. |
| Port 8501 sudah dipakai di lokal | `streamlit run app.py --server.port 8502` |

---

## 👤 Author

[@chalidaaa](https://github.com/chalidaaa)
