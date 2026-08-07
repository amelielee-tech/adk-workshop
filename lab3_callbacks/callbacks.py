"""Lab 3：用 callback 做 guardrail —— 同一個概念、三個掛鉤點。

Callback 是 ADK 在 agent / model / tool 呼叫前後提供的掛鉤點。
這關做三個 guardrail，各掛在不同位置，對比它們攔截時機的差異：

  before_model_callback(callback_context, llm_request) -> Optional[LlmResponse]
    「每次要呼叫 LLM 之前」執行。
    回傳 None → 放行；回傳 LlmResponse → 短路！直接用這個回覆，LLM 不會被呼叫。

  after_model_callback(callback_context, llm_response) -> Optional[LlmResponse]
    「LLM 回覆之後、送回使用者之前」執行。
    回傳 None → 原樣放行；回傳 LlmResponse → 用你的版本取代原回覆。
    （攔截 vs 改寫，是兩種不同的 guardrail 哲學——做完想想各適合什麼場景）

  before_tool_callback(tool, args, tool_context) -> Optional[dict]
    「每次要執行 tool 之前」執行，看得到 tool 名稱與參數。
    回傳 None → 照常執行 tool；回傳 dict → 跳過 tool，直接把這個 dict 當結果。

實務用途：guardrail、logging、快取、參數校驗。
"""

from typing import Any, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

BLOCKED_KEYWORDS = ["品牌A", "品牌B", "品牌C"]

BLOCK_MESSAGE = "（Guardrail）請求中包含競品名稱，依公司政策不予處理。請改用一般性描述。"

RESTRICTED_COUNTRIES = ["敏感國X"]

RESTRICTED_MESSAGE = "（Guardrail）該地區的客群資料受政策限制，無法查詢。"


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

    # TODO(1): 包含競品關鍵字 → 短路擋下（回傳 LlmResponse，LLM 完全不會被呼叫）
    for keyword in BLOCKED_KEYWORDS:
        if keyword in last_user_text:
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=BLOCK_MESSAGE)],
                )
            )
    return None


def mask_competitor_names(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """after_model guardrail：模型輸出裡出現競品名稱時，改寫成 ○○○ 再放行。

    對比 TODO(1)：那邊是「整個擋掉」，這邊是「悄悄改寫」——
    輸出面的 guardrail 通常不能擋（回覆已經生成了），只能淨化。
    """
    # TODO(2): 輸出裡有競品名稱 → 替換成 ○○○ 後包成新的 LlmResponse 取代原回覆
    if not llm_response.content or not llm_response.content.parts:
        return None
    text = "".join(p.text or "" for p in llm_response.content.parts)
    if not any(kw in text for kw in BLOCKED_KEYWORDS):
        return None  # 乾淨的輸出原樣放行
    for kw in BLOCKED_KEYWORDS:
        text = text.replace(kw, "○○○")
    return LlmResponse(
        content=types.Content(role="model", parts=[types.Part(text=text)])
    )


def block_restricted_countries(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext
) -> Optional[dict]:
    """before_tool guardrail：攔截查詢受限地區客群的 tool 呼叫。

    這一層看得到「哪個 tool、帶什麼參數」——
    是三個掛鉤點裡唯一能針對參數做校驗的位置。
    """
    # TODO(3): 只攔 get_audience_profile、country 在受限清單時跳過 tool。
    #   為什麼不能用 before_model 做？因為 country 是「LLM 決定的參數」，
    #   不一定原封不動出現在使用者訊息裡——要卡參數，只能在 tool 層卡。
    if tool.name == "get_audience_profile":
        if args.get("country") in RESTRICTED_COUNTRIES:
            return {"status": "blocked", "message": RESTRICTED_MESSAGE}
    return None
