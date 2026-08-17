"""Lab 1：把 tool 掛上 agent。

這一關「預設就跑得起來」——直接 adk web 選 lab1_tools、問問題就會呼叫工具。
流程（結果導向）：
1. 直接跑：問「幫我查魚油的市場趨勢」→ 到 Events 面板找 functionCall，
   看 product_category 這個參數是 LLM 自己從你的話裡抽出來的——這就是 tool 的意義。
2. 讀 tools.py：重點看 docstring（給 LLM 的說明書）與回傳結構（status + 資料欄位）。

（講師可選 demo：把下面 tools=[...] 那行註解掉、New Session 再問一次，
 會看到它「沒工具」時怎麼瞎編、Events 也沒有 functionCall——這個 before/after
 就是「為什麼要工具」的 aha。改 code 後：存檔 → New Session 才生效。）

進階實驗：只說「查客群輪廓」、不講國家，看 agent 會不會反過來追問你——
它從 docstring 知道這個工具需要 country 參數。
"""

from google.adk.agents import Agent

from .tools import get_audience_profile, get_market_trends

root_agent = Agent(
    name="research_assistant",
    model="gemini-2.5-flash",
    description="市場研究助理，可以查詢市場趨勢與客群輪廓。",
    instruction="""你是市場研究助理，用繁體中文回答。
使用者詢問市場或客群資訊時，務必使用工具查詢，不要憑空編造。
回答市場或客群問題時，只能根據工具回傳的內容；工具沒有提供的資訊
（例如價格、市占率、品牌評價），一律回答「查無資料」，不要推測補充。
若工具回傳的 status 不是 success，直接告知查詢失敗。
回答時整理成條列式，並注明資料來自工具查詢。""",
    # tools：把兩個 function 掛上來，agent 就會用工具查詢。
    # 已預設啟用，直接跑就會呼叫工具（結果導向）。
    # 想示範 before/after：把下面這行註解掉跑一次（看它瞎編），再解開重跑（查工具）。
    tools=[get_market_trends, get_audience_profile],
)
