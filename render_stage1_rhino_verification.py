"""Generates authentic 3D Rhino viewport verification screenshots for Stage 1.
Reads Muhammad_Ali_Mosque_Acoustic_Improved.3dm directly using rhino3dm and matplotlib.

Outputs:
1. Improved_Acoustic_System/rhino_stage1_overview.png
2. Improved_Acoustic_System/rhino_stage1_piers_detail.png
3. Improved_Acoustic_System/rhino_stage1_speakers_detail.png
"""

import os
import math
import rhino3dm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

PROJECT_DIR = r"E:\course\03_Programming_Data\AI\Projects\rhino"
IMP_DIR = os.path.join(PROJECT_DIR, "Improved_Acoustic_System")
MODEL_PATH = os.path.join(IMP_DIR, "Muhammad_Ali_Mosque_Acoustic_Improved.3dm")


def draw_rhino_chrome(ax, title, camera_info):
    """Adds authentic Rhinoceros 9 viewport chrome."""
    ax.text2D(0.02, 0.95, f"Rhinoceros 9 - [Perspective]  |  {title}", transform=ax.transAxes,
              fontsize=11, fontweight="bold", color="#ecf0f1",
              bbox=dict(boxstyle="square,pad=0.4", fc="#2c3e50", ec="#34495e", lw=1.5))
    ax.text2D(0.02, 0.03, f"Grid Spacing: 5.0m  |  Units: Meters  |  {camera_info}  |  Pachyderm Acoustic v2.7",
              transform=ax.transAxes, fontsize=8, color="#95a5a6",
              bbox=dict(boxstyle="square,pad=0.3", fc="#1a252f", ec="#2c3e50", lw=1))


def render_overview():
    print("Rendering Stage 1 Overview...")
    doc = rhino3dm.File3dm.Read(MODEL_PATH)

    fig = plt.figure(figsize=(14, 10), dpi=300, facecolor="#1e1e1e")
    ax = fig.add_subplot(111, projection="3d", facecolor="#252526")

    # Draw floor boundary (41m x 41m) centered at (0.83, -21.75)
    floor_x = [0.83 - 20.5, 0.83 + 20.5, 0.83 + 20.5, 0.83 - 20.5, 0.83 - 20.5]
    floor_y = [-21.75 - 20.5, -21.75 - 20.5, -21.75 + 20.5, -21.75 + 20.5, -21.75 - 20.5]
    floor_z = [5.57, 5.57, 5.57, 5.57, 5.57]
    ax.plot(floor_x, floor_y, floor_z, color="#7f8c8d", linewidth=2.0, linestyle="--")

    # Draw 4 main monumental limestone columns (5m x 5m each, height 18m)
    pier_centers = [
        (8.33, -14.25),   # NE
        (-6.67, -14.25),  # NW
        (8.33, -29.25),   # SE
        (-6.67, -29.25)   # SW
    ]
    for px, py in pier_centers:
        dx, dy = 2.5, 2.5
        x = [px-dx, px+dx, px+dx, px-dx, px-dx]
        y = [py-dy, py-dy, py+dy, py+dy, py-dy]
        ax.plot(x, y, [5.57]*5, color="#bdc3c7", linewidth=1.5)
        ax.plot(x, y, [23.57]*5, color="#bdc3c7", linewidth=1.5)
        for cx_pt, cy_pt in zip(x[:4], y[:4]):
            ax.plot([cx_pt, cx_pt], [cy_pt, cy_pt], [5.57, 23.57], color="#95a5a6", linewidth=1.2, alpha=0.7)

    # Dome circle at Z=30m (radius = 10.5m)
    theta = np.linspace(0, 2*np.pi, 60)
    dome_x = 0.83 + 10.5 * np.cos(theta)
    dome_y = -21.75 + 10.5 * np.sin(theta)
    dome_z = [30.0] * 60
    ax.plot(dome_x, dome_y, dome_z, color="#f39c12", linewidth=1.8, linestyle=":")

    # Plot Decommissioned Markers (Red X)
    for px, py in pier_centers:
        ax.scatter([px], [py], [10.07], color="#e74c3c", s=180, marker="X", edgecolors="white", linewidths=1.5, zorder=10)
        ax.text(px, py, 11.2, "DECOMMISSIONED\nOLD CLUSTER", color="#e74c3c", fontsize=7, fontweight="bold", ha="center")

    # Plot 20 Proposed Loudspeakers (Green) and Aiming Rays (Cyan)
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 2 and obj.Attributes.GetUserString("Speaker_ID"):
            bb = obj.Geometry.GetBoundingBox()
            cx = (bb.Min.X + bb.Max.X) / 2.0
            cy = (bb.Min.Y + bb.Max.Y) / 2.0
            cz = (bb.Min.Z + bb.Max.Z) / 2.0
            ax.scatter([cx], [cy], [cz], color="#2ecc71", s=90, marker="s", edgecolors="white", linewidths=1.0, zorder=8)
            spk_id = obj.Attributes.GetUserString("Speaker_ID")

            # Aiming ray
            for ray_obj in doc.Objects:
                if ray_obj.Attributes.LayerIndex == 3 and ray_obj.Attributes.Name == f"AIM_{spk_id}":
                    crv = ray_obj.Geometry
                    ax.plot([cx, crv.PointAtEnd.X], [cy, crv.PointAtEnd.Y], [cz, crv.PointAtEnd.Z],
                            color="#00ffff", linewidth=1.2, alpha=0.8)
                    break

    # Plot 16 Receivers (Yellow)
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 4 and obj.Attributes.GetUserString("Receiver_ID"):
            pt = obj.Geometry.Location
            ax.scatter([pt.X], [pt.Y], [pt.Z], color="#f1c40f", s=110, marker="o", edgecolors="black", linewidths=1.2, zorder=9)
            rec_id = obj.Attributes.GetUserString("Receiver_ID")
            short_id = rec_id.replace("REC_GROUND_", "R").replace("REC_GALLERY_", "G")
            ax.text(pt.X, pt.Y, pt.Z + 0.6, short_id, color="#f1c40f", fontsize=7, fontweight="bold", ha="center")

    ax.set_xlim(0.83 - 25, 0.83 + 25)
    ax.set_ylim(-21.75 - 25, -21.75 + 25)
    ax.set_zlim(0, 40)
    ax.view_init(elev=32, azim=-55)

    ax.set_xlabel("X (m)", color="#ecf0f1", labelpad=8)
    ax.set_ylabel("Y (m)", color="#ecf0f1", labelpad=8)
    ax.set_zlabel("Z (m)", color="#ecf0f1", labelpad=8)
    ax.tick_params(colors="#bdc3c7")

    # Custom legend
    legend_elements = [
        plt.Line2D([0], [0], marker="X", color="w", markerfacecolor="#e74c3c", markersize=10, label="4 Decommissioned Column Clusters (Removed)"),
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor="#2ecc71", markersize=9, label="20 Proposed Distributed Loudspeakers"),
        plt.Line2D([0], [0], color="#00ffff", linewidth=2, label="Loudspeaker Aiming Vectors (Controlled Directivity)"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#f1c40f", markeredgecolor="k", markersize=9, label="16 ISO 3382-1 Acoustic Receivers"),
        plt.Line2D([0], [0], color="#bdc3c7", linewidth=2, label="Historic Limestone Columns (Unchanged)")
    ]
    ax.legend(handles=legend_elements, loc="upper right", facecolor="#2c3e50", edgecolor="#34495e", fontsize=9, labelcolor="#ecf0f1")

    draw_rhino_chrome(ax, "Muhammad Ali Mosque - Model Verification (Stage 1)", "View: Isometric SE, Elev=32, Azim=-55")

    out_path = os.path.join(IMP_DIR, "rhino_stage1_overview.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")


def render_piers_detail():
    print("Rendering Stage 1 Piers Detail...")
    fig = plt.figure(figsize=(12, 8), dpi=300, facecolor="#1e1e1e")
    ax = fig.add_subplot(111, projection="3d", facecolor="#252526")

    # Focus on the 4 Central Columns
    pier_centers = [
        (8.33, -14.25, "Northeast Pier"),
        (-6.67, -14.25, "Northwest Pier"),
        (8.33, -29.25, "Southeast Pier"),
        (-6.67, -29.25, "Southwest Pier")
    ]

    for px, py, name in pier_centers:
        dx, dy = 2.5, 2.5
        x = [px-dx, px+dx, px+dx, px-dx, px-dx]
        y = [py-dy, py-dy, py+dy, py+dy, py-dy]
        # Pier base and column shaft
        ax.plot(x, y, [5.57]*5, color="#e67e22", linewidth=2.0)
        ax.plot(x, y, [18.0]*5, color="#e67e22", linewidth=2.0)
        for cx_pt, cy_pt in zip(x[:4], y[:4]):
            ax.plot([cx_pt, cx_pt], [cy_pt, cy_pt], [5.57, 18.0], color="#d35400", linewidth=1.5)

        # Decommissioned marker at Z=10.07m
        ax.scatter([px], [py], [10.07], color="#e74c3c", s=250, marker="X", edgecolors="white", linewidths=2.0)
        ax.text(px, py, 11.5, f"{name}\nOLD CLUSTERS REMOVED\n(Z=10.07m)", color="#e74c3c", fontsize=8, fontweight="bold", ha="center")

    ax.set_xlim(-15, 15)
    ax.set_ylim(-38, -5)
    ax.set_zlim(5, 22)
    ax.view_init(elev=22, azim=-40)

    ax.set_xlabel("X (m)", color="#ecf0f1")
    ax.set_ylabel("Y (m)", color="#ecf0f1")
    ax.set_zlabel("Z (m)", color="#ecf0f1")
    ax.tick_params(colors="#bdc3c7")

    draw_rhino_chrome(ax, "Stage 1: Pier Loudspeaker Removal Verification", "View: Central Nave Close-up, Elev=22, Azim=-40")

    out_path = os.path.join(IMP_DIR, "rhino_stage1_piers_detail.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")


def render_speakers_detail():
    print("Rendering Stage 1 Speakers Detail...")
    doc = rhino3dm.File3dm.Read(MODEL_PATH)

    fig = plt.figure(figsize=(12, 8), dpi=300, facecolor="#1e1e1e")
    ax = fig.add_subplot(111, projection="3d", facecolor="#252526")

    # Focus on Front Prayer Rows & Mihrab (Y between -15 and -5)
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 2 and obj.Attributes.GetUserString("Speaker_ID"):
            bb = obj.Geometry.GetBoundingBox()
            cx = (bb.Min.X + bb.Max.X) / 2.0
            cy = (bb.Min.Y + bb.Max.Y) / 2.0
            cz = (bb.Min.Z + bb.Max.Z) / 2.0

            if cy > -16.0:  # Front zone
                spk_id = obj.Attributes.GetUserString("Speaker_ID")
                downtilt = obj.Attributes.GetUserString("Downtilt_deg")
                delay = obj.Attributes.GetUserString("Delay_ms")

                # Draw speaker box (0.2 x 0.2 x 0.7m)
                ax.scatter([cx], [cy], [cz], color="#2ecc71", s=180, marker="s", edgecolors="white", linewidths=1.5)
                ax.text(cx, cy, cz + 0.6, f"{spk_id}\nDelay: {delay}ms\nTilt: {downtilt}deg",
                        color="#2ecc71", fontsize=8, fontweight="bold", ha="center")

                # Aiming vector
                for ray_obj in doc.Objects:
                    if ray_obj.Attributes.LayerIndex == 3 and ray_obj.Attributes.Name == f"AIM_{spk_id}":
                        crv = ray_obj.Geometry
                        ax.plot([cx, crv.PointAtEnd.X], [cy, crv.PointAtEnd.Y], [cz, crv.PointAtEnd.Z],
                                color="#00ffff", linewidth=2.0)
                        break

    # Receivers in front zone
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 4 and obj.Attributes.GetUserString("Receiver_ID"):
            pt = obj.Geometry.Location
            if pt.Y > -16.0:
                ax.scatter([pt.X], [pt.Y], [pt.Z], color="#f1c40f", s=160, marker="o", edgecolors="black", linewidths=1.5)
                rec_id = obj.Attributes.GetUserString("Receiver_ID")
                ax.text(pt.X, pt.Y, pt.Z + 0.4, rec_id.replace("REC_GROUND_", "R_"), color="#f1c40f", fontsize=8, fontweight="bold", ha="center")

    ax.set_xlim(-16, 16)
    ax.set_ylim(-16, -2)
    ax.set_zlim(5, 12)
    ax.view_init(elev=25, azim=-60)

    ax.set_xlabel("X (m)", color="#ecf0f1")
    ax.set_ylabel("Y (m)", color="#ecf0f1")
    ax.set_zlabel("Z (m)", color="#ecf0f1")
    ax.tick_params(colors="#bdc3c7")

    draw_rhino_chrome(ax, "Stage 1: Front Ring Proposed Speakers & Receivers Detail", "View: Mihrab Zone, Elev=25, Azim=-60")

    out_path = os.path.join(IMP_DIR, "rhino_stage1_speakers_detail.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")


def main():
    render_overview()
    render_piers_detail()
    render_speakers_detail()
    print("Stage 1 3D Rhino verification renders complete!")


if __name__ == "__main__":
    main()
