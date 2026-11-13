"""Fixed-size and structure-aware chunking (per page)."""
import re
from .models import Chunk, DocumentPage


def _meta(page, strategy, idx, **extra):
    return {**page.metadata, "strategy": strategy, "chunk_index": idx, **extra}


def fixed_size(page: DocumentPage, size: int, overlap: int) -> list[Chunk]:
    text = re.sub(r"^(## |• )", "", page.text, flags=re.M)
    text = " ".join(text.split())
    out, start, i = [], 0, 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            cut = text.rfind(" ", start + size // 2, end)
            if cut != -1:
                end = cut
        piece = text[start:end].strip()
        if piece:
            out.append(Chunk(f"{page.document_id}-p{page.page:03d}-fx{i:02d}", page.document_id,
                             page.source, page.page, piece, _meta(page, "fixed", i, char_start=start)))
            i += 1
        if end >= len(text):
            break
        start = end - overlap
        sp = text.find(" ", start)
        start = sp + 1 if 0 <= sp < end else end
    return out


def _split_long(par: str, max_size: int) -> list[str]:
    pieces, cur = [], ""
    for s in re.split(r"(?<=[.!?])\s+", par):
        if cur and len(cur) + 1 + len(s) > max_size:
            pieces.append(cur)
            cur = s
        else:
            cur = (cur + " " + s).strip()
    if cur:
        pieces.append(cur)
    final = []
    for p in pieces:
        while len(p) > max_size:
            cut = p.rfind(" ", 0, max_size)
            cut = cut if cut > 0 else max_size
            final.append(p[:cut])
            p = p[cut:].strip()
        final.append(p)
    return final


def by_paragraph(page: DocumentPage, max_size: int) -> list[Chunk]:
    units, pending, section = [], None, None   # units: (text, section)
    for p in (x.strip() for x in page.text.split("\n\n")):
        if not p:
            continue
        if p.startswith("## "):
            pending = p[3:]
            section = pending
            continue
        text = f"{pending}\n{p}" if pending else p
        pending = None
        units += [(t, section) for t in _split_long(text, max_size)]
    if pending:
        units.append((pending, section))

    groups, cur, cur_sec = [], "", None
    for text, sec in units:
        if cur and len(cur) + 1 + len(text) > max_size:
            groups.append((cur, cur_sec))
            cur, cur_sec = "", None
        cur = f"{cur}\n{text}" if cur else text
        cur_sec = cur_sec or sec
    if cur:
        groups.append((cur, cur_sec))
    return [Chunk(f"{page.document_id}-p{page.page:03d}-pg{i:02d}", page.document_id, page.source,
                  page.page, t, _meta(page, "paragraph", i, section=s))
            for i, (t, s) in enumerate(groups)]