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
    instruction="""你是客群研究員。
根據使用者提到的市場/國家，使用工具查詢目標客群，
整理出年齡層、興趣與觸及管道。用繁體中文。""",
    tools=[get_audience_profile],
    output_key="audience_profile",
)
