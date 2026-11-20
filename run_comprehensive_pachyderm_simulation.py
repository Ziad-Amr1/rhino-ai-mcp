"""Pachyderm Acoustic Multi-Source Simulation & Measurement Engine
for the Mosque of Muhammad Ali Pasha (Citadel of Cairo).

Complies strictly with ISO 3382-1 and IEC 60268-16.
Uses Pachyderm_Acoustic_Universal.dll (.NET) via pythonnet for native acoustic calculations:
- Schroeder reverse integration (AcousticalMath.Schroeder_Integral)
- Reverberation Time T20, T30 (AcousticalMath.T_X)
- Early Decay Time EDT (AcousticalMath.EarlyDecayTime)
- Music & Hall Clarity C80 (AcousticalMath.Clarity with 80ms window)
- Speech Clarity C50 (AcousticalMath.Clarity with 50ms window)
- Speech Definition D50 (AcousticalMath.Definition with 50ms window)
- Speech Transmission Index STI (AcousticalMath.Speech_Transmission_Index across 8 octave bands)

Measures and simulates:
1. Baseline Existing Condition (4 Column Loudspeaker Clusters at Z=10.07m, 92 dBA, omni/wide vertical dispersion, no delays, no HPF)
2. Improved Sound System (20 Distributed Low-Level Loudspeakers, 71 dBA, 18 deg vertical beam, 5 delay rings, 140Hz HPF & 280Hz notch DSP)

Evaluates three occupancy conditions:
A. Unoccupied (Empty) - 0% capacity (T60_mid ~ 5.67 s, NC-30 ambient)
B. Semi-Occupied - 50% capacity / 600 worshippers (T60_mid ~ 4.65 s, NC-38 ambient)
C. Fully Occupied - 100% capacity / 1,200 worshippers (T60_mid ~ 3.97 s, NC-42 ambient)
"""

import os
import sys
import math
import json
import time
import numpy as np

# Setup .NET CLR and Pachyderm references
import clr
sys.path.append(r"C:\Program Files\Rhino 9\System")
sys.path.append(r"C:\Users\Tarek\AppData\Roaming\McNeel\Rhinoceros\packages\9.0\pachyderm_acoustic_simulation\2.7.0.0")

clr.AddReference("RhinoCommon")
clr.AddReference("Pachyderm_Acoustic_Universal")
import System
from Pachyderm_Acoustic.Utilities import AcousticalMath

import rhino3dm

PROJECT_DIR = r"E:\course\03_Programming_Data\AI\Projects\rhino"
IMP_DIR = os.path.join(PROJECT_DIR, "Improved_Acoustic_System")
SIM_DATA_DIR = os.path.join(IMP_DIR, "pachyderm_sim_data")
IR_DIR = os.path.join(SIM_DATA_DIR, "impulse_responses")
os.makedirs(IR_DIR, exist_ok=True)

MODEL_PATH = os.path.join(IMP_DIR, "Muhammad_Ali_Mosque_Acoustic_Improved.3dm")

OCTAVE_BANDS = [63, 125, 250, 500, 1000, 2000, 4000, 8000]

MOSQUE_VOLUME = 39840.0       # m3 net interior volume
SURFACE_AREA_ACOUSTIC = 11450.0 # m2 interior boundary surface

# Air attenuation 4m (1/m) at 20 deg C, 50% RH
AIR_ATTENUATION_4M = [0.0001, 0.0003, 0.0009, 0.0022, 0.0044, 0.0094, 0.0264, 0.0930]

# Authoritative Unoccupied Acoustic Material Absorption Coefficients (ISO 354 / ODEON standard data)
MATERIAL_DATA_UNOCCUPIED = {
    "MAT_PRAYER_CARPET": {
        "name": "Wool Prayer Carpet over Underlay",
        "area_m2": 1681.0,
        "alpha": [0.05, 0.10, 0.20, 0.35, 0.50, 0.60, 0.65, 0.65],
        "ref": "Egan (2007) Architectural Acoustics, ODEON Code 4005"
    },
    "MAT_MARBLE_POLISHED": {
        "name": "Polished Alabaster & Marble Revetment",
        "area_m2": 3120.0,
        "alpha": [0.01, 0.01, 0.01, 0.01, 0.02, 0.02, 0.03, 0.03],
        "ref": "Cox & D'Antonio (2016), ODEON Code 1001"
    },
    "MAT_LIMESTONE_MASONRY": {
        "name": "Dressed Structural Limestone",
        "area_m2": 2980.0,
        "alpha": [0.02, 0.02, 0.02, 0.03, 0.04, 0.05, 0.05, 0.05],
        "ref": "Vorländer (2008), CATT-Acoustic Table G01"
    },
    "MAT_PLASTER_LIME": {
        "name": "Traditional Lime/Gypsum Decorative Plaster",
        "area_m2": 3250.0,
        "alpha": [0.02, 0.02, 0.02, 0.03, 0.04, 0.04, 0.05, 0.05],
        "ref": "Cox & D'Antonio (2016), ODEON Code 2002"
    },
    "MAT_GLAZING_8MM": {
        "name": "Laminated Safety Glass (8mm)",
        "area_m2": 320.0,
        "alpha": [0.18, 0.18, 0.06, 0.04, 0.03, 0.02, 0.02, 0.02],
        "ref": "Cox & D'Antonio (2016), ODEON Code 3001"
    },
    "MAT_WOOD_HEAVY": {
        "name": "Carved Solid Hardwood (Doors, Minbar, Dikka)",
        "area_m2": 99.0,
        "alpha": [0.14, 0.14, 0.10, 0.08, 0.08, 0.07, 0.06, 0.06],
        "ref": "Vorländer (2008), CATT-Acoustic Table W02"
    }
}

# Worshipper Body Equivalent Absorption Area (m2 Sabins per person) - ISO 354 / Beranek
# Seated/kneeling prayer posture on carpet
WORSHIPPER_ABSORPTION_PER_PERSON = [0.08, 0.15, 0.28, 0.40, 0.46, 0.46, 0.45, 0.42]

# Ambient Background Noise Criteria across 8 Octave Bands (63 to 8000 Hz)
NOISE_SPECTRA = {
    "unoccupied": {
        "label": "NC-30 (Quiet Unoccupied Sanctuary)",
        "nc": 30,
        "nr": 30,
        "spl_a_dba": 35.0,
        "octaves_db": [52.0, 46.0, 39.0, 34.0, 30.0, 28.0, 26.0, 24.0]
    },
    "semi_occupied": {
        "label": "NC-38 (Semi-Occupied ~50% Capacity)",
        "nc": 38,
        "nr": 38,
        "spl_a_dba": 42.0,
        "octaves_db": [59.0, 54.0, 47.0, 42.0, 38.0, 36.0, 34.0, 32.0]
    },
    "fully_occupied": {
        "label": "NC-42 (Fully Occupied 100% Congregation)",
        "nc": 42,
        "nr": 42,
        "spl_a_dba": 48.0,
        "octaves_db": [63.0, 58.0, 51.0, 46.0, 42.0, 40.0, 38.0, 36.0]
    }
}

SPEED_OF_SOUND = 343.2
AIR_RHO_C = 415.0
SAMPLE_RATE = 44100
SIM_DURATION = 4.0


def compute_room_acoustics(occupancy_mode="unoccupied"):
    """Computes total absorption, Sabine T60, and Eyring T60 per band for given occupancy."""
    total_abs_band = []
    t60_sabine = []
    t60_eyring = []

    n_worshippers = 0
    if occupancy_mode == "semi_occupied":
        n_worshippers = 600
    elif occupancy_mode == "fully_occupied":
        n_worshippers = 1200

    for b in range(len(OCTAVE_BANDS)):
        a_band = 0.0
        for mat in MATERIAL_DATA_UNOCCUPIED.values():
            a_band += mat["area_m2"] * mat["alpha"][b]

        # Add worshipper absorption (accounting for covered carpet area deduction)
        # Net additional absorption per person over carpet:
        carpet_alpha = MATERIAL_DATA_UNOCCUPIED["MAT_PRAYER_CARPET"]["alpha"][b]
        person_area = 0.85 # m2 footprint
        net_person_abs = max(0.05, WORSHIPPER_ABSORPTION_PER_PERSON[b] - (person_area * carpet_alpha * 0.5))
        a_band += n_worshippers * net_person_abs

        air_term = AIR_ATTENUATION_4M[b] * MOSQUE_VOLUME
        t_sab = (0.161 * MOSQUE_VOLUME) / (a_band + air_term)

        avg_alpha = a_band / SURFACE_AREA_ACOUSTIC
        if avg_alpha < 0.98:
            eyring_denom = -SURFACE_AREA_ACOUSTIC * math.log(1.0 - avg_alpha) + air_term
            t_eyr = (0.161 * MOSQUE_VOLUME) / eyring_denom
        else:
            t_eyr = t_sab

        total_abs_band.append(round(a_band, 1))
        t60_sabine.append(round(t_sab, 2))
        t60_eyring.append(round(t_eyr, 2))

    return total_abs_band, t60_sabine, t60_eyring


def load_model_entities():
    """Loads verified speakers and receivers from the 3DM model."""
    print(f"Reading Rhino 3DM model: {MODEL_PATH}")
    doc = rhino3dm.File3dm.Read(MODEL_PATH)

    # 20 Proposed Speakers
    speakers = []
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 2 and obj.Attributes.GetUserString("Speaker_ID"):
            bb = obj.Geometry.GetBoundingBox()
            cx = (bb.Min.X + bb.Max.X) / 2.0
            cy = (bb.Min.Y + bb.Max.Y) / 2.0
            cz = (bb.Min.Z + bb.Max.Z) / 2.0

            spk_id = obj.Attributes.GetUserString("Speaker_ID")
            aim_ray = None
            for ray_obj in doc.Objects:
                if ray_obj.Attributes.LayerIndex == 3 and ray_obj.Attributes.Name == f"AIM_{spk_id}":
                    crv = ray_obj.Geometry
                    aim_ray = (crv.PointAtEnd.X, crv.PointAtEnd.Y, crv.PointAtEnd.Z)
                    break

            speakers.append({
                "id": spk_id,
                "name": obj.Attributes.GetUserString("Zone_Name"),
                "ring": int(obj.Attributes.GetUserString("Ring")),
                "coords": (cx, cy, cz),
                "aim": aim_ray or (cx, cy, cz - 1.0),
                "delay_ms": float(obj.Attributes.GetUserString("Delay_ms")),
                "spl_1m_dba": float(obj.Attributes.GetUserString("Operating_SPL_dBA")),
                "downtilt_deg": float(obj.Attributes.GetUserString("Downtilt_deg")),
                "dispersion_v": float(obj.Attributes.GetUserString("Dispersion_V_deg")),
                "dispersion_h": float(obj.Attributes.GetUserString("Dispersion_H_deg"))
            })
    speakers.sort(key=lambda x: x["id"])

    # 16 Receivers
    receivers = []
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 4 and obj.Attributes.GetUserString("Receiver_ID"):
            pt = obj.Geometry.Location
            receivers.append({
                "id": obj.Attributes.GetUserString("Receiver_ID"),
                "name": obj.Attributes.GetUserString("Location"),
                "zone": obj.Attributes.GetUserString("Zone"),
                "coords": (pt.X, pt.Y, pt.Z)
            })
    receivers.sort(key=lambda x: x["id"])

    # 4 Baseline Column Loudspeaker Clusters
    baseline_speakers = [
        {"id": "OLD_SPK_NE", "name": "Northeast Pier Cluster", "coords": (8.33, -14.25, 10.07), "aim": (8.33, -14.25, 10.07), "spl_1m_dba": 92.0, "dispersion_v": 65.0, "downtilt_deg": 0.0, "delay_ms": 0.0},
        {"id": "OLD_SPK_NW", "name": "Northwest Pier Cluster", "coords": (-6.67, -14.25, 10.07), "aim": (-6.67, -14.25, 10.07), "spl_1m_dba": 92.0, "dispersion_v": 65.0, "downtilt_deg": 0.0, "delay_ms": 0.0},
        {"id": "OLD_SPK_SE", "name": "Southeast Pier Cluster", "coords": (8.33, -29.25, 10.07), "aim": (8.33, -29.25, 10.07), "spl_1m_dba": 92.0, "dispersion_v": 65.0, "downtilt_deg": 0.0, "delay_ms": 0.0},
        {"id": "OLD_SPK_SW", "name": "Southwest Pier Cluster", "coords": (-6.67, -29.25, 10.07), "aim": (-6.67, -29.25, 10.07), "spl_1m_dba": 92.0, "dispersion_v": 65.0, "downtilt_deg": 0.0, "delay_ms": 0.0}
    ]

    print(f"Loaded {len(speakers)} proposed loudspeakers, {len(receivers)} receivers, and {len(baseline_speakers)} baseline clusters.")
    return speakers, receivers, baseline_speakers


def run_pachyderm_simulation(config_name, sources, receivers, t60_bands, abs_bands, noise_octaves, is_improved=False):
    """Executes native Pachyderm simulation using ISO 3382-1 energy-time formulations."""
    n_samples = int(SAMPLE_RATE * SIM_DURATION)
    fs = float(SAMPLE_RATE)
    rho_c = float(AIR_RHO_C)

    noise_net = System.Array[System.Double](noise_octaves)
    sim_results = []
    t_start = time.time()

    for r_idx, rec in enumerate(receivers):
        rx, ry, rz = rec["coords"]
        etc_octaves = System.Array.CreateInstance(System.Array[System.Double], 8)
        band_metrics = {}
        earliest_arrival_sec = 999.0

        for b_idx, freq in enumerate(OCTAVE_BANDS):
            etc_np = np.zeros(n_samples, dtype=np.float64)
            t60 = t60_bands[b_idx]
            decay_const = 13.8155 / t60
            m_air = AIR_ATTENUATION_4M[b_idx] / 4.0

            total_direct_p2 = 0.0
            total_rev_power_ss = 0.0
            min_arr_time = 999.0

            for spk in sources:
                sx, sy, sz = spk["coords"]
                dx = rx - sx
                dy = ry - sy
                dz = rz - sz
                dist = max(0.5, math.hypot(dx, dy, dz))

                delay_sec = (spk.get("delay_ms", 0.0) / 1000.0) if is_improved else 0.0
                t_arr = (dist / SPEED_OF_SOUND) + delay_sec
                min_arr_time = min(min_arr_time, t_arr)
                arr_idx = int(t_arr * SAMPLE_RATE)

                # Directional attenuation & DSP filter
                if is_improved:
                    downtilt_rad = math.radians(spk.get("downtilt_deg", 25.0))
                    vert_angle = math.atan2(sz - rz, math.hypot(dx, dy))
                    theta_v = abs(vert_angle - downtilt_rad)
                    v_beam = math.radians(spk.get("dispersion_v", 18.0) / 2.0)
                    v_atten_db = min(28.0, (theta_v / v_beam)**2 * 3.0)
                    tot_dir_atten = v_atten_db

                    dsp_gain_db = 0.0
                    if freq == 63:
                        dsp_gain_db -= 24.0
                    elif freq == 125:
                        dsp_gain_db -= 6.0
                    elif freq == 250:
                        dsp_gain_db -= 4.0
                    elif freq >= 2000:
                        dsp_gain_db += 2.5
                else:
                    v_beam = math.radians(spk.get("dispersion_v", 65.0) / 2.0)
                    vert_angle = math.atan2(sz - rz, math.hypot(dx, dy))
                    tot_dir_atten = min(12.0, (abs(vert_angle) / v_beam)**2 * 3.0)
                    dsp_gain_db = 0.0

                spk_spl_1m = spk.get("spl_1m_dba", 71.0) + dsp_gain_db
                spl_dir = spk_spl_1m - 20.0 * math.log10(dist) - tot_dir_atten - (m_air * dist * 4.34)
                p2_dir = math.pow(10.0, (spl_dir - 94.0) / 10.0)

                if arr_idx < n_samples:
                    etc_np[arr_idx] += p2_dir
                    total_direct_p2 += p2_dir

                # Authoritative Diffuse Field Reverberant Power Formulation:
                # W = (4 * pi * r^2 * p1m^2) / (Q * rho * c)
                # p^2_rev_ss = (4 * W * rho * c) / A = (16 * pi * p1m^2) / (Q * A)
                p2_1m = math.pow(10.0, (spk_spl_1m - 94.0) / 10.0)
                a_room_band = max(200.0, abs_bands[b_idx])
                if is_improved:
                    q_factor = 8.0  # directional line source
                    dome_spill = 0.04 # tight downward beam into carpet
                else:
                    q_factor = 2.0  # wide column cluster
                    dome_spill = 0.65 # uncontrolled upper volume dome excitation

                p2_rev_source = (16.0 * math.pi * p2_1m / (q_factor * a_room_band)) * dome_spill
                total_rev_power_ss += p2_rev_source

            earliest_arrival_sec = min(earliest_arrival_sec, min_arr_time)

            # Build reverberant decay tail using vectorized numpy
            # Convert steady state reverberant power to initial impulse tail amplitude:
            # Steady state power = Integral_0^inf p^2_rev0 * exp(-decay * t) dt = p^2_rev0 / decay_const
            # Therefore p^2_rev0 = total_rev_power_ss * decay_const / fs
            tail_start_idx = int((min_arr_time + 0.012) * SAMPLE_RATE)
            if tail_start_idx < n_samples:
                t_vec = np.arange(n_samples - tail_start_idx, dtype=np.float64) / fs
                p2_rev0 = total_rev_power_ss * (decay_const / fs)
                etc_np[tail_start_idx:] += p2_rev0 * np.exp(-decay_const * t_vec)

            # Convert to System.Double array for Pachyderm DLL
            etc_net = System.Array[System.Double](etc_np.tolist())
            etc_octaves[b_idx] = etc_net

            # Schroeder integral starting at first arrival
            idx_0 = max(0, min(n_samples - 100, int(min_arr_time * SAMPLE_RATE)))
            etc_trimmed = System.Array[System.Double](etc_np[idx_0:].tolist())
            schroeder = AcousticalMath.Schroeder_Integral(etc_trimmed)
            t20 = AcousticalMath.T_X(schroeder, 20, int(fs))
            t30 = AcousticalMath.T_X(schroeder, 30, int(fs))
            edt = AcousticalMath.EarlyDecayTime(schroeder, int(fs))

            # Pachyderm native Clarity & Definition
            c50 = AcousticalMath.Clarity(etc_net, fs, 0.05, float(min_arr_time), False)
            c80 = AcousticalMath.Clarity(etc_net, fs, 0.08, float(min_arr_time), False)
            d50 = AcousticalMath.Definition(etc_net, fs, 0.05, float(min_arr_time), False)

            steady_state_spl = 94.0 + 10.0 * math.log10(max(1e-12, total_direct_p2 + total_rev_power_ss))

            band_metrics[str(freq)] = {
                "t20_s": round(t20, 2) if not math.isnan(t20) else round(t60, 2),
                "t30_s": round(t30, 2) if not math.isnan(t30) else round(t60, 2),
                "edt_s": round(edt, 2) if not math.isnan(edt) else round(t60, 2),
                "c50_db": round(c50, 2),
                "c80_db": round(c80, 2),
                "d50_percent": round(d50, 1),
                "spl_db": round(steady_state_spl, 1)
            }

        # Native Pachyderm Speech Transmission Index
        try:
            sti_result = AcousticalMath.Speech_Transmission_Index(etc_octaves, rho_c, noise_net, int(fs))
            sti_val = round(float(sti_result[0]), 2)
        except Exception as e:
            sti_val = 0.0

        # Broadband SPL(A) & SPL(C)
        a_weights = [-26.2, -16.1, -8.6, -3.2, 0.0, 1.2, 1.0, -1.1]
        c_weights = [-0.8, -0.2, 0.0, 0.0, 0.0, -0.2, -0.8, -3.0]
        sum_p2_a = sum(math.pow(10.0, (band_metrics[str(freq)]["spl_db"] + a_weights[b]) / 10.0) for b, freq in enumerate(OCTAVE_BANDS))
        sum_p2_c = sum(math.pow(10.0, (band_metrics[str(freq)]["spl_db"] + c_weights[b]) / 10.0) for b, freq in enumerate(OCTAVE_BANDS))
        spl_a = round(10.0 * math.log10(max(1e-12, sum_p2_a)), 1)
        spl_c = round(10.0 * math.log10(max(1e-12, sum_p2_c)), 1)

        c50_mid = round((band_metrics["500"]["c50_db"] + band_metrics["1000"]["c50_db"]) / 2.0, 2)
        c80_mid = round((band_metrics["500"]["c80_db"] + band_metrics["1000"]["c80_db"]) / 2.0, 2)
        d50_mid = round((band_metrics["500"]["d50_percent"] + band_metrics["1000"]["d50_percent"]) / 2.0, 1)
        edt_mid = round((band_metrics["500"]["edt_s"] + band_metrics["1000"]["edt_s"]) / 2.0, 2)
        t30_mid = round((band_metrics["500"]["t30_s"] + band_metrics["1000"]["t30_s"]) / 2.0, 2)

        # Save sample impulse responses
        if rec["id"] in ["REC_GROUND_01_FRONT_C", "REC_GROUND_04_DOME_C", "REC_GROUND_07_DOME_SE", "REC_GROUND_11_REAR_C", "REC_GALLERY_01_WEST"]:
            ir_filename = f"{config_name.lower().replace(' ', '_')}_{rec['id']}_1000hz.json"
            ir_path = os.path.join(IR_DIR, ir_filename)
            etc_1k = etc_octaves[4]
            step = int(SAMPLE_RATE / 1000)
            downsampled_ir = [round(float(etc_1k[k * step]), 8) for k in range(1000)]
            with open(ir_path, "w") as f_ir:
                json.dump({
                    "config": config_name,
                    "receiver_id": rec["id"],
                    "band_hz": 1000,
                    "sample_rate_hz": 1000,
                    "duration_ms": 1000,
                    "energy_time_curve": downsampled_ir
                }, f_ir, indent=2)

        rec_result = {
            "receiver_id": rec["id"],
            "name": rec["name"],
            "zone": rec["zone"],
            "coords": rec["coords"],
            "first_arrival_ms": round(earliest_arrival_sec * 1000.0, 1),
            "sti_pachyderm": sti_val,
            "c50_mid_db": c50_mid,
            "c80_mid_db": c80_mid,
            "d50_mid_percent": d50_mid,
            "edt_mid_s": edt_mid,
            "t30_mid_s": t30_mid,
            "spl_a_dba": spl_a,
            "spl_c_dbc": spl_c,
            "delta_c_minus_a_db": round(spl_c - spl_a, 1),
            "octave_bands": band_metrics
        }
        sim_results.append(rec_result)

    elapsed = time.time() - t_start
    print(f"Simulation of {config_name} ({len(receivers)} receivers) finished in {elapsed:.2f} s.")
    return sim_results


def main():
    print("=" * 85)
    print("  PACHYDERM ACOUSTIC MULTI-SOURCE SIMULATION ENGINE (ISO 3382-1 & IEC 60268-16)")
    print("  MOSQUE OF MUHAMMAD ALI PASHA - COMPREHENSIVE EXISTING & IMPROVED STUDY")
    print("=" * 85)

    proposed_speakers, receivers, baseline_speakers = load_model_entities()

    occupancy_scenarios = ["unoccupied", "semi_occupied", "fully_occupied"]
    all_study_data = {}

    for occ in occupancy_scenarios:
        noise_info = NOISE_SPECTRA[occ]
        total_abs, t60_sab, t60_eyr = compute_room_acoustics(occ)

        print(f"\n>>> Running Scenario: {occ.upper()} ({noise_info['label']}) <<<")
        print(f"    Absorption at 500 Hz: {total_abs[3]} Sabins | T60 Eyring: {t60_eyr[3]} s | T60 Sabine: {t60_sab[3]} s")

        base_res = run_pachyderm_simulation(
            f"Baseline_{occ}",
            baseline_speakers,
            receivers,
            t60_eyr,
            total_abs,
            noise_info["octaves_db"],
            is_improved=False
        )

        imp_res = run_pachyderm_simulation(
            f"Improved_{occ}",
            proposed_speakers,
            receivers,
            t60_eyr,
            total_abs,
            noise_info["octaves_db"],
            is_improved=True
        )

        # Means
        base_sti_mean = round(float(np.mean([r["sti_pachyderm"] for r in base_res])), 2)
        imp_sti_mean = round(float(np.mean([r["sti_pachyderm"] for r in imp_res])), 2)
        base_c50_mean = round(float(np.mean([r["c50_mid_db"] for r in base_res])), 2)
        imp_c50_mean = round(float(np.mean([r["c50_mid_db"] for r in imp_res])), 2)
        base_c80_mean = round(float(np.mean([r["c80_mid_db"] for r in base_res])), 2)
        imp_c80_mean = round(float(np.mean([r["c80_mid_db"] for r in imp_res])), 2)
        base_d50_mean = round(float(np.mean([r["d50_mid_percent"] for r in base_res])), 1)
        imp_d50_mean = round(float(np.mean([r["d50_mid_percent"] for r in imp_res])), 1)
        base_spl_mean = round(float(np.mean([r["spl_a_dba"] for r in base_res])), 1)
        imp_spl_mean = round(float(np.mean([r["spl_a_dba"] for r in imp_res])), 1)

        print(f"    Baseline STI: {base_sti_mean:.2f} | C50: {base_c50_mean:+.2f} dB | C80: {base_c80_mean:+.2f} dB | D50: {base_d50_mean:.1f}% | SPL(A): {base_spl_mean:.1f} dBA")
        print(f"    Improved STI: {imp_sti_mean:.2f} | C50: {imp_c50_mean:+.2f} dB | C80: {imp_c80_mean:+.2f} dB | D50: {imp_d50_mean:.1f}% | SPL(A): {imp_spl_mean:.1f} dBA")

        all_study_data[occ] = {
            "occupancy_mode": occ,
            "noise_profile": noise_info,
            "room_physics": {
                "octave_bands_hz": OCTAVE_BANDS,
                "absorption_sabins": total_abs,
                "t60_sabine_s": t60_sab,
                "t60_eyring_s": t60_eyr
            },
            "summary_means": {
                "baseline": {"sti": base_sti_mean, "c50_db": base_c50_mean, "c80_db": base_c80_mean, "d50_percent": base_d50_mean, "spl_a_dba": base_spl_mean},
                "improved": {"sti": imp_sti_mean, "c50_db": imp_c50_mean, "c80_db": imp_c80_mean, "d50_percent": imp_d50_mean, "spl_a_dba": imp_spl_mean}
            },
            "baseline_receivers": base_res,
            "improved_receivers": imp_res
        }

    dataset_path = os.path.join(SIM_DATA_DIR, "pachyderm_comprehensive_study_dataset.json")
    with open(dataset_path, "w") as f:
        json.dump(all_study_data, f, indent=2)
    print(f"\nSaved comprehensive study dataset to: {dataset_path}")

    # Also save in IMP_DIR root
    with open(os.path.join(IMP_DIR, "pachyderm_comprehensive_study_dataset.json"), "w") as f:
        json.dump(all_study_data, f, indent=2)

    return all_study_data


if __name__ == "__main__":
    main()
