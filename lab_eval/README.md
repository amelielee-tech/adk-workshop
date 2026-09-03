# Lab Eval：怎麼知道你的 agent「真的有用」

延續保健品文案小組——這一關不新做 agent,而是**回頭評估你蓋的東西**。兩種評法、兩個工具面:

| | 評什麼 | 工具 | 在哪跑 |
|---|---|---|---|
| **Lab A** | agent 走對流程沒(trajectory)+ 產出夠好沒(response) | **ADK 原生 `adk eval`** | Cloud Shell |
| **Lab B** | 沒有標準答案的「品質/合規/切題/依據」 | **LLM-as-judge**(Vertex Gen AI Eval)+ 開源 **RAGAS** 對照 | Colab |

> 定調:eval 是**方法論**,GCP 是主力工具、但不是唯一——Lab B 特意用 Vertex + RAGAS **兩家對照**。

---

## Lab A —— 用 `adk eval` 評 lab2 文案小組(Cloud Shell)

評估對象＝ `lab2_multi_agent`(campaign_coordinator → 研究 → writer⇄reviewer → finalizer)。

### 檔案
- `copy_agent.evalset.json` —— evalset,兩個案例(魚油、益生菌)。每個案例釘了**兩軸期望**:
  - **trajectory**:`intermediate_data.tool_uses` = 期望呼叫**研究工具 `get_market_trends`**(這關聚焦「它有沒有先做研究再動筆」)。
  - **response**:`final_response` = 期望的文案大意(用來算 response_match_score)。
- `test_config.json` —— 通過門檻(criteria):`tool_trajectory_avg_score`(門檻 1.0、`match_type: IN_ORDER`)、`response_match_score`(0.15)。

> 先把 `.env` 的 `GOOGLE_CLOUD_PROJECT` 改成**你自己的 GCP project**(跑 agent 會呼叫 Vertex 上的 Gemini)。

### 跑
```bash
# 在 repo 根目錄、Cloud Shell(有 Vertex 認證)
adk eval lab2_multi_agent lab_eval/copy_agent.evalset.json \
  --config_file_path lab_eval/test_config.json \
  --print_detailed_results
```

### 看這裡(兩個分數,分開看)
- **tool_trajectory_avg_score**：實際呼叫的工具 vs 期望工具的吻合度。
  - 觀念:這個指標是**逐案二元**——每個案例只有「全對(1.0)」或「全錯(0.0)」,名字裡的「avg」是**跨案例平均**(不是單案的部分分)。內建的比對**連參數都要對**,而且預設很嚴;本 config 用 `IN_ORDER`(期望工具照順序出現即可、允許中間有別的工具),並只斷言參數穩定的 `get_market_trends`,所以基準會綠。
- **response_match_score**：最終文案跟期望文案的**字面(ROUGE)重疊**。
  - ⚠️ 教學重點:文案是**創作**,字面比對本來就抓不到「語意相同、用字不同」,分數天生低又飄(所以門檻只能設到 0.15)。**這正是為什麼下一關(Lab B)要改用 LLM-judge**——字面指標評不動創作型品質。
- 一句話:**agent 評估分兩軸——走對流程 + 產出夠好;兩個分數要一起讀,而且要知道每個指標的極限。**

### 加一步：打 agent 看「效率」(latency + token)
adk eval 評品質,但 scorecard 還有一軸叫**效率**——時間多久、花多少 token。這只有真的跑一次才看得到:
```bash
set -a; source .env; set +a          # 載入你的 GCP project
python lab_eval/probe_efficiency.py           # 預設魚油;可加參數換產品,如 益生菌
```
看點:latency 幾秒、total tokens 多少 → 對照 scorecard 的「時間 ≤ 11 秒 / 費用壓縮」,討論這條多代理管線的效率代價。(跑兩次還會看到數字不一樣——這就是 LLM 的**非確定性**。)

### 小練習
- 想看「失敗長怎樣」:把某案例的期望工具改成一個不存在的名字 → 重跑 → 該案 trajectory 掉成 0.0、整體通過率下降。**這就是 regression eval 在做的事:證明你的 eval 抓得到退步。**

---

## Lab B —— LLM-as-judge + Groundedness(Colab)

文案的「合規/切題/有沒有依據研究」沒有標準答案 → 用模型當評審(LLM-as-judge)。**但 judge 自己也會判錯——所以本關的高潮是「驗證 judge 準不準」。**

敘事:**沒有標準答案 → 用 LLM-judge 打分 → 但 judge 會錯 → 一定要驗證(人工校準 + 換工具對照)。**

開 Colab notebook:
```
lab_eval/lab_eval.ipynb
```
(GitHub → Colab 一鍵:`https://colab.research.google.com/github/amelielee-tech/adk-workshop/blob/main/lab_eval/lab_eval.ipynb`)

步驟:
1. **Vertex Gen AI Eval — pointwise**:自訂 rubric(1–5)評「合規性」「切題度」(看它抓不抓得到故意寫壞的「神效魚油」)。
2. **Groundedness**:文案是不是真的**依據** market_trends / audience_profile,不是瞎編。
3. **換一家:RAGAS**:同一題用開源 faithfulness 跑一次,對照兩邊分數——**換工具對照本身就是一種 sanity check**(工具不獨大)。
4. ⭐ **驗證 judge(本關高潮)**:拿 3–5 題**人工標好**的分數,對照 judge 分數,算一致率;**找出不一致的那題、討論為什麼,調 rubric 後重跑看有沒有變準**。這步是我們盤點時**全公司專案都漏掉**的關鍵——也是你回到任何專案都能用的一招。

> 需要 GCP project(Vertex 有少量呼叫成本);Colab 與你的 ADK 環境隔離,不會弄壞 lab1–5。

---

## 版本說明
- 實習生環境＝ `google-adk==1.37.0`(見 `requirements.txt`);本 evalset 用 1.37 的 `EvalSet` 模型產生並驗證過格式。
- Lab B 用 `google-cloud-aiplatform[evaluation]`(Vertex Gen AI Eval)+ `ragas`,都在 Colab 裝,與本機/Cloud Shell 隔離。
