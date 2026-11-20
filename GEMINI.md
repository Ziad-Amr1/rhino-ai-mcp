# Rhino AI Assistant Guidelines

## Workspace Rules
- This project (`E:\course\03_Programming_Data\AI\Projects\rhino`) is dedicated to McNeel Rhino 3D automation and AI agent integration.
- Reference projects such as `RevitAI_Studio` and `blender` can be consulted for architectural patterns, but must NEVER be modified.

## Bridge Architecture
- The live bridge is `rhino_bridge.py`, serving HTTP REST on `127.0.0.1:9888`.
- It executes safely on Rhino's main UI thread via `Rhino.RhinoApp.InvokeOnUiThread`.
- `mcp_server.py` implements FastMCP and communicates with the bridge via `rhino_client.py`.
- MCP tools use the `rhino_` prefix (`rhino_get_connection_status`, `rhino_execute_python`, `rhino_query_objects`, etc.).
