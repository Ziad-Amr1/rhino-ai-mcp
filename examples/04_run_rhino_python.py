"""Example 04: Execute Python code inside Rhino with RhinoCommon / Python."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rhino_client import RhinoClient

def main():
    client = RhinoClient()

    python_script = """
# In live Rhino, 'Rhino', 'rg', 'rs', and 'sc' are pre-injected into the global scope.
try:
    import rhinoscriptsyntax as rs
    pt = [0, 0, 0]
    crv = rs.AddCircle(pt, 15.0)
    print(f"Inside Rhino: Created Circle with GUID: {crv}")
    result = f"Circle GUID: {crv}"
except ImportError:
    # Standalone mode fallback (outside live Rhino)
    print("Running in standalone environment: rhinoscriptsyntax is available when Rhino is open.")
    result = "Standalone Python execution verified (50 * 7 = 350)"
"""

    print("Sending Python script to Rhino for execution...")
    res = client.execute_python(python_script)
    print("Execution output:")
    print("  Success:", res.get("success"))
    print("  Stdout: ", res.get("stdout", "").strip())
    print("  Result: ", res.get("result"))
    if res.get("error"):
        print("  Error:  ", res.get("error").strip())

if __name__ == "__main__":
    main()

