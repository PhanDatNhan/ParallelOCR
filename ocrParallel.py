"""
ocrParallel.py — Song song bộ nhớ chia sẻ (multiprocessing + SharedMemory).

Worker chỉ làm: attach shared block → OCR → trả về (fname, predicted, elapsed).
Metrics được tính SAU ở main process nếu --metrics được truyền vào.

Chạy:
  python ocrParallel.py
  python ocrParallel.py --metrics
  python ocrParallel.py --workers 4 --batch 10
"""

import os
import time
import argparse
from multiprocessing import Pool
from multiprocessing.shared_memory import SharedMemory

import numpy as np

import dataConfig
from ocr_engine import load_image, ocr_from_array, load_ground_truth
from metrics import calculate_cer, calculate_wer
from result_writer import ImageResult, RunSummary, save_results, print_summary

# ── Defaults (override qua CLI) ───────────────────────────────────────────────
DEFAULT_WORKERS = 16
DEFAULT_BATCH = 1
# ─────────────────────────────────────────────────────────────────────────────

_shm_registry: dict[str, SharedMemory] = {}


def _allocate_shm(fname: str, img: np.ndarray) -> dict:
    shm = SharedMemory(create=True, size=img.nbytes)
    np.copyto(np.ndarray(img.shape, dtype=img.dtype, buffer=shm.buf), img)
    _shm_registry[fname] = shm
    return {"name": shm.name, "shape": img.shape, "dtype": img.dtype.str}


def _free_all_shm() -> None:
    for shm in _shm_registry.values():
        shm.close()
        shm.unlink()
    _shm_registry.clear()


# ── Worker: CHỈ OCR, không đụng ground truth ─────────────────────────────────

def _worker_batch(batch_meta: list) -> list:
    """
    Input : [(fname, shm_name, shape, dtype), ...]
    Output: [(fname, predicted_text, elapsed_ocr), ...]
    """
    results = []
    for fname, shm_name, shape, dtype in batch_meta:
        shm = SharedMemory(name=shm_name, create=False)
        img = np.ndarray(shape, dtype=np.dtype(dtype), buffer=shm.buf)

        ocr_result = ocr_from_array(img, fname)   # elapsed đo bên trong

        shm.close()  # detach, không unlink
        results.append((fname, ocr_result.predicted, ocr_result.elapsed))
    return results


def _chunkify(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def run(compute_metrics: bool = False,
        max_workers: int = DEFAULT_WORKERS,
        batch_size: int = DEFAULT_BATCH) -> RunSummary:

    image_files = sorted(os.listdir(dataConfig.IMAGE_FOLDER))
    print(f"[Parallel] Workers={max_workers}  Batch={batch_size}  "
          f"Images={len(image_files)}  metrics={'on' if compute_metrics else 'off'}")

    # ── 1. Load → SharedMemory ────────────────────────────────────────────────
    print("[Parallel] Allocating SharedMemory...")
    t_load = time.perf_counter()
    shm_meta = {}
    for fname in image_files:
        img = load_image(os.path.join(dataConfig.IMAGE_FOLDER, fname))
        shm_meta[fname] = _allocate_shm(fname, img)
    print(f"[Parallel] ✓ Ready  {time.perf_counter()-t_load:.2f}s")

    # ── 2. Chuẩn bị batch (không bao gồm label_path) ─────────────────────────
    all_meta = [
        (fname, shm_meta[fname]["name"],
         shm_meta[fname]["shape"], shm_meta[fname]["dtype"])
        for fname in image_files
    ]
    batches = list(_chunkify(all_meta, batch_size))

    # ── 3. Song song OCR — wall clock đo đúng thời gian OCR pool ─────────────
    wall_start = time.perf_counter()
    raw: list[tuple] = []

    with Pool(processes=max_workers) as pool:
        for batch_out in pool.imap_unordered(_worker_batch, batches):
            raw.extend(batch_out)

    total_time = time.perf_counter() - wall_start
    _free_all_shm()

    # ── 4. Sắp xếp theo thứ tự gốc ───────────────────────────────────────────
    order = {fname: i for i, fname in enumerate(image_files)}
    raw.sort(key=lambda x: order[x[0]])

    # ── 5. Tính metrics SAU (không ảnh hưởng total_time) ─────────────────────
    details: list[ImageResult] = []
    for fname, predicted, elapsed in raw:
        cer = wer = None
        if compute_metrics:
            label_path = os.path.join(dataConfig.LABEL_FOLDER,
                                      fname.replace(".png", ".txt"))
            gt = load_ground_truth(label_path)
            cer = calculate_cer(gt, predicted)
            wer = calculate_wer(gt, predicted)
        details.append(ImageResult(
            fname, rank=0, time_s=elapsed, cer=cer, wer=wer))

    avg_time = sum(r.time_s for r in details) / len(details)
    avg_cer = sum(r.cer for r in details) / \
        len(details) if compute_metrics else None
    avg_wer = sum(r.wer for r in details) / \
        len(details) if compute_metrics else None

    summary = RunSummary(
        mode="parallel", total_time=total_time, avg_time=avg_time,
        avg_cer=avg_cer, avg_wer=avg_wer,
        details=details, has_metrics=compute_metrics,
    )
    print_summary(summary)
    save_results(summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics",  action="store_true")
    parser.add_argument("--workers",  type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--batch",    type=int, default=DEFAULT_BATCH)
    args = parser.parse_args()
    run(compute_metrics=args.metrics,
        max_workers=args.workers,
        batch_size=args.batch)
