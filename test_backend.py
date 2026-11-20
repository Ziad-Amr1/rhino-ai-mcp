"""Comprehensive End-to-End Test Suite for Rhino AI Backend & MCP Server."""

import sys
import os
import time
import json
import asyncio
import subprocess

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from rhino_client import RhinoClient
import mcp_server


def run_tests():
    print("=" * 70)
    print("      RUNNING RHINO AI BACKEND & MCP INTEGRATION TESTS")
    print("=" * 70)

    client = RhinoClient(bridge_url="http://127.0.0.1:9888")
    server_process = None

    # Step 1: Check if server is already running, otherwise spawn one
    ping_res = client.ping()
    if "error" in ping_res:
        print("[INFO] Server not detected on port 9888. Spawning background server...")
        python_exe = sys.executable
        server_process = subprocess.Popen(
            [python_exe, os.path.join(PROJECT_DIR, "run_backend.py")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Give server time to bind
        time.sleep(2)
        ping_res = client.ping()

    if "error" in ping_res:
        print(f"[FAIL] Could not connect to backend server: {ping_res['error']}")
        if server_process:
            server_process.terminate()
        return False

    print(f"[PASS] 1. Backend Server Ping / Status")
    print(f"       Status:        {ping_res.get('status')}")
    print(f"       Rhino Version: {ping_res.get('rhino_version')}")
    print(f"       Active Model:  {ping_res.get('document', {}).get('name')}")

    passed = 0
    total = 0

    try:
        # Step 2: Document Info
        total += 1
        doc_info = client.get_document_info()
        assert doc_info.get("status") == "connected"
        doc_data = doc_info.get("document", {})
        print(f"[PASS] 2. Document Info -> Units: {doc_data.get('model_unit_system')}, View: {doc_data.get('active_view')}")
        passed += 1

        # Step 3: Layer Listing
        total += 1
        layers_res = client.list_layers()
        layers = layers_res.get("layers", [])
        assert len(layers) > 0, "No layers returned"
        print(f"[PASS] 3. List Layers -> Found {len(layers)} layers: {[l['name'] for l in layers]}")
        passed += 1

        # Step 4: Query Objects
        total += 1
        objs_res = client.query_objects()
        objs = objs_res.get("objects", [])
        assert len(objs) > 0, "No objects returned"
        print(f"[PASS] 4. Query Objects -> Found {len(objs)} objects: {[o['name'] for o in objs]}")
        passed += 1

        # Step 5: Create Geometry
        total += 1
        geom_res = client.create_geometry("box", origin=[10, 10, 0], size=[20, 20, 5])
        assert geom_res.get("success") is True, f"Geometry creation failed: {geom_res}"
        created_id = geom_res.get("created_ids", [None])[0]
        print(f"[PASS] 5. Create Geometry -> Created Box GUID: {created_id}")
        passed += 1

        # Step 6: Object Selection
        total += 1
        sel_res = client.select_objects([created_id])
        assert sel_res.get("success") is True
        print(f"[PASS] 6. Select Object -> Selected {sel_res.get('selected_count')} object(s)")
        passed += 1

        # Step 7: Get Selected Objects
        total += 1
        selected_objs = client.get_selected_objects()
        assert len(selected_objs.get("selected_objects", [])) > 0
        print(f"[PASS] 7. Get Selected -> Current selected: {[o['name'] for o in selected_objs['selected_objects']]}")
        passed += 1

        # Step 8: Execute Python code
        total += 1
        py_code = """
x = 100
y = 250
result = x + y
print(f"Calculated sum inside Rhino Python: {result}")
"""
        py_res = client.execute_python(py_code)
        assert py_res.get("success") is True, f"Python execution failed: {py_res}"
        assert "350" in py_res.get("stdout", "") or py_res.get("result") == "350"
        print(f"[PASS] 8. Execute Python -> Result: {py_res.get('result')}, Stdout: {py_res.get('stdout').strip()}")
        passed += 1

        # Step 9: Run Rhino Command
        total += 1
        cmd_res = client.run_command("_Circle 0,0,0 50")
        assert cmd_res.get("success") is True
        print(f"[PASS] 9. Run Command -> Command executed: {cmd_res.get('command')}")
        passed += 1

        # Step 10: Viewport Capture
        total += 1
        cap_res = client.capture_viewport(width=800, height=600)
        assert cap_res.get("success") is True
        print(f"[PASS] 10. Viewport Capture -> Captured screenshot to: {cap_res.get('file_path')}")
        passed += 1

        # Step 11: Delete Objects
        total += 1
        del_res = client.delete_objects([created_id])
        assert del_res.get("success") is True
        print(f"[PASS] 11. Delete Objects -> Deleted count: {del_res.get('deleted_count')}")
        passed += 1

        # Step 12: Test FastMCP Server Tools directly
        print("\n--- Testing FastMCP Server async tool bindings ---")
        total += 1
        mcp_status = asyncio.run(mcp_server.rhino_get_connection_status())
        assert mcp_status.get("status") == "connected"
        print(f"[PASS] 12. MCP Tool: rhino_get_connection_status -> OK")
        passed += 1

        total += 1
        mcp_layers = asyncio.run(mcp_server.rhino_list_layers())
        assert "layers" in mcp_layers
        print(f"[PASS] 13. MCP Tool: rhino_list_layers -> {len(mcp_layers['layers'])} layers found")
        passed += 1

        total += 1
        mcp_py = asyncio.run(mcp_server.rhino_execute_python("result = 7 * 8\nprint('MCP Python test passed')"))
        assert mcp_py.get("result") == "56"
        print(f"[PASS] 14. MCP Tool: rhino_execute_python -> Result: 56, Output: {mcp_py.get('stdout').strip()}")
        passed += 1

        print("=" * 70)
        print(f"      ALL TESTS COMPLETED: {passed}/{total} PASSED (100% SUCCESS)")
        print("=" * 70)
        return True

    except Exception as ex:
        import traceback
        print(f"\n[ERROR during tests]: {ex}")
        traceback.print_exc()
        return False
    finally:
        if server_process:
            print("[INFO] Shutting down spawned test server process...")
            server_process.terminate()
            server_process.wait()
            print("[INFO] Server stopped.")


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
