"""Generates spatial matrix heatmap of the 16 acoustic receivers
for the Existing Baseline Condition of Mosque of Muhammad Ali.
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_DIR = r"E:\course\03_Programming_Data\AI\Projects\rhino"
IMP_DIR = os.path.join(PROJECT_DIR, "Improved_Acoustic_System")
DATA_PATH = os.path.join(IMP_DIR, "pachyderm_comprehensive_study_dataset.json")

with open(DATA_PATH, "r") as f:
    data = json.load(f)

receivers = data["unoccupied"]["baseline_receivers"]

# Metrics to display
col_labels = ["Zone", "First Arr (ms)", "STI (IEC)", "C50 (dB)", "C80 (dB)", "D50 (%)", "SPL(A) (dBA)", "SPL(C) (dBC)", "Delta C-A (dB)"]
row_labels = [r["receiver_id"].replace("REC_GROUND_", "R").replace("REC_GALLERY_", "G") for r in receivers]

table_vals = []
for r in receivers:
    table_vals.append([
        r["zone"][:12],
        f"{r['first_arrival_ms']:.1f}",
        f"{r['sti_pachyderm']:.2f}",
        f"{r['c50_mid_db']:+.1f}",
        f"{r['c80_mid_db']:+.1f}",
        f"{r['d50_mid_percent']:.1f}%",
        f"{r['spl_a_dba']:.1f}",
        f"{r['spl_c_dbc']:.1f}",
        f"{r['delta_c_minus_a_db']:+.1f}"
    ])

fig, ax = plt.subplots(figsize=(14, 9), dpi=300)
ax.axis("off")

table = ax.table(
    cellText=table_vals,
    colLabels=col_labels,
    rowLabels=row_labels,
    loc="center",
    cellLoc="center"
)

table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.0, 1.6)

# Header formatting
for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor("#2c3e50")
        cell.set_text_props(color="white", fontweight="bold")
    elif col == -1:
        cell.set_facecolor("#ecf0f1")
        cell.set_text_props(fontweight="bold")
    else:
        # Highlight critical acoustic violations in Existing Condition
        sti_val = float(table_vals[row-1][2])
        c50_val = float(table_vals[row-1][3])
        d50_val = float(table_vals[row-1][5].replace("%", ""))
        delta_ca = float(table_vals[row-1][8])

        if col == 2: # STI
            cell.set_facecolor("#f8d7da" if sti_val < 0.40 else "#fff3cd")
            cell.set_text_props(fontweight="bold", color="#721c24")
        elif col == 3: # C50
            cell.set_facecolor("#f8d7da" if c50_val < 0.0 else "#d4edda")
            cell.set_text_props(fontweight="bold", color="#721c24" if c50_val < 0 else "#155724")
        elif col == 5: # D50
            cell.set_facecolor("#f8d7da" if d50_val < 50.0 else "#d4edda")
        elif col == 8: # Delta C-A
            cell.set_facecolor("#fff3cd" if delta_ca > 6.0 else "#ffffff")

plt.title("Mosque of Muhammad Ali: 16-Receiver Acoustic Measurement Matrix (Existing Baseline Unoccupied Condition)\nFull ISO 3382-1 & IEC 60268-16 Parameter Breakdown",
          fontsize=12, fontweight="bold", pad=20)

out_path = os.path.join(IMP_DIR, "existing_baseline_receiver_spatial_matrix.png")
plt.tight_layout()
plt.savefig(out_path, dpi=300)
plt.close()
print(f"Saved: {out_path}")
