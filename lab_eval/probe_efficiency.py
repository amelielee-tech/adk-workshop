"""Lab A 效率步驟 —— 打一次 agent，量「延遲 latency」與「token 用量」。

為什麼要這支：
  adk eval 評的是「走對流程沒(trajectory) + 產出夠好沒(response)」，
  但 scorecard 上還有一軸叫「效率」——時間多久、花多少 token。
  這兩個數字**只有真的把 agent 跑一次才看得到**，evalset 看不出來。

它怎麼拿到數字（重點觀念）：
  ADK 每個「事件(event)」若來自一次 LLM 呼叫，就帶一包 usage_metadata，
  裡面有 prompt / output / total token 數。把每個 event 的累加起來 = 這次任務的總 token；
  用 time.time() 夾住整段 = latency。全部在本機 in-process，不需要部署任何 endpoint。

跑法（在 repo 根目錄、Cloud Shell / 本機都可，要有 Vertex 認證與 .env）：
  set -a; source .env; set +a          # 載入 GOOGLE_CLOUD_PROJECT 等
  python lab_eval/probe_efficiency.py           # 預設魚油
  python lab_eval/probe_efficiency.py 益生菌     # 換一個產品

看點：
  - latency 幾秒？多代理管線(coordinator→研究→writer⇄reviewer→finalizer)會呼叫多次 LLM，通常不快。
  - total tokens 多少？這對應 scorecard 的「費用壓縮」——token 就是錢。
  - 把數字對照 slide 的「時間 ≤ 11 秒」門檻，討論：這條管線達得到嗎？該怎麼取捨？
"""

import asyncio
import sys
import time

from google.adk.runners import InMemoryRunner
from google.genai import types

from lab2_multi_agent.agent import root_agent


async def run_once(product: str) -> None:
    runner = InMemoryRunner(agent=root_agent, app_name="lab_eval_efficiency")
    session = await runner.session_service.create_session(
        app_name="lab_eval_efficiency", user_id="student"
    )
    prompt = f"幫我為{product}做台灣市場的行銷文案。產品類別：{product}；市場：台灣。"
    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    llm_calls = prompt_tokens = output_tokens = total_tokens = 0
    final_text = ""

    start = time.time()
    async for event in runner.run_async(
        user_id="student", session_id=session.id, new_message=message
    ):
        usage = getattr(event, "usage_metadata", None)
        if usage:  # 這個 event 來自一次 LLM 呼叫
            llm_calls += 1
            prompt_tokens += getattr(usage, "prompt_token_count", 0) or 0
            output_tokens += getattr(usage, "candidates_token_count", 0) or 0
            total_tokens += getattr(usage, "total_token_count", 0) or 0
        if event.is_final_response() and event.content:
            final_text = "".join(p.text or "" for p in event.content.parts)
    latency = time.time() - start

    print("\n===== 效率指標（{}）=====".format(product))
    print(f"latency（牆鐘）: {latency:.1f} 秒")
    print(f"LLM 呼叫次數   : {llm_calls}")
    print(f"prompt tokens  : {prompt_tokens}")
    print(f"output tokens  : {output_tokens}")
    print(f"total tokens   : {total_tokens}")
    print(f"最終文案前 60 字: {final_text[:60]}")
    print("\n看點：對照 scorecard 的「時間 ≤ 11 秒 / 費用壓縮」——這條多代理管線達得到嗎？")


if __name__ == "__main__":
    product = sys.argv[1] if len(sys.argv) > 1 else "魚油"
    asyncio.run(run_once(product))
