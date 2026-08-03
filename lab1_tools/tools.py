"""Lab 1 的 tools。

Agent 的 tool 就是普通的 Python function：
- function 名稱、參數型別、docstring 都會被送給 LLM，讓它知道「這個工具是幹嘛的、怎麼呼叫」
- 所以 docstring 要寫清楚——它就是給 LLM 看的說明書

這裡用 mock 資料（寫死的 dict），重點是學「agent 怎麼用 tool」。
想接真的 BigQuery？做完主線後看 challenges.md 的挑戰 3。
"""


def get_market_trends(product_category: str) -> dict:
    """查詢指定產品類別的市場趨勢。

    Args:
        product_category: 產品類別，例如「運動鞋」「咖啡」「手搖飲」

    Returns:
        dict: 包含 trends（近期趨勢列表）與 competitors（主要競品）
    """
    # TODO(1): 回傳一個 mock 的趨勢資料 dict
    # 格式範例：
    # {
    #     "status": "success",
    #     "category": product_category,
    #     "trends": ["永續材質成為主流", "聯名款帶動話題", "短影音開箱是主要導購管道"],
    #     "competitors": ["品牌A", "品牌B"],
    # }
    # 提示：內容可以自己編，重點是回傳結構清楚的 dict
    pass


def get_audience_profile(country: str) -> dict:
    """查詢指定國家/地區的目標客群輪廓。

    Args:
        country: 國家或地區，例如「台灣」「日本」

    Returns:
        dict: 包含 age_group（主力年齡層）、interests（興趣）、channels（觸及管道）
    """
    # TODO(2): 仿照 get_market_trends，回傳一個 mock 的客群資料 dict
    # 至少包含 age_group、interests、channels 三個 key
    pass
