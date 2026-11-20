# Rhino AI Live Bridge & MCP Integration

Connect **Google Antigravity**, **Cursor**, **Claude Desktop**, and other AI agent clients directly to **Rhinoceros 3D** (Rhino 8 & 9).

---

## Architecture Overview

```
+------------------------------------+           +---------------------------------------+
|  AI Agent / Antigravity            |           |  Rhinoceros 3D (Rhino 8 / 9)          |
|                                    |           |                                       |
|  - MCP Server (mcp_server.py)      | JSON-RPC  |  - rhino_bridge.py                    |
|    stdio / FastMCP                 | HTTP REST |    Live daemon thread on port 9888    |
|    Discovers & calls tools         |<--------->|    Safely executes on Rhino UI thread |
|                                    |   :9888   |    Full RhinoCommon & rhinoscript     |
|  - Python Client (rhino_client.py) |           |                                       |
+------------------------------------+           +---------------------------------------+
```

---

## Quick Start: Starting the Bridge in Rhino

You only need to run `rhino_bridge.py` once per Rhino session (or set it to start automatically on startup).

### Option 1: One Command in Rhino (Fastest)
In Rhino's top command line, paste and hit **Enter**:
```text
-_RunPythonScript "E:\course\03_Programming_Data\AI\Projects\rhino\rhino_bridge.py"
```

### Option 2: Script Editor (Visual)
1. In Rhino, run the command: `ScriptEditor` (or `EditPythonScript`).
2. Open file: `E:\course\03_Programming_Data\AI\Projects\rhino\rhino_bridge.py`.
3. Click the green **Run (Play)** button (or press `F5`).
4. The Rhino command line will output:
   ```text
   [RhinoBridge] Rhino Agent Bridge started successfully on port 9888!
   ```

### Option 3: Auto-Start Every Time Rhino Opens (Recommended)
1. In Rhino, go to **Tools** > **Options** (or type `Options`).
2. Navigate to **General** > **Command Lists**.
3. Under **Run these commands every time Rhino starts**, add:
   ```text
   -_RunPythonScript "E:\course\03_Programming_Data\AI\Projects\rhino\rhino_bridge.py"
   ```
4. Click **OK**. The bridge will now silently launch in the background every time you open Rhino!

---

## Verifying Connection

Run the connection tester from PowerShell or terminal:
```powershell
& "E:\course\03_Programming_Data\AI\Projects\rhino\.venv\Scripts\python.exe" "E:\course\03_Programming_Data\AI\Projects\rhino\test_connection.py"
```

---

## MCP Tools Available to Antigravity

When configured in `~/.gemini/config/mcp_config.json`, the following tools are available to the AI agent:

| Tool Name | Type | Description |
| :--- | :--- | :--- |
| `rhino_get_connection_status` | Read | Checks if Rhino bridge is online and returns document/object counts |
| `rhino_get_document_info` | Read | Retrieves unit system, tolerances, active viewport, and modified status |
| `rhino_list_layers` | Read | Lists all layers with colors, visibility, and lock status |
| `rhino_query_objects` | Read | Searches objects by layer, geometry type (Brep, Curve, Mesh, SubD), or selection |
| `rhino_get_selected_objects` | Read | Returns currently selected objects in Rhino |
| `rhino_select_objects` | Write | Selects or deselects objects by GUID |
| `rhino_delete_objects` | Write | Deletes objects by GUID |
| `rhino_run_command` | Write | Executes any native Rhino command string (e.g. `_Line`, `_ExtrudeCrv`) |
| `rhino_create_geometry` | Write | Creates parametric primitives (box, cylinder, sphere, line, point) |
| `rhino_execute_python` | Write | Executes arbitrary Python code with full access to `RhinoCommon` & `rhinoscriptsyntax` |
| `rhino_capture_viewport` | Read | Takes a high-resolution screenshot of the active viewport and saves to disk |
| `rhino_pachyderm_register_materials`| Write | Synchronizes verified mosque materials into Pachyderm's native material library |
| `rhino_pachyderm_setup_mosque` | Write | Deploys acoustic layers, 3 sound sources, and 16 receivers into active Rhino model |
| `rhino_pachyderm_calculate_rt60` | Read | Computes Sabine & Eyring T60, C50, C80, and STI curves across all octave bands |
| `rhino_pachyderm_get_transducers` | Read | Retrieves coordinates and sound power specs for Imam, Khatib, Muezzin, and receivers |
| `rhino_pachyderm_open_ui` | Action | Opens Pachyderm's Geometrical Acoustics control panel inside Rhino |

---

## Pachyderm Acoustic Simulation: Muhammad Ali Mosque

Pachyderm Acoustic Simulation (v2.7.0.0) is configured to simulate the monumental prayer hall ($V = 39,840 \text{ m}^3$):

1. **Materials Registered in Pachyderm Library**:
   - `Polished Marble / Alabaster Revetment` ($\alpha = [0.01 - 0.03]$, $s=0.05$)
   - `Structural Dressed Limestone` ($\alpha = [0.02 - 0.05]$, $s=0.20$)
   - `Historic Lime / Gypsum Plaster` ($\alpha = [0.02 - 0.05]$, $s=0.15$)
   - `Wool Prayer Carpet on Underlay` ($\alpha = [0.05 - 0.65]$, $s=0.10$)
   - `Laminated Safety Glass (8mm)` ($\alpha = [0.18 - 0.02]$, $s=0.05$)
   - `Carved Hardwood` ($\alpha = [0.14 - 0.06]$, $s=0.25$)

2. **Sound Sources**:
   - `SRC_IMAM_MIHRAB` at `(0.0, 18.5, 1.5)` (74 dB)
   - `SRC_KHATIB_MINBAR` at `(2.8, 17.0, 3.2)` (76 dB)
   - `SRC_MUEZZIN_DIKKA` at `(0.0, -8.0, 4.5)` (78 dB)

3. **Receivers**:
   - 16 listening positions across prayer carpet floor ($Z = 1.20\text{ m}$) and upper women's galleries ($Z = 9.50\text{ m}$).

4. **Run Simulation**:
   ```powershell
   .\.venv\Scripts\python.exe pachyderm_simulation.py
   ```


---

## Project Structure

```
E:\course\03_Programming_Data\AI\Projects\rhino\
├── .venv/                   # Python virtual environment (FastMCP, HTTP, Pydantic)
├── rhino_bridge.py          # The live server script executed inside Rhino
├── rhino_client.py          # Python SDK & CLI client
├── mcp_server.py            # FastMCP Server communicating over stdio JSON-RPC
├── test_connection.py       # Quick test script to verify bridge connectivity
├── requirements.txt         # Package dependencies
├── GEMINI.md                # Agent instruction & operational context
└── README.md                # Documentation & setup guide
```
