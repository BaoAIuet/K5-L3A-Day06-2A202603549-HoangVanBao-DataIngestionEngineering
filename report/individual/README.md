# Báo cáo cá nhân

Họ và tên:Hoàng Văn Bảo
MSSV: 2A202603549

Corpus: _Principles of Management_ (OpenStax), chương 2 (PDF trang 35–58) và chương 13 (trang 375–399), 49 trang. Nguồn và giấy phép: `data/manifest.json` (CC BY-NC-SA 4.0, © OpenStax/Rice University). Các file kết quả có chứa đoạn trích ngắn từ sách, dùng theo cùng giấy phép và có ghi nguồn. PDF gốc không đưa vào repo; tải theo link trong manifest.

## Bản đồ file

| Yêu cầu                | Đường dẫn                                                                     |
| ---------------------- | ----------------------------------------------------------------------------- |
| Code pipeline          | `starter/src/`                                                                |
| Manifest               | `data/manifest.json` (bản gốc code dùng: `starter/data/manifest.json`)        |
| Benchmark, gold, split | `benchmark/benchmark.json` (bản gốc code dùng: `starter/data/benchmark.json`) |
| Experiment log         | `artifacts/experiment_log.csv`                                                |
| Trace, nhãn audit, log | `starter/results/`                                                            |
| Báo cáo                | `report/individual/2A202603549_HoangVanBao.md`                                |

## Cách chạy (Windows PowerShell, Python 3.13)

```powershell
cd starter
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install chromadb==1.5.9 fastembed==0.9.1
# tải PDF từ link trong data/manifest.json, lưu vào starter/data/raw/principles-management.pdf
python scripts\dump_pages.py
python scripts\check_gold.py
python -m src.run --split dev
python -m src.run --split test
```

Không cần Docker; vector store là Chroma lưu tại `starter/data/chroma*` (bị gitignore). Embedding: `BAAI/bge-small-en-v1.5` (384 chiều, chạy local), chi phí 0. Phiên bản đầy đủ: `starter/results/pip_freeze.txt`. **[ĐIỀN: đối chiếu lệnh thực tế]**
