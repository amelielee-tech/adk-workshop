"""Lab 2 的 tools —— 研究類 tool 是 Lab 1 的完成版，直接複用。

但這裡多了一個新概念 —— ToolContext：
tool 的參數裡宣告 tool_context: ToolContext，ADK 就會自動注入。
透過它可以：
  - tool_context.state          → 讀寫 session state（跨 agent 共享的黑板）
  - tool_context.actions        → 控制流程（例如 escalate 跳出迴圈）
state 是 multi-agent 的血管，debug 九成在查它——這關要你親手摸一次。"""

from google.adk.tools.tool_context import ToolContext


def get_market_trends(product_category: str) -> dict:
    """查詢指定產品類別的市場趨勢。

    Args:
        product_category: 產品類別，例如「運動鞋」「咖啡」「手搖飲」

    Returns:
        dict: 包含 trends（近期趨勢列表）與 competitors（主要競品）
    """
    return {
        "status": "success",
        "category": product_category,
        "trends": [
            "永續材質成為主流話題",
            "聯名限定款帶動搶購潮",
            "短影音開箱是最主要的導購管道",
        ],
        "competitors": ["品牌A", "品牌B", "品牌C"],
    }


def get_audience_profile(country: str) -> dict:
    """查詢指定國家/地區的目標客群輪廓。

    Args:
        country: 國家或地區，例如「台灣」「日本」

    Returns:
        dict: 包含 age_group（主力年齡層）、interests（興趣）、channels（觸及管道）
    """
    return {
        "status": "success",
        "country": country,
        "age_group": "22-35 歲",
        "interests": ["健身", "路跑", "潮流穿搭", "咖啡"],
        "channels": ["Instagram", "YouTube Shorts", "Dcard"],
    }


def approve_copy(tool_context: ToolContext) -> dict:
    """審稿通過時呼叫此工具，結束修改迴圈、定稿。

    Args:
        tool_context: ADK 自動注入的工具上下文

    Returns:
        dict: 定稿確認
    """
    # escalate = True 會讓 LoopAgent 停止迴圈——這就是 1.x 跳出迴圈的方式：
    # 「靠 LLM 記得呼叫這個工具」。上完 2.0 的部分後回頭看，
    # 你會發現 2.0 把這件事變成 graph 上一條明確的邊。
    tool_context.actions.escalate = True
    return {"status": "approved", "message": "文案定稿"}


def record_revision(tool_context: ToolContext) -> dict:
    """審稿「不通過、要退回重寫」時呼叫此工具，登記這是第幾輪修改。

    Args:
        tool_context: ADK 自動注入的工具上下文

    Returns:
        dict: 包含 revision_count（目前輪數）與 is_final_round（是否已達最後一輪）
    """
    # TODO(6): 用 tool_context.state 實作輪數計數——
    #   state 用起來就像 dict；這是「在 tool 裡讀寫 state」的標準姿勢。
    #   跑起來後到 adk web 的 State 面板親眼看 revision_count 逐輪 +1，
    #   並對照 reviewer.py 的 instruction 怎麼配合這個工具。
    count = tool_context.state.get("revision_count", 0) + 1
    tool_context.state["revision_count"] = count
    return {"revision_count": count, "is_final_round": count >= 3}
