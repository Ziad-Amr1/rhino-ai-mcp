import os
with open(r"E:\course\03_Programming_Data\AI\Projects\rhino\rhino_exec_success.txt", "w") as f:
    f.write("Rhino executed python script successfully!\n")
    try:
        import Rhino
        f.write(f"Rhino Version: {Rhino.RhinoApp.Version}\n")
        f.write(f"Active Doc: {Rhino.RhinoDoc.ActiveDoc.Name}\n")
    except Exception as e:
        f.write(f"Rhino error: {e}\n")
