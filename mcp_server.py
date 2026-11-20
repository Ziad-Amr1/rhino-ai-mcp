"""Rhino AI Model Context Protocol (MCP) Server.

Enables AI clients (Google Antigravity, OpenCode, Claude Desktop, Cursor)
to interact directly with Rhinoceros 3D (Rhino 8 & 9) through standard MCP protocol.
"""

import os
import sys
import logging
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

from rhino_client import RhinoClient, DEFAULT_BRIDGE_URL
import pachyderm_materials
import pachyderm_simulation
from mosque_acoustic_data import ACOUSTIC_SOURCES, ACOUSTIC_RECEIVERS, ACOUSTIC_MATERIALS

# Configure logging to stderr so stdout is strictly preserved for JSON-RPC stdio
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Rhino.MCP] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("Rhino.MCP.Server")

bridge_url = os.environ.get("RHINO_BRIDGE_URL", DEFAULT_BRIDGE_URL)
client = RhinoClient(bridge_url=bridge_url)

mcp = FastMCP(
    name="Rhino 3D",
    instructions=(
        "Rhino 3D MCP server connects AI clients to McNeel Rhinoceros 3D (Rhino 8 & 9). "
        "Use read-only tools (rhino_get_connection_status, rhino_get_document_info, rhino_list_layers, "
        "rhino_query_objects, rhino_get_selected_objects) to inspect models, layers, and objects. "
        "Use rhino_execute_python to run RhinoCommon or rhinoscriptsyntax code. "
        "Use rhino_create_geometry and rhino_run_command to generate models and execute Rhino commands."
    )
)


@mcp.tool(name="rhino_get_connection_status")
async def rhino_get_connection_status() -> Dict[str, Any]:
    """Check if the Rhino live bridge is active and view active document status and object counts."""
    res = client.get_status()
    if res.get("status") == "connected":
        return res
    if "error" in res:
        return {
            "status": "disconnected",
            "message": (
                "Cannot connect to Rhino Live Bridge. To connect, open Rhino and run the bridge script: "
                "in Rhino command line run: -_RunPythonScript \"E:\\course\\03_Programming_Data\\AI\\Projects\\rhino\\rhino_bridge.py\" "
                "or open rhino_bridge.py in Rhino's ScriptEditor and press Run."
            ),
            "details": res.get("error")
        }
    return res


@mcp.tool(name="rhino_get_document_info")
async def rhino_get_document_info() -> Dict[str, Any]:
    """Get active Rhino document information, including unit system, absolute tolerance, angle tolerance, and active view."""
    return client.get_document_info()


@mcp.tool(name="rhino_list_layers")
async def rhino_list_layers() -> Dict[str, Any]:
    """List all layers in the active Rhino document with their names, full paths, colors, visibility, and lock states."""
    return client.list_layers()


@mcp.tool(name="rhino_query_objects")
async def rhino_query_objects(
    layer: Optional[str] = None,
    geometry_type: Optional[str] = None,
    selected_only: bool = False,
    limit: int = 500
) -> Dict[str, Any]:
    """Query objects in active Rhino document by layer name, geometry type (Brep, Curve, Mesh, Point, SubD), or selection."""
    return client.query_objects(layer=layer, type=geometry_type, selected_only=selected_only, limit=limit)


@mcp.tool(name="rhino_get_selected_objects")
async def rhino_get_selected_objects() -> Dict[str, Any]:
    """Get all currently selected objects in Rhino with their GUIDs, types, layers, and bounding boxes."""
    return client.get_selected_objects()


@mcp.tool(name="rhino_select_objects")
async def rhino_select_objects(
    guids: List[str],
    deselect_others: bool = True
) -> Dict[str, Any]:
    """Select or deselect objects in Rhino by their GUIDs."""
    return client.select_objects(guids=guids, deselect_others=deselect_others)


@mcp.tool(name="rhino_delete_objects")
async def rhino_delete_objects(guids: List[str]) -> Dict[str, Any]:
    """Delete objects in active Rhino document by their GUIDs."""
    return client.delete_objects(guids=guids)


@mcp.tool(name="rhino_run_command")
async def rhino_run_command(command: str, echo: bool = False) -> Dict[str, Any]:
    """Execute a native Rhino command line string (e.g. '_Circle 0,0,0 25', '_ExtrudeCrv', '_ZoomAll')."""
    return client.run_command(command=command, echo=echo)


@mcp.tool(name="rhino_execute_python")
async def rhino_execute_python(code: str) -> Dict[str, Any]:
    """Execute arbitrary Python code inside Rhino with full access to rhinoscriptsyntax (as rs), RhinoCommon (as Rhino/rg), and active document (doc). Returns stdout, stderr, and result."""
    return client.execute_python(code=code)


@mcp.tool(name="rhino_create_geometry")
async def rhino_create_geometry(
    geometry_type: str,
    origin: Optional[List[float]] = None,
    size: Optional[List[float]] = None,
    radius: Optional[float] = None,
    height: Optional[float] = None,
    start_point: Optional[List[float]] = None,
    end_point: Optional[List[float]] = None
) -> Dict[str, Any]:
    """Create parametric primitive geometry in Rhino (box, sphere, cylinder, line, point).

    Args:
        geometry_type: One of 'box', 'sphere', 'cylinder', 'line', 'point'.
        origin: [x, y, z] origin or center coordinates.
        size: [dx, dy, dz] dimensions for box.
        radius: Radius for sphere or cylinder.
        height: Height for cylinder.
        start_point: [x, y, z] start coordinates for line.
        end_point: [x, y, z] end coordinates for line.
    """
    params = {}
    if origin is not None:
        params["origin"] = origin
        params["center"] = origin
        params["base"] = origin
        params["coords"] = origin
    if size is not None:
        params["size"] = size
    if radius is not None:
        params["radius"] = radius
    if height is not None:
        params["height"] = height
    if start_point is not None:
        params["start"] = start_point
    if end_point is not None:
        params["end"] = end_point

    return client.create_geometry(geom_type=geometry_type.lower(), **params)


@mcp.tool(name="rhino_capture_viewport")
async def rhino_capture_viewport(
    file_path: Optional[str] = None,
    width: int = 1920,
    height: int = 1080
) -> Dict[str, Any]:
    """Capture a screenshot of the active Rhino viewport and save it as an image file on disk."""
    return client.capture_viewport(file_path=file_path, width=width, height=height)


# ==============================================================================
# PACHYDERM ACOUSTIC SIMULATION TOOLS (MUHAMMAD ALI MOSQUE)
# ==============================================================================

@mcp.tool(name="rhino_pachyderm_register_materials")
async def rhino_pachyderm_register_materials() -> Dict[str, Any]:
    """Register verified acoustic materials for the Muhammad Ali Mosque in Pachyderm's native material library."""
    success = pachyderm_materials.register_mosque_materials_in_pachyderm()
    return {
        "success": success,
        "registered_materials": list(ACOUSTIC_MATERIALS.keys()),
        "library_path": pachyderm_materials.PACH_LIB_PATH
    }


@mcp.tool(name="rhino_pachyderm_calculate_rt60")
async def rhino_pachyderm_calculate_rt60(
    occupied: bool = False,
    volume_m3: Optional[float] = None
) -> Dict[str, Any]:
    """Calculate analytical Sabine & Eyring Reverberation Time (T60), C50, C80, and STI for the Muhammad Ali Mosque across all octave bands."""
    return pachyderm_simulation.calculate_analytical_acoustics(volume_m3=volume_m3, occupied=occupied)


@mcp.tool(name="rhino_pachyderm_get_transducers")
async def rhino_pachyderm_get_transducers() -> Dict[str, Any]:
    """Get list of acoustic sound sources (Imam, Khatib, Muezzin) and 16 receivers across the mosque prayer hall and galleries."""
    return {
        "sources": ACOUSTIC_SOURCES,
        "receivers": ACOUSTIC_RECEIVERS,
        "counts": {
            "sources": len(ACOUSTIC_SOURCES),
            "receivers": len(ACOUSTIC_RECEIVERS)
        }
    }


@mcp.tool(name="rhino_pachyderm_setup_mosque")
async def rhino_pachyderm_setup_mosque() -> Dict[str, Any]:
    """Deploy acoustic layers, sound sources, and receivers for the Muhammad Ali Mosque in the active Rhino model via live bridge."""
    return pachyderm_simulation.deploy_mosque_acoustics_via_bridge(client=client)


@mcp.tool(name="rhino_pachyderm_open_ui")
async def rhino_pachyderm_open_ui() -> Dict[str, Any]:
    """Launch the Pachyderm Acoustic Simulation interface inside Rhinoceros 3D."""
    return client.run_command("-_PachyDerm_Acoustic", echo=True)



if __name__ == "__main__":
    # Run the FastMCP server over standard input/output
    mcp.run(transport="stdio")
