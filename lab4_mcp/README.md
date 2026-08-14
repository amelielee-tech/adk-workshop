# Lab 4：MCP —— 用別人的工具，做一個自己的

延續保健品文案小組，把兩個工具改成走 **MCP（Model Context Protocol）**——
「AI 工具的 USB-C」：agent 用統一方式接上外部 server 提供的工具，不用每個都自己寫。

## 這一關的兩面

| Part | 你是 | 做什麼 | 檔案 |
|---|---|---|---|
| **A** | MCP **client**（用別人建的） | `audience_researcher` 用 **Fetch MCP** 抓真實網頁，據此整理客群 | `agent.py` 的 `fetch_toolset` |
| **B** | MCP **server**（做一個自己的） | `reviewer` 呼叫**自製的合規檢查 MCP**，定稿前先過一次法規 | `compliance_server.py` |

**概念閉環**：Lab 3 你把合規規則寫成 callback（綁死在這個 app 裡）；Lab 4 你把同一套規則
包成獨立的 **MCP server**——任何 client（我們的 reviewer、Claude Desktop、別人的 agent）都能插上用。
親手體會「callback（app 內）vs MCP 工具（可重用服務）」。

## 前置

```bash
pip install uv          # 取得 uvx，MCPToolset 會用它啟動 Fetch server
```
`MCPToolset` 會自動用 subprocess 啟動兩個 server（`uvx mcp-server-fetch`、`python compliance_server.py`），
你不用手動跑它們。

## TODO

- **Part A**：`agent.py` 把 `fetch_toolset` 掛到 `audience_researcher` 的 `tools`，
  並在 instruction 給它要抓的真實 URL（預設放了維基百科，換成你要的保健品調查頁）。
- **Part B**：`agent.py` 把 `compliance_toolset` 掛到 `reviewer` 的 `tools`，
  instruction 要求它「先呼叫 `check_ad_compliance` 再決定定稿」。

## 驗證（`adk web` 選 `lab4_mcp`）

1. 跑一輪文案 → **Events 面板**看到 `audience_researcher` 呼叫的是 **fetch**（MCP 工具），資料來自真實網頁。
2. reviewer 那輪看到它呼叫 **check_ad_compliance**，回傳 `passed` 與違規清單。
3. 故意讓 writer 產出含「立即見效」→ 合規 MCP 抓出來 → 退回重寫。

> 想手動戳自製 server：`npx @modelcontextprotocol/inspector python lab4_mcp/compliance_server.py`
