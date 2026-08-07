# 延伸挑戰（給做完主線的人）

按難度排序，自由選。撞牆撞夠了再看 `solutions/challenges_solution.md`。

## 挑戰 1：接上真實搜尋——Grounding（★）

把 trend_researcher 的 mock 資料換成真的：ADK 內建 `google_search` tool
（`from google.adk.tools import google_search`），掛上去就能搜真實網路。

但你會踩到一個刻意留給你的坑：**內建 tool 不能和一般 function tool
掛在同一個 agent 上**。想想有哪兩種解法（提示：一是取捨、二是分工——
分工的做法正是 multi-agent 存在的理由之一），選一種做出來。

## 挑戰 2：結構化輸出（★）

讓 writer 保證回傳 JSON。
給 writer 加 `output_schema`（用 Pydantic BaseModel 定義
`slogan`、`selling_points`、`short_copy` 三個欄位）。
注意：設了 output_schema 的 agent 不能再用 tools——想想為什麼。

## 挑戰 3：文案存成 Artifact（★★）

State 是短期記憶，**Artifact 才是交付物**——有檔名、有版本、adk web
有專屬面板可以看。給 reviewer 的 `approve_copy` 加工夫：定稿時把
state 裡的最終文案存成 artifact：

```python
await tool_context.save_artifact(
    "final_copy.md",
    types.Part(text=state_裡的文案),
)
```

（提示：save_artifact 是 async，tool 要改成 `async def`。）
多跑幾次不同產品的文案，到 adk web 的 Artifacts 面板看版本怎麼疊加。
想想：哪些東西該進 state、哪些該進 artifact？

## 挑戰 4：接真的 BigQuery——用現成的 MCP server（★★★）

把 `get_audience_profile` 的 mock 換成真 BQ 查詢。先灌資料：

```bash
cd data && bash load_to_bq.sh   # 建 dataset + 灌範例資料
```

**路線 A（推薦，練 MCP）**：不自己寫 client，直接接 Google 官方的
[MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox)——
用 `MCPToolset` 把 toolbox 的 BigQuery tool 掛給 audience_researcher，
體驗「tool 不是自己寫的，是接現成供應鏈」。

**路線 B（練 SDK）**：用 `google.cloud.bigquery` client 自己改寫 tool，
query `workshop_data.demographics` 表、依 country 過濾。

這正是 Campaign challenge lab 裡 Data Analyst agent 做的事。

## 挑戰 5：加一個 agent（★★★）

給小組加一位「投放建議師」：讀 state 裡的客群輪廓與定稿文案，
建議投放管道與預算分配，掛進 pipeline 的最後一棒。
從零寫一個 agent + 掛進既有結構，是檢驗你真的會了的最好方式。

## 大魔王：Campaign Challenge Lab

去 Google Skills 做 **[PTPPF] Build a Multi-Agent Campaign System
with ADK and Agent Engine**——MCP、A2A、Cloud Run、Agent Engine 全套，
有自動評分。做完它，你就從「會寫 multi-agent」升級到「會部署 multi-agent 系統」。
