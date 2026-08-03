# ADK Multi-Agent Workshop：文案小組

用同一個例子（行銷文案小組）從零打造 multi-agent 系統，體驗 ADK 1.x 的協作方式，
最後對比 ADK 2.0 的 graph-based workflow。

## 課程對應

| 階段 | 資料夾 | 內容 | 形式 |
|---|---|---|---|
| 課前 | `hello_agent/` | 最小 agent，跑通 = 環境 OK | 完整可跑 |
| Lab 1 | `lab1_tools/` | Agent 怎麼用 tool | 填 TODO |
| Lab 2 | `lab2_multi_agent/` | 主戰場：sub-agent、session state、SequentialAgent、LoopAgent | 填 TODO |
| Lab 3 | `lab3_callbacks/` | 用 callback 做 guardrail | 填 TODO |
| Demo | `lab4_workflow_graph/` | ADK 2.0 graph 對比（講師示範/閱讀材料） | 閱讀 |
| 延伸 | `challenges.md` | 給快的人的挑戰題 | 自選 |

卡住了？`solutions/` 裡有每個 lab 的完整解答，diff 一下就知道差在哪。

## 快速開始（Cloud Shell）

```bash
git clone https://github.com/amelielee-tech/adk-workshop.git
cd adk-workshop
pip install -r requirements.txt
cp .env.example .env        # 打開 .env 填自己的 project ID
gcloud services enable aiplatform.googleapis.com
adk web
```

`adk web` 啟動後：Cloud Shell 右上角 **Web Preview → Change port → 8000 → Preview**，
左上角下拉選 `hello_agent`，對它說句話。**它回話 = 環境完成。**

詳細步驟見 [SETUP.md](SETUP.md)。

## 建議做法

1. 每完成一個 TODO 就回 `adk web` 跑一次，觀察行為變化（不是只看 code 有沒有錯）。
2. Lab 2 特別建議：掛上 sub-agent **之前**先跑一次，看 root agent 自己瞎掰；
   掛上**之後**再跑，看它 transfer——這個對比就是 multi-agent 的意義。
3. 用 `adk web` 左側的 Events 面板看 agent 之間的 transfer 與 state 變化。
