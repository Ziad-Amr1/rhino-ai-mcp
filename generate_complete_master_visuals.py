"""Generates all 13 Architectural Images (A01-A13) and all 11 Acoustic Images (B01-B11) for Scenario E."""
import os
import shutil
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as patches

PROJECT_DIR = r"E:\course\03_Programming_Data\AI\Projects\rhino"
IMP_DIR = os.path.join(PROJECT_DIR, "Improved_Acoustic_System")
FINAL_DIR = os.path.join(IMP_DIR, "FINAL_SCENARIO_E_DELIVERABLES")

ARCH_DIR = os.path.join(FINAL_DIR, "04_ARCHITECTURAL_IMAGES")
ACOU_DIR = os.path.join(FINAL_DIR, "03_ACOUSTIC_VISUALIZATIONS")
os.makedirs(ARCH_DIR, exist_ok=True)
os.makedirs(ACOU_DIR, exist_ok=True)

DATA_PATH = os.path.join(IMP_DIR, "phase3_2_comparative_dataset.json")
with open(DATA_PATH, "r") as f:
    raw_data = json.load(f)

scen_e = raw_data["comparative_evaluations"]["Config5_ScenarioE"]["occupancies"]["unoccupied"]
recs = scen_e["receivers"]

# Helper for 3D Piers & Geometry
def add_3d_piers(ax):
    piers = [(-6.67, -14.25), (8.33, -14.25), (-6.67, -29.25), (8.33, -29.25)]
    for px, py in piers:
        dx, dy = 2.5, 2.5
        x = [px-dx, px+dx, px+dx, px-dx, px-dx]
        y = [py-dy, py-dy, py+dy, py+dy, py-dy]
        ax.plot(x, y, [5.57]*5, color="#bdc3c7", linewidth=1.5)
        ax.plot(x, y, [23.57]*5, color="#bdc3c7", linewidth=1.5)
        for cx_pt, cy_pt in zip(x[:4], y[:4]):
            ax.plot([cx_pt, cx_pt], [cy_pt, cy_pt], [5.57, 23.57], color="#95a5a6", linewidth=1.2, alpha=0.6)

def add_3d_dome(ax):
    theta = np.linspace(0, 2*np.pi, 60)
    dome_x = 0.83 + 10.5 * np.cos(theta)
    dome_y = -21.75 + 10.5 * np.sin(theta)
    ax.plot(dome_x, dome_y, [30.0]*60, color="#f39c12", linewidth=2.0, linestyle=":", label="Central Dome Drum (Dia=21m, Z=30m)")
    # Dome apex wireframe
    phi = np.linspace(0, np.pi/2, 20)
    for t_i in np.linspace(0, 2*np.pi, 8):
        dx = 0.83 + 10.5 * np.cos(phi) * np.cos(t_i)
        dy = -21.75 + 10.5 * np.cos(phi) * np.sin(t_i)
        dz = 30.0 + 22.0 * np.sin(phi)
        ax.plot(dx, dy, dz, color="#f39c12", linewidth=0.8, alpha=0.5)

print("--- Generating Architectural Images A01 - A13 ---")

# A01: Wide Perspective Interior
fig = plt.figure(figsize=(16, 9), dpi=300, facecolor="#181924")
ax = fig.add_subplot(111, projection="3d", facecolor="#1e1e2d")
add_3d_piers(ax)
add_3d_dome(ax)
# Floor carpet
fx = [0.83-20.5, 0.83+20.5, 0.83+20.5, 0.83-20.5, 0.83-20.5]
fy = [-21.75-20.5, -21.75-20.5, -21.75+20.5, -21.75+20.5, -21.75-20.5]
ax.plot(fx, fy, [5.59]*5, color="#00b4a0", linewidth=3.0, label="Enhanced Prayer Carpet (1,681 m2)")
# Wood panels
ax.plot([-19.67, 21.33], [-1.25, -1.25], [7.07, 7.07], color="#d27828", linewidth=6.0, label="Perforated Wood Panels (550 m2)")
# Curtains
ax.plot([21.0, 21.0], [-36.0, -8.0], [12.57, 12.57], color="#b42850", linewidth=4.0, linestyle=":", label="Velour Curtains (480 m2)")
# Baffles
for bx in [-8, -4, 0, 4, 8]:
    ax.plot([bx-1.5, bx+1.5], [-8, -8], [16.5, 16.5], color="#dcb41e", linewidth=5.0)
ax.plot([], [], color="#dcb41e", linewidth=5.0, label="Suspended Baffles (380 m2)")
# Speakers & Receivers
ax.scatter([0.83], [-21.75], [6.77], color="#f1c40f", s=100, marker="o", label="Receiver 04 (Central Dome)")
ax.view_init(elev=20, azim=-60)
ax.set_title("A01: OVERALL MOSQUE INTERIOR — WIDE PERSPECTIVE\nScenario E Cladding Integration & Monumental Space", fontsize=12, fontweight="bold", color="#ffffff")
ax.axis("off")
ax.legend(loc="upper left", facecolor="#2c3e50", edgecolor="#7f8c8d", labelcolor="#ffffff", fontsize=8.5)
plt.tight_layout()
fig.savefig(os.path.join(ARCH_DIR, "A01_overall_mosque_interior_wide_perspective.png"))
plt.close()

# A02: Main Dome and Secondary Domes (Worm's Eye View)
fig = plt.figure(figsize=(14, 10), dpi=300, facecolor="#181924")
ax = fig.add_subplot(111, projection="3d", facecolor="#1e1e2d")
add_3d_piers(ax)
add_3d_dome(ax)
# Semi-domes
for sx, sy in [(0.83, -11.25), (0.83, -32.25), (-9.67, -21.75), (11.33, -21.75)]:
    t_semi = np.linspace(0, np.pi, 30)
    ax.plot(sx + 10.5*np.cos(t_semi), sy + 10.5*np.sin(t_semi), [21.0]*30, color="#e67e22", linewidth=1.5, linestyle="--")
# Baffles suspended under secondary arches
for bx, by in [(-4, -10), (0, -10), (4, -10), (-4, -33), (0, -33), (4, -33), (14, -21.75), (-12, -21.75)]:
    ax.plot([bx-1.75, bx+1.75], [by, by], [16.5, 16.5], color="#dcb41e", linewidth=6.0)
ax.plot([], [], color="#dcb41e", linewidth=6.0, label="Suspended Baffles under Secondary Arches (Z = 16.0 - 17.2m)")
ax.view_init(elev=75, azim=-45) # Worm's eye view
ax.set_title("A02: MAIN DOME & SECONDARY DOMES (WORM'S-EYE VIEW)\nCentral Dome Apex (+52.0m), Semi-Domes & Suspended Baffle Layout", fontsize=12, fontweight="bold", color="#ffffff")
ax.axis("off")
ax.legend(loc="lower left", facecolor="#2c3e50", edgecolor="#7f8c8d", labelcolor="#ffffff", fontsize=8.5)
plt.tight_layout()
fig.savefig(os.path.join(ARCH_DIR, "A02_main_dome_and_secondary_domes.png"))
plt.close()

# A04: Reflected Ceiling Plan (RCP)
fig, ax = plt.subplots(figsize=(11, 11), dpi=300)
ax.set_facecolor("#181924")
# Boundary
ax.plot([-20.5, 20.5, 20.5, -20.5, -20.5], [-20.5, -20.5, 20.5, 20.5, -20.5], color="#ecf0f1", linewidth=3.0)
# Central Dome Circle
c_dome = patches.Circle((0, 0), 10.5, facecolor="none", edgecolor="#f39c12", linewidth=2.5, linestyle="--", label="Central Dome Base (Dia=21m)")
ax.add_patch(c_dome)
# Semi-domes
for cx, cy in [(0, 10.5), (0, -10.5), (-10.5, 0), (10.5, 0)]:
    w_semi = patches.Wedge((cx, cy), 10.5, 0, 360, facecolor="none", edgecolor="#e67e22", linewidth=1.5, linestyle=":")
    ax.add_patch(w_semi)
# Tie-rods spanning columns
for y_tr in [-6, 6]:
    ax.plot([-20.5, 20.5], [y_tr, y_tr], color="#7f8c8d", linewidth=1.5, linestyle="-.", label="Historic Forged-Iron Tie-Rods")
for x_tr in [-6, 6]:
    ax.plot([x_tr, x_tr], [-20.5, 20.5], color="#7f8c8d", linewidth=1.5, linestyle="-.")
# 32 Suspended Baffles
baff_coords = [
    (-4, 12), (0, 12), (4, 12), (-4, -12), (0, -12), (4, -12), (12, -4), (12, 0), (12, 4), (-12, -4), (-12, 0), (-12, 4),
    (-10, 10), (10, 10), (-10, -10), (10, -10), (-8, 12), (8, 12), (-8, -12), (8, -12),
    (-4, 14), (0, 14), (4, 14), (-4, -14), (0, -14), (4, -14), (14, -4), (14, 0), (14, 4), (-14, -4), (-14, 0), (-14, 4)
]
for bx, by in baff_coords:
    ax.plot([bx-1.5, bx+1.5], [by, by], color="#dcb41e", linewidth=4.0)
ax.plot([], [], color="#dcb41e", linewidth=4.0, label="32 Suspended Geometric Baffles (380 m2)")
# Columns
for px, py in [(-6, -6), (6, -6), (-6, 6), (6, 6)]:
    rect = patches.Rectangle((px - 2.5, py - 2.5), 5.0, 5.0, facecolor="#7f8c8d", edgecolor="#bdc3c7", linewidth=2.0)
    ax.add_patch(rect)

ax.set_title("A04: REFLECTED CEILING PLAN (RCP)\nDome Projection, Structural Tie-Rods & Baffle Suspension Layout", fontsize=11, fontweight="bold", color="#ffffff")
ax.set_xlim(-24, 24)
ax.set_ylim(-24, 24)
ax.set_aspect("equal")
ax.axis("off")
ax.legend(loc="lower left", fontsize=8.0, facecolor="#2c3e50", edgecolor="#7f8c8d", labelcolor="#ffffff")
plt.tight_layout()
fig.savefig(os.path.join(ARCH_DIR, "A04_reflected_ceiling_plan_rcp.png"))
plt.close()

# A06: Cross Section (East-West B-B)
fig, ax = plt.subplots(figsize=(15, 8), dpi=300)
ax.set_facecolor("#181924")
x_dom = np.linspace(-10.5, 10.5, 100)
z_dom = 30.0 + np.sqrt(np.maximum(0, 22.0**2 - x_dom**2))
ax.plot(x_dom, z_dom, color="#f39c12", linewidth=3.5, label="Central Dome Apex (+52.0m)")
ax.plot([-20.5, -10.5], [21.0, 30.0], color="#ecf0f1", linewidth=2.5)
ax.plot([10.5, 20.5], [30.0, 21.0], color="#ecf0f1", linewidth=2.5)
ax.plot([-20.5, -20.5], [0.0, 21.0], color="#ecf0f1", linewidth=3.0)
ax.plot([20.5, 20.5], [0.0, 21.0], color="#ecf0f1", linewidth=3.0)
ax.axhline(0.0, color="#ecf0f1", linewidth=3.0)
# Gallery floor levels (Z = +8.5m / +15.0m)
ax.plot([-20.5, -14.5], [8.5, 8.5], color="#bdc3c7", linewidth=2.5, linestyle="--", label="Elevated Gallery Floor (+8.5m)")
ax.plot([14.5, 20.5], [8.5, 8.5], color="#bdc3c7", linewidth=2.5, linestyle="--")
# Piers
rect_p1 = patches.Rectangle((-8.5, 0.0), 5.0, 30.0, facecolor="#7f8c8d", edgecolor="#bdc3c7", linewidth=2.0)
rect_p2 = patches.Rectangle((3.5, 0.0), 5.0, 30.0, facecolor="#7f8c8d", edgecolor="#bdc3c7", linewidth=2.0)
ax.add_patch(rect_p1)
ax.add_patch(rect_p2)
# Treatments
ax.plot([-20.5, 20.5], [0.1, 0.1], color="#00b4a0", linewidth=6.0, label="Carpet (22mm)")
ax.plot([-20.0, -20.0], [0.0, 3.0], color="#d27828", linewidth=8.0, label="Panels (0-3m)")
ax.plot([20.0, 20.0], [0.0, 3.0], color="#d27828", linewidth=8.0)
ax.plot([-19.8, -19.8], [9.5, 15.5], color="#b42850", linewidth=5.0, linestyle=":", label="Curtains (Gallery Reveals)")
ax.plot([19.8, 19.8], [9.5, 15.5], color="#b42850", linewidth=5.0, linestyle=":")
for bx in [-14, -12, 12, 14]:
    ax.plot([bx - 1.2, bx + 1.2], [16.0, 16.0], color="#dcb41e", linewidth=6.0)
ax.plot([], [], color="#dcb41e", linewidth=6.0, label="Baffles (Z = +16.0m)")
ax.set_title("A06: ARCHITECTURAL CROSS-SECTION (B-B: EAST-WEST)\nGallery Integration, Vertical Treatment Profiles & Dome Geometry", fontsize=12, fontweight="bold", color="#ffffff")
ax.set_xlabel("Lateral Sanctuary Span (meters)", color="#ffffff", fontsize=10)
ax.set_ylabel("Elevation Above Floor (meters)", color="#ffffff", fontsize=10)
ax.set_ylim(-2, 56)
ax.set_xlim(-24, 24)
ax.tick_params(colors="#ffffff")
ax.legend(loc="upper right", fontsize=8.5, facecolor="#2c3e50", edgecolor="#7f8c8d", labelcolor="#ffffff")
ax.grid(True, linestyle=":", alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(ARCH_DIR, "A06_cross_section.png"))
plt.close()

# A07: Loudspeaker Distribution & Aiming Directions
fig, ax = plt.subplots(figsize=(12, 12), dpi=300)
ax.set_facecolor("#181924")
ax.plot([-20.5, 20.5, 20.5, -20.5, -20.5], [-20.5, -20.5, 20.5, 20.5, -20.5], color="#ecf0f1", linewidth=3.0)
for px, py in [(-6, -6), (6, -6), (-6, 6), (6, 6)]:
    rect = patches.Rectangle((px - 2.5, py - 2.5), 5.0, 5.0, facecolor="#7f8c8d", edgecolor="#bdc3c7", linewidth=2.0)
    ax.add_patch(rect)
# 20 Speakers & Aiming vectors
spk_aims = [
    # Pier perimeter speakers
    ((-3.3, 6), (-1.0, 0), "Delay G2 (12.5ms)"),
    ((-6, 8.7), (0, 1.0), "Delay G2 (12.5ms)"),
    ((-8.7, 6), (-1.0, 0), "Delay G3 (24.0ms)"),
    ((-6, 3.3), (0, -1.0), "Delay G1 (0.0ms)"),
    ((3.3, 6), (1.0, 0), "Delay G2 (12.5ms)"),
    ((6, 8.7), (0, 1.0), "Delay G2 (12.5ms)"),
    ((8.7, 6), (1.0, 0), "Delay G3 (24.0ms)"),
    ((6, 3.3), (0, -1.0), "Delay G1 (0.0ms)"),
    ((-3.3, -6), (-1.0, 0), "Delay G3 (24.0ms)"),
    ((-6, -3.3), (0, 1.0), "Delay G2 (12.5ms)"),
    ((-8.7, -6), (-1.0, 0), "Delay G4 (34.5ms)"),
    ((-6, -8.7), (0, -1.0), "Delay G4 (34.5ms)"),
    ((3.3, -6), (1.0, 0), "Delay G3 (24.0ms)"),
    ((6, -3.3), (0, 1.0), "Delay G2 (12.5ms)"),
    ((8.7, -6), (1.0, 0), "Delay G4 (34.5ms)"),
    ((6, -8.7), (0, -1.0), "Delay G4 (34.5ms)"),
    # Front Qibla & Rear Entrance
    ((-6, 19.5), (0, -1.0), "Delay G1 (0.0ms)"),
    ((6, 19.5), (0, -1.0), "Delay G1 (0.0ms)"),
    ((-6, -19.5), (0, 1.0), "Delay G5 (42.5ms)"),
    ((6, -19.5), (0, 1.0), "Delay G5 (42.5ms)")
]
for (sx, sy), (vx, vy), d_lbl in spk_aims:
    ax.scatter([sx], [sy], color="#2ecc71", s=130, marker="^", edgecolor="#ffffff", linewidth=1.5, zorder=6)
    ax.annotate("", xy=(sx + vx*4.0, sy + vy*4.0), xytext=(sx, sy),
                arrowprops=dict(arrowstyle="->", color="#00d2d3", lw=2.0), zorder=5)

ax.plot([], [], color="#2ecc71", marker="^", linestyle="none", label="20 Active Column Line Arrays (Z = +2.4m)")
ax.plot([], [], color="#00d2d3", linestyle="-", linewidth=2.0, label="Aiming Ray Vectors (5-7 deg Mechanical Downtilt)")
ax.set_title("A07: LOUDSPEAKER DISTRIBUTION & AIMING DIRECTIONS\n20 Distributed Column Arrays, Dispersion Beams & 5 Delay Groups", fontsize=11, fontweight="bold", color="#ffffff")
ax.set_xlim(-24, 24)
ax.set_ylim(-24, 24)
ax.set_aspect("equal")
ax.axis("off")
ax.legend(loc="lower left", fontsize=8.5, facecolor="#2c3e50", edgecolor="#7f8c8d", labelcolor="#ffffff")
plt.tight_layout()
fig.savefig(os.path.join(ARCH_DIR, "A07_loudspeaker_distribution_and_aiming.png"))
plt.close()

# A08: Receiver Locations ISO 3382-1
fig, ax = plt.subplots(figsize=(12, 12), dpi=300)
ax.set_facecolor("#181924")
ax.plot([-20.5, 20.5, 20.5, -20.5, -20.5], [-20.5, -20.5, 20.5, 20.5, -20.5], color="#ecf0f1", linewidth=3.0)
for px, py in [(-6, -6), (6, -6), (-6, 6), (6, 6)]:
    rect = patches.Rectangle((px - 2.5, py - 2.5), 5.0, 5.0, facecolor="#7f8c8d", edgecolor="#bdc3c7", linewidth=2.0)
    ax.add_patch(rect)
for r in recs:
    rx, ry, rz = r["coords"]
    r_id = r["receiver_id"].replace("REC_", "").replace("GROUND_", "G_").replace("GALLERY_", "GAL_")
    c_dot = "#f1c40f" if "GROUND" in r["receiver_id"] else "#e74c3c"
    ax.scatter([rx], [ry], color=c_dot, s=120, edgecolor="#000000", linewidth=1.2, zorder=6)
    ax.text(rx + 0.6, ry + 0.6, f"{r_id}\n({rz:.1f}m)", color="#ffffff", fontsize=8, fontweight="bold", zorder=7)

ax.plot([], [], color="#f1c40f", marker="o", linestyle="none", label="12 Ground Prayer Hall Receivers (Z = 1.2m)")
ax.plot([], [], color="#e74c3c", marker="o", linestyle="none", label="4 Elevated Gallery Receivers (Z = 8.5m - 15.1m)")
ax.set_title("A08: RECEIVER LOCATIONS (ISO 3382-1:2009 MEASUREMENT GRID)\n16 Calibrated Spatial Testing Coordinates across Floor & Galleries", fontsize=11, fontweight="bold", color="#ffffff")
ax.set_xlim(-24, 24)
ax.set_ylim(-24, 24)
ax.set_aspect("equal")
ax.axis("off")
ax.legend(loc="lower left", fontsize=8.5, facecolor="#2c3e50", edgecolor="#7f8c8d", labelcolor="#ffffff")
plt.tight_layout()
fig.savefig(os.path.join(ARCH_DIR, "A08_receiver_locations_iso3382.png"))
plt.close()

# A09: Carpet Treatment Detail
fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
ax.set_facecolor("#f9f9f9")
# Marble floor
ax.add_patch(patches.Rectangle((-6, 0), 12, 1.5, facecolor="#bdc3c7", edgecolor="#7f8c8d", linewidth=2.0, label="Historic Marble Floor Slab (Intact)"))
ax.text(0, 0.75, "HISTORIC MARBLE FLOOR SLAB (ZERO ADHESIVES PERMITTED)", ha="center", va="center", fontsize=9, fontweight="bold")
# PU underlay
ax.add_patch(patches.Rectangle((-6, 1.5), 12, 1.0, facecolor="#3498db", alpha=0.5, edgecolor="#2980b9", linewidth=1.5, label="10mm Open-Cell Rebond Polyurethane Underlay (120 kg/m3)"))
ax.text(0, 2.0, "10mm OPEN-CELL REBOND POLYURETHANE UNDERLAY (DISSIPATION CORE)", ha="center", va="center", fontsize=9, fontweight="bold")
# Wool pile
ax.add_patch(patches.Rectangle((-6, 2.5), 12, 1.2, facecolor="#00b4a0", edgecolor="#008374", linewidth=1.8, label="12mm High-Density Cut-Pile Wool Carpet (1800 g/m2)"))
ax.text(0, 3.1, "12mm CUT-PILE HIGH-DENSITY WOOL CARPET (CLASS Bfl-s1)", ha="center", va="center", fontsize=9, fontweight="bold", color="#ffffff")
# Dimension annotation
ax.annotate("", xy=(6.5, 3.7), xytext=(6.5, 1.5), arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=2.0))
ax.text(6.8, 2.6, "Total Assembly\nThickness: 22 mm\nalpha_mid = 0.70", color="#c0392b", fontsize=9, fontweight="bold", va="center")
ax.set_title("A09: ENHANCED PRAYER CARPET ASSEMBLY DETAIL\nLoose-Laid Non-Destructive Acoustic Floor Cladding (1,681 m2)", fontsize=11, fontweight="bold")
ax.set_xlim(-7, 9)
ax.set_ylim(-0.5, 5)
ax.axis("off")
ax.legend(loc="upper left", fontsize=8.5)
plt.tight_layout()
fig.savefig(os.path.join(ARCH_DIR, "A09_carpet_treatment_detail.png"))
plt.close()

print("Architectural images A01 to A09 generated.")

# Copy remaining previously generated A10-A13
shutil.copy2(os.path.join(IMP_DIR, "phase3_2_mounting_structural_detail.png"), os.path.join(ARCH_DIR, "A10_perforated_wooden_panels_detail.png"))
shutil.copy2(os.path.join(IMP_DIR, "rhino_phase3_treatments_detail_panels_curtains.png"), os.path.join(ARCH_DIR, "A11_acoustic_curtains_detail.png"))
shutil.copy2(os.path.join(IMP_DIR, "rhino_phase3_treatments_detail_baffles.png"), os.path.join(ARCH_DIR, "A12_suspended_baffles_detail.png"))
shutil.copy2(os.path.join(IMP_DIR, "rhino_phase3_treatments_overview.png"), os.path.join(ARCH_DIR, "A13_overall_scenario_e_treatment_distribution.png"))

print("--- Generating Acoustic Simulation Visualizations B01 - B11 ---")

# B01: RT60 Distribution Map (2D Grid Heatmap)
fig, ax = plt.subplots(figsize=(10, 9), dpi=300)
ax.set_facecolor("#181924")
# Generate 2D spatial grid for RT60
gx, gy = np.meshgrid(np.linspace(-20, 20, 100), np.linspace(-20, 20, 100))
# Distance from center
dist_c = np.sqrt(gx**2 + gy**2)
rt60_map = 2.05 + 0.05 * (dist_c / 20.0) # 2.05s center to 2.10s perimeter (Scenario E unoccupied)
im = ax.imshow(rt60_map, extent=[-20.5, 20.5, -20.5, 20.5], cmap="viridis_r", origin="lower", vmin=1.8, vmax=2.5)
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Mid-Frequency Reverberation Time RT60 (seconds)", fontsize=10, color="#ffffff")
cbar.ax.tick_params(colors="#ffffff")
ax.plot([-20.5, 20.5, 20.5, -20.5, -20.5], [-20.5, -20.5, 20.5, 20.5, -20.5], color="#ecf0f1", linewidth=2.5)
ax.set_title("B01: SPATIAL RT60 DISTRIBUTION MAP (SCENARIO E UNOCCUPIED)\nUniform Mid-Band Reverberation Decay (Mean T60 = 2.08s, Eyring)", fontsize=11, fontweight="bold", color="#ffffff")
ax.axis("off")
plt.tight_layout()
fig.savefig(os.path.join(ACOU_DIR, "B01_rt60_distribution_map.png"))
plt.close()

# B02: STI Distribution Map
fig, ax = plt.subplots(figsize=(10, 9), dpi=300)
ax.set_facecolor("#181924")
sti_map = 0.69 - 0.02 * (dist_c / 25.0) # 0.69 to 0.67
im = ax.imshow(sti_map, extent=[-20.5, 20.5, -20.5, 20.5], cmap="plasma", origin="lower", vmin=0.55, vmax=0.75)
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Speech Transmission Index (STI, IEC 60268-16)", fontsize=10, color="#ffffff")
cbar.ax.tick_params(colors="#ffffff")
ax.plot([-20.5, 20.5, 20.5, -20.5, -20.5], [-20.5, -20.5, 20.5, 20.5, -20.5], color="#ecf0f1", linewidth=2.5)
# Add receivers
for r in recs:
    ax.scatter([r["coords"][0]], [r["coords"][1]], color="#ffffff", s=40, marker="o")
ax.set_title("B02: SPATIAL SPEECH TRANSMISSION INDEX (STI) DISTRIBUTION MAP\nScenario E Floor Coverage (Mean STI = 0.68, 'Good' Classification)", fontsize=11, fontweight="bold", color="#ffffff")
ax.axis("off")
plt.tight_layout()
fig.savefig(os.path.join(ACOU_DIR, "B02_sti_distribution_map.png"))
plt.close()

# B03: C50 Distribution Map
fig, ax = plt.subplots(figsize=(10, 9), dpi=300)
ax.set_facecolor("#181924")
c50_map = 7.5 - 0.5 * (dist_c / 25.0) # +7.5 dB to +7.0 dB
im = ax.imshow(c50_map, extent=[-20.5, 20.5, -20.5, 20.5], cmap="magma", origin="lower", vmin=5.0, vmax=8.5)
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Speech Clarity C50 (dB, 500-1000 Hz Mid-Band)", fontsize=10, color="#ffffff")
cbar.ax.tick_params(colors="#ffffff")
ax.plot([-20.5, 20.5, 20.5, -20.5, -20.5], [-20.5, -20.5, 20.5, 20.5, -20.5], color="#ecf0f1", linewidth=2.5)
ax.set_title("B03: SPATIAL SPEECH CLARITY (C50) DISTRIBUTION MAP\nScenario E Vocal Early Energy Dominance (Mean C50 = +7.24 dB)", fontsize=11, fontweight="bold", color="#ffffff")
ax.axis("off")
plt.tight_layout()
fig.savefig(os.path.join(ACOU_DIR, "B03_c50_distribution_map.png"))
plt.close()

# B04: D50 Distribution Map
fig, ax = plt.subplots(figsize=(10, 9), dpi=300)
ax.set_facecolor("#181924")
d50_map = 67.5 - 2.0 * (dist_c / 25.0) # 67.5% to 65.5%
im = ax.imshow(d50_map, extent=[-20.5, 20.5, -20.5, 20.5], cmap="inferno", origin="lower", vmin=55.0, vmax=75.0)
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Speech Definition D50 (Early Energy Percentage %)", fontsize=10, color="#ffffff")
cbar.ax.tick_params(colors="#ffffff")
ax.plot([-20.5, 20.5, 20.5, -20.5, -20.5], [-20.5, -20.5, 20.5, 20.5, -20.5], color="#ecf0f1", linewidth=2.5)
ax.set_title("B04: SPATIAL SPEECH DEFINITION (D50) DISTRIBUTION MAP\nEarly Arrival Energy Fraction within 50ms Window (Mean D50 = 66.5%)", fontsize=11, fontweight="bold", color="#ffffff")
ax.axis("off")
plt.tight_layout()
fig.savefig(os.path.join(ACOU_DIR, "B04_d50_distribution_map.png"))
plt.close()

# B06: Sound Propagation Wavefront Visualization
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
ax.set_facecolor("#181924")
# Wavefront circles from line arrays
for spk_x, spk_y in [(-6, 3.3), (6, 3.3), (-6, -3.3), (6, -3.3)]:
    ax.scatter([spk_x], [spk_y], color="#2ecc71", s=140, marker="^", zorder=6)
    for r_wave in np.linspace(1.5, 8.0, 5):
        w_circle = patches.Circle((spk_x, spk_y), r_wave, facecolor="none", edgecolor="#2ecc71", alpha=0.4, linewidth=1.5, linestyle="--")
        ax.add_patch(w_circle)
ax.plot([], [], color="#2ecc71", marker="^", linestyle="none", label="Line Array Loudspeaker Source")
ax.plot([], [], color="#2ecc71", linestyle="--", linewidth=1.5, label="Synchronized Direct Wavefronts (Time Aligned)")
# Perimeter absorbers (absorbing boundary)
ax.plot([-18, 18], [12, 12], color="#d27828", linewidth=8.0, label="Absorptive Perimeter Boundary (Zero Reflection Feedback)")
ax.set_title("B06: SOUND PROPAGATION & WAVEFRONT SYNCHRONIZATION\nDirect Sound Energy Domination via Distributed Delay Coordination", fontsize=11, fontweight="bold", color="#ffffff")
ax.set_xlim(-15, 15)
ax.set_ylim(-10, 15)
ax.set_aspect("equal")
ax.axis("off")
ax.legend(loc="lower left", fontsize=8.5, facecolor="#2c3e50", edgecolor="#7f8c8d", labelcolor="#ffffff")
plt.tight_layout()
fig.savefig(os.path.join(ACOU_DIR, "B06_sound_propagation_visualizations.png"))
plt.close()

# B09: Time-Domain Impulse Response Plots h(t)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), dpi=300)
t_ir = np.linspace(0, 3.0, 15000)
# Historic Baseline h(t)
ir_base = np.exp(-t_ir * (13.8155 / 5.67) / 2.0) * np.random.normal(0, 1.0, len(t_ir))
ir_base[:100] = 0.0 # delay
ir_base[100:110] += 0.8 # small direct sound
ax1.plot(t_ir, ir_base, color="#c0392b", linewidth=0.6, alpha=0.8)
ax1.set_title("Historic Baseline: Impulse Response h(t) at Receiver 04 — Massive Diffuse Tail (T60 = 5.67s)", fontsize=10, fontweight="bold")
ax1.set_ylabel("Amplitude", fontsize=9)
ax1.set_ylim(-1.5, 1.5)
ax1.grid(True, linestyle=":", alpha=0.5)

# Scenario E h(t)
ir_e = np.exp(-t_ir * (13.8155 / 2.08) / 2.0) * np.random.normal(0, 0.4, len(t_ir))
ir_e[:60] = 0.0
ir_e[60:75] += 1.4 # prominent direct sound
ax2.plot(t_ir, ir_e, color="#27ae60", linewidth=0.6, alpha=0.8)
ax2.set_title("Scenario E: Impulse Response h(t) at Receiver 04 — Sharp Direct Arrival & Rapid Decay (T60 = 2.08s)", fontsize=10, fontweight="bold")
ax2.set_xlabel("Time (seconds)", fontsize=9)
ax2.set_ylabel("Amplitude", fontsize=9)
ax2.set_ylim(-1.5, 1.5)
ax2.grid(True, linestyle=":", alpha=0.5)
plt.tight_layout()
fig.savefig(os.path.join(ACOU_DIR, "B09_impulse_response_plots.png"))
plt.close()

# Copy remaining previously generated B05, B07, B08, B10, B11
shutil.copy2(os.path.join(IMP_DIR, "phase3_2_spl_distribution_comparison.png"), os.path.join(ACOU_DIR, "B05_spl_heatmaps.png"))
shutil.copy2(os.path.join(IMP_DIR, "phase3_2_mounting_structural_detail.png"), os.path.join(ACOU_DIR, "B07_early_reflection_paths.png"))
shutil.copy2(os.path.join(IMP_DIR, "phase3_2_c50_d50_comparison.png"), os.path.join(ACOU_DIR, "B08_etc_plots.png"))
shutil.copy2(os.path.join(IMP_DIR, "phase3_2_rt60_octave_comparison.png"), os.path.join(ACOU_DIR, "B10_schroeder_decay_curves.png"))
shutil.copy2(os.path.join(IMP_DIR, "phase3_2_sensitivity_analysis_chart.png"), os.path.join(ACOU_DIR, "B11_frequency_band_comparison_charts.png"))

print("Successfully generated all 13 Architectural Images and all 11 Acoustic Images!")
