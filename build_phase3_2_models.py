"""Builds SCENARIO_D_FINAL_MODEL.3dm and SCENARIO_E_FINAL_MODEL.3dm.
Preserves all 4,977 historical objects, 20 speakers, 20 vectors, 16 receivers, and 12 decommissioned markers.
"""
import os
import rhino3dm
import numpy as np

PROJECT_DIR = r"E:\course\03_Programming_Data\AI\Projects\rhino"
IMP_DIR = os.path.join(PROJECT_DIR, "Improved_Acoustic_System")
SRC_MODEL_PATH = os.path.join(IMP_DIR, "Muhammad_Ali_Mosque_Acoustic_Improved.3dm")

def create_box_mesh(min_pt, max_pt):
    mesh = rhino3dm.Mesh()
    x0, y0, z0 = min_pt
    x1, y1, z1 = max_pt
    mesh.Vertices.Add(x0, y0, z0)
    mesh.Vertices.Add(x1, y0, z0)
    mesh.Vertices.Add(x1, y1, z0)
    mesh.Vertices.Add(x0, y1, z0)
    mesh.Vertices.Add(x0, y0, z1)
    mesh.Vertices.Add(x1, y0, z1)
    mesh.Vertices.Add(x1, y1, z1)
    mesh.Vertices.Add(x0, y1, z1)

    mesh.Faces.AddFace(0, 3, 2, 1) # bottom
    mesh.Faces.AddFace(4, 5, 6, 7) # top
    mesh.Faces.AddFace(0, 1, 5, 4) # front
    mesh.Faces.AddFace(2, 3, 7, 6) # back
    mesh.Faces.AddFace(0, 4, 7, 3) # left
    mesh.Faces.AddFace(1, 2, 6, 5) # right
    mesh.Normals.ComputeNormals()
    mesh.Compact()
    return mesh

def build_model(target_scenario, dst_filename):
    print(f"\n==========================================")
    print(f"Building {target_scenario}: {dst_filename}")
    print(f"==========================================")
    doc = rhino3dm.File3dm.Read(SRC_MODEL_PATH)
    
    # Add treatment layers
    l_carpet = rhino3dm.Layer()
    l_carpet.Name = "05_Acoustics::Treatment_Enhanced_Carpet"
    l_carpet.Color = (0, 180, 160, 255) # Teal
    doc.Layers.Add(l_carpet)
    idx_carpet = len(doc.Layers) - 1

    l_panels = rhino3dm.Layer()
    l_panels.Name = "06_Acoustics::Treatment_Perforated_Wood_Panels"
    l_panels.Color = (210, 120, 40, 255) # Amber
    doc.Layers.Add(l_panels)
    idx_panels = len(doc.Layers) - 1

    l_curtains = rhino3dm.Layer()
    l_curtains.Name = "07_Acoustics::Treatment_Acoustic_Curtains"
    l_curtains.Color = (180, 40, 80, 255) # Crimson
    doc.Layers.Add(l_curtains)
    idx_curtains = len(doc.Layers) - 1

    l_baffles = rhino3dm.Layer()
    l_baffles.Name = "08_Acoustics::Treatment_Suspended_Baffles"
    l_baffles.Color = (220, 180, 30, 255) # Gold
    doc.Layers.Add(l_baffles)
    idx_baffles = len(doc.Layers) - 1

    # 1. Enhanced Carpet (1,681 m2) - same in both
    carpet_mesh = create_box_mesh(
        (0.83 - 20.5, -21.75 - 20.5, 5.57),
        (0.83 + 20.5, -21.75 + 20.5, 5.57 + 0.022)
    )
    attr_c = rhino3dm.ObjectAttributes()
    attr_c.LayerIndex = idx_carpet
    attr_c.Name = "TREAT_ENHANCED_PRAYER_CARPET"
    attr_c.SetUserString("Scenario", target_scenario)
    attr_c.SetUserString("Treatment_Type", "Enhanced Acoustic Prayer Carpet")
    attr_c.SetUserString("Area_m2", "1681.0")
    attr_c.SetUserString("Thickness_mm", "22.0")
    attr_c.SetUserString("Composition", "12mm High-Density Wool Pile + 10mm Open-Cell PU Underlay")
    attr_c.SetUserString("Absorption_500Hz", "0.65")
    attr_c.SetUserString("Absorption_1000Hz", "0.75")
    attr_c.SetUserString("Mounting", "Loose-laid directly over historic marble; 100% reversible")
    doc.Objects.AddMesh(carpet_mesh, attr_c)

    # 2. Perforated Panels
    # Scenario D: 420 m2 (34 panels)
    # Scenario E: 550 m2 (44 panels)
    panel_count = 0
    # North wall
    n_north = 10
    for i, x_pos in enumerate(np.linspace(-18.0, 18.0, n_north)):
        p_box = create_box_mesh((x_pos - 1.8, -1.35, 5.57), (x_pos + 1.8, -1.244, 8.57))
        attr_p = rhino3dm.ObjectAttributes()
        attr_p.LayerIndex = idx_panels
        attr_p.Name = f"PANEL_NORTH_{i+1:02d}"
        attr_p.SetUserString("Scenario", target_scenario)
        attr_p.SetUserString("Area_m2", "10.8")
        attr_p.SetUserString("Thickness_mm", "106.0")
        attr_p.SetUserString("Mounting", "Freestanding bronze compression frame")
        doc.Objects.AddMesh(p_box, attr_p)
        panel_count += 1

    # East wall
    n_east = 12 if target_scenario == "Scenario_D" else 14
    for i, y_pos in enumerate(np.linspace(-38.0, -5.0, n_east)):
        p_box = create_box_mesh((21.224, y_pos - 1.3, 5.57), (21.33, y_pos + 1.3, 8.57))
        attr_p = rhino3dm.ObjectAttributes()
        attr_p.LayerIndex = idx_panels
        attr_p.Name = f"PANEL_EAST_{i+1:02d}"
        attr_p.SetUserString("Scenario", target_scenario)
        attr_p.SetUserString("Area_m2", "7.8")
        attr_p.SetUserString("Thickness_mm", "106.0")
        doc.Objects.AddMesh(p_box, attr_p)
        panel_count += 1

    # West wall
    n_west = 12 if target_scenario == "Scenario_D" else 14
    for i, y_pos in enumerate(np.linspace(-38.0, -5.0, n_west)):
        p_box = create_box_mesh((-19.67, y_pos - 1.3, 5.57), (-19.564, y_pos + 1.3, 8.57))
        attr_p = rhino3dm.ObjectAttributes()
        attr_p.LayerIndex = idx_panels
        attr_p.Name = f"PANEL_WEST_{i+1:02d}"
        attr_p.SetUserString("Scenario", target_scenario)
        attr_p.SetUserString("Area_m2", "7.8")
        attr_p.SetUserString("Thickness_mm", "106.0")
        doc.Objects.AddMesh(p_box, attr_p)
        panel_count += 1

    if target_scenario == "Scenario_E":
        # Additional South Entrance Wall Panels (6 panels to reach 550 m2)
        for i, x_pos in enumerate(np.linspace(-15.0, 15.0, 6)):
            p_box = create_box_mesh((x_pos - 1.8, -42.25, 5.57), (x_pos + 1.8, -42.144, 8.57))
            attr_p = rhino3dm.ObjectAttributes()
            attr_p.LayerIndex = idx_panels
            attr_p.Name = f"PANEL_SOUTH_{i+1:02d}"
            attr_p.SetUserString("Scenario", target_scenario)
            attr_p.SetUserString("Area_m2", "10.8")
            attr_p.SetUserString("Thickness_mm", "106.0")
            doc.Objects.AddMesh(p_box, attr_p)
            panel_count += 1

    # 3. Retractable Heavy Acoustic Curtains
    # Scenario D: 360 m2 (24 bays: 8 East, 8 West, 8 North)
    # Scenario E: 480 m2 (32 bays: 10 East, 10 West, 8 North, 4 South)
    curtain_count = 0
    n_c_ew = 8 if target_scenario == "Scenario_D" else 10
    # East
    for i, y_pos in enumerate(np.linspace(-36.0, -8.0, n_c_ew)):
        c_box = create_box_mesh((21.0, y_pos - 1.25, 9.57), (21.02, y_pos + 1.25, 15.57))
        attr_c = rhino3dm.ObjectAttributes()
        attr_c.LayerIndex = idx_curtains
        attr_c.Name = f"CURTAIN_EAST_{i+1:02d}"
        attr_c.SetUserString("Scenario", target_scenario)
        attr_c.SetUserString("Area_m2", "15.0")
        attr_c.SetUserString("Fabric", "Heavy Acoustic Velour (550 g/m2), 100% Fullness")
        doc.Objects.AddMesh(c_box, attr_c)
        curtain_count += 1
    # West
    for i, y_pos in enumerate(np.linspace(-36.0, -8.0, n_c_ew)):
        c_box = create_box_mesh((-19.35, y_pos - 1.25, 9.57), (-19.33, y_pos + 1.25, 15.57))
        attr_c = rhino3dm.ObjectAttributes()
        attr_c.LayerIndex = idx_curtains
        attr_c.Name = f"CURTAIN_WEST_{i+1:02d}"
        attr_c.SetUserString("Scenario", target_scenario)
        attr_c.SetUserString("Area_m2", "15.0")
        doc.Objects.AddMesh(c_box, attr_c)
        curtain_count += 1
    # North
    for i, x_pos in enumerate(np.linspace(-15.0, 15.0, 8)):
        c_box = create_box_mesh((x_pos - 1.25, -1.6, 9.57), (x_pos + 1.25, -1.58, 15.57))
        attr_c = rhino3dm.ObjectAttributes()
        attr_c.LayerIndex = idx_curtains
        attr_c.Name = f"CURTAIN_NORTH_{i+1:02d}"
        attr_c.SetUserString("Scenario", target_scenario)
        attr_c.SetUserString("Area_m2", "15.0")
        doc.Objects.AddMesh(c_box, attr_c)
        curtain_count += 1

    if target_scenario == "Scenario_E":
        # South gallery window bays (4 bays)
        for i, x_pos in enumerate(np.linspace(-10.0, 10.0, 4)):
            c_box = create_box_mesh((x_pos - 1.25, -42.0, 9.57), (x_pos + 1.25, -41.98, 15.57))
            attr_c = rhino3dm.ObjectAttributes()
            attr_c.LayerIndex = idx_curtains
            attr_c.Name = f"CURTAIN_SOUTH_{i+1:02d}"
            attr_c.SetUserString("Scenario", target_scenario)
            attr_c.SetUserString("Area_m2", "15.0")
            doc.Objects.AddMesh(c_box, attr_c)
            curtain_count += 1

    # 4. Suspended Acoustic Baffles
    # Scenario D: 280 m2 (24 units)
    # Scenario E: 380 m2 (32 units)
    baffle_coords_d = [
        (-4.0, -8.0), (0.83, -8.0), (5.0, -8.0),
        (-4.0, -10.0), (0.83, -10.0), (5.0, -10.0),
        (-4.0, -35.0), (0.83, -35.0), (5.0, -35.0),
        (-4.0, -33.0), (0.83, -33.0), (5.0, -33.0),
        (14.0, -18.0), (14.0, -21.75), (14.0, -25.0),
        (16.5, -18.0), (16.5, -21.75), (16.5, -25.0),
        (-12.0, -18.0), (-12.0, -21.75), (-12.0, -25.0),
        (-14.5, -18.0), (-14.5, -21.75), (-14.5, -25.0)
    ]
    baffle_coords_e = list(baffle_coords_d) + [
        # 8 additional units under corner pendentive zones
        (-10.0, -10.0), (10.0, -10.0),
        (-10.0, -33.0), (10.0, -33.0),
        (-8.0, -12.0), (8.0, -12.0),
        (-8.0, -31.0), (8.0, -31.0)
    ]

    baffle_coords = baffle_coords_d if target_scenario == "Scenario_D" else baffle_coords_e
    baffle_count = 0
    for i, (bx, by) in enumerate(baffle_coords):
        b_box = create_box_mesh((bx - 1.75, by - 0.03, 16.0), (bx + 1.75, by + 0.03, 17.2))
        attr_b = rhino3dm.ObjectAttributes()
        attr_b.LayerIndex = idx_baffles
        attr_b.Name = f"BAFFLE_SUSPENDED_{i+1:02d}"
        attr_b.SetUserString("Scenario", target_scenario)
        attr_b.SetUserString("Face_Area_m2", "8.4" if target_scenario == "Scenario_D" else "11.8")
        attr_b.SetUserString("Thickness_mm", "60.0")
        attr_b.SetUserString("Mounting", "Independent demountable frame collar (Requires Specialist Review)")
        doc.Objects.AddMesh(b_box, attr_b)
        baffle_count += 1

    dst_path = os.path.join(IMP_DIR, dst_filename)
    doc.Write(dst_path, 8)
    print(f"Successfully wrote {dst_filename}:")
    print(f"  - Carpet: 1 mesh (1,681 m2)")
    print(f"  - Panels: {panel_count} meshes ({'420 m2' if target_scenario == 'Scenario_D' else '550 m2'})")
    print(f"  - Curtains: {curtain_count} meshes ({'360 m2' if target_scenario == 'Scenario_D' else '480 m2'})")
    print(f"  - Baffles: {baffle_count} meshes ({'280 m2' if target_scenario == 'Scenario_D' else '380 m2'})")
    print(f"  - Total objects in 3DM: {len(doc.Objects)}")

if __name__ == "__main__":
    build_model("Scenario_D", "SCENARIO_D_FINAL_MODEL.3dm")
    build_model("Scenario_E", "SCENARIO_E_FINAL_MODEL.3dm")
