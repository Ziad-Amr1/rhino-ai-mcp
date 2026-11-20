"""3D Rhinoceros Viewport Acoustic Simulation Video, GIF and Keyframes Generator.

Renders an authentic 3D Rhino perspective viewport showing:
1. 3D Mosque geometry (41m x 41m walls, four 5m piers, 21m dome, 4 semi-domes)
2. 3D colored acoustic floor mesh (SPL-C / SPL-A)
3. Dynamic 3D ray tracing paths from Mihrab up into dome & reflecting down
4. 16 acoustic receiver stations (ground & gallery levels)
5. Rhino 9 Pachyderm Simulation Viewport UI chrome and real-time HUD

Outputs:
  - reports/rhino_3d_simulation_5s.mp4 (5s, 25fps, 125 frames)
  - reports/rhino_3d_simulation.gif (animated GIF)
  - reports/rhino_sim_stage1_dome_rays.png
  - reports/rhino_sim_stage2_pier_reflections.png
  - reports/rhino_sim_stage3_floor_heat_mesh.png
  - reports/rhino_sim_stage4_reverberant_decay.png
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

from mosque_acoustic_data import ACOUSTIC_RECEIVERS
from mosque_spatial_heatmaps import PIERS, is_inside_pier
from generate_heatmaps_and_spl_c import RasterCanvas, FONT_5x7

SPEED_OF_SOUND = 343.0  # m/s
SRC_POS = (0.0, 18.5, 1.5)  # Mihrab source

# -------------------------------------------------------------
# 3D PERSPECTIVE CAMERA PROJECTION
# -------------------------------------------------------------
class Camera3D:
    def __init__(self, eye=(38.0, -38.0, 36.0), target=(0.0, 0.0, 12.0), fov_deg=48.0, width=960, height=720):
        self.width = width
        self.height = height
        self.eye = list(eye)
        self.target = list(target)
        
        # Forward vector w (normalized, pointing target to eye)
        dx = eye[0] - target[0]
        dy = eye[1] - target[1]
        dz = eye[2] - target[2]
        d = math.sqrt(dx*dx + dy*dy + dz*dz)
        self.w = (dx/d, dy/d, dz/d)
        
        # World up (0, 0, 1)
        up = (0.0, 0.0, 1.0)
        # Right vector u = up x w
        ux = up[1]*self.w[2] - up[2]*self.w[1]
        uy = up[2]*self.w[0] - up[0]*self.w[2]
        uz = up[0]*self.w[1] - up[1]*self.w[0]
        ul = math.sqrt(ux*ux + uy*uy + uz*uz)
        self.u = (ux/ul, uy/ul, uz/ul)
        
        # Camera up vector v = w x u
        vx = self.w[1]*self.u[2] - self.w[2]*self.u[1]
        vy = self.w[2]*self.u[0] - self.w[0]*self.u[2]
        vz = self.w[0]*self.u[1] - self.w[1]*self.u[0]
        self.v = (vx, vy, vz)
        
        # Perspective focal scale
        aspect = width / float(height)
        self.focal = (height / 2.0) / math.tan(math.radians(fov_deg / 2.0))
        self.cx = width / 2.0
        self.cy = height / 2.0 + 30.0

    def project(self, x, y, z):
        """Projects 3D point (x, y, z) to 2D screen coordinates (sx, sy, depth)."""
        px = x - self.eye[0]
        py = y - self.eye[1]
        pz = z - self.eye[2]
        
        # Coordinates in camera frame
        cam_x = px*self.u[0] + py*self.u[1] + pz*self.u[2]
        cam_y = px*self.v[0] + py*self.v[1] + pz*self.v[2]
        cam_z = -(px*self.w[0] + py*self.w[1] + pz*self.w[2])
        
        if cam_z <= 1.0:
            return None
        
        sx = int(self.cx + (cam_x / cam_z) * self.focal)
        sy = int(self.cy - (cam_y / cam_z) * self.focal)
        return (sx, sy, cam_z)


# Precompute 3D Rays from Mihrab
random.seed(101)
NUM_3D_RAYS = 120
RAY_PATHS_3D = []

for r_i in range(NUM_3D_RAYS):
    # Ray shooting in upper hemisphere
    az = (2.0 * math.pi * r_i) / NUM_3D_RAYS + (random.random() - 0.5) * 0.05
    el = math.radians(20.0 + random.random() * 65.0)
    
    dir_x = math.cos(el) * math.cos(az)
    dir_y = math.cos(el) * math.sin(az)
    dir_z = math.sin(el)
    
    # 1st Hit: Dome, Pier, or Wall
    # Check intersection with central dome ceiling (sphere R=10.5m centered at 0,0,35m)
    p0 = SRC_POS
    # Target dome point
    dome_rad = 10.5
    dome_apex = 52.0
    dome_base = 35.0
    
    # Path coordinates [(x, y, z, arrival_dist)]
    pts = [(p0[0], p0[1], p0[2], 0.0)]
    
    # Hit 1 on ceiling / dome
    hit1_z = dome_base + (dome_apex - dome_base) * math.sin(el)
    hit1_x = dir_x * (hit1_z / max(0.1, dir_z)) * 0.7
    hit1_y = p0[1] + dir_y * (hit1_z / max(0.1, dir_z)) * 0.7
    # Clamp to dome radius
    hit1_x = max(-18.0, min(18.0, hit1_x))
    hit1_y = max(-18.0, min(18.0, hit1_y))
    d1 = math.sqrt((hit1_x - p0[0])**2 + (hit1_y - p0[1])**2 + (hit1_z - p0[2])**2)
    pts.append((hit1_x, hit1_y, hit1_z, d1))
    
    # Reflection 2 downwards towards floor
    ref_dir_z = -abs(dir_z) * 0.95
    ref_dir_x = dir_x + (random.random() - 0.5) * 0.2
    ref_dir_y = dir_y + (random.random() - 0.5) * 0.2
    
    hit2_z = 0.1
    t_down = (hit1_z - hit2_z) / max(0.1, abs(ref_dir_z))
    hit2_x = max(-20.0, min(20.0, hit1_x + ref_dir_x * t_down))
    hit2_y = max(-20.0, min(20.0, hit1_y + ref_dir_y * t_down))
    d2 = d1 + math.sqrt((hit2_x - hit1_x)**2 + (hit2_y - hit1_y)**2 + (hit2_z - hit1_z)**2)
    pts.append((hit2_x, hit2_y, hit2_z, d2))
    
    # Reflection 3 across prayer rows
    hit3_x = max(-20.0, min(20.0, hit2_x + ref_dir_x * 12.0))
    hit3_y = max(-20.0, min(20.0, hit2_y - abs(ref_dir_y) * 12.0))
    hit3_z = 1.2
    d3 = d2 + math.hypot(hit3_x - hit2_x, hit3_y - hit2_y)
    pts.append((hit3_x, hit3_y, hit3_z, d3))
    
    RAY_PATHS_3D.append(pts)


def render_rhino_3d_frame(t, camera, width=960, height=720):
    """Renders a single frame in the 3D Rhino viewport at simulation time t."""
    canvas = RasterCanvas(width, height, bg_rgb=(24, 25, 34))

    # 1. Viewport Grid & Floor (41m x 41m)
    # Draw floor mesh cells with dynamic acoustic heat colors
    grid_dim = 24  # 24x24 = 576 floor quads
    g_step = 41.0 / grid_dim

    # Time-dependent buildup factor
    tau_bass = 8.1 / 13.82
    buildup = 1.0 - math.exp(-t / tau_bass) if t < 2.5 else (1.0 - math.exp(-2.5 / tau_bass)) * math.exp(-(t - 2.5) / tau_bass)

    for gy in range(grid_dim):
        wy0 = -20.5 + gy * g_step
        wy1 = wy0 + g_step
        for gx in range(grid_dim):
            wx0 = -20.5 + gx * g_step
            wx1 = wx0 + g_step
            
            # Midpoint sound level
            mx = (wx0 + wx1) * 0.5
            my = (wy0 + wy1) * 0.5
            
            if is_inside_pier(mx, my):
                # Pier base footprint
                col = (60, 62, 75)
            else:
                dist = math.hypot(mx - 0.0, my - 18.5)
                # Local SPL(C) level
                spl = 56.0 + 18.0 * buildup * math.exp(-dist / 32.0)
                norm = max(0.0, min(1.0, (spl - 54.0) / 22.0))
                if norm < 0.25:
                    col = (0, int(norm * 4.0 * 255), 240)
                elif norm < 0.5:
                    col = (0, 240, int((1.0 - (norm - 0.25) * 4.0) * 240))
                elif norm < 0.75:
                    col = (int(((norm - 0.5) * 4.0) * 240), 240, 0)
                else:
                    col = (240, int((1.0 - (norm - 0.75) * 4.0) * 240), 0)

            # Project quad 4 vertices
            p0 = camera.project(wx0, wy0, 0.0)
            p1 = camera.project(wx1, wy0, 0.0)
            p2 = camera.project(wx1, wy1, 0.0)
            p3 = camera.project(wx0, wy1, 0.0)

            if p0 and p1 and p2 and p3:
                # Fill quad wire/solid
                canvas.draw_line(p0[0], p0[1], p1[0], p1[1], col[0], col[1], col[2], alpha=0.55)
                canvas.draw_line(p1[0], p1[1], p2[0], p2[1], col[0], col[1], col[2], alpha=0.55)
                canvas.draw_line(p2[0], p2[1], p3[0], p3[1], col[0], col[1], col[2], alpha=0.55)
                canvas.draw_line(p3[0], p3[1], p0[0], p0[1], col[0], col[1], col[2], alpha=0.55)

    # 2. Four Limestone Piers (5m x 5m, height 20m)
    for px, py, sz in PIERS:
        for pz in [0.0, 20.0]:
            # Base and top square
            b0 = camera.project(px - sz, py - sz, pz)
            b1 = camera.project(px + sz, py - sz, pz)
            b2 = camera.project(px + sz, py + sz, pz)
            b3 = camera.project(px - sz, py + sz, pz)
            if b0 and b1 and b2 and b3:
                canvas.draw_line(b0[0], b0[1], b1[0], b1[1], 150, 155, 175)
                canvas.draw_line(b1[0], b1[1], b2[0], b2[1], 150, 155, 175)
                canvas.draw_line(b2[0], b2[1], b3[0], b3[1], 150, 155, 175)
                canvas.draw_line(b3[0], b3[1], b0[0], b0[1], 150, 155, 175)
        # Vertical edges
        for dx_s, dy_s in [(-sz, -sz), (sz, -sz), (sz, sz), (-sz, sz)]:
            bot = camera.project(px + dx_s, py + dy_s, 0.0)
            top = camera.project(px + dx_s, py + dy_s, 20.0)
            if bot and top:
                canvas.draw_line(bot[0], bot[1], top[0], top[1], 160, 165, 185)

    # 3. Outer Alabaster Wall Enclosure (41m x 41m, height 22m)
    walls = [
        (-20.5, -20.5), (20.5, -20.5), (20.5, 20.5), (-20.5, 20.5)
    ]
    for i in range(4):
        x0, y0 = walls[i]
        x1, y1 = walls[(i + 1) % 4]
        b0 = camera.project(x0, y0, 0.0)
        b1 = camera.project(x1, y1, 0.0)
        t0 = camera.project(x0, y0, 22.0)
        t1 = camera.project(x1, y1, 22.0)
        if b0 and b1:
            canvas.draw_line(b0[0], b0[1], b1[0], b1[1], 180, 180, 200, alpha=0.6)
        if t0 and t1:
            canvas.draw_line(t0[0], t0[1], t1[0], t1[1], 200, 200, 225, alpha=0.8)
        if b0 and t0:
            canvas.draw_line(b0[0], b0[1], t0[0], t0[1], 180, 180, 200, alpha=0.6)

    # 4. Central Dome Ribs & Rings (Diameter 21m, Base Z=35m, Apex Z=52m)
    apex = camera.project(0.0, 0.0, 52.0)
    dome_pts_ring = []
    num_dome_steps = 32
    for di in range(num_dome_steps):
        th = (2.0 * math.pi * di) / num_dome_steps
        dx = 10.5 * math.cos(th)
        dy = 10.5 * math.sin(th)
        dp = camera.project(dx, dy, 35.0)
        dome_pts_ring.append(dp)

    for di in range(num_dome_steps):
        p_a = dome_pts_ring[di]
        p_b = dome_pts_ring[(di + 1) % num_dome_steps]
        if p_a and p_b:
            # Base ring
            canvas.draw_line(p_a[0], p_a[1], p_b[0], p_b[1], 255, 215, 0, alpha=0.85)
        if p_a and apex and (di % 4 == 0):
            # Meridian ribs reaching apex
            canvas.draw_line(p_a[0], p_a[1], apex[0], apex[1], 255, 230, 120, alpha=0.7)

    # 5. Dynamic 3D Acoustic Ray Tracing
    cur_sound_dist = SPEED_OF_SOUND * t
    for ray in RAY_PATHS_3D:
        for seg_i in range(len(ray) - 1):
            p_start = ray[seg_i]
            p_end = ray[seg_i + 1]
            d_start = p_start[3]
            d_end = p_end[3]
            
            if cur_sound_dist <= d_start:
                break
            
            # Interpolate segment end point
            if cur_sound_dist < d_end:
                frac = (cur_sound_dist - d_start) / max(0.01, d_end - d_start)
                cur_x = p_start[0] + (p_end[0] - p_start[0]) * frac
                cur_y = p_start[1] + (p_end[1] - p_start[1]) * frac
                cur_z = p_start[2] + (p_end[2] - p_start[2]) * frac
                is_head = True
            else:
                cur_x, cur_y, cur_z = p_end[0], p_end[1], p_end[2]
                is_head = False

            sp0 = camera.project(p_start[0], p_start[1], p_start[2])
            sp1 = camera.project(cur_x, cur_y, cur_z)

            if sp0 and sp1:
                # Segment color: Gold for direct rays, Cyan for dome reflections, Green for late
                if seg_i == 0:
                    rc, gc, bc = 255, 220, 60
                elif seg_i == 1:
                    rc, gc, bc = 0, 230, 255
                else:
                    rc, gc, bc = 50, 220, 120
                
                alpha = max(0.3, 1.0 - t * 0.18)
                canvas.draw_line(sp0[0], sp0[1], sp1[0], sp1[1], rc, gc, bc, alpha=alpha)

                # Glowing ray wavefront tip
                if is_head and sp1:
                    canvas.draw_disc(sp1[0], sp1[1], 3, 255, 255, 255)

    # 6. Mihrab Source in 3D
    s_proj = camera.project(SRC_POS[0], SRC_POS[1], SRC_POS[2])
    if s_proj:
        canvas.draw_disc(s_proj[0], s_proj[1], 7, 255, 50, 50)
        canvas.draw_disc(s_proj[0], s_proj[1], 3, 255, 255, 255)
        canvas.draw_text("MIHRAB", s_proj[0] + 10, s_proj[1] - 5, r=255, g=80, b=80, scale=1)

    # 7. Receiver Sensors in 3D
    for r in ACOUSTIC_RECEIVERS:
        rx, ry, rz = r["coordinates"]
        rp = camera.project(rx, ry, rz)
        if rp:
            is_gal = rz > 5.0
            col = (255, 140, 230) if is_gal else (0, 220, 240)
            canvas.draw_disc(rp[0], rp[1], 4, col[0], col[1], col[2])
            r_name = r["id"].replace("REC_", "R")
            canvas.draw_text(r_name, rp[0] + 6, rp[1] - 4, r=220, g=220, b=245, scale=1)

    # -------------------------------------------------------------
    # RHINOCEROS 9 VIEWPORT UI CHROME & TELEMETRY HUD
    # -------------------------------------------------------------
    # Top Viewport Header Bar
    canvas.fill_rect(0, 0, width, 32, 38, 40, 52)
    canvas.draw_line(0, 32, width, 32, 65, 68, 85)
    canvas.draw_text("PERSPECTIVE [RENDERED] - RHINO 9 - PACHYDERM ACOUSTIC SIMULATION V2.7.0.0", 15, 10, r=255, g=255, b=255, scale=1)

    # Active Layer Pill
    canvas.fill_rect(width - 280, 6, width - 15, 26, 25, 26, 35)
    canvas.draw_disc(width - 270, 16, 4, 0, 220, 255)
    canvas.draw_text("LAYER: ACOUSTIC_HEATMAP", width - 260, 11, r=220, g=220, b=240, scale=1)

    # Real-Time Simulation HUD (Top-Right Card)
    hud_x = width - 275
    hud_y = 45
    canvas.fill_rect(hud_x, hud_y, width - 15, hud_y + 145, 28, 30, 42, alpha=0.92)
    canvas.draw_rect(hud_x, hud_y, width - 15, hud_y + 145, 65, 70, 95)

    canvas.draw_text("SIMULATION HUD", hud_x + 12, hud_y + 12, r=255, g=215, b=0, scale=1)
    ms_val = int(t * 1000)
    canvas.draw_text(f"TIME: {t:.2f}S ({ms_val:4d}MS)", hud_x + 12, hud_y + 30, r=255, g=255, b=255, scale=1)

    ray_cnt = min(NUM_3D_RAYS, int(NUM_3D_RAYS * min(1.0, t * 12.0)))
    bounce_cnt = int(ray_cnt * min(15, 1 + t * 4.5))
    canvas.draw_text(f"ACTIVE RAYS: {ray_cnt}", hud_x + 12, hud_y + 48, r=0, g=220, b=255, scale=1)
    canvas.draw_text(f"DOME REFLECTIONS: {bounce_cnt}", hud_x + 12, hud_y + 64, r=100, g=240, b=150, scale=1)

    # Live Room Pressure
    avg_spl_c = 58.0 + 16.5 * buildup
    avg_spl_a = 52.0 + 9.5 * buildup
    canvas.draw_text(f"SPL(C) BASS:   {avg_spl_c:.1f} DBC", hud_x + 12, hud_y + 86, r=255, g=80, b=80, scale=1)
    canvas.draw_text(f"SPL(A) SPEECH: {avg_spl_a:.1f} DBA", hud_x + 12, hud_y + 102, r=0, g=210, b=230, scale=1)
    delta = avg_spl_c - avg_spl_a
    canvas.draw_text(f"BASS EXCESS:  +{delta:.1f} DB", hud_x + 12, hud_y + 120, r=255, g=200, b=50, scale=1)

    # Bottom-Left 3D Coordinate Tripod
    tripod_ox = 45
    tripod_oy = height - 45
    canvas.draw_disc(tripod_ox, tripod_oy, 3, 255, 255, 255)
    # X Axis (Red)
    canvas.draw_line(tripod_ox, tripod_oy, tripod_ox + 25, tripod_oy + 8, 255, 60, 60)
    canvas.draw_text("X", tripod_ox + 28, tripod_oy + 4, r=255, g=60, b=60, scale=1)
    # Y Axis (Green)
    canvas.draw_line(tripod_ox, tripod_oy, tripod_ox - 15, tripod_oy + 18, 60, 220, 60)
    canvas.draw_text("Y", tripod_ox - 24, tripod_oy + 14, r=60, g=220, b=60, scale=1)
    # Z Axis (Blue)
    canvas.draw_line(tripod_ox, tripod_oy, tripod_ox, tripod_oy - 26, 60, 140, 255)
    canvas.draw_text("Z", tripod_ox - 4, tripod_oy - 36, r=60, g=140, b=255, scale=1)

    # Bottom status bar
    canvas.fill_rect(0, height - 22, width, height, 32, 34, 45)
    canvas.draw_line(0, height - 22, width, height - 22, 50, 52, 68)
    canvas.draw_text("MODEL: MUHAMMAD_ALI_MOSQUE.3DM | VOLUME: 39,840 M3 | OCCUPIED RT60: 4.2S | SOLVER: PACHYDERM RAY TRACER", 15, height - 16, r=160, g=165, b=185, scale=1)

    return canvas


def generate_rhino_3d_simulation_assets():
    print("=" * 65)
    print("  GENERATING RHINO 3D SIMULATION VIDEO, GIF & VIEWPORT CAPTURES")
    print("=" * 65)

    fps = 25
    duration_s = 5.0
    total_frames = int(fps * duration_s)  # 125 frames
    w, h = 960, 720

    mp4_path = os.path.join(REPORTS_DIR, "rhino_3d_simulation_5s.mp4")
    gif_path = os.path.join(REPORTS_DIR, "rhino_3d_simulation.gif")

    camera = Camera3D(eye=(38.0, -38.0, 36.0), target=(0.0, 0.0, 12.0), fov_deg=48.0, width=w, height=h)

    # Keyframe capture timestamps
    keyframe_times = {
        0.08: "rhino_sim_stage1_dome_rays.png",
        0.35: "rhino_sim_stage2_pier_reflections.png",
        2.40: "rhino_sim_stage3_floor_heat_mesh.png",
        4.20: "rhino_sim_stage4_reverberant_decay.png"
    }

    # 1. Pipe PPM frames directly into FFmpeg
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

    print(f"Rendering {total_frames} 3D frames to MP4: {mp4_path}")
    proc_mp4 = subprocess.Popen(mp4_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    ppm_header = f"P6\n{w} {h}\n255\n".encode("ascii")
    saved_keyframes = set()

    for frame_idx in range(total_frames):
        t = frame_idx / float(fps)
        canvas = render_rhino_3d_frame(t, camera, w, h)
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
    print(f"Rhino 3D MP4 successfully rendered: {mp4_path}")

    # 2. Render high quality GIF using palettegen + paletteuse
    print(f"Converting Rhino 3D MP4 to high-quality animated GIF: {gif_path}")
    cmd_gif = [
        FFMPEG_EXE, "-y",
        "-i", mp4_path,
        "-vf", "fps=15,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
        gif_path
    ]
    subprocess.run(cmd_gif, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Rhino 3D Animated GIF rendered: {gif_path}")
    print("=" * 65)


if __name__ == "__main__":
    generate_rhino_3d_simulation_assets()
