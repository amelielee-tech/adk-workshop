"""Lab 3 解答（callbacks.py 的 TODO(1) + agent.py 的 TODO(2)）"""

# ── TODO(1) callbacks.py：guardrail 邏輯 ──────────────────────────
# for keyword in BLOCKED_KEYWORDS:
#     if keyword in last_user_text:
#         return LlmResponse(
#             content=types.Content(
#                 role="model",
#                 parts=[types.Part(text=BLOCK_MESSAGE)],
#             )
#         )
# return None

# ── TODO(2) agent.py：掛上 callback ───────────────────────────────
# root_agent = Agent(
#     ...,
#     sub_agents=[campaign_pipeline],
#     before_model_callback=block_competitor_names,
# )

# 驗證：
#   「幫我寫跟品牌A比較的文案」→ 被擋（Events 面板看不到 LLM 呼叫）
#   「幫我寫台灣運動鞋的文案」  → 照常運作
