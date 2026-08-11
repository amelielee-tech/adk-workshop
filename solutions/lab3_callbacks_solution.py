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

# ── TODO(4) agent.py：把三個 callback 掛上「對的」agent ────────────
# 本關最重要的一句話：callback 掛在哪個 agent，就只管那個 agent。
#
# (4a) 輸入攔截 → 掛 root（使用者訊息的第一站，前門）：
# root_agent = Agent(
#     ...,
#     sub_agents=[campaign_pipeline],
#     before_model_callback=block_competitor_names,
# )
# (4b) 參數校驗 → 掛「擁有那個 tool 的 agent」：
# audience_researcher = Agent(
#     ...,
#     tools=[get_audience_profile],
#     output_key="audience_profile",
#     before_tool_callback=block_restricted_countries,
# )
# (4c) 輸出淨化 → 掛「會講髒話的那張嘴」：
# trend_researcher = Agent(
#     ...,
#     tools=[get_market_trends],
#     output_key="market_trends",
#     after_model_callback=mask_competitor_names,
# )
# 為什麼 4c 不能掛 root？實測踩過的坑：root transfer 之後不再說話，
# 講「品牌A」的是 trend_researcher——mask 掛在 root 上永遠不會觸發，
# 競品名整路裸奔。掛錯位置的 guardrail 等於沒有 guardrail。
# 額外紅利：淨化發生在寫進 state 之前，下游 writer 拿到的原料已是 ○○○ 版。

# 驗證：
#   「幫我寫跟品牌A比較的文案」→ 被擋（Events 面板看不到 LLM 呼叫）
#   正常請求但輸出提到競品      → 回覆裡競品變 ○○○
#   「幫我查敏感國X的客群」      → tool 沒執行，回傳 blocked dict
