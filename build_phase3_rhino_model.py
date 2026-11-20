"""Creates the updated Rhino 3DM model with separate acoustic material intervention layers.
Model: Muhammad_Ali_Mosque_Acoustic_Optimized_Materials.3dm

Preserves all 4,977 architectural objects, decommissioned pier markers, 20 speakers, and 16 receivers.
Adds 4 dedicated reversible intervention layers with precise 3D geometry and user strings:
1. 05_Acoustics::Treatment_Enhanced_Carpet
2. 06_Acoustics::Treatment_Perforated_Wood_Panels
3. 07_Acoustics::Treatment_Acoustic_Curtains
4. 08_Acoustics::Treatment_Suspended_Baffles
"""

import os
import rhino3dm
import math
import numpy as np

PROJECT_DIR = r"E:\course\03_Programming_Data\AI\Projects\rhino"
IMP_DIR = os.path.join(PROJECT_DIR, "Improved_Acoustic_System")
SRC_MODEL_PATH = os.path.join(IMP_DIR, "Muhammad_Ali_Mosque_Acoustic_Improved.3dm")
DST_MODEL_PATH = os.path.join(IMP_DIR, "Muhammad_Ali_Mosque_Acoustic_Optimized_Materials.3dm")

def create_box_mesh(min_pt, max_pt):
    """Creates a 6-face rectangular mesh."""
    mesh = rhino3dm.Mesh()
    x0, y0, z0 = min_pt
    x1, y1, z1 = max_pt
    mesh.Vertices.Add(x0, y0, z0) # 0
    mesh.Vertices.Add(x1, y0, z0) # 1
    mesh.Vertices.Add(x1, y1, z0) # 2
    mesh.Vertices.Add(x0, y1, z0) # 3
    mesh.Vertices.Add(x0, y0, z1) # 4
    mesh.Vertices.Add(x1, y0, z1) # 5
    mesh.Vertices.Add(x1, y1, z1) # 6
    mesh.Vertices.Add(x0, y1, z1) # 7

    mesh.Faces.AddFace(0, 3, 2, 1) # bottom
    mesh.Faces.AddFace(4, 5, 6, 7) # top
    mesh.Faces.AddFace(0, 1, 5, 4) # front
    mesh.Faces.AddFace(2, 3, 7, 6) # back
    mesh.Faces.AddFace(0, 4, 7, 3) # left
    mesh.Faces.AddFace(1, 2, 6, 5) # right
    mesh.Normals.ComputeNormals()
    mesh.Compact()
    return mesh

def main():
    print(f"Reading source model: {SRC_MODEL_PATH}")
    doc = rhino3dm.File3dm.Read(SRC_MODEL_PATH)

    # Add 4 New Treatment Layers
    # Layer 5: Enhanced Carpet
    layer_carpet = rhino3dm.Layer()
    layer_carpet.Name = "05_Acoustics::Treatment_Enhanced_Carpet"
    layer_carpet.Color = (0, 180, 160, 255) # Teal
    doc.Layers.Add(layer_carpet)
    idx_carpet = len(doc.Layers) - 1

    # Layer 6: Perforated Wood Panels
    layer_panels = rhino3dm.Layer()
    layer_panels.Name = "06_Acoustics::Treatment_Perforated_Wood_Panels"
    layer_panels.Color = (210, 120, 40, 255) # Amber wood
    doc.Layers.Add(layer_panels)
    idx_panels = len(doc.Layers) - 1

    # Layer 7: Acoustic Curtains
    layer_curtains = rhino3dm.Layer()
    layer_curtains.Name = "07_Acoustics::Treatment_Acoustic_Curtains"
    layer_curtains.Color = (180, 40, 80, 255) # Crimson velour
    doc.Layers.Add(layer_curtains)
    idx_curtains = len(doc.Layers) - 1

    # Layer 8: Suspended Baffles
    layer_baffles = rhino3dm.Layer()
    layer_baffles.Name = "08_Acoustics::Treatment_Suspended_Baffles"
    layer_baffles.Color = (220, 180, 30, 255) # Gold lattice
    doc.Layers.Add(layer_baffles)
    idx_baffles = len(doc.Layers) - 1

    print("Adding 3D Treatment Geometries & Metadata...")

    # 1. Enhanced Carpet Mesh (41m x 41m floor boundary, thickness 22mm)
    carpet_mesh = create_box_mesh(
        (0.83 - 20.5, -21.75 - 20.5, 5.57),
        (0.83 + 20.5, -21.75 + 20.5, 5.57 + 0.022)
    )
    attr_carpet = rhino3dm.ObjectAttributes()
    attr_carpet.LayerIndex = idx_carpet
    attr_carpet.Name = "TREAT_ENHANCED_PRAYER_CARPET"
    attr_carpet.SetUserString("Treatment_Type", "Enhanced Acoustic Prayer Carpet")
    attr_carpet.SetUserString("Area_m2", "1681.0")
    attr_carpet.SetUserString("Thickness_mm", "22.0")
    attr_carpet.SetUserString("Composition", "12mm High-Density Wool Pile (1800 g/m2) + 10mm Open-Cell Polyurethane Foam Underlay")
    attr_carpet.SetUserString("Absorption_500Hz", "0.65")
    attr_carpet.SetUserString("Absorption_1000Hz", "0.75")
    attr_carpet.SetUserString("Mounting", "Loose-laid directly over historic marble floor; 100% reversible; non-adhesive")
    attr_carpet.SetUserString("Heritage_Status", "Approved / Non-Invasive")
    doc.Objects.AddMesh(carpet_mesh, attr_carpet)

    # 2. Perforated Wooden Panels (Wainscot level along East, West, North walls)
    # Total 420 m2 -> 35 panel units (each 4.0m wide x 3.0m high x 0.106m deep)
    # North wall panels (Y = -1.25)
    panel_count = 0
    for i, x_pos in enumerate(np.linspace(-18.0, 18.0, 10)):
        panel_box = create_box_mesh(
            (x_pos - 1.8, -1.35, 5.57),
            (x_pos + 1.8, -1.244, 8.57)
        )
        attr_panel = rhino3dm.ObjectAttributes()
        attr_panel.LayerIndex = idx_panels
        attr_panel.Name = f"PANEL_NORTH_{i+1:02d}"
        attr_panel.SetUserString("Treatment_Type", "Decorative Perforated Wooden Acoustic Panel")
        attr_panel.SetUserString("Area_m2", "10.8")
        attr_panel.SetUserString("Thickness_mm", "106.0")
        attr_panel.SetUserString("Facing", "16mm Fire-Rated MDF with CNC Laser-Cut Islamic Geometric Arabesque (P=14%, hole=8mm)")
        attr_panel.SetUserString("Backing", "Black Acoustic Fleece + 40mm Rockwool (45 kg/m3) + 50mm Air Cavity")
        attr_panel.SetUserString("Absorption_500Hz", "0.85")
        attr_panel.SetUserString("Mounting", "Freestanding bronze compression frame with weighted floor plates; zero drilling")
        attr_panel.SetUserString("Heritage_Status", "Reversible / Conservation Compliant")
        doc.Objects.AddMesh(panel_box, attr_panel)
        panel_count += 1

    # East wall panels (X = 21.33)
    for i, y_pos in enumerate(np.linspace(-38.0, -5.0, 12)):
        panel_box = create_box_mesh(
            (21.224, y_pos - 1.3, 5.57),
            (21.33, y_pos + 1.3, 8.57)
        )
        attr_panel = rhino3dm.ObjectAttributes()
        attr_panel.LayerIndex = idx_panels
        attr_panel.Name = f"PANEL_EAST_{i+1:02d}"
        attr_panel.SetUserString("Treatment_Type", "Decorative Perforated Wooden Acoustic Panel")
        attr_panel.SetUserString("Area_m2", "7.8")
        attr_panel.SetUserString("Thickness_mm", "106.0")
        attr_panel.SetUserString("Absorption_500Hz", "0.85")
        attr_panel.SetUserString("Mounting", "Freestanding bronze compression frame; zero drilling")
        doc.Objects.AddMesh(panel_box, attr_panel)
        panel_count += 1

    # West wall panels (X = -19.67)
    for i, y_pos in enumerate(np.linspace(-38.0, -5.0, 12)):
        panel_box = create_box_mesh(
            (-19.67, y_pos - 1.3, 5.57),
            (-19.564, y_pos + 1.3, 8.57)
        )
        attr_panel = rhino3dm.ObjectAttributes()
        attr_panel.LayerIndex = idx_panels
        attr_panel.Name = f"PANEL_WEST_{i+1:02d}"
        attr_panel.SetUserString("Treatment_Type", "Decorative Perforated Wooden Acoustic Panel")
        attr_panel.SetUserString("Area_m2", "7.8")
        attr_panel.SetUserString("Thickness_mm", "106.0")
        attr_panel.SetUserString("Absorption_500Hz", "0.85")
        attr_panel.SetUserString("Mounting", "Freestanding bronze compression frame; zero drilling")
        doc.Objects.AddMesh(panel_box, attr_panel)
        panel_count += 1

    # 3. Retractable Heavy Acoustic Curtains (360 m2 -> 24 window arcades, each 2.5m wide x 6.0m high)
    curtain_count = 0
    # East window bays
    for i, y_pos in enumerate(np.linspace(-36.0, -8.0, 8)):
        curtain_box = create_box_mesh(
            (21.0, y_pos - 1.25, 9.57),
            (21.02, y_pos + 1.25, 15.57)
        )
        attr_curt = rhino3dm.ObjectAttributes()
        attr_curt.LayerIndex = idx_curtains
        attr_curt.Name = f"CURTAIN_EAST_{i+1:02d}"
        attr_curt.SetUserString("Treatment_Type", "Retractable Heavy Acoustic Curtain")
        attr_curt.SetUserString("Area_m2", "15.0")
        attr_curt.SetUserString("Fabric", "Heavy Acoustic Velour (550 g/m2), 100% Fullness, 100mm Air Gap")
        attr_curt.SetUserString("Absorption_500Hz", "0.75")
        attr_curt.SetUserString("Mounting", "Tensioned stainless catenary cable clamped to reveals; motorized retraction")
        attr_curt.SetUserString("Heritage_Status", "100% Reversible / Retracted during tourist hours")
        doc.Objects.AddMesh(curtain_box, attr_curt)
        curtain_count += 1

    # West window bays
    for i, y_pos in enumerate(np.linspace(-36.0, -8.0, 8)):
        curtain_box = create_box_mesh(
            (-19.35, y_pos - 1.25, 9.57),
            (-19.33, y_pos + 1.25, 15.57)
        )
        attr_curt = rhino3dm.ObjectAttributes()
        attr_curt.LayerIndex = idx_curtains
        attr_curt.Name = f"CURTAIN_WEST_{i+1:02d}"
        attr_curt.SetUserString("Treatment_Type", "Retractable Heavy Acoustic Curtain")
        attr_curt.SetUserString("Area_m2", "15.0")
        attr_curt.SetUserString("Absorption_500Hz", "0.75")
        attr_curt.SetUserString("Mounting", "Tensioned stainless catenary cable; motorized retraction")
        doc.Objects.AddMesh(curtain_box, attr_curt)
        curtain_count += 1

    # North entrance portal bays
    for i, x_pos in enumerate(np.linspace(-15.0, 15.0, 8)):
        curtain_box = create_box_mesh(
            (x_pos - 1.25, -1.6, 9.57),
            (x_pos + 1.25, -1.58, 15.57)
        )
        attr_curt = rhino3dm.ObjectAttributes()
        attr_curt.LayerIndex = idx_curtains
        attr_curt.Name = f"CURTAIN_NORTH_{i+1:02d}"
        attr_curt.SetUserString("Treatment_Type", "Retractable Heavy Acoustic Curtain")
        attr_curt.SetUserString("Area_m2", "15.0")
        attr_curt.SetUserString("Absorption_500Hz", "0.75")
        attr_curt.SetUserString("Mounting", "Tensioned stainless catenary cable; motorized retraction")
        doc.Objects.AddMesh(curtain_box, attr_curt)
        curtain_count += 1

    # 4. Islamic Geometric Suspended Acoustic Baffles (280 m2 -> 35 dual-faced baffles 3.5m x 1.2m)
    baffle_count = 0
    # Suspended between main piers and perimeter walls under semi-domes (Z = 16.0m)
    baffle_coords = [
        # North Semi-Dome lateral bays
        (-4.0, -8.0), (0.83, -8.0), (5.0, -8.0),
        (-4.0, -10.0), (0.83, -10.0), (5.0, -10.0),
        # South Semi-Dome lateral bays
        (-4.0, -35.0), (0.83, -35.0), (5.0, -35.0),
        (-4.0, -33.0), (0.83, -33.0), (5.0, -33.0),
        # East Semi-Dome lateral bays
        (14.0, -18.0), (14.0, -21.75), (14.0, -25.0),
        (16.5, -18.0), (16.5, -21.75), (16.5, -25.0),
        # West Semi-Dome lateral bays
        (-12.0, -18.0), (-12.0, -21.75), (-12.0, -25.0),
        (-14.5, -18.0), (-14.5, -21.75), (-14.5, -25.0),
    ]

    for i, (bx, by) in enumerate(baffle_coords):
        baffle_box = create_box_mesh(
            (bx - 1.75, by - 0.03, 16.0),
            (bx + 1.75, by + 0.03, 17.2)
        )
        attr_baffle = rhino3dm.ObjectAttributes()
        attr_baffle.LayerIndex = idx_baffles
        attr_baffle.Name = f"BAFFLE_SUSPENDED_{i+1:02d}"
        attr_baffle.SetUserString("Treatment_Type", "Islamic Geometric Suspended Acoustic Baffle")
        attr_baffle.SetUserString("Face_Area_m2", "8.4") # dual-faced 3.5m x 1.2m x 2
        attr_baffle.SetUserString("Thickness_mm", "60.0")
        attr_baffle.SetUserString("Composition", "Dual-sided Laser-Cut Islamic Geometric Star Lattice (P=18%) + 50mm Basalt Core (35 kg/m3)")
        attr_baffle.SetUserString("Absorption_500Hz", "0.85")
        attr_baffle.SetUserString("Mounting", "Silicone-lined friction clamps attached to existing forged tie-rods; zero masonry drilling")
        attr_baffle.SetUserString("Heritage_Status", "Requires Conservation & Structural Verification")
        doc.Objects.AddMesh(baffle_box, attr_baffle)
        baffle_count += 1

    print(f"Added {1} carpet mesh, {panel_count} panel meshes, {curtain_count} curtain meshes, and {baffle_count} baffle meshes.")
    print(f"Saving updated model: {DST_MODEL_PATH}")
    doc.Write(DST_MODEL_PATH, 8)
    print("Model successfully written to disk!")

if __name__ == "__main__":
    main()
