# Lab 5（Demo）：把 Lab 1–4 整套翻成 ADK 2.0

> 注意：ADK 2.0 的 graph API 目前 Go 版先行、Python 版仍在 alpha，
> 這個資料夾是**閱讀材料 / 講師示範**，不保證在你的環境直接跑起來
>（所以刻意不放 `__init__.py`，`adk web` 不會載入它）。

這一關不是新做一個系統，而是**回頭把你 Lab 1–4 蓋好的東西，用 2.0 的語言重講一次**——
看同一套 agent／工具／護欄／記憶，在「明確的圖」裡長什麼樣。

## 1.x 一路上那些「勉強」的地方

| 你在哪一關踩到 | 1.x 的做法（勉強） |
|---|---|
| Lab 2 並行 | 兩個 researcher 互不相依，`SequentialAgent` 卻只能排隊 |
| Lab 2 條件路由 | 「合格→定稿」靠 reviewer**記得**呼叫 `approve_copy`（拜託 LLM） |
| Lab 2 重寫上限 | `max_iterations=3` 只是保險絲，「耗盡怎麼辦」沒地方表達 |
| Lab 3 護欄 | callback 要**掛在對的 agent**上，掛錯就默默失效 |
| Lab 3 記憶 | load/save 靠 before/after_agent 手工掛點 |
| Lab 4 MCP | 工具來自 server，用起來 OK，但流程裡看不出它的位置 |

## 2.0 的解法：整套流程畫成一張圖

看 `workflow.py`——同一套東西，全部變成 nodes + edges：

```
START ─> load_memory ─┬─> trend_researcher ─────┐
                      └─> audience_researcher ──┴─> [Join] ─> writer ─> compliance_check
                                                                  ^            │
                                                        "revise" ─┤            ├─ "revise" ─┐
                                                                  │            └─ "ok" ─> reviewer ─> route_quality
                                                                  └────────────────────── "revise" ────────┤
                                                                                                "good" ─> finalize ─> save_memory ─> END
```

- 兩條邊同時從 `load_memory` 出發 = **並行**（取代 Lab 2 的排隊）
- `route_quality`／`compliance_gate` 是**普通 Python function**，不呼叫 LLM——條件路由與 retry 上限都是確定的 `if`
- Lab 3 的**護欄**與**記憶**：從「掛對 agent」變成圖上**看得見位置**的節點/邊
- Lab 4 的 **MCP 工具**：一樣掛節點，「工具即供應鏈」不變

**核心一句話：流程從「LLM 的一種行為」變成「程式的一個資料結構」。**
不確定性關進節點裡，流程本身可測試、可重現，還免費拿到並行與 human-in-the-loop。

## 跑得起來的差異示範（不用 adk web、不用 API key）

`workflow.py` 是示意 code（2.0 Python graph 仍 alpha），但差異可以**實際跑給人看**：

```bash
python lab5_workflow_graph/compare.py
```

它用兩個「假研究員」示範兩個核心差別，看得到數字：
- **序列 vs 並行**：1.x 排隊 ≈ 2.4s、2.0 並行 ≈ 1.2s（快一倍，研究員越多差距越大）
- **迴圈跳出**：2.0 的 `route_quality` 是純 Python，同樣的 state 永遠走同一條邊（可測試、可重現）

當天建議節奏：adk web 跑 **lab2**（看 researcher 排隊）→ `compare.py`（看並行快一倍）→ 讀 `workflow.py`（完整 2.0 圖）。**體感痛點 → 量化差異 → 看解法。**

> 只點到、不做：**MCP 是 agent 接工具，A2A 是 agent 接 agent**（跨系統/跨組織互相呼叫）——那是 capstone 的主題。

延伸閱讀：
- [ADK graph-based workflows](https://adk.dev/graphs/)
- [ADK Go 2.0 announcement](https://developers.googleblog.com/announcing-adk-go-20/)
