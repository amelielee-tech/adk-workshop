"""Lab 5：可跑的 1.x vs 2.0 差異示範（terminal，不用 adk web、不用 API key）。

    python lab5_workflow_graph/compare.py

用兩個「假研究員」（睡一下模擬查詢等待）示範 1.x → 2.0 最核心的兩個差別，
讓人親眼看到差異，而不是只讀 workflow.py 的示意 code。

真實情況：那 1.2 秒代表「等 LLM / 等工具回應」的時間；
並行的意義就是把兩邊的等待「疊在一起」，而不是排隊等兩次。
"""

import asyncio
import time


async def research(name: str, seconds: float = 1.2) -> str:
    print(f"    [{time.strftime('%H:%M:%S')}] {name} 開始查詢…")
    await asyncio.sleep(seconds)
    print(f"    [{time.strftime('%H:%M:%S')}] {name} 完成")
    return f"{name}_result"


# ── 差別①：序列 vs 並行 ──────────────────────────────────────
async def one_x_sequential() -> float:
    """1.x SequentialAgent：兩個研究員只能排隊，一個做完才換下一個。"""
    t = time.perf_counter()
    await research("trend_researcher")
    await research("audience_researcher")
    return time.perf_counter() - t


async def two_x_parallel() -> float:
    """2.0 graph：從 START 拉兩條邊 = 天然並行（兩邊的等待疊在一起）。"""
    t = time.perf_counter()
    await asyncio.gather(
        research("trend_researcher"),
        research("audience_researcher"),
    )
    return time.perf_counter() - t


# ── 差別②：迴圈跳出——拜託 LLM vs 確定的程式碼 ──────────────────
def route_quality(state: dict) -> str:
    """2.0：純 Python 的條件路由，不呼叫 LLM——同樣輸入永遠同樣結果。

    對比 1.x：迴圈能不能跳出，靠 reviewer「記得」呼叫 approve_copy（拜託 LLM）。
    """
    if state.get("verdict") == "good":
        return "good"
    if state.get("revision_count", 0) >= 3:  # retry 上限：一行 if
        return "good"  # 強制出場
    return "revise"


async def main() -> None:
    print("=" * 56)
    print("差別①：序列 vs 並行（跑跑看誰快）")
    print("=" * 56)
    print("\n[1.x SequentialAgent] 兩個研究員排隊：")
    seq = await one_x_sequential()
    print(f"  → 1.x 序列總耗時：{seq:.2f}s")
    print("\n[2.0 graph] 兩條邊從 START 出發、天然並行：")
    par = await two_x_parallel()
    print(f"  → 2.0 並行總耗時：{par:.2f}s")
    print(f"\n  結論：同樣兩個查詢，並行快了約 {seq - par:.2f}s（≈ {seq / par:.1f}x）。")
    print("  研究員越多、差距越大——這是 2.0 把並行變成預設的價值。\n")

    print("=" * 56)
    print("差別②：迴圈跳出——拜託 LLM vs 確定的程式碼")
    print("=" * 56)
    print("\n[1.x] 靠 reviewer『記得』呼叫 approve_copy 才跳出——會忘、不可測。")
    print("[2.0] route_quality 是純 Python，同樣的 state 永遠走同一條邊：")
    for s in [
        {"verdict": "good"},
        {"verdict": "bad", "revision_count": 1},
        {"verdict": "bad", "revision_count": 3},
    ]:
        print(f"    state={s} → 走 '{route_quality(s)}' 邊")
    print("\n  結論：流程從『LLM 的一種行為』變成『程式的一個資料結構』——")
    print("  可測試、可重現、retry 上限說了算。")


if __name__ == "__main__":
    asyncio.run(main())
