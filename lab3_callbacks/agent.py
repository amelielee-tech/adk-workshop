"""Lab 3：在完成版的文案小組上掛 guardrail callback（三個掛鉤點）。

情境＝保健食品行銷，法規禁令具體，三個掛鉤點各對一個真實需求。
這裡直接給你 Lab 2 的完成版（Lab 2 沒寫完也能做這關），任務：
  1. callbacks.py 的 TODO(1)(2)(3)：完成三個 guardrail
  2. 這個檔案的 TODO(4a)(4b)(4c)：把三個 callback 掛上「對的」agent
  3. 加碼 memory（TODO(5)）：用 before_agent 載入、after_agent 存記憶——
     補齊 agent/model/tool 三個層級，並帶出「跨 session 長期記憶」概念。
     （驗證：跑完一次某品牌的文案 → 開新 session 再跑同品牌，
      State 面板的 brand_memory 會出現上一次的內容。adk web 預設帶 InMemoryMemoryService。）

本關最重要的一句話：**callback 掛在哪個 agent，就只管那個 agent**——
掛錯位置的 guardrail 等於沒有 guardrail（我們實測踩過：淨化掛在 root 上，
但 root transfer 之後不再說話，講出誇大詞的是 trend_researcher，結果整路裸奔）。

驗證方式（每完成一個 TODO 就驗一次）：
  - TODO(1)：說「幫我寫這款魚油能『治療』高血壓的文案」→ 直接被擋（含療效字眼），
    Events 面板裡那一輪根本沒有 LLM 呼叫（連錢都沒花）。
  - TODO(2)：正常請求文案 → trend_researcher 的 mock 趨勢必含「全球銷量第一／立即見效」，
    它的輸出裡會全部變成 ○○○——State 面板的 market_trends 也是淨化過的版本
    （淨化發生在寫進 state 之前）。
  - TODO(3)：說「幫我為『褪黑激素』做文案」→ get_market_trends 被擋（受限成分）；
    說「針對『孕婦』做文案」→ get_audience_profile 被擋（受限對象）。
    兩者的 tool response 都是我們塞的 blocked dict，tool 本體沒有執行。
"""

from google.adk.agents import Agent, LoopAgent, SequentialAgent

from .callbacks import (
    block_efficacy_claims,
    block_restricted_requests,
    load_brand_memory,
    mask_exaggeration,
    save_campaign_to_memory,
)
from .tools import approve_copy, get_audience_profile, get_market_trends

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
    # TODO(4c): 「輸出淨化」guardrail 掛在這裡而不是 root——
    #   它的 mock 資料必含誇大詞，而 root transfer 之後不再說話；
    #   after_model 要掛在「會講髒話的那張嘴」上。淨化發生在寫進 state 之前，
    #   所以下游 writer 拿到的原料已經是 ○○○ 版。
    after_model_callback=mask_exaggeration,
    # TODO(4b-i): 「受限成分」guardrail——get_market_trends 是這個 agent 的 tool，
    #   要卡它的 product_category 參數，before_tool 就得掛在這個 agent 上。
    #   （同一個 callback 也掛在 audience_researcher，見下——一個 callback 守兩個 tool）
    before_tool_callback=block_restricted_requests,
)

audience_researcher = Agent(
    name="audience_researcher",
    model="gemini-2.5-flash",
    description="客群研究員，負責查詢並整理目標客群輪廓。",
    instruction="""你是客群研究員，在自動化管線中執行——
使用者不會回覆你，所以絕對不要打招呼、提問或等待確認。
收到任務後的第一個動作永遠是呼叫工具查詢目標客群，
若任務有指定客群（如銀髮族、孕婦），呼叫工具時一併帶入 audience_group，
然後直接輸出條列結果：年齡層、興趣與觸及管道。用繁體中文。""",
    tools=[get_audience_profile],
    output_key="audience_profile",
    # TODO(4b-ii): 「受限對象」guardrail——get_audience_profile 是這個 agent 的 tool，
    #   要卡它的 audience_group 參數，before_tool 就得掛在這個 agent 上。
    before_tool_callback=block_restricted_requests,
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

這個品牌過去的文案與調性（若有，盡量延續一致）：
{brand_memory?}

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

評估標準：slogan 是否有記憶點、賣點是否呼應市場趨勢與客群、文案是否口語自然、
是否符合保健食品法規（無療效宣稱、無誇大用語）。

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
    # TODO(5b): 「存記憶」掛在 pipeline 的 after_agent——整條跑完才存一次，
    #   保證在最後執行（掛在迴圈裡的 reviewer 會每輪存一次，不對）。
    after_agent_callback=save_campaign_to_memory,
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
    # TODO(4a): 「輸入攔截」guardrail 掛在 root——它是使用者訊息的第一站（前門）。
    #   注意這裡「沒有」掛 after_model：輸出淨化掛在 root 沒用，
    #   因為 transfer 之後 root 不再說話（見 TODO(4c)）。
    before_model_callback=block_efficacy_claims,
    # TODO(5a): 「載入記憶」掛在 root 的 before_agent——前門就先把品牌過去的
    #   內容撈進 state，下游 writer 才讀得到 {brand_memory}。
    before_agent_callback=load_brand_memory,
)
