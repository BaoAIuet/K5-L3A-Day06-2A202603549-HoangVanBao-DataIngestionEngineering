import sys
from pypdf import PdfReader

reader = PdfReader(sys.argv[1])

def walk(items, depth=0):
    for it in items:
        if isinstance(it, list):
            walk(it, depth + 1)
        else:
            page = reader.get_destination_page_number(it) + 1  # đổi sang số trang tính từ 1
            if depth <= 1:  # chỉ in cấp chương và cấp mục lớn
                print("  " * depth + f"{it.title}  ->  trang PDF {page}")

walk(reader.outline)
print("Tổng số trang:", len(reader.pages))