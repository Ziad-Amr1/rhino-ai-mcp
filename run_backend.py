"""Dedicated entrypoint for running Rhino AI Bridge Backend on Windows."""

import sys
import os

# Ensure current directory is in sys.path
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import rhino_bridge

def main():
    print("=" * 65)
    print("      RHINO AI LIVE BRIDGE & BACKEND SERVER")
    print("=" * 65)
    print(f"Project Path:     {PROJECT_DIR}")
    print(f"Host / Port:      http://{rhino_bridge.HOST}:{rhino_bridge.PORT}")
    print(f"Environment:      {'Inside Rhino' if rhino_bridge.IN_RHINO else 'Terminal Standalone (Simulated / Mock mode)'}")
    print(f"Endpoints Ready:  /status, /document, /layers, /objects, /selected,")
    print(f"                  /execute, /command, /geometry/create, /view/capture")
    print("=" * 65)
    print("Press Ctrl+C to stop server.\n")

    try:
        rhino_bridge.start_server()
    except KeyboardInterrupt:
        print("\n[RhinoBackend] Server shutting down cleanly...")
        if globals().get("RHINO_BRIDGE_SERVER"):
            globals()["RHINO_BRIDGE_SERVER"].shutdown()
        print("[RhinoBackend] Stopped.")

if __name__ == "__main__":
    main()
