import json
from datetime import date

rows = {r["page"]: r["chars"] for r in json.load(open("data/raw/principles-management.pdf.pages.json"))}
ranges = {"2": (35, 58), "13": (375, 399)}

def chars(a, b):
    return sum(rows[p] for p in range(a, b + 1))

chapters = {
    ch: {
        "pdf_pages": [a, b],
        "page_count": b - a + 1,
        "total_chars": chars(a, b),
    }
    for ch, (a, b) in ranges.items()
}

manifest = {
    "corpus_name": "OpenStax Principles of Management (chương 2 và 13)",
    "created_at": str(date.today()),
    "filter_fields": [
        {
            "name": "chapter",
            "type": "int",
            "source": "mục lục (outline) nhúng trong PDF gốc",
            "values": [2, 13],
            "reason": "hai chương khác chủ đề (ra quyết định và lãnh đạo) nên phân biệt được phạm vi tìm kiếm",
            "limitation": "không giúp khi câu hỏi liên quan nhiều chương; chỉ có 2 giá trị",
        }
    ],
    "sources": [
        {
            "source_id": "principles-management",
            "title": "Principles of Management (OpenStax, Rice University)",
            "source_path_or_url": "https://assets.openstax.org/oscms-prodcms/media/documents/principles-management_-_WEB.pdf",
            "license_or_permission": "CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-ShareAlike), theo trang Preface: https://openstax.org/books/principles-management/pages/preface",
            "accessed_at": "2026-11-13",
            "physical_pages": 605,
            "counted_pages": "35-58, 375-399",
            "counted_page_count": sum(c["page_count"] for c in chapters.values()),
            "excluded_pages": "toàn bộ trang ngoài hai khoảng trên (bìa, mục lục, preface, các chương khác, ôn tập cuối chương, tài liệu tham khảo, index)",
            "chapters": chapters,
            "total_chars": sum(c["total_chars"] for c in chapters.values()),
            "notes": "gold_page dùng số trang PDF (khớp trình đọc PDF), không dùng số trang in trên sách",
        }
    ],
}

with open("data/manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print(json.dumps(manifest, ensure_ascii=False, indent=2))