"""Lab 1 解答（tools.py 的 TODO(1)(2) + agent.py 的 TODO(3)）。保健品行銷情境。"""

from google.adk.agents import Agent


# TODO(1) 解答
def get_market_trends(product_category: str) -> dict:
    """查詢指定保健品類別的市場趨勢。

    Args:
        product_category: 保健品類別，例如「魚油」「益生菌」「葉黃素」

    Returns:
        dict: 包含 trends（近期趨勢列表）與 competitors（主要競品）
    """
    return {
        # status 是給 LLM 讀的紅綠燈：用固定欄位明說「查到了/失敗了」，
        # 它才不會拿到空資料自由發揮
        "status": "success",
        "category": product_category,
        "trends": [
            "「無添加」與「有效成分含量標示」成為選購主流",
            "銀髮保養與慢性調理族群快速成長",
            "短影音與 KOL 開箱是最主要的導購管道",
        ],
        "competitors": ["品牌A", "品牌B", "品牌C"],
    }


# TODO(2) 解答：mock 資料庫——有資料的國家才在這裡，查不到就 error
MOCK_PROFILES = {
    "台灣": {
        "age_group": "35-55 歲",
        "interests": ["保健養生", "運動健身", "抗老"],
        "channels": ["Facebook", "LINE", "YouTube"],
    },
    "日本": {
        "age_group": "40-60 歲",
        "interests": ["抗老", "機能食品", "骨骼保健"],
        "channels": ["LINE", "X", "YouTube"],
    },
}


def get_audience_profile(country: str, audience_group: str = "一般成人") -> dict:
    """查詢指定市場／客群的目標客群輪廓。

    Args:
        country: 國家或地區，例如「台灣」「日本」
        audience_group: 目標客群，例如「一般成人」「銀髮族」

    Returns:
        dict: 成功時包含 age_group（主力年齡層）、interests（興趣）、
        channels（觸及管道）；查無該國資料時 status 為 error
    """
    profile = MOCK_PROFILES.get(country)
    if profile is None:
        return {
            "status": "error",
            "error_message": (
                f"查無「{country}」的客群資料，目前僅支援：{'、'.join(MOCK_PROFILES)}"
            ),
        }
    return {"status": "success", "country": country, "audience_group": audience_group, **profile}


# TODO(3) 解答：tools 參數掛上 function list
root_agent = Agent(
    name="research_assistant",
    model="gemini-2.5-flash",
    description="保健品市場研究助理，可以查詢市場趨勢與客群輪廓。",
    instruction="""你是保健品市場研究助理，用繁體中文回答。
使用者詢問市場或客群資訊時，務必使用工具查詢，不要憑空編造。
回答市場或客群問題時，只能根據工具回傳的內容；工具沒有提供的資訊
（例如價格、市占率、品牌評價），一律回答「查無資料」，不要推測補充。
若工具回傳的 status 不是 success，直接告知查詢失敗。
回答時整理成條列式，並注明資料來自工具查詢。""",
    tools=[get_market_trends, get_audience_profile],
)
