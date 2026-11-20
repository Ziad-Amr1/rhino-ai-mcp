"""Rhino Live Bridge Client

Python SDK and CLI tool to interact with Rhino 8/9 through the Rhino Live Agent Bridge.
"""

import sys
import json
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

DEFAULT_BRIDGE_URL = "http://127.0.0.1:9888"


class RhinoClient:
    """Client for Rhino Live Agent Bridge."""

    def __init__(self, bridge_url: str = DEFAULT_BRIDGE_URL, timeout: float = 30.0):
        self.bridge_url = bridge_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.bridge_url}{path}"
        if params:
            query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            if query:
                url = f"{url}?{query}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": f"Cannot connect to Rhino Bridge at {self.bridge_url}. Is Rhino running with rhino_bridge.py active?",
                "details": str(e)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.bridge_url}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": f"Cannot connect to Rhino Bridge at {self.bridge_url}. Is Rhino running with rhino_bridge.py active?",
                "details": str(e)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def ping(self) -> Dict[str, Any]:
        """Check connection status and active document overview."""
        return self._get("/ping")

    def get_status(self) -> Dict[str, Any]:
        """Get detailed connection and document status."""
        return self._get("/status")

    def get_document_info(self) -> Dict[str, Any]:
        """Get active document metadata, units, and tolerances."""
        return self._get("/document")

    def list_layers(self) -> Dict[str, Any]:
        """List all layers in the active Rhino document."""
        return self._get("/layers")

    def query_objects(
        self,
        layer: Optional[str] = None,
        type: Optional[str] = None,
        selected_only: bool = False,
        limit: int = 500
    ) -> Dict[str, Any]:
        """Query objects in the document with optional filters."""
        import urllib.parse
        params = {
            "layer": layer,
            "type": type,
            "selected_only": "true" if selected_only else "false",
            "limit": str(limit)
        }
        return self._get("/objects", params)

    def get_selected_objects(self) -> Dict[str, Any]:
        """Get currently selected objects in Rhino."""
        return self._get("/selected")

    def select_objects(self, guids: List[str], deselect_others: bool = True) -> Dict[str, Any]:
        """Select objects in Rhino by GUID."""
        return self._post("/select", {"guids": guids, "deselect_others": deselect_others})

    def delete_objects(self, guids: List[str]) -> Dict[str, Any]:
        """Delete objects in Rhino by GUID."""
        return self._post("/delete", {"guids": guids})

    def run_command(self, command: str, echo: bool = False) -> Dict[str, Any]:
        """Execute a Rhino command line string (e.g. '_Circle 0,0,0 20')."""
        return self._post("/command", {"command": command, "echo": echo})

    def execute_python(self, code: str) -> Dict[str, Any]:
        """Execute Python code in Rhino with access to RhinoCommon and rhinoscriptsyntax."""
        return self._post("/execute", {"code": code})

    def create_geometry(self, geom_type: str, **params) -> Dict[str, Any]:
        """Create parametric primitive geometry (point, line, box, sphere, cylinder)."""
        return self._post("/geometry/create", {"type": geom_type, "params": params})

    def capture_viewport(
        self,
        file_path: Optional[str] = None,
        width: int = 1920,
        height: int = 1080
    ) -> Dict[str, Any]:
        """Capture the active Rhino viewport to an image file."""
        return self._post("/view/capture", {
            "file_path": file_path,
            "width": width,
            "height": height
        })


def main():
    """Command-line interface for Rhino Live Bridge."""
    client = RhinoClient()
    if len(sys.argv) < 2:
        print("Usage: rhino-cli [status|layers|objects|selected|run <file.py>|cmd <command>]")
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd in ("status", "ping"):
        print(json.dumps(client.get_status(), indent=2))
    elif cmd == "layers":
        print(json.dumps(client.list_layers(), indent=2))
    elif cmd == "objects":
        print(json.dumps(client.query_objects(), indent=2))
    elif cmd == "selected":
        print(json.dumps(client.get_selected_objects(), indent=2))
    elif cmd == "cmd" and len(sys.argv) > 2:
        command_str = " ".join(sys.argv[2:])
        print(json.dumps(client.run_command(command_str), indent=2))
    elif cmd == "run" and len(sys.argv) > 2:
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            script_code = f.read()
        print(json.dumps(client.execute_python(script_code), indent=2))
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()

