"""自製 MCP server：保健品廣告合規檢查。

這是 Lab 4 的「Part B — 做一個自己的 MCP server」。
概念閉環：Lab 3 你把合規規則寫成 callback（綁死在那個 app 裡）；
這裡你把「同一套規則」包成一個獨立的 MCP server——
任何 MCP client（我們的 reviewer agent、Claude Desktop、別人的 agent…）
都能插上用。這就是「callback（app 內）vs MCP 工具（可重用服務）」的差別。

跑法（stdio 傳輸，給 MCPToolset 用 subprocess 啟動，不用自己手動跑）：
    python lab4_mcp/compliance_server.py

自己想手動測，可以裝 inspector：npx @modelcontextprotocol/inspector python lab4_mcp/compliance_server.py
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("supplement-compliance")

# 跟 Lab 3 callbacks 同一套規則——差別只在「這裡是可重用的獨立服務」
EFFICACY_CLAIMS = [
    "治療", "治癒", "療效", "根治", "抗癌", "降血壓", "降血糖", "預防疾病", "壯陽",
]
EXAGGERATION_TERMS = [
    "全球銷量第一", "全台第一", "第一品牌", "100%有效",
    "立即見效", "七天見效", "無副作用", "永不復發", "保證有效",
]


@mcp.tool()
def check_ad_compliance(text: str) -> dict:
    """檢查保健品文案是否違反台灣廣告法規。

    Args:
        text: 要檢查的文案全文

    Returns:
        dict: passed（是否過關）、efficacy_claims（踩到的療效字眼）、
        exaggeration_terms（踩到的誇大用語）、message（人類可讀結論）
    """
    efficacy = [w for w in EFFICACY_CLAIMS if w in text]
    exaggeration = [w for w in EXAGGERATION_TERMS if w in text]
    passed = not efficacy and not exaggeration
    if passed:
        message = "合規：未偵測到療效宣稱或誇大用語。"
    else:
        parts = []
        if efficacy:
            parts.append(f"療效宣稱 {efficacy}（保健食品不得宣稱醫療療效）")
        if exaggeration:
            parts.append(f"誇大用語 {exaggeration}（廣告不得誇大不實）")
        message = "不合規：" + "；".join(parts) + "，請修改。"
    return {
        "passed": passed,
        "efficacy_claims": efficacy,
        "exaggeration_terms": exaggeration,
        "message": message,
    }


if __name__ == "__main__":
    mcp.run()  # 預設 stdio 傳輸
