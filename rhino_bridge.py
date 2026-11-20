"""Rhino Live Agent Bridge (Rhino 8 & 9 Compatible)

Runs inside Rhino (via Script Editor, RunPythonScript, or Rhino startup)
to expose an HTTP REST / JSON-RPC interface for external AI agents, Antigravity,
and MCP tools.

Default port: 9888
"""

import sys
import os
import json
import threading
import traceback
import time

try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from urlparse import urlparse, parse_qs

try:
    import queue
except ImportError:
    import Queue as queue

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

# Rhino namespaces (available when running inside Rhino)
try:
    import Rhino
    import Rhino.Geometry as rg
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
    IN_RHINO = True
except ImportError:
    IN_RHINO = False
    Rhino = None
    rg = None
    rs = None
    sc = None

PORT = 9888
HOST = "127.0.0.1"

# Global state to prevent duplicate server instances
if "RHINO_BRIDGE_SERVER" in globals() and globals()["RHINO_BRIDGE_SERVER"]:
    try:
        globals()["RHINO_BRIDGE_SERVER"].shutdown()
        globals()["RHINO_BRIDGE_SERVER"].server_close()
        print("[RhinoBridge] Closed previous server instance.")
    except Exception as e:
        print("[RhinoBridge] Error closing previous server: {}".format(e))

SERVER_RUNNING = True


def run_on_ui_thread(callable_func, timeout=30.0):
    """Safely executes a function on Rhino's main UI thread."""
    if not IN_RHINO:
        return callable_func()

    result_box = {"value": None, "error": None}
    done_event = threading.Event()

    def action_wrapper():
        try:
            result_box["value"] = callable_func()
        except Exception as exc:
            result_box["error"] = traceback.format_exc()
        finally:
            done_event.set()

    try:
        import System
        Rhino.RhinoApp.InvokeOnUiThread(System.Action(action_wrapper))
    except Exception:
        # If InvokeOnUiThread is not available, execute directly
        action_wrapper()

    finished = done_event.wait(timeout=timeout)
    if not finished:
        raise RuntimeError("Operation timed out waiting for Rhino main thread.")
    if result_box["error"]:
        raise RuntimeError(result_box["error"])
    return result_box["value"]


# In-memory mock store for standalone terminal testing when outside Rhino
try:
    import rhino3dm
    HAS_RHINO3DM = True
except ImportError:
    HAS_RHINO3DM = False

# Standalone 3DM model path (configurable via RHINO_MODEL_PATH env var)
STANDALONE_MODEL_PATH = os.environ.get("RHINO_MODEL_PATH", "")
if not STANDALONE_MODEL_PATH or not os.path.exists(STANDALONE_MODEL_PATH):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for f in os.listdir(current_dir):
        if f.lower().endswith(".3dm") and not f.startswith("~$"):
            STANDALONE_MODEL_PATH = os.path.join(current_dir, f)
            break

STANDALONE_DOC = None
if not IN_RHINO and HAS_RHINO3DM and STANDALONE_MODEL_PATH and os.path.exists(STANDALONE_MODEL_PATH):
    try:
        print("[RhinoBridge] Loading standalone 3DM model from: {}".format(STANDALONE_MODEL_PATH))
        STANDALONE_DOC = rhino3dm.File3dm.Read(STANDALONE_MODEL_PATH)
        print("[RhinoBridge] Loaded {} objects and {} layers from 3DM!".format(len(STANDALONE_DOC.Objects), len(STANDALONE_DOC.Layers)))
    except Exception as e:
        print("[RhinoBridge] Failed to load 3DM: {}".format(e))

MOCK_LAYERS = [
    {"index": 0, "id": "00000000-0000-0000-0000-000000000001", "name": "Default", "full_path": "Default", "color": "#000000", "visible": True, "locked": False, "is_current": True},
    {"index": 1, "id": "00000000-0000-0000-0000-000000000002", "name": "01_Architecture", "full_path": "01_Architecture", "color": "#e056fd", "visible": True, "locked": False, "is_current": False},
    {"index": 2, "id": "00000000-0000-0000-0000-000000000003", "name": "02_Structure", "full_path": "02_Structure", "color": "#0984e3", "visible": True, "locked": False, "is_current": False},
]

MOCK_OBJECTS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "Wall_Exterior_01",
        "type": "Brep",
        "layer": "01_Architecture",
        "visible": True,
        "selected": False,
        "bbox": {"min": [0.0, 0.0, 0.0], "max": [10.0, 0.3, 3.5]},
        "user_strings": {"Category": "Wall", "Phase": "New Construction"}
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "name": "Column_C1",
        "type": "Brep",
        "layer": "02_Structure",
        "visible": True,
        "selected": True,
        "bbox": {"min": [5.0, 5.0, 0.0], "max": [5.5, 5.5, 4.0]},
        "user_strings": {"Category": "Column", "Material": "Concrete"}
    }
]


def get_doc_summary():
    """Returns active document information."""
    if not IN_RHINO:
        if STANDALONE_DOC:
            model_name = os.path.basename(STANDALONE_MODEL_PATH) if STANDALONE_MODEL_PATH else "Standalone_Model.3dm"
            return {
                "status": "connected",
                "mode": "standalone_3dm_verified",
                "message": "Bridge connected to standalone 3DM model ({})".format(model_name),
                "rhino_version": "Rhino Standalone (OpenNURBS / rhino3dm verified)",
                "build_date": "2026-11-20",
                "document": {
                    "name": model_name,
                    "path": STANDALONE_MODEL_PATH,
                    "model_unit_system": "Meters",
                    "distance_tolerance": 0.001,
                    "angle_tolerance_degrees": 1.0,
                    "is_modified": False,
                    "active_view": "Perspective"
                },
                "counts": {
                    "total_objects": len(STANDALONE_DOC.Objects),
                    "selected_objects": 0,
                    "layers": len(STANDALONE_DOC.Layers),
                    "materials": 0
                }
            }
        selected_cnt = len([o for o in MOCK_OBJECTS if o.get("selected")])
        return {
            "status": "connected",
            "mode": "standalone_mock",
            "message": "Bridge is running in standalone terminal mode (ready for Rhino connection)",
            "rhino_version": "Rhino 9.x (Terminal Standalone / Simulated)",
            "build_date": "2026-11-20",
            "document": {
                "name": "Rhino_Model_Workspace.3dm",
                "path": os.path.abspath("Rhino_Model_Workspace.3dm"),
                "model_unit_system": "Millimeters",
                "distance_tolerance": 0.001,
                "angle_tolerance_degrees": 1.0,
                "is_modified": False,
                "active_view": "Perspective"
            },
            "counts": {
                "total_objects": len(MOCK_OBJECTS),
                "selected_objects": selected_cnt,
                "layers": len(MOCK_LAYERS),
                "materials": 2
            }
        }

    doc = Rhino.RhinoDoc.ActiveDoc
    if doc is None:
        return {"status": "error", "message": "No active document in Rhino"}

    active_view = doc.Views.ActiveView
    view_name = active_view.MainViewport.Name if active_view else "None"

    return {
        "status": "connected",
        "mode": "live_rhino",
        "rhino_version": str(Rhino.RhinoApp.Version),
        "build_date": str(Rhino.RhinoApp.BuildDate),
        "document": {
            "name": doc.Name or "Untitled",
            "path": doc.Path or "",
            "model_unit_system": str(doc.ModelUnitSystem),
            "distance_tolerance": doc.ModelAbsoluteTolerance,
            "angle_tolerance_degrees": doc.ModelAngleToleranceDegrees,
            "is_modified": doc.Modified,
            "active_view": view_name
        },
        "counts": {
            "total_objects": doc.Objects.Count,
            "selected_objects": len(doc.Objects.GetSelectedObjects(False, False)),
            "layers": doc.Layers.Count,
            "materials": doc.Materials.Count
        }
    }


def get_layers_list():
    """Returns all layers in the active document."""
    if not IN_RHINO:
        if STANDALONE_DOC:
            layers = []
            for lyr in STANDALONE_DOC.Layers:
                color_hex = "#{:02x}{:02x}{:02x}".format(lyr.Color[0], lyr.Color[1], lyr.Color[2])
                layers.append({
                    "index": lyr.Index,
                    "id": str(lyr.Id),
                    "name": lyr.Name,
                    "full_path": lyr.FullPath,
                    "color": color_hex,
                    "visible": lyr.Visible,
                    "locked": lyr.Locked,
                    "is_current": (lyr.Index == 0)
                })
            return layers
        return list(MOCK_LAYERS)

    doc = Rhino.RhinoDoc.ActiveDoc
    if doc is None:
        return []

    layers = []
    current_layer_idx = doc.Layers.CurrentLayerIndex
    for i in range(doc.Layers.Count):
        lyr = doc.Layers[i]
        if lyr.IsDeleted:
            continue
        color_hex = "#{:02x}{:02x}{:02x}".format(lyr.Color.R, lyr.Color.G, lyr.Color.B)
        layers.append({
            "index": lyr.Index,
            "id": str(lyr.Id),
            "name": lyr.Name,
            "full_path": lyr.FullPath,
            "color": color_hex,
            "visible": lyr.IsVisible,
            "locked": lyr.IsLocked,
            "is_current": (lyr.Index == current_layer_idx)
        })
    return layers


def get_objects_list(layer_filter=None, type_filter=None, selected_only=False, limit=500):
    """Returns objects matching optional filters."""
    if not IN_RHINO:
        if STANDALONE_DOC:
            results = []
            for obj in STANDALONE_DOC.Objects:
                lyr = STANDALONE_DOC.Layers[obj.Attributes.LayerIndex]
                layer_name = lyr.Name if lyr else "Default"
                if layer_filter and layer_filter.lower() not in layer_name.lower():
                    continue
                obj_type = type(obj.Geometry).__name__
                if type_filter and type_filter.lower() not in obj_type.lower():
                    continue
                
                bb = obj.Geometry.GetBoundingBox()
                bbox_data = None
                if bb.IsValid:
                    bbox_data = {
                        "min": [round(bb.Min.X, 4), round(bb.Min.Y, 4), round(bb.Min.Z, 4)],
                        "max": [round(bb.Max.X, 4), round(bb.Max.Y, 4), round(bb.Max.Z, 4)]
                    }
                
                user_strings = {}
                for k in ["Speaker_ID", "Zone_Name", "Ring", "Delay_ms", "Operating_SPL_dBA", "Downtilt_deg", "Status", "Receiver_ID", "Improved_STI", "Improved_C50_dB"]:
                    val = obj.Attributes.GetUserString(k)
                    if val:
                        user_strings[k] = val
                
                results.append({
                    "id": str(obj.Attributes.Id),
                    "name": obj.Attributes.Name or "",
                    "type": obj_type,
                    "layer": layer_name,
                    "visible": True,
                    "selected": False,
                    "bbox": bbox_data,
                    "user_strings": user_strings
                })
                if len(results) >= limit:
                    break
            return results

        results = []
        for obj in MOCK_OBJECTS:
            if selected_only and not obj.get("selected"):
                continue
            if layer_filter and obj.get("layer", "").lower() != layer_filter.lower():
                continue
            if type_filter and type_filter.lower() not in obj.get("type", "").lower():
                continue
            results.append(dict(obj))
            if len(results) >= limit:
                break
        return results

    doc = Rhino.RhinoDoc.ActiveDoc
    if doc is None:
        return []

    results = []
    selected_set = set(str(obj.Id) for obj in doc.Objects.GetSelectedObjects(False, False))

    for obj in doc.Objects:
        if obj.IsDeleted:
            continue
        obj_id = str(obj.Id)
        is_selected = obj_id in selected_set

        if selected_only and not is_selected:
            continue

        lyr = doc.Layers[obj.Attributes.LayerIndex]
        layer_name = lyr.Name if lyr else "Default"
        if layer_filter and layer_name.lower() != layer_filter.lower():
            continue

        obj_type = str(obj.ObjectType)
        if type_filter and type_filter.lower() not in obj_type.lower():
            continue

        bbox = obj.Geometry.GetBoundingBox(True)
        bbox_data = None
        if bbox.IsValid:
            bbox_data = {
                "min": [round(bbox.Min.X, 4), round(bbox.Min.Y, 4), round(bbox.Min.Z, 4)],
                "max": [round(bbox.Max.X, 4), round(bbox.Max.Y, 4), round(bbox.Max.Z, 4)]
            }

        # User strings (custom metadata attributes)
        user_strings = {}
        for key in obj.Attributes.GetUserStrings():
            user_strings[key] = obj.Attributes.GetUserString(key)

        results.append({
            "id": obj_id,
            "name": obj.Attributes.Name or "",
            "type": obj_type,
            "layer": layer_name,
            "visible": obj.Attributes.Visible,
            "selected": is_selected,
            "bbox": bbox_data,
            "user_strings": user_strings
        })

        if len(results) >= limit:
            break

    return results


def select_objects(guids, deselect_others=True):
    """Selects objects by GUID in Rhino."""
    if not IN_RHINO:
        if deselect_others:
            for o in MOCK_OBJECTS:
                o["selected"] = False
        selected_count = 0
        guid_set = set(str(g).lower() for g in guids)
        for o in MOCK_OBJECTS:
            if o["id"].lower() in guid_set:
                o["selected"] = True
                selected_count += 1
        return {"success": True, "selected_count": selected_count, "mode": "standalone_mock"}

    doc = Rhino.RhinoDoc.ActiveDoc
    if doc is None:
        return {"success": False, "message": "No active document"}

    import System
    if deselect_others:
        doc.Objects.UnselectAll()

    selected_count = 0
    for g_str in guids:
        try:
            guid = System.Guid(g_str)
            obj = doc.Objects.FindId(guid)
            if obj:
                doc.Objects.Select(guid)
                selected_count += 1
        except Exception:
            pass

    doc.Views.Redraw()
    return {"success": True, "selected_count": selected_count}


def delete_objects(guids):
    """Deletes objects by GUID."""
    if not IN_RHINO:
        global MOCK_OBJECTS
        initial_len = len(MOCK_OBJECTS)
        guid_set = set(str(g).lower() for g in guids)
        MOCK_OBJECTS = [o for o in MOCK_OBJECTS if o["id"].lower() not in guid_set]
        return {"success": True, "deleted_count": initial_len - len(MOCK_OBJECTS), "mode": "standalone_mock"}

    doc = Rhino.RhinoDoc.ActiveDoc
    if doc is None:
        return {"success": False, "message": "No active document"}

    import System
    deleted_count = 0
    for g_str in guids:
        try:
            guid = System.Guid(g_str)
            if doc.Objects.Delete(guid, True):
                deleted_count += 1
        except Exception:
            pass

    doc.Views.Redraw()
    return {"success": True, "deleted_count": deleted_count}


def create_primitive_geometry(geom_type, params):
    """Creates parametric primitives in Rhino."""
    if not IN_RHINO:
        import uuid
        new_id = str(uuid.uuid4())
        name = f"Mock_{geom_type.capitalize()}_{len(MOCK_OBJECTS) + 1}"
        MOCK_OBJECTS.append({
            "id": new_id,
            "name": name,
            "type": geom_type.capitalize(),
            "layer": "Default",
            "visible": True,
            "selected": False,
            "bbox": {"min": [0.0, 0.0, 0.0], "max": [10.0, 10.0, 10.0]},
            "user_strings": {"CreatedBy": "RhinoBridge"}
        })
        return {"success": True, "created_ids": [new_id], "name": name, "mode": "standalone_mock"}

    doc = Rhino.RhinoDoc.ActiveDoc
    if doc is None:
        return {"success": False, "message": "No active document"}

    created_ids = []

    if geom_type == "point":
        coords = params.get("coords", [0, 0, 0])
        pt = rg.Point3d(coords[0], coords[1], coords[2])
        g = doc.Objects.AddPoint(pt)
        if g:
            created_ids.append(str(g))

    elif geom_type == "line":
        start = params.get("start", [0, 0, 0])
        end = params.get("end", [10, 0, 0])
        pt1 = rg.Point3d(start[0], start[1], start[2])
        pt2 = rg.Point3d(end[0], end[1], end[2])
        line = rg.Line(pt1, pt2)
        g = doc.Objects.AddLine(line)
        if g:
            created_ids.append(str(g))

    elif geom_type == "box":
        origin = params.get("origin", [0, 0, 0])
        size = params.get("size", [10, 10, 10])
        dx, dy, dz = size[0], size[1], size[2]
        plane = rg.Plane(rg.Point3d(origin[0], origin[1], origin[2]), rg.Vector3d.ZAxis)
        box = rg.Box(plane, rg.Interval(0, dx), rg.Interval(0, dy), rg.Interval(0, dz))
        brep = box.ToBrep()
        g = doc.Objects.AddBrep(brep)
        if g:
            created_ids.append(str(g))

    elif geom_type == "sphere":
        center = params.get("center", [0, 0, 0])
        radius = float(params.get("radius", 5.0))
        sphere = rg.Sphere(rg.Point3d(center[0], center[1], center[2]), radius)
        g = doc.Objects.AddSphere(sphere)
        if g:
            created_ids.append(str(g))

    elif geom_type == "cylinder":
        base = params.get("base", [0, 0, 0])
        radius = float(params.get("radius", 5.0))
        height = float(params.get("height", 10.0))
        plane = rg.Plane(rg.Point3d(base[0], base[1], base[2]), rg.Vector3d.ZAxis)
        circle = rg.Circle(plane, radius)
        cylinder = rg.Cylinder(circle, height)
        brep = cylinder.ToBrep(True, True)
        g = doc.Objects.AddBrep(brep)
        if g:
            created_ids.append(str(g))

    else:
        return {"success": False, "error": "Unsupported geometry type: {}".format(geom_type)}

    doc.Views.Redraw()
    return {"success": True, "created_ids": created_ids}


def capture_viewport(output_path=None, width=1920, height=1080):
    """Captures the active Rhino viewport to an image file."""
    if not IN_RHINO:
        if not output_path:
            temp_dir = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "RhinoScreenshots")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            output_path = os.path.join(temp_dir, "viewport_mock_{}.png".format(int(time.time())))
        with open(output_path, "wb") as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82')
        return {"success": True, "file_path": output_path, "width": width, "height": height, "mode": "standalone_mock"}

    doc = Rhino.RhinoDoc.ActiveDoc
    if doc is None or doc.Views.ActiveView is None:
        return {"success": False, "error": "No active view to capture"}

    import System.Drawing
    if not output_path:
        temp_dir = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "RhinoScreenshots")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        output_path = os.path.join(temp_dir, "viewport_{}.png".format(int(time.time())))

    size = System.Drawing.Size(width, height)
    view = doc.Views.ActiveView
    bitmap = view.CaptureToBitmap(size)
    bitmap.Save(output_path, System.Drawing.Imaging.ImageFormat.Png)
    bitmap.Dispose()

    return {"success": True, "file_path": output_path, "width": width, "height": height}


def execute_python_code(code_str):
    """Executes arbitrary Python code inside Rhino with full namespace."""
    stdout_buf = StringIO()
    stderr_buf = StringIO()
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    exec_globals = {
        "Rhino": Rhino,
        "rg": rg,
        "rs": rs,
        "sc": sc,
        "doc": Rhino.RhinoDoc.ActiveDoc if IN_RHINO else None,
        "result": None
    }

    success = False
    error_msg = None
    result_val = None

    try:
        sys.stdout = stdout_buf
        sys.stderr = stderr_buf
        exec(code_str, exec_globals)
        result_val = exec_globals.get("result")
        success = True
    except Exception:
        error_msg = traceback.format_exc()
        success = False
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    if IN_RHINO and Rhino.RhinoDoc.ActiveDoc:
        Rhino.RhinoDoc.ActiveDoc.Views.Redraw()

    return {
        "success": success,
        "stdout": stdout_buf.getvalue(),
        "stderr": stderr_buf.getvalue(),
        "error": error_msg,
        "result": str(result_val) if result_val is not None else None
    }


class RhinoBridgeHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path in ("/ping", "/status"):
            try:
                summary = run_on_ui_thread(get_doc_summary)
                self._send_json(200, summary)
            except Exception as e:
                self._send_json(500, {"status": "error", "message": str(e)})

        elif path == "/document":
            try:
                summary = run_on_ui_thread(get_doc_summary)
                self._send_json(200, summary)
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        elif path == "/layers":
            try:
                layers = run_on_ui_thread(get_layers_list)
                self._send_json(200, {"layers": layers})
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        elif path == "/objects":
            try:
                layer_filter = query.get("layer", [None])[0]
                type_filter = query.get("type", [None])[0]
                selected_only = query.get("selected_only", ["false"])[0].lower() == "true"
                limit = int(query.get("limit", [500])[0])

                objs = run_on_ui_thread(lambda: get_objects_list(
                    layer_filter=layer_filter,
                    type_filter=type_filter,
                    selected_only=selected_only,
                    limit=limit
                ))
                self._send_json(200, {"objects": objs, "count": len(objs)})
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        elif path == "/selected":
            try:
                objs = run_on_ui_thread(lambda: get_objects_list(selected_only=True))
                self._send_json(200, {"selected_objects": objs, "count": len(objs)})
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        else:
            self._send_json(404, {"error": "Endpoint not found: {}".format(path)})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        data = {}
        if post_data:
            try:
                data = json.loads(post_data)
            except Exception as e:
                self._send_json(400, {"error": "Invalid JSON: {}".format(e)})
                return

        if path == "/command":
            cmd = data.get("command", "")
            echo = bool(data.get("echo", False))
            if not cmd:
                self._send_json(400, {"error": "Missing 'command' parameter"})
                return

            def run_cmd():
                if not IN_RHINO:
                    return True
                return Rhino.RhinoApp.RunScript(cmd, echo)

            try:
                success = run_on_ui_thread(run_cmd)
                self._send_json(200, {"success": success, "command": cmd})
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        elif path == "/execute":
            code = data.get("code", "")
            if not code:
                self._send_json(400, {"error": "Missing 'code' parameter"})
                return

            try:
                result = run_on_ui_thread(lambda: execute_python_code(code))
                self._send_json(200, result)
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        elif path == "/select":
            guids = data.get("guids", [])
            deselect_others = bool(data.get("deselect_others", True))
            try:
                res = run_on_ui_thread(lambda: select_objects(guids, deselect_others))
                self._send_json(200, res)
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        elif path == "/delete":
            guids = data.get("guids", [])
            try:
                res = run_on_ui_thread(lambda: delete_objects(guids))
                self._send_json(200, res)
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        elif path == "/geometry/create":
            geom_type = data.get("type", "")
            params = data.get("params", {})
            try:
                res = run_on_ui_thread(lambda: create_primitive_geometry(geom_type, params))
                self._send_json(200, res)
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        elif path == "/view/capture":
            file_path = data.get("file_path")
            width = int(data.get("width", 1920))
            height = int(data.get("height", 1080))
            try:
                res = run_on_ui_thread(lambda: capture_viewport(file_path, width, height))
                self._send_json(200, res)
            except Exception as e:
                self._send_json(500, {"error": str(e)})

        else:
            self._send_json(404, {"error": "Endpoint not found: {}".format(path)})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        # Silence standard HTTP logging in Rhino command line / console
        pass


def start_server():
    server = HTTPServer((HOST, PORT), RhinoBridgeHandler)
    globals()["RHINO_BRIDGE_SERVER"] = server
    print("[RhinoBridge] Live Bridge listening on http://{}:{}".format(HOST, PORT))
    try:
        server.serve_forever()
    except Exception:
        pass


# Start the bridge server when run directly or inside Rhino
if IN_RHINO:
    # Inside Rhino: run in a daemon background thread so Rhino UI stays responsive
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    print("[RhinoBridge] Rhino Agent Bridge started successfully on port {}!".format(PORT))
elif __name__ == "__main__":
    # Standalone / test mode: keep main thread alive
    print("[RhinoBridge] Starting standalone bridge server on http://{}:{}...".format(HOST, PORT))
    print("[RhinoBridge] WARNING: Running outside Rhino process. RhinoCommon calls will be simulated.")
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[RhinoBridge] Stopped.")


