"""審稿員：評估文案品質，決定「定稿」或「退回重寫」。

關鍵概念 —— LoopAgent 的跳出機制（1.x 的方式）：
審稿通過時，reviewer 要「記得」呼叫 approve_copy 工具（裡面設 escalate=True）
來停止迴圈。注意：這個跳出時機是靠 prompt 拜託 LLM 的——
這正是 2.0 要解決的痛點（2.0 把它變成 graph 上一條條件邊）。
"""

from google.adk.agents import Agent

from ..tools import approve_copy, record_revision

reviewer = Agent(
    name="copy_reviewer",
    model="gemini-2.5-flash",
    description="文案審稿員，評估文案品質並給出修改意見。",
    instruction="""你是嚴格的文案審稿員。評估 state 中的文案：
{campaign_copy}

評估標準：slogan 是否有記憶點、賣點是否呼應市場趨勢與客群、文案是否口語自然。

- 如果文案合格：呼叫 approve_copy 工具定稿，並簡短說明通過理由。
- 如果不合格：先呼叫 record_revision 工具登記輪數，再列出具體修改意見
  （會退回給寫手重寫）。如果工具回報 is_final_round 為 true，
  意見開頭必須註明「最後一輪，請務必定稿」。""",
    tools=[approve_copy, record_revision],
    output_key="review_feedback",
)
