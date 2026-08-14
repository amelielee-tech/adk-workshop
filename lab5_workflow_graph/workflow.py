"""Lab 5：把 Lab 1–4 整套「保健品文案小組」翻成 ADK 2.0 的 graph 版。

（示意程式碼，API 以正式版文件為準——重點是「流程怎麼表達」的轉變，不是背 API。）

對照 Lab 1–4：agent／工具／護欄／記憶都一樣，改變的只有「流程怎麼被表達」——
從「SequentialAgent/LoopAgent 的包裝 + prompt 裡的拜託 + callback 的手工掛點」，
變成一張明確的圖：節點是工作，邊是流程，條件是普通程式碼。

────────────────────────────────────────────────────────────
Lab 1–4 → 2.0 對照表（這一關的主線）
────────────────────────────────────────────────────────────
  Lab 1  tool＝Python function              → 2.0 一樣；tool 就是節點會用到的能力
  Lab 2  SequentialAgent 排隊               → 2.0 從 START 拉邊；互不相依的兩條邊＝天然並行
  Lab 2  LoopAgent + max_iterations 保險絲   → 2.0 一條「revise」回邊 + route 裡的計數器上限
  Lab 2  靠 prompt 拜託 reviewer 呼叫 approve → 2.0 route_quality 是確定的 if/else
  Lab 2  finalizer 手工收尾（怕斷尾）         → 2.0 finalize 是節點，「過稿」「耗盡」兩條邊都通到它
  Lab 3  guardrail 用 callback 手工掛對 agent  → 2.0 護欄是節點/邊上的攔截，位置畫在圖上看得見
  Lab 3  memory 用 before/after_agent          → 2.0 load/save memory 是圖首尾的節點
  Lab 4  MCP 工具（別人的/自製的）             → 2.0 一樣掛節點；「工具即供應鏈」不變
"""


def route_quality(state: dict) -> str:
    """條件路由：普通 Python 程式碼，不呼叫 LLM。

    reviewer（LLM）負責「評」，這裡負責「看評的結果決定走哪條邊」——
    把不確定性關在節點裡，路由本身是確定的。取代 Lab 2 靠 prompt 拜託跳迴圈。
    """
    if state.get("verdict") == "good":
        return "good"
    if state.get("revision_count", 0) >= 3:  # retry 上限：一行 if，不是 prompt 裡的拜託
        return "good"  # 強制出場（實務上可改走一條 "escalate" 邊交人工）
    state["revision_count"] = state.get("revision_count", 0) + 1
    return "revise"


def compliance_gate(state: dict) -> str:
    """Lab 3 的合規護欄，在 2.0 變成圖上一個明確關卡的路由。

    Lab 3 是把 callback「掛」在對的 agent 上（掛錯就失效）；
    2.0 直接把它畫成一條邊——不合規就回 writer，位置一目了然。
    """
    return "revise" if state.get("compliance", {}).get("passed") is False else "ok"


# --- 圖：整個應用的流程是一個資料結構 ---
#
# workflow = Workflow(
#     nodes=[load_memory,                       # Lab 3 memory：圖的第一個節點
#            trend_researcher, audience_researcher, join,   # audience 可掛 Lab 4 的 MCP 工具
#            writer, compliance_check, reviewer, route_quality,
#            finalize, save_memory],            # Lab 3 memory：圖的最後一個節點
#     edges=[
#         Edge(START, load_memory),
#         Edge(load_memory, trend_researcher),  # 兩條邊同時出發 = 並行
#         Edge(load_memory, audience_researcher),
#         Edge(trend_researcher, join),         # JoinNode：等兩邊都到齊
#         Edge(audience_researcher, join),
#         Edge(join, writer),
#         Edge(writer, compliance_check),       # Lab 4 自製合規 MCP：先過合規
#         Edge(compliance_check, writer,   condition="revise"),  # 不合規 → 退回（compliance_gate）
#         Edge(compliance_check, reviewer, condition="ok"),
#         Edge(reviewer, route_quality),
#         Edge(route_quality, finalize, condition="good"),
#         Edge(route_quality, writer,   condition="revise"),     # 迴圈 = 圖上一條回邊
#         Edge(finalize, save_memory),
#         Edge(save_memory, END),
#     ],
# )
#
# 一句話總結全場：
#   1.x 讓 LLM「即興」控制流程（靠 prompt 拜託、靠 callback 掛對位置）；
#   2.0 先「畫好」控制流程（節點、邊、條件），再讓 LLM 去填節點裡的內容。
#
# 延伸一句（不做，只點到）：MCP 是「agent 接工具」，A2A 是「agent 接 agent」——
#   跨系統/跨組織讓 agent 互相呼叫，是 capstone 的主題。
