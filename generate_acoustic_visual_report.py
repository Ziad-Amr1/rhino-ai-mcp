"""Generates clean SVG acoustic visual charts for Muhammad Ali Mosque."""

import os
import sys

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from mosque_acoustic_data import OCTAVE_BANDS, ACOUSTIC_MATERIALS
from pachyderm_simulation import calculate_analytical_acoustics

REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_rt60_svg():
    unocc = calculate_analytical_acoustics(occupied=False)
    occ = calculate_analytical_acoustics(occupied=True)

    bands = OCTAVE_BANDS
    unocc_rt = [r["t60_eyring_s"] for r in unocc["octave_band_results"]]
    occ_rt = [r["t60_eyring_s"] for r in occ["octave_band_results"]]

    w, h = 800, 450
    margin = {"top": 60, "right": 50, "bottom": 60, "left": 70}
    plot_w = w - margin["left"] - margin["right"]
    plot_h = h - margin["top"] - margin["bottom"]

    max_rt = 10.0
    x_coords = [margin["left"] + i * (plot_w / (len(bands) - 1)) for i in range(len(bands))]
    y_unocc = [margin["top"] + plot_h * (1.0 - rt / max_rt) for rt in unocc_rt]
    y_occ = [margin["top"] + plot_h * (1.0 - rt / max_rt) for rt in occ_rt]

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="background:#1e1e24; font-family:sans-serif;">']
    svg.append(f'<text x="{w/2}" y="35" text-anchor="middle" fill="#ffffff" font-size="20" font-weight="bold">Muhammad Ali Mosque - Reverberation Time T60 (Eyring)</text>')

    # Grid lines
    for val in range(0, 11, 2):
        y = margin["top"] + plot_h * (1.0 - val / max_rt)
        svg.append(f'<line x1="{margin["left"]}" y1="{y}" x2="{w - margin["right"]}" y2="{y}" stroke="#33333d" stroke-width="1"/>')
        svg.append(f'<text x="{margin["left"] - 15}" y="{y + 5}" text-anchor="end" fill="#888899" font-size="12">{val}s</text>')

    # X axis labels
    for i, freq in enumerate(bands):
        x = x_coords[i]
        svg.append(f'<line x1="{x}" y1="{margin["top"]}" x2="{x}" y2="{margin["top"] + plot_h}" stroke="#2a2a35" stroke-width="1"/>')
        svg.append(f'<text x="{x}" y="{h - margin["bottom"] + 25}" text-anchor="middle" fill="#cccccc" font-size="12">{freq} Hz</text>')

    # Target optimal Quranic chanting & speech bands
    target_y1 = margin["top"] + plot_h * (1.0 - 4.5 / max_rt)
    target_y2 = margin["top"] + plot_h * (1.0 - 3.0 / max_rt)
    svg.append(f'<rect x="{margin["left"]}" y="{target_y1}" width="{plot_w}" height="{target_y2 - target_y1}" fill="rgba(46, 204, 113, 0.15)" stroke="none"/>')
    svg.append(f'<text x="{w - margin["right"] - 10}" y="{(target_y1 + target_y2)/2 + 4}" text-anchor="end" fill="#2ecc71" font-size="11">Optimal Chanting Zone (3.0s - 4.5s)</text>')

    # Unoccupied Path (Orange)
    pts_unocc = " ".join(f"{x},{y}" for x, y in zip(x_coords, y_unocc))
    svg.append(f'<polyline points="{pts_unocc}" fill="none" stroke="#e67e22" stroke-width="3.5"/>')
    for x, y, rt in zip(x_coords, y_unocc, unocc_rt):
        svg.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#e67e22" stroke="#ffffff" stroke-width="1.5"/>')
        svg.append(f'<text x="{x}" y="{y - 10}" text-anchor="middle" fill="#e67e22" font-size="11" font-weight="bold">{rt}s</text>')

    # Occupied Path (Cyan)
    pts_occ = " ".join(f"{x},{y}" for x, y in zip(x_coords, y_occ))
    svg.append(f'<polyline points="{pts_occ}" fill="none" stroke="#00d2d3" stroke-width="3.5"/>')
    for x, y, rt in zip(x_coords, y_occ, occ_rt):
        svg.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#00d2d3" stroke="#ffffff" stroke-width="1.5"/>')
        svg.append(f'<text x="{x}" y="{y + 18}" text-anchor="middle" fill="#00d2d3" font-size="11" font-weight="bold">{rt}s</text>')

    # Legend
    svg.append(f'<rect x="{margin["left"] + 20}" y="{margin["top"] + 15}" width="280" height="50" rx="5" fill="#141419" stroke="#33333d"/>')
    svg.append(f'<line x1="{margin["left"] + 35}" y1="{margin["top"] + 30}" x2="{margin["left"] + 65}" y2="{margin["top"] + 30}" stroke="#e67e22" stroke-width="3"/>')
    svg.append(f'<text x="{margin["left"] + 75}" y="{margin["top"] + 34}" fill="#ffffff" font-size="12">Unoccupied Mosque (Empty Hall)</text>')
    svg.append(f'<line x1="{margin["left"] + 35}" y1="{margin["top"] + 50}" x2="{margin["left"] + 65}" y2="{margin["top"] + 50}" stroke="#00d2d3" stroke-width="3"/>')
    svg.append(f'<text x="{margin["left"] + 75}" y="{margin["top"] + 54}" fill="#ffffff" font-size="12">Occupied (Full Congregation)</text>')

    svg.append('</svg>')

    out_path = os.path.join(REPORTS_DIR, "mosque_acoustic_reverberation_chart.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated RT60 chart at: {out_path}")
    return out_path


if __name__ == "__main__":
    generate_rt60_svg()
