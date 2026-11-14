# Nhật ký xử lý dữ liệu

Nguồn: OpenStax _Principles of Management_ (605 trang PDF). Chỉ tính chương 2 (trang PDF 35-58, 24 trang) và chương 13 (trang PDF 375-399, 25 trang): 49 trang, 165.375 ký tự. Số trang dùng trong `gold_page` và metadata là số trang PDF. Số in trên sách lệch 14 (PDF 41 = trang in 27; PDF 383 = trang in 369).

## Kiểm tra trang rỗng

`scripts/count_pages.py` đánh dấu 19 trang ít chữ (<300 ký tự) trong toàn sách, đều nằm ngoài hai khoảng đã chọn. Trong 49 trang được tính, không trang nào dưới 800 ký tự.

## Lỗi gặp và cách xử lý (`src/normalize.py`)

| #   | Triệu chứng                                    | Ví dụ                                                                   | Xử lý                                                                                                                                                         |
| --- | ---------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Footer trang lẻ                                | `13.3 • Leader Emergence 369`                                           | regex, loại bỏ                                                                                                                                                |
| 2   | Header trang chẵn, 2 dạng                      | `380 13 • Leadership`; `Access for free at openstax.org`                | regex, loại bỏ                                                                                                                                                |
| 3   | Nhãn lẫn vào đoạn                              | `CONCEPT CHECK`                                                         | loại bỏ                                                                                                                                                       |
| 4   | Caption Exhibit nhiều dòng                     | `Exhibit 2.7 The Devils Advocate ...` kèm các dòng nối tiếp             | loại từ dòng `Exhibit` đến dòng `Credit (...)` (nhìn trước 6 dòng); nếu không có dòng Credit thì loại các dòng nối tiếp bắt đầu bằng chữ thường, `(` hoặc năm |
| 5   | Chú thích ảnh còn sót                          | `... Credit (New America/ flickr/ Attribution 2.0 Generic (CC BY 2.0))` | regex `CREDIT`, cắt phần credit                                                                                                                               |
| 6   | Số chú thích dính sau dấu câu                  | `goals.25 People`, `findings,76 Fiedler`                                | regex, xóa số                                                                                                                                                 |
| 7   | Xuống dòng cứng, không có dòng trống giữa đoạn |                                                                         | ghép dòng thành đoạn; ngắt đoạn khi dòng trước kết thúc câu và ngắn hơn 75% độ rộng dòng điển hình                                                            |
| 8   | Từ bị ngắt bằng gạch nối cuối dòng             | `well-` / `understood`                                                  | ghép, giữ gạch nối                                                                                                                                            |
| 9   | Tiêu đề mục đánh số bị dính vào câu hỏi        | `2.3 Programmed and Nonprogrammed Decisions`                            | nhận dạng heading bằng regex; câu hỏi đánh số tách riêng                                                                                                      |
| 10  | Hiển thị `â€¢`                                 |                                                                         | chỉ là lỗi hiển thị của `Get-Content`; file UTF-8 đúng (đã kiểm tra)                                                                                          |
| 11  | Câu bị cắt ở cuối trang                        | `...increase staff by 30% every`                                        | không ghép xuyên trang; mỗi chunk thuộc đúng một trang (xem giới hạn)                                                                                         |

Kiểm tra sau làm sạch: `scripts/check_evidence.py` xác nhận 21/21 đoạn evidence trong benchmark vẫn khớp (so khớp sau khi bỏ dấu câu, khoảng trắng, hoa/thường).

## Giới hạn còn lại (không sửa)

- Ranh giới đoạn suy ra từ độ dài dòng nên bỏ sót khi đoạn trước kết thúc sát lề phải (trang 45: `Consider a manager ...` bị gộp vào đoạn trước).
- Chữ dính từ chính PDF: `attorneyBob`, `isbeing`, `andmilitary`.
- Nhiễu còn sót: dòng `Table 2.3 (Attribution: ...)` (trang 58), dòng tham khảo `May-June 1971. How to choose a leadership pattern...` (trang 385), câu hỏi ôn tập cuối mục lẫn vào trang 41 và 43, danh sách URL nguồn ở trang 36-37.
- Câu bị cắt qua ranh giới trang không được ghép, nên một câu evidence nằm ở hai trang sẽ không khớp trọn trong một chunk.
