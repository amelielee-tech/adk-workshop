"""Lab 3：用 callback 做 guardrail —— 同一個概念、三個掛鉤點。

情境是「保健食品行銷」，因為法規對這行有很具體的禁令，三個掛鉤點正好各對一個真實需求：
  - 保健食品不得宣稱「醫療療效」（食安法／藥事法）→ 進來就擋（before_model）
  - 廣告不得「誇大不實／絕對化用語」→ 產生了只能洗（after_model）
  - 受限「成分／對象」不得行銷 → 卡在工具參數（before_tool）

三個掛鉤點的行為差異：

  before_model_callback(callback_context, llm_request) -> Optional[LlmResponse]
    「每次要呼叫 LLM 之前」執行。
    回傳 None → 放行；回傳 LlmResponse → 短路！直接用這個回覆，LLM 不會被呼叫。

  after_model_callback(callback_context, llm_response) -> Optional[LlmResponse]
    「LLM 回覆之後、送回使用者之前」執行。
    回傳 None → 原樣放行；回傳 LlmResponse → 用你的版本取代原回覆。
    （攔截 vs 改寫，是兩種不同的 guardrail 哲學——輸入面能「擋」，輸出面只能「洗」）

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

# ① before_model 要擋的：保健食品不得宣稱「醫療療效」
EFFICACY_CLAIMS = [
    "治療", "治癒", "療效", "根治", "抗癌", "降血壓", "降血糖", "預防疾病", "壯陽",
]
BLOCK_MESSAGE = (
    "（Guardrail）保健食品不得宣稱醫療療效（違反食品安全衛生管理法／藥事法），"
    "請改用「幫助」「調節生理機能」等一般性描述。"
)

# ② after_model 要洗的：廣告不得「誇大不實／絕對化用語」
EXAGGERATION_TERMS = [
    "全球銷量第一", "全台第一", "第一品牌", "100%有效",
    "立即見效", "七天見效", "無副作用", "永不復發", "保證有效",
]

# ③ before_tool 要卡的兩個維度：受限「成分」與受限「對象」
RESTRICTED_INGREDIENTS = ["褪黑激素", "大麻二酚", "CBD"]  # 在台屬藥品／管制，不得當保健食品行銷
INGREDIENT_MESSAGE = "（Guardrail）該成分在台灣屬藥品或管制項目，不得作為保健食品行銷。"

RESTRICTED_AUDIENCES = ["孕婦", "嬰幼兒", "慢性病患者"]  # 對這些族群宣稱保健功效受法規特別限制
AUDIENCE_MESSAGE = "（Guardrail）針對該族群宣稱保健功效受法規特別限制，無法產生此客群的文案。"


def block_efficacy_claims(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """before_model guardrail：使用者要求宣稱醫療療效時短路擋下。"""
    # 取出最後一則使用者訊息的文字
    last_user_text = ""
    for content in reversed(llm_request.contents or []):
        if content.role == "user" and content.parts:
            last_user_text = "".join(p.text or "" for p in content.parts)
            break

    # TODO(1): 包含療效宣稱字眼 → 短路擋下（回傳 LlmResponse，LLM 完全不會被呼叫）
    for keyword in EFFICACY_CLAIMS:
        if keyword in last_user_text:
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=BLOCK_MESSAGE)],
                )
            )
    return None


def mask_exaggeration(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """after_model guardrail：模型輸出出現誇大／絕對化用語時，改寫成 ○○○ 再放行。

    對比 TODO(1)：那邊是「整個擋掉」，這邊是「悄悄改寫」——
    輸出面的 guardrail 通常不能擋（回覆已經生成了），只能淨化。
    """
    # TODO(2): 輸出裡有誇大用語 → 替換成 ○○○ 後包成新的 LlmResponse 取代原回覆
    if not llm_response.content or not llm_response.content.parts:
        return None
    text = "".join(p.text or "" for p in llm_response.content.parts)
    if not any(term in text for term in EXAGGERATION_TERMS):
        return None  # 乾淨的輸出原樣放行
    for term in EXAGGERATION_TERMS:
        text = text.replace(term, "○○○")
    return LlmResponse(
        content=types.Content(role="model", parts=[types.Part(text=text)])
    )


def block_restricted_requests(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext
) -> Optional[dict]:
    """before_tool guardrail：攔截「受限成分」與「受限對象」的 tool 呼叫。

    這一層看得到「哪個 tool、帶什麼參數」——
    是三個掛鉤點裡唯一能針對參數做校驗的位置。
    我們同時守兩個 tool，所以這個 callback 會掛在「兩個」agent 上
    （擁有 get_market_trends 的 trend_researcher、擁有 get_audience_profile 的 audience_researcher）。
    """
    # TODO(3a): 產品類別是受限成分 → 跳過 tool（product_category 是 LLM 決定的參數，
    #   不一定原封不動出現在使用者訊息裡——要卡參數，只能在 tool 層卡）
    if tool.name == "get_market_trends":
        if args.get("product_category") in RESTRICTED_INGREDIENTS:
            return {"status": "blocked", "message": INGREDIENT_MESSAGE}

    # TODO(3b): 目標客群是受限對象 → 跳過 tool
    if tool.name == "get_audience_profile":
        if args.get("audience_group") in RESTRICTED_AUDIENCES:
            return {"status": "blocked", "message": AUDIENCE_MESSAGE}

    return None


# ═══════════════════════════════════════════════════════════════════
# 加碼：memory —— 用「agent 層」的掛鉤點（before/after_agent）
#
# 前面三個 guardrail 用的是 model 層與 tool 層；memory 從「agent 層」進來，
# 剛好把三個層級補齊。關鍵概念對比：
#   - session state（Lab 2）＝「這一場對話」的短期黑板，換 session 就沒了
#   - memory            ＝「跨 session」的長期記憶，這次存了下次還記得
# 情境：記住這個品牌過去的定稿與調性，讓 writer 保持一致。
#
# 註：memory 需要 runner 有配 MemoryService。adk web 預設帶 InMemoryMemoryService
#    （重啟就清空）。下面都包了 try/except，沒配也不會讓整條管線掛掉。
# ═══════════════════════════════════════════════════════════════════


async def load_brand_memory(callback_context: CallbackContext) -> Optional[Any]:
    """before_agent：agent 開跑前，從跨 session 的 memory 撈這個品牌過去的內容，
    塞進 state["brand_memory"] 供下游 writer 參考。

    第一次跑 memory 是空的——先跑完一次（after_agent 會存），下次再跑就撈得到。
    回傳 None → agent 照常執行（我們只是「順路載入記憶」，不攔截）。
    """
    # TODO(5a): 用 callback_context.search_memory 撈記憶，整理成文字寫進 state
    try:
        resp = await callback_context.search_memory("保健品行銷文案 品牌調性")
        snippets = []
        for m in resp.memories:
            if m.content and m.content.parts:
                snippets.append("".join(p.text or "" for p in m.content.parts))
        callback_context.state["brand_memory"] = (
            "\n".join(snippets) if snippets else "（尚無過去記錄）"
        )
    except Exception:
        callback_context.state["brand_memory"] = "（memory 未啟用）"
    return None


async def save_campaign_to_memory(callback_context: CallbackContext) -> Optional[Any]:
    """after_agent：整個 pipeline 跑完後，把這次 session 存進 memory，
    下次同品牌的活動就記得（跨 session）。回傳 None → 不改動輸出。
    """
    # TODO(5b): 用 callback_context.add_session_to_memory() 把這次對話存進長期記憶
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        pass
    return None
