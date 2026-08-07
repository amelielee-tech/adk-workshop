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
# 根據以上研究，產出：一句 slogan、三個賣點、一段 50 字內的短文案。
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
#     sub_agents=[trend_researcher, audience_researcher, write_review_loop],
# )

# ── TODO(5) agent.py：掛 sub_agents ───────────────────────────────
# root_agent = Agent(
#     ...,
#     sub_agents=[campaign_pipeline],
# )

# ── TODO(6) tools.py：在 tool 裡讀寫 state ────────────────────────
# def record_revision(tool_context: ToolContext) -> dict:
#     count = tool_context.state.get("revision_count", 0) + 1
#     tool_context.state["revision_count"] = count
#     return {"revision_count": count, "is_final_round": count >= 3}
#
# 驗證：故意讓 reviewer 挑剔（例如要求「slogan 必須押韻」），
# 在 adk web 的 State 面板看 revision_count 逐輪 +1；
# 第 3 輪 reviewer 的意見開頭會出現「最後一輪，請務必定稿」。
