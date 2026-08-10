"""Lab 2 解答（TODO(1)–(5)）。

完整組裝好的版本可以直接看 lab3_callbacks/agent.py——
它就是 Lab 2 的完成版（外加 callback 的 TODO）。
這裡列出每個 TODO 的關鍵解答片段。
"""

# ── TODO(1) trend_researcher.py：加上 output_key ──────────────────
# trend_researcher = Agent(
#     ...,
#     tools=[get_market_trends],
#     output_key="market_trends",        # ← 就這一行
# )

# ── TODO(2) audience_researcher.py：完整 agent ────────────────────
# audience_researcher = Agent(
#     name="audience_researcher",
#     model="gemini-2.5-flash",
#     description="客群研究員，負責查詢並整理目標客群輪廓。",
#     instruction="""你是客群研究員。
# 根據使用者提到的市場/國家，使用工具查詢目標客群，
# 整理出年齡層、興趣與觸及管道。用繁體中文。""",
#     tools=[get_audience_profile],
#     output_key="audience_profile",
# )

# ── TODO(3) writer.py：instruction 讀 state ───────────────────────
# instruction="""你是資深文案寫手，用繁體中文。
#
# 市場趨勢研究：
# {market_trends}
#
# 目標客群輪廓：
# {audience_profile}
#
# 根據以上研究，產出符合規格書的文案：
# - slogan：12 字以內
# - 賣點：恰好三條
# - 短文案：50 字以內
# - 全文至少自然提及一個目標客群的觸及管道
#
# 審稿意見（如果有，必須根據意見修改）：
# {review_feedback?}"""

# ── TODO(4) agent.py：組 LoopAgent 與 SequentialAgent ─────────────
# write_review_loop = LoopAgent(
#     name="write_review_loop",
#     sub_agents=[writer, reviewer],
#     max_iterations=3,
# )
# campaign_pipeline = SequentialAgent(
#     name="campaign_pipeline",
#     sub_agents=[trend_researcher, audience_researcher, write_review_loop, finalizer],
# )
# 注意最後一棒 finalizer（sub_agents/finalizer.py）：transfer 之後 root
# 拿不回控制權，若三輪審稿都沒過、迴圈被保險絲終止，沒有 finalizer 的話
# 對話會停在 reviewer 的退稿意見——成品躺在 state 裡沒人端出來。

# ── TODO(5) agent.py：掛 sub_agents ───────────────────────────────
# root_agent = Agent(
#     ...,
#     sub_agents=[campaign_pipeline],
# )

# ── TODO(6) tools.py：在 tool 裡讀寫 state ────────────────────────
# def record_revision(tool_context: ToolContext) -> dict:
#     count = tool_context.state.get("revision_count", 0) + 1
#     tool_context.state["revision_count"] = count
#     return {"revision_count": count, "is_final_round": count >= 2}
#     # 注意 >= 2 不是 3：max_iterations=3 下，第 2 次退稿後的 writer
#     # 是最後一次修改機會；count=3 時迴圈已結束，警告沒人讀得到
#
# 驗證：LLM 天生不擅長字數控制，規格書（check_copy_format 的 50 字/12 字限制）
# 常會讓迴圈自然轉起來——在 adk web 的 State 面板看 revision_count 逐輪 +1；
# 第 3 輪 reviewer 的意見開頭會出現「最後一輪，請務必定稿」。
#
# ── 設計筆記：為什麼審稿判準是數字不是品味 ─────────────────────────
# 迴圈的退出條件必須「可驗證」才不會漂：
#   check_copy_format（工具）給事實 → reviewer（LLM）給判斷。
# 主觀品味（有沒有記憶點）說不準，不適合當迴圈的方向盤——
# 那種審查留給人，或留在迴圈外。
#
# ── 設計筆記：回饋要帶目標值 ──────────────────────────────────────
# check_copy_format 的回傳連「上限」一起給（short_copy_limit 等欄位）。
# 實走時抓到的教訓：只回「61 字、不合格」，reviewer 會從 docstring
# 腦補目標值——docstring 一旦跟 code 脫鉤，writer 就朝錯的目標修，
# 迴圈永不收斂。權威數字只能有一個來源：工具的回傳值。
#
# ── 設計筆記：中間棒不要寒暄 ──────────────────────────────────────
# researcher/writer 的讀者是「下一位 agent」不是人——開場白與結尾反問
# 會原封不動存進 state（output_key 存的是整段回覆），下游拿到髒原料。
# 所以 instruction 明說「直接輸出結果，不要寒暄」。
