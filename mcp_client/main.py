# mcp_client/main.py
import os
from agent import Agent

llm_api_key = "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"
base = os.path.dirname(__file__)   # → mcp_client/
tools_json = os.path.abspath(os.path.join(base, '../mcp_server/tools.json'))

agent = Agent(tools_json)

# ✅ Directly run both tools, no prompt matching needed
agent = Agent(tools_json)

agent.run(llm_api_key)

