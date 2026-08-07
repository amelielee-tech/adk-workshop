# ADK Multi-Agent Workshop：文案小組

用同一個例子（行銷文案小組）從零打造 multi-agent 系統，體驗 ADK 1.x 的協作方式，
最後對比 ADK 2.0 的 graph-based workflow。

## 課程對應

| 階段 | 資料夾 | 內容 | 形式 |
|---|---|---|---|
| 課前 | `hello_agent/` | 最小 agent，跑通 = 環境 OK | 完整可跑 |
| Lab 1 | `lab1_tools/` | Agent 怎麼用 tool | 讀 TODO(1)(2)，動手解開 TODO(3) 一行註解 |
| Lab 2 | `lab2_multi_agent/` | 主戰場：sub-agent、session state、SequentialAgent、LoopAgent、ToolContext 讀寫 state | 完整可跑，跟著 TODO 標註讀 |
| Lab 3 | `lab3_callbacks/` | 用 callback 做 guardrail（before_model / after_model / before_tool 三掛鉤對比） | 完整可跑，跟著 TODO 標註讀 |
| Demo | `lab4_workflow_graph/` | ADK 2.0 graph 對比（講師示範/閱讀材料） | 閱讀 |
| 延伸 | `challenges.md` | 給快的人的挑戰題 | 自選 |

Lab 裡的 `TODO(n)` 標註是導讀路標：解答已填好，照編號順序讀、每讀完一個就跑一次觀察行為。
（例外：Lab 1 的 TODO(3) `tools=[...]` 預設是**註解狀態**——先跑一次沒工具的版本看它瞎掰，
再解開註解對比 Events 的差別，這個對比就是 Lab 1 的重點。）
想自己動手挑戰的話，把 TODO 那幾行刪掉重寫，再和 `solutions/` 對答案；延伸挑戰見 `challenges.md`。

## 快速開始（Cloud Shell）

```bash
git clone https://github.com/amelielee-tech/adk-workshop.git
cd adk-workshop
pip install -r requirements.txt
cp .env.example .env        # 用 cloudshell edit .env 填自己的 project ID
gcloud services enable aiplatform.googleapis.com
adk web --allow_origins="regex:https://8000-cs-.*\.cloudshell\.dev" --reload_agents   # 兩個參數都必帶，見 SETUP.md
```

`adk web` 啟動後：Cloud Shell 右上角 **Web Preview → Change port → 8000 → Preview**，
左上角下拉選 `hello_agent`（清單裡的 `data`/`solutions`/`lab4` 不是 agent，點了會報錯屬正常），
對它說句話。**它回話 = 環境完成。**

> 模型註記：教材以 `gemini-2.5-flash` 測試（官方退役不早於 2026-10-16）。
> 屆時只需改各 lab `agent.py` 的 `model` 參數，但改完請重測 Lab 3 的 guardrail 行為。

詳細步驟見 [SETUP.md](SETUP.md)。
卡住時怎麼看發生了什麼（adk web 介面導覽、Logs Explorer）見 [DEBUGGING.md](DEBUGGING.md)。
想讀更完整的設計理念導覽（英文版，含每個 lab 的 why）見 [OVERVIEW.en.md](OVERVIEW.en.md)。

## 建議做法

1. 每完成一個 TODO 就回 `adk web` 跑一次，觀察行為變化（不是只看 code 有沒有錯）。
2. Lab 2 特別建議：掛上 sub-agent **之前**先跑一次，看 root agent 自己瞎掰；
   掛上**之後**再跑，看它 transfer——這個對比就是 multi-agent 的意義。
3. 用 `adk web` 左側的 Events 面板看 agent 之間的 transfer 與 state 變化。

## 部署呢？

部署在前一堂課教過，這裡不重複：這套文案小組同樣一行 `adk deploy agent_engine`
就能上 Agent Engine。想完整走一遍雲端部署，直接挑戰 `challenges.md` 的大魔王 lab。
