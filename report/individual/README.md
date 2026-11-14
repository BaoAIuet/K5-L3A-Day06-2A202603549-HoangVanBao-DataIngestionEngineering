# Báo cáo cá nhân

Họ và tên: Hoàng Văn Bảo

MSSV: 2A202603549

Corpus: _Principles of Management_ (OpenStax), chương 2 (PDF trang 35–58) và chương 13 (trang 375–399), tổng 49 trang. Nguồn và giấy phép: `starter/data/manifest.json` (CC BY-NC-SA 4.0, © OpenStax/Rice University). Các file kết quả có chứa đoạn trích ngắn từ sách, có ghi nguồn. PDF không được đưa vào repo này; tải theo link trong manifest nếu cần tái tạo.

## Bản đồ file

| Yêu cầu                | Đường dẫn |
| ---------------------- | --------- |
| Code pipeline          | `starter/src/` |
| Manifest               | `starter/data/manifest.json` |
| Benchmark, gold, split | `starter/data/benchmark.json` |
| Experiment log         | `artifacts/experiment_log.csv` |
| Trace, nhãn audit, log | `starter/results/` |
| Báo cáo                | `report/individual/2A202603549_HoangVanBao.md` |

## Cách chạy (Windows PowerShell, Python 3.13.17)

Các lệnh pipeline phải chạy từ `starter/`, vì đường dẫn dữ liệu và kết quả tương đối với thư mục đó:

```powershell
Set-Location starter
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Tải PDF từ link trong data/manifest.json, đặt tại data/raw/principles-management.pdf
python scripts\check_gold.py
python scripts\check_evidence.py
python -m src.run --split dev --tag _v2_b1000
python -m src.run --split test
```

`requirements.txt` cài Chroma `1.5.9` và FastEmbed `0.9.1`; không cần cài lặp lại. Model `BAAI/bge-small-en-v1.5` (384 chiều) chạy local và được tải ở lần đầu, chi phí API là 0. Không cần Docker. Chroma lưu tại `data/chroma*` (được gitignore); `CHROMA_PATH`, nếu đặt, sẽ thay đường dẫn mặc định. Phiên bản môi trường ghi ở `starter/results/pip_freeze.txt`.

Lệnh chạy test ghi lại trace, summary và file audit tương ứng. Không chạy lại sau khi đã nhập nhãn thủ công, trừ khi muốn tạo lại các kết quả đó. Kết quả benchmark đã lưu trong `starter/results/`; lệnh trên dành cho tái tạo trong một bản làm việc sạch.
