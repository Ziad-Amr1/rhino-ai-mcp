"""Generates a high-precision focused acoustic chart on 500 Hz & 1000 Hz (RT60m) for Muhammad Ali Mosque."""

import os
import sys

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from mosque_acoustic_data import ACOUSTIC_MATERIALS, MOSQUE_GEOMETRY
from pachyderm_simulation import calculate_analytical_acoustics

REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def build_focused_mid_frequency_svg():
    unocc = calculate_analytical_acoustics(occupied=False)
    occ = calculate_analytical_acoustics(occupied=True)

    # 500 Hz (index 3) and 1000 Hz (index 4)
    u_500 = unocc["octave_band_results"][3]
    u_1000 = unocc["octave_band_results"][4]
    o_500 = occ["octave_band_results"][3]
    o_1000 = occ["octave_band_results"][4]

    sab_unocc_mid = unocc["summary"]["reverberation_time_t60_mid_sabine_s"]
    eyr_unocc_mid = unocc["summary"]["reverberation_time_t60_mid_eyring_s"]
    sab_occ_mid = occ["summary"]["reverberation_time_t60_mid_sabine_s"]
    eyr_occ_mid = occ["summary"]["reverberation_time_t60_mid_eyring_s"]

    # Canvas dimensions
    w, h = 1000, 620
    margin = {"top": 90, "right": 380, "bottom": 90, "left": 80}
    plot_w = w - margin["left"] - margin["right"]  # 540 px
    plot_h = h - margin["top"] - margin["bottom"]   # 440 px

    # Focused time scale: 0.0s to 8.0s (zoomed into critical speech/chanting range)
    max_t = 8.0

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="background:#16161e; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">']

    # Header
    svg.append(f'<text x="{w/2}" y="36" text-anchor="middle" fill="#ffffff" font-size="22" font-weight="700">Muhammad Ali Mosque — Mid-Frequency Focus (500 Hz &amp; 1000 Hz)</text>')
    svg.append(f'<text x="{w/2}" y="60" text-anchor="middle" fill="#9fa0b5" font-size="13">Detailed Reverberation Time (RT60m) Analysis &amp; Material Absorption Breakdown | V = 39,840 m³</text>')

    # -------------------------------------------------------------
    # LEFT PANEL: ZOOMED RT60 COMPARISON (500 Hz, 1000 Hz, RT60m)
    # -------------------------------------------------------------
    # Y-axis Grid lines & ticks (0.0s to 8.0s in 1.0s increments)
    for t in range(0, 9):
        y = margin["top"] + plot_h * (1.0 - t / max_t)
        svg.append(f'<line x1="{margin["left"]}" y1="{y}" x2="{margin["left"] + plot_w}" y2="{y}" stroke="#272738" stroke-width="1"/>')
        svg.append(f'<text x="{margin["left"] - 15}" y="{y + 4}" text-anchor="end" fill="#888899" font-size="12" font-weight="500">{t}.0s</text>')

    # Optimal Quran Recitation Zone (3.0s - 4.5s)
    opt_y1 = margin["top"] + plot_h * (1.0 - 4.5 / max_t)
    opt_y2 = margin["top"] + plot_h * (1.0 - 3.0 / max_t)
    svg.append(f'<rect x="{margin["left"]}" y="{opt_y1}" width="{plot_w}" height="{opt_y2 - opt_y1}" fill="rgba(46, 204, 113, 0.12)" stroke="#2ecc71" stroke-width="1" stroke-dasharray="4,4"/>')
    svg.append(f'<text x="{margin["left"] + 15}" y="{(opt_y1 + opt_y2)/2 + 4}" fill="#2ecc71" font-size="11" font-weight="600">Optimal Quran Chanting Target (3.0s - 4.5s)</text>')

    # Three evaluation columns: 500 Hz, 1000 Hz, and RT60m (Average)
    col_x = [
        margin["left"] + plot_w * 0.18,  # 500 Hz
        margin["left"] + plot_w * 0.50,  # 1000 Hz
        margin["left"] + plot_w * 0.82   # RT60m Mid Avg
    ]
    col_labels = ["500 Hz", "1000 Hz", "RT60m (Average)"]

    # Draw vertical category guides
    for x, lbl in zip(col_x, col_labels):
        svg.append(f'<line x1="{x}" y1="{margin["top"]}" x2="{x}" y2="{margin["top"] + plot_h}" stroke="#232332" stroke-width="1"/>')
        svg.append(f'<text x="{x}" y="{h - margin["bottom"] + 25}" text-anchor="middle" fill="#e0e0f0" font-size="14" font-weight="700">{lbl}</text>')

    # Data for the 3 columns: (Sabine Unocc, Eyring Unocc, Sabine Occ, Eyring Occ)
    col_data = [
        (u_500["t60_sabine_s"], u_500["t60_eyring_s"], o_500["t60_sabine_s"], o_500["t60_eyring_s"]),
        (u_1000["t60_sabine_s"], u_1000["t60_eyring_s"], o_1000["t60_sabine_s"], o_1000["t60_eyring_s"]),
        (sab_unocc_mid, eyr_unocc_mid, sab_occ_mid, eyr_occ_mid)
    ]

    bar_width = 18
    offsets = [-28, -9, 9, 28]  # Sab Unocc, Eyr Unocc, Sab Occ, Eyr Occ
    colors = ["#e67e22", "#f39c12", "#00d2d3", "#0abde3"]

    for cx, data_vals in zip(col_x, col_data):
        for val, off, col in zip(data_vals, offsets, colors):
            bx = cx + off - bar_width / 2
            by = margin["top"] + plot_h * (1.0 - val / max_t)
            bh = (margin["top"] + plot_h) - by
            # Bar with rounded top
            svg.append(f'<rect x="{bx}" y="{by}" width="{bar_width}" height="{bh}" rx="3" fill="{col}" opacity="0.88"/>')
            # Data label on top
            svg.append(f'<text x="{cx + off}" y="{by - 7}" text-anchor="middle" fill="{col}" font-size="11" font-weight="bold">{val}s</text>')

    # Left Panel Legend (clean horizontal bar at bottom left)
    leg_y = h - margin["bottom"] + 52
    svg.append(f'<rect x="{margin["left"]}" y="{leg_y}" width="{plot_w}" height="32" rx="4" fill="#1b1b26" stroke="#2c2c3e"/>')
    svg.append(f'<rect x="{margin["left"] + 15}" y="{leg_y + 11}" width="12" height="12" rx="2" fill="#e67e22"/>')
    svg.append(f'<text x="{margin["left"] + 32}" y="{leg_y + 21}" fill="#cccccc" font-size="11">Sabine (Unocc)</text>')
    svg.append(f'<rect x="{margin["left"] + 140}" y="{leg_y + 11}" width="12" height="12" rx="2" fill="#f39c12"/>')
    svg.append(f'<text x="{margin["left"] + 157}" y="{leg_y + 21}" fill="#cccccc" font-size="11">Eyring (Unocc)</text>')
    svg.append(f'<rect x="{margin["left"] + 265}" y="{leg_y + 11}" width="12" height="12" rx="2" fill="#00d2d3"/>')
    svg.append(f'<text x="{margin["left"] + 282}" y="{leg_y + 21}" fill="#cccccc" font-size="11">Sabine (Occ)</text>')
    svg.append(f'<rect x="{margin["left"] + 380}" y="{leg_y + 11}" width="12" height="12" rx="2" fill="#0abde3"/>')
    svg.append(f'<text x="{margin["left"] + 397}" y="{leg_y + 21}" fill="#cccccc" font-size="11">Eyring (Occ)</text>')

    # -------------------------------------------------------------
    # RIGHT PANEL: MATERIAL ABSORPTION AT 500 Hz & 1000 Hz
    # -------------------------------------------------------------
    rp_x = w - margin["right"] + 25  # 645 px
    rp_w = margin["right"] - 45      # 335 px
    rp_y = margin["top"]
    rp_h = plot_h + 32               # 472 px

    svg.append(f'<rect x="{rp_x}" y="{rp_y}" width="{rp_w}" height="{rp_h}" rx="6" fill="#1b1b26" stroke="#2c2c3e"/>')
    svg.append(f'<text x="{rp_x + rp_w/2}" y="{rp_y + 26}" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="700">Absorption Share at Mid Frequencies</text>')
    svg.append(f'<text x="{rp_x + rp_w/2}" y="{rp_y + 44}" text-anchor="middle" fill="#88889a" font-size="11">Total Equivalent Absorption Area A (m²)</text>')

    # Comparison metrics between 500 Hz & 1000 Hz
    card_y = rp_y + 60
    # 500 Hz Card
    svg.append(f'<rect x="{rp_x + 15}" y="{card_y}" width="{rp_w - 30}" height="80" rx="4" fill="#222230" stroke="#323245"/>')
    svg.append(f'<text x="{rp_x + 25}" y="{card_y + 22}" fill="#f1c40f" font-size="13" font-weight="700">500 Hz Band Analysis</text>')
    svg.append(f'<text x="{rp_x + 25}" y="{card_y + 42}" fill="#cccccc" font-size="11">Total Absorption A (Unocc): <tspan fill="#ffaa55" font-weight="bold">948.4 m²</tspan></text>')
    svg.append(f'<text x="{rp_x + 25}" y="{card_y + 60}" fill="#cccccc" font-size="11">Total Absorption A (Occ):   <tspan fill="#55ffff" font-weight="bold">1,247.4 m²</tspan> (+31.5%)</text>')
    svg.append(f'<text x="{rp_x + rp_w - 30}" y="{card_y + 42}" text-anchor="end" fill="#ffaa55" font-size="12" font-weight="bold">Sab: 7.01s</text>')
    svg.append(f'<text x="{rp_x + rp_w - 30}" y="{card_y + 60}" text-anchor="end" fill="#55ffff" font-size="12" font-weight="bold">Sab: 4.80s</text>')

    # 1000 Hz Card
    card_y2 = card_y + 90
    svg.append(f'<rect x="{rp_x + 15}" y="{card_y2}" width="{rp_w - 30}" height="80" rx="4" fill="#222230" stroke="#323245"/>')
    svg.append(f'<text x="{rp_x + 25}" y="{card_y2 + 22}" fill="#f1c40f" font-size="13" font-weight="700">1000 Hz Band Analysis</text>')
    svg.append(f'<text x="{rp_x + 25}" y="{card_y2 + 42}" fill="#cccccc" font-size="11">Total Absorption A (Unocc): <tspan fill="#ffaa55" font-weight="bold">1,169.6 m²</tspan></text>')
    svg.append(f'<text x="{rp_x + 25}" y="{card_y2 + 60}" fill="#cccccc" font-size="11">Total Absorption A (Occ):   <tspan fill="#55ffff" font-weight="bold">1,589.9 m²</tspan> (+35.9%)</text>')
    svg.append(f'<text x="{rp_x + rp_w - 30}" y="{card_y2 + 42}" text-anchor="end" fill="#ffaa55" font-size="12" font-weight="bold">Sab: 4.77s</text>')
    svg.append(f'<text x="{rp_x + rp_w - 30}" y="{card_y2 + 60}" text-anchor="end" fill="#55ffff" font-size="12" font-weight="bold">Sab: 3.63s</text>')

    # Material Contribution Breakdown (Horizontal proportion bars)
    mat_y = card_y2 + 95
    svg.append(f'<text x="{rp_x + 15}" y="{mat_y + 12}" fill="#ffffff" font-size="12" font-weight="700">Surface Absorption Contribution (Occupied):</text>')

    # At 1000 Hz Occupied:
    # Carpet: 1260.8 m2 (79.3%)
    # Limestone: 119.2 m2 (7.5%)
    # Plaster: 130.0 m2 (8.2%)
    # Marble: 62.4 m2 (3.9%)
    # Others: ~18 m2 (1.1%)
    items = [
        ("Wool Prayer Carpet + Worshippers", 79.3, "#00d2d3"),
        ("Dome Historic Plaster", 8.2, "#feca57"),
        ("Dressed Limestone Piers/Arches", 7.5, "#ff9ff3"),
        ("Alabaster / Marble Revetment", 3.9, "#54a0ff"),
        ("Glazing &amp; Hardwood", 1.1, "#5f27cd")
    ]

    cur_y = mat_y + 30
    for name, pct, col in items:
        svg.append(f'<text x="{rp_x + 15}" y="{cur_y}" fill="#d0d0d8" font-size="11">{name}</text>')
        svg.append(f'<text x="{rp_x + rp_w - 15}" y="{cur_y}" text-anchor="end" fill="{col}" font-size="11" font-weight="bold">{pct}%</text>')
        # Bar track
        svg.append(f'<rect x="{rp_x + 15}" y="{cur_y + 4}" width="{rp_w - 30}" height="7" rx="2" fill="#272736"/>')
        svg.append(f'<rect x="{rp_x + 15}" y="{cur_y + 4}" width="{(rp_w - 30) * (pct / 100.0)}" height="7" rx="2" fill="{col}"/>')
        cur_y += 24

    # Explanatory Note box
    note_y = cur_y + 10
    svg.append(f'<rect x="{rp_x + 15}" y="{note_y}" width="{rp_w - 30}" height="55" rx="4" fill="#14141e" stroke="#2d2d3e"/>')
    svg.append(f'<text x="{rp_x + 25}" y="{note_y + 18}" fill="#2ecc71" font-size="11" font-weight="bold">Why 500 Hz &amp; 1000 Hz Define RT60m:</text>')
    svg.append(f'<text x="{rp_x + 25}" y="{note_y + 34}" fill="#9999a8" font-size="10">These bands contain human vocal fundamentals.</text>')
    svg.append(f'<text x="{rp_x + 25}" y="{note_y + 48}" fill="#9999a8" font-size="10">Carpet dominates absorption, keeping speech legible.</text>')

    svg.append('</svg>')

    out_path = os.path.join(REPORTS_DIR, "mosque_rt60_mid_frequency_focus.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Focused Mid-Frequency SVG created successfully at: {out_path}")
    return out_path


if __name__ == "__main__":
    build_focused_mid_frequency_svg()
