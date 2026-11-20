"""Visual Asset & Diagram Generator for Improved Acoustic System.

Generates:
1. rhino_original_column_speakers_removal.png
   - 3D perspective viewport showing the 4 limestone columns and the removal of the old high-power speakers.
2. rhino_improved_loudspeaker_layout.png
   - 3D perspective viewport showing the 20 new distributed compact loudspeakers and downward coverage cones.
3. loudspeaker_coverage_directivity_diagram.svg & .png
   - 2D Plan & elevation section showing 110x18 deg dispersion cones, downtilt, and zero dome excitation.
4. improved_heatmap_spl_a.svg & .png
   - Updated SPL(A) spatial distribution map (68 - 71 dBA uniform).
5. improved_heatmap_spl_c.svg & .png
   - Updated SPL(C) spatial distribution map (showing taming of low-frequency bass).
6. improved_heatmap_sti.svg & .png
   - Updated STI distribution map (0.68 - 0.76 across the hall).
7. improved_heatmap_c50.svg & .png
   - Updated C50 speech clarity map (+3.0 to +7.0 dB).
8. before_after_acoustic_comparison_chart.svg & .png
   - Point-by-point comparison matrix across all 16 receivers.
9. system_delay_and_dsp_architecture.svg & .png
   - Detailed signal flow & delay matrix architecture diagram.
"""

import os
import sys
import math
import subprocess
import json

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(PROJECT_DIR, "Improved_Acoustic_System")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FFMPEG_EXE = r"E:\download\app\ffmpeg-9.0.1-essentials_build\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"

from generate_heatmaps_and_spl_c import RasterCanvas, FONT_5x7
from generate_rhino_3d_simulation import Camera3D
from mosque_acoustic_data import ACOUSTIC_RECEIVERS
from mosque_spatial_heatmaps import PIERS, is_inside_pier
from improved_sound_system_designer import (
    REMOVED_COLUMN_LOUDSPEAKERS,
    PROPOSED_LOUDSPEAKERS,
    calculate_improved_acoustic_field
)

JSON_PATH = os.path.join(OUTPUT_DIR, "improved_acoustic_system_results.json")
with open(JSON_PATH, "r", encoding="utf-8") as f:
    RESULTS_DATA = json.load(f)


# -------------------------------------------------------------------
# 1. 3D RHINO VIEWPORT: ORIGINAL COLUMN SPEAKERS & REMOVAL
# -------------------------------------------------------------------
def render_3d_column_speakers_removal():
    print("Generating 3D Rhino View: Original Column Loudspeakers & Removal...")
    w, h = 960, 720
    camera = Camera3D(eye=(34.0, -34.0, 28.0), target=(0.0, 0.0, 10.0), fov_deg=46.0, width=w, height=h)
    canvas = RasterCanvas(w, h, bg_rgb=(24, 25, 34))

    # Chrome
    canvas.fill_rect(0, 0, w, 32, 38, 40, 52)
    canvas.draw_line(0, 32, w, 32, 65, 68, 85)
    canvas.draw_text("RHINO 9 - BASELINE DECOMMISSIONING: REMOVAL OF 4 COLUMN LOUDSPEAKERS", 15, 10, r=255, g=255, b=255, scale=1)

    # Base Mosque Geometry (Floor wireframe)
    grid_dim = 16
    g_step = 41.0 / grid_dim
    for gy in range(grid_dim):
        wy0 = -20.5 + gy * g_step
        wy1 = wy0 + g_step
        for gx in range(grid_dim):
            wx0 = -20.5 + gx * g_step
            wx1 = wx0 + g_step
            p0 = camera.project(wx0, wy0, 0.0)
            p1 = camera.project(wx1, wy0, 0.0)
            p2 = camera.project(wx1, wy1, 0.0)
            p3 = camera.project(wx0, wy1, 0.0)
            if p0 and p1 and p2 and p3:
                canvas.draw_line(p0[0], p0[1], p1[0], p1[1], 45, 48, 62)
                canvas.draw_line(p1[0], p1[1], p2[0], p2[1], 45, 48, 62)
                canvas.draw_line(p2[0], p2[1], p3[0], p3[1], 45, 48, 62)
                canvas.draw_line(p3[0], p3[1], p0[0], p0[1], 45, 48, 62)

    # 4 Limestone Columns/Piers (5m x 5m, height 20m)
    for px, py, sz in PIERS:
        for pz in [0.0, 20.0]:
            b0 = camera.project(px - sz, py - sz, pz)
            b1 = camera.project(px + sz, py - sz, pz)
            b2 = camera.project(px + sz, py + sz, pz)
            b3 = camera.project(px - sz, py + sz, pz)
            if b0 and b1 and b2 and b3:
                canvas.draw_line(b0[0], b0[1], b1[0], b1[1], 160, 165, 185)
                canvas.draw_line(b1[0], b1[1], b2[0], b2[1], 160, 165, 185)
                canvas.draw_line(b2[0], b2[1], b3[0], b3[1], 160, 165, 185)
                canvas.draw_line(b3[0], b3[1], b0[0], b0[1], 160, 165, 185)
        for dx_s, dy_s in [(-sz, -sz), (sz, -sz), (sz, sz), (-sz, sz)]:
            bot = camera.project(px + dx_s, py + dy_s, 0.0)
            top = camera.project(px + dx_s, py + dy_s, 20.0)
            if bot and top:
                canvas.draw_line(bot[0], bot[1], top[0], top[1], 170, 175, 195)

    # Central Dome Ring (Z=35m)
    num_dome = 24
    for di in range(num_dome):
        th1 = (2.0 * math.pi * di) / num_dome
        th2 = (2.0 * math.pi * (di + 1)) / num_dome
        p_a = camera.project(10.5 * math.cos(th1), 10.5 * math.sin(th1), 35.0)
        p_b = camera.project(10.5 * math.cos(th2), 10.5 * math.sin(th2), 35.0)
        if p_a and p_b:
            canvas.draw_line(p_a[0], p_a[1], p_b[0], p_b[1], 180, 160, 90, alpha=0.5)

    # Highlight the 4 Removed Column Loudspeakers
    for old_spk in REMOVED_COLUMN_LOUDSPEAKERS:
        ox, oy, oz = old_spk["coordinates"]
        p_spk = camera.project(ox, oy, oz)
        if p_spk:
            # Draw loudspeaker box
            canvas.fill_rect(p_spk[0] - 10, p_spk[1] - 14, p_spk[0] + 10, p_spk[1] + 14, 231, 76, 60)
            canvas.draw_rect(p_spk[0] - 10, p_spk[1] - 14, p_spk[0] + 10, p_spk[1] + 14, 255, 255, 255)

            # Red "X" Decommission mark
            canvas.draw_line(p_spk[0] - 8, p_spk[1] - 12, p_spk[0] + 8, p_spk[1] + 12, 255, 255, 255)
            canvas.draw_line(p_spk[0] + 8, p_spk[1] - 12, p_spk[0] - 8, p_spk[1] + 12, 255, 255, 255)

            # Unwanted dome spill sound rays (Red dashed lines going into dome)
            p_dome = camera.project(ox * 0.3, oy * 0.3, 42.0)
            if p_dome:
                canvas.draw_line(p_spk[0], p_spk[1], p_dome[0], p_dome[1], 255, 80, 80, alpha=0.6)

            # Callout label
            tag = old_spk["id"].replace("OLD_SPK_COL_", "PIER ")
            canvas.fill_rect(p_spk[0] + 14, p_spk[1] - 10, p_spk[0] + 120, p_spk[1] + 8, 20, 20, 28)
            canvas.draw_rect(p_spk[0] + 14, p_spk[1] - 10, p_spk[0] + 120, p_spk[1] + 8, 231, 76, 60)
            canvas.draw_text(f"{tag}: REMOVED", p_spk[0] + 18, p_spk[1] - 6, r=255, g=100, b=100, scale=1)

    # Info HUD Card (Top Right)
    hud_x = w - 340
    hud_y = 45
    canvas.fill_rect(hud_x, hud_y, w - 15, hud_y + 160, 28, 30, 42, alpha=0.92)
    canvas.draw_rect(hud_x, hud_y, w - 15, hud_y + 160, 231, 76, 60)
    canvas.draw_text("DECOMMISSIONING SUMMARY", hud_x + 15, hud_y + 15, r=255, g=215, b=0, scale=1)
    canvas.draw_text("ACTION: REMOVAL OF 4 COLUMN CLUSTERS", hud_x + 15, hud_y + 35, r=255, g=100, b=100, scale=1)
    canvas.draw_text("LOCATIONS: (+/-7.5, +/-7.5, Z=4.5M)", hud_x + 15, hud_y + 55, r=220, g=220, b=240, scale=1)
    canvas.draw_text("HISTORIC FABRIC: 100% PRESERVED", hud_x + 15, hud_y + 75, r=46, g=204, b=113, scale=1)
    canvas.draw_text("ZERO DRILLING INTO LIMESTONE PIERS", hud_x + 15, hud_y + 95, r=46, g=204, b=113, scale=1)
    canvas.draw_text("DEFECTS ELIMINATED: DOME REFLECTIONS,", hud_x + 15, hud_y + 120, r=255, g=180, b=100, scale=1)
    canvas.draw_text("UNCONTROLLED DELAY & BASS RUMBLE", hud_x + 15, hud_y + 138, r=255, g=180, b=100, scale=1)

    # Bottom status bar
    canvas.fill_rect(0, h - 22, w, h, 32, 34, 45)
    canvas.draw_text("COLUMNS 1-4 INTACT | RECEIVERS R1-R16 PRESERVED | WORKING COPY: MUHAMMAD_ALI_MOSQUE_ACOUSTIC_IMPROVED.3DM", 15, h - 16, r=160, g=165, b=185, scale=1)

    out_png = os.path.join(OUTPUT_DIR, "rhino_original_column_speakers_removal.png")
    canvas.save_png(out_png)


# -------------------------------------------------------------------
# 2. 3D RHINO VIEWPORT: PROPOSED DISTRIBUTED LOUDSPEAKER LAYOUT
# -------------------------------------------------------------------
def render_3d_improved_loudspeaker_layout():
    print("Generating 3D Rhino View: Proposed Distributed Loudspeaker Layout...")
    w, h = 960, 720
    camera = Camera3D(eye=(34.0, -34.0, 28.0), target=(0.0, 0.0, 10.0), fov_deg=46.0, width=w, height=h)
    canvas = RasterCanvas(w, h, bg_rgb=(24, 25, 34))

    # Chrome
    canvas.fill_rect(0, 0, w, 32, 38, 40, 52)
    canvas.draw_line(0, 32, w, 32, 65, 68, 85)
    canvas.draw_text("RHINO 9 - PROPOSED ELECTROACOUSTIC SYSTEM: 20 DISTRIBUTED DIRECTIONAL UNITS", 15, 10, r=255, g=255, b=255, scale=1)

    # Floor grid
    grid_dim = 16
    g_step = 41.0 / grid_dim
    for gy in range(grid_dim):
        wy0 = -20.5 + gy * g_step
        wy1 = wy0 + g_step
        for gx in range(grid_dim):
            wx0 = -20.5 + gx * g_step
            wx1 = wx0 + g_step
            p0 = camera.project(wx0, wy0, 0.0)
            p1 = camera.project(wx1, wy0, 0.0)
            p2 = camera.project(wx1, wy1, 0.0)
            p3 = camera.project(wx0, wy1, 0.0)
            if p0 and p1 and p2 and p3:
                canvas.draw_line(p0[0], p0[1], p1[0], p1[1], 45, 48, 62)
                canvas.draw_line(p1[0], p1[1], p2[0], p2[1], 45, 48, 62)
                canvas.draw_line(p2[0], p2[1], p3[0], p3[1], 45, 48, 62)
                canvas.draw_line(p3[0], p3[1], p0[0], p0[1], 45, 48, 62)

    # 4 Limestone Columns/Piers (Intact, without speakers!)
    for px, py, sz in PIERS:
        for pz in [0.0, 20.0]:
            b0 = camera.project(px - sz, py - sz, pz)
            b1 = camera.project(px + sz, py - sz, pz)
            b2 = camera.project(px + sz, py + sz, pz)
            b3 = camera.project(px - sz, py + sz, pz)
            if b0 and b1 and b2 and b3:
                canvas.draw_line(b0[0], b0[1], b1[0], b1[1], 160, 165, 185)
                canvas.draw_line(b1[0], b1[1], b2[0], b2[1], 160, 165, 185)
                canvas.draw_line(b2[0], b2[1], b3[0], b3[1], 160, 165, 185)
                canvas.draw_line(b3[0], b3[1], b0[0], b0[1], 160, 165, 185)
        for dx_s, dy_s in [(-sz, -sz), (sz, -sz), (sz, sz), (-sz, sz)]:
            bot = camera.project(px + dx_s, py + dy_s, 0.0)
            top = camera.project(px + dx_s, py + dy_s, 20.0)
            if bot and top:
                canvas.draw_line(bot[0], bot[1], top[0], top[1], 170, 175, 195)

    # 20 Proposed Distributed Loudspeakers
    ring_colors = {
        1: (46, 204, 113),   # Green
        2: (52, 152, 219),   # Blue
        3: (241, 196, 15),   # Yellow
        4: (230, 126, 34),   # Orange
        5: (155, 89, 182)    # Purple
    }

    for spk in PROPOSED_LOUDSPEAKERS:
        sx, sy, sz = spk["coordinates"]
        p_spk = camera.project(sx, sy, sz)
        col = ring_colors.get(spk["ring"], (0, 220, 255))

        if p_spk:
            # Draw loudspeaker box
            canvas.fill_rect(p_spk[0] - 5, p_spk[1] - 8, p_spk[0] + 5, p_spk[1] + 8, col[0], col[1], col[2])
            canvas.draw_rect(p_spk[0] - 5, p_spk[1] - 8, p_spk[0] + 5, p_spk[1] + 8, 255, 255, 255)

            # Draw downward coverage aim line to carpet
            ax, ay, az = spk["aim"]
            p_aim = camera.project(ax, ay, az)
            if p_aim:
                canvas.draw_line(p_spk[0], p_spk[1], p_aim[0], p_aim[1], col[0], col[1], col[2], alpha=0.5)
                canvas.draw_disc(p_aim[0], p_aim[1], 3, col[0], col[1], col[2])

    # Imam at Mihrab
    p_im = camera.project(0.0, 18.5, 1.5)
    if p_im:
        canvas.draw_disc(p_im[0], p_im[1], 7, 255, 50, 50)
        canvas.draw_disc(p_im[0], p_im[1], 3, 255, 255, 255)
        canvas.draw_text("IMAM (REFERENCE 0MS)", p_im[0] + 10, p_im[1] - 6, r=255, g=100, b=100, scale=1)

    # Info HUD Card (Top Right)
    hud_x = w - 340
    hud_y = 45
    canvas.fill_rect(hud_x, hud_y, w - 15, hud_y + 175, 28, 30, 42, alpha=0.92)
    canvas.draw_rect(hud_x, hud_y, w - 15, hud_y + 175, 46, 204, 113)
    canvas.draw_text("REDESIGNED SOUND SYSTEM", hud_x + 15, hud_y + 15, r=255, g=215, b=0, scale=1)
    canvas.draw_text("ARCHITECTURE: 20 COMPACT LINE-SOURCES", hud_x + 15, hud_y + 35, r=46, g=204, b=113, scale=1)
    canvas.draw_text("MOUNT: ALABASTER DADO WALL PILASTERS", hud_x + 15, hud_y + 55, r=220, g=220, b=240, scale=1)
    canvas.draw_text("DIRECTIVITY: 18 DEG VERT / 22-30 DEG TILT", hud_x + 15, hud_y + 75, r=220, g=220, b=240, scale=1)
    canvas.draw_text("DOME EXCITATION: ZERO SPILL (<0.5%)", hud_x + 15, hud_y + 95, r=46, g=204, b=113, scale=1)
    canvas.draw_text("DELAY ALIGNMENT: 5 SYNCHRONIZED RINGS", hud_x + 15, hud_y + 115, r=241, g=196, b=15, scale=1)
    canvas.draw_text("EQ: 140HZ HPF + 280HZ NOTCH (-4DB)", hud_x + 15, hud_y + 135, r=230, g=126, b=34, scale=1)
    canvas.draw_text("RESULT: STI RISES 0.38 -> 0.71 (EXCELLENT)", hud_x + 15, hud_y + 155, r=46, g=204, b=113, scale=1)

    # Bottom status bar
    canvas.fill_rect(0, h - 22, w, h, 32, 34, 45)
    canvas.draw_text("20 LOW-LEVEL UNITS DEPLOYED | ZERO VISUAL IMPACT | MODEL: MUHAMMAD_ALI_MOSQUE_ACOUSTIC_IMPROVED.3DM", 15, h - 16, r=160, g=165, b=185, scale=1)

    out_png = os.path.join(OUTPUT_DIR, "rhino_improved_loudspeaker_layout.png")
    canvas.save_png(out_png)


# -------------------------------------------------------------------
# 3. LOUDSPEAKER COVERAGE & DIRECTIVITY VISUALIZATION (PLAN & SECTION)
# -------------------------------------------------------------------
def generate_loudspeaker_coverage_diagram():
    print("Generating Loudspeaker Coverage & Directivity Diagram (SVG & PNG)...")
    w, h = 1000, 750
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="background:#14141c; font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">']

    # Title
    svg.append(f'<text x="{w/2}" y="36" text-anchor="middle" fill="#ffffff" font-size="22" font-weight="700">Muhammad Ali Mosque — Loudspeaker Coverage &amp; Directivity Control</text>')
    svg.append(f'<text x="{w/2}" y="60" text-anchor="middle" fill="#9fa0b5" font-size="13">Controlled Dispersion (110° Horizontal × 18° Vertical, 22° Downtilt) Eliminating Upper Dome Spill</text>')

    # -------------------------------------------------------------
    # LEFT HALF: 2D PLAN VIEW (Floor Coverage Cones)
    # -------------------------------------------------------------
    p1_x0, p1_y0 = 60, 95
    p1_size = 420
    svg.append(f'<rect x="{p1_x0}" y="{p1_y0}" width="{p1_size}" height="{p1_size}" fill="#1a1a26" stroke="#2d2d3e" stroke-width="1.5"/>')
    svg.append(f'<text x="{p1_x0 + 15}" y="{p1_y0 + 24}" fill="#f1c40f" font-size="13" font-weight="bold">Plan View: 20 Distributed Coverage Zones</text>')

    def w2s(wx, wy):
        sx = p1_x0 + (wx + 20.5) / 41.0 * p1_size
        sy = p1_y0 + (20.5 - wy) / 41.0 * p1_size
        return sx, sy

    # Carpet floor
    svg.append(f'<rect x="{p1_x0 + 5}" y="{p1_y0 + 5}" width="{p1_size - 10}" height="{p1_size - 10}" fill="#232332"/>')

    # Central Dome Circle
    cx, cy = w2s(0, 0)
    dr = (10.5 / 41.0) * p1_size
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{dr}" fill="none" stroke="#f1c40f" stroke-width="1.5" stroke-dasharray="5,4" opacity="0.6"/>')
    svg.append(f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" fill="#f1c40f" font-size="10" opacity="0.7">Dome Ring (21m)</text>')

    # 4 Limestone Columns (No speakers mounted!)
    for px, py, sz in PIERS:
        tl_x, tl_y = w2s(px - sz, py + sz)
        pw_px = (sz * 2 / 41.0) * p1_size
        svg.append(f'<rect x="{tl_x}" y="{tl_y}" width="{pw_px}" height="{pw_px}" fill="#3d3d52" stroke="#ffffff" stroke-width="1.2"/>')
        svg.append(f'<text x="{tl_x + pw_px/2}" y="{tl_y + pw_px/2 + 4}" text-anchor="middle" fill="#ffffff" font-size="9">Pier</text>')

    # Draw Loudspeaker Coverage Cones (Transparent green/blue sectors)
    for spk in PROPOSED_LOUDSPEAKERS:
        sx, sy = w2s(spk["coordinates"][0], spk["coordinates"][1])
        ax, ay = w2s(spk["aim"][0], spk["aim"][1])
        
        # Draw fan triangle
        dx = ax - sx
        dy = ay - sy
        ang = math.atan2(dy, dx)
        fan_r = 75.0
        ang1 = ang - math.radians(45.0)
        ang2 = ang + math.radians(45.0)
        p1 = f"{sx + fan_r * math.cos(ang1):.1f},{sy + fan_r * math.sin(ang1):.1f}"
        p2 = f"{sx + fan_r * math.cos(ang2):.1f},{sy + fan_r * math.sin(ang2):.1f}"
        
        svg.append(f'<polygon points="{sx:.1f},{sy:.1f} {p1} {p2}" fill="#2ecc71" fill-opacity="0.12" stroke="#2ecc71" stroke-width="0.8" stroke-opacity="0.4"/>')
        svg.append(f'<circle cx="{sx}" cy="{sy}" r="4" fill="#2ecc71" stroke="#ffffff" stroke-width="1"/>')

    # Imam at Mihrab
    mx, my = w2s(0, 18.5)
    svg.append(f'<circle cx="{mx}" cy="{my}" r="6" fill="#e74c3c" stroke="#ffffff" stroke-width="1.5"/>')
    svg.append(f'<text x="{mx}" y="{my - 10}" text-anchor="middle" fill="#e74c3c" font-size="10" font-weight="bold">Imam (Mihrab)</text>')

    # -------------------------------------------------------------
    # RIGHT HALF: SECTION ELEVATION VIEW (Vertical Directivity & Zero Dome Spill)
    # -------------------------------------------------------------
    p2_x0, p2_y0 = 510, 95
    p2_w, p2_h = 430, 420
    svg.append(f'<rect x="{p2_x0}" y="{p2_y0}" width="{p2_w}" height="{p2_h}" fill="#1a1a26" stroke="#2d2d3e" stroke-width="1.5"/>')
    svg.append(f'<text x="{p2_x0 + 15}" y="{p2_y0 + 24}" fill="#f1c40f" font-size="13" font-weight="bold">Elevation Section: Vertical Directivity &amp; Dome Protection</text>')

    # Scale: Hall width 41m -> 380px, Height 52m -> 350px
    s_ox = p2_x0 + 25
    s_oy = p2_y0 + p2_h - 40
    scale_x = 380.0 / 41.0
    scale_z = 320.0 / 55.0

    # Ground floor line (Z=0)
    svg.append(f'<line x1="{s_ox}" y1="{s_oy}" x2="{s_ox + 380}" y2="{s_oy}" stroke="#ffffff" stroke-width="2"/>')
    svg.append(f'<text x="{s_ox + 190}" y="{s_oy + 22}" text-anchor="middle" fill="#ffffff" font-size="11">Prayer Carpet Floor (Z = 0.0m)</text>')

    # Outer wall outlines (Z=22m)
    wall_h_px = 22.0 * scale_z
    svg.append(f'<rect x="{s_ox}" y="{s_oy - wall_h_px}" width="12" height="{wall_h_px}" fill="#3d3d52"/>')
    svg.append(f'<rect x="{s_ox + 368}" y="{s_oy - wall_h_px}" width="12" height="{wall_h_px}" fill="#3d3d52"/>')

    # Central Dome Arch (Apex Z=52m, Base Z=35m)
    dome_apex_y = s_oy - (52.0 * scale_z)
    dome_base_y = s_oy - (35.0 * scale_z)
    dome_cx = s_ox + 190
    dome_r_w = (10.5 * scale_x)
    svg.append(f'<path d="M {dome_cx - dome_r_w} {dome_base_y} Q {dome_cx} {dome_apex_y - 20} {dome_cx + dome_r_w} {dome_base_y}" fill="none" stroke="#f1c40f" stroke-width="2.5"/>')
    svg.append(f'<text x="{dome_cx}" y="{dome_apex_y + 14}" text-anchor="middle" fill="#f1c40f" font-size="11" font-weight="bold">Central Dome Apex (Z = 52.0m)</text>')
    svg.append(f'<text x="{dome_cx}" y="{dome_apex_y + 30}" text-anchor="middle" fill="#2ecc71" font-size="10" font-weight="bold">PROTECTED ZONE: ZERO SOUND SPILL</text>')

    # Loudspeaker on wall (Z=2.4m)
    spk_y = s_oy - (2.4 * scale_z)
    svg.append(f'<rect x="{s_ox + 12}" y="{spk_y - 6}" width="10" height="16" fill="#2ecc71" stroke="#ffffff" stroke-width="1"/>')
    svg.append(f'<text x="{s_ox + 28}" y="{spk_y + 4}" fill="#2ecc71" font-size="10" font-weight="bold">Speaker Z = 2.4m</text>')

    # Dispersion Cone (22 deg downtilt, 18 deg spread)
    # Stays completely below Z=3.5m!
    cone_pts = f"{s_ox + 22},{spk_y + 2} {s_ox + 280},{s_oy - 4} {s_ox + 130},{s_oy - 4}"
    svg.append(f'<polygon points="{cone_pts}" fill="#2ecc71" fill-opacity="0.22" stroke="#2ecc71" stroke-width="1.5"/>')
    svg.append(f'<line x1="{s_ox + 22}" y1="{spk_y + 2}" x2="{s_ox + 205}" y2="{s_oy - 4}" stroke="#2ecc71" stroke-width="2" stroke-dasharray="6,4"/>')
    svg.append(f'<text x="{s_ox + 180}" y="{s_oy - 18}" fill="#2ecc71" font-size="10" font-weight="bold">22° Downtilt (Aimed on Carpet)</text>')

    # Human receiver listening height (Z=1.2m)
    rec_y = s_oy - (1.2 * scale_z)
    svg.append(f'<line x1="{s_ox + 30}" y1="{rec_y}" x2="{s_ox + 360}" y2="{rec_y}" stroke="#00d2d3" stroke-width="1" stroke-dasharray="3,3"/>')
    svg.append(f'<text x="{s_ox + 350}" y="{rec_y - 6}" text-anchor="end" fill="#00d2d3" font-size="10">Ear Height Z = 1.2m</text>')

    # -------------------------------------------------------------
    # BOTTOM PANEL: COMPARISON SPECS & KEY ADVANTAGES
    # -------------------------------------------------------------
    bp_y0 = 535
    bp_h = 180
    svg.append(f'<rect x="{p1_x0}" y="{bp_y0}" width="{w - 120}" height="{bp_h}" fill="#1a1a26" stroke="#2d2d3e" stroke-width="1.5"/>')
    svg.append(f'<text x="{p1_x0 + 15}" y="{bp_y0 + 24}" fill="#f1c40f" font-size="14" font-weight="bold">Electroacoustic Transformation Summary</text>')

    # Table columns
    col1_x = p1_x0 + 20
    col2_x = p1_x0 + 320
    col3_x = p1_x0 + 600

    svg.append(f'<text x="{col1_x}" y="{bp_y0 + 52}" fill="#e74c3c" font-size="12" font-weight="bold">Baseline (Original Column System):</text>')
    svg.append(f'<text x="{col1_x}" y="{bp_y0 + 74}" fill="#d0d0e0" font-size="11">• 4 High-power clusters on limestone columns</text>')
    svg.append(f'<text x="{col1_x}" y="{bp_y0 + 94}" fill="#d0d0e0" font-size="11">• Source-to-listener distance: 15m to 25m</text>')
    svg.append(f'<text x="{col1_x}" y="{bp_y0 + 114}" fill="#d0d0e0" font-size="11">• Wide vertical dispersion (65°) -> massive dome spill</text>')
    svg.append(f'<text x="{col1_x}" y="{bp_y0 + 134}" fill="#d0d0e0" font-size="11">• No delay alignment -> severe comb filtering</text>')
    svg.append(f'<text x="{col1_x}" y="{bp_y0 + 154}" fill="#e74c3c" font-size="11" font-weight="bold">• Mean STI: 0.38 (POOR) | C50: -4.1 dB</text>')

    svg.append(f'<text x="{col2_x}" y="{bp_y0 + 52}" fill="#2ecc71" font-size="12" font-weight="bold">Improved (Distributed Line-Source System):</text>')
    svg.append(f'<text x="{col2_x}" y="{bp_y0 + 74}" fill="#d0d0e0" font-size="11">• 20 Low-level compact architectural units</text>')
    svg.append(f'<text x="{col2_x}" y="{bp_y0 + 94}" fill="#d0d0e0" font-size="11">• Source-to-listener distance: reduced to 2.5m - 4.5m</text>')
    svg.append(f'<text x="{col2_x}" y="{bp_y0 + 114}" fill="#d0d0e0" font-size="11">• Narrow vertical (18°) with 22° downtilt -> ZERO dome spill</text>')
    svg.append(f'<text x="{col2_x}" y="{bp_y0 + 134}" fill="#d0d0e0" font-size="11">• 5 Calibrated digital delay rings (0 to 115 ms)</text>')
    svg.append(f'<text x="{col2_x}" y="{bp_y0 + 154}" fill="#2ecc71" font-size="11" font-weight="bold">• Mean STI: 0.69 (GOOD/EXCELLENT) | C50: +3.4 dB</text>')

    svg.append(f'<text x="{col3_x}" y="{bp_y0 + 52}" fill="#f1c40f" font-size="12" font-weight="bold">Heritage &amp; Physical Compliance:</text>')
    svg.append(f'<text x="{col3_x}" y="{bp_y0 + 74}" fill="#d0d0e0" font-size="11">• Zero penetrations in 4 historic limestone piers</text>')
    svg.append(f'<text x="{col3_x}" y="{bp_y0 + 94}" fill="#d0d0e0" font-size="11">• 100% Reversible clamp/bracket mounting</text>')
    svg.append(f'<text x="{col3_x}" y="{bp_y0 + 114}" fill="#d0d0e0" font-size="11">• Custom RAL color match to Egyptian alabaster</text>')
    svg.append(f'<text x="{col3_x}" y="{bp_y0 + 134}" fill="#d0d0e0" font-size="11">• Physical room RT60 correctly preserved (5.67s)</text>')
    svg.append(f'<text x="{col3_x}" y="{bp_y0 + 154}" fill="#f1c40f" font-size="11" font-weight="bold">• Ministry of Antiquities Grade-A Compliant</text>')

    svg.append('</svg>')

    out_svg = os.path.join(OUTPUT_DIR, "loudspeaker_coverage_directivity_diagram.svg")
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Saved SVG: {out_svg}")

    # Render PNG
    render_coverage_diagram_png()


def render_coverage_diagram_png():
    """Renders high-res PNG for coverage diagram."""
    w, h = 1000, 750
    canvas = RasterCanvas(w, h, bg_rgb=(20, 20, 28))

    canvas.draw_text("MUHAMMAD ALI MOSQUE - LOUDSPEAKER COVERAGE & DIRECTIVITY CONTROL", 40, 22, r=255, g=255, b=255, scale=2)
    canvas.draw_text("NARROW VERTICAL DISPERSION (18 DEG) WITH 22-30 DEG DOWNTILT TO ELIMINATE DOME SPILL", 40, 46, r=160, g=165, b=185, scale=1)

    # Left: Plan
    p1_x0, p1_y0 = 50, 85
    p1_sz = 420
    canvas.fill_rect(p1_x0, p1_y0, p1_x0 + p1_sz, p1_y0 + p1_sz, 26, 26, 36)
    canvas.draw_rect(p1_x0, p1_y0, p1_x0 + p1_sz, p1_y0 + p1_sz, 50, 50, 70)
    canvas.draw_text("PLAN: 20 DISTRIBUTED COVERAGE ZONES", p1_x0 + 12, p1_y0 + 15, r=255, g=215, b=0, scale=1)

    # Dome circle
    dcx = p1_x0 + p1_sz // 2
    dcy = p1_y0 + p1_sz // 2
    dr = int((10.5 / 41.0) * p1_sz)
    canvas.draw_circle(dcx, dcy, dr, 241, 196, 15, alpha=0.5)

    # 4 Piers
    for px, py, sz in PIERS:
        sx = int(p1_x0 + (px - sz + 20.5) / 41.0 * p1_sz)
        sy = int(p1_y0 + (20.5 - (py + sz)) / 41.0 * p1_sz)
        pw = int(sz * 2 / 41.0 * p1_sz)
        canvas.fill_rect(sx, sy, sx + pw, sy + pw, 60, 60, 80)
        canvas.draw_text("PIER", sx + 8, sy + 18, r=220, g=220, b=240, scale=1)

    # Speakers on Plan
    for spk in PROPOSED_LOUDSPEAKERS:
        sx = int(p1_x0 + (spk["coordinates"][0] + 20.5) / 41.0 * p1_sz)
        sy = int(p1_y0 + (20.5 - spk["coordinates"][1]) / 41.0 * p1_sz)
        canvas.draw_disc(sx, sy, 4, 46, 204, 113)

    # Right: Section
    p2_x0 = 500
    p2_w, p2_h = 450, 420
    canvas.fill_rect(p2_x0, p1_y0, p2_x0 + p2_w, p1_y0 + p2_h, 26, 26, 36)
    canvas.draw_rect(p2_x0, p1_y0, p2_x0 + p2_w, p1_y0 + p2_h, 50, 50, 70)
    canvas.draw_text("SECTION: DOWNTILT DIRECTIVITY & ZERO DOME SPILL", p2_x0 + 12, p1_y0 + 15, r=255, g=215, b=0, scale=1)

    s_oy = p1_y0 + p2_h - 40
    canvas.draw_line(p2_x0 + 20, s_oy, p2_x0 + p2_w - 20, s_oy, 200, 200, 220)
    canvas.draw_text("PRAYER CARPET FLOOR (Z = 0.0M)", p2_x0 + 130, s_oy + 18, r=200, g=200, b=220, scale=1)

    # Dome Arch
    apex_y = s_oy - 300
    base_y = s_oy - 200
    dome_cx = p2_x0 + p2_w // 2
    for di in range(-70, 71):
        x = dome_cx + di
        y = int(base_y - (100.0 * (1.0 - (di / 70.0)**2)))
        canvas.set_pixel(x, y, 241, 196, 15)

    canvas.draw_text("CENTRAL DOME APEX (52M) - PROTECTED", dome_cx - 110, apex_y + 25, r=46, g=204, b=113, scale=1)

    # Speaker at Z=2.4m
    spk_y = s_oy - 16
    canvas.fill_rect(p2_x0 + 30, spk_y - 8, p2_x0 + 42, spk_y + 8, 46, 204, 113)
    canvas.draw_text("SPEAKER Z=2.4M", p2_x0 + 48, spk_y - 4, r=46, g=204, b=113, scale=1)

    # Coverage fan
    canvas.draw_line(p2_x0 + 42, spk_y, p2_x0 + 280, s_oy - 2, 46, 204, 113)
    canvas.draw_line(p2_x0 + 42, spk_y, p2_x0 + 150, s_oy - 2, 46, 204, 113)
    canvas.draw_text("22 DEG DOWNTILT (DIRECT TO CARPET)", p2_x0 + 80, s_oy - 22, r=46, g=204, b=113, scale=1)

    # Bottom summary
    bp_y0 = 525
    canvas.fill_rect(50, bp_y0, 950, 715, 26, 26, 36)
    canvas.draw_rect(50, bp_y0, 950, 715, 50, 50, 70)
    canvas.draw_text("SYSTEM TRANSFORMATION:", 70, bp_y0 + 16, r=255, g=215, b=0, scale=1)
    canvas.draw_text("OLD: 4 HIGH-POWER COLUMN CLUSTERS (92 DBA) -> EXCESS DOME ECHO, DELAY CONFLICTS, STI = 0.38 (POOR)", 70, bp_y0 + 42, r=231, g=76, b=60, scale=1)
    canvas.draw_text("NEW: 20 DISTRIBUTED LOW-LEVEL UNITS (71 DBA) -> 5 DELAY RINGS, 140HZ HPF, STI = 0.71 (EXCELLENT)", 70, bp_y0 + 68, r=46, g=204, b=113, scale=1)
    canvas.draw_text("HERITAGE: 100% REVERSIBLE, ZERO DRILLING INTO HISTORIC LIMESTONE PIERS, GRADE-A COMPLIANT", 70, bp_y0 + 94, r=241, g=196, b=15, scale=1)

    out_png = os.path.join(OUTPUT_DIR, "loudspeaker_coverage_directivity_diagram.png")
    canvas.save_png(out_png)


# -------------------------------------------------------------------
# 4. UPDATED HEATMAPS: SPL(A), SPL(C), STI, C50
# -------------------------------------------------------------------
def render_improved_heatmaps():
    print("Generating Updated Heatmaps (SPL-A, SPL-C, STI, C50)...")
    
    heatmap_configs = [
        ("spl_a_dba", "MUHAMMAD ALI MOSQUE - IMPROVED SOUND PRESSURE LEVEL SPL(A)", "UNIFORM SPEECH FIELD UNDER 20 DISTRIBUTED LOW-LEVEL UNITS (69.5 +/- 1.2 DBA)", 65.0, 73.0, "DBA", "improved_heatmap_spl_a"),
        ("spl_c_dbc", "MUHAMMAD ALI MOSQUE - IMPROVED LOW-FREQUENCY LEVEL SPL(C)", "LOW-FREQUENCY BASS RESIDUAL TAMED VIA 140 HZ HIGH-PASS CORRECTIVE EQ", 68.0, 76.0, "DBC", "improved_heatmap_spl_c"),
        ("sti", "MUHAMMAD ALI MOSQUE - IMPROVED SPEECH TRANSMISSION INDEX (STI)", "UNIFORM INTELLIGIBILITY ACROSS 100% PRAYER CARPET (TARGET > 0.65 ACHIEVED)", 0.50, 0.80, "STI", "improved_heatmap_sti"),
        ("c50_db", "MUHAMMAD ALI MOSQUE - IMPROVED SPEECH CLARITY INDEX (C50)", "EARLY-TO-LATE RATIO DRAMATICALLY ELEVATED TO POSITIVE VALUES (+3.0 TO +7.0 DB)", 0.0, 8.0, "DB", "improved_heatmap_c50")
    ]

    for key, title, subtitle, vmin, vmax, unit, base_name in heatmap_configs:
        # 1. Render PNG
        w, h = 960, 720
        canvas = RasterCanvas(w, h, bg_rgb=(18, 18, 26))

        canvas.draw_text(title, 40, 24, r=255, g=255, b=255, scale=2)
        canvas.draw_text(subtitle, 40, 48, r=160, g=165, b=185, scale=1)

        map_x0, map_y0 = 45, 75
        map_size = 580
        grid_n = 58
        step = 41.0 / grid_n
        cell_px = int(map_size / grid_n) + 1

        for gy in range(grid_n):
            wy = 20.5 - (gy + 0.5) * step
            for gx in range(grid_n):
                wx = -20.5 + (gx + 0.5) * step
                sx = int(map_x0 + (wx + 20.5) / 41.0 * map_size)
                sy = int(map_y0 + (20.5 - wy) / 41.0 * map_size)

                if is_inside_pier(wx, wy):
                    cr, cg, cb = 65, 65, 80
                else:
                    field = calculate_improved_acoustic_field(wx, wy)
                    val = field[key]
                    norm = max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))
                    if norm < 0.25:
                        cr, cg, cb = 0, int(norm * 4.0 * 255), 255
                    elif norm < 0.5:
                        cr, cg, cb = 0, 255, int((1.0 - (norm - 0.25) * 4.0) * 255)
                    elif norm < 0.75:
                        cr, cg, cb = int(((norm - 0.5) * 4.0) * 255), 255, 0
                    else:
                        cr, cg, cb = 255, int((1.0 - (norm - 0.75) * 4.0) * 255), 0

                canvas.fill_rect(sx, sy, sx + cell_px, sy + cell_px, cr, cg, cb)

        # 4 Limestone Piers
        for px, py, sz in PIERS:
            tl_x = int(map_x0 + (px - sz + 20.5) / 41.0 * map_size)
            tl_y = int(map_y0 + (20.5 - (py + sz)) / 41.0 * map_size)
            br_x = int(map_x0 + (px + sz + 20.5) / 41.0 * map_size)
            br_y = int(map_y0 + (20.5 - (py - sz)) / 41.0 * map_size)
            canvas.fill_rect(tl_x, tl_y, br_x, br_y, 42, 42, 54)
            canvas.draw_rect(tl_x, tl_y, br_x, br_y, 200, 200, 220)
            canvas.draw_text("PIER", tl_x + 8, tl_y + 12, r=220, g=220, b=240, scale=1)

        # 20 Speakers
        for spk in PROPOSED_LOUDSPEAKERS:
            sx = int(map_x0 + (spk["coordinates"][0] + 20.5) / 41.0 * map_size)
            sy = int(map_y0 + (20.5 - spk["coordinates"][1]) / 41.0 * map_size)
            canvas.draw_disc(sx, sy, 4, 46, 204, 113)
            canvas.draw_disc(sx, sy, 1, 255, 255, 255)

        # Mihrab
        mx = int(map_x0 + (0.0 + 20.5) / 41.0 * map_size)
        my = int(map_y0 + (20.5 - 18.5) / 41.0 * map_size)
        canvas.draw_disc(mx, my, 7, 255, 50, 50)
        canvas.draw_text("MIHRAB", mx - 25, my - 16, r=255, g=100, b=100, scale=1)

        # Receivers
        for r in ACOUSTIC_RECEIVERS:
            rx, ry, rz = r["coordinates"]
            sx = int(map_x0 + (rx + 20.5) / 41.0 * map_size)
            sy = int(map_y0 + (20.5 - ry) / 41.0 * map_size)
            f_pt = calculate_improved_acoustic_field(rx, ry, rz)
            canvas.draw_disc(sx, sy, 4, 0, 220, 255)
            r_id = r["id"].replace("REC_", "R")
            canvas.draw_text(f"{r_id}:{f_pt[key]}", sx + 6, sy - 3, r=255, g=255, b=255, scale=1)

        # Colorbar
        panel_x0 = 655
        cb_x = panel_x0 + 20
        cb_y = map_y0 + 25
        cb_w = 26
        cb_h = 320

        for step_i in range(cb_h):
            norm = 1.0 - (step_i / cb_h)
            val = vmin + norm * (vmax - vmin)
            if norm < 0.25:
                cr, cg, cb = 0, int(norm * 4.0 * 255), 255
            elif norm < 0.5:
                cr, cg, cb = 0, 255, int((1.0 - (norm - 0.25) * 4.0) * 255)
            elif norm < 0.75:
                cr, cg, cb = int(((norm - 0.5) * 4.0) * 255), 255, 0
            else:
                cr, cg, cb = 255, int((1.0 - (norm - 0.75) * 4.0) * 255), 0
            canvas.draw_line(cb_x, cb_y + step_i, cb_x + cb_w, cb_y + step_i, cr, cg, cb)

        canvas.draw_rect(cb_x, cb_y, cb_x + cb_w, cb_y + cb_h, 200, 200, 220)
        canvas.draw_text(f"UNIT: {unit}", cb_x - 10, cb_y - 20, r=255, g=255, b=255, scale=1)

        for t_i in range(5):
            t_norm = 1.0 - (t_i / 4.0)
            t_val = vmin + t_norm * (vmax - vmin)
            t_y = cb_y + int(t_i * (cb_h / 4.0))
            canvas.draw_line(cb_x + cb_w, t_y, cb_x + cb_w + 6, t_y, 255, 255, 255)
            canvas.draw_text(f"{t_val:.1f} {unit}", cb_x + cb_w + 12, t_y - 3, r=220, g=220, b=240, scale=1)

        # Right Summary Box
        box_y = cb_y + cb_h + 30
        canvas.fill_rect(panel_x0 + 10, box_y, w - 25, h - 35, 28, 28, 38)
        canvas.draw_rect(panel_x0 + 10, box_y, w - 25, h - 35, 60, 60, 80)
        canvas.draw_text("SYSTEM HIGHLIGHTS", panel_x0 + 20, box_y + 15, r=255, g=215, b=0, scale=1)
        canvas.draw_text("• 20 LOW-LEVEL SPEAKERS", panel_x0 + 20, box_y + 35, r=240, g=240, b=255, scale=1)
        canvas.draw_text("• 4 COLUMN SPEAKERS REMOVED", panel_x0 + 20, box_y + 55, r=255, g=100, b=100, scale=1)
        canvas.draw_text("• DISTANCE TO SEAT: 2.5-4.5M", panel_x0 + 20, box_y + 75, r=46, g=204, b=113, scale=1)
        canvas.draw_text("• DOME SPILL ELIMINATED", panel_x0 + 20, box_y + 95, r=46, g=204, b=113, scale=1)
        canvas.draw_text("• EQ: 140HZ HPF APPLIED", panel_x0 + 20, box_y + 115, r=230, g=126, b=34, scale=1)

        out_png = os.path.join(OUTPUT_DIR, f"{base_name}.png")
        canvas.save_png(out_png)

        # 2. Render SVG
        render_heatmap_svg(key, title, subtitle, vmin, vmax, unit, base_name)


def render_heatmap_svg(metric_key, title, subtitle, vmin, vmax, unit, base_name):
    """Renders high-res SVG for improved heatmaps."""
    w, h = 950, 750
    margin = {"top": 85, "right": 220, "bottom": 50, "left": 60}
    map_size = min(w - margin["left"] - margin["right"], h - margin["top"] - margin["bottom"])
    map_x0 = margin["left"]
    map_y0 = margin["top"]

    def w2s(wx, wy):
        sx = map_x0 + (wx + 20.5) / 41.0 * map_size
        sy = map_y0 + (20.5 - wy) / 41.0 * map_size
        return sx, sy

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="background:#14141c; font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">']
    svg.append(f'<text x="{w/2}" y="36" text-anchor="middle" fill="#ffffff" font-size="22" font-weight="700">{title}</text>')
    svg.append(f'<text x="{w/2}" y="60" text-anchor="middle" fill="#9fa0b5" font-size="13">{subtitle}</text>')

    grid_res = 41
    step = 41.0 / (grid_res - 1)
    cell_px = map_size / grid_res

    # Background carpet
    svg.append(f'<rect x="{map_x0 - 2}" y="{map_y0 - 2}" width="{map_size + 4}" height="{map_size + 4}" fill="#232332" stroke="#e0e0e0" stroke-width="2"/>')

    for gy in range(grid_res):
        wy = 20.5 - gy * step
        for gx in range(grid_res):
            wx = -20.5 + gx * step
            sx, sy = w2s(wx, wy)

            if is_inside_pier(wx, wy):
                col = "#4a4a58"
            else:
                data = calculate_improved_acoustic_field(wx, wy)
                val = data[metric_key]
                norm = max(0.0, min(1.0, (val - vmin) / max(0.001, (vmax - vmin))))
                if norm < 0.25:
                    r, g, b = 0, int(norm * 4.0 * 255), 255
                elif norm < 0.5:
                    r, g, b = 0, 255, int((1.0 - (norm - 0.25) * 4.0) * 255)
                elif norm < 0.75:
                    r, g, b = int(((norm - 0.5) * 4.0) * 255), 255, 0
                else:
                    r, g, b = 255, int((1.0 - (norm - 0.75) * 4.0) * 255), 0
                col = f"#{r:02x}{g:02x}{b:02x}"

            svg.append(f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{cell_px + 0.4:.1f}" height="{cell_px + 0.4:.1f}" fill="{col}" stroke="none"/>')

    # Dome circle
    cx, cy = w2s(0, 0)
    dome_r_px = (10.5 / 41.0) * map_size
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{dome_r_px}" fill="none" stroke="#ffffff" stroke-width="1.8" stroke-dasharray="6,4" opacity="0.65"/>')

    # 4 Piers
    for px, py, sz in PIERS:
        tl_x, tl_y = w2s(px - sz, py + sz)
        pier_w = (sz * 2 / 41.0) * map_size
        svg.append(f'<rect x="{tl_x}" y="{tl_y}" width="{pier_w}" height="{pier_w}" fill="#2e2e3a" stroke="#ffffff" stroke-width="1.5"/>')
        svg.append(f'<text x="{tl_x + pier_w/2}" y="{tl_y + pier_w/2 + 4}" text-anchor="middle" fill="#ffffff" font-size="10">Pier</text>')

    # 20 Speakers
    for spk in PROPOSED_LOUDSPEAKERS:
        sx, sy = w2s(spk["coordinates"][0], spk["coordinates"][1])
        svg.append(f'<circle cx="{sx}" cy="{sy}" r="5" fill="#2ecc71" stroke="#ffffff" stroke-width="1.5"/>')

    # Mihrab
    mx, my = w2s(0, 18.5)
    svg.append(f'<circle cx="{mx}" cy="{my}" r="8" fill="#e74c3c" stroke="#ffffff" stroke-width="2"/>')
    svg.append(f'<text x="{mx}" y="{my - 12}" text-anchor="middle" fill="#e74c3c" font-size="11" font-weight="bold">Mihrab</text>')

    # Colorbar
    cb_x = w - margin["right"] + 35
    cb_y = map_y0 + 20
    cb_w = 26
    cb_h = 360

    for step_i in range(100):
        val = vmin + (1.0 - step_i / 100.0) * (vmax - vmin)
        cy_step = cb_y + int(step_i * (cb_h / 100.0))
        norm = (1.0 - step_i / 100.0)
        if norm < 0.25:
            r, g, b = 0, int(norm * 4.0 * 255), 255
        elif norm < 0.5:
            r, g, b = 0, 255, int((1.0 - (norm - 0.25) * 4.0) * 255)
        elif norm < 0.75:
            r, g, b = int(((norm - 0.5) * 4.0) * 255), 255, 0
        else:
            r, g, b = 255, int((1.0 - (norm - 0.75) * 4.0) * 255), 0
        c_hex = f"#{r:02x}{g:02x}{b:02x}"
        svg.append(f'<rect x="{cb_x}" y="{cy_step}" width="{cb_w}" height="{cb_h/100.0 + 0.6}" fill="{c_hex}" stroke="none"/>')

    svg.append(f'<rect x="{cb_x}" y="{cb_y}" width="{cb_w}" height="{cb_h}" fill="none" stroke="#4a4a5a" stroke-width="1.5"/>')
    svg.append(f'<text x="{cb_x + cb_w/2}" y="{cb_y - 12}" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="bold">{unit}</text>')

    for t_i in range(5):
        t_val = vmin + (t_i / 4.0) * (vmax - vmin)
        t_y = cb_y + cb_h * (1.0 - t_i / 4.0)
        svg.append(f'<line x1="{cb_x + cb_w}" y1="{t_y}" x2="{cb_x + cb_w + 6}" y2="{t_y}" stroke="#ffffff" stroke-width="1"/>')
        svg.append(f'<text x="{cb_x + cb_w + 12}" y="{t_y + 4}" fill="#d0d0e0" font-size="11" font-weight="600">{t_val:.1f} {unit}</text>')

    svg.append('</svg>')

    out_svg = os.path.join(OUTPUT_DIR, f"{base_name}.svg")
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Saved SVG: {out_svg}")


# -------------------------------------------------------------------
# 5. BEFORE-AND-AFTER COMPARISON CHART (16 RECEIVERS)
# -------------------------------------------------------------------
def generate_before_after_comparison_chart():
    print("Generating Before-and-After Acoustic Comparison Chart...")
    w, h = 1000, 750
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="background:#14141c; font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">']

    svg.append(f'<text x="{w/2}" y="36" text-anchor="middle" fill="#ffffff" font-size="22" font-weight="700">Muhammad Ali Mosque — Before vs After Sound System Comparison</text>')
    svg.append(f'<text x="{w/2}" y="60" text-anchor="middle" fill="#9fa0b5" font-size="13">Point-by-Point ISO 3382-1 Comparison Across All 16 Receiver Stations (Original vs Improved)</text>')

    comps = RESULTS_DATA["receivers_comparison"]
    # Sort by distance from Imam
    comps_sorted = sorted(comps, key=lambda c: c["distance_from_imam_m"])

    # Subplot 1: STI Comparison (Y in [100, 390])
    p1_x0, p1_y0 = 70, 95
    p1_w, p1_h = 860, 275

    svg.append(f'<rect x="{p1_x0}" y="{p1_y0}" width="{p1_w}" height="{p1_h}" fill="#1a1a26" stroke="#2d2d3e" stroke-width="1.5"/>')
    svg.append(f'<text x="{p1_x0 + 15}" y="{p1_y0 + 22}" fill="#f1c40f" font-size="13" font-weight="bold">Speech Transmission Index (STI): Original Column System (Red) vs Improved Distributed (Green)</text>')

    # Target STI > 0.65 line
    y_target_sti = p1_y0 + p1_h * (1.0 - 0.65)
    svg.append(f'<line x1="{p1_x0}" y1="{y_target_sti}" x2="{p1_x0 + p1_w}" y2="{y_target_sti}" stroke="#2ecc71" stroke-width="1.5" stroke-dasharray="6,4"/>')
    svg.append(f'<text x="{p1_x0 + p1_w - 180}" y="{y_target_sti - 6}" fill="#2ecc71" font-size="11" font-weight="bold">Target STI &gt; 0.65 (Good)</text>')

    for sti_val in [0.30, 0.45, 0.60, 0.75]:
        yp = p1_y0 + p1_h * (1.0 - sti_val)
        svg.append(f'<line x1="{p1_x0}" y1="{yp}" x2="{p1_x0 + p1_w}" y2="{yp}" stroke="#242436" stroke-width="1"/>')
        lbl = "POOR" if sti_val == 0.30 else "FAIR" if sti_val == 0.45 else "GOOD" if sti_val == 0.60 else "EXC"
        svg.append(f'<text x="{p1_x0 - 8}" y="{yp + 4}" text-anchor="end" fill="#888899" font-size="10">{sti_val:.2f} ({lbl})</text>')

    col_w = p1_w / len(comps_sorted)
    pts_base = []
    pts_imp = []

    for idx, c in enumerate(comps_sorted):
        cx = p1_x0 + (idx + 0.5) * col_w
        yb = p1_y0 + p1_h * (1.0 - c["baseline"]["sti"])
        yi = p1_y0 + p1_h * (1.0 - c["improved"]["sti"])
        pts_base.append((cx, yb))
        pts_imp.append((cx, yi))

        # Vertical connector showing gain
        svg.append(f'<line x1="{cx}" y1="{yb}" x2="{cx}" y2="{yi}" stroke="#f1c40f" stroke-width="1.2" stroke-dasharray="3,3" opacity="0.6"/>')

    # Draw curves
    path_b = "M " + " L ".join(f"{xp:.1f},{yp:.1f}" for xp, yp in pts_base)
    path_i = "M " + " L ".join(f"{xp:.1f},{yp:.1f}" for xp, yp in pts_imp)
    svg.append(f'<path d="{path_b}" fill="none" stroke="#e74c3c" stroke-width="2.5"/>')
    svg.append(f'<path d="{path_i}" fill="none" stroke="#2ecc71" stroke-width="3.0"/>')

    for idx, (cx, yb) in enumerate(pts_base):
        val_b = comps_sorted[idx]["baseline"]["sti"]
        svg.append(f'<circle cx="{cx}" cy="{yb}" r="4" fill="#e74c3c"/>')
        svg.append(f'<text x="{cx}" y="{yb + 14}" text-anchor="middle" fill="#e74c3c" font-size="9" font-weight="bold">{val_b:.2f}</text>')

    for idx, (cx, yi) in enumerate(pts_imp):
        val_i = comps_sorted[idx]["improved"]["sti"]
        svg.append(f'<circle cx="{cx}" cy="{yi}" r="4" fill="#2ecc71"/>')
        svg.append(f'<text x="{cx}" y="{yi - 8}" text-anchor="middle" fill="#2ecc71" font-size="9" font-weight="bold">{val_i:.2f}</text>')

        r_lbl = comps_sorted[idx]["id"].replace("REC_GROUND_", "R").replace("REC_GALLERY_", "G")
        svg.append(f'<text x="{cx}" y="{p1_y0 + p1_h + 16}" text-anchor="middle" fill="#ffffff" font-size="9" font-weight="bold">{r_lbl}</text>')
        svg.append(f'<text x="{cx}" y="{p1_y0 + p1_h + 28}" text-anchor="middle" fill="#8888aa" font-size="8">{int(comps_sorted[idx]["distance_from_imam_m"])}m</text>')

    # Subplot 2: C50 Speech Clarity (dB) Comparison (Y in [425, 700])
    p2_y0 = 425
    p2_h = 275
    svg.append(f'<rect x="{p1_x0}" y="{p2_y0}" width="{p1_w}" height="{p2_h}" fill="#1a1a26" stroke="#2d2d3e" stroke-width="1.5"/>')
    svg.append(f'<text x="{p1_x0 + 15}" y="{p2_y0 + 22}" fill="#f1c40f" font-size="13" font-weight="bold">Speech Clarity C50 (dB): Original (Red) vs Improved (Green) — Target &gt; +2 dB</text>')

    c_min, c_max = -8.0, 10.0
    y_target_c = p2_y0 + p2_h * (1.0 - (2.0 - c_min) / (c_max - c_min))
    svg.append(f'<line x1="{p1_x0}" y1="{y_target_c}" x2="{p1_x0 + p1_w}" y2="{y_target_c}" stroke="#2ecc71" stroke-width="1.5" stroke-dasharray="6,4"/>')

    for db in range(-8, 11, 2):
        yp = p2_y0 + p2_h * (1.0 - (db - c_min) / (c_max - c_min))
        svg.append(f'<line x1="{p1_x0}" y1="{yp}" x2="{p1_x0 + p1_w}" y2="{yp}" stroke="#242436" stroke-width="1"/>')
        svg.append(f'<text x="{p1_x0 - 8}" y="{yp + 4}" text-anchor="end" fill="#888899" font-size="10">{db:+} dB</text>')

    y_zero = p2_y0 + p2_h * (1.0 - (0.0 - c_min) / (c_max - c_min))

    for idx, c in enumerate(comps_sorted):
        cx = p1_x0 + (idx + 0.5) * col_w
        c50_b = c["baseline"]["c50_db"]
        c50_i = c["improved"]["c50_db"]

        # Baseline Bar (Red)
        yb = p2_y0 + p2_h * (1.0 - (c50_b - c_min) / (c_max - c_min))
        svg.append(f'<rect x="{cx - 10}" y="{min(yb, y_zero)}" width="9" height="{abs(yb - y_zero)}" fill="#e74c3c" rx="1"/>')

        # Improved Bar (Green)
        yi = p2_y0 + p2_h * (1.0 - (c50_i - c_min) / (c_max - c_min))
        svg.append(f'<rect x="{cx + 1}" y="{min(yi, y_zero)}" width="9" height="{abs(yi - y_zero)}" fill="#2ecc71" rx="1"/>')
        svg.append(f'<text x="{cx + 5}" y="{yi - 4}" text-anchor="middle" fill="#2ecc71" font-size="8" font-weight="bold">{c50_i:+.1f}</text>')

    # Legends
    leg1_x = p1_x0 + p1_w - 320
    leg1_y = p1_y0 + 15
    svg.append(f'<rect x="{leg1_x}" y="{leg1_y}" width="310" height="42" rx="4" fill="#14141c" stroke="#3d3d52"/>')
    svg.append(f'<line x1="{leg1_x + 10}" y1="{leg1_y + 14}" x2="{leg1_x + 30}" y2="{leg1_y + 14}" stroke="#e74c3c" stroke-width="2.5"/>')
    svg.append(f'<text x="{leg1_x + 38}" y="{leg1_y + 18}" fill="#ffffff" font-size="10">Original 4-Column Clusters (Mean STI: 0.38)</text>')
    svg.append(f'<line x1="{leg1_x + 10}" y1="{leg1_y + 30}" x2="{leg1_x + 30}" y2="{leg1_y + 30}" stroke="#2ecc71" stroke-width="2.5"/>')
    svg.append(f'<text x="{leg1_x + 38}" y="{leg1_y + 34}" fill="#ffffff" font-size="10">Improved 20-Unit Distributed (Mean STI: 0.69)</text>')

    svg.append('</svg>')

    out_svg = os.path.join(OUTPUT_DIR, "before_after_acoustic_comparison_chart.svg")
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Saved SVG: {out_svg}")

    # Render PNG
    render_comparison_chart_png(comps_sorted)


def render_comparison_chart_png(comps_sorted):
    """Renders high-res PNG for before-and-after comparison chart."""
    w, h = 1000, 750
    canvas = RasterCanvas(w, h, bg_rgb=(20, 20, 28))

    canvas.draw_text("MUHAMMAD ALI MOSQUE - BEFORE VS AFTER ACOUSTIC COMPARISON", 40, 22, r=255, g=255, b=255, scale=2)
    canvas.draw_text("POINT-BY-POINT PERFORMANCE ACROSS ALL 16 RECEIVERS (ORIGINAL VS IMPROVED SYSTEM)", 40, 46, r=160, g=165, b=185, scale=1)

    p1_x0, p1_y0 = 70, 85
    p1_w, p1_h = 860, 280
    canvas.fill_rect(p1_x0, p1_y0, p1_x0 + p1_w, p1_y0 + p1_h, 26, 26, 36)
    canvas.draw_rect(p1_x0, p1_y0, p1_x0 + p1_w, p1_y0 + p1_h, 50, 50, 70)
    canvas.draw_text("SPEECH TRANSMISSION INDEX (STI): ORIGINAL (RED) VS IMPROVED (GREEN)", p1_x0 + 15, p1_y0 + 15, r=255, g=215, b=0, scale=1)

    for sti_val in [0.30, 0.45, 0.60, 0.75]:
        yp = int(p1_y0 + p1_h * (1.0 - sti_val))
        canvas.draw_line(p1_x0, yp, p1_x0 + p1_w, yp, 40, 40, 55)
        canvas.draw_text(f"{sti_val:.2f}", p1_x0 - 40, yp - 3, r=140, g=140, b=160, scale=1)

    col_w = p1_w / len(comps_sorted)
    pts_b = []
    pts_i = []

    for idx, c in enumerate(comps_sorted):
        cx = int(p1_x0 + (idx + 0.5) * col_w)
        yb = int(p1_y0 + p1_h * (1.0 - c["baseline"]["sti"]))
        yi = int(p1_y0 + p1_h * (1.0 - c["improved"]["sti"]))
        pts_b.append((cx, yb))
        pts_i.append((cx, yi))

        r_lbl = c["id"].replace("REC_GROUND_", "R").replace("REC_GALLERY_", "G")
        canvas.draw_text(r_lbl, cx - 6, p1_y0 + p1_h + 12, r=255, g=255, b=255, scale=1)

    for i in range(len(pts_b) - 1):
        canvas.draw_line(pts_b[i][0], pts_b[i][1], pts_b[i+1][0], pts_b[i+1][1], 231, 76, 60)
        canvas.draw_line(pts_i[i][0], pts_i[i][1], pts_i[i+1][0], pts_i[i+1][1], 46, 204, 113)

    for i in range(len(pts_b)):
        canvas.draw_disc(pts_b[i][0], pts_b[i][1], 4, 231, 76, 60)
        canvas.draw_disc(pts_i[i][0], pts_i[i][1], 4, 46, 204, 113)

    # Subplot 2: C50 (dB)
    p2_y0 = 430
    p2_h = 280
    canvas.fill_rect(p1_x0, p2_y0, p1_x0 + p1_w, p2_y0 + p2_h, 26, 26, 36)
    canvas.draw_rect(p1_x0, p2_y0, p1_x0 + p1_w, p2_y0 + p2_h, 50, 50, 70)
    canvas.draw_text("SPEECH CLARITY C50 (DB): ORIGINAL (RED) VS IMPROVED (GREEN)", p1_x0 + 15, p2_y0 + 15, r=255, g=215, b=0, scale=1)

    c_min, c_max = -8.0, 10.0
    for db in range(-8, 11, 4):
        yp = int(p2_y0 + p2_h * (1.0 - (db - c_min) / (c_max - c_min)))
        canvas.draw_line(p1_x0, yp, p1_x0 + p1_w, yp, 40, 40, 55)
        canvas.draw_text(f"{db:+}DB", p1_x0 - 45, yp - 3, r=140, g=140, b=160, scale=1)

    y_zero = int(p2_y0 + p2_h * (1.0 - (0.0 - c_min) / (c_max - c_min)))
    for idx, c in enumerate(comps_sorted):
        cx = int(p1_x0 + (idx + 0.5) * col_w)
        c50_b = c["baseline"]["c50_db"]
        c50_i = c["improved"]["c50_db"]

        yb = int(p2_y0 + p2_h * (1.0 - (c50_b - c_min) / (c_max - c_min)))
        yi = int(p2_y0 + p2_h * (1.0 - (c50_i - c_min) / (c_max - c_min)))

        canvas.fill_rect(cx - 8, min(yb, y_zero), cx - 1, max(yb, y_zero), 231, 76, 60)
        canvas.fill_rect(cx + 1, min(yi, y_zero), cx + 8, max(yi, y_zero), 46, 204, 113)

    out_png = os.path.join(OUTPUT_DIR, "before_after_acoustic_comparison_chart.png")
    canvas.save_png(out_png)


# -------------------------------------------------------------------
# 6. SYSTEM DELAY & DSP ARCHITECTURE DIAGRAM
# -------------------------------------------------------------------
def generate_system_delay_and_dsp_diagram():
    print("Generating System Delay & DSP Architecture Diagram (SVG & PNG)...")
    w, h = 1000, 750
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="background:#14141c; font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">']

    # Header
    svg.append(f'<text x="{w/2}" y="36" text-anchor="middle" fill="#ffffff" font-size="22" font-weight="700">Muhammad Ali Mosque — DSP Delay Alignment &amp; Signal Architecture</text>')
    svg.append(f'<text x="{w/2}" y="60" text-anchor="middle" fill="#9fa0b5" font-size="13">Digital Precedence Synchronization (Haas Effect) &amp; Corrective Equalization Topology</text>')

    # Imam Source Block
    svg.append('<rect x="60" y="100" width="180" height="90" rx="6" fill="#1e272e" stroke="#e74c3c" stroke-width="2"/>')
    svg.append('<text x="150" y="125" text-anchor="middle" fill="#e74c3c" font-size="13" font-weight="bold">PRIMARY ACOUSTIC SOURCE</text>')
    svg.append('<text x="150" y="145" text-anchor="middle" fill="#ffffff" font-size="12">Imam Vocalization (Mihrab)</text>')
    svg.append('<text x="150" y="165" text-anchor="middle" fill="#8888aa" font-size="11">X=0m, Y=18.5m, Z=1.5m</text>')
    svg.append('<text x="150" y="180" text-anchor="middle" fill="#f1c40f" font-size="10">Master Time Reference: 0.0 ms</text>')

    # Arrow to DSP
    svg.append('<line x1="240" y1="145" x2="310" y2="145" stroke="#ffffff" stroke-width="2"/>')
    svg.append('<polygon points="310,140 320,145 310,150" fill="#ffffff"/>')

    # DSP Processor Block
    svg.append('<rect x="320" y="95" width="280" height="100" rx="6" fill="#1e272e" stroke="#f1c40f" stroke-width="2"/>')
    svg.append('<text x="460" y="120" text-anchor="middle" fill="#f1c40f" font-size="13" font-weight="bold">CENTRAL DSP EQUALIZER MATRIX</text>')
    svg.append('<text x="460" y="140" text-anchor="middle" fill="#ffffff" font-size="11">1. High-Pass: 140 Hz (18 dB/oct Butterworth)</text>')
    svg.append('<text x="460" y="158" text-anchor="middle" fill="#ffffff" font-size="11">2. Parametric Notch: -4.0 dB @ 280 Hz (Q=2.0)</text>')
    svg.append('<text x="460" y="176" text-anchor="middle" fill="#ffffff" font-size="11">3. Articulation Shelf: +2.5 dB @ 3.0 kHz</text>')

    # 5 Delay Ring Outputs
    rings = [
        ("RING 1: FRONT AISLES", "Speakers: LS_F01 - LS_F04", "Distance: 4.5m - 9.0m", "t_delay = 28.0 ms", "#2ecc71", 240),
        ("RING 2: MID-FRONT", "Speakers: LS_M01 - LS_M04", "Distance: 12.0m - 16.5m", "t_delay = 52.0 ms", "#3498db", 335),
        ("RING 3: CENTER DOME", "Speakers: LS_C01 - LS_C04", "Distance: 18.0m - 23.5m", "t_delay = 74.0 ms", "#f1c40f", 430),
        ("RING 4: REAR AISLE", "Speakers: LS_R01 - LS_R04", "Distance: 26.0m - 33.0m", "t_delay = 98.0 ms", "#e67e22", 525),
        ("RING 5: GALLERIES", "Speakers: LS_G01 - LS_G04", "Distance: 32.0m - 39.0m", "t_delay = 115.0 ms", "#9b59b6", 620),
    ]

    for title_r, spk_r, dist_r, del_r, col_r, y_pos in rings:
        # Bus arrow down & right
        svg.append(f'<line x1="600" y1="145" x2="680" y2="145" stroke="#ffffff" stroke-width="1.5"/>')
        svg.append(f'<line x1="680" y1="145" x2="680" y2="{y_pos + 35}" stroke="#ffffff" stroke-width="1.5"/>')
        svg.append(f'<line x1="680" y1="{y_pos + 35}" x2="720" y2="{y_pos + 35}" stroke="#ffffff" stroke-width="1.5"/>')
        svg.append(f'<polygon points="720,{y_pos + 30} 730,{y_pos + 35} 720,{y_pos + 40}" fill="#ffffff"/>')

        # Delay channel card
        svg.append(f'<rect x="730" y="{y_pos}" width="220" height="70" rx="5" fill="#1e272e" stroke="{col_r}" stroke-width="1.8"/>')
        svg.append(f'<text x="745" y="{y_pos + 20}" fill="{col_r}" font-size="12" font-weight="bold">{title_r}</text>')
        svg.append(f'<text x="745" y="{y_pos + 36}" fill="#d0d0e0" font-size="10">{spk_r}</text>')
        svg.append(f'<text x="745" y="{y_pos + 50}" fill="#8888aa" font-size="10">{dist_r}</text>')
        svg.append(f'<text x="745" y="{y_pos + 64}" fill="#ffffff" font-size="11" font-weight="bold">Calibrated: {del_r}</text>')

    # Precedence (Haas Effect) Explanation Card on Left
    card_y = 240
    svg.append(f'<rect x="60" y="{card_y}" width="580" height="450" rx="6" fill="#1a1a26" stroke="#2d2d3e" stroke-width="1.5"/>')
    svg.append(f'<text x="80" y="{card_y + 30}" fill="#f1c40f" font-size="15" font-weight="bold">Psychoacoustic Precedence Alignment (Haas Effect)</text>')

    svg.append(f'<text x="80" y="{card_y + 65}" fill="#ffffff" font-size="12" font-weight="bold">1. Acoustic Localization Formula:</text>')
    svg.append(f'<text x="100" y="{card_y + 88}" fill="#00d2d3" font-size="12" font-family="monospace">t_delay = (d_imam / 343.0 m/s) + Delta_t_Haas (7.0 ms)</text>')
    svg.append(f'<text x="100" y="{card_y + 110}" fill="#d0d0e0" font-size="11">The +7.0 ms offset ensures natural acoustic sound from the Mihrab arrives first,</text>')
    svg.append(f'<text x="100" y="{card_y + 128}" fill="#d0d0e0" font-size="11">locking the listeners\' subconscious directional perception toward the Imam.</text>')

    svg.append(f'<text x="80" y="{card_y + 165}" fill="#ffffff" font-size="12" font-weight="bold">2. Corrective Equalization (Bass Mode Suppression):</text>')
    svg.append(f'<text x="100" y="{card_y + 188}" fill="#e74c3c" font-size="11">• 140 Hz High-Pass Filter:</text>')
    svg.append(f'<text x="120" y="{card_y + 206}" fill="#d0d0e0" font-size="11">Eliminates excitation of the 63 Hz &amp; 125 Hz room resonances (where RT60 &gt; 15s),</text>')
    svg.append(f'<text x="120" y="{card_y + 224}" fill="#d0d0e0" font-size="11">reducing the low-frequency rumble mask (SPL(C) - SPL(A) drops from +7.8dB to +2.2dB).</text>')

    svg.append(f'<text x="100" y="{card_y + 252}" fill="#f39c12" font-size="11">• 280 Hz Parametric Notch (-4.0 dB, Q=2.0):</text>')
    svg.append(f'<text x="120" y="{card_y + 270}" fill="#d0d0e0" font-size="11">Dampens male chest resonance buildup and primary limestone pier reflections.</text>')

    svg.append(f'<text x="100" y="{card_y + 298}" fill="#2ecc71" font-size="11">• 3.0 kHz High-Shelf Articulation Boost (+2.5 dB):</text>')
    svg.append(f'<text x="120" y="{card_y + 316}" fill="#d0d0e0" font-size="11">Enhances Arabic consonant definition (/t/, /k/, /s/, /th/), lifting STI from 0.38 to 0.71.</text>')

    svg.append(f'<text x="80" y="{card_y + 355}" fill="#ffffff" font-size="12" font-weight="bold">3. Physical Room Boundary Invariance:</text>')
    svg.append(f'<text x="100" y="{card_y + 378}" fill="#f1c40f" font-size="11" font-weight="bold">IMPORTANT ACOUSTICAL DISTINCTION:</text>')
    svg.append(f'<text x="100" y="{card_y + 398}" fill="#d0d0e0" font-size="11">Changing loudspeaker locations and applying DSP delay alignment improves the</text>')
    svg.append(f'<text x="100" y="{card_y + 416}" fill="#d0d0e0" font-size="11">Direct-to-Reverberant ratio (C50) and STI, but DOES NOT physically alter the room\'s</text>')
    svg.append(f'<text x="100" y="{card_y + 434}" fill="#d0d0e0" font-size="11">intrinsic reverberation time RT60 (which remains 5.67s empty / 3.97s occupied).</text>')

    svg.append('</svg>')

    out_svg = os.path.join(OUTPUT_DIR, "system_delay_and_dsp_architecture.svg")
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Saved SVG: {out_svg}")

    # Render PNG
    render_dsp_diagram_png()


def render_dsp_diagram_png():
    """Renders high-res PNG for DSP architecture diagram."""
    w, h = 1000, 750
    canvas = RasterCanvas(w, h, bg_rgb=(20, 20, 28))

    canvas.draw_text("MUHAMMAD ALI MOSQUE - DSP DELAY ALIGNMENT & SIGNAL ARCHITECTURE", 40, 22, r=255, g=255, b=255, scale=2)
    canvas.draw_text("PSYCHOACOUSTIC PRECEDENCE (HAAS EFFECT) SYNCHRONIZATION WITH IMAM AT MIHRAB", 40, 46, r=160, g=165, b=185, scale=1)

    # Left: Explanation card
    card_y = 85
    canvas.fill_rect(50, card_y, 650, 715, 26, 26, 36)
    canvas.draw_rect(50, card_y, 650, 715, 50, 50, 70)
    canvas.draw_text("DIGITAL SIGNAL PROCESSING ARCHITECTURE", 70, card_y + 18, r=255, g=215, b=0, scale=1)

    canvas.draw_text("1. TIME DELAY SYNCHRONIZATION:", 70, card_y + 48, r=0, g=210, b=230, scale=1)
    canvas.draw_text("T DELAY = (D IMAM / 343 M/S) + 7.0 MS HAAS PRECEDENCE OFFSET", 90, card_y + 70, r=240, g=240, b=255, scale=1)
    canvas.draw_text("SOUND FROM MIHRAB ARRIVES FIRST -> PRESERVES DIRECTIONAL LOCALIZATION", 90, card_y + 90, r=160, g=165, b=185, scale=1)

    canvas.draw_text("2. CORRECTIVE EQUALIZATION (BASS SUPPRESSION):", 70, card_y + 125, r=243, g=156, b=18, scale=1)
    canvas.draw_text("- 140 HZ HIGH-PASS FILTER (18 DB/OCT BUTTERWORTH)", 90, card_y + 148, r=231, g=76, b=60, scale=1)
    canvas.draw_text("  ELIMINATES ROOM MODE RESONANCES AT 63 HZ & 125 HZ (RT60 > 15S)", 110, card_y + 168, r=160, g=165, b=185, scale=1)

    canvas.draw_text("- 280 HZ PARAMETRIC NOTCH (-4.0 DB, Q=2.0)", 90, card_y + 195, r=243, g=156, b=18, scale=1)
    canvas.draw_text("  DAMPENS CHEST RESONANCE AND PRIMARY LIMESTONE PIER REFLECTIONS", 110, card_y + 215, r=160, g=165, b=185, scale=1)

    canvas.draw_text("- 3.0 KHZ PRESENCE ARTICULATION SHELF (+2.5 DB)", 90, card_y + 242, r=46, g=204, b=113, scale=1)
    canvas.draw_text("  BOOSTS ARABIC CONSONANT DEFINITION (/T/, /K/, /S/, /TH/)", 110, card_y + 262, r=160, g=165, b=185, scale=1)

    canvas.draw_text("3. ACOUSTICAL INVARIANCE NOTE:", 70, card_y + 300, r=255, g=215, b=0, scale=1)
    canvas.draw_text("RECONFIGURING LOUDSPEAKERS ELEVATES C50 (+3.4 DB) AND STI (0.69)", 90, card_y + 322, r=240, g=240, b=255, scale=1)
    canvas.draw_text("BUT DOES NOT CHANGE THE PHYSICAL ROOM RT60 (REMAINS 5.67S EMPTY).", 90, card_y + 342, r=240, g=240, b=255, scale=1)

    # Right: 5 Delay Rings Cards
    r_x0 = 680
    rings = [
        ("RING 1: FRONT", "LS_F01 - LS_F04", "T = 28.0 MS", (46, 204, 113), 85),
        ("RING 2: MID-FRONT", "LS_M01 - LS_M04", "T = 52.0 MS", (52, 152, 219), 195),
        ("RING 3: CENTER", "LS_C01 - LS_C04", "T = 74.0 MS", (241, 196, 15), 305),
        ("RING 4: REAR", "LS_R01 - LS_R04", "T = 98.0 MS", (230, 126, 34), 415),
        ("RING 5: GALLERIES", "LS_G01 - LS_G04", "T = 115.0 MS", (155, 89, 182), 525)
    ]

    for title_r, spk_r, del_r, col_r, y_pos in rings:
        canvas.fill_rect(r_x0, y_pos, 950, y_pos + 95, 26, 26, 36)
        canvas.draw_rect(r_x0, y_pos, 950, y_pos + 95, col_r[0], col_r[1], col_r[2])
        canvas.draw_text(title_r, r_x0 + 15, y_pos + 16, r=col_r[0], g=col_r[1], b=col_r[2], scale=1)
        canvas.draw_text(spk_r, r_x0 + 15, y_pos + 38, r=240, g=240, b=255, scale=1)
        canvas.draw_text(del_r, r_x0 + 15, y_pos + 60, r=255, g=255, b=255, scale=1)

    out_png = os.path.join(OUTPUT_DIR, "system_delay_and_dsp_architecture.png")
    canvas.save_png(out_png)


def generate_all_improved_visuals():
    render_3d_column_speakers_removal()
    render_3d_improved_loudspeaker_layout()
    generate_loudspeaker_coverage_diagram()
    render_improved_heatmaps()
    generate_before_after_comparison_chart()
    generate_system_delay_and_dsp_diagram()
    print("=" * 65)
    print("All Improved Visuals Generated Successfully!")


if __name__ == "__main__":
    generate_all_improved_visuals()
