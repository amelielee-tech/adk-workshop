# 課前環境設定（約 10 分鐘）

全程在 **Cloud Shell** 進行，本機不需要安裝任何東西。

## 課前一天（30 秒）

1. 登入你的 GCP 專案 Console
2. 右上角啟動 Cloud Shell
3. 執行 `echo $GOOGLE_CLOUD_PROJECT`，把輸出貼到群組

這一步驗證：帳號能登、專案存在、Cloud Shell 能開。

## 當天步驟

### 1. 拿 code + 裝依賴

```bash
git clone https://github.com/amelielee-tech/adk-workshop.git
cd adk-workshop
pip install -r requirements.txt
```

（`pip install` 一定要在 `adk-workshop` 目錄下跑——家目錄若有別的專案留下的
`requirements.txt`，在外面跑會默默裝錯東西。）

### 2. 開 Cloud Shell Editor

```bash
cloudshell workspace ~/adk-workshop
```

這樣 Editor 檔案樹只會看到課程檔案，不會混進你家目錄的其他東西。
建議把 Editor 開成獨立視窗（右上角 Open in new window），一邊 Editor 一邊終端機。

### 3. 設定環境變數

```bash
cp .env.example .env
cloudshell edit .env
```

把 `GOOGLE_CLOUD_PROJECT` 改成你自己的 project ID，存檔。其他值不用動。

> 注意：`.env` 開頭是點，屬於隱藏檔——**Editor 的檔案樹看不到它是正常的**，
> 所以用 `cloudshell edit` 直接開。想確認檔案存在：`ls -a | grep env`。

### 4. 啟用 Vertex AI API

```bash
gcloud services enable aiplatform.googleapis.com
```

（Cloud Shell 的認證是自動的，不需要 `gcloud auth login`。）

### 5. 驗證：跑通 hello agent

```bash
adk web --allow_origins="regex:https://8000-cs-.*\.cloudshell\.dev" --reload_agents
```

兩個參數都**必帶**，這行全班通用、直接複製：
- `--allow_origins`：Web Preview 是反向代理，ADK 的 CSRF 防護會把它當
  陌生來源——少了它，畫面開得起來、但一開始對話就 403。
- `--reload_agents`：改 code 存檔後自動重新載入 agent。少了它，
  改任何 code 都要 Ctrl+C 重啟 adk web 才生效（Lab 都要改 code，必開）。

- 右上角 **Web Preview → Change port → 8000 → Preview**
- 左上角下拉選 `hello_agent`
  （清單裡的 `data`、`solutions`、`lab5_workflow_graph` 不是 agent，
  點了會報錯，屬正常，不用理）
- 對它說：「你好，你是誰？」

**它回話 = 環境完成，可以開始上課。**

## 常見問題

| 症狀 | 解法 |
|---|---|
| `adk: command not found` | `pip install -r requirements.txt` 沒跑成功（或不是在 `adk-workshop` 目錄下跑的），重跑並看錯誤訊息 |
| 畫面正常但一開始對話就 403 | `adk web` 沒帶 `--allow_origins` 參數，照步驟 5 的指令重啟 |
| Editor 檔案樹找不到 `.env` | 隱藏檔本來就不顯示，屬正常；用 `cloudshell edit .env` 開 |
| Agent 回 permission / 403 錯誤 | 步驟 4 的 API 沒啟用，或專案沒掛 billing |
| Web Preview 開不出來 | 確認 port 改成 8000；`adk web` 的終端機要保持開著 |
| Cloud Shell 重開後東西不見 | 只有 `~` 底下會保留；repo 有 clone 在 `~` 就沒事，重新 `cd adk-workshop` 即可 |
