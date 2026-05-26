"""
metrics.py — Tính WER và CER.
Import module này ở bất kỳ đâu cần đánh giá chất lượng OCR.
"""

from itertools import zip_longest


def _edit_distance(seq1: list, seq2: list) -> int:
    """Levenshtein distance giữa hai sequence."""
    m, n = len(seq1), len(seq2)
    # Rolling 2-row DP để tiết kiệm bộ nhớ
    prev = list(range(n + 1))
    for i, s1 in enumerate(seq1, 1):
        curr = [i] + [0] * n
        for j, s2 in enumerate(seq2, 1):
            if s1 == s2:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev = curr
    return prev[n]


def calculate_cer(reference: str, hypothesis: str) -> float:
    """Character Error Rate = edit_distance(chars) / len(reference_chars)."""
    ref = list(reference.strip())
    hyp = list(hypothesis.strip())
    if not ref:
        return 0.0
    return _edit_distance(ref, hyp) / len(ref)


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Word Error Rate = edit_distance(words) / len(reference_words)."""
    ref = reference.strip().split()
    hyp = hypothesis.strip().split()
    if not ref:
        return 0.0
    return _edit_distance(ref, hyp) / len(ref)
