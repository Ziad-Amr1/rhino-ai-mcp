"""Generates Phase 3 Acoustic Material Optimization Charts:
1. phase3_rt60_reduction_scenarios_comparison.png
2. phase3_octave_band_rt60_curves.png
3. phase3_absorption_area_deficit_waterfall.png
4. phase3_speech_metrics_evolution.png
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_DIR = r"E:\course\03_Programming_Data\AI\Projects\rhino"
IMP_DIR = os.path.join(PROJECT_DIR, "Improved_Acoustic_System")
DATA_PATH = os.path.join(IMP_DIR, "phase3_material_optimization_dataset.json")


def load_dataset():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def plot_rt60_scenarios_comparison(data):
    """Plot 1: Mid-Frequency RT60 (500 Hz & 1000 Hz) across Scenarios."""
    scenarios = ["Baseline", "Scenario_A", "Scenario_B", "Scenario_C", "Scenario_D", "Scenario_E"]
    scen_labels = [
        "Baseline\n(Existing)",
        "Scenario A\n(Carpet)",
        "Scenario B\n(+ Panels)",
        "Scenario C\n(+ Curtains)",
        "Scenario D\n(+ Baffles)",
        "Scenario E\n(Max Reversible)"
    ]

    unocc_t60 = [data[s]["occupancy_runs"]["unoccupied"]["mid_t60_eyring_s"] for s in scenarios]
    semi_t60 = [data[s]["occupancy_runs"]["semi_occupied"]["mid_t60_eyring_s"] for s in scenarios]
    full_t60 = [data[s]["occupancy_runs"]["fully_occupied"]["mid_t60_eyring_s"] for s in scenarios]

    fig, ax = plt.subplots(figsize=(13, 7), dpi=300)
    x = np.arange(len(scenarios))
    w = 0.26

    rects1 = ax.bar(x - w, unocc_t60, w, label="Unoccupied (Empty)", color="#d9534f", alpha=0.9)
    rects2 = ax.bar(x, semi_t60, w, label="Semi-Occupied (50% / 600 Worshippers)", color="#f0ad4e", alpha=0.9)
    rects3 = ax.bar(x + w, full_t60, w, label="Fully Occupied (100% / 1,200 Congregation)", color="#5cb85c", alpha=0.9)

    # Target line at 0.8s
    ax.axhline(0.8, color="#e74c3c", linestyle="--", linewidth=2.0, label="Proposed Target RT60 = 0.8 s (Unachievable in Sacred Dome)")
    ax.axhspan(1.8, 2.3, color="#2ecc71", alpha=0.15, label="Optimal Conservation Limit (1.8 s - 2.3 s)")

    # Value labels
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.2f}s", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#d9534f")
    for rect in rects3:
        h = rect.get_height()
        ax.annotate(f"{h:.2f}s", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#27ae60")

    ax.set_xticks(x)
    ax.set_xticklabels(scen_labels, fontsize=10, fontweight="bold")
    ax.set_ylabel("Mid-Frequency Reverberation Time T60 (seconds)", fontsize=11, fontweight="bold")
    ax.set_title("Mosque of Muhammad Ali: RT60 Reduction across 5 Material Intervention Scenarios\nTarget RT60 = 0.8s Verification across Occupancy States",
                 fontsize=12, fontweight="bold", pad=15)
    ax.set_ylim(0, 7.0)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", frameon=True, shadow=True, fontsize=9.5)

    out_path = os.path.join(IMP_DIR, "phase3_rt60_reduction_scenarios_comparison.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_octave_curves(data):
    """Plot 2: Octave Band RT60 Curves across 125 Hz to 4000 Hz."""
    bands = [125, 250, 500, 1000, 2000, 4000]
    band_indices = [1, 2, 3, 4, 5, 6]

    base_curve = [data["Baseline"]["occupancy_runs"]["unoccupied"]["t60_eyring_s"][i] for i in band_indices]
    scen_a_curve = [data["Scenario_A"]["occupancy_runs"]["unoccupied"]["t60_eyring_s"][i] for i in band_indices]
    scen_c_curve = [data["Scenario_C"]["occupancy_runs"]["unoccupied"]["t60_eyring_s"][i] for i in band_indices]
    scen_e_curve = [data["Scenario_E"]["occupancy_runs"]["unoccupied"]["t60_eyring_s"][i] for i in band_indices]
    scen_e_occ = [data["Scenario_E"]["occupancy_runs"]["fully_occupied"]["t60_eyring_s"][i] for i in band_indices]

    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    x = np.arange(len(bands))

    ax.plot(x, base_curve, marker="o", linewidth=2.5, color="#d9534f", label="Baseline (Unoccupied): Mid T60 = 5.67s")
    ax.plot(x, scen_a_curve, marker="s", linewidth=2.0, color="#f0ad4e", label="Scenario A (Carpet Only): Mid T60 = 3.82s")
    ax.plot(x, scen_c_curve, marker="^", linewidth=2.0, color="#3498db", label="Scenario C (Carpet + Panels + Curtains): Mid T60 = 2.68s")
    ax.plot(x, scen_e_curve, marker="d", linewidth=2.5, color="#9b59b6", label="Scenario E (Max Reversible Unocc): Mid T60 = 2.25s")
    ax.plot(x, scen_e_occ, marker="*", markersize=10, linewidth=2.5, color="#2ecc71", linestyle="--", label="Scenario E (Fully Occupied): Mid T60 = 1.82s")

    ax.axhline(0.8, color="#e74c3c", linestyle=":", linewidth=2.0, label="Proposed Target 0.8s")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{b} Hz" for b in bands], fontsize=11, fontweight="bold")
    ax.set_ylabel("Reverberation Time T60 (seconds)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Octave Band Center Frequency (Hz)", fontsize=11, fontweight="bold")
    ax.set_title("Mosque of Muhammad Ali: Frequency-Dependent RT60 Spectrum\nDramatic Suppression of Low-Frequency Booming (125-500 Hz)",
                 fontsize=12, fontweight="bold", pad=15)
    ax.set_ylim(0, 17)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", frameon=True, fontsize=9.5)

    out_path = os.path.join(IMP_DIR, "phase3_octave_band_rt60_curves.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_absorption_deficit_waterfall(data):
    """Plot 3: Absorption Area Deficit Waterfall (Why 0.8s is Unachievable)."""
    # Absorption at 500 Hz
    base_abs = 827.2
    carpet_add = 504.3
    panels_add = 352.8
    curtains_add = 255.6
    baffles_add = 238.0
    total_realistic = base_abs + carpet_add + panels_add + curtains_add + baffles_add # 2177.9
    req_for_08s = 8017.8
    deficit = req_for_08s - total_realistic # 5839.9

    categories = [
        "Baseline\nAbsorption",
        "+ Enhanced\nCarpet",
        "+ Perforated\nPanels",
        "+ Acoustic\nCurtains",
        "+ Suspended\nBaffles",
        "Total Reversible\nAchieved",
        "TARGET\nREQUIRED (0.8s)",
        "REMAINING\nDEFICIT"
    ]
    vals = [base_abs, carpet_add, panels_add, curtains_add, baffles_add, total_realistic, req_for_08s, deficit]
    colors = ["#7f8c8d", "#00b4a0", "#d37828", "#b42850", "#dcb41e", "#2ecc71", "#e74c3c", "#c0392b"]

    fig, ax = plt.subplots(figsize=(13, 6), dpi=300)
    x = np.arange(len(categories))

    bars = ax.bar(x, vals, width=0.55, color=colors, alpha=0.9, edgecolor="black", linewidth=1.0)

    for bar, val in zip(bars, vals):
        h = bar.get_height()
        ax.annotate(f"{val:.0f} m2\nSabins", xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 4),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9.5, fontweight="bold")
    ax.set_ylabel("Equivalent Sound Absorption Area (m2 Sabins at 500 Hz)", fontsize=11, fontweight="bold")
    ax.set_title("Acoustic Absorption Deficit Analysis: Proving Why RT60 = 0.8s is Physically Unachievable\nReversible Treatments vs Massive Absorption Deficit (5,840 m2 Sabins)",
                 fontsize=12, fontweight="bold", pad=15)
    ax.set_ylim(0, 9500)
    ax.grid(True, linestyle=":", alpha=0.6)

    # Explanatory annotation
    ax.annotate("Absorbing 5,840 m2 more would require\ncovering 63% of the historic painted dome\nand alabaster revetment!",
                xy=(x[7], deficit), xytext=(x[7]-1.8, deficit+1500),
                arrowprops=dict(facecolor="#c0392b", shrink=0.05, width=1.5, headwidth=6),
                fontsize=9, fontweight="bold", color="#c0392b",
                bbox=dict(boxstyle="round,pad=0.4", fc="#fadbd8", ec="#c0392b", lw=1))

    out_path = os.path.join(IMP_DIR, "phase3_absorption_area_deficit_waterfall.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_speech_metrics_evolution(data):
    """Plot 4: Speech Metrics Evolution (STI, C50, C80, D50)."""
    scenarios = ["Baseline", "Scenario_A", "Scenario_B", "Scenario_C", "Scenario_D", "Scenario_E"]
    scen_labels = ["Baseline", "Scen A\n(Carpet)", "Scen B\n(+Panels)", "Scen C\n(+Curtains)", "Scen D\n(+Baffles)", "Scen E\n(Max)"]

    sti_unocc = [data[s]["occupancy_runs"]["unoccupied"]["means"]["sti"] for s in scenarios]
    c50_unocc = [data[s]["occupancy_runs"]["unoccupied"]["means"]["c50_mid_db"] for s in scenarios]
    c80_unocc = [data[s]["occupancy_runs"]["unoccupied"]["means"]["c80_mid_db"] for s in scenarios]
    d50_unocc = [data[s]["occupancy_runs"]["unoccupied"]["means"]["d50_mid_percent"] for s in scenarios]

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(13, 8), dpi=300)
    x = np.arange(len(scenarios))

    # STI
    ax1.plot(x, sti_unocc, marker="o", linewidth=2.5, color="#27ae60")
    ax1.axhline(0.60, color="#2ecc71", linestyle="--", label="Good STI (0.60)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(scen_labels, fontsize=9, fontweight="bold")
    ax1.set_ylabel("Speech Transmission Index (STI)", fontweight="bold")
    ax1.set_title("Speech Intelligibility (STI)", fontweight="bold")
    ax1.set_ylim(0.2, 0.8)
    ax1.grid(True, linestyle=":")

    # C50
    ax2.plot(x, c50_unocc, marker="s", linewidth=2.5, color="#2980b9")
    ax2.axhline(0.0, color="black", linestyle="--", label="0 dB Threshold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(scen_labels, fontsize=9, fontweight="bold")
    ax2.set_ylabel("Speech Clarity C50 (dB)", fontweight="bold")
    ax2.set_title("Speech Clarity (C50)", fontweight="bold")
    ax2.grid(True, linestyle=":")

    # C80
    ax3.plot(x, c80_unocc, marker="^", linewidth=2.5, color="#8e44ad")
    ax3.axhline(0.0, color="black", linestyle="--")
    ax3.set_xticks(x)
    ax3.set_xticklabels(scen_labels, fontsize=9, fontweight="bold")
    ax3.set_ylabel("Hall Clarity C80 (dB)", fontweight="bold")
    ax3.set_title("Sacred Hall Clarity (C80)", fontweight="bold")
    ax3.grid(True, linestyle=":")

    # D50
    ax4.plot(x, d50_unocc, marker="d", linewidth=2.5, color="#e67e22")
    ax4.axhline(50.0, color="#27ae60", linestyle="--", label="Target D50 (50%)")
    ax4.set_xticks(x)
    ax4.set_xticklabels(scen_labels, fontsize=9, fontweight="bold")
    ax4.set_ylabel("Speech Definition D50 (%)", fontweight="bold")
    ax4.set_title("Speech Definition (D50)", fontweight="bold")
    ax4.set_ylim(20, 90)
    ax4.grid(True, linestyle=":")

    fig.suptitle("Mosque of Muhammad Ali: Acoustic Performance Metrics Evolution across Scenarios\nPachyderm Acoustic Universal Native Solvers (ISO 3382-1 & IEC 60268-16)",
                 fontsize=12, fontweight="bold", y=0.99)

    out_path = os.path.join(IMP_DIR, "phase3_speech_metrics_evolution.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def main():
    print("Loading Phase 3 simulation dataset...")
    data = load_dataset()
    print("Generating Phase 3 acoustic charts...")
    plot_rt60_scenarios_comparison(data)
    plot_octave_curves(data)
    plot_absorption_deficit_waterfall(data)
    plot_speech_metrics_evolution(data)
    print("All Phase 3 charts successfully generated!")


if __name__ == "__main__":
    main()
