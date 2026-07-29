"""
STEP 6: agent loop  <- นี่คือ 'backend ที่ Claude Code ซ่อนไว้'

รันแล้วจะเห็น messages[] ทุกรอบ ว่ามันโตขึ้นยังไงและใครใส่อะไรเข้าไป
"""
import json
import sys

import requests

from config import OLLAMA_URL, CHAT_MODEL, MAX_STEPS, NUM_CTX
from tools import TOOLS, dispatch

SYSTEM = (
    "คุณเป็นผู้ช่วยที่ตอบจาก knowledge base ของผู้ใช้เท่านั้น\n"
    "- ถ้าคำถามเกี่ยวกับ project/note ของผู้ใช้ ให้เรียก search_kb ก่อนเสมอ\n"
    "- ตอบจาก context ที่ได้เท่านั้น ห้ามเดา\n"
    "- อ้างอิงไฟล์ต้นทางท้ายคำตอบ\n"
    "- ถ้าไม่เจอ ให้บอกตรงๆ ว่าไม่เจอ"
)

BAR = "=" * 70


def show_messages(step, messages):
    print(f"\n{BAR}\nSTEP {step}  |  ส่งเข้าโมเดล {len(messages)} messages")
    print(BAR)
    for m in messages:
        body = m.get("content") or ""
        if m.get("tool_calls"):
            body = "TOOL_CALLS -> " + json.dumps(
                [c["function"] for c in m["tool_calls"]], ensure_ascii=False)
        body = body if len(body) < 300 else body[:300] + f" ...(+{len(body)-300} ตัวอักษร)"
        print(f"  [{m['role']:9}] {body}")
    approx = sum(len(str(m.get('content') or '')) for m in messages) // 3
    print(f"  ~{approx} tokens (ประมาณคร่าวๆ)")


def chat(messages):
    r = requests.post(f"{OLLAMA_URL}/api/chat", json={
        "model": CHAT_MODEL,
        "messages": messages,
        "tools": TOOLS,          # <- schema ถูก serialize เข้า prompt ตรงนี้
        "stream": False,
        "options": {"temperature": 0.2, "num_ctx": NUM_CTX},
    }, timeout=600)
    r.raise_for_status()
    return r.json()["message"]


def run(question, verbose=True):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": question}]

    for step in range(1, MAX_STEPS + 1):
        if verbose:
            show_messages(step, messages)

        msg = chat(messages)
        messages.append(msg)

        calls = msg.get("tool_calls") or []
        if not calls:                       # โมเดลไม่เรียก tool แล้ว = จบ
            return msg.get("content", "")

        for c in calls:
            name = c["function"]["name"]
            args = c["function"]["arguments"]
            if isinstance(args, str):       # บาง model คืนเป็น JSON string
                args = json.loads(args)
            if verbose:
                print(f"\n  >> เรียก {name}({args})")
            result = dispatch(name, args)
            if verbose:
                print(f"  << ได้กลับ {len(result)} ตัวอักษร")
            messages.append({"role": "tool", "name": name, "content": result})

    return "(หยุดเพราะชน MAX_STEPS — ระวัง infinite loop)"


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "สรุปโครงสร้าง project ของผมหน่อย"
    answer = run(q)
    print(f"\n{BAR}\nคำตอบ:\n{BAR}\n{answer}")
