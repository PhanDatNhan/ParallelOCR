# Parallel OCR Project

Dự án này triển khai hệ thống nhận diện ký tự (OCR) với Tesseract, hỗ trợ 4 chế độ xử lý:

- `ocrBaseline.py`: chế độ tuần tự.
- `ocrParallel.py`: song song trên một máy bằng nhiều process.
- `ocrMPI.py`: phân tán với MPI.
- `ocrHybrid.py`: kết hợp MPI và nhiều process trên mỗi node.

## Tính năng chính

- Đọc ảnh và so sánh với nhãn ground truth.
- Tính toán CER (Character Error Rate) và WER (Word Error Rate) cho từng ảnh và trung bình toàn bộ tập.
- Ghi kết quả ra file TXT và CSV.
- Hỗ trợ xử lý dataset lớn.

## Yêu cầu

- Python 3.12
- Tesseract OCR đã cài đặt và cấu hình trong `PATH`.
- Microsoft MPI (MS-MPI) cho chế độ MPI.
- Các thư viện Python trong `requirements.txt`:
  - `mpi4py`
  - `opencv-python`
  - `pytesseract`
  - `python-Levenshtein`
  - `numpy`
  - `pandas`

## Cài đặt

1. Cài đặt Tesseract OCR:
   https://github.com/UB-Mannheim/tesseract/wiki

2. Cài đặt Microsoft MPI:
   https://learn.microsoft.com/en-us/message-passing-interface/microsoft-mpi

3. Tạo và kích hoạt virtual environment:

```
python -m venv ocr_env
ocr_env\Scripts\activate
```

4. Cài đặt các thư viện Python:

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

### 3. Chạy chế độ MPI phân tán

Ví dụ chạy trên hai host:

```powershell
mpiexec -hosts 2 IP1 IP2 -n 2 python ocrMPI.py
```

### 4. Chạy chế độ kết hợp MPI + shared memory

Ví dụ:

```powershell
mpiexec -hosts 2 IP1 IP2 -n 8 python ocrHybrid.py
```

Hoặc dùng file host:

```powershell
mpiexec -machinefile hostfile.txt -n 8 python ocrHybrid.py
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
├── ocrHybrid.py
├── ocrMPI.py
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

- Đảm bảo mọi máy tham gia MPI đều cài đặt cùng phiên bản Python, Tesseract và thư viện giống nhau.
- Nếu gặp lỗi với `pytesseract`, kiểm tra lại đường dẫn Tesseract trong biến môi trường `PATH`.
- Sửa đường dẫn `IMAGE_FOLDER` và `LABEL_FOLDER` trong `dataConfig.py` nếu cần sử dụng dataset khác.
