"""Lab 3：用 callback 做 guardrail。

Callback 是 ADK 在 agent / model / tool 呼叫前後提供的掛鉤點。
before_model_callback 會在「每次要呼叫 LLM 之前」被執行：
  - 回傳 None       → 放行，照常呼叫 LLM
  - 回傳 LlmResponse → 短路！直接用這個回覆，LLM 根本不會被呼叫

實務用途：guardrail（擋敏感內容）、logging、快取。
這裡做一個 guardrail：使用者輸入提到競品名稱就直接擋下。
"""

from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

BLOCKED_KEYWORDS = ["品牌A", "品牌B", "品牌C"]

BLOCK_MESSAGE = "（Guardrail）請求中包含競品名稱，依公司政策不予處理。請改用一般性描述。"


def block_competitor_names(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """before_model guardrail：使用者訊息提到競品名稱時短路擋下。"""
    # 取出最後一則使用者訊息的文字
    last_user_text = ""
    for content in reversed(llm_request.contents or []):
        if content.role == "user" and content.parts:
            last_user_text = "".join(p.text or "" for p in content.parts)
            break

    # TODO(1): 完成 guardrail 邏輯——
    #   如果 last_user_text 包含任何 BLOCKED_KEYWORDS 裡的關鍵字，
    #   回傳一個 LlmResponse 短路擋下；否則回傳 None 放行。
    #
    #   短路回覆的寫法：
    #   return LlmResponse(
    #       content=types.Content(
    #           role="model",
    #           parts=[types.Part(text=BLOCK_MESSAGE)],
    #       )
    #   )
    return None
