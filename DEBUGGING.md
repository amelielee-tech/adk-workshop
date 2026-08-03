# 怎麼看系統發生了什麼：adk web 與 Logs Explorer

寫 agent 最重要的能力不是寫 prompt，是**看得懂它為什麼這樣做**。
兩個工具：`adk web`（開發時看行為）、Logs Explorer（看底層 API 呼叫）。

## 1. adk web —— 你的主要觀測工具

### 打開方式

```bash
cd ~/adk-workshop
adk web          # 保持這個終端機開著
```

Cloud Shell：右上角 **Web Preview（眼睛圖示）→ Change port → 8000 → Preview**。
本機：直接開瀏覽器 http://localhost:8000。

### 介面導覽

- **左上角下拉選單**：選要跑哪個 agent（hello_agent / lab1_tools / ...）。
  改了 code 之後重新選一次 agent 或重整頁面即可，通常不用重啟 adk web。
- **中間對話區**：跟 agent 互動。
- **左側 Events 面板**：每一步都是一個 event，點開可以看到——
  - `functionCall`：LLM 決定呼叫哪個 tool、帶了什麼參數
  - `functionResponse`：tool 回了什麼
  - agent 之間的 **transfer**（誰把任務交給誰）——Lab 2 必看
  - 每個 event 來自哪個 agent（看 author 欄位）
- **State 分頁**：session state 的即時內容。Lab 2 觀察重點：
  跑完 trend_researcher 後 `market_trends` 什麼時候出現、
  writer 重寫時 `campaign_copy` 怎麼被覆蓋。
- **Trace 檢視**：點 event 可以看該次 LLM 呼叫的完整 request
  （system instruction、歷史、tool 定義）——「LLM 到底看到了什麼」的最終答案。

### 每個 Lab 該看什麼

| Lab | 觀察重點 |
|---|---|
| Lab 1 | Events 裡的 functionCall：參數是 LLM 自己從你的話裡抽出來的 |
| Lab 2 | transfer 順序 + State 分頁：資料怎麼一棒一棒傳 |
| Lab 3 | 被 guardrail 擋下的那輪：**沒有任何 LLM call 的 event** |

## 2. Logs Explorer —— 看雲端那一側

adk web 看的是「框架層」；Vertex AI 的 API 呼叫本身（誰打的、
打到哪個 model、有沒有 4xx/5xx）要去 Cloud Logging 看。

### 打開方式

GCP Console → 左側選單 **Logging → Logs Explorer**
（或搜尋列直接打 "Logs Explorer"）。

### 實用查詢

看所有 Vertex AI API 呼叫（確認 agent 真的打到雲端）：

```
resource.type="audited_resource"
protoPayload.serviceName="aiplatform.googleapis.com"
```

只看錯誤（403 權限、429 quota 超限都在這）：

```
protoPayload.serviceName="aiplatform.googleapis.com"
severity>=ERROR
```

右上角把時間範圍調成 **Last 30 minutes**，不然查詢很慢。

### 什麼時候需要來這裡

- agent 一直報錯但 adk web 的訊息看不出原因（權限/quota 問題會在這現形）
- 想確認「這次呼叫真的發生了嗎、打到哪個 model」
- 之後做 Campaign lab 部署到 Cloud Run / Agent Engine 時，
  **這裡就是你唯一的眼睛**——現在先養成看 log 的習慣

## 3. debug 的順序建議

1. 行為怪 → 先看 **Events**：LLM 有沒有呼叫你以為它會呼叫的 tool？
2. 資料不對 → 看 **State**：上游 agent 真的寫進去了嗎？key 名對嗎？
3. prompt 疑慮 → 看 **Trace**：LLM 實際收到的 instruction 長什麼樣？
4. 直接報錯 → 看終端機（跑 `adk web` 的那個）的 Python traceback
5. 雲端側錯誤（403/429/5xx）→ **Logs Explorer**
