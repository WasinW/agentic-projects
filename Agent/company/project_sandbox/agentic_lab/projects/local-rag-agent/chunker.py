"""
STEP 1: .md  ->  chunks

หลักการ 2 ข้อ:
1. structure-aware  : ตัดตาม heading เพราะคนเขียนขีดเส้นแบ่งความหมายไว้ให้แล้ว
2. parent-child     : embed ก้อนเล็ก (แม่นยำ) แต่ส่งก้อนใหญ่ให้โมเดล (context ครบ)
"""
import re
import pathlib

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")

# --- filter ตอน index ต้นไม้จริง (option ก) ---
# กัน dir ที่ไม่ใช่ความรู้ + machine-excluded (_prefix) + lab ตัวเอง
SKIP_PARTS = {".git", "node_modules", ".venv", "_venv", "qdrant_storage",
              "archive", "memory", "bak_mem", "knowledge_base_legacy",
              "index", "agentic_lab"}
# agent.md = "พฤติกรรม/system prompt" คนละแกนกับ RAG -> โหลดเป็น persona ไม่ใช่ index
# (ดู persona.py) ; knowledge.md / kb / SKILL.md = ข้อเท็จจริง -> index
EXCLUDE_NAMES = {"agent.md"}


def is_excluded(path, root):
    parts = path.relative_to(root).parts
    if any(p.startswith("_") or p in SKIP_PARTS for p in parts):
        return True
    return path.name in EXCLUDE_NAMES


def split_sections(text):
    """แตกเอกสารเป็น section ตาม heading พร้อมเก็บ heading path เต็ม"""
    stack, sections = [], []
    cur = {"path": [], "lines": []}

    for line in text.split("\n"):
        m = HEADING.match(line)
        if m:
            if cur["lines"]:
                sections.append({"path": list(cur["path"]),
                                 "text": "\n".join(cur["lines"]).strip()})
            level, title = len(m.group(1)), m.group(2).strip()
            # pop heading ที่ level เท่ากันหรือลึกกว่า -> ได้ path ที่ถูกต้อง
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
            cur = {"path": [t for _, t in stack], "lines": []}
        else:
            cur["lines"].append(line)

    if cur["lines"]:
        sections.append({"path": list(cur["path"]),
                         "text": "\n".join(cur["lines"]).strip()})
    return [s for s in sections if s["text"]]


def split_children(text, max_chars):
    """ซอย section ยาวๆ เป็น child ตามย่อหน้า"""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, buf = [], ""
    for p in paras:
        # ย่อหน้าเดียวยาวเกิน -> ตัดดิบๆ (ภาษาไทยเจอบ่อย เพราะไม่มีเว้นวรรค)
        while len(p) > max_chars:
            if buf:
                chunks.append(buf); buf = ""
            chunks.append(p[:max_chars]); p = p[max_chars:]
        if buf and len(buf) + len(p) + 2 > max_chars:
            chunks.append(buf); buf = p
        else:
            buf = f"{buf}\n\n{p}" if buf else p
    if buf:
        chunks.append(buf)
    return chunks or [text]


def build_chunks(root, max_chars=600):
    """คืน list ของ dict ที่พร้อม embed"""
    out = []
    root = pathlib.Path(root)
    for path in sorted(root.rglob("*.md")):
        if is_excluded(path, root):
            continue
        raw = path.read_text(encoding="utf-8", errors="ignore")
        for si, sec in enumerate(split_sections(raw)):
            heading = " > ".join(sec["path"]) or path.stem
            parent  = f"# {heading}\n\n{sec['text']}"
            for ci, child in enumerate(split_children(sec["text"], max_chars)):
                out.append({
                    "id":      f"{path.name}::{si}::{ci}",
                    "file":    str(path),
                    "heading": heading,
                    # contextual retrieval: ยัด context นำหน้าก่อน embed
                    # แก้ปัญหา chunk ที่อ่านเดี่ยวๆ แล้วไม่รู้ว่าพูดถึงอะไร
                    "embed_text": f"[{path.stem} | {heading}]\n{child}",
                    "child":  child,
                    "parent": parent,
                })
    return out


if __name__ == "__main__":
    from config import KB_ROOT, MAX_CHARS
    cs = build_chunks(KB_ROOT, MAX_CHARS)
    print(f"{len(cs)} chunks จาก {len({c['file'] for c in cs})} ไฟล์")
    for c in cs[:3]:
        print("-" * 60)
        print(c["id"], "|", c["heading"])
        print(c["child"][:200])
