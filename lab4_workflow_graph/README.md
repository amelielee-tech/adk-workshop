# Lab 4（Demo）：同一個文案小組的 ADK 2.0 版本

> 注意：ADK 2.0 的 graph API 目前 Go 版先行、Python 版仍在 alpha，
> 這個資料夾是**閱讀材料 / 講師示範**，不保證在你的環境直接跑起來
>（所以刻意不放 `__init__.py`，`adk web` 不會載入它）。

## 1.x 做不到（或做得很勉強）的三件事

回想你剛在 Lab 2 寫的系統：

1. **並行**：trend_researcher 和 audience_researcher 互不相依，
   但 `SequentialAgent` 只能讓它們排隊跑。
2. **明確的條件路由**：「合格→定稿、不合格→重寫」靠 reviewer
   「記得」呼叫 `approve_copy`——這是拜託 LLM，不是程式保證。
3. **重寫上限**：`max_iterations=3` 只是保險絲，
   「第 3 次還不合格該怎麼辦」沒有地方表達。

## 2.0 的解法：把流程畫成圖

看 `workflow.py`——同一個文案小組，流程全部變成 nodes + edges：

```
START ─┬─> trend_researcher ─────┐
       └─> audience_researcher ──┴─> [JoinNode] ─> writer ─> reviewer ─> route_quality
                                                      ^                       │
                                                      └──── "revise" ─────────┤
                                                                    "good" ──> finalize
```

- 兩條邊同時從 START 出發 = **並行**（scheduler 自動處理）
- JoinNode = 等兩份研究都到齊才往下
- route_quality 是**普通 Python function**，不呼叫 LLM：
  讀 reviewer 的結果決定走哪條邊，retry 上限就是一行 `>= 3`

**核心一句話：流程從「LLM 的一種行為」變成「程式的一個資料結構」。**
不確定性關進節點裡，流程本身是確定的——可測試、可重現、
還免費拿到並行、狀態保存和 human-in-the-loop。

延伸閱讀：
- [ADK graph-based workflows](https://adk.dev/graphs/)
- [ADK Go 2.0 announcement](https://developers.googleblog.com/announcing-adk-go-20/)
