# Báo cáo cá nhân — Day 6

Họ tên: Hoàng Văn Bảo · MSSV: 2A202603549

## Dữ liệu và pipeline

- Chủ đề, nguồn/quyền, số trang và quy tắc tính trang: giáo trình _Principles of Management_ (OpenStax, Rice University), chương 2 "Managerial Decision-Making" (trang PDF 35–58, 24 trang) và chương 13 "Leadership" (trang PDF 375–399, 25 trang), tổng 49 trang, 165.375 ký tự. Giấy phép CC BY-NC-SA 4.0 (theo trang Preface), tải ngày 2026-11-13 từ https://assets.openstax.org/oscms-prodcms/media/documents/principles-management_-_WEB.pdf. PDF gốc có 605 trang; chỉ tính hai khoảng trên, loại bìa, mục lục, các chương khác, phần ôn tập cuối chương, tài liệu tham khảo, index. Kiểm tra bằng `starter/scripts/count_pages.py`: không trang nào trong hai khoảng có dưới 800 ký tự. `gold_page` dùng số trang PDF (số in trên sách lệch 14 trang, ví dụ trang PDF 41 in là 27). Không commit PDF; manifest ở `starter/data/manifest.json`.
- Chuẩn hóa, lỗi và giới hạn: chuẩn hóa Unicode NFC; `starter/src/normalize.py` loại số chú thích, caption exhibit, ghi công ảnh, chân trang/đầu trang, nhãn "CONCEPT CHECK", đoạn nối tiếp của exhibit; phân loại heading/đoạn/bullet. Evidence của 21/21 câu hỏi khớp sau chuẩn hóa (`starter/scripts/check_gold.py`, `starter/scripts/check_evidence.py`). Nhật ký xử lý chi tiết ở `starter/results/processing_log.md`. Giới hạn đã biết, chưa sửa để giữ nguyên cấu hình đóng băng: (1) `pypdf` làm mất dấu cách khi nối dòng (`relyon`, `towhom`, `orbe accepted`); (2) bảng (Table 2.1, 2.3) bị trích thành văn bản phẳng.
- Embedding model/provider/version/số chiều, vector store/version, metric, lệnh chạy và chi phí: `BAAI/bge-small-en-v1.5` qua `fastembed==0.9.1` (local/ONNX), 384 chiều; tài liệu dùng `passage_embed`, query dùng `query_embed` của fastembed. Vector store là Chroma `chromadb==1.5.9`, `PersistentClient`, cosine (`hnsw:space=cosine`); A và B lưu ở collection riêng, C dùng collection B với filter. Đường dẫn mặc định là `starter/data/chroma*`; các phiên bản thư viện được lưu trong `starter/results/pip_freeze.txt`. Môi trường `.venv` được kiểm tra là Python 3.13.17 ngày 2026-11-14. Lệnh chạy từ `starter/`: `python -m src.run --split dev --tag _v2_b1000` và `python -m src.run --split test`; log thí nghiệm ghi các lần chạy. Chi phí 0 USD (không dùng dịch vụ trả phí). Mã dùng `upsert` theo chunk ID và xóa chunk cũ không còn trong lần nạp lại.
- Metadata bắt buộc, trường lọc bổ sung, nguồn giá trị và lý do chọn: mỗi chunk có `document_id` (`principles-management`), `source` (URL PDF), `page` (số trang PDF), `chunk_id` (dạng `principles-management-p057-fx00` hoặc `principles-management-p057-pg00`) và trường lọc `chapter` (số nguyên 2 hoặc 13). Các khoảng trang chương được cấu hình trước trong pipeline theo ranh giới chương đã xác định từ tài liệu. Chọn `chapter` vì hai chương khác chủ đề nên là hai phạm vi phân biệt được. Hạn chế: chỉ có 2 giá trị, không phân biệt các mục trong cùng một chương.

## Cấu hình và benchmark

- A / B / C (tham số cụ thể, khác biệt duy nhất B–C):
  - A: cắt cố định 1000 ký tự, overlap 100, trong từng trang, lùi về khoảng trắng gần nhất.
  - B: gom theo đoạn trong từng trang, tối đa 1000 ký tự, tách theo câu khi đoạn dài hơn ngưỡng, gắn tiêu đề mục vào đầu chunk. Có thử thêm ngưỡng 600 ký tự.
  - C: dùng đúng chunk và vector của B; khác biệt duy nhất là thêm metadata filter `chapter` ở bước truy xuất khi câu hỏi có trường `filter`.
  - Cùng corpus, cùng model, cùng top-k (3), cùng benchmark cho cả ba cấu hình.
- ≥20 câu: phân chia ≥15 dev / ≥5 test, câu metadata filter và cách kiểm chứng evidence: 21 câu, 15 dev / 6 test. Tách bằng `starter/scripts/rebalance_split.py` (seed cố định), chọn câu chuyển sang dev không thuộc nhóm filter để test vẫn giữ 3 câu filter (q13, q15, q17); dev có 1 câu filter (q21). Mỗi câu có `evidence_quote` nguyên văn, số trang PDF và đáp án ngắn; `starter/scripts/check_gold.py` kiểm tra cấu trúc, `starter/scripts/check_evidence.py` xác nhận evidence khớp với trang gold sau khi làm sạch (21/21). Git ghi nhận benchmark và các lần chạy cùng ngày 2026-11-13, nhưng không có bằng chứng thời gian đủ chính xác để xác nhận split được commit trước mọi lần chạy dev; vì vậy không khẳng định thứ tự này như một holdout đã được chứng minh độc lập.
- Tiêu chí chọn chiến lược đã chốt trước khi xem test: chọn theo dev, ưu tiên Evidence Hit@3, sau đó Hit@1 và MRR. Tiêu chí này được đặt sau khi đã xem kết quả dev và trước khi chạy test. Test chạy đúng một lần (`--split test`), không chỉnh tham số nào sau đó. Cấu hình chọn trên dev là A.

Dev: 15 câu. Test: 6 câu. Ba lần chạy dev khác nhau ở mức làm sạch dữ liệu (v1 chưa lọc `Credit`/đoạn rác Exhibit, v2 đã lọc) và ngưỡng B.

## Kết quả

| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Tổng thời gian lượt chạy (s) | Chi phí |
| -------- | ----- | ----------- | -------------------- | ----------- | ---------------------------- | ------- |
| A        | dev   | 11/15       | 15/15                | 190         | 23,4                         | 0       |
| B        | dev   | 9/15        | 11/15                | 224         | 23,4                         | 0       |
| C        | dev   | 9/15        | 11/15                | 224         | 23,4                         | 0       |
| A        | test  | 4/6         | 5/6                  | 190         | 30,5                         | 0       |
| B        | test  | 4/6         | 6/6                  | 224         | 30,5                         | 0       |
| C        | test  | 4/6         | 6/6                  | 224         | 30,5                         | 0       |

Thời gian là tổng của một lượt chạy gồm các chiến lược A/B/C trên split tương ứng, không phải thời gian riêng của từng chiến lược.

MRR dev v2: A 0.856, B/C (1000) 0.656, B/C (600) 0.522. MRR test: A 0.722, B/C 0.806.

| Strategy | Coherence trung bình /2 (n) | Metadata đủ và đúng (n/N) | Filter tuân thủ                                  | Grounding 0/1/2; trung bình /2 |
| -------- | --------------------------- | ------------------------- | ------------------------------------------------ | ------------------------------ |
| A        | 1.05 (20 chunk)             | 15/15                     | N/A (không áp dụng filter)                       | 0/0/5; 2.00                    |
| B        | 1.40 (20 chunk)             | 15/15                     | N/A (không áp dụng filter)                       | 0/0/5; 2.00                    |
| C        | dùng chunk của B            | 15/15                     | 3/3 câu (9/9 chunk; q13, q15, q17)               | 0/0/5; 2.00                    |

Đường dẫn trace, nhãn thủ công và cách chọn mẫu: trace ở `starter/results/traces_dev*.jsonl`, `starter/results/traces_test.jsonl` (top-3 đầy đủ, cờ `page_hit`, `evidence_hit`); thống kê ở `starter/results/summary_*.json`. Nhãn coherence ở `starter/results/audit_coherence_v2_b1000.csv` (20 chunk A + 20 chunk B, lấy ngẫu nhiên với seed 42); grounding dev ở `starter/results/audit_grounding_dev_v2_b1000.csv` (45 dòng); grounding test ở `starter/results/audit_grounding_test.csv` (5 câu × 3 chiến lược). Metadata test ở `starter/results/audit_metadata_test.csv` (5 câu × top-3 × 3 chiến lược). Thang điểm 0–2: coherence 2 = đọc riêng vẫn hiểu trọn ý, 1 = hiểu được nhưng thiếu hoặc thừa một phần, 0 = cụt hoặc chủ yếu là nhiễu; grounding 2 = top-3 đủ để trả lời và truy nguồn, 1 = có manh mối nhưng thiếu, 0 = không đủ hoặc sai. Các nhãn grounding và metadata cuối cùng do tác giả xem trace/store, nhập và xác nhận; AI hỗ trợ giải thích quy trình audit và rà cách diễn giải, không thay thế quyết định chấm.

Mẫu coherence gồm 20 chunk ngẫu nhiên mỗi chiến lược, không phải cùng 10 vị trí nguồn được ghép cặp theo hướng dẫn; vì vậy các điểm trung bình là mô tả mẫu đã chấm, chưa phải so sánh coherence ghép cặp hoàn toàn tương đương.

## Phân tích và kết luận

- So sánh A–B và B–C; 2 ví dụ sai có ID câu và nguồn:
  - A–B: trên dev, A vượt B ở Evidence Hit@3 (15/15 so với 11/15) và MRR (0.856 so với 0.656). Trên test, chiều ngược lại: B 6/6, A 5/6 (Hit@1 bằng nhau, 4/6). Dev và test cho kết quả ngược nhau và chênh lệch chỉ là vài câu, nên không có cấu hình nào vượt trội ổn định. Chia B nhỏ hơn (600 ký tự, 357 chunk) làm kết quả dev tệ hơn (Hit@3 10/15), trái với giả thuyết ban đầu rằng chunk nhỏ sẽ truy xuất tốt hơn. Ở A có hai khác biệt cùng lúc so với B (overlap 100 ký tự và không gắn tiêu đề), nên chưa tách được yếu tố nào gây ra chênh lệch.
  - B–C: giống hệt nhau ở mọi chỉ số, trên cả dev (1 câu filter) lẫn test (3 câu filter). Ở cả 3 câu filter của test, top-3 của A và B không lọc đã nằm trọn trong đúng chương, nên filter không còn việc để làm. Không có bằng chứng filter cải thiện truy xuất trên benchmark này.
  - Ví dụ sai 1, câu q17 (test, nguồn `principles-management`, trang PDF 394, mô hình Fiedler): A không có chunk nào chứa evidence trong top-3; top-3 toàn là trang 379-380 (khái niệm lãnh đạo chung). B và C đưa evidence lên hạng 3. Đây là kiểu lỗi đoạn lân cận cùng chủ đề lấn át khi câu hỏi diễn đạt lại.
  - Ví dụ sai 2, câu q07 (dev, trang PDF 383, "emergent leader"; trace `traces_dev_v2_b1000.jsonl`): A đưa chunk chứa evidence lên hạng 2; B và C không có chunk gold/evidence trong top-3, thay vào đó lấy các đoạn định nghĩa lãnh đạo chung ở trang 376–378. Câu hỏi diễn đạt lại nhưng không dùng từ "emergent", nên nội dung khái quát về leadership cạnh tranh với evidence cụ thể.
  - Lỗi ranh giới chunk (dev v1, A): ở q03 (trang 41) và q10 (trang 57), top-1 đã đúng trang nhưng câu evidence nằm ở chunk kế bên, nên chỉ tính là trúng ở hạng 2.
- Chiến lược chọn, đánh đổi, điều kiện áp dụng: chọn A theo dev. A đơn giản và truy xuất tốt hơn trên dev, nhưng coherence trung bình thấp hơn B (1.05 so với 1.40); kết quả mẫu coherence chưa ghép cặp cùng vị trí nên chỉ xem là tín hiệu mô tả. B giữ cấu trúc đoạn nên dễ đọc hơn nhưng chunk gom nhiều ý có thể bị đẩy xuống hạng thấp. Nếu ưu tiên chunk đọc được để đưa cho người hoặc mô hình sinh câu trả lời, B hợp lý hơn dù Hit@k trên dev thấp hơn; nếu ưu tiên retrieval theo tiêu chí dev đã chọn, A đứng đầu. Test không xác nhận lợi thế ổn định của A. Filter không cải thiện chỉ số trên bộ câu hỏi này; nhưng `chapter` vẫn giúp giới hạn phạm vi khi câu hỏi có filter và metadata hỗ trợ truy vết nguồn.
- Hạn chế của dữ liệu, nhãn, test nhỏ, đo thời gian/chi phí: chỉ 2 chương của một giáo trình tiếng Anh, 21 câu tập trung vào vài trang gold (41, 45, 57, 383, 394) nên dễ đạt Hit@3 cao và khó phân biệt cấu hình. Dev 15 câu (mỗi câu 6,7 điểm phần trăm) và test 6 câu (mỗi câu 16,7 điểm phần trăm) là mẫu quá nhỏ để kết luận; dev và test cho chiều ngược nhau. Chỉ 4 câu dùng filter (dev 1, test 3) và `chapter` chỉ có 2 giá trị. Chunk không vượt ranh giới trang. Metric Evidence Hit@3 đòi chunk chứa trọn đoạn evidence nên phạt cả khi truy xuất đúng trang. Nhãn thủ công do một người chấm, không có độ đồng thuận giữa người chấm. Chỉ dùng một embedding model nhỏ (lượng tử hóa), chạy trên CPU; thời gian đo một lần trên một máy; chi phí tiền bằng 0 do chạy local. Benchmark được commit sau các lần chạy dev nên thứ tự chốt split không có bằng chứng trong git.
- Nếu làm lại hoặc mở rộng, cải tiến gì? Viết 40-60 câu phủ nhiều trang hơn và tách dev/test lớn hơn, commit split trước khi chạy; thêm câu có từ khóa lặp ở cả hai chương để kiểm tra filter thật sự; ghép chunk xuyên trang; thử overlap cho B hoặc bỏ tiêu đề khỏi chunk để tách riêng hai yếu tố đang bị trộn ở A–B; thử embedding model lớn hơn và tìm kiếm lai (từ khóa + vector) cho câu diễn đạt lại; chấm nhãn bởi hai người.

## Ghi chú về công cụ

AI assistant được dùng để giải thích quy trình audit, hướng dẫn thao tác tổng hợp bảng và rà cách diễn giải kết quả. Tác giả chạy pipeline, kiểm tra trace và metadata, nhập các nhãn cuối cùng, đối chiếu kết quả với CSV và chịu trách nhiệm về lựa chọn chiến lược cũng như kết luận. Các gợi ý tự động trong audit metadata được xem là gợi ý, không được coi là nhãn nếu chưa đối chiếu với trace/store.
