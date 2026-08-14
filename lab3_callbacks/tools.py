"""Lab 3 的 tools —— 與 Lab 2 相同，不用改。（保健品行銷情境）"""

from google.adk.tools.tool_context import ToolContext


def get_market_trends(product_category: str) -> dict:
    """查詢指定保健品類別的市場趨勢。

    Args:
        product_category: 保健品類別，例如「魚油」「益生菌」「葉黃素」

    Returns:
        dict: 包含 trends（近期趨勢列表）與 competitors（主要競品）
    """
    return {
        "status": "success",
        "category": product_category,
        # 注意最後一條刻意含「誇大／絕對化」用語——after_model guardrail 的活靶：
        # 研究員照實輸出趨勢時就會帶出這些詞，正好示範「輸出淨化」怎麼把它洗掉。
        "trends": [
            "「無添加」與「有效成分含量標示」成為選購主流",
            "銀髮保養與慢性調理族群快速成長",
            "競品普遍主打「全球銷量第一」「七天立即見效」等強打訴求",
        ],
        "competitors": ["品牌A", "品牌B", "品牌C"],
    }


def get_audience_profile(country: str, audience_group: str = "一般成人") -> dict:
    """查詢指定市場／客群的目標客群輪廓。

    Args:
        country: 國家或地區，例如「台灣」「日本」
        audience_group: 目標客群，例如「一般成人」「銀髮族」「孕婦」

    Returns:
        dict: 包含 age_group（主力年齡層）、interests（興趣）、channels（觸及管道）
    """
    return {
        "status": "success",
        "country": country,
        "audience_group": audience_group,
        "age_group": "35-55 歲",
        "interests": ["保健養生", "運動健身", "抗老"],
        "channels": ["Facebook", "LINE", "YouTube"],
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
