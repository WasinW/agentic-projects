"""
(ค) persona loader — agent.md = "พฤติกรรม/ตัวตน" โหลดเป็น system prompt (ไม่ index!)

ย้ำแกน (kb/model-file-formats.md):
  knowledge.md = ข้อเท็จจริง   -> RAG (retrieve ด้วย search_kb)
  agent.md     = พฤติกรรม/persona -> system prompt (โหลดตรงๆ)
การเอา system prompt 21 ตัวไป embed แล้ว retrieve ด้วย cosine = ผิดหมวด
คุณ "เลือก" persona ไม่ได้ "ค้นหา" มัน

ใช้กับ agent.py:  python agent.py --persona technical/architect "คำถาม"
"""
import pathlib

from config import REAL_KB

ROLES_ROOT = pathlib.Path(REAL_KB) / "roles"


def list_personas(roles_root=ROLES_ROOT):
    """คืน {'<cat>/<role>': path ของ agent.md}"""
    out = {}
    root = pathlib.Path(roles_root)
    if not root.exists():
        return out
    for p in sorted(root.rglob("agent.md")):
        name = "/".join(p.relative_to(root).parts[:-1])   # ตัด 'agent.md' ออก
        out[name] = p
    return out


def load_persona(name):
    """คืนเนื้อ agent.md เพื่อใช้เป็น system prompt; รับชื่อ role หรือ path ตรงๆ"""
    personas = list_personas()
    if name in personas:
        return personas[name].read_text(encoding="utf-8", errors="ignore")
    p = pathlib.Path(name)
    if p.exists():
        return p.read_text(encoding="utf-8", errors="ignore")
    raise KeyError(f"ไม่พบ persona '{name}'. มีให้เลือก: {sorted(personas)}")


if __name__ == "__main__":
    import sys
    personas = list_personas()
    print(f"เจอ {len(personas)} personas (agent.md) ใน {ROLES_ROOT}:")
    for n in sorted(personas):
        print("  -", n)
    if len(sys.argv) > 1:
        name = sys.argv[1]
        sp = load_persona(name)
        print(f"\n=== system prompt ของ '{name}' ({len(sp)} chars, โชว์ 600 ตัวแรก) ===")
        print(sp[:600] + (" ..." if len(sp) > 600 else ""))
        print("\n=== messages[] ที่ agent.py จะสร้าง ===")
        print("  [system] <agent.md ข้างบน>  +  <SYSTEM ของ RAG>")
        print("  [user  ] <คำถามของคุณ>")
        print("=> persona กำหนด 'พฤติกรรม', search_kb เติม 'ความรู้' — คนละแกน")
