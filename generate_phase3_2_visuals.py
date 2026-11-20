"""Generates all Phase 3.2 comparison charts and architectural visualizations."""
import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_DIR = r"E:\course\03_Programming_Data\AI\Projects\rhino"
IMP_DIR = os.path.join(PROJECT_DIR, "Improved_Acoustic_System")
DATA_PATH = os.path.join(IMP_DIR, "phase3_2_comparative_dataset.json")

with open(DATA_PATH, "r") as f:
    d = json.load(f)

comp = d["comparative_evaluations"]
sens = d["sensitivity_analysis"]

octaves = [63, 125, 250, 500, 1000, 2000, 4000, 8000]
cfg_keys = [
    "Config1_HistoricBaseline",
    "Config2_Phase2Baseline",
    "Config3_ScenarioC",
    "Config4_ScenarioD",
    "Config5_ScenarioE"
]
cfg_labels = [
    "Historic Baseline (Old Column Spks)",
    "Phase 2 Baseline (20 Line Arrays)",
    "Scenario C (Carpet + Panels + Curtains)",
    "Scenario D [Balanced Heritage]",
    "Scenario E [Max Reversible]"
]
colors = ["#c0392b", "#e67e22", "#2980b9", "#27ae60", "#8e44ad"]

# -------------------------------------------------------------------------
# Chart 1: Octave Band RT60 Comparison (Unoccupied)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
for k, lbl, c in zip(cfg_keys, cfg_labels, colors):
    t60_vals = comp[k]["occupancies"]["unoccupied"]["t60_eyring_s"]
    ax.plot([str(f) for f in octaves], t60_vals, marker="o", linewidth=2.5, label=lbl, color=c)

ax.axhline(0.8, color="#d35400", linestyle="--", linewidth=2.0, label="Theoretical Target (RT60 = 0.8 s)")
ax.axhspan(1.8, 2.2, color="#27ae60", alpha=0.15, label="Heritage Mosque Ideal Range (1.8 - 2.2 s)")
ax.set_title("Reverberation Time (T60 Eyring) across Octave Bands (63 Hz - 8000 Hz)\nMosque of Muhammad Ali Pasha — Unoccupied State", fontsize=13, fontweight="bold")
ax.set_xlabel("Octave Band Center Frequency (Hz)", fontsize=11, fontweight="bold")
ax.set_ylabel("Reverberation Time T60 (seconds)", fontsize=11, fontweight="bold")
ax.grid(True, linestyle=":", alpha=0.6)
ax.set_ylim(0, 22)
ax.legend(loc="upper right", framealpha=0.9, fontsize=9)
plt.tight_layout()
p1 = os.path.join(IMP_DIR, "phase3_2_rt60_octave_comparison.png")
fig.savefig(p1)
plt.close()
print(f"Generated: {p1}")

# -------------------------------------------------------------------------
# Chart 2: Speech Transmission Index (STI) Comparison across 16 Receivers
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 7), dpi=300)
recs = comp["Config2_Phase2Baseline"]["occupancies"]["unoccupied"]["receivers"]
rec_names = [r["receiver_id"].replace("REC_", "").replace("GROUND_", "G_").replace("GALLERY_", "GAL_") for r in recs]
x = np.arange(len(rec_names))
w = 0.16

for i, (k, lbl, c) in enumerate(zip(cfg_keys, cfg_labels, colors)):
    sti_vals = [r["sti"] for r in comp[k]["occupancies"]["unoccupied"]["receivers"]]
    ax.bar(x + (i - 2) * w, sti_vals, width=w, label=lbl, color=c, alpha=0.9)

ax.axhline(0.60, color="#27ae60", linestyle="--", linewidth=1.8, label="IEC 60268-16 'Good' Threshold (0.60)")
ax.axhline(0.45, color="#f39c12", linestyle=":", linewidth=1.5, label="IEC 60268-16 'Fair' Threshold (0.45)")
ax.set_title("Speech Transmission Index (STI) Comparison across 16 ISO 3382-1 Receivers\nUnoccupied Sanctuary Evaluation", fontsize=13, fontweight="bold")
ax.set_xlabel("Receiver Position Identifier", fontsize=11, fontweight="bold")
ax.set_ylabel("STI (0.0 to 1.0)", fontsize=11, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(rec_names, rotation=45, ha="right", fontsize=9)
ax.set_ylim(0.2, 0.8)
ax.grid(True, axis="y", linestyle=":", alpha=0.6)
ax.legend(loc="upper right", framealpha=0.9, fontsize=9)
plt.tight_layout()
p2 = os.path.join(IMP_DIR, "phase3_2_sti_distribution_comparison.png")
fig.savefig(p2)
plt.close()
print(f"Generated: {p2}")

# -------------------------------------------------------------------------
# Chart 3: Speech Clarity (C50) & Definition (D50) Comparison
# -------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

# C50 Means across occupancies
occupancies = ["unoccupied", "semi_occupied", "fully_occupied"]
occ_labels = ["Unoccupied (Empty)", "Semi-Occupied (50%)", "Fully Occupied (100%)"]
x_occ = np.arange(len(occ_labels))
w_occ = 0.15

for i, (k, lbl, c) in enumerate(zip(cfg_keys, cfg_labels, colors)):
    c50_vals = [comp[k]["occupancies"][o]["means"]["c50_mid_db"] for o in occupancies]
    ax1.bar(x_occ + (i - 2) * w_occ, c50_vals, width=w_occ, label=lbl, color=c, alpha=0.9)

ax1.axhline(0.0, color="#7f8c8d", linestyle="-", linewidth=1.0)
ax1.axhline(2.0, color="#27ae60", linestyle="--", linewidth=1.5, label="Good Speech Target (>= +2 dB)")
ax1.set_title("Speech Clarity C50 (Mid-Band Average)\nAcross Occupancy States", fontsize=11, fontweight="bold")
ax1.set_ylabel("C50 (dB)", fontsize=10, fontweight="bold")
ax1.set_xticks(x_occ)
ax1.set_xticklabels(occ_labels, fontsize=9)
ax1.set_ylim(-1, 9)
ax1.grid(True, axis="y", linestyle=":", alpha=0.6)
ax1.legend(loc="upper left", fontsize=8)

# D50 Definition across occupancies
for i, (k, lbl, c) in enumerate(zip(cfg_keys, cfg_labels, colors)):
    d50_vals = [comp[k]["occupancies"][o]["means"]["d50_mid_percent"] for o in occupancies]
    ax2.bar(x_occ + (i - 2) * w_occ, d50_vals, width=w_occ, label=lbl, color=c, alpha=0.9)

ax2.axhline(50.0, color="#d35400", linestyle="--", linewidth=1.5, label="Standard Target (>= 50%)")
ax2.set_title("Speech Definition D50 (Early Energy Fraction)\nAcross Occupancy States", fontsize=11, fontweight="bold")
ax2.set_ylabel("D50 (%)", fontsize=10, fontweight="bold")
ax2.set_xticks(x_occ)
ax2.set_xticklabels(occ_labels, fontsize=9)
ax2.set_ylim(40, 80)
ax2.grid(True, axis="y", linestyle=":", alpha=0.6)
ax2.legend(loc="upper left", fontsize=8)

plt.tight_layout()
p3 = os.path.join(IMP_DIR, "phase3_2_c50_d50_comparison.png")
fig.savefig(p3)
plt.close()
print(f"Generated: {p3}")

# -------------------------------------------------------------------------
# Chart 4: SPL(A), SPL(C) and Low-Frequency Delta Comparison
# -------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

spl_a_means = [comp[k]["occupancies"]["unoccupied"]["means"]["spl_a_dba"] for k in cfg_keys]
spl_c_means = [comp[k]["occupancies"]["unoccupied"]["means"]["spl_c_dbc"] for k in cfg_keys]
delta_means = [comp[k]["occupancies"]["unoccupied"]["means"]["delta_c_minus_a_db"] for k in cfg_keys]

x_cfg = np.arange(len(cfg_keys))
ax1.bar(x_cfg - 0.18, spl_a_means, width=0.35, label="SPL(A) [dBA]", color="#2980b9")
ax1.bar(x_cfg + 0.18, spl_c_means, width=0.35, label="SPL(C) [dBC]", color="#e74c3c")
ax1.axhspan(65, 70, color="#27ae60", alpha=0.2, label="Comfortable Speech SPL (65-70 dBA)")
ax1.set_title("Sound Pressure Levels SPL(A) vs SPL(C)\nUnoccupied Baseline to Scenario E", fontsize=11, fontweight="bold")
ax1.set_ylabel("Sound Pressure Level (dB)", fontsize=10, fontweight="bold")
ax1.set_xticks(x_cfg)
ax1.set_xticklabels(["Historic", "Phase 2", "Scen. C", "Scen. D", "Scen. E"], fontsize=9)
ax1.set_ylim(50, 105)
ax1.grid(True, axis="y", linestyle=":", alpha=0.6)
ax1.legend(loc="upper right", fontsize=8)

# Delta C - A (Spectral imbalance / rumble)
bars = ax2.bar(x_cfg, delta_means, width=0.5, color=["#c0392b", "#27ae60", "#27ae60", "#27ae60", "#27ae60"])
ax2.axhline(0.0, color="#7f8c8d", linestyle="-")
ax2.set_title("Low-Frequency Accumulation Delta (SPL C - A)\nSpectral Balance & Drone Suppression", fontsize=11, fontweight="bold")
ax2.set_ylabel("Delta C - A (dB)", fontsize=10, fontweight="bold")
ax2.set_xticks(x_cfg)
ax2.set_xticklabels(["Historic", "Phase 2", "Scen. C", "Scen. D", "Scen. E"], fontsize=9)
ax2.set_ylim(-1.0, 4.0)
ax2.grid(True, axis="y", linestyle=":", alpha=0.6)

for bar in bars:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, f"{yval:+.1f} dB", ha="center", va="bottom", fontsize=9, fontweight="bold")

plt.tight_layout()
p4 = os.path.join(IMP_DIR, "phase3_2_spl_distribution_comparison.png")
fig.savefig(p4)
plt.close()
print(f"Generated: {p4}")

# -------------------------------------------------------------------------
# Chart 5: Sensitivity Analysis on Provisional Coefficients
# -------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

labels_sens = ["Scenario D (Balanced)", "Scenario E (Max Reversible)"]
x_s = np.arange(len(labels_sens))
nom_t60 = [sens["Config4_ScenarioD"]["nominal"]["t60"], sens["Config5_ScenarioE"]["nominal"]["t60"]]
cons_t60 = [sens["Config4_ScenarioD"]["conservative"]["t60"], sens["Config5_ScenarioE"]["conservative"]["t60"]]

ax1.bar(x_s - 0.18, nom_t60, width=0.35, label="Nominal Lab Performance", color="#27ae60")
ax1.bar(x_s + 0.18, cons_t60, width=0.35, label="Conservative Bound (-15% on Provisional)", color="#e67e22")
ax1.set_title("Reverberation Time Sensitivity (T60 Mid)\nNominal vs Conservative Material Performance", fontsize=11, fontweight="bold")
ax1.set_ylabel("T60 Eyring (s)", fontsize=10, fontweight="bold")
ax1.set_xticks(x_s)
ax1.set_xticklabels(labels_sens, fontsize=10, fontweight="bold")
ax1.set_ylim(0, 3.5)
ax1.grid(True, axis="y", linestyle=":", alpha=0.6)
ax1.legend(loc="upper right", fontsize=9)

nom_sti = [sens["Config4_ScenarioD"]["nominal"]["sti"], sens["Config5_ScenarioE"]["nominal"]["sti"]]
cons_sti = [sens["Config4_ScenarioD"]["conservative"]["sti"], sens["Config5_ScenarioE"]["conservative"]["sti"]]

ax2.bar(x_s - 0.18, nom_sti, width=0.35, label="Nominal STI", color="#2980b9")
ax2.bar(x_s + 0.18, cons_sti, width=0.35, label="Conservative STI (-15% Abs)", color="#8e44ad")
ax2.axhline(0.60, color="#27ae60", linestyle="--", label="IEC Good Threshold (0.60)")
ax2.set_title("Speech Transmission Index Robustness\nUnder Provisional Material Uncertainty", fontsize=11, fontweight="bold")
ax2.set_ylabel("STI", fontsize=10, fontweight="bold")
ax2.set_xticks(x_s)
ax2.set_xticklabels(labels_sens, fontsize=10, fontweight="bold")
ax2.set_ylim(0.5, 0.75)
ax2.grid(True, axis="y", linestyle=":", alpha=0.6)
ax2.legend(loc="upper right", fontsize=9)

plt.tight_layout()
p5 = os.path.join(IMP_DIR, "phase3_2_sensitivity_analysis_chart.png")
fig.savefig(p5)
plt.close()
print(f"Generated: {p5}")

# -------------------------------------------------------------------------
# Chart 6: Architectural Perspective Views (Scenario D vs Scenario E in Context)
# -------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=300)

# Architectural perspective layout diagram - Scenario D
ax1.set_facecolor("#1a1a24")
# Draw prayer hall boundary
ax1.plot([-20.5, 20.5, 20.5, -20.5, -20.5], [-20.5, -20.5, 20.5, 20.5, -20.5], color="#ecf0f1", linewidth=2.5, label="Historic Perimeter Wall")
# Draw 4 central columns
for px, py in [(-6, -6), (6, -6), (-6, 6), (6, 6)]:
    rect = plt.Rectangle((px - 2.5, py - 2.5), 5.0, 5.0, facecolor="#7f8c8d", edgecolor="#bdc3c7", linewidth=1.5)
    ax1.add_patch(rect)
    ax1.text(px, py, "Limestone\nPier", color="#ffffff", ha="center", va="center", fontsize=8, fontweight="bold")

# Carpet
rect_c = plt.Rectangle((-20.0, -20.0), 40.0, 40.0, facecolor="#00b4a0", alpha=0.25, edgecolor="#00b4a0", linestyle="--", label="Enhanced Carpet (1,681 m2)")
ax1.add_patch(rect_c)

# Panels D: North (10), East (12), West (12)
ax1.plot([-18, 18], [20.0, 20.0], color="#d27828", linewidth=6.0, label="Perforated Wood Panels (420 m2)")
ax1.plot([20.0, 20.0], [-18, 18], color="#d27828", linewidth=6.0)
ax1.plot([-20.0, -20.0], [-18, 18], color="#d27828", linewidth=6.0)

# Curtains D: 24 bays
ax1.plot([19.5, 19.5], [-17, 17], color="#b42850", linewidth=3.5, linestyle=":", label="Retractable Curtains (360 m2)")
ax1.plot([-19.5, -19.5], [-17, 17], color="#b42850", linewidth=3.5, linestyle=":")
ax1.plot([-14, 14], [19.5, 19.5], color="#b42850", linewidth=3.5, linestyle=":")

# Baffles D: 24 units in secondary arches
for bx, by in [(-4, 12), (0, 12), (4, 12), (-4, -12), (0, -12), (4, -12), (12, -4), (12, 0), (12, 4), (-12, -4), (-12, 0), (-12, 4)]:
    ax1.plot([bx - 1.5, bx + 1.5], [by, by], color="#dcb41e", linewidth=4.0)
ax1.plot([], [], color="#dcb41e", linewidth=4.0, label="Suspended Baffles (280 m2)")

# Speakers
spk_xs = [s["coords"][0] for s in comp["Config2_Phase2Baseline"]["occupancies"]["unoccupied"]["receivers"][:20]]
ax1.scatter([px + dx for px in [-6, 6] for py in [-6, 6] for dx in [-2.7, 2.7]], 
            [py + dy for px in [-6, 6] for py in [-6, 6] for dy in [-2.7, 2.7]], 
            color="#2ecc71", s=60, marker="^", label="20 Distributed Line Arrays", zorder=5)

ax1.set_title("SCENARIO D: BALANCED HERITAGE INTERVENTION\nArchitectural Plan Layout & Zonal Integration", fontsize=11, fontweight="bold", color="#ffffff")
ax1.set_xlim(-24, 24)
ax1.set_ylim(-24, 24)
ax1.set_aspect("equal")
ax1.legend(loc="lower left", fontsize=7.5, facecolor="#2c3e50", edgecolor="#7f8c8d", labelcolor="#ffffff")
ax1.axis("off")

# Architectural perspective layout diagram - Scenario E
ax2.set_facecolor("#1a1a24")
ax2.plot([-20.5, 20.5, 20.5, -20.5, -20.5], [-20.5, -20.5, 20.5, 20.5, -20.5], color="#ecf0f1", linewidth=2.5)
for px, py in [(-6, -6), (6, -6), (-6, 6), (6, 6)]:
    rect = plt.Rectangle((px - 2.5, py - 2.5), 5.0, 5.0, facecolor="#7f8c8d", edgecolor="#bdc3c7", linewidth=1.5)
    ax2.add_patch(rect)
    ax2.text(px, py, "Limestone\nPier", color="#ffffff", ha="center", va="center", fontsize=8, fontweight="bold")

rect_c_e = plt.Rectangle((-20.0, -20.0), 40.0, 40.0, facecolor="#00b4a0", alpha=0.25, edgecolor="#00b4a0", linestyle="--", label="Enhanced Carpet (1,681 m2)")
ax2.add_patch(rect_c_e)

# Panels E: 550 m2 (North, East, West + South vestibule)
ax2.plot([-18, 18], [20.0, 20.0], color="#d27828", linewidth=7.5, label="Expanded Wood Panels (550 m2)")
ax2.plot([20.0, 20.0], [-19, 19], color="#d27828", linewidth=7.5)
ax2.plot([-20.0, -20.0], [-19, 19], color="#d27828", linewidth=7.5)
ax2.plot([-14, 14], [-20.0, -20.0], color="#d27828", linewidth=7.5)

# Curtains E: 480 m2 (All arcades + South)
ax2.plot([19.5, 19.5], [-19, 19], color="#b42850", linewidth=4.5, linestyle=":", label="Expanded Curtains (480 m2)")
ax2.plot([-19.5, -19.5], [-19, 19], color="#b42850", linewidth=4.5, linestyle=":")
ax2.plot([-16, 16], [19.5, 19.5], color="#b42850", linewidth=4.5, linestyle=":")
ax2.plot([-10, 10], [-19.5, -19.5], color="#b42850", linewidth=4.5, linestyle=":")

# Baffles E: 380 m2 (32 units including pendentive corners)
for bx, by in [(-4, 12), (0, 12), (4, 12), (-4, -12), (0, -12), (4, -12), (12, -4), (12, 0), (12, 4), (-12, -4), (-12, 0), (-12, 4),
              (-10, 10), (10, 10), (-10, -10), (10, -10), (-8, 12), (8, 12), (-8, -12), (8, -12)]:
    ax2.plot([bx - 1.5, bx + 1.5], [by, by], color="#dcb41e", linewidth=4.5)
ax2.plot([], [], color="#dcb41e", linewidth=4.5, label="Expanded Baffles (380 m2)")

ax2.scatter([px + dx for px in [-6, 6] for py in [-6, 6] for dx in [-2.7, 2.7]], 
            [py + dy for px in [-6, 6] for py in [-6, 6] for dy in [-2.7, 2.7]], 
            color="#2ecc71", s=60, marker="^", label="20 Distributed Line Arrays", zorder=5)

ax2.set_title("SCENARIO E: MAXIMUM REVERSIBLE INTERVENTION\nExpanded Boundary & Pendentive Cladding", fontsize=11, fontweight="bold", color="#ffffff")
ax2.set_xlim(-24, 24)
ax2.set_ylim(-24, 24)
ax2.set_aspect("equal")
ax2.legend(loc="lower left", fontsize=7.5, facecolor="#2c3e50", edgecolor="#7f8c8d", labelcolor="#ffffff")
ax2.axis("off")

plt.tight_layout()
p6 = os.path.join(IMP_DIR, "phase3_2_architectural_perspective_comparison.png")
fig.savefig(p6)
plt.close()
print(f"Generated: {p6}")

# -------------------------------------------------------------------------
# Chart 7: Structural Mounting & Conservation Detail Diagram
# -------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

# Diagram 1: Suspended Baffle Clamping Mechanism
ax1.set_facecolor("#f9f9f9")
# Iron tie rod
ax1.axhline(6.0, color="#2c3e50", linewidth=12.0, label="19th-C Forged-Iron Structural Tie-Rod (Pure Tension Member)")
# Demountable collar
collar = plt.Rectangle((-3.0, 5.2), 6.0, 1.6, facecolor="#d35400", edgecolor="#962d00", linewidth=2.0, label="Split-Sleeve Bronze Friction Collar (No Drilling/Welding)")
ax1.add_patch(collar)
# Elastomeric liner
liner = plt.Rectangle((-2.8, 5.5), 5.6, 1.0, facecolor="#3498db", alpha=0.6, label="5mm Neoprene/Silicone Conservation Buffer")
ax1.add_patch(liner)
# Suspension drop wires
ax1.plot([-2.0, -2.0], [5.2, 3.0], color="#7f8c8d", linewidth=3.0)
ax1.plot([2.0, 2.0], [5.2, 3.0], color="#7f8c8d", linewidth=3.0)
# Baffle body
baffle = plt.Rectangle((-4.5, 0.5), 9.0, 2.5, facecolor="#dcb41e", edgecolor="#b89410", linewidth=2.5, label="Dual-Faced Islamic Arabesque Baffle (50mm Basalt Core)")
ax1.add_patch(baffle)
ax1.text(0.0, 1.75, "Laser-Cut Decorative Screen Lattice\nP=18%, Basalt Mineral Core", ha="center", va="center", fontsize=9, fontweight="bold")
ax1.text(0.0, 4.0, "Suspension Cables\n(Demountable Turnbuckles)", ha="center", va="center", fontsize=8, color="#555")

ax1.set_title("STRUCTURAL DETAIL 1: SUSPENDED BAFFLE MOUNTING\nFriction-Clamped Non-Destructive Assembly", fontsize=11, fontweight="bold")
ax1.set_xlim(-6, 6)
ax1.set_ylim(0, 8)
ax1.axis("off")
ax1.legend(loc="lower center", fontsize=8, framealpha=0.9)

# Diagram 2: Freestanding Wood Panel Compression Framing
ax2.set_facecolor("#f9f9f9")
# Historic Marble Wall
wall = plt.Rectangle((-5.0, 0.0), 1.5, 8.0, facecolor="#bdc3c7", edgecolor="#7f8c8d", linewidth=2.0, label="Historic Marble Wall (Zero Fasteners Permitted)")
ax2.add_patch(wall)
ax2.text(-4.25, 4.0, "Historic\nMarble\nRevetment", ha="center", va="center", fontsize=9, fontweight="bold", rotation=90)

# Air Cavity Gap (10mm)
ax2.axvline(-3.5, color="#e74c3c", linestyle="--", linewidth=1.5, label="10mm Air Separation Gap (Non-Contact)")

# Panel Frame
panel_frame = plt.Rectangle((-3.3, 0.5), 2.2, 6.0, facecolor="#d27828", edgecolor="#a05210", linewidth=2.0, label="Perforated Wood Panel (106mm Assembly)")
ax2.add_patch(panel_frame)
ax2.text(-2.2, 3.5, "16mm MDF (P=14%)\n+\n40mm Rockwool\n+\n50mm Cavity", ha="center", va="center", fontsize=8, fontweight="bold", color="#ffffff")

# Weighted Floor Base
base = plt.Rectangle((-3.8, 0.0), 3.5, 0.5, facecolor="#34495e", edgecolor="#2c3e50", linewidth=2.0, label="Weighted Bronze Foot with Elastomeric Pad")
ax2.add_patch(base)
ax2.text(-2.0, 0.25, "Weighted Floor Base", ha="center", va="center", fontsize=7.5, color="#ffffff")

# Compression Strut at top
strut = plt.Rectangle((-3.4, 6.5), 0.5, 1.2, facecolor="#7f8c8d", edgecolor="#333", linewidth=1.5, label="Telescopic Spring Compression Strut")
ax2.add_patch(strut)
ax2.text(-1.5, 7.1, "Telescopic Spring Strut\n(Reversible Compression)", ha="left", va="center", fontsize=8)

ax2.set_title("STRUCTURAL DETAIL 2: FREESTANDING PANEL MOUNTING\nSelf-Supporting Compression Stanchion Assembly", fontsize=11, fontweight="bold")
ax2.set_xlim(-6, 2)
ax2.set_ylim(0, 8)
ax2.axis("off")
ax2.legend(loc="lower center", fontsize=8, framealpha=0.9)

plt.tight_layout()
p7 = os.path.join(IMP_DIR, "phase3_2_mounting_structural_detail.png")
fig.savefig(p7)
plt.close()
print(f"Generated: {p7}")
