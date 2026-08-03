# 課前環境設定（約 10 分鐘）

全程在 **Cloud Shell** 進行，本機不需要安裝任何東西。

## 課前一天（30 秒）

1. 登入你的 GCP 專案 Console
2. 右上角啟動 Cloud Shell
3. 執行 `echo $GOOGLE_CLOUD_PROJECT`，把輸出貼到群組

這一步驗證：帳號能登、專案存在、Cloud Shell 能開。

## 當天步驟

### 1. 開 Cloud Shell Editor

```bash
cloudshell workspace ~
```

建議把 Editor 開成獨立視窗（右上角 Open in new window），一邊 Editor 一邊終端機。

### 2. 拿 code + 裝依賴

```bash
git clone https://github.com/amelielee-tech/adk-workshop.git
cd adk-workshop
pip install -r requirements.txt
```

### 3. 設定環境變數

```bash
cp .env.example .env
```

在 Editor 打開 `.env`，把 `GOOGLE_CLOUD_PROJECT` 改成你自己的 project ID。
其他值不用動。

### 4. 啟用 Vertex AI API

```bash
gcloud services enable aiplatform.googleapis.com
```

（Cloud Shell 的認證是自動的，不需要 `gcloud auth login`。）

### 5. 驗證：跑通 hello agent

```bash
adk web
```

- 右上角 **Web Preview → Change port → 8000 → Preview**
- 左上角下拉選 `hello_agent`
- 對它說：「你好，你是誰？」

**它回話 = 環境完成，可以開始上課。**

## 常見問題

| 症狀 | 解法 |
|---|---|
| `adk: command not found` | `pip install -r requirements.txt` 沒跑成功，重跑並看錯誤訊息 |
| Agent 回 permission / 403 錯誤 | 步驟 4 的 API 沒啟用，或專案沒掛 billing |
| Web Preview 開不出來 | 確認 port 改成 8000；`adk web` 的終端機要保持開著 |
| Cloud Shell 重開後東西不見 | 只有 `~` 底下會保留；repo 有 clone 在 `~` 就沒事，重新 `cd adk-workshop` 即可 |
