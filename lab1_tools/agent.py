"""Lab 1：把 tool 掛上 agent。

目標：完成 tools.py 的兩個 TODO，再把 tools 掛上這個 agent，
然後在 adk web 問它「幫我查台灣運動鞋的市場趨勢和客群」，
觀察 Events 面板裡 tool 被呼叫的過程（帶了什麼參數、回了什麼）。

對照組實驗：先「不掛 tool」跑一次，看 agent 只能瞎掰；
掛上 tool 再跑一次，看差別——這就是 tool 的意義。
"""

from google.adk.agents import Agent

from .tools import get_audience_profile, get_market_trends

root_agent = Agent(
    name="research_assistant",
    model="gemini-2.5-flash",
    description="市場研究助理，可以查詢市場趨勢與客群輪廓。",
    instruction="""你是市場研究助理，用繁體中文回答。
使用者詢問市場或客群資訊時，務必使用工具查詢，不要憑空編造。
回答時整理成條列式，並注明資料來自工具查詢。""",
    # TODO(3): 把兩個 tool 掛上來（提示：tools 參數接一個 function 的 list）
)
