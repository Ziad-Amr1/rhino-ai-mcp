"""Example 01: Check connection and query active document overview."""

import sys
import os
import json

# Add parent directory to path so rhino_client can be imported directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rhino_client import RhinoClient

def main():
    client = RhinoClient()
    print("Checking connection to Rhino Live Bridge...")
    status = client.get_status()

    if status.get("status") == "connected":
        print("[CONNECTED] Successfully reached Rhino Live Bridge.")
        doc = status.get("document", {})
        print(f"  Document Name: {doc.get('name')}")
        print(f"  Unit System:   {doc.get('model_unit_system')}")
        print(f"  Active View:   {doc.get('active_view')}")
        counts = status.get("counts", {})
        print(f"  Total Objects: {counts.get('total_objects')}")
        print(f"  Total Layers:  {counts.get('layers')}")
    else:
        print("[DISCONNECTED] Could not connect to Rhino bridge.")
        print(json.dumps(status, indent=2))

if __name__ == "__main__":
    main()
