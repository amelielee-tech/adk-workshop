"""Lab 3：在完成版的文案小組上掛 guardrail callback（三個掛鉤點）。

這裡直接給你 Lab 2 的完成版（Lab 2 沒寫完也能做這關），任務：
  1. callbacks.py 的 TODO(1)(2)(3)：完成三個 guardrail
  2. 這個檔案的 TODO(4a)(4b)(4c)：把三個 callback 掛上「對的」agent

本關最重要的一句話：**callback 掛在哪個 agent，就只管那個 agent**——
掛錯位置的 guardrail 等於沒有 guardrail（我們實測踩過：mask 掛在 root 上，
但 root transfer 之後不再說話，講「品牌A」的是 trend_researcher，結果競品名整路裸奔）。

驗證方式（每完成一個 TODO 就驗一次）：
  - TODO(1)：說「幫我寫跟品牌A比較的文案」→ 直接被擋，
    Events 面板裡那一輪根本沒有 LLM 呼叫（連錢都沒花）。
  - TODO(2)：正常請求文案 → trend_researcher 的 mock 資料必含品牌A/B/C，
    它的輸出裡會全部變成 ○○○——State 面板的 market_trends 也是淨化過的版本
    （淨化發生在寫進 state 之前）。
  - TODO(3)：說「幫我查敏感國X的客群」→ tool 沒有被執行，
    Events 面板裡 tool response 是我們塞的 blocked dict。
"""

from google.adk.agents import Agent, LoopAgent, SequentialAgent

from .callbacks import (
    block_competitor_names,
    block_restricted_countries,
    mask_competitor_names,
)
from .tools import approve_copy, get_audience_profile, get_market_trends

trend_researcher = Agent(
    name="trend_researcher",
    model="gemini-2.5-flash",
    description="市場趨勢研究員，負責查詢並整理產品的市場趨勢。",
    instruction="""你是市場趨勢研究員，在自動化管線中執行——
使用者不會回覆你，所以絕對不要打招呼、提問或等待確認。
收到任務後的第一個動作永遠是呼叫工具查詢市場趨勢，
然後用 3-5 個條列直接輸出重點趨勢與競品概況。用繁體中文。""",
    tools=[get_market_trends],
    output_key="market_trends",
    # TODO(4c): 「輸出淨化」guardrail 掛在這裡而不是 root——
    #   它的 mock 資料必含競品名，而 root transfer 之後不再說話；
    #   after_model 要掛在「會講髒話的那張嘴」上。淨化發生在寫進 state 之前，
    #   所以下游 writer 拿到的原料已經是 ○○○ 版。
    after_model_callback=mask_competitor_names,
)

audience_researcher = Agent(
    name="audience_researcher",
    model="gemini-2.5-flash",
    description="客群研究員，負責查詢並整理目標客群輪廓。",
    instruction="""你是客群研究員，在自動化管線中執行——
使用者不會回覆你，所以絕對不要打招呼、提問或等待確認。
收到任務後的第一個動作永遠是呼叫工具查詢目標客群，
然後直接輸出條列結果：年齡層、興趣與觸及管道。用繁體中文。""",
    tools=[get_audience_profile],
    output_key="audience_profile",
    # TODO(4b): 「受限地區」guardrail 掛在這裡而不是 root——
    #   before_tool_callback 要掛在「擁有那個 tool 的 agent」上才攔得到
    before_tool_callback=block_restricted_countries,
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
    # TODO(4a): 「輸入攔截」guardrail 掛在 root——它是使用者訊息的第一站（前門）。
    #   注意這裡「沒有」掛 after_model：輸出淨化掛在 root 沒用，
    #   因為 transfer 之後 root 不再說話（見 TODO(4c)）。
    before_model_callback=block_competitor_names,
)
