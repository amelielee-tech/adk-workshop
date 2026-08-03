"""客群研究員：查目標客群，把結果寫進 session state。

這個檔案結構跟 trend_researcher.py 一模一樣——
請仿照它完成整個 agent（這是刻意的：驗證你真的懂了，而不是照抄）。
"""

from google.adk.agents import Agent

from ..tools import get_audience_profile

# TODO(2): 仿照 trend_researcher 建立 audience_researcher agent
# 要求：
#   - name="audience_researcher"
#   - 使用 get_audience_profile 工具
#   - instruction：根據使用者提到的市場/國家，查詢並整理目標客群輪廓
#   - output_key="audience_profile"（產出寫進 state["audience_profile"]）
audience_researcher = None
