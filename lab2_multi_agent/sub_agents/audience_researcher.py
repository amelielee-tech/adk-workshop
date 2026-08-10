"""客群研究員：查目標客群，把結果寫進 session state。

這個檔案結構跟 trend_researcher.py 一模一樣——
請仿照它完成整個 agent（這是刻意的：驗證你真的懂了，而不是照抄）。
"""

from google.adk.agents import Agent

from ..tools import get_audience_profile

# TODO(2): 仿照 trend_researcher 建立 audience_researcher agent
# （結構一模一樣：tools 換成 get_audience_profile、output_key 換 key）
audience_researcher = Agent(
    name="audience_researcher",
    model="gemini-2.5-flash",
    description="客群研究員，負責查詢並整理目標客群輪廓。",
    instruction="""你是客群研究員，在自動化管線中執行——
使用者不會回覆你，所以絕對不要打招呼、提問或等待確認。
收到任務後的第一個動作永遠是呼叫工具查詢目標客群，
然後直接輸出條列結果：年齡層、興趣與觸及管道。用繁體中文。
（你的讀者是下一位 agent：開場白、寒暄、反問都會污染 state。）""",
    tools=[get_audience_profile],
    output_key="audience_profile",
)
