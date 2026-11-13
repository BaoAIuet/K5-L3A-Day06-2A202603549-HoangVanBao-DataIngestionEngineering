import re
import unicodedata

# Footer trang lẻ: "13.3 • Leader Emergence     369"
FOOTER_ODD = re.compile(r"^\s*\d{1,2}\.\d{1,2}\s*[•·]\s*.+?\s+\d{1,3}\s*$")
# Header trang chẵn dạng "368 Chapter 13 • Leadership"
FOOTER_EVEN = re.compile(r"^\s*(\d{1,3}\s+)?Chapter\s+\d{1,2}\s*[•·]\s*[^\d]+?(\s+\d{1,3})?\s*$")
# Header trang chẵn dạng "380     13 • Leadership"
FOOTER_EVEN2 = re.compile(r"^\s*\d{1,3}\s+\d{1,2}\s*[•·]\s*[A-Za-z][A-Za-z ,&'’\-]*$")
ACCESS = re.compile(r"Access for free at openstax\.org", re.I)
LABEL = re.compile(r"^\s*CONCEPT CHECK\s*$", re.I)
# Số chú thích dính sau dấu câu: "goals.25 People", "findings,76 Fiedler"
FOOTNOTE = re.compile(r"(?<=[A-Za-z’”)\"][.!?,;:])\d{1,3}(?=\s|$)")
SENT_END = re.compile(r"[.!?][”\")\]]*$")
# Caption của Exhibit (dài nhiều dòng) và các dòng nối tiếp
EXHIBIT = re.compile(r"^\s*Exhibit\s+\d+\.\d+\b.*$", re.I)
EXHIBIT_CONT = re.compile(r"^(?:[a-z(]|\d{4}\.\s)")
# Tiêu đề mục đánh số "2.3 Programmed ..." và câu hỏi đánh số "1. Explain ..."
NUM_HEADING = re.compile(r"^\d{1,2}\.\d{1,2}\s+[A-Z][^.!?]{2,70}$")
NUM_ITEM = re.compile(r"^\d{1,2}\.\s+[A-Z]")


def clean_lines(raw):
    raw = unicodedata.normalize("NFC", raw).replace("\u00a0", " ").replace("\u00ad", "")
    out, log = [], []
    in_exhibit = False
    for ln in raw.splitlines():
        s = ln.strip()
        if not s:
            continue
        if (ACCESS.search(s) or FOOTER_ODD.match(s) or FOOTER_EVEN.match(s)
                or FOOTER_EVEN2.match(s)):
            log.append(("footer/header", s))
            in_exhibit = False
            continue
        if LABEL.match(s):
            log.append(("label", s))
            continue
        if EXHIBIT.match(s):
            log.append(("exhibit_caption", s))
            in_exhibit = True
            continue
        if in_exhibit and EXHIBIT_CONT.match(s):
            log.append(("exhibit_continuation", s))
            continue
        in_exhibit = False
        s2 = FOOTNOTE.sub("", s)
        if s2 != s:
            log.append(("footnote_marker", s))
        out.append(s2)
    return out, log


def _join(a, b):
    # "well-" + "understood" -> "well-understood" (giữ gạch nối, bỏ khoảng trắng)
    if a.endswith("-") and len(a) > 1 and a[-2].isalpha() and b[:1].islower():
        return a + b
    return a + " " + b


def _is_heading(line, prev, nxt):
    if nxt is not None and NUM_HEADING.match(line):
        return True
    return (
        nxt is not None
        and len(line) <= 70
        and line[0].isupper()
        and not line.startswith("•")
        and not SENT_END.search(line)
        and not line.endswith((",", ";", ":"))
        and (prev is None or bool(SENT_END.search(prev)))
    )


def to_blocks(lines):
    """Lines -> blocks {type: heading|para|bullet, text}."""
    maxlen = max((len(l) for l in lines), default=0)
    blocks, cur = [], None
    for i, l in enumerate(lines):
        prev = lines[i - 1] if i else None
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        if l.startswith("•"):
            if cur:
                blocks.append(cur)
            cur = {"type": "bullet", "text": l.lstrip("• ").strip()}
            continue
        if _is_heading(l, prev, nxt):
            if cur:
                blocks.append(cur)
                cur = None
            blocks.append({"type": "heading", "text": l})
            continue
        if NUM_ITEM.match(l):
            if cur:
                blocks.append(cur)
            cur = {"type": "para", "text": l}
            continue
        # dòng trước kết thúc câu và ngắn hơn hẳn dòng đầy -> hết đoạn
        para_break = prev is not None and SENT_END.search(prev) and len(prev) < 0.85 * maxlen
        if cur is None or para_break:
            if cur:
                blocks.append(cur)
            cur = {"type": "para", "text": l}
        else:
            cur["text"] = _join(cur["text"], l)
    if cur:
        blocks.append(cur)
    return blocks


def clean_page(raw):
    lines, log = clean_lines(raw)
    return to_blocks(lines), log