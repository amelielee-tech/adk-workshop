"""文案寫手：讀 state 裡的研究結果，寫文案。

關鍵概念 —— 在 instruction 裡讀 state：
instruction 字串裡的 {market_trends} 會在執行時被替換成
state["market_trends"] 的內容。這就是「下游 agent 讀上游產出」的方式。
"""

from google.adk.agents import Agent

writer = Agent(
    name="copy_writer",
    model="gemini-2.5-flash",
    description="文案寫手，根據市場研究結果撰寫保健品行銷文案。",
    # TODO(3): 用 {market_trends} 和 {audience_profile} 把研究員的產出帶進 prompt；
    #   {review_feedback?} 的 ? 表示「可選」——第一輪還沒有審稿意見時不會報錯
    instruction="""你是資深文案寫手，用繁體中文。

市場趨勢研究：
{market_trends}

目標客群輪廓：
{audience_profile}

根據以上研究，產出符合規格書的文案：
- slogan：12 字以內
- 賣點：恰好三條
- 短文案：50 字以內（硬規格，寧可 40 字也不要超過）
- 全文至少自然提及一個目標客群的觸及管道

審稿意見（如果有，必須根據意見修改）：
{review_feedback?}

直接輸出文案本體（Slogan／賣點／短文案三段），
不要開場白或說明你做了什麼——你的輸出會被存進 state 供審稿使用。""",
    output_key="campaign_copy",
)
