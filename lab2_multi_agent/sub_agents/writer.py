"""文案寫手：讀 state 裡的研究結果，寫文案。

關鍵概念 —— 在 instruction 裡讀 state：
instruction 字串裡的 {market_trends} 會在執行時被替換成
state["market_trends"] 的內容。這就是「下游 agent 讀上游產出」的方式。
"""

from google.adk.agents import Agent

writer = Agent(
    name="copy_writer",
    model="gemini-2.5-flash",
    description="文案寫手，根據市場研究結果撰寫行銷文案。",
    # TODO(3): 完成 instruction——
    #   用 {market_trends} 和 {audience_profile} 把兩位研究員的產出帶進 prompt，
    #   要求產出：一句 slogan + 三個賣點 + 一段 50 字內的短文案。
    #   如果 state 裡有 {review_feedback?}（審稿意見），必須根據意見修改。
    #   （鍵名後加 ? 表示「可選」——第一輪還沒有審稿意見時不會報錯）
    instruction="""（在這裡完成 TODO(3)）""",
    output_key="campaign_copy",
)
