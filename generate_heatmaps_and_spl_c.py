"""Acoustic Heatmap and SPL(C) vs SPL(A) Comprehensive Visual Generator.

Generates:
1. High-resolution PNGs of all 4 spatial heatmaps:
   - mosque_heatmap_spl_a.png
   - mosque_heatmap_spl_c.png
   - mosque_heatmap_sti.png
   - mosque_heatmap_c50_clarity.png
2. SPL(C) vs SPL(A) Acoustic Diagnosis Chart:
   - mosque_spl_c_vs_spl_a_analysis.svg
   - mosque_spl_c_vs_spl_a_analysis.png
"""

import os
import sys
import math
import subprocess

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

FFMPEG_EXE = r"E:\download\app\ffmpeg-9.0.1-essentials_build\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"

from mosque_acoustic_data import MOSQUE_GEOMETRY, ACOUSTIC_RECEIVERS
from mosque_spatial_heatmaps import calculate_field_at_point, colormap_jet, PIERS

# -------------------------------------------------------------
# 5x7 BITMAP FONT FOR PURE-PYTHON RASTER RENDERING
# -------------------------------------------------------------
FONT_5x7 = {
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    '3': ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "01010", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    ':': ["00000", "00100", "00000", "00000", "00100", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "00100", "00100", "01000"],
    '-': ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    '+': ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    '=': ["00000", "11111", "00000", "11111", "00000", "00000", "00000"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '/': ["00001", "00010", "00100", "00100", "01000", "10000", "00000"],
    '%': ["11001", "11010", "00100", "01000", "01011", "10011", "00000"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}


class RasterCanvas:
    def __init__(self, width=960, height=720, bg_rgb=(20, 20, 28)):
        self.width = width
        self.height = height
        self.buf = bytearray(width * height * 3)
        self.fill(bg_rgb[0], bg_rgb[1], bg_rgb[2])

    def fill(self, r, g, b):
        for i in range(0, len(self.buf), 3):
            self.buf[i] = r
            self.buf[i + 1] = g
            self.buf[i + 2] = b

    def set_pixel(self, x, y, r, g, b):
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = (y * self.width + x) * 3
            self.buf[idx] = r
            self.buf[idx + 1] = g
            self.buf[idx + 2] = b

    def blend_pixel(self, x, y, r, g, b, alpha=0.5):
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = (y * self.width + x) * 3
            self.buf[idx] = int(self.buf[idx] * (1.0 - alpha) + r * alpha)
            self.buf[idx + 1] = int(self.buf[idx + 1] * (1.0 - alpha) + g * alpha)
            self.buf[idx + 2] = int(self.buf[idx + 2] * (1.0 - alpha) + b * alpha)

    def draw_line(self, x0, y0, x1, y1, r, g, b, alpha=1.0):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            if alpha >= 1.0:
                self.set_pixel(x0, y0, r, g, b)
            else:
                self.blend_pixel(x0, y0, r, g, b, alpha)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw_rect(self, x0, y0, x1, y1, r, g, b, alpha=1.0):
        self.draw_line(x0, y0, x1, y0, r, g, b, alpha)
        self.draw_line(x1, y0, x1, y1, r, g, b, alpha)
        self.draw_line(x1, y1, x0, y1, r, g, b, alpha)
        self.draw_line(x0, y1, x0, y0, r, g, b, alpha)

    def fill_rect(self, x0, y0, x1, y1, r, g, b, alpha=1.0):
        xa = max(0, min(x0, x1))
        xb = min(self.width - 1, max(x0, x1))
        ya = max(0, min(y0, y1))
        yb = min(self.height - 1, max(y0, y1))
        for y in range(ya, yb + 1):
            for x in range(xa, xb + 1):
                if alpha >= 1.0:
                    self.set_pixel(x, y, r, g, b)
                else:
                    self.blend_pixel(x, y, r, g, b, alpha)

    def draw_disc(self, cx, cy, radius, r, g, b):
        r2 = radius * radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= r2:
                    self.set_pixel(cx + dx, cy + dy, r, g, b)

    def draw_circle(self, cx, cy, radius, r, g, b, alpha=0.8):
        steps = int(2 * math.pi * radius)
        for i in range(steps):
            th = (2.0 * math.pi * i) / steps
            px = int(cx + radius * math.cos(th))
            py = int(cy + radius * math.sin(th))
            self.blend_pixel(px, py, r, g, b, alpha)

    def draw_text(self, text, x, y, r=255, g=255, b=255, scale=2):
        """Draws ASCII uppercase text with 5x7 font."""
        cur_x = x
        for ch in text.upper():
            glyph = FONT_5x7.get(ch, FONT_5x7[' '])
            for row_idx, row_bits in enumerate(glyph):
                for col_idx, bit in enumerate(row_bits):
                    if bit == '1':
                        px = cur_x + col_idx * scale
                        py = y + row_idx * scale
                        self.fill_rect(px, py, px + scale - 1, py + scale - 1, r, g, b)
            cur_x += (5 + 1) * scale

    def save_png(self, output_path):
        """Pipes raw RGB buffer to ffmpeg to output crisp PNG."""
        cmd = [
            FFMPEG_EXE, "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{self.width}x{self.height}",
            "-pix_fmt", "rgb24",
            "-i", "-",
            "-frames:v", "1",
            output_path
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        _, err = proc.communicate(input=bytes(self.buf))
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {err.decode('utf-8', errors='ignore')}")
        print(f"Saved PNG: {output_path}")


def render_spatial_heatmap_png(metric_key, title, subtitle, vmin, vmax, unit, filename):
    """Renders a 960x720 high-resolution PNG spatial acoustic heatmap."""
    w, h = 960, 720
    canvas = RasterCanvas(w, h, bg_rgb=(18, 18, 26))

    # Header Title & Subtitle
    canvas.draw_text(title, 40, 24, r=255, g=255, b=255, scale=2)
    canvas.draw_text(subtitle, 40, 48, r=160, g=165, b=185, scale=1)

    # Map area layout: 41m x 41m floor
    map_x0, map_y0 = 45, 75
    map_size = 580
    map_x1 = map_x0 + map_size
    map_y1 = map_y0 + map_size

    def w2s(wx, wy):
        sx = int(map_x0 + (wx + 20.5) / 41.0 * map_size)
        sy = int(map_y0 + (20.5 - wy) / 41.0 * map_size)
        return sx, sy

    # Carpet floor background
    canvas.fill_rect(map_x0, map_y0, map_x1, map_y1, 28, 25, 36)

    # Draw Heatmap Grid Cells (82 x 82 high resolution sampling = 0.5m grid)
    grid_n = 82
    step = 41.0 / grid_n
    cell_px = int(map_size / grid_n) + 1

    for gy in range(grid_n):
        wy = 20.5 - (gy + 0.5) * step
        for gx in range(grid_n):
            wx = -20.5 + (gx + 0.5) * step
            data = calculate_field_at_point(wx, wy)
            sx, sy = w2s(wx, wy)

            if data is None:
                # Inside limestone pier
                cr, cg, cb = 65, 65, 80
            else:
                val = data[metric_key]
                norm = max(0.0, min(1.0, (val - vmin) / max(0.001, (vmax - vmin))))
                # Rainbow Jet
                if norm < 0.25:
                    cr = 0
                    cg = int(norm * 4.0 * 255)
                    cb = 255
                elif norm < 0.5:
                    cr = 0
                    cg = 255
                    cb = int((1.0 - (norm - 0.25) * 4.0) * 255)
                elif norm < 0.75:
                    cr = int(((norm - 0.5) * 4.0) * 255)
                    cg = 255
                    cb = 0
                else:
                    cr = 255
                    cg = int((1.0 - (norm - 0.75) * 4.0) * 255)
                    cb = 0

            canvas.fill_rect(sx, sy, sx + cell_px, sy + cell_px, cr, cg, cb)

    # Dome circle
    dcx, dcy = w2s(0, 0)
    dome_r_px = int((10.5 / 41.0) * map_size)
    canvas.draw_circle(dcx, dcy, dome_r_px, 255, 255, 255, alpha=0.7)
    canvas.draw_text("CENTRAL DOME 21M", dcx - 70, dcy - 5, r=255, g=255, b=255, scale=1)

    # 4 Limestone Piers
    for px, py, sz in PIERS:
        tl_x, tl_y = w2s(px - sz, py + sz)
        br_x, br_y = w2s(px + sz, py - sz)
        canvas.fill_rect(tl_x, tl_y, br_x, br_y, 42, 42, 54)
        canvas.draw_rect(tl_x, tl_y, br_x, br_y, 200, 200, 220)
        canvas.draw_text("PIER", tl_x + 8, tl_y + 12, r=220, g=220, b=240, scale=1)

    # Outer Alabaster Wall perimeter
    for thick in range(3):
        canvas.draw_rect(map_x0 - thick, map_y0 - thick, map_x1 + thick, map_y1 + thick, 230, 230, 245)

    # Mihrab Source
    mx, my = w2s(0.0, 18.5)
    canvas.draw_disc(mx, my, 8, 255, 60, 60)
    canvas.draw_disc(mx, my, 3, 255, 255, 255)
    canvas.draw_text("MIHRAB (SOURCE)", mx - 55, my - 20, r=255, g=90, b=90, scale=1)

    # Minbar & Dikka
    kx, ky = w2s(2.8, 17.0)
    canvas.draw_disc(kx, ky, 6, 255, 170, 20)
    dk_x, dk_y = w2s(0.0, -8.0)
    canvas.draw_disc(dk_x, dk_y, 6, 170, 80, 255)
    canvas.draw_text("DIKKA", dk_x + 10, dk_y - 4, r=210, g=150, b=255, scale=1)

    # Receivers Overlay
    for r in ACOUSTIC_RECEIVERS:
        rx, ry, rz = r["coordinates"]
        sx, sy = w2s(rx, ry)
        pt_data = calculate_field_at_point(rx, ry)
        val_str = f"{pt_data[metric_key]}" if pt_data else ""
        col = (0, 220, 240) if rz < 5.0 else (255, 140, 230)
        canvas.draw_disc(sx, sy, 5, col[0], col[1], col[2])
        canvas.draw_disc(sx, sy, 2, 20, 20, 30)
        r_label = r["id"].replace("REC_", "R")
        canvas.draw_text(f"{r_label}:{val_str}", sx + 7, sy - 3, r=240, g=240, b=255, scale=1)

    # -------------------------------------------------------------
    # RIGHT SIDE PANEL: COLORBAR & LEGEND
    # -------------------------------------------------------------
    panel_x0 = 655
    cb_x = panel_x0 + 20
    cb_y = map_y0 + 25
    cb_w = 30
    cb_h = 320

    # Colorbar gradient
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

    # Colorbar ticks
    for t_i in range(7):
        t_norm = 1.0 - (t_i / 6.0)
        t_val = vmin + t_norm * (vmax - vmin)
        t_y = cb_y + int(t_i * (cb_h / 6.0))
        canvas.draw_line(cb_x + cb_w, t_y, cb_x + cb_w + 6, t_y, 255, 255, 255)
        canvas.draw_text(f"{t_val:.1f} {unit}", cb_x + cb_w + 12, t_y - 3, r=220, g=220, b=240, scale=1)

    # Legend info box below colorbar
    box_y = cb_y + cb_h + 35
    canvas.fill_rect(panel_x0 + 10, box_y, w - 25, h - 35, 28, 28, 38)
    canvas.draw_rect(panel_x0 + 10, box_y, w - 25, h - 35, 60, 60, 80)
    canvas.draw_text("ACOUSTIC SETUP", panel_x0 + 20, box_y + 15, r=255, g=215, b=0, scale=1)

    # Items
    canvas.draw_disc(panel_x0 + 25, box_y + 40, 5, 255, 60, 60)
    canvas.draw_text("MIHRAB IMAM (74 DBA)", panel_x0 + 38, box_y + 36, r=240, g=240, b=255, scale=1)

    canvas.draw_disc(panel_x0 + 25, box_y + 60, 5, 255, 170, 20)
    canvas.draw_text("MINBAR KHATIB", panel_x0 + 38, box_y + 56, r=240, g=240, b=255, scale=1)

    canvas.draw_disc(panel_x0 + 25, box_y + 80, 5, 170, 80, 255)
    canvas.draw_text("DIKKA MUEZZIN", panel_x0 + 38, box_y + 76, r=240, g=240, b=255, scale=1)

    canvas.draw_disc(panel_x0 + 25, box_y + 100, 5, 0, 220, 240)
    canvas.draw_text("GROUND RECEIVER (Z=1.2M)", panel_x0 + 38, box_y + 96, r=240, g=240, b=255, scale=1)

    canvas.draw_disc(panel_x0 + 25, box_y + 120, 5, 255, 140, 230)
    canvas.draw_text("GALLERY RECEIVER (Z=9.5M)", panel_x0 + 38, box_y + 116, r=240, g=240, b=255, scale=1)

    canvas.fill_rect(panel_x0 + 20, box_y + 138, panel_x0 + 30, box_y + 148, 65, 65, 80)
    canvas.draw_rect(panel_x0 + 20, box_y + 138, panel_x0 + 30, box_y + 148, 200, 200, 220)
    canvas.draw_text("PIERS (LIMESTONE 5X5M)", panel_x0 + 38, box_y + 138, r=240, g=240, b=255, scale=1)

    canvas.draw_text("ALABASTER ENVELOPE: 81.6%", panel_x0 + 20, box_y + 165, r=255, g=180, b=100, scale=1)
    canvas.draw_text(f"VOLUME: 39,840 M3", panel_x0 + 20, box_y + 185, r=180, g=190, b=210, scale=1)

    out_path = os.path.join(REPORTS_DIR, filename)
    canvas.save_png(out_path)
    return out_path


def generate_spl_c_vs_spl_a_analysis():
    """Generates a dedicated SVG and PNG chart diagnosing SPL(C) vs SPL(A) excess bass rumble."""
    print("=" * 65)
    print("  GENERATING SPL(C) VS SPL(A) BASS ACCUMULATION ANALYSIS CHART")
    print("=" * 65)

    w, h = 1000, 720
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="background:#14141c; font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">']

    # Header
    svg.append(f'<text x="{w/2}" y="36" text-anchor="middle" fill="#ffffff" font-size="22" font-weight="700">Muhammad Ali Mosque — SPL(C) vs SPL(A) Bass Resonance Diagnosis</text>')
    svg.append(f'<text x="{w/2}" y="60" text-anchor="middle" fill="#9fa0b5" font-size="13">Acoustic Masking Analysis: Low-Frequency Bass Energy Trapped by Alabaster and Marble Surfaces</text>')

    # -------------------------------------------------------------
    # TOP SUBPLOT: LONGITUDINAL SOUND LEVEL PROFILE (Y in [100, 360])
    # Distance from Mihrab (Y = +18.5m down to -18.5m, 0 to 37m)
    # -------------------------------------------------------------
    p1_x0, p1_y0 = 80, 105
    p1_w, p1_h = 840, 235

    svg.append(f'<rect x="{p1_x0}" y="{p1_y0}" width="{p1_w}" height="{p1_h}" fill="#1a1a26" stroke="#2d2d3e" stroke-width="1.5"/>')
    svg.append(f'<text x="{p1_x0 + 15}" y="{p1_y0 + 24}" fill="#f1c40f" font-size="14" font-weight="bold">Longitudinal Spatial Profile: Mihrab (0m) → Central Dome (18.5m) → Rear Entrance (37m)</text>')

    # Gridlines and Y-axis (45 dB to 80 dB)
    db_min, db_max = 45.0, 80.0
    for db_tick in range(45, 81, 5):
        y_pos = p1_y0 + p1_h * (1.0 - (db_tick - db_min) / (db_max - db_min))
        svg.append(f'<line x1="{p1_x0}" y1="{y_pos}" x2="{p1_x0 + p1_w}" y2="{y_pos}" stroke="#2a2a3e" stroke-width="1"/>')
        svg.append(f'<text x="{p1_x0 - 8}" y="{y_pos + 4}" text-anchor="end" fill="#888899" font-size="11">{db_tick} dB</text>')

    # X-axis distance ticks (0 to 37m)
    for dist in range(0, 40, 5):
        x_pos = p1_x0 + (dist / 37.0) * p1_w
        svg.append(f'<line x1="{x_pos}" y1="{p1_y0}" x2="{x_pos}" y2="{p1_y0 + p1_h}" stroke="#242436" stroke-width="1"/>')
        svg.append(f'<text x="{x_pos}" y="{p1_y0 + p1_h + 18}" text-anchor="middle" fill="#888899" font-size="11">{dist} m</text>')

    # Highlight Zones: Mihrab, Dome, Rear
    dome_center_x = p1_x0 + (18.5 / 37.0) * p1_w
    svg.append(f'<rect x="{dome_center_x - 70}" y="{p1_y0}" width="140" height="{p1_h}" fill="#f39c12" fill-opacity="0.08"/>')
    svg.append(f'<text x="{dome_center_x}" y="{p1_y0 + 45}" text-anchor="middle" fill="#f39c12" font-size="11" font-weight="600">Central Dome Area</text>')

    # Calculate points for SPL(C), SPL(A), and Delta
    pts_spl_a = []
    pts_spl_c = []
    pts_delta = []
    num_samples = 75
    for i in range(num_samples + 1):
        dist = (i / num_samples) * 37.0
        wy = 18.5 - dist  # From +18.5 to -18.5
        data = calculate_field_at_point(0.0, wy)
        if data:
            xp = p1_x0 + (dist / 37.0) * p1_w
            yp_a = p1_y0 + p1_h * (1.0 - (data["spl_a_dba"] - db_min) / (db_max - db_min))
            yp_c = p1_y0 + p1_h * (1.0 - (data["spl_c_dbc"] - db_min) / (db_max - db_min))
            pts_spl_a.append((xp, yp_a))
            pts_spl_c.append((xp, yp_c))
            delta = data["spl_c_dbc"] - data["spl_a_dba"]
            yp_delta = p1_y0 + p1_h * (1.0 - (45.0 + delta * 3.5 - db_min) / (db_max - db_min))
            pts_delta.append((xp, yp_delta))

    # Delta shaded band between SPL(A) and SPL(C)
    poly_pts = []
    for xp, yp in pts_spl_c:
        poly_pts.append(f"{xp:.1f},{yp:.1f}")
    for xp, yp in reversed(pts_spl_a):
        poly_pts.append(f"{xp:.1f},{yp:.1f}")
    svg.append(f'<polygon points="{" ".join(poly_pts)}" fill="#ff4757" fill-opacity="0.18"/>')

    # Line SPL(C) - Red
    path_c = "M " + " L ".join(f"{xp:.1f},{yp:.1f}" for xp, yp in pts_spl_c)
    svg.append(f'<path d="{path_c}" fill="none" stroke="#ff4757" stroke-width="3"/>')

    # Line SPL(A) - Cyan
    path_a = "M " + " L ".join(f"{xp:.1f},{yp:.1f}" for xp, yp in pts_spl_a)
    svg.append(f'<path d="{path_a}" fill="none" stroke="#00d2d3" stroke-width="3"/>')

    # Legend inside Plot 1
    leg_x = p1_x0 + p1_w - 240
    leg_y = p1_y0 + 15
    svg.append(f'<rect x="{leg_x}" y="{leg_y}" width="225" height="80" rx="4" fill="#14141c" stroke="#3d3d52"/>')
    svg.append(f'<line x1="{leg_x + 12}" y1="{leg_y + 20}" x2="{leg_x + 38}" y2="{leg_y + 20}" stroke="#ff4757" stroke-width="3"/>')
    svg.append(f'<text x="{leg_x + 46}" y="{leg_y + 24}" fill="#ff4757" font-size="11" font-weight="bold">SPL(C) Low-Freq Bass [dBC]</text>')

    svg.append(f'<line x1="{leg_x + 12}" y1="{leg_y + 42}" x2="{leg_x + 38}" y2="{leg_y + 42}" stroke="#00d2d3" stroke-width="3"/>')
    svg.append(f'<text x="{leg_x + 46}" y="{leg_y + 46}" fill="#00d2d3" font-size="11" font-weight="bold">SPL(A) Speech Band [dBA]</text>')

    svg.append(f'<rect x="{leg_x + 12}" y="{leg_y + 56}" width="26" height="12" fill="#ff4757" fill-opacity="0.35"/>')
    svg.append(f'<text x="{leg_x + 46}" y="{leg_y + 66}" fill="#fbc531" font-size="11" font-weight="bold">Excess Bass Rumble Δ: +7.5 to +9 dB</text>')

    # -------------------------------------------------------------
    # BOTTOM SUBPLOT: OCTAVE BAND REVERBERATION & WEIGHTING SPECTRUM (Y in [390, 670])
    # -------------------------------------------------------------
    p2_x0, p2_y0 = 80, 395
    p2_w, p2_h = 840, 250

    svg.append(f'<rect x="{p2_x0}" y="{p2_y0}" width="{p2_w}" height="{p2_h}" fill="#1a1a26" stroke="#2d2d3e" stroke-width="1.5"/>')
    svg.append(f'<text x="{p2_x0 + 15}" y="{p2_y0 + 24}" fill="#f1c40f" font-size="14" font-weight="bold">Octave Band Analysis (63 Hz to 8000 Hz): RT60 Decay vs Weighting Filter Profiles</text>')

    # Octave bands: 63, 125, 250, 500, 1000, 2000, 4000, 8000 Hz
    OCTAVES = ["63 Hz", "125 Hz", "250 Hz", "500 Hz", "1000 Hz", "2000 Hz", "4000 Hz", "8000 Hz"]
    RT60_SABINE = [8.52, 7.84, 6.72, 5.89, 5.14, 4.38, 3.42, 2.31]
    RT60_OCCUPIED = [8.10, 7.35, 5.95, 4.21, 3.82, 3.30, 2.75, 1.95]
    A_WEIGHTING = [-26.2, -16.1, -8.6, -3.2, 0.0, +1.2, +1.0, -1.1]
    C_WEIGHTING = [-0.8, -0.2, 0.0, 0.0, 0.0, -0.2, -0.8, -3.0]

    bar_group_w = p2_w / len(OCTAVES)
    for idx, oct_name in enumerate(OCTAVES):
        group_x = p2_x0 + idx * bar_group_w

        # Vertical separator
        if idx > 0:
            svg.append(f'<line x1="{group_x}" y1="{p2_y0 + 35}" x2="{group_x}" y2="{p2_y0 + p2_h - 30}" stroke="#252538" stroke-width="1"/>')

        # Octave label
        svg.append(f'<text x="{group_x + bar_group_w/2}" y="{p2_y0 + p2_h - 10}" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="bold">{oct_name}</text>')

        # Bar: Unoccupied RT60 (Scale: 0 to 10s -> max_h = 130)
        rt_u = RT60_SABINE[idx]
        bar_h_u = (rt_u / 10.0) * 130
        bar_x_u = group_x + bar_group_w * 0.15
        bar_y_u = p2_y0 + 170 - bar_h_u
        svg.append(f'<rect x="{bar_x_u}" y="{bar_y_u}" width="{bar_group_w * 0.32}" height="{bar_h_u}" fill="#e74c3c" rx="2"/>')
        svg.append(f'<text x="{bar_x_u + bar_group_w*0.16}" y="{bar_y_u - 5}" text-anchor="middle" fill="#e74c3c" font-size="11" font-weight="bold">{rt_u:.1f}s</text>')

        # Bar: Occupied RT60
        rt_o = RT60_OCCUPIED[idx]
        bar_h_o = (rt_o / 10.0) * 130
        bar_x_o = group_x + bar_group_w * 0.52
        bar_y_o = p2_y0 + 170 - bar_h_o
        svg.append(f'<rect x="{bar_x_o}" y="{bar_y_o}" width="{bar_group_w * 0.32}" height="{bar_h_o}" fill="#3498db" rx="2"/>')
        svg.append(f'<text x="{bar_x_o + bar_group_w*0.16}" y="{bar_y_o - 5}" text-anchor="middle" fill="#3498db" font-size="11" font-weight="bold">{rt_o:.1f}s</text>')

        # Weighting Filter badges below bars
        aw = A_WEIGHTING[idx]
        cw = C_WEIGHTING[idx]
        aw_str = f"{aw:+.1f}"
        cw_str = f"{cw:+.1f}"
        badge_y = p2_y0 + 185
        svg.append(f'<text x="{group_x + bar_group_w/2}" y="{badge_y}" text-anchor="middle" fill="#ff7675" font-size="10">C-wt: {cw_str} dB</text>')
        svg.append(f'<text x="{group_x + bar_group_w/2}" y="{badge_y + 16}" text-anchor="middle" fill="#74b9ff" font-size="10">A-wt: {aw_str} dB</text>')

    # Plot 2 Legend
    leg2_x = p2_x0 + p2_w - 330
    leg2_y = p2_y0 + 35
    svg.append(f'<rect x="{leg2_x}" y="{leg2_y}" width="315" height="52" rx="4" fill="#14141c" stroke="#3d3d52"/>')
    svg.append(f'<rect x="{leg2_x + 12}" y="{leg2_y + 12}" width="14" height="12" fill="#e74c3c" rx="2"/>')
    svg.append(f'<text x="{leg2_x + 32}" y="{leg2_y + 22}" fill="#ffffff" font-size="11">RT60 Unoccupied (Sabine)</text>')
    svg.append(f'<rect x="{leg2_x + 12}" y="{leg2_y + 30}" width="14" height="12" fill="#3498db" rx="2"/>')
    svg.append(f'<text x="{leg2_x + 32}" y="{leg2_y + 40}" fill="#ffffff" font-size="11">RT60 Occupied (1,200 Worshippers)</text>')

    svg.append('</svg>')

    out_svg = os.path.join(REPORTS_DIR, "mosque_spl_c_vs_spl_a_analysis.svg")
    with open(out_svg, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Saved SVG: {out_svg}")

    # Now render the PNG version of this diagnosis chart using RasterCanvas
    render_spl_c_analysis_png()


def render_spl_c_analysis_png():
    """Renders high-res PNG for SPL(C) vs SPL(A) analysis."""
    w, h = 1000, 720
    canvas = RasterCanvas(w, h, bg_rgb=(20, 20, 28))

    canvas.draw_text("MUHAMMAD ALI MOSQUE - SPL(C) VS SPL(A) BASS RESIDUAL DIAGNOSIS", 40, 22, r=255, g=255, b=255, scale=2)
    canvas.draw_text("EXCESS LOW-FREQUENCY REVERBERATION MASKING SPEECH INTELLIGIBILITY", 40, 46, r=160, g=165, b=185, scale=1)

    # Subplot 1: Longitudinal Profile
    p1_x0, p1_y0 = 60, 75
    p1_w, p1_h = 880, 260
    canvas.fill_rect(p1_x0, p1_y0, p1_x0 + p1_w, p1_y0 + p1_h, 26, 26, 36)
    canvas.draw_rect(p1_x0, p1_y0, p1_x0 + p1_w, p1_y0 + p1_h, 50, 50, 70)
    canvas.draw_text("LONGITUDINAL PROFILE: MIHRAB (0M) TO REAR ENTRANCE (37M)", p1_x0 + 15, p1_y0 + 15, r=255, g=215, b=0, scale=1)

    db_min, db_max = 45.0, 80.0
    for db_tick in range(45, 81, 5):
        y_pos = int(p1_y0 + p1_h * (1.0 - (db_tick - db_min) / (db_max - db_min)))
        canvas.draw_line(p1_x0, y_pos, p1_x0 + p1_w, y_pos, 40, 40, 55)
        canvas.draw_text(f"{db_tick}DB", p1_x0 - 38, y_pos - 3, r=140, g=140, b=160, scale=1)

    pts_spl_a = []
    pts_spl_c = []
    num_samples = 120
    for i in range(num_samples + 1):
        dist = (i / num_samples) * 37.0
        wy = 18.5 - dist
        data = calculate_field_at_point(0.0, wy)
        if data:
            xp = int(p1_x0 + (dist / 37.0) * p1_w)
            yp_a = int(p1_y0 + p1_h * (1.0 - (data["spl_a_dba"] - db_min) / (db_max - db_min)))
            yp_c = int(p1_y0 + p1_h * (1.0 - (data["spl_c_dbc"] - db_min) / (db_max - db_min)))
            pts_spl_a.append((xp, yp_a))
            pts_spl_c.append((xp, yp_c))

    # Fill shaded band
    for i in range(len(pts_spl_a)):
        xp = pts_spl_a[i][0]
        ya = pts_spl_a[i][1]
        yc = pts_spl_c[i][1]
        for y in range(min(ya, yc), max(ya, yc) + 1):
            canvas.blend_pixel(xp, y, 255, 70, 80, alpha=0.25)

    # Draw curves
    for i in range(len(pts_spl_c) - 1):
        canvas.draw_line(pts_spl_c[i][0], pts_spl_c[i][1], pts_spl_c[i + 1][0], pts_spl_c[i + 1][1], 255, 70, 80, alpha=1.0)
        canvas.draw_line(pts_spl_c[i][0], pts_spl_c[i][1] + 1, pts_spl_c[i + 1][0], pts_spl_c[i + 1][1] + 1, 255, 70, 80, alpha=1.0)

    for i in range(len(pts_spl_a) - 1):
        canvas.draw_line(pts_spl_a[i][0], pts_spl_a[i][1], pts_spl_a[i + 1][0], pts_spl_a[i + 1][1], 0, 210, 230, alpha=1.0)
        canvas.draw_line(pts_spl_a[i][0], pts_spl_a[i][1] + 1, pts_spl_a[i + 1][0], pts_spl_a[i + 1][1] + 1, 0, 210, 230, alpha=1.0)

    # Subplot 1 Legend
    canvas.fill_rect(p1_x0 + p1_w - 230, p1_y0 + 12, p1_x0 + p1_w - 15, p1_y0 + 75, 20, 20, 28)
    canvas.draw_line(p1_x0 + p1_w - 220, p1_y0 + 25, p1_x0 + p1_w - 195, p1_y0 + 25, 255, 70, 80)
    canvas.draw_text("SPL(C) BASS [DBC]", p1_x0 + p1_w - 190, p1_y0 + 22, r=255, g=70, b=80, scale=1)

    canvas.draw_line(p1_x0 + p1_w - 220, p1_y0 + 45, p1_x0 + p1_w - 195, p1_y0 + 45, 0, 210, 230)
    canvas.draw_text("SPL(A) SPEECH [DBA]", p1_x0 + p1_w - 190, p1_y0 + 42, r=0, g=210, b=230, scale=1)

    canvas.draw_text("DELTA SPL: +7.5 TO +9.0 DB", p1_x0 + p1_w - 220, p1_y0 + 60, r=255, g=200, b=50, scale=1)

    # Subplot 2: Octave Bars
    p2_x0, p2_y0 = 60, 365
    p2_w, p2_h = 880, 320
    canvas.fill_rect(p2_x0, p2_y0, p2_x0 + p2_w, p2_y0 + p2_h, 26, 26, 36)
    canvas.draw_rect(p2_x0, p2_y0, p2_x0 + p2_w, p2_y0 + p2_h, 50, 50, 70)
    canvas.draw_text("OCTAVE BANDS: RT60 DECAY TIME VS WEIGHTING FILTER ATTENUATION", p2_x0 + 15, p2_y0 + 15, r=255, g=215, b=0, scale=1)

    OCTAVES = ["63HZ", "125HZ", "250HZ", "500HZ", "1KHZ", "2KHZ", "4KHZ", "8KHZ"]
    RT60_SABINE = [8.52, 7.84, 6.72, 5.89, 5.14, 4.38, 3.42, 2.31]
    RT60_OCCUPIED = [8.10, 7.35, 5.95, 4.21, 3.82, 3.30, 2.75, 1.95]
    A_WT = ["-26DB", "-16DB", "-9DB", "-3DB", "0DB", "+1DB", "+1DB", "-1DB"]
    C_WT = ["-1DB", "0DB", "0DB", "0DB", "0DB", "0DB", "-1DB", "-3DB"]

    group_w = p2_w / len(OCTAVES)
    for idx, oct_name in enumerate(OCTAVES):
        gx = int(p2_x0 + idx * group_w)
        canvas.draw_text(oct_name, gx + 20, p2_y0 + p2_h - 22, r=255, g=255, b=255, scale=1)

        # Sabine Bar (Red)
        rt_u = RT60_SABINE[idx]
        bh_u = int((rt_u / 10.0) * 160)
        bx_u = gx + 15
        by_u = p2_y0 + 220 - bh_u
        canvas.fill_rect(bx_u, by_u, bx_u + 35, by_u + bh_u, 230, 75, 60)
        canvas.draw_text(f"{rt_u:.1f}S", bx_u + 2, by_u - 12, r=230, g=75, b=60, scale=1)

        # Occupied Bar (Blue)
        rt_o = RT60_OCCUPIED[idx]
        bh_o = int((rt_o / 10.0) * 160)
        bx_o = gx + 55
        by_o = p2_y0 + 220 - bh_o
        canvas.fill_rect(bx_o, by_o, bx_o + 35, by_o + bh_o, 52, 152, 219)
        canvas.draw_text(f"{rt_o:.1f}S", bx_o + 2, by_o - 12, r=52, g=152, b=219, scale=1)

        # Filter attenuation annotations
        canvas.draw_text(f"C:{C_WT[idx]}", gx + 12, p2_y0 + 235, r=255, g=118, b=117, scale=1)
        canvas.draw_text(f"A:{A_WT[idx]}", gx + 12, p2_y0 + 252, r=116, g=185, b=255, scale=1)

    # Subplot 2 Legend
    canvas.fill_rect(p2_x0 + p2_w - 290, p2_y0 + 12, p2_x0 + p2_w - 15, p2_y0 + 65, 20, 20, 28)
    canvas.fill_rect(p2_x0 + p2_w - 280, p2_y0 + 22, p2_x0 + p2_w - 265, p2_y0 + 34, 230, 75, 60)
    canvas.draw_text("RT60 UNOCCUPIED", p2_x0 + p2_w - 258, p2_y0 + 22, r=240, g=240, b=255, scale=1)

    canvas.fill_rect(p2_x0 + p2_w - 280, p2_y0 + 42, p2_x0 + p2_w - 265, p2_y0 + 54, 52, 152, 219)
    canvas.draw_text("RT60 OCCUPIED (1,200)", p2_x0 + p2_w - 258, p2_y0 + 42, r=240, g=240, b=255, scale=1)

    out_png = os.path.join(REPORTS_DIR, "mosque_spl_c_vs_spl_a_analysis.png")
    canvas.save_png(out_png)


def generate_all_images():
    print("=" * 65)
    print("  GENERATING HIGH-RES PNG SPATIAL HEATMAPS")
    print("=" * 65)

    # 1. SPL(A)
    render_spatial_heatmap_png(
        metric_key="spl_a_dba",
        title="MUHAMMAD ALI MOSQUE - SPATIAL SOUND PRESSURE LEVEL SPL(A)",
        subtitle="SPEECH SOUND FIELD ACROSS PRAYER FLOOR (IMAM SOURCE: 74 DBA)",
        vmin=48.0, vmax=72.0, unit="DBA",
        filename="mosque_heatmap_spl_a.png"
    )

    # 2. SPL(C)
    render_spatial_heatmap_png(
        metric_key="spl_c_dbc",
        title="MUHAMMAD ALI MOSQUE - LOW-FREQUENCY BASS PRESSURE LEVEL SPL(C)",
        subtitle="C-WEIGHTED BASS ACCUMULATION TRAPPED BY ALABASTER BOUNDARIES",
        vmin=56.0, vmax=78.0, unit="DBC",
        filename="mosque_heatmap_spl_c.png"
    )

    # 3. STI
    render_spatial_heatmap_png(
        metric_key="sti",
        title="MUHAMMAD ALI MOSQUE - SPEECH TRANSMISSION INDEX (STI)",
        subtitle="INTELLIGIBILITY DISTRIBUTION: EXCELLENT (>0.75) TO POOR (<0.45)",
        vmin=0.35, vmax=0.75, unit="STI",
        filename="mosque_heatmap_sti.png"
    )

    # 4. C50 Clarity
    render_spatial_heatmap_png(
        metric_key="c50_db",
        title="MUHAMMAD ALI MOSQUE - SPEECH CLARITY INDEX (C50)",
        subtitle="EARLY-TO-LATE RATIO (0-50MS VS >50MS): SPEECH TARGET > +2.0 DB",
        vmin=-5.0, vmax=7.0, unit="DB",
        filename="mosque_heatmap_c50_clarity.png"
    )

    # 5. SPL(C) vs SPL(A) Analysis
    generate_spl_c_vs_spl_a_analysis()
    print("=" * 65)
    print("All Heatmap PNGs and SPL(C) Analysis generated successfully!")


if __name__ == "__main__":
    generate_all_images()
