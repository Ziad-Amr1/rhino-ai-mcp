"""Test connection to the Rhino Live Agent Bridge."""

import sys
from rhino_client import RhinoClient

def main():
    client = RhinoClient()
    print("Testing connection to Rhino Live Bridge at http://127.0.0.1:9888...")
    status = client.get_status()

    if status.get("status") == "connected":
        print("\n[SUCCESS] Connected to Rhino Live Bridge!")
        print(f"Rhino Version: {status.get('rhino_version')}")
        print(f"Document Name: {status.get('document', {}).get('name')}")
        print(f"Unit System:   {status.get('document', {}).get('model_unit_system')}")
        print(f"Active View:   {status.get('document', {}).get('active_view')}")
        counts = status.get('counts', {})
        print(f"Objects:       {counts.get('total_objects')} (Selected: {counts.get('selected_objects')})")
        print(f"Layers:        {counts.get('layers')}")
    elif status.get("status") == "mock":
        print("\n[NOTICE] Bridge is running in standalone mock mode (outside Rhino).")
    else:
        print("\n[DISCONNECTED] Rhino Live Bridge is not running.")
        print("To start the bridge:")
        print("  1. In Rhino, type into the command line:")
        print(r'     -_RunPythonScript "E:\course\03_Programming_Data\AI\Projects\rhino\rhino_bridge.py"')
        print("  2. Or open rhino_bridge.py in Rhino ScriptEditor (command: ScriptEditor) and click Run (Play).")
        if "details" in status:
            print(f"Error details: {status['details']}")

if __name__ == "__main__":
    main()
