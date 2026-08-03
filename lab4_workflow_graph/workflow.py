"""文案小組的 ADK 2.0 graph 版（示意程式碼，API 以正式版文件為準）。

對照 Lab 2：agent 們完全一樣，改變的只有「流程怎麼表達」——
從 SequentialAgent/LoopAgent 的包裝 + prompt 裡的拜託，
變成一張明確的圖。
"""

# --- 節點：跟 Lab 2 相同的 agents（略，想像它們已 import 進來）---
# trend_researcher, audience_researcher, writer, reviewer, finalize


def route_quality(state: dict) -> str:
    """條件路由：普通 Python 程式碼，不呼叫 LLM。

    reviewer（LLM）負責「評」，這裡負責「看評的結果決定走哪條邊」——
    把不確定性關在節點裡，路由本身是確定的。
    """
    if state.get("verdict") == "good":
        return "good"
    if state.get("revision_count", 0) >= 3:  # retry 上限：一行 if，不是 prompt 裡的拜託
        return "good"  # 強制出場（實務上可改走一條 "escalate" 邊交人工）
    state["revision_count"] = state.get("revision_count", 0) + 1
    return "revise"


# --- 圖：整個應用的流程是一個資料結構 ---
#
# workflow = Workflow(
#     nodes=[trend_researcher, audience_researcher, join,
#            writer, reviewer, route_quality, finalize],
#     edges=[
#         Edge(START, trend_researcher),       # 兩條邊同時出發 = 並行
#         Edge(START, audience_researcher),
#         Edge(trend_researcher, join),        # JoinNode：等兩邊都到齊
#         Edge(audience_researcher, join),
#         Edge(join, writer),
#         Edge(writer, reviewer),
#         Edge(reviewer, route_quality),
#         Edge(route_quality, finalize, condition="good"),
#         Edge(route_quality, writer,   condition="revise"),  # 迴圈 = 圖上一條邊
#     ],
# )
#
# 對照表：
#   1.x 的 SequentialAgent 排隊     → 2.0 從 START 拉兩條邊，天然並行
#   1.x 靠 prompt 拜託 reviewer 跳出 → 2.0 的 route_quality 是確定的 if/else
#   1.x 的 max_iterations 保險絲    → 2.0 的 revision_count 計數器，超限走哪條邊你說了算
