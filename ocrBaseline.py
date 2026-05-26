"""
ocrBaseline.py — OCR tuần tự (single process).

Chạy:
  python ocrBaseline.py              # chỉ OCR + đo thời gian
  python ocrBaseline.py --metrics    # OCR + đo thời gian + tính CER/WER
"""

import os
import time
import argparse

import dataConfig
from ocr_engine import ocr_from_path, load_ground_truth
from metrics import calculate_cer, calculate_wer
from result_writer import ImageResult, RunSummary, save_results, print_summary


def run(compute_metrics: bool = False) -> RunSummary:
    image_files = sorted(os.listdir(dataConfig.IMAGE_FOLDER))
    details: list[ImageResult] = []

    print(f"[Baseline] {len(image_files)} ảnh | metrics={'on' if compute_metrics else 'off'}")

    wall_start = time.perf_counter()

    for fname in image_files:
        img_path = os.path.join(dataConfig.IMAGE_FOLDER, fname)

        # ── OCR + đo thời gian (bên trong ocr_engine) ────────────────────────
        result = ocr_from_path(img_path, fname)

        # ── Metrics tách biệt, không ảnh hưởng elapsed ───────────────────────
        cer = wer = None
        if compute_metrics:
            label_path = os.path.join(dataConfig.LABEL_FOLDER,
                                      fname.replace(".png", ".txt"))
            gt  = load_ground_truth(label_path)
            cer = calculate_cer(gt, result.predicted)
            wer = calculate_wer(gt, result.predicted)

        details.append(ImageResult(fname, rank=0,
                                   time_s=result.elapsed, cer=cer, wer=wer))

        log = f"[Baseline] {fname}  t={result.elapsed:.3f}s"
        if compute_metrics:
            log += f"  CER={cer:.4f}  WER={wer:.4f}"
        print(log)

    total_time = time.perf_counter() - wall_start
    avg_time   = sum(r.time_s for r in details) / len(details)
    avg_cer    = sum(r.cer for r in details) / len(details) if compute_metrics else None
    avg_wer    = sum(r.wer for r in details) / len(details) if compute_metrics else None

    summary = RunSummary(
        mode="baseline", total_time=total_time, avg_time=avg_time,
        avg_cer=avg_cer, avg_wer=avg_wer,
        details=details, has_metrics=compute_metrics,
    )
    print_summary(summary)
    save_results(summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", action="store_true",
                        help="Tính CER/WER sau OCR (không ảnh hưởng đo thời gian OCR)")
    args = parser.parse_args()
    run(compute_metrics=args.metrics)
