"""Lab 2 的 tools —— 研究類 tool 是 Lab 1 的完成版，直接複用。

但這裡多了一個新概念 —— ToolContext：
tool 的參數裡宣告 tool_context: ToolContext，ADK 就會自動注入。
透過它可以：
  - tool_context.state          → 讀寫 session state（跨 agent 共享的黑板）
  - tool_context.actions        → 控制流程（例如 escalate 跳出迴圈）
state 是 multi-agent 的血管，debug 九成在查它——這關要你親手摸一次。"""

from google.adk.tools.tool_context import ToolContext


def get_market_trends(product_category: str) -> dict:
    """查詢指定保健品類別的市場趨勢。

    Args:
        product_category: 保健品類別，例如「魚油」「益生菌」「葉黃素」

    Returns:
        dict: 包含 trends（近期趨勢列表）與 competitors（主要競品）
    """
    return {
        # status 是給 LLM 讀的紅綠燈：用固定欄位明說「查到了/失敗了」
        "status": "success",
        "category": product_category,
        "trends": [
            "「無添加」與「有效成分含量標示」成為選購主流",
            "銀髮保養與慢性調理族群快速成長",
            "短影音與 KOL 開箱是最主要的導購管道",
        ],
        "competitors": ["品牌A", "品牌B", "品牌C"],
    }


# mock 資料庫：有資料的國家才在這裡。查得到就回、查不到就 error（同 Lab 1）
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
    # is_final_round 在「倒數第二次退稿」就要亮——max_iterations=3 之下，
    # 第 2 次退稿後的那輪 writer 是最後一次修改機會；等 count=3 才警告，
    # 迴圈已經結束，誰都讀不到
    return {"revision_count": count, "is_final_round": count >= 2}


def check_copy_format(slogan: str, selling_points: list[str], short_copy: str) -> dict:
    """檢查文案是否符合規格書，回傳各項量測數字。

    規格書：slogan ≤ 12 字；賣點恰好 3 條；短文案 ≤ 50 字；
    至少自然提及 1 個觸及管道。

    Args:
        slogan: 文案的 slogan
        selling_points: 賣點列表
        short_copy: 短文案內文

    Returns:
        dict: 各項規格的量測值與是否達標，all_passed 為總結論
    """
    # 設計重點：工具給「事實」（len() 算出來的數字），LLM 給「判斷」——
    # 審稿的判準因此說得準、看得見，這正是迴圈方向盤該有的樣子。
    # 回傳裡「連上限一起給」：reviewer 引用的目標值永遠與 code 同步
    # （不會從 docstring 腦補），writer 才能一輪就改到位——回饋要帶目標值。
    slogan_limit, required_points, short_copy_limit = 12, 3, 50
    all_channels = {ch for p in MOCK_PROFILES.values() for ch in p["channels"]}
    full_text = slogan + "".join(selling_points) + short_copy
    channels_mentioned = sorted(ch for ch in all_channels if ch in full_text)
    slogan_len = len(slogan.strip())
    short_copy_len = len(short_copy.strip())
    result = {
        "slogan_len": slogan_len,
        "slogan_limit": slogan_limit,
        "slogan_ok": slogan_len <= slogan_limit,
        "selling_point_count": len(selling_points),
        "selling_point_required": required_points,
        "selling_points_ok": len(selling_points) == required_points,
        "short_copy_len": short_copy_len,
        "short_copy_limit": short_copy_limit,
        "short_copy_ok": short_copy_len <= short_copy_limit,
        "channels_mentioned": channels_mentioned,
        "channel_ok": len(channels_mentioned) >= 1,
    }
    result["all_passed"] = all(v for k, v in result.items() if k.endswith("_ok"))
    return {"status": "success", **result}
