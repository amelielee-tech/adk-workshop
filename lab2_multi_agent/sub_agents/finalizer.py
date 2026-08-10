"""收尾員：pipeline 的最後一棒，負責把 state 裡的成果端給使用者。

為什麼需要它——實走 Lab 2 時發現的真實缺口：
root 把任務 transfer 給 pipeline 之後「不會拿回控制權」。
如果審稿三輪都沒過，迴圈被 max_iterations 保險絲終止，
使用者看到的最後一句話是 reviewer 的退稿意見——
成品明明躺在 state["campaign_copy"] 裡，卻沒有任何人端出來。
finalizer 補上「誰負責收尾」這一棒：不管迴圈怎麼結束，它都會執行。

對照 lab4：ADK 2.0 的 graph 裡 finalize 是一個「節點」，
「過稿」和「三輪耗盡」兩條邊都通到它——這裡是 1.x 的手工版。
"""

from google.adk.agents import Agent

finalizer = Agent(
    name="campaign_finalizer",
    model="gemini-2.5-flash",
    description="收尾員，整理最終文案交付給使用者。",
    instruction="""你是專案收尾員，用繁體中文，負責把文案小組的成果整理給使用者。

最終文案：
{campaign_copy}

審稿結論：
{review_feedback?}

規則：
- 審稿結論是「定稿／通過」→ 直接把最終文案乾淨排版呈現給使用者
- 審稿結論是「未通過」→ 開頭誠實告知「已達修改上限，文案未完全達標」，
  照樣呈現目前版本，並附上尚未達標的項目（引用審稿結論裡的數字），
  建議使用者自行微調該處
- 你只做整理與呈現，不要改寫文案內容""",
)
