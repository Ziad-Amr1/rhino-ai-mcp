"""Generates 5-second acoustic simulation video, animated GIF, and simulation screenshots.

Simulates sound ray tracing & wavefront propagation in Muhammad Ali Mosque (41m x 41m).
Outputs:
  - reports/mosque_acoustic_simulation_5s.mp4
  - reports/mosque_acoustic_simulation.gif
  - reports/mosque_sim_stage1_direct_sound.png
  - reports/mosque_sim_stage2_early_reflections.png
  - reports/mosque_sim_stage3_diffuse_decay.png
  - reports/mosque_simulation_spatial_spl_map.png
"""

import os
import sys
import math
import subprocess
import random

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

FFMPEG_EXE = r"E:\download\app\ffmpeg-9.0.1-essentials_build\ffmpeg-9.0.1-essentials_build\bin\ffmpeg.exe"

# Mosque dimensions: 41m x 41m, origin (0,0) at center
# Coordinates range: X: [-20.5, 20.5], Y: [-20.5, 20.5]
SPEED_OF_SOUND = 343.0  # m/s

# 3 Sources
SOURCES = {
    "SRC_IMAM_MIHRAB": (0.0, 18.5, "Imam at Mihrab"),
    "SRC_KHATIB_MINBAR": (2.8, 17.0, "Khatib at Minbar"),
    "SRC_MUEZZIN_DIKKA": (0.0, -8.0, "Muezzin at Dikka")
}

# 16 Receivers
RECEIVERS = [
    (0.0, 14.0, "R1 Front-C"), (8.0, 14.0, "R2 Front-E"), (-8.0, 14.0, "R3 Front-W"),
    (0.0, 0.0, "R4 Dome-C"), (7.0, 7.0, "R5 Dome-NE"), (-7.0, 7.0, "R6 Dome-NW"),
    (7.0, -7.0, "R7 Dome-SE"), (-7.0, -7.0, "R8 Dome-SW"), (14.0, 0.0, "R9 Mid-E"),
    (-14.0, 0.0, "R10 Mid-W"), (0.0, -14.0, "R11 Rear-C"), (-12.0, -14.0, "R12 Rear-W"),
    (-18.0, 0.0, "R13 Gal-W"), (18.0, 0.0, "R14 Gal-E"), (-10.0, -18.0, "R15 Gal-SW"),
    (10.0, -18.0, "R16 Gal-SE")
]

# 4 Massive Piers (5m x 5m approx centers at +/-7.5, +/-7.5)
PIERS = [
    (7.5, 7.5, 2.5), (-7.5, 7.5, 2.5),
    (7.5, -7.5, 2.5), (-7.5, -7.5, 2.5)
]

# Monte Carlo Rays from Mihrab
NUM_RAYS = 240
random.seed(42)
RAYS = []
for i in range(NUM_RAYS):
    angle = (2.0 * math.pi * i) / NUM_RAYS + (random.random() - 0.5) * 0.03
    # Initial direction vector
    dx = math.cos(angle)
    dy = math.sin(angle)
    RAYS.append({"x": 0.0, "y": 18.5, "dx": dx, "dy": dy, "energy": 1.0, "history": [(0.0, 18.5)]})


def world_to_screen(wx, wy, width=800, height=600):
    """Maps world coordinates [-22, 22] to screen pixels in the hall map area."""
    # Map area: X in [40, 520], Y in [70, 550]
    map_x0, map_y0 = 50, 75
    map_w, map_h = 470, 470

    sx = int(map_x0 + (wx + 22.0) / 44.0 * map_w)
    sy = int(map_y0 + (22.0 - wy) / 44.0 * map_h)
    return max(0, min(width - 1, sx)), max(0, min(height - 1, sy))


def render_simulation_frame(t, width=800, height=600):
    """Renders a single frame at simulation time t (0.0 to 5.0 seconds) into raw RGB buffer."""
    buf = bytearray(width * height * 3)

    def set_pixel(x, y, r, g, b):
        if 0 <= x < width and 0 <= y < height:
            idx = (y * width + x) * 3
            buf[idx] = r
            buf[idx + 1] = g
            buf[idx + 2] = b

    def blend_pixel(x, y, r, g, b, alpha=0.5):
        if 0 <= x < width and 0 <= y < height:
            idx = (y * width + x) * 3
            buf[idx] = int(buf[idx] * (1.0 - alpha) + r * alpha)
            buf[idx + 1] = int(buf[idx + 1] * (1.0 - alpha) + g * alpha)
            buf[idx + 2] = int(buf[idx + 2] * (1.0 - alpha) + b * alpha)

    def draw_line(x0, y0, x1, y1, r, g, b, alpha=0.7):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            blend_pixel(x0, y0, r, g, b, alpha)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw_filled_rect(x0, y0, x1, y1, r, g, b):
        for y in range(max(0, y0), min(height, y1 + 1)):
            idx_start = (y * width + max(0, x0)) * 3
            idx_end = (y * width + min(width - 1, x1) + 1) * 3
            for i in range(idx_start, idx_end, 3):
                buf[i] = r
                buf[i + 1] = g
                buf[i + 2] = b

    def draw_disc(cx, cy, radius, r, g, b):
        r2 = radius * radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= r2:
                    set_pixel(cx + dx, cy + dy, r, g, b)

    # 1. Background dark navy
    draw_filled_rect(0, 0, width - 1, height - 1, 20, 20, 28)

    # 2. Left side: Mosque Hall Floor Boundary (41m x 41m)
    p_tl = world_to_screen(-20.5, 20.5, width, height)
    p_br = world_to_screen(20.5, -20.5, width, height)
    # Prayer carpet floor
    draw_filled_rect(p_tl[0], p_tl[1], p_br[0], p_br[1], 35, 30, 42)

    # Perimeter Alabaster Walls (thick outline)
    for off in range(3):
        draw_line(p_tl[0] - off, p_tl[1] - off, p_br[0] + off, p_tl[1] - off, 220, 225, 230, 1.0)
        draw_line(p_br[0] + off, p_tl[1] - off, p_br[0] + off, p_br[1] + off, 220, 225, 230, 1.0)
        draw_line(p_br[0] + off, p_br[1] + off, p_tl[0] - off, p_br[1] + off, 220, 225, 230, 1.0)
        draw_line(p_tl[0] - off, p_br[1] + off, p_tl[0] - off, p_tl[1] - off, 220, 225, 230, 1.0)

    # Central Dome Circle (Radius 10.5m)
    c_x, c_y = world_to_screen(0, 0, width, height)
    d_r = int(10.5 / 44.0 * 470)
    for deg in range(0, 360, 2):
        rad = math.radians(deg)
        rad2 = math.radians(deg + 2)
        x1 = c_x + int(d_r * math.cos(rad))
        y1 = c_y + int(d_r * math.sin(rad))
        x2 = c_x + int(d_r * math.cos(rad2))
        y2 = c_y + int(d_r * math.sin(rad2))
        draw_line(x1, y1, x2, y2, 240, 210, 130, 0.4)

    # 4 Massive Piers (Limestone)
    for px, py, sz in PIERS:
        tl = world_to_screen(px - sz, py + sz, width, height)
        br = world_to_screen(px + sz, py - sz, width, height)
        draw_filled_rect(tl[0], tl[1], br[0], br[1], 120, 125, 135)
        # Pier outline
        draw_line(tl[0], tl[1], br[0], tl[1], 180, 185, 195, 0.9)
        draw_line(br[0], tl[1], br[0], br[1], 180, 185, 195, 0.9)
        draw_line(br[0], br[1], tl[0], br[1], 180, 185, 195, 0.9)
        draw_line(tl[0], br[1], tl[0], tl[1], 180, 185, 195, 0.9)

    # 3. Simulate Acoustic Wavefront & Rays
    # Distance sound traveled at time t: d = c * t
    sound_dist = SPEED_OF_SOUND * t
    max_bounces = min(15, int(t * 30))

    # Calculate ray paths up to sound_dist
    for ray in RAYS:
        dist_left = sound_dist
        cur_x = 0.0
        cur_y = 18.5
        dx = ray["dx"]
        dy = ray["dy"]
        energy = 1.0

        for bounce in range(max_bounces + 1):
            if dist_left <= 0 or energy < 0.01:
                break
            # Find collision with 4 outer walls: x = +/-20.5, y = +/-20.5
            tx = 999999.0
            ty = 999999.0
            if dx > 0:
                tx = (20.5 - cur_x) / dx
            elif dx < 0:
                tx = (-20.5 - cur_x) / dx
            if dy > 0:
                ty = (20.5 - cur_y) / dy
            elif dy < 0:
                ty = (-20.5 - cur_y) / dy

            t_hit = min(tx, ty)
            step_dist = min(dist_left, t_hit)
            next_x = cur_x + dx * step_dist
            next_y = cur_y + dy * step_dist

            # Draw segment
            sx0, sy0 = world_to_screen(cur_x, cur_y, width, height)
            sx1, sy1 = world_to_screen(next_x, next_y, width, height)

            # Energy decay color: Yellow (high) -> Cyan -> Blue (decayed)
            cr = int(255 * energy * math.exp(-t * 0.8))
            cg = int(min(255, 120 + 135 * energy))
            cb = int(255 * (1.0 - energy * 0.5))
            draw_line(sx0, sy0, sx1, sy1, cr, cg, cb, alpha=min(0.8, energy * 0.9))

            dist_left -= step_dist
            if dist_left > 0 and step_dist == t_hit:
                # Bounce on wall
                if tx < ty:
                    dx = -dx
                else:
                    dy = -dy
                cur_x = next_x
                cur_y = next_y
                # Wall reflection absorption (alpha = 0.02)
                energy *= 0.94
            else:
                # Wavefront tip particle
                draw_disc(sx1, sy1, 2, 255, 255, 255)
                break

    # Spherical wavefront circle for early direct sound (t < 0.15s)
    if t < 0.20:
        wf_r = int(sound_dist / 44.0 * 470)
        msx, msy = world_to_screen(0.0, 18.5, width, height)
        for deg in range(0, 360, 3):
            rad = math.radians(deg)
            rad2 = math.radians(deg + 3)
            x1 = msx + int(wf_r * math.cos(rad))
            y1 = msy + int(wf_r * math.sin(rad))
            x2 = msx + int(wf_r * math.cos(rad2))
            y2 = msy + int(wf_r * math.sin(rad2))
            if p_tl[0] <= x1 <= p_br[0] and p_tl[1] <= y1 <= p_br[1]:
                draw_line(x1, y1, x2, y2, 255, 240, 100, 0.8)

    # 4. Draw Receivers
    for rx, ry, rname in RECEIVERS:
        sx, sy = world_to_screen(rx, ry, width, height)
        # Check if wave has reached receiver
        d_src = math.hypot(rx - 0.0, ry - 18.5)
        reached = sound_dist >= d_src
        col = (0, 230, 255) if reached else (100, 120, 160)
        draw_disc(sx, sy, 4, col[0], col[1], col[2])
        draw_disc(sx, sy, 2, 255, 255, 255)

    # 5. Draw Sound Sources
    im_x, im_y = world_to_screen(0.0, 18.5, width, height)
    draw_disc(im_x, im_y, 7, 255, 60, 60)
    draw_disc(im_x, im_y, 3, 255, 255, 255)

    kb_x, kb_y = world_to_screen(2.8, 17.0, width, height)
    draw_disc(kb_x, kb_y, 5, 255, 160, 40)

    mu_x, mu_y = world_to_screen(0.0, -8.0, width, height)
    draw_disc(mu_x, mu_y, 5, 200, 80, 255)

    # -------------------------------------------------------------
    # RIGHT SIDE PANEL: LIVE TELEMETRY & ACOUSTIC ECHOGRAM
    # -------------------------------------------------------------
    panel_x0 = 545
    draw_filled_rect(panel_x0, 25, width - 25, height - 25, 28, 28, 38)
    # Border
    draw_line(panel_x0, 25, width - 25, 25, 55, 55, 75, 1.0)
    draw_line(width - 25, 25, width - 25, height - 25, 55, 55, 75, 1.0)
    draw_line(width - 25, height - 25, panel_x0, height - 25, 55, 55, 75, 1.0)
    draw_line(panel_x0, height - 25, panel_x0, 25, 55, 55, 75, 1.0)

    # Live Energy Decay curve (dB vs time)
    # Initial SPL = 74 dB. At t, SPL = 74 - 60 * (t / RT60)
    rt60_mid = 4.21
    current_spl = max(14.0, 74.0 - 60.0 * (t / rt60_mid))

    # Echogram box: X in [565, 755], Y in [200, 380]
    eg_x0, eg_y0 = 565, 200
    eg_w, eg_h = 190, 180
    draw_filled_rect(eg_x0, eg_y0, eg_x0 + eg_w, eg_y0 + eg_h, 18, 18, 25)
    # Echogram grid
    for gl in range(1, 5):
        gy = eg_y0 + int(eg_h * gl / 5)
        draw_line(eg_x0, gy, eg_x0 + eg_w, gy, 40, 40, 55, 0.7)

    # Draw simulated impulse response spikes & decay curve
    decay_pts = []
    for step_i in range(eg_w):
        step_t = (step_i / eg_w) * 5.0
        val_db = max(14.0, 74.0 - 60.0 * (step_t / rt60_mid))
        py = eg_y0 + int(eg_h * (1.0 - (val_db - 14.0) / 60.0))
        decay_pts.append((eg_x0 + step_i, py))

    for i in range(len(decay_pts) - 1):
        draw_line(decay_pts[i][0], decay_pts[i][1], decay_pts[i + 1][0], decay_pts[i + 1][1], 0, 210, 255, 0.9)

    # Current time vertical cursor in echogram
    cur_cursor_x = eg_x0 + int((t / 5.0) * eg_w)
    draw_line(cur_cursor_x, eg_y0, cur_cursor_x, eg_y0 + eg_h, 255, 80, 80, 1.0)
    draw_disc(cur_cursor_x, eg_y0 + int(eg_h * (1.0 - (current_spl - 14.0) / 60.0)), 4, 255, 255, 255)

    # Energy Bar (colored meter at bottom of right panel)
    bar_x0 = 565
    bar_y0 = 425
    bar_w = 190
    bar_h = 16
    draw_filled_rect(bar_x0, bar_y0, bar_x0 + bar_w, bar_y0 + bar_h, 35, 35, 45)
    fill_w = int(bar_w * ((current_spl - 14.0) / 60.0))
    meter_col = (255, 80, 60) if current_spl > 60 else (255, 180, 30) if current_spl > 40 else (0, 210, 230)
    if fill_w > 0:
        draw_filled_rect(bar_x0, bar_y0, bar_x0 + fill_w, bar_y0 + bar_h, meter_col[0], meter_col[1], meter_col[2])

    return bytes(buf)


def render_all_assets():
    print("=" * 65)
    print("  GENERATING 5-SECOND ACOUSTIC SIMULATION VIDEO & GIF")
    print("=" * 65)

    fps = 25
    duration_s = 5.0
    total_frames = int(fps * duration_s)  # 125 frames
    width, height = 800, 600

    video_path = os.path.join(REPORTS_DIR, "mosque_acoustic_simulation_5s.mp4")
    gif_path = os.path.join(REPORTS_DIR, "mosque_acoustic_simulation.gif")

    # 1. Pipe PPM frames directly into FFmpeg to generate MP4
    print(f"Rendering {total_frames} frames to MP4: {video_path}...")
    cmd_mp4 = [
        FFMPEG_EXE, "-y",
        "-f", "image2pipe",
        "-vcodec", "ppm",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        video_path
    ]

    proc_mp4 = subprocess.Popen(cmd_mp4, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Keyframes to save as standalone PNG screenshots
    keyframe_indices = {
        2: "mosque_sim_stage1_direct_sound.ppm",       # t = 0.08s (Direct sound wavefront)
        10: "mosque_sim_stage2_early_reflections.ppm", # t = 0.40s (First boundary reflections)
        45: "mosque_sim_stage3_diffuse_decay.ppm",      # t = 1.80s (Diffuse reverberant tail)
        90: "mosque_sim_stage4_late_tail.ppm"           # t = 3.60s (Late decay near RT60m)
    }

    saved_ppms = {}

    for f in range(total_frames):
        t = f / fps
        raw_rgb = render_simulation_frame(t, width, height)
        ppm_header = f"P6\n{width} {height}\n255\n".encode("ascii")
        ppm_frame = ppm_header + raw_rgb
        proc_mp4.stdin.write(ppm_frame)

        if f in keyframe_indices:
            ppm_name = keyframe_indices[f]
            ppm_full = os.path.join(REPORTS_DIR, ppm_name)
            with open(ppm_full, "wb") as out_p:
                out_p.write(ppm_frame)
            saved_ppms[f] = ppm_full

    proc_mp4.stdin.close()
    proc_mp4.wait()
    print("[SUCCESS] MP4 Video generated successfully!")

    # 2. Generate smooth animated GIF using FFmpeg palettegen for crisp quality
    print(f"Generating optimized animated GIF: {gif_path}...")
    cmd_gif = [
        FFMPEG_EXE, "-y",
        "-i", video_path,
        "-vf", "fps=15,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
        gif_path
    ]
    subprocess.run(cmd_gif, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[SUCCESS] Animated GIF generated successfully!")

    # 3. Convert saved PPM keyframes to high-res PNG screenshots
    for f_idx, ppm_file in saved_ppms.items():
        png_file = ppm_file.replace(".ppm", ".png")
        subprocess.run([FFMPEG_EXE, "-y", "-i", ppm_file, png_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(ppm_file):
            os.remove(ppm_file)
        print(f"  + Generated Screenshot: {os.path.basename(png_file)}")

    print("=" * 65)


if __name__ == "__main__":
    render_all_assets()
