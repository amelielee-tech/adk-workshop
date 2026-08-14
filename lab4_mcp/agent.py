"""Lab 4：MCP —— 用「別人建的」工具，也「做一個自己的」。

情境延續保健品文案小組，但兩個工具改成走 MCP：

  Part A（當 MCP client，用別人建的）
    audience_researcher 不再用寫死的 mock，改用「Fetch MCP server」
    抓真實網頁內容，據此整理客群輪廓。你沒寫這個工具——它來自外部 server。
    （Fetch server 零 API key，只是抓公開網頁。由 MCPToolset 自動用 subprocess 啟動。）

  Part B（當 MCP server，做一個自己的）
    reviewer 呼叫我們「自製的合規檢查 MCP server」（compliance_server.py）——
    把 Lab 3 的 guardrail 規則包成可重用服務。定稿前先過一次合規檢查。

核心對照：Lab 2 的 tool 是你自己寫的 Python function；這裡 tool 來自 MCP server，
但 agent 用起來一模一樣——這就是 MCP：「AI 工具的 USB-C」。

前置：Fetch server 需要 uvx（`pip install uv` 後就有 uvx）。
驗證：Events 面板看到 audience 的資料來自 fetch 工具、reviewer 呼叫 check_ad_compliance。
"""

import os

from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters

from .tools import approve_copy, get_market_trends

HERE = os.path.dirname(os.path.abspath(__file__))

# ── Part A：別人建的 MCP server（Fetch）──────────────────────────
# MCPToolset 會用 subprocess 啟動 `uvx mcp-server-fetch`，並自動把它提供的
# `fetch` 工具發現、掛給 agent。你一行工具都沒寫。
fetch_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uvx",
            args=["mcp-server-fetch"],
        ),
    ),
)

# ── Part B：自己做的 MCP server（合規檢查）──────────────────────
# 同樣用 subprocess 啟動我們的 compliance_server.py，掛給 reviewer。
compliance_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[os.path.join(HERE, "compliance_server.py")],
        ),
    ),
)

trend_researcher = Agent(
    name="trend_researcher",
    model="gemini-2.5-flash",
    description="市場趨勢研究員，負責查詢並整理保健品的市場趨勢。",
    instruction="""你是保健品市場趨勢研究員，在自動化管線中執行——
使用者不會回覆你，所以絕對不要打招呼、提問或等待確認。
收到任務後的第一個動作永遠是呼叫工具查詢市場趨勢，
然後用 3-5 個條列直接輸出重點趨勢與競品概況。用繁體中文。""",
    tools=[get_market_trends],
    output_key="market_trends",
)

# TODO(Part A): audience_researcher 的 tools 掛 fetch_toolset（別人建的 MCP）
audience_researcher = Agent(
    name="audience_researcher",
    model="gemini-2.5-flash",
    description="客群研究員，用 Fetch MCP 抓真實網頁後整理客群輪廓。",
    instruction="""你是客群研究員，在自動化管線中執行——
使用者不會回覆你，所以絕對不要打招呼、提問或等待確認。
第一個動作：用 fetch 工具抓取這個保健品消費者參考頁面：
    https://en.wikipedia.org/wiki/Dietary_supplement
（TODO：換成你想要的真實保健品市場/客群調查 URL）
再根據抓回來的內容，整理出目標客群的年齡層、興趣與觸及管道，條列輸出。用繁體中文。""",
    tools=[fetch_toolset],
    output_key="audience_profile",
)

writer = Agent(
    name="copy_writer",
    model="gemini-2.5-flash",
    description="文案寫手，根據市場研究結果撰寫保健品行銷文案。",
    instruction="""你是資深保健品文案寫手，用繁體中文。

市場趨勢研究：
{market_trends}

目標客群輪廓：
{audience_profile}

根據以上研究，產出：一句 slogan、三個賣點、一段 50 字內的短文案。
注意：保健食品不得宣稱療效，也不得使用誇大不實或絕對化用語。

審稿意見（如果有，必須根據意見修改）：
{review_feedback?}""",
    output_key="campaign_copy",
)

# TODO(Part B): reviewer 的 tools 掛 compliance_toolset（自製 MCP）+ approve_copy
reviewer = Agent(
    name="copy_reviewer",
    model="gemini-2.5-flash",
    description="文案審稿員，先過合規檢查再決定定稿或退回。",
    instruction="""你是嚴格的保健品文案審稿員，用繁體中文。待審文案：
{campaign_copy}

每一輪都照這個流程：
1. 先呼叫 check_ad_compliance 工具（來自合規 MCP server）檢查文案。
2. 若 passed 為 false（有療效或誇大用語）→ 不要定稿，直接列出違規項要求修改。
3. 若 passed 為 true 且文案品質合格 → 呼叫 approve_copy 定稿，簡短說明通過理由。""",
    tools=[compliance_toolset, approve_copy],
    output_key="review_feedback",
)

write_review_loop = LoopAgent(
    name="write_review_loop",
    sub_agents=[writer, reviewer],
    max_iterations=3,
)

campaign_pipeline = SequentialAgent(
    name="campaign_pipeline",
    sub_agents=[trend_researcher, audience_researcher, write_review_loop],
)

root_agent = Agent(
    name="campaign_coordinator",
    model="gemini-2.5-flash",
    description="保健品行銷文案專案的協調者。",
    instruction="""你是保健品行銷文案專案的接待窗口，用繁體中文。
詢問使用者想為什麼保健品、哪個市場製作文案，
資訊齊全後，把任務交給 campaign_pipeline 執行。
pipeline 完成後，把 state 裡的最終文案整理給使用者。""",
    sub_agents=[campaign_pipeline],
)
