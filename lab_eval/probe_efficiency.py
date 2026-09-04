"""Lab A 效率步驟 —— 打一次 agent，① 看它吐的 event stream ② 量 latency 與 token。

為什麼要這支：
  adk eval 評「走對流程沒＋產出夠好沒」，但 scorecard 還有一軸叫「效率」——
  時間多久、花多少 token。這兩個只有真的把 agent 跑一次才看得到。

原理（重點觀念）：
  用 ADK 的 InMemoryRunner 跑 agent，runner.run_async() 會「一顆一顆」吐出 **event**
  （每個 event＝一件發生的事：交棒、呼叫工具、工具回應、LLM 產文字…）。
  其中「來自 LLM 呼叫」的 event 會帶一包 usage_metadata（prompt/output/total token）。
  → 我們邊收 event 邊：印出來給你看、順便把 token 累加；前後夾 time.time() = latency。

跑法（Colab / Cloud Shell 皆可，要有認證）：
  python lab_eval/probe_efficiency.py          # 預設魚油
  python lab_eval/probe_efficiency.py 益生菌    # 換產品
"""

import asyncio
import os
import sys
import time

# 讓「python lab_eval/probe_efficiency.py」從 repo 根目錄跑時，找得到 lab2_multi_agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.runners import InMemoryRunner
from google.genai import types

from lab2_multi_agent.agent import root_agent


def _describe(event) -> str:
    """把一個 event 濃縮成一行人看得懂的描述。"""
    bits = []
    if event.content and event.content.parts:
        for p in event.content.parts:
            fc = getattr(p, "function_call", None)
            fr = getattr(p, "function_response", None)
            if fc:
                bits.append(f"呼叫工具 {fc.name}")
            elif fr:
                bits.append(f"工具回應 {fr.name}")
            elif getattr(p, "text", None):
                bits.append("產文字：" + p.text.strip().replace("\n", " ")[:24])
    return "；".join(bits) if bits else "(狀態更新)"


async def run_once(product: str) -> None:
    runner = InMemoryRunner(agent=root_agent, app_name="lab_eval_efficiency")
    session = await runner.session_service.create_session(
        app_name="lab_eval_efficiency", user_id="student"
    )
    prompt = f"幫我為{product}做台灣市場的行銷文案。產品類別：{product}；市場：台灣。"
    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    n = llm_calls = prompt_tokens = output_tokens = total_tokens = 0
    final_text = ""

    print(f"===== agent 跑起來吐的 event stream（{product}）=====")
    start = time.time()
    async for event in runner.run_async(
        user_id="student", session_id=session.id, new_message=message
    ):
        n += 1
        usage = getattr(event, "usage_metadata", None)
        tok = ""
        if usage:  # 這個 event 來自一次 LLM 呼叫 → 帶 token
            llm_calls += 1
            prompt_tokens += getattr(usage, "prompt_token_count", 0) or 0
            output_tokens += getattr(usage, "candidates_token_count", 0) or 0
            total_tokens += getattr(usage, "total_token_count", 0) or 0
            tok = f"  [+{getattr(usage, 'total_token_count', 0)} tok]"
        author = getattr(event, "author", "?")
        print(f"event {n:2d} | {author:20.20s} | {_describe(event)}{tok}")
        if event.is_final_response() and event.content:
            final_text = "".join(p.text or "" for p in event.content.parts)
    latency = time.time() - start

    print(f"\n===== 效率總計（{product}）=====")
    print(f"latency（牆鐘）: {latency:.1f} 秒")
    print(f"event 總數     : {n}（其中 {llm_calls} 個來自 LLM 呼叫、帶 token）")
    print(f"prompt tokens  : {prompt_tokens}")
    print(f"output tokens  : {output_tokens}")
    print(f"total tokens   : {total_tokens}")
    print(f"最終文案前 60 字: {final_text[:60]}")
    print("\n看點：① 每個 LLM event 的 token 加總就是 total ② 對照 scorecard「時間 ≤ 11 秒」——這條多代理管線達得到嗎？")


if __name__ == "__main__":
    product = sys.argv[1] if len(sys.argv) > 1 else "魚油"
    asyncio.run(run_once(product))
