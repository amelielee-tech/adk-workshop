"""Lab 1：把 tool 掛上 agent。

流程：
1. 先讀 tools.py 的 TODO(1)(2)——兩個工具已寫好，重點看 docstring（給 LLM 的說明書）
   與回傳結構（status + 資料欄位）
2. 什麼都別改，先跑一次：adk web 選 lab1_tools，問「幫我查運動鞋的市場趨勢」，
   看它「沒有工具」時怎麼回答，Events 面板裡也不會有 functionCall
3. 解開下面 TODO(3) 那行註解 → 存檔 → New Session → 同一句再問
   （adk web 啟動要帶 --reload_agents 才會讀到新 code；沒生效就 Ctrl+C 重啟）
4. 到 Events 面板找 functionCall：product_category 這個參數是 LLM 自己
   從你的話裡抽出來的——這個對比就是 tool 的意義

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
    # TODO(3): 把兩個 tool 掛上來——tools 參數接一個 function 的 list。
    # 先「不解開」跑一次看它沒工具的樣子，再解開這行：
    # 存檔 → New Session → 同一句再問，對比 Events 的差別。
    # tools=[get_market_trends, get_audience_profile],
)
