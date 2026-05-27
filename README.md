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
[@chalidaaa](https://github.com/chalidaaa)
