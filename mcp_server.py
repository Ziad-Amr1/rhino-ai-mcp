"""Rhino AI Model Context Protocol (MCP) Server.

Enables AI clients (Google Antigravity, Claude Desktop, Cursor, OpenCode)
to interact directly with Rhinoceros 3D (Rhino 8 & 9) through standard MCP protocol.
"""

import os
import sys
import logging
from typing import Any, Dict, List, Optional
try:
    from mcp.server.fastmcp import FastMCP
except (ImportError, ModuleNotFoundError):
    from mcp.server.mcpserver import MCPServer as FastMCP


from rhino_client import RhinoClient, DEFAULT_BRIDGE_URL

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
        "Use rhino_create_geometry and rhino_run_command to generate models and execute Rhino commands. "
        "Use rhino_capture_viewport to take screenshots of the active viewport."
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
                "Cannot connect to Rhino Live Bridge. To connect, open Rhino and run rhino_bridge.py: "
                "In Rhino command line run: -_RunPythonScript \"<path_to>/rhino_bridge.py\" "
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
# GENERAL COMPUTATIONAL ACOUSTICS EXTENSION TOOLS
# ==============================================================================

@mcp.tool(name="rhino_calculate_rt60")
async def rhino_calculate_rt60(
    volume_m3: float,
    total_surface_area_m2: float,
    absorption_coefficients: Dict[str, float]
) -> Dict[str, Any]:
    """Calculate general room reverberation time (Sabine and Eyring equations) for any architectural space.

    Args:
        volume_m3: Total room enclosure volume in cubic meters.
        total_surface_area_m2: Total interior surface area in square meters.
        absorption_coefficients: Dictionary mapping material/surface names to absorption values (alpha 0.0 to 1.0).
    """
    import math
    if volume_m3 <= 0 or total_surface_area_m2 <= 0:
        return {"error": "Volume and surface area must be positive numbers."}

    total_sabins = sum(absorption_coefficients.values())
    mean_alpha = max(0.001, min(0.999, total_sabins / total_surface_area_m2))

    # Sabine Formula: T60 = 0.161 * V / A
    t60_sabine = (0.161 * volume_m3) / max(0.1, total_sabins)

    # Eyring Formula: T60 = -0.161 * V / (S * ln(1 - alpha_bar))
    t60_eyring = (-0.161 * volume_m3) / (total_surface_area_m2 * math.log(1.0 - mean_alpha))

    return {
        "volume_m3": volume_m3,
        "total_surface_area_m2": total_surface_area_m2,
        "total_absorption_sabins": round(total_sabins, 2),
        "mean_absorption_alpha": round(mean_alpha, 4),
        "t60_sabine_seconds": round(t60_sabine, 3),
        "t60_eyring_seconds": round(t60_eyring, 3)
    }


@mcp.tool(name="rhino_pachyderm_open_ui")
async def rhino_pachyderm_open_ui() -> Dict[str, Any]:
    """Launch the Pachyderm Acoustic Simulation interface inside Rhinoceros 3D."""
    return client.run_command("-_PachyDerm_Acoustic", echo=True)


def main():
    """Run the FastMCP server over standard input/output (stdio)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

