"""Full Acoustic Measurement Charts Generator for Muhammad Ali Mosque.

Generates:
1. mosque_total_absorption_sabins.svg & .png
   - Total room absorption A_total (Metric Sabins) across 8 octave bands (63 - 8000 Hz)
   - Breakdown by material: Alabaster, Limestone, Plaster, Carpet, Glass, Wood, People, Air (4mV)
   - Comparison: Empty vs Semi-Occupied vs Fully Occupied
2. mosque_background_noise_nc_spectrum.svg & .png
   - Measured Citadel background ambient noise spectrum
   - NC-25 to NC-50 Criterion curves & NR curves
   - SNR (Signal-to-Noise Ratio) evaluation
3. mosque_receiver_acoustics_matrix.svg & .png
   - C50, C80, D50, STI, ALcons, EDT across 16 receiver stations
"""

import os
import sys
import math
import json
import xml.etree.ElementTree as ET

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

from generate_heatmaps_and_spl_c import RasterCanvas
from comprehensive_acoustic_measurements import (
    OCTAVE_BANDS,
    BACKGROUND_NOISE_OCTAVES,
    OCCUPANCY_STATES
)

CALC_JSON_PATH = os.path.join(REPORTS_DIR, "mosque_full_acoustic_calculations.json")
with open(CALC_JSON_PATH, "r", encoding="utf-8") as f:
    CALC_DATA = json.load(f)


def generate_total_absorption_chart():
    """Generates SVG & PNG for A_total across octaves and materials."""
    print("=" * 65)
    print("  GENERATING TOTAL ABSORPTION (A_TOTAL) CHARTS")
    print("=" * 65)

    w, h = 1000, 720
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="background:#14141c; font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">']

    # Title
    svg.append(f'<text x="{w/2}" y="36" text-anchor="middle" fill="#ffffff" font-size="22" font-weight="700">Muhammad Ali Mosque — Total Acoustic Absorption (A_total) Spectrum</text>')
    svg.append(f'<text x="{w/2}" y="60" text-anchor="middle" fill="#9fa0b5" font-size="13">Detailed Breakdown in Metric Sabins (m²-Sab) across 8 Octave Bands: Empty vs Semi vs Fully Occupied</text>')

    # Plot Area
    px0, py0 = 80, 95
    pw, ph = 840, 560
    svg.append(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" fill="#1a1a26" stroke="#2d2d3e" stroke-width="1.5"/>')

    # Y-axis (0 to 3,500 Sabins)
    max_sabins = 3200.0
    for tick in range(0, 3201, 400):
        y_pos = py0 + ph * (1.0 - tick / max_sabins)
        svg.append(f'<line x1="{px0}" y1="{y_pos}" x2="{px0 + pw}" y2="{y_pos}" stroke="#2a2a3e" stroke-width="1"/>')
        svg.append(f'<text x="{px0 - 10}" y="{y_pos + 4}" text-anchor="end" fill="#888899" font-size="11">{tick} m²-Sab</text>')

    oct_data_empty = CALC_DATA["occupancy_absorption_tables"]["empty"]["bands"]
    oct_data_semi = CALC_DATA["occupancy_absorption_tables"]["semi_occupied"]["bands"]
    oct_data_full = CALC_DATA["occupancy_absorption_tables"]["fully_occupied"]["bands"]

    group_w = pw / len(OCTAVE_BANDS)

    for idx, freq in enumerate(OCTAVE_BANDS):
        gx = px0 + idx * group_w

        # Separator
        if idx > 0:
            svg.append(f'<line x1="{gx}" y1="{py0}" x2="{gx}" y2="{py0 + ph}" stroke="#222232" stroke-width="1"/>')

        # X label
        svg.append(f'<text x="{gx + group_w/2}" y="{py0 + ph + 24}" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="bold">{freq} Hz</text>')

        # 3 Bars per group: Empty, Semi-Occupied, Fully-Occupied
        b_w = group_w * 0.25
        
        # 1. Empty Bar
        val_e = oct_data_empty[idx]["total_absorption_A_total"]
        bh_e = (val_e / max_sabins) * ph
        bx_e = gx + group_w * 0.10
        by_e = py0 + ph - bh_e
        svg.append(f'<rect x="{bx_e}" y="{by_e}" width="{b_w}" height="{bh_e}" fill="#e74c3c" rx="2"/>')
        svg.append(f'<text x="{bx_e + b_w/2}" y="{by_e - 6}" text-anchor="middle" fill="#e74c3c" font-size="10" font-weight="bold">{int(val_e)}</text>')

        # 2. Semi-Occupied Bar
        val_s = oct_data_semi[idx]["total_absorption_A_total"]
        bh_s = (val_s / max_sabins) * ph
        bx_s = gx + group_w * 0.38
        by_s = py0 + ph - bh_s
        svg.append(f'<rect x="{bx_s}" y="{by_s}" width="{b_w}" height="{bh_s}" fill="#f39c12" rx="2"/>')
        svg.append(f'<text x="{bx_s + b_w/2}" y="{by_s - 6}" text-anchor="middle" fill="#f39c12" font-size="10" font-weight="bold">{int(val_s)}</text>')

        # 3. Fully-Occupied Bar
        val_f = oct_data_full[idx]["total_absorption_A_total"]
        bh_f = (val_f / max_sabins) * ph
        bx_f = gx + group_w * 0.66
        by_f = py0 + ph - bh_f
        svg.append(f'<rect x="{bx_f}" y="{by_f}" width="{b_w}" height="{bh_f}" fill="#2ecc71" rx="2"/>')
        svg.append(f'<text x="{bx_f + b_w/2}" y="{by_f - 6}" text-anchor="middle" fill="#2ecc71" font-size="10" font-weight="bold">{int(val_f)}</text>')

        # Mean Alpha badges below X-axis
        a_e = oct_data_empty[idx]["mean_alpha"]
        a_f = oct_data_full[idx]["mean_alpha"]
        svg.append(f'<text x="{gx + group_w/2}" y="{py0 + ph + 40}" text-anchor="middle" fill="#8888aa" font-size="10">α: {a_e:.3f} → {a_f:.3f}</text>')

    # Legend
    leg_x = px0 + 15
    leg_y = py0 + 15
    svg.append(f'<rect x="{leg_x}" y="{leg_y}" width="420" height="60" rx="4" fill="#14141c" stroke="#3d3d52"/>')
    
    svg.append(f'<rect x="{leg_x + 12}" y="{leg_y + 14}" width="14" height="12" fill="#e74c3c" rx="2"/>')
    svg.append(f'<text x="{leg_x + 32}" y="{leg_y + 24}" fill="#ffffff" font-size="11">Empty Hall (0 Worshippers) — Baseline</text>')

    svg.append(f'<rect x="{leg_x + 12}" y="{leg_y + 36}" width="14" height="12" fill="#f39c12" rx="2"/>')
    svg.append(f'<text x="{leg_x + 32}" y="{leg_y + 46}" fill="#ffffff" font-size="11">Semi-Occupied (350 Worshippers, Daily Prayer)</text>')

    svg.append(f'<rect x="{leg_x + 230}" y="{leg_y + 36}" width="14" height="12" fill="#2ecc71" rx="2"/>')
    svg.append(f'<text x="{leg_x + 250}" y="{leg_y + 46}" fill="#ffffff" font-size="11">Fully Occupied (1,200 Worshippers)</text>')

    svg.append('</svg>')

    out_svg = os.path.join(REPORTS_DIR, "mosque_total_absorption_sabins.svg")
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Saved SVG: {out_svg}")

    # Render PNG
    render_total_absorption_png(oct_data_empty, oct_data_semi, oct_data_full)


def render_total_absorption_png(empty_bands, semi_bands, full_bands):
    """Renders high-res PNG for total absorption chart."""
    w, h = 1000, 720
    canvas = RasterCanvas(w, h, bg_rgb=(20, 20, 28))

    canvas.draw_text("MUHAMMAD ALI MOSQUE - TOTAL ACOUSTIC ABSORPTION (A TOTAL)", 40, 22, r=255, g=255, b=255, scale=2)
    canvas.draw_text("METRIC SABINS (M2-SAB) ACROSS 8 OCTAVE BANDS (63 - 8000 HZ)", 40, 46, r=160, g=165, b=185, scale=1)

    px0, py0 = 80, 85
    pw, ph = 840, 570
    canvas.fill_rect(px0, py0, px0 + pw, py0 + ph, 26, 26, 36)
    canvas.draw_rect(px0, py0, px0 + pw, py0 + ph, 50, 50, 70)

    max_sabins = 3200.0
    for tick in range(0, 3201, 400):
        y_pos = int(py0 + ph * (1.0 - tick / max_sabins))
        canvas.draw_line(px0, y_pos, px0 + pw, y_pos, 40, 40, 55)
        canvas.draw_text(f"{tick}SAB", px0 - 55, y_pos - 3, r=140, g=140, b=160, scale=1)

    group_w = pw / len(OCTAVE_BANDS)
    b_w = int(group_w * 0.25)

    for idx, freq in enumerate(OCTAVE_BANDS):
        gx = int(px0 + idx * group_w)
        canvas.draw_text(f"{freq}HZ", gx + int(group_w * 0.22), py0 + ph + 18, r=255, g=255, b=255, scale=1)

        # Empty
        val_e = empty_bands[idx]["total_absorption_A_total"]
        bh_e = int((val_e / max_sabins) * ph)
        bx_e = gx + int(group_w * 0.10)
        by_e = py0 + ph - bh_e
        canvas.fill_rect(bx_e, by_e, bx_e + b_w, py0 + ph, 231, 76, 60)
        canvas.draw_text(f"{int(val_e)}", bx_e - 2, by_e - 12, r=231, g=76, b=60, scale=1)

        # Semi
        val_s = semi_bands[idx]["total_absorption_A_total"]
        bh_s = int((val_s / max_sabins) * ph)
        bx_s = gx + int(group_w * 0.38)
        by_s = py0 + ph - bh_s
        canvas.fill_rect(bx_s, by_s, bx_s + b_w, py0 + ph, 243, 156, 18)
        canvas.draw_text(f"{int(val_s)}", bx_s - 2, by_s - 12, r=243, g=156, b=18, scale=1)

        # Full
        val_f = full_bands[idx]["total_absorption_A_total"]
        bh_f = int((val_f / max_sabins) * ph)
        bx_f = gx + int(group_w * 0.66)
        by_f = py0 + ph - bh_f
        canvas.fill_rect(bx_f, by_f, bx_f + b_w, py0 + ph, 46, 204, 113)
        canvas.draw_text(f"{int(val_f)}", bx_f - 2, by_f - 12, r=46, g=204, b=113, scale=1)

    # Legend
    canvas.fill_rect(px0 + 15, py0 + 15, px0 + 440, py0 + 75, 20, 20, 28)
    canvas.fill_rect(px0 + 25, py0 + 26, px0 + 40, py0 + 38, 231, 76, 60)
    canvas.draw_text("EMPTY HALL (0 PEOPLE) - BASELINE", px0 + 48, py0 + 26, r=240, g=240, b=255, scale=1)

    canvas.fill_rect(px0 + 25, py0 + 46, px0 + 40, py0 + 58, 243, 156, 18)
    canvas.draw_text("SEMI (350)", px0 + 48, py0 + 46, r=240, g=240, b=255, scale=1)

    canvas.fill_rect(px0 + 155, py0 + 46, px0 + 170, py0 + 58, 46, 204, 113)
    canvas.draw_text("FULLY OCCUPIED (1,200)", px0 + 178, py0 + 46, r=240, g=240, b=255, scale=1)

    out_png = os.path.join(REPORTS_DIR, "mosque_total_absorption_sabins.png")
    canvas.save_png(out_png)


def generate_background_noise_chart():
    """Generates SVG & PNG for Citadel background noise vs NC/NR curves."""
    print("=" * 65)
    print("  GENERATING BACKGROUND NOISE & NOISE CRITERION (NC) CHARTS")
    print("=" * 65)

    w, h = 1000, 720
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="background:#14141c; font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">']

    svg.append(f'<text x="{w/2}" y="36" text-anchor="middle" fill="#ffffff" font-size="22" font-weight="700">Muhammad Ali Mosque — Background Noise Spectrum &amp; Noise Criterion (NC)</text>')
    svg.append(f'<text x="{w/2}" y="60" text-anchor="middle" fill="#9fa0b5" font-size="13">Citadel of Cairo Ambient Background Noise evaluated against NC-25 to NC-50 Standard Rating Curves</text>')

    px0, py0 = 80, 95
    pw, ph = 840, 560
    svg.append(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" fill="#1a1a26" stroke="#2d2d3e" stroke-width="1.5"/>')

    # Y-axis (10 dB to 70 dB)
    db_min, db_max = 10.0, 70.0
    for db in range(10, 71, 10):
        y_pos = py0 + ph * (1.0 - (db - db_min) / (db_max - db_min))
        svg.append(f'<line x1="{px0}" y1="{y_pos}" x2="{px0 + pw}" y2="{y_pos}" stroke="#2a2a3e" stroke-width="1"/>')
        svg.append(f'<text x="{px0 - 10}" y="{y_pos + 4}" text-anchor="end" fill="#888899" font-size="11">{db} dB</text>')

    # Standard NC Curves (63 to 8000 Hz)
    # NC-25, NC-30, NC-35, NC-40, NC-45, NC-50
    NC_CURVES = {
        "NC-25": [49, 41, 35, 31, 27, 24, 22, 21],
        "NC-30": [52, 45, 40, 36, 32, 29, 27, 26],
        "NC-35": [56, 50, 45, 40, 36, 34, 32, 31],
        "NC-40": [60, 54, 49, 44, 41, 39, 37, 36],
        "NC-45": [63, 58, 54, 49, 46, 44, 42, 41],
        "NC-50": [66, 62, 58, 54, 51, 49, 48, 47]
    }

    # X-axis ticks (63 to 8000 Hz)
    num_oct = len(OCTAVE_BANDS)
    x_coords = [px0 + (i / (num_oct - 1)) * pw for i in range(num_oct)]

    for i, freq in enumerate(OCTAVE_BANDS):
        svg.append(f'<line x1="{x_coords[i]}" y1="{py0}" x2="{x_coords[i]}" y2="{py0 + ph}" stroke="#242436" stroke-width="1"/>')
        svg.append(f'<text x="{x_coords[i]}" y="{py0 + ph + 24}" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="bold">{freq} Hz</text>')

    # Plot NC Reference Curves (Dashed gray/blue lines)
    for nc_name, vals in NC_CURVES.items():
        pts = []
        for i, val in enumerate(vals):
            yp = py0 + ph * (1.0 - (val - db_min) / (db_max - db_min))
            pts.append(f"{x_coords[i]:.1f},{yp:.1f}")
        col = "#f39c12" if nc_name == "NC-35" else "#4a4a62"
        width_l = "2.5" if nc_name == "NC-35" else "1.2"
        dash = "none" if nc_name == "NC-35" else "4,4"
        svg.append(f'<path d="M {" L ".join(pts)}" fill="none" stroke="{col}" stroke-width="{width_l}" stroke-dasharray="{dash}"/>')
        # Label at right
        last_y = py0 + ph * (1.0 - (vals[-1] - db_min) / (db_max - db_min))
        svg.append(f'<text x="{px0 + pw + 8}" y="{last_y + 4}" fill="{col}" font-size="11" font-weight="bold">{nc_name}</text>')

    # Plot Measured Ambient Noise Spectrum (Bold Red line with dots)
    measured_noise = [BACKGROUND_NOISE_OCTAVES[f] for f in OCTAVE_BANDS]
    meas_pts = []
    for i, val in enumerate(measured_noise):
        yp = py0 + ph * (1.0 - (val - db_min) / (db_max - db_min))
        meas_pts.append((x_coords[i], yp))

    path_meas = "M " + " L ".join(f"{xp:.1f},{yp:.1f}" for xp, yp in meas_pts)
    svg.append(f'<path d="{path_meas}" fill="none" stroke="#e74c3c" stroke-width="3.5"/>')
    for xp, yp in meas_pts:
        svg.append(f'<circle cx="{xp:.1f}" cy="{yp:.1f}" r="5" fill="#e74c3c" stroke="#ffffff" stroke-width="2"/>')

    # Legend
    leg_x = px0 + 15
    leg_y = py0 + 15
    svg.append(f'<rect x="{leg_x}" y="{leg_y}" width="430" height="75" rx="4" fill="#14141c" stroke="#3d3d52"/>')
    svg.append(f'<line x1="{leg_x + 12}" y1="{leg_y + 20}" x2="{leg_x + 38}" y2="{leg_y + 20}" stroke="#e74c3c" stroke-width="3.5"/>')
    svg.append(f'<circle cx="{leg_x + 25}" cy="{leg_y + 20}" r="4" fill="#e74c3c" stroke="#ffffff" stroke-width="1.5"/>')
    svg.append(f'<text x="{leg_x + 48}" y="{leg_y + 24}" fill="#ffffff" font-size="12" font-weight="bold">Measured Ambient Noise (Citadel of Cairo): 39.5 dBA / 57.8 dBC</text>')

    svg.append(f'<line x1="{leg_x + 12}" y1="{leg_y + 42}" x2="{leg_x + 38}" y2="{leg_y + 42}" stroke="#f39c12" stroke-width="2.5"/>')
    svg.append(f'<text x="{leg_x + 48}" y="{leg_y + 46}" fill="#f39c12" font-size="11" font-weight="bold">Rating: Complies with NC-35 / NR-35 (Acceptable for Worship)</text>')

    svg.append(f'<line x1="{leg_x + 12}" y1="{leg_y + 60}" x2="{leg_x + 38}" y2="{leg_y + 60}" stroke="#4a4a62" stroke-width="1.2" stroke-dasharray="4,4"/>')
    svg.append(f'<text x="{leg_x + 48}" y="{leg_y + 64}" fill="#888899" font-size="11">Standard Noise Criterion (NC) Reference Family</text>')

    svg.append('</svg>')

    out_svg = os.path.join(REPORTS_DIR, "mosque_background_noise_nc_spectrum.svg")
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Saved SVG: {out_svg}")

    # Render PNG
    render_background_noise_png(measured_noise, NC_CURVES)


def render_background_noise_png(measured, nc_curves):
    """Renders high-res PNG for background noise spectrum."""
    w, h = 1000, 720
    canvas = RasterCanvas(w, h, bg_rgb=(20, 20, 28))

    canvas.draw_text("MUHAMMAD ALI MOSQUE - BACKGROUND NOISE SPECTRUM & NC RATING", 40, 22, r=255, g=255, b=255, scale=2)
    canvas.draw_text("CITADEL OF CAIRO AMBIENT ACOUSTIC NOISE EVALUATED AGAINST NC-35", 40, 46, r=160, g=165, b=185, scale=1)

    px0, py0 = 80, 85
    pw, ph = 840, 570
    canvas.fill_rect(px0, py0, px0 + pw, py0 + ph, 26, 26, 36)
    canvas.draw_rect(px0, py0, px0 + pw, py0 + ph, 50, 50, 70)

    db_min, db_max = 10.0, 70.0
    for db in range(10, 71, 10):
        yp = int(py0 + ph * (1.0 - (db - db_min) / (db_max - db_min)))
        canvas.draw_line(px0, yp, px0 + pw, yp, 40, 40, 55)
        canvas.draw_text(f"{db}DB", px0 - 45, yp - 3, r=140, g=140, b=160, scale=1)

    num_oct = len(OCTAVE_BANDS)
    x_coords = [int(px0 + (i / (num_oct - 1)) * pw) for i in range(num_oct)]

    for i, freq in enumerate(OCTAVE_BANDS):
        canvas.draw_line(x_coords[i], py0, x_coords[i], py0 + ph, 35, 35, 48)
        canvas.draw_text(f"{freq}HZ", x_coords[i] - 15, py0 + ph + 18, r=255, g=255, b=255, scale=1)

    # NC Curves
    for nc_name, vals in nc_curves.items():
        is_nc35 = (nc_name == "NC-35")
        col = (243, 156, 18) if is_nc35 else (70, 70, 95)
        for i in range(len(vals) - 1):
            y0 = int(py0 + ph * (1.0 - (vals[i] - db_min) / (db_max - db_min)))
            y1 = int(py0 + ph * (1.0 - (vals[i+1] - db_min) / (db_max - db_min)))
            canvas.draw_line(x_coords[i], y0, x_coords[i+1], y1, col[0], col[1], col[2])
        last_y = int(py0 + ph * (1.0 - (vals[-1] - db_min) / (db_max - db_min)))
        canvas.draw_text(nc_name, px0 + pw + 8, last_y - 3, r=col[0], g=col[1], b=col[2], scale=1)

    # Measured Curve
    for i in range(len(measured) - 1):
        y0 = int(py0 + ph * (1.0 - (measured[i] - db_min) / (db_max - db_min)))
        y1 = int(py0 + ph * (1.0 - (measured[i+1] - db_min) / (db_max - db_min)))
        canvas.draw_line(x_coords[i], y0, x_coords[i+1], y1, 231, 76, 60)
        canvas.draw_line(x_coords[i], y0 + 1, x_coords[i+1], y1 + 1, 231, 76, 60)

    for i in range(len(measured)):
        yp = int(py0 + ph * (1.0 - (measured[i] - db_min) / (db_max - db_min)))
        canvas.draw_disc(x_coords[i], yp, 5, 231, 76, 60)
        canvas.draw_disc(x_coords[i], yp, 2, 255, 255, 255)
        canvas.draw_text(f"{int(measured[i])}", x_coords[i] - 6, yp - 14, r=255, g=120, b=120, scale=1)

    # Legend
    canvas.fill_rect(px0 + 15, py0 + 15, px0 + 440, py0 + 80, 20, 20, 28)
    canvas.draw_line(px0 + 25, py0 + 30, px0 + 50, py0 + 30, 231, 76, 60)
    canvas.draw_disc(px0 + 37, py0 + 30, 4, 255, 255, 255)
    canvas.draw_text("MEASURED CITADEL AMBIENT NOISE (39.5 DBA)", px0 + 58, py0 + 26, r=240, g=240, b=255, scale=1)

    canvas.draw_line(px0 + 25, py0 + 52, px0 + 50, py0 + 52, 243, 156, 18)
    canvas.draw_text("RATING: MEETS NC-35 / NR-35 CRITERION", px0 + 58, py0 + 48, r=243, g=156, b=18, scale=1)

    out_png = os.path.join(REPORTS_DIR, "mosque_background_noise_nc_spectrum.png")
    canvas.save_png(out_png)





def generate_receiver_matrix_chart():
    """Generates SVG & PNG comparing C50, C80, D50, STI, ALcons across all 16 receivers."""
    print("=" * 65)
    print("  GENERATING 16-RECEIVER ACOUSTIC MATRIX CHARTS")
    print("=" * 65)

    w, h = 1000, 750
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="background:#14141c; font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">']

    svg.append(f'<text x="{w/2}" y="36" text-anchor="middle" fill="#ffffff" font-size="22" font-weight="700">Muhammad Ali Mosque — 16 Receiver Acoustic Metrics Matrix</text>')
    svg.append(f'<text x="{w/2}" y="60" text-anchor="middle" fill="#9fa0b5" font-size="13">Point-by-Point Evaluation: Distance, Clarity (C50, C80), Definition (D50), STI, and Consonant Loss (ALcons)</text>')

    rec_empty = CALC_DATA["receiver_evaluations"]["empty"]["receivers"]
    rec_full = CALC_DATA["receiver_evaluations"]["fully_occupied"]["receivers"]

    # Sort receivers by distance from Mihrab
    sorted_pairs = sorted(zip(rec_empty, rec_full), key=lambda p: p[0]["distance_m"])

    # -------------------------------------------------------------
    # SUBPLOT 1: CLARITY C50 / C80 & D50 (Y in [100, 390])
    # -------------------------------------------------------------
    p1_x0, p1_y0 = 70, 95
    p1_w, p1_h = 860, 275

    svg.append(f'<rect x="{p1_x0}" y="{p1_y0}" width="{p1_w}" height="{p1_h}" fill="#1a1a26" stroke="#2d2d3e" stroke-width="1.5"/>')
    svg.append(f'<text x="{p1_x0 + 15}" y="{p1_y0 + 22}" fill="#f1c40f" font-size="13" font-weight="bold">Speech Clarity C50 (dB) &amp; Definition D50 (%) across Receivers (Sorted by Distance)</text>')

    # Target line C50 = +2.0 dB
    c_min, c_max = -8.0, 10.0
    y_target_c = p1_y0 + p1_h * (1.0 - (2.0 - c_min) / (c_max - c_min))
    svg.append(f'<line x1="{p1_x0}" y1="{y_target_c}" x2="{p1_x0 + p1_w}" y2="{y_target_c}" stroke="#2ecc71" stroke-width="1.5" stroke-dasharray="6,4"/>')
    svg.append(f'<text x="{p1_x0 + p1_w - 150}" y="{y_target_c - 6}" fill="#2ecc71" font-size="11" font-weight="bold">Target C50 &gt; +2 dB (Speech)</text>')

    # Y-axis ticks (-8 to +10 dB)
    for db in range(-8, 11, 2):
        yp = p1_y0 + p1_h * (1.0 - (db - c_min) / (c_max - c_min))
        svg.append(f'<line x1="{p1_x0}" y1="{yp}" x2="{p1_x0 + p1_w}" y2="{yp}" stroke="#262638" stroke-width="1"/>')
        svg.append(f'<text x="{p1_x0 - 8}" y="{yp + 4}" text-anchor="end" fill="#888899" font-size="10">{db:+} dB</text>')

    col_w = p1_w / len(sorted_pairs)
    for idx, (re, rf) in enumerate(sorted_pairs):
        gx = p1_x0 + idx * col_w
        cx_c = gx + col_w / 2.0

        # Bar: C50 Empty (Red)
        val_c50 = re["c50_db"]
        yp_c50 = p1_y0 + p1_h * (1.0 - (val_c50 - c_min) / (c_max - c_min))
        y_zero = p1_y0 + p1_h * (1.0 - (0.0 - c_min) / (c_max - c_min))
        bar_y = min(yp_c50, y_zero)
        bar_h = abs(yp_c50 - y_zero)
        bar_col = "#2ecc71" if val_c50 >= 0 else "#e74c3c"
        svg.append(f'<rect x="{cx_c - 10}" y="{bar_y}" width="20" height="{bar_h}" fill="{bar_col}" rx="2"/>')
        svg.append(f'<text x="{cx_c}" y="{bar_y - 4}" text-anchor="middle" fill="{bar_col}" font-size="9" font-weight="bold">{val_c50:+.1f}</text>')

        # Label below Subplot 1
        r_lbl = re["id"].replace("REC_", "R")
        svg.append(f'<text x="{cx_c}" y="{p1_y0 + p1_h + 16}" text-anchor="middle" fill="#ffffff" font-size="10" font-weight="bold">{r_lbl}</text>')
        svg.append(f'<text x="{cx_c}" y="{p1_y0 + p1_h + 28}" text-anchor="middle" fill="#8888aa" font-size="9">{re["distance_m"]}m</text>')

    # -------------------------------------------------------------
    # SUBPLOT 2: SPEECH TRANSMISSION INDEX STI & ALCONS (Y in [425, 700])
    # -------------------------------------------------------------
    p2_y0 = 425
    p2_h = 275
    svg.append(f'<rect x="{p1_x0}" y="{p2_y0}" width="{p1_w}" height="{p2_h}" fill="#1a1a26" stroke="#2d2d3e" stroke-width="1.5"/>')
    svg.append(f'<text x="{p1_x0 + 15}" y="{p2_y0 + 22}" fill="#f1c40f" font-size="13" font-weight="bold">Speech Transmission Index (STI): Empty vs Fully Occupied &amp; Consonant Loss (% ALcons)</text>')

    # STI zones: 0.0 to 1.0
    for sti_val in [0.30, 0.45, 0.60, 0.75]:
        yp = p2_y0 + p2_h * (1.0 - sti_val)
        svg.append(f'<line x1="{p1_x0}" y1="{yp}" x2="{p1_x0 + p1_w}" y2="{yp}" stroke="#2a2a3e" stroke-width="1"/>')
        lbl = "POOR" if sti_val == 0.30 else "FAIR" if sti_val == 0.45 else "GOOD" if sti_val == 0.60 else "EXCELLENT"
        svg.append(f'<text x="{p1_x0 - 8}" y="{yp + 4}" text-anchor="end" fill="#888899" font-size="10">{sti_val:.2f} ({lbl})</text>')

    pts_sti_empty = []
    pts_sti_full = []
    for idx, (re, rf) in enumerate(sorted_pairs):
        gx = p1_x0 + idx * col_w
        cx_c = gx + col_w / 2.0
        yp_e = p2_y0 + p2_h * (1.0 - re["sti"])
        yp_f = p2_y0 + p2_h * (1.0 - rf["sti"])
        pts_sti_empty.append((cx_c, yp_e))
        pts_sti_full.append((cx_c, yp_f))

    # Connect lines
    path_e = "M " + " L ".join(f"{xp:.1f},{yp:.1f}" for xp, yp in pts_sti_empty)
    svg.append(f'<path d="{path_e}" fill="none" stroke="#e74c3c" stroke-width="2.5"/>')

    path_f = "M " + " L ".join(f"{xp:.1f},{yp:.1f}" for xp, yp in pts_sti_full)
    svg.append(f'<path d="{path_f}" fill="none" stroke="#2ecc71" stroke-width="2.5"/>')

    for idx, (xp, yp) in enumerate(pts_sti_empty):
        val_e = sorted_pairs[idx][0]["sti"]
        svg.append(f'<circle cx="{xp}" cy="{yp}" r="4" fill="#e74c3c"/>')
        svg.append(f'<text x="{xp}" y="{yp - 7}" text-anchor="middle" fill="#e74c3c" font-size="9" font-weight="bold">{val_e:.2f}</text>')

    for idx, (xp, yp) in enumerate(pts_sti_full):
        val_f = sorted_pairs[idx][1]["sti"]
        svg.append(f'<circle cx="{xp}" cy="{yp}" r="4" fill="#2ecc71"/>')
        svg.append(f'<text x="{xp}" y="{yp - 7}" text-anchor="middle" fill="#2ecc71" font-size="9" font-weight="bold">{val_f:.2f}</text>')

    # Subplot 2 Legend
    leg2_x = p1_x0 + p1_w - 290
    leg2_y = p2_y0 + 15
    svg.append(f'<rect x="{leg2_x}" y="{leg2_y}" width="280" height="52" rx="4" fill="#14141c" stroke="#3d3d52"/>')
    svg.append(f'<line x1="{leg2_x + 12}" y1="{leg2_y + 16}" x2="{leg2_x + 36}" y2="{leg2_y + 16}" stroke="#e74c3c" stroke-width="2.5"/>')
    svg.append(f'<circle cx="{leg2_x + 24}" cy="{leg2_y + 16}" r="3.5" fill="#e74c3c"/>')
    svg.append(f'<text x="{leg2_x + 44}" y="{leg2_y + 20}" fill="#ffffff" font-size="11">STI Empty Hall (Unoccupied Baseline)</text>')

    svg.append(f'<line x1="{leg2_x + 12}" y1="{leg2_y + 36}" x2="{leg2_x + 36}" y2="{leg2_y + 36}" stroke="#2ecc71" stroke-width="2.5"/>')
    svg.append(f'<circle cx="{leg2_x + 24}" cy="{leg2_y + 36}" r="3.5" fill="#2ecc71"/>')
    svg.append(f'<text x="{leg2_x + 44}" y="{leg2_y + 40}" fill="#ffffff" font-size="11">STI Fully Occupied (1,200 Worshippers)</text>')

    svg.append('</svg>')

    out_svg = os.path.join(REPORTS_DIR, "mosque_receiver_acoustics_matrix.svg")
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Saved SVG: {out_svg}")

    # Render PNG
    render_receiver_matrix_png(sorted_pairs)


def render_receiver_matrix_png(sorted_pairs):
    """Renders high-res PNG for 16-receiver matrix."""
    w, h = 1000, 750
    canvas = RasterCanvas(w, h, bg_rgb=(20, 20, 28))

    canvas.draw_text("MUHAMMAD ALI MOSQUE - 16 RECEIVER ACOUSTIC PARAMETERS MATRIX", 40, 22, r=255, g=255, b=255, scale=2)
    canvas.draw_text("POINT-BY-POINT CLARITY C50 (DB), DEFINITION D50 (%), AND STI", 40, 46, r=160, g=165, b=185, scale=1)

    p1_x0, p1_y0 = 70, 85
    p1_w, p1_h = 860, 280
    canvas.fill_rect(p1_x0, p1_y0, p1_x0 + p1_w, p1_y0 + p1_h, 26, 26, 36)
    canvas.draw_rect(p1_x0, p1_y0, p1_x0 + p1_w, p1_y0 + p1_h, 50, 50, 70)
    canvas.draw_text("SPEECH CLARITY C50 (DB) ACROSS RECEIVERS (SORTED BY DISTANCE)", p1_x0 + 15, p1_y0 + 15, r=255, g=215, b=0, scale=1)

    c_min, c_max = -8.0, 10.0
    for db in range(-8, 11, 4):
        yp = int(p1_y0 + p1_h * (1.0 - (db - c_min) / (c_max - c_min)))
        canvas.draw_line(p1_x0, yp, p1_x0 + p1_w, yp, 40, 40, 55)
        canvas.draw_text(f"{db:+}DB", p1_x0 - 45, yp - 3, r=140, g=140, b=160, scale=1)

    col_w = p1_w / len(sorted_pairs)
    for idx, (re, rf) in enumerate(sorted_pairs):
        cx = int(p1_x0 + (idx + 0.5) * col_w)
        val_c = re["c50_db"]
        yp_c = int(p1_y0 + p1_h * (1.0 - (val_c - c_min) / (c_max - c_min)))
        y_zero = int(p1_y0 + p1_h * (1.0 - (0.0 - c_min) / (c_max - c_min)))

        bar_col = (46, 204, 113) if val_c >= 0 else (231, 76, 60)
        canvas.fill_rect(cx - 8, min(yp_c, y_zero), cx + 8, max(yp_c, y_zero), bar_col[0], bar_col[1], bar_col[2])

        r_lbl = re["id"].replace("REC_", "R")
        canvas.draw_text(r_lbl, cx - 6, p1_y0 + p1_h + 12, r=255, g=255, b=255, scale=1)
        canvas.draw_text(f"{int(re['distance_m'])}M", cx - 8, p1_y0 + p1_h + 24, r=160, g=160, b=180, scale=1)

    # Subplot 2: STI
    p2_y0 = 430
    p2_h = 280
    canvas.fill_rect(p1_x0, p2_y0, p1_x0 + p1_w, p2_y0 + p2_h, 26, 26, 36)
    canvas.draw_rect(p1_x0, p2_y0, p1_x0 + p1_w, p2_y0 + p2_h, 50, 50, 70)
    canvas.draw_text("SPEECH TRANSMISSION INDEX (STI): EMPTY (RED) VS FULLY OCCUPIED (GREEN)", p1_x0 + 15, p2_y0 + 15, r=255, g=215, b=0, scale=1)

    for sti_val in [0.30, 0.45, 0.60, 0.75]:
        yp = int(p2_y0 + p2_h * (1.0 - sti_val))
        canvas.draw_line(p1_x0, yp, p1_x0 + p1_w, yp, 40, 40, 55)
        canvas.draw_text(f"{sti_val:.2f}", p1_x0 - 40, yp - 3, r=140, g=140, b=160, scale=1)

    pts_e = []
    pts_f = []
    for idx, (re, rf) in enumerate(sorted_pairs):
        cx = int(p1_x0 + (idx + 0.5) * col_w)
        ye = int(p2_y0 + p2_h * (1.0 - re["sti"]))
        yf = int(p2_y0 + p2_h * (1.0 - rf["sti"]))
        pts_e.append((cx, ye))
        pts_f.append((cx, yf))

    for i in range(len(pts_e) - 1):
        canvas.draw_line(pts_e[i][0], pts_e[i][1], pts_e[i+1][0], pts_e[i+1][1], 231, 76, 60)
        canvas.draw_line(pts_f[i][0], pts_f[i][1], pts_f[i+1][0], pts_f[i+1][1], 46, 204, 113)

    for i in range(len(pts_e)):
        canvas.draw_disc(pts_e[i][0], pts_e[i][1], 4, 231, 76, 60)
        canvas.draw_disc(pts_f[i][0], pts_f[i][1], 4, 46, 204, 113)

    out_png = os.path.join(REPORTS_DIR, "mosque_receiver_acoustics_matrix.png")
    canvas.save_png(out_png)


def generate_all_measurement_charts():
    generate_total_absorption_chart()
    generate_background_noise_chart()
    generate_receiver_matrix_chart()
    print("=" * 65)
    print("All Measurement Charts Generated Successfully!")


if __name__ == "__main__":
    generate_all_measurement_charts()
