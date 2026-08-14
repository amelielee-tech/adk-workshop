"""Lab 3 解答（callbacks.py 的 TODO(1)(2)(3) + agent.py 的 TODO(4)）。保健品行銷情境。"""

# ── TODO(1) callbacks.py：before_model 輸入攔截（療效宣稱）──────────
# for keyword in EFFICACY_CLAIMS:
#     if keyword in last_user_text:
#         return LlmResponse(
#             content=types.Content(
#                 role="model",
#                 parts=[types.Part(text=BLOCK_MESSAGE)],
#             )
#         )
# return None

# ── TODO(2) callbacks.py：after_model 輸出改寫（誇大用語）──────────
# if not llm_response.content or not llm_response.content.parts:
#     return None
# text = "".join(p.text or "" for p in llm_response.content.parts)
# if not any(term in text for term in EXAGGERATION_TERMS):
#     return None
# for term in EXAGGERATION_TERMS:
#     text = text.replace(term, "○○○")
# return LlmResponse(
#     content=types.Content(role="model", parts=[types.Part(text=text)])
# )

# ── TODO(3) callbacks.py：before_tool 參數校驗（成分 + 對象）───────
# if tool.name == "get_market_trends":
#     if args.get("product_category") in RESTRICTED_INGREDIENTS:
#         return {"status": "blocked", "message": INGREDIENT_MESSAGE}
# if tool.name == "get_audience_profile":
#     if args.get("audience_group") in RESTRICTED_AUDIENCES:
#         return {"status": "blocked", "message": AUDIENCE_MESSAGE}
# return None
#
# 為什麼不能用 before_model 做？因為 product_category / audience_group 是「LLM 決定的」，
# 不一定原封不動出現在使用者訊息裡（使用者說「幫我做助眠的」，
# LLM 可能自己填成分「褪黑激素」）——要卡參數，只能在 tool 層卡。

# ── TODO(4) agent.py：把三個 callback 掛上「對的」agent ────────────
# 本關最重要的一句話：callback 掛在哪個 agent，就只管那個 agent。
#
# (4a) 輸入攔截 → 掛 root（使用者訊息的第一站，前門）：
# root_agent = Agent(
#     ...,
#     sub_agents=[campaign_pipeline],
#     before_model_callback=block_efficacy_claims,
# )
# (4b) 參數校驗 → 掛「擁有那個 tool 的 agent」。這關守兩個 tool，所以掛兩個 agent：
# trend_researcher = Agent(
#     ..., tools=[get_market_trends], output_key="market_trends",
#     after_model_callback=mask_exaggeration,         # 4c 也在這，一個 agent 可多個 callback
#     before_tool_callback=block_restricted_requests,  # 守 product_category（成分）
# )
# audience_researcher = Agent(
#     ..., tools=[get_audience_profile], output_key="audience_profile",
#     before_tool_callback=block_restricted_requests,  # 守 audience_group（對象）
# )
# (4c) 輸出淨化 → 掛「會講髒話的那張嘴」= trend_researcher（見上）：
# 為什麼 4c 不能掛 root？實測踩過的坑：root transfer 之後不再說話，
# 講出誇大詞的是 trend_researcher——mask 掛在 root 上永遠不會觸發，整路裸奔。
# 掛錯位置的 guardrail 等於沒有 guardrail。
# 額外紅利：淨化發生在寫進 state 之前，下游 writer 拿到的原料已是 ○○○ 版。

# ── TODO(5) 加碼 memory：before_agent 載入 / after_agent 存 ─────────
# (5a) callbacks.py：before_agent 從 memory 撈，寫進 state
# resp = await callback_context.search_memory("保健品行銷文案 品牌調性")
# snippets = ["".join(p.text or "" for p in m.content.parts)
#             for m in resp.memories if m.content and m.content.parts]
# callback_context.state["brand_memory"] = "\n".join(snippets) or "（尚無過去記錄）"
# (5b) callbacks.py：after_agent 把這次 session 存進 memory
# await callback_context.add_session_to_memory()
# 掛法（agent.py）：載入掛 root.before_agent_callback（前門）；
#   存記憶掛 campaign_pipeline.after_agent_callback（整條跑完才存一次，
#   別掛迴圈裡的 reviewer——那會每輪存一次）。writer instruction 加 {brand_memory?}。
# 概念：session state=這場對話的短期黑板；memory=跨 session 的長期記憶。

# 驗證：
#   「幫我寫魚油能『治療』高血壓的文案」→ 被擋（Events 面板看不到 LLM 呼叫）
#   正常請求但輸出提到「全球銷量第一／立即見效」→ 回覆裡誇大詞變 ○○○
#   「幫『褪黑激素』做文案」→ get_market_trends 沒執行，回傳 blocked dict
#   「針對『孕婦』做文案」  → get_audience_profile 沒執行，回傳 blocked dict
#   memory：跑完一次某品牌 → 新 session 再跑同品牌，state.brand_memory 出現舊內容
