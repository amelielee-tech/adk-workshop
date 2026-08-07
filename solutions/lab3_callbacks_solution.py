"""Lab 3 解答（callbacks.py 的 TODO(1)(2)(3) + agent.py 的 TODO(4)）"""

# ── TODO(1) callbacks.py：before_model 輸入攔截 ───────────────────
# for keyword in BLOCKED_KEYWORDS:
#     if keyword in last_user_text:
#         return LlmResponse(
#             content=types.Content(
#                 role="model",
#                 parts=[types.Part(text=BLOCK_MESSAGE)],
#             )
#         )
# return None

# ── TODO(2) callbacks.py：after_model 輸出改寫 ────────────────────
# if not llm_response.content or not llm_response.content.parts:
#     return None
# text = "".join(p.text or "" for p in llm_response.content.parts)
# if not any(kw in text for kw in BLOCKED_KEYWORDS):
#     return None
# for kw in BLOCKED_KEYWORDS:
#     text = text.replace(kw, "○○○")
# return LlmResponse(
#     content=types.Content(role="model", parts=[types.Part(text=text)])
# )

# ── TODO(3) callbacks.py：before_tool 參數校驗 ────────────────────
# if tool.name == "get_audience_profile":
#     if args.get("country") in RESTRICTED_COUNTRIES:
#         return {"status": "blocked", "message": RESTRICTED_MESSAGE}
# return None
#
# 為什麼不能用 before_model 做？因為 country 參數是「LLM 決定的」，
# 不一定原封不動出現在使用者訊息裡（使用者說「查對岸的」，
# LLM 可能翻成正式國名）——要卡參數，只能在 tool 層卡。

# ── TODO(4) agent.py：掛上三個 callback ───────────────────────────
# (4a) root_agent = Agent(
#     ...,
#     sub_agents=[campaign_pipeline],
#     before_model_callback=block_competitor_names,
#     after_model_callback=mask_competitor_names,
# )
# (4b) audience_researcher = Agent(
#     ...,
#     tools=[get_audience_profile],
#     output_key="audience_profile",
#     before_tool_callback=block_restricted_countries,
# )
# 掛 4b 在 audience_researcher 而非 root：tool 是掛在哪個 agent 上，
# before_tool_callback 就要掛在哪個 agent 上才攔得到。

# 驗證：
#   「幫我寫跟品牌A比較的文案」→ 被擋（Events 面板看不到 LLM 呼叫）
#   正常請求但輸出提到競品      → 回覆裡競品變 ○○○
#   「幫我查敏感國X的客群」      → tool 沒執行，回傳 blocked dict
