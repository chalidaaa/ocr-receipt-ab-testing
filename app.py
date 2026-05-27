"""Receipt OCR Dashboard — EasyOCR + A/B preprocessing.

Streamlit app yang mengekstrak Store, Date, dan Total Amount dari gambar
struk / invoice menggunakan EasyOCR.
"""

import re

import cv2
import easyocr
import numpy as np
import streamlit as st
from PIL import Image

# =====================================================================
# STREAMLIT CONFIG
# =====================================================================

st.set_page_config(
    page_title="Receipt OCR",
    page_icon=":receipt:",
    layout="wide",
)

st.title(":receipt: Receipt OCR Dashboard")
st.caption(
    "Upload gambar struk / invoice → OCR otomatis dengan EasyOCR + "
    "A/B testing preprocessing → ekstraksi **Store**, **Date**, **Total Amount**."
)


# =====================================================================
# EASYOCR LOADER (cached)
# =====================================================================


@st.cache_resource(show_spinner="Memuat model EasyOCR (sekali saja)...")
def load_reader() -> easyocr.Reader:
    return easyocr.Reader(["en"], gpu=False)


reader = load_reader()


# =====================================================================
# IMAGE PREPROCESSING
# =====================================================================


def preprocess_image(img: np.ndarray) -> np.ndarray:
    """Grayscale + denoise + adaptive threshold dengan auto-upscale."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if img.ndim == 3 else img.copy()

    h, w = gray.shape[:2]
    if max(h, w) < 1200:
        scale = 1200 / max(h, w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    denoised = cv2.fastNlMeansDenoising(gray, h=15)
    return cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )


# =====================================================================
# OCR
# =====================================================================


def run_ocr(img: np.ndarray) -> list[tuple]:
    """EasyOCR dengan parameter high-accuracy untuk struk."""
    return reader.readtext(
        img,
        detail=1,
        paragraph=False,
        decoder="beamsearch",
        beamWidth=5,
        contrast_ths=0.1,
        adjust_contrast=0.7,
        text_threshold=0.6,
        low_text=0.3,
    )


# =====================================================================
# ROW CLUSTERING (gabungkan bbox per baris)
# =====================================================================


def _meta(det: tuple) -> dict:
    bbox, text, conf = det
    xs = [p[0] for p in bbox]
    ys = [p[1] for p in bbox]
    return {
        "text": text,
        "conf": float(conf or 0.0),
        "x_left": float(min(xs)),
        "x_right": float(max(xs)),
        "y_top": float(min(ys)),
        "y_bottom": float(max(ys)),
        "y_center": float(sum(ys) / 4.0),
        "height": float(max(ys) - min(ys)),
    }


def cluster_rows(detections: list[tuple]) -> list[list[dict]]:
    items = [_meta(d) for d in detections]
    items.sort(key=lambda i: i["y_center"])
    rows: list[list[dict]] = []
    for it in items:
        if rows:
            last = rows[-1][-1]
            tol = max(it["height"], last["height"]) * 0.6
            if abs(it["y_center"] - last["y_center"]) <= max(tol, 8):
                rows[-1].append(it)
                continue
        rows.append([it])
    for row in rows:
        row.sort(key=lambda i: i["x_left"])
    return rows


def row_text(row: list[dict]) -> str:
    return " ".join(i["text"] for i in row).strip()


# =====================================================================
# DATE EXTRACTION
# =====================================================================

DATE_PATTERNS = [
    r"\b\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}\b",
    r"\b\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2}\b",
    r"\b\d{1,2}\s+(?:Jan(?:uary|uari)?|Feb(?:ruary|ruari)?|Mar(?:ch|et)?|"
    r"Apr(?:il)?|May|Mei|Jun(?:e|i)?|Jul(?:y|i)?|Aug(?:ust)?|Agu(?:stus)?|"
    r"Sep(?:tember)?|Oct(?:ober)?|Okt(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|"
    r"Des(?:ember)?)[a-z]*\.?\s+\d{2,4}\b",
]


def extract_date(text: str) -> str:
    for pat in DATE_PATTERNS:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return m.group().strip()
    return "-"


# =====================================================================
# AMOUNT EXTRACTION
# =====================================================================

HIGH_KEYWORDS = (
    "grand total", "total bayar", "total belanja", "total pembayaran",
    "total payment", "total amount", "amount due", "net total",
    "net amount", "total akhir", "total tagihan",
)
MID_KEYWORDS = ("total",)
LOW_KEYWORDS = ("jumlah", "harga total", "harga")
SUBTOTAL_KEYWORDS = ("subtotal", "sub total", "sub-total")
SKIP_PATTERNS = (
    "total item", "total items", "total qty", "total quantity",
    "jumlah item", "jumlah barang", "qty", "kembalian", "tunai",
    "kembali", "change", "bayar tunai", "cash",
)
RP_PREFIX = re.compile(r"\b(?:rp\.?|idr\.?)\b", re.I)
MONEY_PATTERN = re.compile(
    r"-?\d{1,3}(?:[.,\s]\d{3})+(?:[.,]\d{1,2})?|-?\d{3,}(?:[.,]\d{1,2})?"
)
DIGIT_FIX = str.maketrans({
    "O": "0", "o": "0", "Q": "0", "l": "1", "I": "1", "|": "1",
    "B": "8", "S": "5", "Z": "2",
})


def find_amounts_in_text(text: str) -> list[int]:
    candidate = text.translate(DIGIT_FIX)
    out: list[int] = []
    for m in MONEY_PATTERN.finditer(candidate):
        digits = re.sub(r"\D", "", m.group())
        if len(digits) < 3:
            continue
        if len(digits) == 4 and digits[:2] in ("19", "20"):
            continue  # kemungkinan tahun
        v = int(digits)
        if v >= 100:
            out.append(v)
    return out


def format_rupiah(value: int | None) -> str:
    return "-" if value is None else "Rp" + f"{value:,}".replace(",", ".")


def _row_amounts_with_x(row: list[dict]) -> list[tuple[float, int]]:
    out: list[tuple[float, int]] = []
    for it in row:
        for amt in find_amounts_in_text(it["text"]):
            out.append((it["x_right"], amt))
    return out


def extract_total(rows: list[list[dict]]) -> str:
    if not rows:
        return "-"

    n = len(rows)
    candidates: list[tuple[float, int]] = []

    for idx, row in enumerate(rows):
        ll = row_text(row).lower()

        if any(skip in ll for skip in SKIP_PATTERNS):
            continue

        is_high = any(kw in ll for kw in HIGH_KEYWORDS)
        is_subtotal = any(kw in ll for kw in SUBTOTAL_KEYWORDS)
        is_mid = (not is_high) and (not is_subtotal) and any(kw in ll for kw in MID_KEYWORDS)
        is_low = (
            not is_high and not is_mid and not is_subtotal
            and any(kw in ll for kw in LOW_KEYWORDS)
        )
        has_rp = bool(RP_PREFIX.search(ll))

        kw_score = 200 if is_high else 100 if is_mid else 40 if is_subtotal else 25 if is_low else 0
        amounts = _row_amounts_with_x(row)

        # keyword tanpa angka → cek baris berikutnya
        if (is_high or is_mid) and not amounts and idx + 1 < n:
            next_amounts = _row_amounts_with_x(rows[idx + 1])
            if next_amounts:
                next_amounts.sort(key=lambda x: x[0], reverse=True)
                pos_bonus = (idx / max(n - 1, 1)) * 50
                rp_bonus = 30 if has_rp else 0
                candidates.append((kw_score + pos_bonus + rp_bonus, next_amounts[0][1]))
                continue

        if not amounts:
            continue

        amounts.sort(key=lambda x: x[0], reverse=True)
        amount = amounts[0][1]

        pos_bonus = (idx / max(n - 1, 1)) * 50
        avg_h = sum(it["height"] for it in row) / len(row)
        font_bonus = min(avg_h * 0.5, 30)
        rp_bonus = 30 if has_rp else 0
        no_kw_penalty = 0 if kw_score > 0 else -150

        candidates.append((kw_score + pos_bonus + font_bonus + rp_bonus + no_kw_penalty, amount))

    if not candidates:
        all_amounts = [a for row in rows for it in row for a in find_amounts_in_text(it["text"])]
        return format_rupiah(max(all_amounts)) if all_amounts else "-"

    candidates.sort(key=lambda x: x[0], reverse=True)
    best_score, best_amount = candidates[0]
    if best_score <= 0:
        return format_rupiah(max(c[1] for c in candidates))
    return format_rupiah(best_amount)


# =====================================================================
# STORE EXTRACTION (row-level scoring)
# =====================================================================

STORE_BLACKLIST = (
    "receipt", "invoice", "struk", "nota", "bill", "tax invoice",
    "welcome", "thank you", "terima kasih", "kasir", "cashier",
    "npwp", "telp", "phone", "alamat",
)
ADDRESS_PATTERN = re.compile(r"\b(jl\.?|jalan|no\.?|rt\.?|rw\.?|kel\.?|kec\.?|kota|kab\.?)\b", re.I)


def extract_store(rows: list[list[dict]], img_shape: tuple[int, int]) -> str:
    """Pilih row di area header yang paling mirip nama merchant.

    Strategi:
      1. Hanya pertimbangkan row di 35 % area atas gambar.
      2. Skor per ROW (bukan per bbox) — logo sering ter-OCR jadi banyak bbox.
      3. Signal: font size relatif vs median, panjang teks, confidence,
         posisi vertikal, rasio huruf vs digit.
      4. Skip blacklist (RECEIPT/INVOICE/NPWP/dll) & alamat (Jl/RT/RW).
    """
    if not rows:
        return "-"

    h = img_shape[0]
    header_limit = h * 0.35

    # median font size global → baseline untuk deteksi "logo besar"
    all_heights = [it["height"] for row in rows for it in row]
    median_h = float(np.median(all_heights)) if all_heights else 1.0
    median_h = max(median_h, 1.0)

    candidates: list[tuple[float, str]] = []

    for row in rows:
        y_avg = sum(it["y_center"] for it in row) / len(row)
        if y_avg > header_limit:
            continue

        text = row_text(row)
        if len(text) < 3:
            continue

        ll = text.lower()
        if any(b in ll for b in STORE_BLACKLIST):
            continue
        if ADDRESS_PATTERN.search(text):
            continue

        letters = sum(c.isalpha() for c in text)
        digits = sum(c.isdigit() for c in text)
        if letters < 3 or digits > letters:
            continue

        avg_h = sum(it["height"] for it in row) / len(row)
        avg_conf = sum(it["conf"] for it in row) / len(row)
        font_ratio = avg_h / median_h
        position_bonus = 1 - (y_avg / header_limit)
        length_bonus = min(len(text), 40) / 40
        upper_ratio = sum(c.isupper() for c in text) / max(letters, 1)

        score = (
            font_ratio * 60        # logo besar = signal terkuat
            + position_bonus * 25  # makin atas makin baik
            + avg_conf * 20        # confidence OCR
            + length_bonus * 15    # row dengan teks panjang biasanya nama lengkap
            + upper_ratio * 10     # nama merchant biasanya UPPERCASE
        )
        candidates.append((score, text))

    if not candidates:
        return "-"

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


# =====================================================================
# MAIN UI
# =====================================================================

uploaded = st.file_uploader(
    "Upload gambar struk / invoice",
    type=["jpg", "jpeg", "png"],
)

if uploaded is None:
    st.info("Silakan upload gambar struk untuk mulai.")
    st.stop()

image = Image.open(uploaded).convert("RGB")
img_np = np.array(image)
processed = preprocess_image(img_np)

with st.spinner("Menjalankan OCR (Original + Preprocessing)..."):
    det_a = run_ocr(img_np)
    det_b = run_ocr(processed)

text_a = "\n".join(d[1] for d in det_a)
text_b = "\n".join(d[1] for d in det_b)

# ----- Side-by-side preview -----
st.subheader("Perbandingan Gambar")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**A — Original**")
    st.image(image, use_container_width=True)
with col2:
    st.markdown("**B — Grayscale + Adaptive Threshold**")
    st.image(processed, use_container_width=True, clamp=True)

# ----- A/B Testing analysis -----
st.subheader("Hasil A/B Testing")

len_a, len_b = len(text_a), len(text_b)
conf_a = float(np.mean([d[2] for d in det_a])) if det_a else 0.0
conf_b = float(np.mean([d[2] for d in det_b])) if det_b else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Karakter Original", len_a)
m2.metric("Karakter Preprocessing", len_b)
m3.metric("Confidence Original", f"{conf_a:.2f}")
m4.metric("Confidence Preproc.", f"{conf_b:.2f}")

score_a = len_a * conf_a
score_b = len_b * conf_b

if score_a >= score_b:
    chosen_label = "A — Original"
    chosen_dets = det_a
    chosen_shape = img_np.shape[:2]
    chosen_text = text_a
    if len_a > len_b:
        st.warning("OCR Original lebih baik")
        reason = "Gambar original menghasilkan lebih banyak karakter."
    else:
        st.info("OCR Original dipilih (skor karakter × confidence lebih tinggi)")
        reason = "Confidence OCR pada gambar Original lebih tinggi."
else:
    chosen_label = "B — Preprocessing"
    chosen_dets = det_b
    chosen_shape = processed.shape[:2]
    chosen_text = text_b
    st.success("Preprocessing menghasilkan OCR lebih baik")
    reason = (
        "Grayscale + adaptive threshold meningkatkan kontras teks sehingga "
        "EasyOCR menangkap lebih banyak karakter dengan confidence lebih tinggi."
    )

st.caption(f"**Pilihan otomatis:** {chosen_label}. {reason}")

# ----- Label extraction -----
st.subheader("Label Extraction")

rows = cluster_rows(chosen_dets)
store = extract_store(rows, chosen_shape)
date = extract_date(chosen_text)
total = extract_total(rows)

st.success(f"🏪  **Store** : {store}")
st.success(f"📅  **Date** : {date}")
st.success(f"💰  **Total Amount** : {total}")
