# Rhino AI Model Context Protocol (MCP) Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Rhino: 8 & 9](https://img.shields.io/badge/Rhinoceros-8%20%7C%209-red.svg)](https://www.rhino3d.com/)
[![MCP Compliant](https://img.shields.io/badge/MCP-1.0-green.svg)](https://modelcontextprotocol.io/)

A general-purpose **Model Context Protocol (MCP)** server and live bidirectional bridge for **McNeel Rhinoceros 3D** (Rhino 8 & 9).

Connect AI agent workflows—including **Google Antigravity**, **Claude Desktop**, **Cursor**, **VS Code**, and custom LLM orchestrators—directly to Rhino's geometry engine, active document state, and command pipeline.

---

## Architecture

```
+-------------------------------------------------------+
|  AI Agent / LLM Client                                |
|  (Google Antigravity, Claude Desktop, Cursor, etc.)  |
+-------------------------------------------------------+
                           |
                     stdio | (JSON-RPC 2.0 / MCP Protocol)
                           v
+-------------------------------------------------------+
|  FastMCP Server (mcp_server.py)                       |
|  - Tool discovery & schema generation                 |
|  - Parameter validation (Pydantic)                    |
|  - Client proxy (rhino_client.py)                     |
+-------------------------------------------------------+
                           |
                      HTTP | REST API (http://127.0.0.1:9888)
                           v
+-------------------------------------------------------+
|  Rhino Live Agent Bridge (rhino_bridge.py)            |
|  - Embedded daemon running inside Rhino 8 / 9         |
|  - Dispatches tasks to Rhino Main UI Thread           |
|  - Full access to RhinoCommon, rs, and RhinoDoc       |
|  - Headless standalone fallback mode (via rhino3dm)   |
+-------------------------------------------------------+
```

---

## Key Features

- **Live Bidirectional Bridge:** Control Rhino in real time via an embedded daemon thread on port `9888`.
- **UI Thread Safety:** All geometry and document operations execute safely on Rhino's main UI thread.
- **Document & Layer Inspection:** Query model units, bounding boxes, viewports, layer hierarchies, colors, and visibility.
- **Object Filtering & Querying:** Search and filter objects by layer, geometry type (`Brep`, `Curve`, `Mesh`, `SubD`, `Point`), or selection state.
- **Parametric Geometry Generation:** Create parametric primitives (`box`, `cylinder`, `sphere`, `line`, `point`) with a single tool call.
- **Arbitrary Python Execution:** Execute arbitrary Python code inside Rhino with pre-injected `Rhino`, `rg` (`Rhino.Geometry`), `rs` (`rhinoscriptsyntax`), and `doc` (`RhinoDoc.ActiveDoc`).
- **Rhino Command Execution:** Execute any native Rhino command string (e.g., `_Circle`, `_ExtrudeCrv`, `_ZoomAll`).
- **Viewport Screenshot Capture:** Capture high-resolution viewport screenshots and save them directly to disk.
- **Acoustic RT60 Calculator:** Built-in Sabine and Eyring reverberation time calculations for architectural enclosures.
- **Standalone Emulation Mode:** Operates outside Rhino via `rhino3dm` for automated testing, CI/CD, and offline development.

---

## Quick Start

### 1. Installation

Clone the repository and install the dependencies in your Python environment (Python 3.9+ recommended):

```bash
git clone https://github.com/Ziad-Amr1/rhino-ai-mcp.git
cd rhino-ai-mcp
pip install -e .
```

Or install using `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Launch the Bridge Inside Rhino

To connect to a live Rhino session, run `rhino_bridge.py` inside Rhino:

#### Option A: Rhino Command Line (Fastest)
In Rhino's command bar, run:
```text
-_RunPythonScript "C:\path\to\rhino-ai-mcp\rhino_bridge.py"
```

#### Option B: Rhino ScriptEditor
1. Type `ScriptEditor` (Rhino 8+) or `EditPythonScript`.
2. Open `rhino_bridge.py`.
3. Press **Run** (`F5`).

#### Option C: Auto-Start on Rhino Launch (Recommended)
1. In Rhino, open **Options** (`Tools > Options` or type `Options`).
2. Go to **General** > **Command Lists**.
3. Under **Run these commands every time Rhino starts**, add:
   ```text
   -_RunPythonScript "C:\path\to\rhino-ai-mcp\rhino_bridge.py"
   ```
4. Click **OK**. The bridge will start automatically whenever Rhino opens.

### 3. Verify Connection

Check the connection from your terminal:

```bash
python test_connection.py
```

Expected output:
```text
Testing connection to Rhino Live Bridge at http://127.0.0.1:9888...

[SUCCESS] Connected to Rhino Live Bridge!
Rhino Version: Rhino 8.x / 9.x
Document Name: Untitled.3dm
Unit System:   Millimeters
Active View:   Perspective
Objects:       0 (Selected: 0)
Layers:        1
```

---

## AI Client Configuration

### Google Antigravity / Gemini CLI

Add the server to your `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "rhino": {
      "command": "python",
      "args": [
        "C:/path/to/rhino-ai-mcp/mcp_server.py"
      ],
      "env": {
        "RHINO_BRIDGE_URL": "http://127.0.0.1:9888"
      }
    }
  }
}
```

### Claude Desktop

Add to `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "rhino": {
      "command": "python",
      "args": [
        "C:/path/to/rhino-ai-mcp/mcp_server.py"
      ],
      "env": {
        "RHINO_BRIDGE_URL": "http://127.0.0.1:9888"
      }
    }
  }
}
```

### Cursor

Add to your project's `.cursor/mcp.json` or global Cursor settings:

```json
{
  "mcpServers": {
    "rhino": {
      "command": "python",
      "args": [
        "${workspaceFolder}/mcp_server.py"
      ],
      "env": {
        "RHINO_BRIDGE_URL": "http://127.0.0.1:9888"
      }
    }
  }
}
```

---

## MCP Tools Reference

| Tool Name | Type | Description | Key Parameters |
| :--- | :---: | :--- | :--- |
| `rhino_get_connection_status` | Read | Checks if Rhino bridge is online and returns document overview | — |
| `rhino_get_document_info` | Read | Retrieves unit system, tolerances, and active viewport | — |
| `rhino_list_layers` | Read | Lists all layers with colors, visibility, and lock status | — |
| `rhino_query_objects` | Read | Searches objects by layer, geometry type, or selection | `layer`, `geometry_type`, `selected_only`, `limit` |
| `rhino_get_selected_objects` | Read | Returns GUIDs and metadata of currently selected objects | — |
| `rhino_select_objects` | Write | Selects or deselects objects by GUID | `guids`, `deselect_others` |
| `rhino_delete_objects` | Write | Deletes objects by GUID | `guids` |
| `rhino_create_geometry` | Write | Creates parametric primitives (`box`, `cylinder`, `sphere`, `line`, `point`) | `geometry_type`, `origin`, `size`, `radius`, `height` |
| `rhino_run_command` | Write | Executes any native Rhino command string | `command`, `echo` |
| `rhino_execute_python` | Write | Runs Python script in Rhino with access to `RhinoCommon` & `rs` | `code` |
| `rhino_capture_viewport` | Read | Captures a high-resolution screenshot of active viewport | `file_path`, `width`, `height` |
| `rhino_calculate_rt60` | Read | Computes room Sabine and Eyring reverberation time | `volume_m3`, `total_surface_area_m2`, `absorption_coefficients` |
| `rhino_pachyderm_open_ui` | Action | Opens Pachyderm Acoustic Simulation UI panel | — |

---

## Python SDK Examples

The toolkit includes a lightweight Python client (`rhino_client.py`) that can be used directly in Python scripts:

```python
from rhino_client import RhinoClient

client = RhinoClient()

# Check bridge status
status = client.get_status()
print(f"Connected: {status['status']}")

# Create a box
box = client.create_geometry("box", origin=[0, 0, 0], size=[20, 10, 5])
print("Created Box GUID:", box["created_ids"][0])

# Execute RhinoCommon code
res = client.execute_python("""
import rhinoscriptsyntax as rs
circle_id = rs.AddCircle([0, 0, 0], 25.0)
result = f"Circle GUID: {circle_id}"
""")
print(res["result"])
```

Explore runnable examples in the [`examples/`](./examples/) folder:
- [`01_check_connection.py`](./examples/01_check_connection.py) — Connect and inspect document properties.
- [`02_create_geometry.py`](./examples/02_create_geometry.py) — Create parametric boxes, cylinders, and spheres.
- [`03_query_objects_and_layers.py`](./examples/03_query_objects_and_layers.py) — Query and filter layers and objects.
- [`04_run_rhino_python.py`](./examples/04_run_rhino_python.py) — Execute Python code dynamically inside Rhino.

---

## Testing & Verification

Run the comprehensive end-to-end test suite:

```bash
python test_backend.py
```

The test suite validates:
1. REST bridge connection and status checks.
2. Document metadata extraction.
3. Layer listing and hierarchy queries.
4. Object queries with filtering.
5. Parametric geometry creation and GUID tracking.
6. Object selection and retrieval.
7. Dynamic Python execution and output capture.
8. Rhino command line execution.
9. Viewport image capture.
10. Object deletion and cleanup.
11. FastMCP server async tool bindings.

---

## Repository Structure

```text
rhino-ai-mcp/
├── .gitignore               # Excludes virtual environments, caches, and local archives
├── LICENSE                  # MIT License
├── README.md                # Project documentation and setup guide
├── pyproject.toml           # Standard Python packaging configuration
├── requirements.txt         # Package dependencies
├── mcp_server.py            # FastMCP Server (stdio JSON-RPC for AI clients)
├── rhino_bridge.py          # Live bridge daemon (runs inside Rhino 8 / 9)
├── rhino_client.py          # Python SDK & CLI client
├── run_backend.py           # Standalone headless runner
├── test_backend.py          # Comprehensive test suite (13/13 passing)
├── test_connection.py       # Quick bridge connection check
├── test_rhino_exec.py       # Python execution verification script
├── examples/                # Ready-to-run Python examples
│   ├── 01_check_connection.py
│   ├── 02_create_geometry.py
│   ├── 03_query_objects_and_layers.py
│   └── 04_run_rhino_python.py
└── mcp_schemas/             # Tool definitions and documentation
```

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for improvements, bug fixes, or new MCP tool integrations.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for details.

Copyright &copy; 2026 Ziad Amr.
