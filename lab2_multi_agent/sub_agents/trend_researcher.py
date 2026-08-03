"""趨勢研究員：查市場趨勢，把結果寫進 session state。

關鍵概念 —— output_key：
agent 設定 output_key="market_trends" 之後，它的最終回覆會自動寫進
session state 的 state["market_trends"]，後面的 agent 就能讀到。
這就是 ADK 1.x 裡 agent 之間傳資料的方式。
"""

from google.adk.agents import Agent

from ..tools import get_market_trends

trend_researcher = Agent(
    name="trend_researcher",
    model="gemini-2.5-flash",
    description="市場趨勢研究員，負責查詢並整理產品的市場趨勢。",
    instruction="""你是市場趨勢研究員。
根據使用者提到的產品，使用工具查詢市場趨勢，
然後用 3-5 個條列整理重點趨勢與競品概況。用繁體中文。""",
    tools=[get_market_trends],
    # TODO(1): 設定 output_key，讓這個 agent 的產出寫進 state["market_trends"]
)
