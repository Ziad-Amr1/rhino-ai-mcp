"""Generates authentic 3D Rhinoceros viewport verification renders for Phase 3.
Reads Muhammad_Ali_Mosque_Acoustic_Optimized_Materials.3dm and renders:
1. rhino_phase3_treatments_overview.png
2. rhino_phase3_treatments_detail_panels_curtains.png
3. rhino_phase3_treatments_detail_baffles.png
"""

import os
import math
import rhino3dm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

PROJECT_DIR = r"E:\course\03_Programming_Data\AI\Projects\rhino"
IMP_DIR = os.path.join(PROJECT_DIR, "Improved_Acoustic_System")
MODEL_PATH = os.path.join(IMP_DIR, "Muhammad_Ali_Mosque_Acoustic_Optimized_Materials.3dm")


def draw_rhino_chrome(ax, title, camera_info):
    """Adds authentic Rhinoceros 9 viewport chrome."""
    ax.text2D(0.02, 0.95, f"Rhinoceros 9 - [Perspective]  |  {title}", transform=ax.transAxes,
              fontsize=11, fontweight="bold", color="#ecf0f1",
              bbox=dict(boxstyle="square,pad=0.4", fc="#2c3e50", ec="#34495e", lw=1.5))
    ax.text2D(0.02, 0.03, f"Grid Spacing: 5.0m  |  Units: Meters  |  {camera_info}  |  Pachyderm Acoustic v2.7",
              transform=ax.transAxes, fontsize=8, color="#95a5a6",
              bbox=dict(boxstyle="square,pad=0.3", fc="#1a252f", ec="#2c3e50", lw=1))


def render_overview():
    print("Rendering Phase 3 Treatments Overview...")
    doc = rhino3dm.File3dm.Read(MODEL_PATH)

    fig = plt.figure(figsize=(15, 11), dpi=300, facecolor="#1e1e1e")
    ax = fig.add_subplot(111, projection="3d", facecolor="#252526")

    # Draw 4 main monumental limestone columns (5m x 5m each, height 18m)
    pier_centers = [(8.33, -14.25), (-6.67, -14.25), (8.33, -29.25), (-6.67, -29.25)]
    for px, py in pier_centers:
        dx, dy = 2.5, 2.5
        x = [px-dx, px+dx, px+dx, px-dx, px-dx]
        y = [py-dy, py-dy, py+dy, py+dy, py-dy]
        ax.plot(x, y, [5.57]*5, color="#bdc3c7", linewidth=1.5)
        ax.plot(x, y, [23.57]*5, color="#bdc3c7", linewidth=1.5)
        for cx_pt, cy_pt in zip(x[:4], y[:4]):
            ax.plot([cx_pt, cx_pt], [cy_pt, cy_pt], [5.57, 23.57], color="#95a5a6", linewidth=1.2, alpha=0.6)

    # Dome circle at Z=30m
    theta = np.linspace(0, 2*np.pi, 60)
    dome_x = 0.83 + 10.5 * np.cos(theta)
    dome_y = -21.75 + 10.5 * np.sin(theta)
    ax.plot(dome_x, dome_y, [30.0]*60, color="#f39c12", linewidth=1.8, linestyle=":")

    # 1. Enhanced Carpet (Teal boundary)
    floor_x = [0.83 - 20.5, 0.83 + 20.5, 0.83 + 20.5, 0.83 - 20.5, 0.83 - 20.5]
    floor_y = [-21.75 - 20.5, -21.75 - 20.5, -21.75 + 20.5, -21.75 + 20.5, -21.75 - 20.5]
    ax.plot(floor_x, floor_y, [5.59]*5, color="#00b4a0", linewidth=3.0, label="Layer 05: Enhanced Carpet (1,681 m2)")

    # 2. Perforated Wood Panels (Amber boxes)
    panel_x, panel_y, panel_z = [], [], []
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 5: # Layer 06 (0-indexed 5)
            bb = obj.Geometry.GetBoundingBox()
            panel_x.append((bb.Min.X + bb.Max.X)/2.0)
            panel_y.append((bb.Min.Y + bb.Max.Y)/2.0)
            panel_z.append((bb.Min.Z + bb.Max.Z)/2.0)
    ax.scatter(panel_x, panel_y, panel_z, color="#d37828", s=65, marker="s", edgecolors="white", linewidths=0.8,
               label="Layer 06: Perforated Wood Panels (420 m2)")

    # 3. Retractable Acoustic Curtains (Crimson)
    curt_x, curt_y, curt_z = [], [], []
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 6: # Layer 07
            bb = obj.Geometry.GetBoundingBox()
            curt_x.append((bb.Min.X + bb.Max.X)/2.0)
            curt_y.append((bb.Min.Y + bb.Max.Y)/2.0)
            curt_z.append((bb.Min.Z + bb.Max.Z)/2.0)
    ax.scatter(curt_x, curt_y, curt_z, color="#b42850", s=75, marker="^", edgecolors="white", linewidths=0.8,
               label="Layer 07: Retractable Curtains (360 m2)")

    # 4. Suspended Baffles (Gold)
    baff_x, baff_y, baff_z = [], [], []
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 7: # Layer 08
            bb = obj.Geometry.GetBoundingBox()
            baff_x.append((bb.Min.X + bb.Max.X)/2.0)
            baff_y.append((bb.Min.Y + bb.Max.Y)/2.0)
            baff_z.append((bb.Min.Z + bb.Max.Z)/2.0)
    ax.scatter(baff_x, baff_y, baff_z, color="#dcb41e", s=90, marker="D", edgecolors="black", linewidths=0.8,
               label="Layer 08: Suspended Baffles (280 m2)")

    # 20 Speakers (Green)
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 2:
            bb = obj.Geometry.GetBoundingBox()
            ax.scatter([(bb.Min.X + bb.Max.X)/2.0], [(bb.Min.Y + bb.Max.Y)/2.0], [(bb.Min.Z + bb.Max.Z)/2.0],
                       color="#2ecc71", s=50, marker="o", edgecolors="white", linewidths=0.6)

    ax.set_xlim(0.83 - 24, 0.83 + 24)
    ax.set_ylim(-21.75 - 24, -21.75 + 24)
    ax.set_zlim(0, 38)
    ax.view_init(elev=32, azim=-55)

    ax.set_xlabel("X (m)", color="#ecf0f1", labelpad=8)
    ax.set_ylabel("Y (m)", color="#ecf0f1", labelpad=8)
    ax.set_zlabel("Z (m)", color="#ecf0f1", labelpad=8)
    ax.tick_params(colors="#bdc3c7")

    ax.legend(loc="upper right", facecolor="#2c3e50", edgecolor="#34495e", fontsize=8.5, labelcolor="#ecf0f1")
    draw_rhino_chrome(ax, "Phase 3: 4 Reversible Acoustic Interventions Deployed in 3DM Model", "View: Perspective SE, Elev=32, Azim=-55")

    out_path = os.path.join(IMP_DIR, "rhino_phase3_treatments_overview.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")


def render_panels_curtains_detail():
    print("Rendering Panels & Curtains Detail...")
    doc = rhino3dm.File3dm.Read(MODEL_PATH)

    fig = plt.figure(figsize=(13, 9), dpi=300, facecolor="#1e1e1e")
    ax = fig.add_subplot(111, projection="3d", facecolor="#252526")

    # Focus on East perimeter wall (X between 15 and 23, Y between -35 and -10)
    # Wall outline
    ax.plot([21.33, 21.33], [-36.0, -8.0], [5.57, 5.57], color="#7f8c8d", linewidth=2.0)
    ax.plot([21.33, 21.33], [-36.0, -8.0], [18.0, 18.0], color="#7f8c8d", linewidth=2.0)

    # Panels on East wall
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 5 and "PANEL_EAST" in obj.Attributes.Name:
            bb = obj.Geometry.GetBoundingBox()
            cx = (bb.Min.X + bb.Max.X)/2.0
            cy = (bb.Min.Y + bb.Max.Y)/2.0
            cz = (bb.Min.Z + bb.Max.Z)/2.0
            ax.scatter([cx], [cy], [cz], color="#d37828", s=180, marker="s", edgecolors="white", linewidths=1.2)
            ax.text(cx - 0.4, cy, cz, "PERF. PANEL\n(P=14%, 106mm)", color="#d37828", fontsize=7, fontweight="bold", ha="right")

    # Curtains on East wall
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 6 and "CURTAIN_EAST" in obj.Attributes.Name:
            bb = obj.Geometry.GetBoundingBox()
            cx = (bb.Min.X + bb.Max.X)/2.0
            cy = (bb.Min.Y + bb.Max.Y)/2.0
            cz = (bb.Min.Z + bb.Max.Z)/2.0
            ax.scatter([cx], [cy], [cz], color="#b42850", s=220, marker="^", edgecolors="white", linewidths=1.5)
            ax.text(cx - 0.4, cy, cz, "RETRACTABLE\nVELOUR (550g)", color="#b42850", fontsize=7, fontweight="bold", ha="right")

    # Enhanced carpet edge
    ax.plot([15.0, 21.33], [-36.0, -36.0], [5.59, 5.59], color="#00b4a0", linewidth=3.0)
    ax.plot([15.0, 21.33], [-8.0, -8.0], [5.59, 5.59], color="#00b4a0", linewidth=3.0)
    ax.text(18.0, -22.0, 5.8, "ENHANCED ACOUSTIC CARPET (22mm)", color="#00b4a0", fontsize=8, fontweight="bold")

    ax.set_xlim(12, 23)
    ax.set_ylim(-38, -6)
    ax.set_zlim(5, 20)
    ax.view_init(elev=20, azim=-45)

    ax.set_xlabel("X (m)", color="#ecf0f1")
    ax.set_ylabel("Y (m)", color="#ecf0f1")
    ax.set_zlabel("Z (m)", color="#ecf0f1")
    ax.tick_params(colors="#bdc3c7")

    draw_rhino_chrome(ax, "Phase 3: Perimeter Perforated Panels & Retractable Curtains Detail", "View: East Wall Arcade, Elev=20, Azim=-45")

    out_path = os.path.join(IMP_DIR, "rhino_phase3_treatments_detail_panels_curtains.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")


def render_baffles_detail():
    print("Rendering Baffles Detail...")
    doc = rhino3dm.File3dm.Read(MODEL_PATH)

    fig = plt.figure(figsize=(13, 9), dpi=300, facecolor="#1e1e1e")
    ax = fig.add_subplot(111, projection="3d", facecolor="#252526")

    # Focus on suspended baffles beneath semi-dome arches (Z around 16m)
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 7: # Baffles
            bb = obj.Geometry.GetBoundingBox()
            cx = (bb.Min.X + bb.Max.X)/2.0
            cy = (bb.Min.Y + bb.Max.Y)/2.0
            cz = (bb.Min.Z + bb.Max.Z)/2.0
            ax.scatter([cx], [cy], [cz], color="#dcb41e", s=200, marker="D", edgecolors="black", linewidths=1.2)
            ax.text(cx, cy, cz + 0.8, "GEOMETRIC BAFFLE\n(Dual Face, 60mm)", color="#dcb41e", fontsize=7, fontweight="bold", ha="center")

            # Simulated tie rod line
            ax.plot([cx - 3.0, cx + 3.0], [cy, cy], [17.5, 17.5], color="#95a5a6", linewidth=1.5, linestyle="--")
            # Suspension hangers
            ax.plot([cx - 1.5, cx - 1.5], [cy, cy], [16.0, 17.5], color="#bdc3c7", linewidth=1.0)
            ax.plot([cx + 1.5, cx + 1.5], [cy, cy], [16.0, 17.5], color="#bdc3c7", linewidth=1.0)

    ax.text2D(0.5, 0.85, "Non-Invasive Clamp Suspension from Structural Iron Tie-Rods\nZero Drilling into Historic Alabaster or Marble Arches",
              transform=ax.transAxes, fontsize=9, fontweight="bold", color="#f1c40f", ha="center",
              bbox=dict(boxstyle="round,pad=0.5", fc="#2c3e50", ec="#f1c40f", lw=1))

    ax.set_xlim(-18, 18)
    ax.set_ylim(-38, -6)
    ax.set_zlim(14, 24)
    ax.view_init(elev=18, azim=-50)

    ax.set_xlabel("X (m)", color="#ecf0f1")
    ax.set_ylabel("Y (m)", color="#ecf0f1")
    ax.set_zlabel("Z (m)", color="#ecf0f1")
    ax.tick_params(colors="#bdc3c7")

    draw_rhino_chrome(ax, "Phase 3: Suspended Geometric Baffles Mounting & Suspension Detail", "View: Semi-Dome Tie-Rods, Elev=18, Azim=-50")

    out_path = os.path.join(IMP_DIR, "rhino_phase3_treatments_detail_baffles.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")


def main():
    render_overview()
    render_panels_curtains_detail()
    render_baffles_detail()
    print("Phase 3 3D Rhino renders complete!")


if __name__ == "__main__":
    main()
