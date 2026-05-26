"""
result_writer.py — Ghi kết quả TXT + CSV.
Hỗ trợ cả hai chế độ: OCR-only và OCR + Metrics.
"""

import csv
import os
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class ImageResult:
    image_name: str
    rank:       int
    time_s:     float          # thời gian OCR thuần
    cer:        Optional[float] = None   # None nếu không tính metrics
    wer:        Optional[float] = None


@dataclass
class RunSummary:
    mode:         str
    total_time:   float        # wall-clock toàn bộ quá trình OCR song song
    avg_time:     float        # trung bình thời gian OCR mỗi ảnh
    avg_cer:      Optional[float] = None
    avg_wer:      Optional[float] = None
    details:      List[ImageResult] = field(default_factory=list)
    has_metrics:  bool = False


def _fmt(v: Optional[float], precision: int = 4) -> str:
    return f"{v:.{precision}f}" if v is not None else "N/A"


def save_results(summary: RunSummary, out_dir: str = "result") -> None:
    os.makedirs(out_dir, exist_ok=True)
    prefix = os.path.join(out_dir, summary.mode)

    # ── TXT ──────────────────────────────────────────────────────────────────
    with open(f"{prefix}_results.txt", "w", encoding="utf-8") as f:
        f.write(f"Mode            : {summary.mode}\n")
        f.write(f"Tổng TG OCR     : {summary.total_time:.2f}s\n")
        f.write(f"Avg TG / ảnh    : {summary.avg_time:.3f}s\n")
        if summary.has_metrics:
            f.write(f"Avg CER         : {_fmt(summary.avg_cer)}\n")
            f.write(f"Avg WER         : {_fmt(summary.avg_wer)}\n")
        else:
            f.write("CER / WER       : không đo (chạy lại với --metrics)\n")
        f.write("─" * 65 + "\n")
        for r in summary.details:
            metrics_str = (
                f"  CER={_fmt(r.cer)}  WER={_fmt(r.wer)}"
                if summary.has_metrics else ""
            )
            f.write(
                f"[Rank {r.rank:>2}] {r.image_name:25s} "
                f"t={r.time_s:.3f}s{metrics_str}\n"
            )

    # ── CSV ──────────────────────────────────────────────────────────────────
    headers = ["image", "rank", "time_s"]
    if summary.has_metrics:
        headers += ["cer", "wer"]

    with open(f"{prefix}_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in summary.details:
            row = [r.image_name, r.rank, f"{r.time_s:.4f}"]
            if summary.has_metrics:
                row += [_fmt(r.cer), _fmt(r.wer)]
            writer.writerow(row)

    print(f"[result_writer] Đã lưu → {prefix}_results.{{txt,csv}}")


def print_summary(summary: RunSummary) -> None:
    bar = "=" * 50
    print(f"\n{bar}")
    print(f"  MODE           : {summary.mode.upper()}")
    print(f"  Tổng TG OCR    : {summary.total_time:.2f}s")
    print(f"  Avg TG / ảnh   : {summary.avg_time:.3f}s")
    if summary.has_metrics:
        print(f"  Avg CER        : {_fmt(summary.avg_cer)}")
        print(f"  Avg WER        : {_fmt(summary.avg_wer)}")
    else:
        print("  CER / WER      : --  (thêm --metrics để tính)")
    print(bar)
