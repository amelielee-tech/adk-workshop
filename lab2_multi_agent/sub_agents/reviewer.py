"""審稿員：按「規格書」審稿，決定「定稿」或「退回重寫」。

兩個關鍵概念：

1. 工具給事實、LLM 給判斷——審稿判準不是 LLM 的品味（說不準），
   而是 check_copy_format 量出來的數字（字數、條數、管道），
   每一輪為什麼過/為什麼退，在 Events 裡看得一清二楚。

2. LoopAgent 的跳出機制（1.x 的方式）：
   審稿通過時，reviewer 要「記得」呼叫 approve_copy 工具（裡面設 escalate=True）
   來停止迴圈。注意：這個跳出時機是靠 prompt 拜託 LLM 的——
   這正是 2.0 要解決的痛點（2.0 把它變成 graph 上一條條件邊）。
"""

from google.adk.agents import Agent

from ..tools import approve_copy, check_copy_format, record_revision

reviewer = Agent(
    name="copy_reviewer",
    model="gemini-2.5-flash",
    description="文案審稿員，按規格書檢查文案並給出修改意見。",
    instruction="""你是文案審稿員，按規格書審稿，用繁體中文。待審文案：
{campaign_copy}

每一輪都照這個流程：
1. 從文案中抽出 slogan、賣點列表、短文案，呼叫 check_copy_format 取得量化結果
2. all_passed 為 true → 呼叫 approve_copy 定稿，引用數字簡短說明通過
3. all_passed 為 false → 先呼叫 record_revision 登記輪數，
   再引用數字指出哪幾項不合格（會退回給寫手重寫）。
   如果 record_revision 回報 is_final_round 為 true，
   意見開頭必須註明「最後一輪，請務必定稿」。""",
    tools=[check_copy_format, approve_copy, record_revision],
    output_key="review_feedback",
)
