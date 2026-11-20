import os
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rhino_exec_success.txt")
with open(out_path, "w") as f:
    f.write("Rhino executed python script successfully!\n")
    try:
        import Rhino
        f.write(f"Rhino Version: {Rhino.RhinoApp.Version}\n")
        f.write(f"Active Doc: {Rhino.RhinoDoc.ActiveDoc.Name}\n")
    except Exception as e:
        f.write(f"Rhino error: {e}\n")
