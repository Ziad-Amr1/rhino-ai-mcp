"""Generates dedicated Sabine Reverberation Time (RT60) charts for Muhammad Ali Mosque."""

import os
import sys

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from mosque_acoustic_data import OCTAVE_BANDS
from pachyderm_simulation import calculate_analytical_acoustics

REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def build_sabine_rt60_svg():
    unocc = calculate_analytical_acoustics(occupied=False)
    occ = calculate_analytical_acoustics(occupied=True)

    bands = OCTAVE_BANDS
    sabine_unocc = [r["t60_sabine_s"] for r in unocc["octave_band_results"]]
    sabine_occ = [r["t60_sabine_s"] for r in occ["octave_band_results"]]
    eyring_unocc = [r["t60_eyring_s"] for r in unocc["octave_band_results"]]
    eyring_occ = [r["t60_eyring_s"] for r in occ["octave_band_results"]]

    rt_mid_sab_unocc = unocc["summary"]["reverberation_time_t60_mid_sabine_s"]
    rt_mid_sab_occ = occ["summary"]["reverberation_time_t60_mid_sabine_s"]

    # Extended canvas dimensions for crisp legibility
    w, h = 960, 580
    margin = {"top": 80, "right": 70, "bottom": 85, "left": 80}
    plot_w = w - margin["left"] - margin["right"]
    plot_h = h - margin["top"] - margin["bottom"]

    # Scaled to 24s so all points (up to 20.34s) have clean headroom
    max_rt = 24.0
    x_coords = [margin["left"] + i * (plot_w / (len(bands) - 1)) for i in range(len(bands))]
    y_sab_unocc = [margin["top"] + plot_h * (1.0 - rt / max_rt) for rt in sabine_unocc]
    y_sab_occ = [margin["top"] + plot_h * (1.0 - rt / max_rt) for rt in sabine_occ]
    y_ey_unocc = [margin["top"] + plot_h * (1.0 - rt / max_rt) for rt in eyring_unocc]
    y_ey_occ = [margin["top"] + plot_h * (1.0 - rt / max_rt) for rt in eyring_occ]

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="background:#16161e; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">']

    # Title & Subtitle
    svg.append(f'<text x="{w/2}" y="35" text-anchor="middle" fill="#ffffff" font-size="21" font-weight="700">Muhammad Ali Mosque - Sabine Reverberation Time T60</text>')
    svg.append(f'<text x="{w/2}" y="58" text-anchor="middle" fill="#a0a0b2" font-size="13">Formula: T60 = 0.161 × V / (A + 4mV) | Hall Volume V = 39,840 m³ | Surface S = 11,450 m²</text>')

    # Grid lines & Y Axis labels (0s to 24s in 2s increments)
    for val in range(0, 25, 2):
        y = margin["top"] + plot_h * (1.0 - val / max_rt)
        svg.append(f'<line x1="{margin["left"]}" y1="{y}" x2="{w - margin["right"]}" y2="{y}" stroke="#262635" stroke-width="1"/>')
        svg.append(f'<text x="{margin["left"] - 15}" y="{y + 4}" text-anchor="end" fill="#78788c" font-size="12" font-weight="500">{val}.0s</text>')

    # X axis vertical grid lines & labels
    for i, freq in enumerate(bands):
        x = x_coords[i]
        svg.append(f'<line x1="{x}" y1="{margin["top"]}" x2="{x}" y2="{margin["top"] + plot_h}" stroke="#222230" stroke-width="1"/>')
        svg.append(f'<text x="{x}" y="{h - margin["bottom"] + 25}" text-anchor="middle" fill="#d0d0e0" font-size="13" font-weight="600">{freq} Hz</text>')

    # Target optimal acoustic band for Monumental Mosque Quran Recitation (3.0s - 4.5s)
    target_y1 = margin["top"] + plot_h * (1.0 - 4.5 / max_rt)
    target_y2 = margin["top"] + plot_h * (1.0 - 3.0 / max_rt)
    svg.append(f'<rect x="{margin["left"]}" y="{target_y1}" width="{plot_w}" height="{target_y2 - target_y1}" fill="rgba(46, 204, 113, 0.12)" stroke="#2ecc71" stroke-width="1" stroke-dasharray="4,4"/>')
    svg.append(f'<text x="{margin["left"] + 15}" y="{(target_y1 + target_y2)/2 + 4}" text-anchor="start" fill="#2ecc71" font-size="12" font-weight="600">Optimal Quran Chanting Zone (3.0s - 4.5s)</text>')

    # Mid-frequency highlight zone (500 Hz to 1000 Hz)
    mid_x1 = x_coords[3]
    mid_x2 = x_coords[4]
    svg.append(f'<rect x="{mid_x1}" y="{margin["top"]}" width="{mid_x2 - mid_x1}" height="{plot_h}" fill="rgba(255, 255, 255, 0.03)" stroke="none"/>')
    svg.append(f'<text x="{(mid_x1 + mid_x2)/2}" y="{margin["top"] + 20}" text-anchor="middle" fill="#f1c40f" font-size="11" font-weight="bold">RT60m Mid Band</text>')

    # Eyring Reference lines (dashed)
    pts_ey_unocc = " ".join(f"{x},{y}" for x, y in zip(x_coords, y_ey_unocc))
    svg.append(f'<polyline points="{pts_ey_unocc}" fill="none" stroke="#e67e22" stroke-width="1.8" stroke-dasharray="5,5" opacity="0.55"/>')
    pts_ey_occ = " ".join(f"{x},{y}" for x, y in zip(x_coords, y_ey_occ))
    svg.append(f'<polyline points="{pts_ey_occ}" fill="none" stroke="#00d2d3" stroke-width="1.8" stroke-dasharray="5,5" opacity="0.55"/>')

    # Sabine Unoccupied (Solid Orange with Clean Labels)
    pts_sab_unocc = " ".join(f"{x},{y}" for x, y in zip(x_coords, y_sab_unocc))
    svg.append(f'<polyline points="{pts_sab_unocc}" fill="none" stroke="#e67e22" stroke-width="3.5"/>')
    for x, y, rt in zip(x_coords, y_sab_unocc, sabine_unocc):
        svg.append(f'<circle cx="{x}" cy="{y}" r="5.5" fill="#e67e22" stroke="#ffffff" stroke-width="2"/>')
        svg.append(f'<text x="{x}" y="{y - 12}" text-anchor="middle" fill="#ffaa55" font-size="12" font-weight="bold">{rt}s</text>')

    # Sabine Occupied (Solid Cyan with Clean Labels)
    pts_sab_occ = " ".join(f"{x},{y}" for x, y in zip(x_coords, y_sab_occ))
    svg.append(f'<polyline points="{pts_sab_occ}" fill="none" stroke="#00d2d3" stroke-width="3.5"/>')
    for x, y, rt in zip(x_coords, y_sab_occ, sabine_occ):
        svg.append(f'<circle cx="{x}" cy="{y}" r="5.5" fill="#00d2d3" stroke="#ffffff" stroke-width="2"/>')
        svg.append(f'<text x="{x}" y="{y + 20}" text-anchor="middle" fill="#55ffff" font-size="12" font-weight="bold">{rt}s</text>')

    # LEGEND MOVED TO TOP-RIGHT (Clean area where curves have dropped down)
    legend_w = 320
    legend_h = 105
    legend_x = w - margin["right"] - legend_w - 10
    legend_y = margin["top"] + 15
    svg.append(f'<rect x="{legend_x}" y="{legend_y}" width="{legend_w}" height="{legend_h}" rx="6" fill="#14141e" stroke="#2e2e40" stroke-width="1.2"/>')

    svg.append(f'<line x1="{legend_x + 15}" y1="{legend_y + 24}" x2="{legend_x + 45}" y2="{legend_y + 24}" stroke="#e67e22" stroke-width="3.5"/>')
    svg.append(f'<circle cx="{legend_x + 30}" cy="{legend_y + 24}" r="4" fill="#ffffff"/>')
    svg.append(f'<text x="{legend_x + 55}" y="{legend_y + 28}" fill="#ffffff" font-size="12" font-weight="600">Sabine T60 - Unoccupied (Empty Hall)</text>')

    svg.append(f'<line x1="{legend_x + 15}" y1="{legend_y + 48}" x2="{legend_x + 45}" y2="{legend_y + 48}" stroke="#00d2d3" stroke-width="3.5"/>')
    svg.append(f'<circle cx="{legend_x + 30}" cy="{legend_y + 48}" r="4" fill="#ffffff"/>')
    svg.append(f'<text x="{legend_x + 55}" y="{legend_y + 52}" fill="#ffffff" font-size="12" font-weight="600">Sabine T60 - Occupied (Congregation)</text>')

    svg.append(f'<line x1="{legend_x + 15}" y1="{legend_y + 72}" x2="{legend_x + 45}" y2="{legend_y + 72}" stroke="#e67e22" stroke-width="2" stroke-dasharray="4,4" opacity="0.6"/>')
    svg.append(f'<text x="{legend_x + 55}" y="{legend_y + 76}" fill="#9999aa" font-size="11">Eyring T60 - Unoccupied (Reference)</text>')

    svg.append(f'<line x1="{legend_x + 15}" y1="{legend_y + 92}" x2="{legend_x + 45}" y2="{legend_y + 92}" stroke="#00d2d3" stroke-width="2" stroke-dasharray="4,4" opacity="0.6"/>')
    svg.append(f'<text x="{legend_x + 55}" y="{legend_y + 96}" fill="#9999aa" font-size="11">Eyring T60 - Occupied (Reference)</text>')

    # KPI Callout Cards (Bottom)
    svg.append(f'<rect x="{margin["left"] + 20}" y="{h - margin["bottom"] + 42}" width="370" height="34" rx="5" fill="#20202c" stroke="#353545"/>')
    svg.append(f'<text x="{margin["left"] + 35}" y="{h - margin["bottom"] + 64}" fill="#ffaa55" font-size="13" font-weight="bold">Sabine RT60m (Unoccupied): {rt_mid_sab_unocc} s</text>')
    svg.append(f'<text x="{margin["left"] + 265}" y="{h - margin["bottom"] + 64}" fill="#a0a0b2" font-size="11">(Eyring: {unocc["summary"]["reverberation_time_t60_mid_eyring_s"]} s)</text>')

    svg.append(f'<rect x="{margin["left"] + 420}" y="{h - margin["bottom"] + 42}" width="370" height="34" rx="5" fill="#20202c" stroke="#353545"/>')
    svg.append(f'<text x="{margin["left"] + 435}" y="{h - margin["bottom"] + 64}" fill="#55ffff" font-size="13" font-weight="bold">Sabine RT60m (Occupied): {rt_mid_sab_occ} s</text>')
    svg.append(f'<text x="{margin["left"] + 655}" y="{h - margin["bottom"] + 64}" fill="#a0a0b2" font-size="11">(Eyring: {occ["summary"]["reverberation_time_t60_mid_eyring_s"]} s)</text>')

    svg.append('</svg>')

    out_path = os.path.join(REPORTS_DIR, "mosque_sabine_rt60_chart.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Sabine RT60 SVG created successfully at: {out_path}")
    return out_path


if __name__ == "__main__":
    build_sabine_rt60_svg()
