# mcp_client/agent.py

import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../tools')))
from my_tools import mcp

class Agent:
    def __init__(self, mcp_server):
        with open(mcp_server, 'r') as f:
            data = json.load(f)
        self.tools = data['tools']

    def run(self, llm_api_key):
        print("🤖 Agent started")

        for t in mcp.tools_registry:
            if t.__name__ == "send_mail":
                t(llm_api_key)

        for t in mcp.tools_registry:
            if t.__name__ == "reply_mail":
                t(llm_api_key)

        print("🤖 Agent finished")
