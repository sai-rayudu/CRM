# tools/mcp.py

tools_registry = []

def tool(func):
    tools_registry.append(func)
    return func
