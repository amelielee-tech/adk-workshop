"""環境驗證用的最小 agent。這個 agent 能回話，代表你的環境全部設定正確。"""

from google.adk.agents import Agent

root_agent = Agent(
    name="hello_agent",
    model="gemini-2.5-flash",
    description="環境驗證用的打招呼 agent。",
    instruction="""你是一個友善的助理，用繁體中文回答。
如果使用者跟你打招呼，恭喜他們環境設定成功，並告訴他們可以開始工作坊了。""",
)
