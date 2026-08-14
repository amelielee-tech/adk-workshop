"""Lab 4 的本地 tools —— trend_researcher 仍用它，audience_researcher 改用 MCP。"""

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
        "trends": [
            "「無添加」與「有效成分含量標示」成為選購主流",
            "銀髮保養與慢性調理族群快速成長",
            "短影音與 KOL 開箱是最主要的導購管道",
        ],
        "competitors": ["品牌A", "品牌B", "品牌C"],
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
