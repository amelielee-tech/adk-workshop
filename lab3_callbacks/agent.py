"""Lab 3：在完成版的文案小組上掛 guardrail callback。

這裡直接給你 Lab 2 的完成版（Lab 2 沒寫完也能做這關），
你的任務只有兩個：
  1. callbacks.py 的 TODO(1)：完成 guardrail 邏輯
  2. 這個檔案的 TODO(2)：把 callback 掛上 root agent

驗證方式：
  - 對 agent 說「幫我寫跟品牌A比較的文案」→ 應該被 guardrail 直接擋下
  - 說正常的需求 → 照常運作
  - 看 Events 面板：被擋下的那次，根本沒有呼叫 LLM
"""

from google.adk.agents import Agent, LoopAgent, SequentialAgent

from .callbacks import block_competitor_names
from .tools import approve_copy, get_audience_profile, get_market_trends

trend_researcher = Agent(
    name="trend_researcher",
    model="gemini-2.5-flash",
    description="市場趨勢研究員，負責查詢並整理產品的市場趨勢。",
    instruction="""你是市場趨勢研究員。
根據使用者提到的產品，使用工具查詢市場趨勢，
然後用 3-5 個條列整理重點趨勢與競品概況。用繁體中文。""",
    tools=[get_market_trends],
    output_key="market_trends",
)

audience_researcher = Agent(
    name="audience_researcher",
    model="gemini-2.5-flash",
    description="客群研究員，負責查詢並整理目標客群輪廓。",
    instruction="""你是客群研究員。
根據使用者提到的市場/國家，使用工具查詢目標客群，
整理出年齡層、興趣與觸及管道。用繁體中文。""",
    tools=[get_audience_profile],
    output_key="audience_profile",
)

writer = Agent(
    name="copy_writer",
    model="gemini-2.5-flash",
    description="文案寫手，根據市場研究結果撰寫行銷文案。",
    instruction="""你是資深文案寫手，用繁體中文。

市場趨勢研究：
{market_trends}

目標客群輪廓：
{audience_profile}

根據以上研究，產出：一句 slogan、三個賣點、一段 50 字內的短文案。

審稿意見（如果有，必須根據意見修改）：
{review_feedback?}""",
    output_key="campaign_copy",
)

reviewer = Agent(
    name="copy_reviewer",
    model="gemini-2.5-flash",
    description="文案審稿員，評估文案品質並給出修改意見。",
    instruction="""你是嚴格的文案審稿員。評估 state 中的文案：
{campaign_copy}

評估標準：slogan 是否有記憶點、賣點是否呼應市場趨勢與客群、文案是否口語自然。

- 如果文案合格：呼叫 approve_copy 工具定稿，並簡短說明通過理由。
- 如果不合格：不要呼叫工具，直接列出具體修改意見（會退回給寫手重寫）。""",
    tools=[approve_copy],
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
    description="行銷文案專案的協調者。",
    instruction="""你是行銷文案專案的接待窗口，用繁體中文。
詢問使用者想為什麼產品、哪個市場製作文案，
資訊齊全後，把任務交給 campaign_pipeline 執行。
pipeline 完成後，把 state 裡的最終文案整理給使用者。""",
    sub_agents=[campaign_pipeline],
    # TODO(2): 掛上 guardrail（提示：before_model_callback 參數）
)
