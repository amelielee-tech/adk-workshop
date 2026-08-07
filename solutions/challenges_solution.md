# 延伸挑戰解答

對照 `challenges.md`。先自己撞過牆再看——挑戰的一半價值在撞牆。

## 挑戰 1：Grounding（google_search）

先踩坑：直接把 `google_search` 加進 trend_researcher 的 `tools`：

```python
from google.adk.tools import google_search

trend_researcher = Agent(
    ...,
    tools=[get_market_trends, google_search],   # ❌ 會報錯
)
```

錯誤訊息會告訴你：**內建 tool（google_search 這種由 Gemini 原生執行的）
不能和一般 function tool 混掛在同一個 agent 上**。兩種解法：

**解法一（取捨）**：trend_researcher 只留 `google_search`，
放棄 mock tool——研究員全面改用真實搜尋。

```python
trend_researcher = Agent(
    name="trend_researcher",
    model="gemini-2.5-flash",
    description="市場趨勢研究員，用 Google 搜尋整理即時趨勢。",
    instruction="""你是市場趨勢研究員。用搜尋工具查使用者提到的產品
的近期市場趨勢，整理 3-5 個條列重點與主要競品。用繁體中文。""",
    tools=[google_search],
    output_key="market_trends",
)
```

**解法二（分工，推薦）**：內建 tool 自成一個專屬 agent，
再用 `AgentTool` 把它包成一般 tool 掛回來——「一個 agent 一種能力」，
這正是 multi-agent 分工存在的理由之一。

```python
from google.adk.tools.agent_tool import AgentTool

search_agent = Agent(
    name="web_searcher",
    model="gemini-2.5-flash",
    description="即時網路搜尋員。",
    instruction="用 Google 搜尋回答查詢，條列重點與來源。",
    tools=[google_search],          # 內建 tool 獨占一個 agent
)

trend_researcher = Agent(
    ...,
    tools=[get_market_trends, AgentTool(agent=search_agent)],  # ✅ 混搭成功
    output_key="market_trends",
)
```

## 挑戰 2：結構化輸出（output_schema）

```python
from pydantic import BaseModel, Field

class CampaignCopy(BaseModel):
    slogan: str = Field(description="一句有記憶點的 slogan")
    selling_points: list[str] = Field(description="三個賣點")
    short_copy: str = Field(description="50 字內的短文案")

writer = Agent(
    name="copy_writer",
    model="gemini-2.5-flash",
    description="文案寫手，輸出結構化 JSON 文案。",
    instruction="""（原本的 instruction 不變，最後加一句：）
嚴格依照 schema 輸出 JSON。""",
    output_schema=CampaignCopy,     # ← 關鍵
    output_key="campaign_copy",
)
```

為什麼設了 `output_schema` 就不能用 tools？因為結構化輸出是用
「受控生成」實作的——模型的最後一輪輸出被鎖成指定 JSON 格式，
而 tool calling 需要模型能自由輸出 function call，兩者互斥。
所以 schema 適合掛在「純轉換/產出」的 agent（writer 正是），
需要工具的 agent（reviewer）就不能掛。

## 挑戰 3：文案存成 Artifact

改 `approve_copy`（記得改成 `async def`）：

```python
from google.genai import types

async def approve_copy(tool_context: ToolContext) -> dict:
    """審稿通過時呼叫此工具，結束修改迴圈、定稿並存檔。"""
    tool_context.actions.escalate = True

    final_copy = tool_context.state.get("campaign_copy", "")
    version = await tool_context.save_artifact(
        "final_copy.md",
        types.Part(text=final_copy),
    )
    return {"status": "approved", "message": "文案定稿", "version": version}
```

驗證：跑兩次不同產品的文案，到 adk web 的 Artifacts 面板
看 `final_copy.md` 有 v0、v1 兩個版本。

State vs Artifact 的分界：
- **state** = 流程中的工作記憶（研究結果、輪數、意見）——小、結構化、給 agent 讀
- **artifact** = 交付物（定稿、報告、圖片）——有檔名、有版本、給人拿走

## 挑戰 4：接真的 BigQuery

### 路線 A：MCP Toolbox for Databases（現成 server）

1. 下載並設定 toolbox（單一 binary）：

```yaml
# tools.yaml
sources:
  workshop-bq:
    kind: bigquery
    project: ${GOOGLE_CLOUD_PROJECT}
tools:
  get-audience-profile:
    kind: bigquery-sql
    source: workshop-bq
    description: 查詢指定國家的目標客群輪廓。
    parameters:
      - name: country
        type: string
        description: 國家或地區，例如「台灣」
    statement: |
      SELECT age_group, interests, channels
      FROM `workshop_data.demographics`
      WHERE country = @country
```

```bash
./toolbox --tools-file tools.yaml   # 起在 localhost:5000
```

2. 在 agent 端用 toolbox client 載入（`pip install toolbox-core`）：

```python
from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
bq_tools = toolbox.load_toolset()

audience_researcher = Agent(
    ...,
    tools=bq_tools,          # tool 不是自己寫的，是接現成供應鏈
    output_key="audience_profile",
)
```

### 路線 B：自己寫 SDK client

```python
from google.cloud import bigquery

def get_audience_profile(country: str) -> dict:
    """查詢指定國家/地區的目標客群輪廓（BigQuery 真實資料）。

    Args:
        country: 國家或地區，例如「台灣」「日本」
    """
    client = bigquery.Client()
    query = """
        SELECT age_group, interests, channels
        FROM `workshop_data.demographics`
        WHERE country = @country
        LIMIT 1
    """
    job = client.query(
        query,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("country", "STRING", country)
            ]
        ),
    )
    rows = list(job.result())
    if not rows:
        return {"status": "not_found", "country": country}
    row = rows[0]
    return {
        "status": "success",
        "country": country,
        "age_group": row.age_group,
        "interests": list(row.interests),
        "channels": list(row.channels),
    }
```

（用 query parameter 而不是 f-string 拼 SQL——LLM 決定的參數
直接拼字串就是 SQL injection 的門。）

## 挑戰 5：加一個 agent（投放建議師）

```python
# sub_agents/media_planner.py
from google.adk.agents import Agent

media_planner = Agent(
    name="media_planner",
    model="gemini-2.5-flash",
    description="投放建議師，根據客群與定稿文案建議投放管道與預算分配。",
    instruction="""你是廣告投放建議師，用繁體中文。

目標客群輪廓：
{audience_profile}

定稿文案：
{campaign_copy}

根據客群的觸及管道與文案調性，產出：
1. 建議投放管道排序（附一句理由）
2. 預算分配比例（總和 100%）
3. 一個投放時機建議""",
    output_key="media_plan",
)
```

掛進 pipeline 最後一棒：

```python
campaign_pipeline = SequentialAgent(
    name="campaign_pipeline",
    sub_agents=[
        trend_researcher,
        audience_researcher,
        write_review_loop,
        media_planner,          # ← 新棒次：迴圈定稿後才輪到它
    ],
)
```

再把 root agent 的 instruction 補一句「最後把文案與投放建議一起整理給使用者」。

檢驗點：media_planner 放在 loop **外面**——它要讀的是定稿，
不該參與修改迴圈。如果你把它放進 LoopAgent 裡，每輪重寫都會多跑
一次投放建議，燒 token 又沒意義。位置就是設計。
