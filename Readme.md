# Parallel OCR Project

Dự án này triển khai hệ thống nhận diện ký tự (OCR) với Tesseract, hỗ trợ 4 chế độ xử lý:

- `ocrBaseline.py`: chế độ tuần tự.
- `ocrParallel.py`: song song trên một máy bằng nhiều process.

## Tính năng chính

- Đọc ảnh và so sánh với nhãn ground truth.
- Tính toán CER (Character Error Rate) và WER (Word Error Rate) cho từng ảnh và trung bình toàn bộ tập.
- Ghi kết quả ra file TXT và CSV.
- Hỗ trợ xử lý dataset lớn.

## Yêu cầu

- Python 3.12
- Tesseract OCR đã cài đặt và cấu hình trong `PATH`.
- Các thư viện Python trong `requirements.txt`:
  - `opencv-python`
  - `pytesseract`
  - `python-Levenshtein`
  - `numpy`
  - `pandas`

## Cài đặt

1. Cài đặt Tesseract OCR:
   https://github.com/UB-Mannheim/tesseract/wiki

2. Tạo và kích hoạt virtual environment:

```
python -m venv ocr_env
ocr_env\Scripts\activate
```

3. Cài đặt các thư viện Python:

```
pip install -r requirements.txt
```

## Chuẩn bị dữ liệu

- `dataset/images10/`: chứa ảnh đầu vào.
- `dataset/labels10/`: chứa nhãn tương ứng cho từng ảnh.
- Nếu muốn tạo dữ liệu tự động, chỉnh sửa cấu hình trong `dataConfig.py` rồi chạy:

```powershell
python dataGenerator.py
```

## Cách chạy

### 1. Chạy chế độ tuần tự

```powershell
python ocrBaseline.py
```

### 2. Chạy chế độ song song trên cùng một máy

```powershell
python ocrParallel.py
```

## Cấu trúc thư mục

```
files/
├── cpuCount.py
├── dataConfig.py
├── dataGenerator.py
├── hostfile.txt
├── metrics.py
├── ocr_engine.py
├── ocrBaseline.py
├── ocrParallel.py
├── result_writer.py
├── requirements.txt
├── Readme.md
├── dataset/
│   ├── images10/
│   └── labels10/
└── result/
    ├── baseline_results.csv
    └── baseline_results.txt
```

## Ghi chú

- Nếu gặp lỗi với `pytesseract`, kiểm tra lại đường dẫn Tesseract trong biến môi trường `PATH`.
- Sửa đường dẫn `IMAGE_FOLDER` và `LABEL_FOLDER` trong `dataConfig.py` nếu cần sử dụng dataset khác.
