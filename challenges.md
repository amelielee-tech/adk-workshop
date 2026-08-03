# 延伸挑戰（給做完主線的人）

按難度排序，自由選。

## 挑戰 1：結構化輸出（★）

讓 writer 保證回傳 JSON。
給 writer 加 `output_schema`（用 Pydantic BaseModel 定義
`slogan`、`selling_points`、`short_copy` 三個欄位）。
注意：設了 output_schema 的 agent 不能再用 tools——想想為什麼。

## 挑戰 2：retry 計數進 state（★★）

Lab 2 的重寫上限是 `max_iterations=3` 這個保險絲。
改成：在 state 裡記 `revision_count`，reviewer 的 instruction 讀得到
「這是第幾輪」，第 3 輪時必須在意見裡註明「最後一輪，請務必定稿」。
提示：可以在 tool 裡用 `tool_context.state` 讀寫。

## 挑戰 3：接真的 BigQuery（★★★）

把 `get_audience_profile` 的 mock 換成真 BQ 查詢：

```bash
cd data && bash load_to_bq.sh   # 建 dataset + 灌範例資料
```

然後用 `google.cloud.bigquery` 的 client 改寫 tool，
query `workshop_data.demographics` 表、依 country 過濾。
這正是 Campaign challenge lab 裡 Data Analyst agent 做的事（那邊用 MCP）。

## 挑戰 4：加一個 agent（★★★）

給小組加一位「投放建議師」：讀 state 裡的客群輪廓與定稿文案，
建議投放管道與預算分配，掛進 pipeline 的最後一棒。
從零寫一個 agent + 掛進既有結構，是檢驗你真的會了的最好方式。

## 大魔王：Campaign Challenge Lab

去 Google Skills 做 **[PTPPF] Build a Multi-Agent Campaign System
with ADK and Agent Engine**——MCP、A2A、Cloud Run、Agent Engine 全套，
有自動評分。做完它，你就從「會寫 multi-agent」升級到「會部署 multi-agent 系統」。
