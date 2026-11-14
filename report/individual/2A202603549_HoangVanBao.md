# Báo cáo cá nhân — Day 6

Họ tên: Hoàng Văn Bảo · MSSV: 2A202603549

## Dữ liệu và pipeline

- Chủ đề, nguồn/quyền, số trang và quy tắc tính trang: giáo trình _Principles of Management_ (OpenStax, Rice University), chương 2 "Managerial Decision-Making" (trang PDF 35–58, 24 trang) và chương 13 "Leadership" (trang PDF 375–399, 25 trang), tổng 49 trang, 165.375 ký tự. Giấy phép CC BY-NC-SA 4.0 (theo trang Preface), tải ngày 2026-11-13 từ https://assets.openstax.org/oscms-prodcms/media/documents/principles-management_-_WEB.pdf. PDF gốc có 605 trang; chỉ tính hai khoảng trên, loại bìa, mục lục, các chương khác, phần ôn tập cuối chương, tài liệu tham khảo, index. Kiểm tra bằng `scripts/count_pages.py`: không trang nào trong hai khoảng có dưới 800 ký tự. `gold_page` dùng số trang PDF (số in trên sách lệch 14 trang, ví dụ trang PDF 41 in là 27). Không commit PDF (giấy phép NC-SA); manifest ở `data/manifest.json`.
- Chuẩn hóa, lỗi và giới hạn: chuẩn hóa Unicode NFC; `src/normalize.py` loại số chú thích, caption exhibit, ghi công ảnh, chân trang/đầu trang, nhãn "CONCEPT CHECK", đoạn nối tiếp của exhibit; phân loại heading/đoạn/bullet. Evidence của 21/21 câu hỏi khớp sau chuẩn hóa (`scripts/check_gold.py`, `scripts/check_evidence.py`). Log xử lý: `results/processing_log.md` **[ĐIỀN: xác nhận nội dung]**. Giới hạn đã biết, chưa sửa để giữ nguyên cấu hình đóng băng: (1) `pypdf` làm mất dấu cách khi nối dòng (`relyon`, `towhom`, `orbe accepted`); (2) bảng (Table 2.1, 2.3) bị trích thành văn bản phẳng.
- Embedding model/provider/version/số chiều, vector store/version, metric, lệnh chạy và chi phí: `BAAI/bge-small-en-v1.5` qua `fastembed==0.9.1` (chạy local), 384 chiều; cách xử lý query/document: **[ĐIỀN]**. Vector store: Chroma `chromadb==1.5.9`, PersistentClient, thư mục `data/chroma*`, metric **[ĐIỀN: cosine?]**, Python **[ĐIỀN: phiên bản]**, `results/pip_freeze.txt` lưu phiên bản đầy đủ. Lệnh: `python -m src.run --split dev --tag _v2_b1000` và `python -m src.run --split test` **[ĐIỀN: đối chiếu lệnh thực tế]**. Chi phí 0 USD (không dùng dịch vụ trả phí).
- Metadata bắt buộc, trường lọc bổ sung, nguồn giá trị và lý do chọn: mỗi chunk có `document_id`, `source` (`principles-management`), `page` (số trang PDF), `chunk_id` (dạng `principles-management-p041-pg01`) và trường lọc `chapter` (số nguyên 2 hoặc 13) lấy từ mục lục nhúng trong PDF. Chọn `chapter` vì hai chương khác chủ đề nên là hai phạm vi phân biệt được. Hạn chế: chỉ có 2 giá trị, không phân biệt các mục trong cùng một chương.

## Cấu hình và benchmark

- A / B / C (tham số cụ thể, khác biệt duy nhất B–C):
  - A: cắt cố định 1000 ký tự, overlap 100, trong từng trang, lùi về khoảng trắng gần nhất.
  - B: gom theo đoạn trong từng trang, tối đa 1000 ký tự, tách theo câu khi đoạn dài hơn ngưỡng, gắn tiêu đề mục vào đầu chunk. Có thử thêm ngưỡng 600 ký tự.
  - C: dùng đúng chunk và vector của B; khác biệt duy nhất là thêm metadata filter `chapter` ở bước truy xuất khi câu hỏi có trường `filter`.
  - Cùng corpus, cùng model, cùng top-k (3), cùng benchmark cho cả ba cấu hình.
- ≥20 câu: phân chia ≥15 dev / ≥5 test, câu metadata filter và cách kiểm chứng evidence: 21 câu, 15 dev / 6 test. Tách bằng `scripts/rebalance_split.py` (seed cố định), chọn câu chuyển sang dev không thuộc nhóm filter để test vẫn giữ 3 câu filter (q13, q15, q17); dev có 1 câu filter (q21). Mỗi câu có `evidence_quote` nguyên văn, số trang PDF và đáp án ngắn; `scripts/check_gold.py` kiểm tra cấu trúc, `scripts/check_evidence.py` xác nhận evidence khớp với trang gold sau khi làm sạch (21/21). Thứ tự thời gian của split: [ĐIỀN: kết quả `Get-ChildItem data\benchmark.json, results\traces_dev.jsonl | Select-Object Name, LastWriteTime` và ngày giờ commit benchmark. Benchmark được commit sau các lần chạy dev nên git không chứng minh thứ tự; chỉ ghi đúng những gì thời gian file cho thấy].
- Tiêu chí chọn chiến lược đã chốt trước khi xem test: chọn theo dev, ưu tiên Evidence Hit@3, sau đó Hit@1 và MRR. Tiêu chí này được đặt sau khi đã xem kết quả dev và trước khi chạy test. Test chạy đúng một lần (`--split test`), không chỉnh tham số nào sau đó. Cấu hình chọn trên dev là A.

## Kết quả

Dev: 15 câu. Test: 6 câu. Ba lần chạy dev khác nhau ở mức làm sạch dữ liệu (v1 chưa lọc `Credit`/đoạn rác Exhibit, v2 đã lọc) và ngưỡng B.

| Strategy     | Split  | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Thời gian | Chi phí |
| ------------ | ------ | ----------- | -------------------- | ----------- | --------- | ------- |
| A            | dev v1 | 10/15       | 15/15                | 190         | [ĐIỀN]    | 0       |
| B            | dev v1 | 9/15        | 12/15                | 225         | [ĐIỀN]    | 0       |
| C            | dev v1 | 9/15        | 12/15                | 225         | [ĐIỀN]    | 0       |
| A            | dev v2 | 11/15       | 15/15                | 190         | [ĐIỀN]    | 0       |
| B (max 1000) | dev v2 | 9/15        | 11/15                | 224         | [ĐIỀN]    | 0       |
| C (max 1000) | dev v2 | 9/15        | 11/15                | 224         | [ĐIỀN]    | 0       |
| B (max 600)  | dev v2 | 6/15        | 10/15                | 357         | [ĐIỀN]    | 0       |
| C (max 600)  | dev v2 | 6/15        | 10/15                | 357         | [ĐIỀN]    | 0       |
| A            | test   | 4/6         | 5/6                  | 190         | [ĐIỀN]    | 0       |
| B (max 1000) | test   | 4/6         | 6/6                  | 224         | [ĐIỀN]    | 0       |
| C (max 1000) | test   | 4/6         | 6/6                  | 224         | [ĐIỀN]    | 0       |

MRR dev v2: A 0.856, B/C (1000) 0.656, B/C (600) 0.522. MRR test: A 0.722, B/C 0.806.

| Strategy | Coherence trung bình /2 (n) | Metadata đủ và đúng (n/N) | Filter tuân thủ (n/N hoặc N/A)                                        | Grounding 0/1/2 (số câu) và trung bình /2 |
| -------- | --------------------------- | ------------------------- | --------------------------------------------------------------------- | ----------------------------------------- |
| A        | [ĐIỀN] (20)                 | [ĐIỀN]                    | N/A (không dùng filter); top-3 của các câu filter vẫn đúng chương 9/9 | [ĐIỀN]                                    |
| B        | [ĐIỀN] (20)                 | [ĐIỀN]                    | N/A (không dùng filter); top-3 của các câu filter vẫn đúng chương 9/9 | [ĐIỀN]                                    |
| C        | dùng chunk của B            | [ĐIỀN]                    | 9/9 (3 câu filter × top-3, đúng chương)                               | [ĐIỀN]                                    |

Đường dẫn trace, nhãn thủ công và cách chọn mẫu: trace ở `results/traces_dev*.jsonl`, `results/traces_test.jsonl` (top-3 đầy đủ, cờ `page_hit`, `evidence_hit`); thống kê ở `results/summary_*.json`. Nhãn thủ công ở `results/audit_coherence_v2_b1000.csv` (20 chunk A + 20 chunk B, lấy ngẫu nhiên với seed 42) và `results/audit_grounding_dev_v2_b1000.csv` (45 dòng) [ĐIỀN: và `audit_grounding_test.csv` nếu chấm]. Cách chấm: thang 0-2; coherence 2 = đọc riêng vẫn hiểu trọn ý, 1 = hiểu được nhưng thiếu hoặc thừa một phần, 0 = cụt hoặc chủ yếu là nhiễu; grounding 2 = top-3 đủ để trả lời đúng và dẫn đúng nguồn, 1 = có manh mối nhưng thiếu, 0 = không đủ hoặc sai. [ĐIỀN: nêu rõ nhãn do bạn chấm; nếu có dùng gợi ý của công cụ AI thì ghi là bản nháp bạn đã kiểm tra và tự quyết điểm].

## Phân tích và kết luận

- So sánh A–B và B–C; 2 ví dụ sai có ID câu và nguồn:
  - A–B: trên dev, A vượt B ở Evidence Hit@3 (15/15 so với 11/15) và MRR (0.856 so với 0.656). Trên test, chiều ngược lại: B 6/6, A 5/6 (Hit@1 bằng nhau, 4/6). Dev và test cho kết quả ngược nhau và chênh lệch chỉ là vài câu, nên không có cấu hình nào vượt trội ổn định. Chia B nhỏ hơn (600 ký tự, 357 chunk) làm kết quả dev tệ hơn (Hit@3 10/15), trái với giả thuyết ban đầu rằng chunk nhỏ sẽ truy xuất tốt hơn. Ở A có hai khác biệt cùng lúc so với B (overlap 100 ký tự và không gắn tiêu đề), nên chưa tách được yếu tố nào gây ra chênh lệch.
  - B–C: giống hệt nhau ở mọi chỉ số, trên cả dev (1 câu filter) lẫn test (3 câu filter). Ở cả 3 câu filter của test, top-3 của A và B không lọc đã nằm trọn trong đúng chương, nên filter không còn việc để làm. Không có bằng chứng filter cải thiện truy xuất trên benchmark này.
  - Ví dụ sai 1, câu q17 (test, nguồn `principles-management`, trang PDF 394, mô hình Fiedler): A không có chunk nào chứa evidence trong top-3; top-3 toàn là trang 379-380 (khái niệm lãnh đạo chung). B và C đưa evidence lên hạng 3. Đây là kiểu lỗi đoạn lân cận cùng chủ đề lấn át khi câu hỏi diễn đạt lại.
  - Ví dụ sai 2, câu q07 (dev, trang PDF 383, "emergent leader"; số liệu từ lần chạy v1, cần kiểm lại trên v2): B không có trang gold trong top-3, chunk chứa evidence (`principles-management-p383-pg00`, dài 676 ký tự, gom tiêu đề và đoạn dẫn) nằm hạng 6. A đưa evidence lên hạng 2. Câu hỏi không chứa từ "emergent" nên truy xuất kéo về các đoạn định nghĩa lãnh đạo chung ở trang 376-378.
  - Lỗi ranh giới chunk (dev v1, A): ở q03 (trang 41) và q10 (trang 57), top-1 đã đúng trang nhưng câu evidence nằm ở chunk kế bên, nên chỉ tính là trúng ở hạng 2.
- Chiến lược chọn, đánh đổi, điều kiện áp dụng: chọn A theo dev. A đơn giản và truy xuất tốt hơn trên dev, nhưng nhiều chunk cắt giữa câu (kết quả coherence ở bảng trên [ĐIỀN: nhận xét theo điểm bạn chấm]). B giữ cấu trúc đoạn nên dễ đọc hơn nhưng chunk gom nhiều ý có thể bị đẩy xuống hạng thấp. Nếu ưu tiên chunk đọc được để đưa cho người hoặc mô hình sinh câu trả lời, B hợp lý hơn dù Hit@k trên dev thấp hơn; nếu ưu tiên truy xuất, A trên dev. Test không xác nhận lợi thế của A. Metadata filter không đổi Hit@k ở đây nhưng vẫn cần cho truy vết nguồn (trang, tài liệu) và sẽ có ích khi corpus có nhiều chương/tài liệu dùng chung từ khóa.
- Hạn chế của dữ liệu, nhãn, test nhỏ, đo thời gian/chi phí: chỉ 2 chương của một giáo trình tiếng Anh, 21 câu tập trung vào vài trang gold (41, 45, 57, 383, 394) nên dễ đạt Hit@3 cao và khó phân biệt cấu hình. Dev 15 câu (mỗi câu 6,7 điểm phần trăm) và test 6 câu (mỗi câu 16,7 điểm phần trăm) là mẫu quá nhỏ để kết luận; dev và test cho chiều ngược nhau. Chỉ 4 câu dùng filter (dev 1, test 3) và `chapter` chỉ có 2 giá trị. Chunk không vượt ranh giới trang. Metric Evidence Hit@3 đòi chunk chứa trọn đoạn evidence nên phạt cả khi truy xuất đúng trang. Nhãn thủ công do một người chấm, không có độ đồng thuận giữa người chấm. Chỉ dùng một embedding model nhỏ (lượng tử hóa), chạy trên CPU; thời gian đo một lần trên một máy; chi phí tiền bằng 0 do chạy local. Benchmark được commit sau các lần chạy dev nên thứ tự chốt split không có bằng chứng trong git.
- Nếu làm lại hoặc mở rộng, cải tiến gì? Viết 40-60 câu phủ nhiều trang hơn và tách dev/test lớn hơn, commit split trước khi chạy; thêm câu có từ khóa lặp ở cả hai chương để kiểm tra filter thật sự; ghép chunk xuyên trang; thử overlap cho B hoặc bỏ tiêu đề khỏi chunk để tách riêng hai yếu tố đang bị trộn ở A–B; thử embedding model lớn hơn và tìm kiếm lai (từ khóa + vector) cho câu diễn đạt lại; chấm nhãn bởi hai người.

## Ghi chú về công cụ

[ĐIỀN: theo `RULES.md`, nêu cách bạn đã dùng AI (ví dụ trợ giúp viết và gỡ lỗi mã, gợi ý nháp nhãn đánh giá) và phần bạn tự thực hiện, kiểm tra và quyết định.]
