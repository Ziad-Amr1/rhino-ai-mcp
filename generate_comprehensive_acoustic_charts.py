"""Generates comprehensive acoustic charts for Mosque of Muhammad Ali Pasha
covering the Existing Condition (Baseline) and Improved Sound System across
Unoccupied, Semi-Occupied, and Fully-Occupied conditions.

Outputs:
1. existing_baseline_rt60_edt_frequency_curve.png
2. existing_baseline_clarity_c80_c50_d50.png
3. background_noise_nc_nr_curves.png
4. multi_zone_spatial_comparison_matrix.png
5. baseline_vs_improved_comprehensive_comparison.png
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


def load_dataset():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def plot_rt60_frequency_curves(data):
    """Plot 1: RT60 / EDT at 125-4000 Hz for Empty, Semi-Occupied, and Fully-Occupied."""
    bands = [125, 250, 500, 1000, 2000, 4000]
    band_indices = [1, 2, 3, 4, 5, 6] # indices in 8-band array (63 to 8000)

    unocc_t60 = [data["unoccupied"]["room_physics"]["t60_eyring_s"][i] for i in band_indices]
    semi_t60 = [data["semi_occupied"]["room_physics"]["t60_eyring_s"][i] for i in band_indices]
    full_t60 = [data["fully_occupied"]["room_physics"]["t60_eyring_s"][i] for i in band_indices]

    # Average EDT across receivers for unoccupied baseline
    unocc_edt = []
    for b in bands:
        edts = [r["octave_bands"][str(b)]["edt_s"] for r in data["unoccupied"]["baseline_receivers"]]
        unocc_edt.append(round(float(np.mean(edts)), 2))

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    x = np.arange(len(bands))

    ax.plot(x, unocc_t60, marker="o", linewidth=2.5, color="#d9534f", label="Unoccupied RT60 (T30 / Eyring) - Baseline")
    ax.plot(x, unocc_edt, marker="s", linewidth=2.0, linestyle="--", color="#f0ad4e", label="Unoccupied EDT (Early Decay Time)")
    ax.plot(x, semi_t60, marker="^", linewidth=2.2, color="#5bc0de", label="Semi-Occupied RT60 (~50% Capacity / 600 Worshippers)")
    ax.plot(x, full_t60, marker="d", linewidth=2.2, color="#5cb85c", label="Fully Occupied RT60 (100% Capacity / 1200 Worshippers)")

    # Optimum target band for speech intelligibility in mosques (ISO 3382 / Beranek)
    ax.axhspan(1.5, 2.0, color="#2ecc71", alpha=0.15, label="Target Speech RT60 Range (1.5 - 2.0 s)")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{b} Hz" for b in bands], fontsize=11, fontweight="bold")
    ax.set_ylabel("Reverberation Time (seconds)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Octave Band Frequency (Hz)", fontsize=12, fontweight="bold")
    ax.set_title("Mosque of Muhammad Ali: Reverberation Time (RT60) & EDT vs Frequency\nExisting Condition across Empty, Semi-Occupied, and Fully-Occupied States", fontsize=13, fontweight="bold", pad=15)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.set_ylim(0, 18)
    ax.legend(loc="upper right", frameon=True, shadow=True, fontsize=10)

    # Annotations
    ax.annotate(f"Mid T60: {unocc_t60[2]:.2f}s\nLow-freq boom: {unocc_t60[0]:.2f}s", xy=(x[2], unocc_t60[2]), xytext=(x[2]-0.3, unocc_t60[2]+2.5),
                arrowprops=dict(facecolor="#d9534f", shrink=0.05, width=1.5, headwidth=6), fontsize=9, fontweight="bold", color="#d9534f")

    out_path = os.path.join(IMP_DIR, "existing_baseline_rt60_edt_frequency_curve.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_clarity_definition(data):
    """Plot 2: C80, C50, and D50 across 16 receiver positions in Baseline."""
    receivers = data["unoccupied"]["baseline_receivers"]
    rec_names = [r["receiver_id"].replace("REC_GROUND_", "R_").replace("REC_GALLERY_", "G_") for r in receivers]
    c80_vals = [r["c80_mid_db"] for r in receivers]
    c50_vals = [r["c50_mid_db"] for r in receivers]
    d50_vals = [r["d50_mid_percent"] for r in receivers]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), dpi=300, sharex=True)
    x = np.arange(len(receivers))
    width = 0.38

    # Top: C80 vs C50
    ax1.bar(x - width/2, c80_vals, width, label="C80 (Music / Sacred Hall Clarity)", color="#3498db", alpha=0.9)
    ax1.bar(x + width/2, c50_vals, width, label="C50 (Speech Clarity)", color="#e74c3c", alpha=0.9)
    ax1.axhline(0.0, color="black", linestyle="--", linewidth=1.2, label="0 dB Threshold")
    ax1.axhspan(-15, 0, color="#e74c3c", alpha=0.08, label="Muffled / Poor Intelligibility (< 0 dB)")
    ax1.axhspan(0, 15, color="#2ecc71", alpha=0.08, label="Acceptable Clarity (> 0 dB)")
    ax1.set_ylabel("Clarity Index (dB)", fontsize=11, fontweight="bold")
    ax1.set_title("Mosque of Muhammad Ali: Existing Baseline Clarity (C80 & C50) across 16 Receivers", fontsize=12, fontweight="bold")
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(loc="upper right", fontsize=9)

    # Bottom: D50 Definition
    ax2.bar(x, d50_vals, width=0.6, label="D50 (Speech Definition %)", color="#9b59b6", alpha=0.85)
    ax2.axhline(50.0, color="#27ae60", linestyle="--", linewidth=1.5, label="50% Good Definition Standard (ISO 3382)")
    ax2.axhspan(0, 50, color="#e74c3c", alpha=0.08)
    ax2.set_ylabel("Definition D50 (%)", fontsize=11, fontweight="bold")
    ax2.set_title("Speech Definition (D50) across 16 Receivers (Existing Baseline Condition)", fontsize=12, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(rec_names, rotation=45, ha="right", fontsize=9, fontweight="bold")
    ax2.set_ylim(0, 100)
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="upper right", fontsize=9)

    out_path = os.path.join(IMP_DIR, "existing_baseline_clarity_c80_c50_d50.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_noise_curves(data):
    """Plot 3: Background Noise / NC and NR curves vs Mosque Ambient Noise."""
    octaves = [63, 125, 250, 500, 1000, 2000, 4000, 8000]
    x = np.arange(len(octaves))

    # Standard NC Curves
    nc_curves = {
        "NC-25": [50, 44, 38, 31, 25, 22, 20, 18],
        "NC-30": [52, 46, 39, 34, 30, 28, 26, 24],
        "NC-35": [56, 50, 44, 39, 35, 33, 31, 29],
        "NC-40": [60, 54, 48, 44, 40, 38, 36, 34],
        "NC-45": [63, 58, 53, 49, 45, 43, 41, 39]
    }

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    for nc_name, curve in nc_curves.items():
        style = "--" if nc_name not in ["NC-30", "NC-35", "NC-40"] else "-"
        width = 1.0 if nc_name not in ["NC-30", "NC-35", "NC-40"] else 1.5
        ax.plot(x, curve, linestyle=style, linewidth=width, color="#7f8c8d", alpha=0.5, label=f"Standard {nc_name}")

    # Mosque measured/simulated background noise spectra
    unocc_noise = data["unoccupied"]["noise_profile"]["octaves_db"]
    semi_noise = data["semi_occupied"]["noise_profile"]["octaves_db"]
    full_noise = data["fully_occupied"]["noise_profile"]["octaves_db"]

    ax.plot(x, unocc_noise, marker="o", linewidth=2.5, color="#2980b9", label="Unoccupied Ambient (NC-30, 35 dBA)")
    ax.plot(x, semi_noise, marker="s", linewidth=2.5, color="#f39c12", label="Semi-Occupied Ambient (NC-38, 42 dBA)")
    ax.plot(x, full_noise, marker="^", linewidth=2.5, color="#c0392b", label="Fully Occupied Ambient (NC-42, 48 dBA)")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{f} Hz" for f in octaves], fontsize=11, fontweight="bold")
    ax.set_ylabel("Octave Band Sound Pressure Level (dB re 20 uPa)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Octave Band Center Frequency (Hz)", fontsize=11, fontweight="bold")
    ax.set_title("Mosque of Muhammad Ali: Ambient Background Noise vs Standard NC Curves\nImpact of Congregation Occupancy on Acoustic Noise Floor", fontsize=12, fontweight="bold", pad=15)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.set_ylim(10, 75)
    ax.legend(loc="upper right", frameon=True, fontsize=9)

    out_path = os.path.join(IMP_DIR, "background_noise_nc_nr_curves.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_baseline_vs_improved(data):
    """Plot 4: Before vs After Comprehensive Comparison across Occupancies."""
    scenarios = ["unoccupied", "semi_occupied", "fully_occupied"]
    scen_labels = ["Unoccupied (Empty)", "Semi-Occupied (50%)", "Fully Occupied (100%)"]

    base_sti = [data[s]["summary_means"]["baseline"]["sti"] for s in scenarios]
    imp_sti = [data[s]["summary_means"]["improved"]["sti"] for s in scenarios]

    base_c50 = [data[s]["summary_means"]["baseline"]["c50_db"] for s in scenarios]
    imp_c50 = [data[s]["summary_means"]["improved"]["c50_db"] for s in scenarios]

    base_d50 = [data[s]["summary_means"]["baseline"]["d50_percent"] for s in scenarios]
    imp_d50 = [data[s]["summary_means"]["improved"]["d50_percent"] for s in scenarios]

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5), dpi=300)
    x = np.arange(len(scenarios))
    w = 0.35

    # STI
    ax1.bar(x - w/2, base_sti, w, label="Baseline (4 Column Clusters)", color="#e74c3c")
    ax1.bar(x + w/2, imp_sti, w, label="Improved (20 Distributed)", color="#2ecc71")
    ax1.axhline(0.60, color="#27ae60", linestyle="--", label="Good STI (0.60)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(scen_labels, fontsize=10, fontweight="bold")
    ax1.set_ylabel("Speech Transmission Index (STI)", fontsize=11, fontweight="bold")
    ax1.set_title("Speech Intelligibility (STI)", fontsize=12, fontweight="bold")
    ax1.set_ylim(0, 1.0)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(loc="lower right", fontsize=8)

    # C50
    ax2.bar(x - w/2, base_c50, w, label="Baseline", color="#e74c3c")
    ax2.bar(x + w/2, imp_c50, w, label="Improved", color="#2ecc71")
    ax2.axhline(0.0, color="black", linestyle="--")
    ax2.set_xticks(x)
    ax2.set_xticklabels(scen_labels, fontsize=10, fontweight="bold")
    ax2.set_ylabel("Speech Clarity C50 (dB)", fontsize=11, fontweight="bold")
    ax2.set_title("Speech Clarity (C50)", fontsize=12, fontweight="bold")
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="lower right", fontsize=8)

    # D50
    ax3.bar(x - w/2, base_d50, w, label="Baseline", color="#e74c3c")
    ax3.bar(x + w/2, imp_d50, w, label="Improved", color="#2ecc71")
    ax3.axhline(50.0, color="#27ae60", linestyle="--", label="Target D50 (50%)")
    ax3.set_xticks(x)
    ax3.set_xticklabels(scen_labels, fontsize=10, fontweight="bold")
    ax3.set_ylabel("Speech Definition D50 (%)", fontsize=11, fontweight="bold")
    ax3.set_title("Speech Definition (D50)", fontsize=12, fontweight="bold")
    ax3.set_ylim(0, 100)
    ax3.grid(True, linestyle=":", alpha=0.6)
    ax3.legend(loc="lower right", fontsize=8)

    fig.suptitle("Mosque of Muhammad Ali: Acoustic Performance Comparison\nExisting Baseline vs Proposed Improved System across Occupancy States", fontsize=13, fontweight="bold", y=1.03)

    out_path = os.path.join(IMP_DIR, "baseline_vs_improved_comprehensive_comparison.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def main():
    print("Loading simulation dataset...")
    data = load_dataset()
    print("Generating comprehensive acoustic charts...")
    plot_rt60_frequency_curves(data)
    plot_clarity_definition(data)
    plot_noise_curves(data)
    plot_baseline_vs_improved(data)
    print("All charts successfully generated!")


if __name__ == "__main__":
    main()
