"""Lab 2 主戰場：把文案小組組裝起來。

目標結構（ADK 1.x 的世界）：

    root_agent (campaign_coordinator)
    └── campaign_pipeline (SequentialAgent — 依序執行)
        ├── trend_researcher       → 寫 state["market_trends"]
        ├── audience_researcher    → 寫 state["audience_profile"]
        └── write_review_loop (LoopAgent — 最多 3 輪)
            ├── writer             → 讀研究結果，寫 state["campaign_copy"]
            └── reviewer           → 合格就 approve_copy 跳出；不合格寫修改意見

做題順序：
  1. sub_agents/trend_researcher.py 的 TODO(1)
  2. sub_agents/audience_researcher.py 的 TODO(2)
  3. sub_agents/writer.py 的 TODO(3)
  4. 這個檔案的 TODO(4) 和 TODO(5)

每完成一步就回 adk web 跑一次、看 Events 面板——
特別觀察：agent 之間怎麼 transfer、state 什麼時候被寫入。
"""

from google.adk.agents import Agent, LoopAgent, SequentialAgent

from .sub_agents.audience_researcher import audience_researcher
from .sub_agents.reviewer import reviewer
from .sub_agents.trend_researcher import trend_researcher
from .sub_agents.writer import writer

# TODO(4): 組出 write_review_loop 和 campaign_pipeline
#   - write_review_loop：LoopAgent，sub_agents 依序是 [writer, reviewer]，
#     max_iterations=3（重寫上限——想想看：跳出迴圈靠的是 reviewer 記得呼叫工具，
#     這個上限只是保險絲）
#   - campaign_pipeline：SequentialAgent，依序是
#     [trend_researcher, audience_researcher, write_review_loop]
#   （兩個都需要 name 參數）
write_review_loop = None
campaign_pipeline = None

root_agent = Agent(
    name="campaign_coordinator",
    model="gemini-2.5-flash",
    description="行銷文案專案的協調者。",
    instruction="""你是行銷文案專案的接待窗口，用繁體中文。
詢問使用者想為什麼產品、哪個市場製作文案，
資訊齊全後，把任務交給 campaign_pipeline 執行。
pipeline 完成後，把 state 裡的最終文案整理給使用者。""",
    # TODO(5): 把 campaign_pipeline 掛成 sub agent
    #   （提示：sub_agents 參數。掛好後 root agent 就能 transfer 給它）
)
