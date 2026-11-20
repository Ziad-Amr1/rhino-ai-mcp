# Rhino AI Model Context Protocol (MCP) Toolkit v1.0.0

Initial public release of the **Rhino AI MCP Toolkit**, connecting modern AI agent workflows (Google Antigravity, Claude Desktop, Cursor, OpenCode, VS Code) directly to McNeel Rhinoceros 3D (Rhino 8 & 9).

---

### What's Included in v1.0.0

#### 1. Live Bidirectional Bridge (`rhino_bridge.py`)
- Embedded HTTP REST daemon running on port `9888` inside Rhinoceros 3D.
- Thread-safe dispatch to the Rhino main UI thread via `RhinoApp.InvokeOnUiThread`.
- Full access to `RhinoCommon`, `rhinoscriptsyntax` (`rs`), and `RhinoDoc.ActiveDoc`.
- Standalone emulation mode with `rhino3dm` support for headless CI/CD, testing, and offline development.

#### 2. FastMCP Server (`mcp_server.py`)
- Standard JSON-RPC stdio transport for direct LLM agent integration.
- Dual compatibility with both `mcp` 1.x (`FastMCP`) and `mcp` 2.x (`MCPServer`).
- 13 comprehensive tools covering:
  - **Inspection:** `rhino_get_connection_status`, `rhino_get_document_info`, `rhino_list_layers`, `rhino_query_objects`, `rhino_get_selected_objects`
  - **Modification:** `rhino_select_objects`, `rhino_delete_objects`, `rhino_create_geometry`
  - **Execution:** `rhino_run_command`, `rhino_execute_python`
  - **Capture:** `rhino_capture_viewport`
  - **Acoustics & Simulation:** `rhino_calculate_rt60`, `rhino_pachyderm_open_ui`

#### 3. Python SDK & CLI (`rhino_client.py`)
- Lightweight `RhinoClient` for Python automation scripts.
- CLI entry points: `rhino-cli` and `rhino-mcp`.

#### 4. Examples & Verification
- 4 ready-to-run Python examples covering connection, geometry creation, object queries, and Python execution.
- Comprehensive end-to-end test suite (`test_backend.py`) with 100% pass rate (13/13).

---

### Installation

```bash
git clone https://github.com/Ziad-Amr1/rhino-ai-mcp.git
cd rhino-ai-mcp
pip install -e .
```

Or install the attached pre-built wheel directly:
```bash
pip install rhino_ai_mcp-1.0.0-py3-none-any.whl
```
