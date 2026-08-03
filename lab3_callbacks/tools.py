"""Lab 3 的 tools —— 與 Lab 2 相同，不用改。"""

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
    tool_context.actions.escalate = True
    return {"status": "approved", "message": "文案定稿"}
