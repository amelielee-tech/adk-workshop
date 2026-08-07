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
    # TODO(1): 回傳一個 mock 的趨勢資料 dict——內容可以自己編，
    # 重點是結構清楚（status + 資料欄位），LLM 才好消化
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
        dict: 成功時包含 age_group（主力年齡層）、interests（興趣）、
        channels（觸及管道）；查無該國資料時 status 為 error
    """
    # TODO(2): 仿照 get_market_trends 回傳 mock dict——多一個看點：
    # 不支援的國家走 error 分支。試試問「德國的客群」，
    # 觀察 LLM 讀到 status=error 之後怎麼跟使用者說。
    if country not in ("台灣", "日本"):
        return {
            "status": "error",
            "error_message": f"查無「{country}」的客群資料，目前僅支援：台灣、日本",
        }
    return {
        "status": "success",
        "country": country,
        "age_group": "22-35 歲",
        "interests": ["健身", "路跑", "潮流穿搭", "咖啡"],
        "channels": ["Instagram", "YouTube Shorts", "Dcard"],
    }
