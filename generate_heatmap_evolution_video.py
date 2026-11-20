"""Dynamic Acoustic Heatmap Evolution Video and GIF Generator.

Simulates the time-dependent spatial sound pressure field (SPL-A and SPL-C)
across the 41m x 41m floor of the Muhammad Ali Mosque:
  - Direct sound wavefront expansion from Mihrab (t = 0.0 to 0.12s)
  - Pier scattering and acoustic shadow formation (t = 0.12 to 0.35s)
  - Diffuse reverberant buildup and bass energy entrapment (t = 0.35 to 2.5s)
  - Continuous vocalization steady-state field
  - Sound cutoff and slow low-frequency decay tail (t = 2.5 to 5.0s)

Outputs:
  - reports/mosque_heatmap_evolution_5s.mp4 (H.264, 25fps, 125 frames)
  - reports/mosque_heatmap_evolution.gif (high-quality animated GIF)
  - reports/heatmap_stage1_direct_wavefront.png (t = 0.06s)
  - reports/heatmap_stage2_pier_scattering.png (t = 0.20s)
  - reports/heatmap_stage3_dome_reverberation.png (t = 0.65s)
  - reports/heatmap_stage4_spl_c_bass_accumulation.png (t = 2.40s)
  - reports/heatmap_stage5_decay_tail.png (t = 4.20s)
"""

import os
import sys
import math
import subprocess

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

FFMPEG_EXE = r"E:\download\app\ffmpeg-9.0.1-essentials_build\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"

from mosque_acoustic_data import ACOUSTIC_RECEIVERS
from mosque_spatial_heatmaps import PIERS, is_inside_pier
from generate_heatmaps_and_spl_c import RasterCanvas

SPEED_OF_SOUND = 343.0  # m/s
SRC_X = 0.0
SRC_Y = 18.5
LW_A = 74.0
LW_C = 81.5


def compute_transient_field(wx, wy, t):
    """Computes instantaneous SPL(A) and SPL(C) at (wx, wy) at simulation time t (0 to 5s)."""
    if is_inside_pier(wx, wy):
        return None

    dx = wx - SRC_X
    dy = wy - SRC_Y
    dist = math.hypot(dx, dy)
    dist = max(1.0, dist)

    # Time of direct sound arrival
    t_direct = dist / SPEED_OF_SOUND

    # Directivity
    forward_angle = math.atan2(-dy, dx)
    q_dir = max(1.2, 3.5 * math.cos(forward_angle * 0.5))

    # Pier shadowing
    shadow_loss_db = 0.0
    for px, py, sz in PIERS:
        line_len = dist
        proj = ((px - SRC_X) * dx + (py - SRC_Y) * dy) / line_len
        if 0 < proj < line_len:
            perp = abs((px - SRC_X) * (-dy) + (py - SRC_Y) * dx) / line_len
            if perp < sz * 1.1:
                shadow_loss_db = max(shadow_loss_db, 5.0 * (1.0 - perp / (sz * 1.5)))

    # Direct sound term
    # Source speaks continuously for t in [0.0, 2.5], then stops
    is_source_on = (t < 2.5)
    direct_sound_active = (t >= t_direct) and (t < t_direct + 2.5)

    if direct_sound_active:
        direct_energy = q_dir / (4.0 * math.pi * dist * dist)
    else:
        direct_energy = 0.0

    # Reverberant buildup & decay
    # Buildup rate: (1 - exp(-t / tau)), where tau = RT60 / 13.82
    tau_mid = 4.21 / 13.82  # ~0.30s
    tau_bass = 8.10 / 13.82  # ~0.59s

    room_const_mid = 1415.0
    room_const_bass = 720.0

    # Diffuse A (mid frequencies)
    if t < 2.5:
        # Buildup
        diffuse_a = (4.0 / room_const_mid) * (1.0 - math.exp(-t / tau_mid))
        diffuse_c = (4.0 / room_const_bass) * (1.0 - math.exp(-t / tau_bass))
    else:
        # Decay from steady-state
        t_off = t - 2.5
        ss_diffuse_a = (4.0 / room_const_mid) * (1.0 - math.exp(-2.5 / tau_mid))
        ss_diffuse_c = (4.0 / room_const_bass) * (1.0 - math.exp(-2.5 / tau_bass))
        diffuse_a = ss_diffuse_a * math.exp(-t_off / tau_mid)
        diffuse_c = ss_diffuse_c * math.exp(-t_off / tau_bass)

    total_a = direct_energy + diffuse_a
    total_c = direct_energy * 0.7 + diffuse_c

    spl_a = LW_A + 10.0 * math.log10(max(1e-6, total_a)) - shadow_loss_db
    spl_c = (LW_C - 2.0) + 10.0 * math.log10(max(1e-6, total_c)) + 6.5 * (1.0 - math.exp(-dist / 15.0)) - shadow_loss_db

    # Clamping
    spl_a = max(25.0, min(75.0, spl_a))
    spl_c = max(30.0, min(80.0, spl_c))

    return {
        "spl_a": spl_a,
        "spl_c": spl_c,
        "direct_active": direct_sound_active,
        "dist": dist
    }


def render_heatmap_frame(t, width=960, height=720):
    """Renders a single simulation frame at time t (0.0 to 5.0s) showing the dynamic acoustic heat field."""
    canvas = RasterCanvas(width, height, bg_rgb=(18, 18, 26))

    # Header
    canvas.draw_text("MUHAMMAD ALI MOSQUE - ACOUSTIC HEATMAP SIMULATION", 40, 20, r=255, g=255, b=255, scale=2)

    # Subtitle based on phase
    if t < 0.12:
        phase_str = "PHASE 1: DIRECT SOUND WAVEFRONT PROPAGATING ACROSS PRAYER FLOOR"
        p_col = (0, 220, 240)
    elif t < 0.35:
        phase_str = "PHASE 2: PIER SCATTERING & ACOUSTIC SHADOW ZONE FORMATION"
        p_col = (255, 200, 50)
    elif t < 1.0:
        phase_str = "PHASE 3: DIFFUSE SOUND REFLECTIONS ACCUMULATING FROM DOME & WALLS"
        p_col = (255, 140, 40)
    elif t < 2.5:
        phase_str = "PHASE 4: STEADY STATE - EXCESS BASS ENERGY SPL(C) FLOODING HALL"
        p_col = (255, 70, 70)
    else:
        phase_str = "PHASE 5: SOUND CUTOFF - PERSISTENT LOW-FREQUENCY DECAY TAIL (8.1S)"
        p_col = (180, 120, 255)

    canvas.draw_text(phase_str, 40, 44, r=p_col[0], g=p_col[1], b=p_col[2], scale=1)

    # Map area layout: 41m x 41m floor
    map_x0, map_y0 = 45, 75
    map_size = 580
    map_x1 = map_x0 + map_size
    map_y1 = map_y0 + map_size

    def w2s(wx, wy):
        sx = int(map_x0 + (wx + 20.5) / 41.0 * map_size)
        sy = int(map_y0 + (20.5 - wy) / 41.0 * map_size)
        return sx, sy

    # Carpet floor base
    canvas.fill_rect(map_x0, map_y0, map_x1, map_y1, 28, 25, 36)

    # Render dynamic sound pressure field (Grid resolution 58x58 = 10px per cell)
    grid_n = 58
    step = 41.0 / grid_n
    cell_px = int(map_size / grid_n) + 1

    vmin = 35.0
    vmax = 75.0

    avg_spl_a = 0.0
    avg_spl_c = 0.0
    valid_pts = 0

    for gy in range(grid_n):
        wy = 20.5 - (gy + 0.5) * step
        for gx in range(grid_n):
            wx = -20.5 + (gx + 0.5) * step
            field = compute_transient_field(wx, wy, t)
            sx, sy = w2s(wx, wy)

            if field is None:
                # Inside limestone pier
                cr, cg, cb = 65, 65, 80
            else:
                # Display SPL(C) heat field (since user specifically requested SPL C heatmap)
                val = field["spl_c"]
                avg_spl_a += field["spl_a"]
                avg_spl_c += field["spl_c"]
                valid_pts += 1

                norm = max(0.0, min(1.0, (val - vmin) / (vmax - vmin)))
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

    if valid_pts > 0:
        avg_spl_a /= valid_pts
        avg_spl_c /= valid_pts

    # Wavefront circle expanding if t < 0.18s
    if t < 0.18:
        wf_r = SPEED_OF_SOUND * t
        wf_r_px = int((wf_r / 41.0) * map_size)
        mx_s, my_s = w2s(SRC_X, SRC_Y)
        canvas.draw_circle(mx_s, my_s, wf_r_px, 255, 255, 255, alpha=0.9)
        canvas.draw_circle(mx_s, my_s, max(1, wf_r_px - 2), 255, 230, 100, alpha=0.7)

    # Central Dome Circle
    dcx, dcy = w2s(0, 0)
    dome_r_px = int((10.5 / 41.0) * map_size)
    canvas.draw_circle(dcx, dcy, dome_r_px, 255, 255, 255, alpha=0.6)
    canvas.draw_text("CENTRAL DOME 21M", dcx - 70, dcy - 5, r=255, g=255, b=255, scale=1)

    # 4 Massive Piers
    for px, py, sz in PIERS:
        tl_x, tl_y = w2s(px - sz, py + sz)
        br_x, br_y = w2s(px + sz, py - sz)
        canvas.fill_rect(tl_x, tl_y, br_x, br_y, 42, 42, 54)
        canvas.draw_rect(tl_x, tl_y, br_x, br_y, 200, 200, 220)
        canvas.draw_text("PIER", tl_x + 8, tl_y + 12, r=220, g=220, b=240, scale=1)

    # Perimeter Walls
    for thick in range(3):
        canvas.draw_rect(map_x0 - thick, map_y0 - thick, map_x1 + thick, map_y1 + thick, 230, 230, 245)

    # Mihrab Source Marker
    mx, my = w2s(SRC_X, SRC_Y)
    src_active = (t < 2.5)
    src_col = (255, 50, 50) if src_active else (150, 150, 170)
    canvas.draw_disc(mx, my, 8, src_col[0], src_col[1], src_col[2])
    canvas.draw_disc(mx, my, 3, 255, 255, 255)
    canvas.draw_text("MIHRAB", mx - 25, my - 18, r=255, g=90, b=90, scale=1)

    # Receivers Overlay
    for r in ACOUSTIC_RECEIVERS:
        rx, ry, rz = r["coordinates"]
        sx, sy = w2s(rx, ry)
        pt_f = compute_transient_field(rx, ry, t)
        val_c = pt_f["spl_c"] if pt_f else 0.0
        col = (0, 220, 240) if rz < 5.0 else (255, 140, 230)
        canvas.draw_disc(sx, sy, 4, col[0], col[1], col[2])
        r_label = r["id"].replace("REC_", "R")
        canvas.draw_text(f"{r_label}:{val_c:.0f}", sx + 6, sy - 3, r=240, g=240, b=255, scale=1)

    # -------------------------------------------------------------
    # RIGHT SIDE PANEL: LIVE TELEMETRY, TIME HUD, COLORBAR & METERS
    # -------------------------------------------------------------
    panel_x0 = 655

    # 1. Digital Time HUD Box
    hud_y = map_y0
    canvas.fill_rect(panel_x0 + 10, hud_y, width - 25, hud_y + 85, 28, 28, 38)
    canvas.draw_rect(panel_x0 + 10, hud_y, width - 25, hud_y + 85, 55, 55, 75)

    canvas.draw_text("SIMULATION TIME", panel_x0 + 20, hud_y + 12, r=255, g=215, b=0, scale=1)
    ms_val = int(t * 1000)
    canvas.draw_text(f"T = {t:.2f} S ({ms_val:4d} MS)", panel_x0 + 20, hud_y + 28, r=255, g=255, b=255, scale=2)

    status_txt = "SOURCE: ACTIVE (VOCALIZING)" if t < 2.5 else "SOURCE: OFF (ROOM DECAYING)"
    st_col = (46, 204, 113) if t < 2.5 else (231, 76, 60)
    canvas.draw_text(status_txt, panel_x0 + 20, hud_y + 60, r=st_col[0], g=st_col[1], b=st_col[2], scale=1)

    # 2. Live SPL(C) vs SPL(A) Dual Meters
    meter_y = hud_y + 98
    canvas.fill_rect(panel_x0 + 10, meter_y, width - 25, meter_y + 120, 28, 28, 38)
    canvas.draw_rect(panel_x0 + 10, meter_y, width - 25, meter_y + 120, 55, 55, 75)

    canvas.draw_text("AVERAGE FLOOR SOUND PRESSURE", panel_x0 + 20, meter_y + 12, r=255, g=215, b=0, scale=1)

    # Meter SPL(C)
    canvas.draw_text(f"SPL(C) BASS:  {avg_spl_c:.1f} DBC", panel_x0 + 20, meter_y + 32, r=255, g=80, b=80, scale=1)
    c_bar_w = int(220 * max(0.0, min(1.0, (avg_spl_c - 30.0) / 50.0)))
    canvas.fill_rect(panel_x0 + 20, meter_y + 46, panel_x0 + 20 + 220, meter_y + 54, 40, 40, 52)
    canvas.fill_rect(panel_x0 + 20, meter_y + 46, panel_x0 + 20 + c_bar_w, meter_y + 54, 255, 70, 80)

    # Meter SPL(A)
    canvas.draw_text(f"SPL(A) SPEECH: {avg_spl_a:.1f} DBA", panel_x0 + 20, meter_y + 64, r=0, g=210, b=230, scale=1)
    a_bar_w = int(220 * max(0.0, min(1.0, (avg_spl_a - 30.0) / 50.0)))
    canvas.fill_rect(panel_x0 + 20, meter_y + 78, panel_x0 + 20 + 220, meter_y + 86, 40, 40, 52)
    canvas.fill_rect(panel_x0 + 20, meter_y + 78, panel_x0 + 20 + a_bar_w, meter_y + 86, 0, 210, 230)

    # Bass Delta
    delta = avg_spl_c - avg_spl_a
    canvas.draw_text(f"EXCESS BASS RUMBLE: +{delta:.1f} DB", panel_x0 + 20, meter_y + 98, r=255, g=200, b=50, scale=1)

    # 3. Colorbar (SPL-C dBC Scale)
    cb_x = panel_x0 + 20
    cb_y = meter_y + 135
    cb_w = 26
    cb_h = 190

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
    canvas.draw_text("SPL(C) DBC", cb_x - 5, cb_y - 15, r=255, g=255, b=255, scale=1)

    for t_i in range(5):
        t_norm = 1.0 - (t_i / 4.0)
        t_val = vmin + t_norm * (vmax - vmin)
        t_y = cb_y + int(t_i * (cb_h / 4.0))
        canvas.draw_line(cb_x + cb_w, t_y, cb_x + cb_w + 5, t_y, 255, 255, 255)
        canvas.draw_text(f"{t_val:.0f} DBC", cb_x + cb_w + 10, t_y - 3, r=220, g=220, b=240, scale=1)

    # 4. Hall Properties Card
    prop_y = cb_y + cb_h + 20
    canvas.fill_rect(panel_x0 + 10, prop_y, width - 25, height - 30, 28, 28, 38)
    canvas.draw_rect(panel_x0 + 10, prop_y, width - 25, height - 30, 55, 55, 75)
    canvas.draw_text("VENUE CONSTANTS", panel_x0 + 20, prop_y + 12, r=255, g=215, b=0, scale=1)
    canvas.draw_text("VOLUME: 39,840 M3", panel_x0 + 20, prop_y + 30, r=220, g=220, b=240, scale=1)
    canvas.draw_text("ALABASTER & MARBLE: 81.6%", panel_x0 + 20, prop_y + 46, r=255, g=150, b=100, scale=1)
    canvas.draw_text("RT60 BASS (63-125HZ): 8.1S", panel_x0 + 20, prop_y + 62, r=255, g=80, b=80, scale=1)
    canvas.draw_text("RT60 SPEECH (1KHZ):   4.2S", panel_x0 + 20, prop_y + 78, r=0, g=210, b=230, scale=1)

    return canvas


def generate_heatmap_video_and_assets():
    print("=" * 65)
    print("  GENERATING 5-SECOND HEATMAP EVOLUTION VIDEO, GIF & KEYFRAMES")
    print("=" * 65)

    fps = 25
    duration_s = 5.0
    total_frames = int(fps * duration_s)  # 125 frames
    w, h = 960, 720

    mp4_path = os.path.join(REPORTS_DIR, "mosque_heatmap_evolution_5s.mp4")
    gif_path = os.path.join(REPORTS_DIR, "mosque_heatmap_evolution.gif")

    # Keyframe capture timestamps
    keyframe_times = {
        0.06: "heatmap_stage1_direct_wavefront.png",
        0.20: "heatmap_stage2_pier_scattering.png",
        0.65: "heatmap_stage3_dome_reverberation.png",
        2.40: "heatmap_stage4_spl_c_bass_accumulation.png",
        4.20: "heatmap_stage5_decay_tail.png"
    }

    # 1. Pipe PPM frames to FFmpeg for MP4
    mp4_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "image2pipe",
        "-vcodec", "ppm",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        mp4_path
    ]

    print(f"Rendering {total_frames} frames to MP4: {mp4_path}")
    proc_mp4 = subprocess.Popen(mp4_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    saved_keyframes = set()
    ppm_header = f"P6\n{w} {h}\n255\n".encode("ascii")

    for frame_idx in range(total_frames):
        t = frame_idx / float(fps)
        canvas = render_heatmap_frame(t, w, h)
        frame_bytes = ppm_header + bytes(canvas.buf)
        proc_mp4.stdin.write(frame_bytes)

        # Check keyframe matches
        for k_time, k_name in keyframe_times.items():
            if abs(t - k_time) < (0.5 / fps) and k_name not in saved_keyframes:
                k_out = os.path.join(REPORTS_DIR, k_name)
                canvas.save_png(k_out)
                saved_keyframes.add(k_name)

        if frame_idx % 25 == 0:
            print(f"  Frame {frame_idx:3d}/{total_frames} (t = {t:.2f}s)")

    proc_mp4.stdin.close()
    proc_mp4.wait()
    print(f"MP4 successfully rendered: {mp4_path}")

    # 2. Render high quality GIF using palettegen + paletteuse
    print(f"Converting MP4 to high-quality animated GIF: {gif_path}")
    cmd_gif = [
        FFMPEG_EXE, "-y",
        "-i", mp4_path,
        "-vf", "fps=15,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
        gif_path
    ]
    subprocess.run(cmd_gif, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Animated GIF rendered: {gif_path}")
    print("=" * 65)


if __name__ == "__main__":
    generate_heatmap_video_and_assets()
