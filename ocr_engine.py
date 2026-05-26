"""
ocr_engine.py — Lõi OCR duy nhất.
Tất cả module song song import từ đây; không có code OCR nào ở nơi khác.
"""

import os
import cv2
import pytesseract
from dataclasses import dataclass

os.environ.setdefault("OMP_THREAD_LIMIT",    "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS","1")
os.environ.setdefault("MKL_NUM_THREADS",     "1")


# ── Kết quả 1 ảnh sau OCR (chưa tính metrics) ────────────────────────────────
@dataclass
class OCRResult:
    image_name: str
    predicted:  str    # text OCR ra
    elapsed:    float  # giây — ĐO ĐÚNG thời gian OCR thuần


# ── I/O helpers ───────────────────────────────────────────────────────────────

def load_image(image_path: str):
    """Đọc ảnh grayscale từ đĩa → numpy array."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")
    return img


def load_ground_truth(label_path: str) -> str:
    with open(label_path, "r", encoding="utf-8") as f:
        return f.read()


def build_image_cache(image_files: list, image_folder: str) -> dict:
    """Load toàn bộ ảnh vào RAM → dict {filename: ndarray}."""
    return {
        fname: load_image(os.path.join(image_folder, fname))
        for fname in image_files
    }


# ── OCR core — ĐO THỜI GIAN CHỈ Ở ĐÂY ───────────────────────────────────────

def ocr_from_path(image_path: str, image_name: str = "") -> OCRResult:
    """OCR 1 ảnh từ đường dẫn. Elapsed = thời gian OCR thuần."""
    import time
    img = load_image(image_path)
    t0  = time.perf_counter()
    text = pytesseract.image_to_string(img)
    elapsed = time.perf_counter() - t0
    return OCRResult(image_name or os.path.basename(image_path), text, elapsed)


def ocr_from_array(img, image_name: str = "") -> OCRResult:
    """OCR 1 ảnh từ numpy array. Elapsed = thời gian OCR thuần."""
    import time
    t0  = time.perf_counter()
    text = pytesseract.image_to_string(img)
    elapsed = time.perf_counter() - t0
    return OCRResult(image_name, text, elapsed)
