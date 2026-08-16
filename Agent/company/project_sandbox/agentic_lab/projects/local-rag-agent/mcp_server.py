"""
(ง) MCP server — ยก search_kb ออกมาเป็น server ให้ client ไหนก็เสียบได้

เดิม:  agent.py --import--> tools.search_kb ตรงๆ            (1 tool, 1 client)
นี่ :  search_kb กลายเป็น MCP tool
       -> Ollama-agent / Claude Code / Cursor ใช้ 'ตัวเดียวกัน' ได้
       = แก้ N×M เหลือ N+M  (kb/agent-fundamentals.md)

รัน (stdio):   .venv/bin/python mcp_server.py
เทสต์ด้วยตา:   .venv/bin/mcp dev mcp_server.py      # เปิด MCP Inspector ใน browser

เสียบเข้า Claude Code (ทำเองเมื่อพร้อม — ไม่แตะ agent-knowledge เดิม):
  claude mcp add agentic-lab-kb -- \\
     <ABS>/.venv/bin/python <ABS>/mcp_server.py
ถอนออก:  claude mcp remove agentic-lab-kb
"""
from fastmcp import FastMCP

from tools import search_kb

mcp = FastMCP("agentic-lab-kb")


@mcp.tool()
def search_kb_tool(query: str, mode: str = "hybrid") -> str:
    """ค้น knowledge base ของ agentic_lab (RAG hybrid = dense + BM25 รวมด้วย RRF).

    query: คำค้นภาษาธรรมชาติ อธิบายสิ่งที่อยากรู้
    mode : hybrid | dense | bm25  (default hybrid)
    คืน chunk ที่เกี่ยวข้องพร้อมไฟล์ต้นทาง
    """
    return search_kb(query, mode)


if __name__ == "__main__":
    mcp.run()   # stdio transport (default)
