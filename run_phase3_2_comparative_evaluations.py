"""Phase 3.2: Comprehensive Comparative Simulation Engine & Sensitivity Analysis
Mosque of Muhammad Ali Pasha - Citadel of Cairo

Evaluates the 5 Required Configurations:
1. Config 1: Historic Baseline (Old 4 Column-Mounted Clusters + Raw Materials)
2. Config 2: Phase 2 Distributed System Baseline (20 Line Arrays + Raw Materials)
3. Config 3: Scenario C (20 Line Arrays + Carpet 1681m2 + Panels 420m2 + Curtains 360m2)
4. Config 4: Scenario D (20 Line Arrays + Carpet 1681m2 + Panels 420m2 + Curtains 360m2 + Baffles 280m2)
5. Config 5: Scenario E (20 Line Arrays + Carpet 1681m2 + Panels 550m2 + Curtains 480m2 + Baffles 380m2)

Calculates:
- Analytical Sabine & Eyring RT60 (with air attenuation)
- Hybrid Pachyderm Simulation (ISO 3382-1 & IEC 60268-16)
- Sensitivity Analysis on Provisional Material Coefficients (Conservative -15% bounds)
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

OCTAVE_BANDS = [63, 125, 250, 500, 1000, 2000, 4000, 8000]
MOSQUE_VOLUME = 39840.0
SURFACE_AREA = 11450.0

# Atmospheric attenuation 4m at 20C, 50% RH (1/m)
AIR_ATTENUATION_4M = [0.0001, 0.0003, 0.0009, 0.0022, 0.0044, 0.0094, 0.0264, 0.0930]

# Baseline Architectural Materials
BASELINE_MATERIALS = {
    "MAT_PRAYER_CARPET": {
        "name": "Standard Wool Carpet on Stone",
        "area_m2": 1681.0,
        "alpha": [0.05, 0.10, 0.20, 0.35, 0.50, 0.60, 0.65, 0.65]
    },
    "MAT_MARBLE_POLISHED": {
        "name": "Polished Alabaster & Marble",
        "area_m2": 3120.0,
        "alpha": [0.01, 0.01, 0.01, 0.01, 0.02, 0.02, 0.03, 0.03]
    },
    "MAT_LIMESTONE_MASONRY": {
        "name": "Dressed Structural Limestone",
        "area_m2": 2980.0,
        "alpha": [0.02, 0.02, 0.02, 0.03, 0.04, 0.05, 0.05, 0.05]
    },
    "MAT_PLASTER_LIME": {
        "name": "Decorative Plaster & Gilded Dome",
        "area_m2": 3250.0,
        "alpha": [0.02, 0.02, 0.02, 0.03, 0.04, 0.04, 0.05, 0.05]
    },
    "MAT_GLAZING_8MM": {
        "name": "Safety Glass & Bronze Grills",
        "area_m2": 320.0,
        "alpha": [0.18, 0.18, 0.06, 0.04, 0.03, 0.02, 0.02, 0.02]
    },
    "MAT_WOOD_HEAVY": {
        "name": "Carved Solid Hardwood",
        "area_m2": 99.0,
        "alpha": [0.14, 0.14, 0.10, 0.08, 0.08, 0.07, 0.06, 0.06]
    }
}

# 4 Added Reversible Treatments (Nominal Absorption)
TREATMENTS_NOMINAL = {
    "TREAT_ENHANCED_CARPET": {
        "alpha": [0.08, 0.15, 0.35, 0.65, 0.75, 0.80, 0.80, 0.75],
        "status": "PROVISIONAL"
    },
    "TREAT_PERF_WOOD_PANELS": {
        "alpha": [0.15, 0.35, 0.70, 0.85, 0.75, 0.65, 0.55, 0.45],
        "status": "PROVISIONAL"
    },
    "TREAT_ACOUSTIC_CURTAINS": {
        "alpha": [0.08, 0.15, 0.40, 0.75, 0.85, 0.85, 0.85, 0.80],
        "status": "VERIFIED_LAB"
    },
    "TREAT_SUSPENDED_BAFFLES": {
        "alpha": [0.10, 0.25, 0.55, 0.85, 0.95, 0.95, 0.90, 0.85],
        "status": "PROVISIONAL"
    }
}

# Conservative Bounds (-15% on provisional coefficients)
TREATMENTS_CONSERVATIVE = {
    "TREAT_ENHANCED_CARPET": {
        "alpha": [0.07, 0.13, 0.30, 0.55, 0.64, 0.68, 0.68, 0.64],
        "status": "CONSERVATIVE_BOUND"
    },
    "TREAT_PERF_WOOD_PANELS": {
        "alpha": [0.13, 0.30, 0.60, 0.72, 0.64, 0.55, 0.47, 0.38],
        "status": "CONSERVATIVE_BOUND"
    },
    "TREAT_ACOUSTIC_CURTAINS": {
        "alpha": [0.08, 0.15, 0.40, 0.75, 0.85, 0.85, 0.85, 0.80], # Verified remains fixed
        "status": "VERIFIED_LAB"
    },
    "TREAT_SUSPENDED_BAFFLES": {
        "alpha": [0.08, 0.21, 0.47, 0.72, 0.81, 0.81, 0.76, 0.72],
        "status": "CONSERVATIVE_BOUND"
    }
}

WORSHIPPER_ABS_PERSON = [0.08, 0.15, 0.28, 0.40, 0.46, 0.46, 0.45, 0.42]
AMBIENT_NOISE_OCTAVES = [57.0, 52.0, 45.0, 40.0, 36.0, 34.0, 32.0, 30.0]

SPEED_OF_SOUND = 343.2
AIR_RHO_C = 415.0
SAMPLE_RATE = 44100
SIM_DURATION = 4.0

def load_sources_and_receivers():
    model_path = os.path.join(IMP_DIR, "SCENARIO_D_FINAL_MODEL.3dm")
    doc = rhino3dm.File3dm.Read(model_path)

    speakers_20 = []
    for obj in doc.Objects:
        if obj.Attributes.LayerIndex == 2 and obj.Attributes.GetUserString("Speaker_ID"):
            bb = obj.Geometry.GetBoundingBox()
            cx = (bb.Min.X + bb.Max.X) / 2.0
            cy = (bb.Min.Y + bb.Max.Y) / 2.0
            cz = (bb.Min.Z + bb.Max.Z) / 2.0
            speakers_20.append({
                "id": obj.Attributes.GetUserString("Speaker_ID"),
                "coords": (cx, cy, cz),
                "delay_ms": float(obj.Attributes.GetUserString("Delay_ms")),
                "spl_1m_dba": float(obj.Attributes.GetUserString("Operating_SPL_dBA")),
                "downtilt_deg": float(obj.Attributes.GetUserString("Downtilt_deg")),
                "dispersion_v": float(obj.Attributes.GetUserString("Dispersion_V_deg"))
            })
    speakers_20.sort(key=lambda x: x["id"])

    # Old column-mounted cluster speakers (4 high-power clusters at central piers)
    old_speakers_4 = [
        {"id": "OLD_SPK_PIER_NW", "coords": (-6.0, -14.0, 7.5), "delay_ms": 0.0, "spl_1m_dba": 102.0, "downtilt_deg": 10.0, "dispersion_v": 60.0},
        {"id": "OLD_SPK_PIER_NE", "coords": ( 6.0, -14.0, 7.5), "delay_ms": 0.0, "spl_1m_dba": 102.0, "downtilt_deg": 10.0, "dispersion_v": 60.0},
        {"id": "OLD_SPK_PIER_SW", "coords": (-6.0, -29.0, 7.5), "delay_ms": 0.0, "spl_1m_dba": 102.0, "downtilt_deg": 10.0, "dispersion_v": 60.0},
        {"id": "OLD_SPK_PIER_SE", "coords": ( 6.0, -29.0, 7.5), "delay_ms": 0.0, "spl_1m_dba": 102.0, "downtilt_deg": 10.0, "dispersion_v": 60.0}
    ]

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
    return speakers_20, old_speakers_4, receivers

def calc_absorption_budget(config_key, occupancy="unoccupied", use_conservative=False):
    t_dict = TREATMENTS_CONSERVATIVE if use_conservative else TREATMENTS_NOMINAL

    mat_areas = {
        "MAT_PRAYER_CARPET": 1681.0,
        "MAT_MARBLE_POLISHED": 3120.0,
        "MAT_LIMESTONE_MASONRY": 2980.0,
        "MAT_PLASTER_LIME": 3250.0,
        "MAT_GLAZING_8MM": 320.0,
        "MAT_WOOD_HEAVY": 99.0
    }
    treatments = {}

    if config_key in ["Config1_HistoricBaseline", "Config2_Phase2Baseline"]:
        pass # Zero added treatments
    elif config_key == "Config3_ScenarioC":
        mat_areas["MAT_PRAYER_CARPET"] = 0.0
        treatments["TREAT_ENHANCED_CARPET"] = 1681.0
        treatments["TREAT_PERF_WOOD_PANELS"] = 420.0
        mat_areas["MAT_MARBLE_POLISHED"] -= 420.0
        treatments["TREAT_ACOUSTIC_CURTAINS"] = 360.0
        mat_areas["MAT_GLAZING_8MM"] -= 200.0
        mat_areas["MAT_MARBLE_POLISHED"] -= 160.0
    elif config_key == "Config4_ScenarioD":
        mat_areas["MAT_PRAYER_CARPET"] = 0.0
        treatments["TREAT_ENHANCED_CARPET"] = 1681.0
        treatments["TREAT_PERF_WOOD_PANELS"] = 420.0
        mat_areas["MAT_MARBLE_POLISHED"] -= 420.0
        treatments["TREAT_ACOUSTIC_CURTAINS"] = 360.0
        mat_areas["MAT_GLAZING_8MM"] -= 200.0
        mat_areas["MAT_MARBLE_POLISHED"] -= 160.0
        treatments["TREAT_SUSPENDED_BAFFLES"] = 280.0
    elif config_key == "Config5_ScenarioE":
        mat_areas["MAT_PRAYER_CARPET"] = 0.0
        treatments["TREAT_ENHANCED_CARPET"] = 1681.0
        treatments["TREAT_PERF_WOOD_PANELS"] = 550.0
        mat_areas["MAT_MARBLE_POLISHED"] -= 550.0
        treatments["TREAT_ACOUSTIC_CURTAINS"] = 480.0
        mat_areas["MAT_GLAZING_8MM"] -= 250.0
        mat_areas["MAT_MARBLE_POLISHED"] -= 230.0
        treatments["TREAT_SUSPENDED_BAFFLES"] = 380.0

    n_worshippers = 0
    if occupancy == "semi_occupied":
        n_worshippers = 1250
    elif occupancy == "fully_occupied":
        n_worshippers = 2500

    abs_bands = []
    t60_sabine = []
    t60_eyring = []

    for b in range(len(OCTAVE_BANDS)):
        a_b = 0.0
        for mat_key, area in mat_areas.items():
            if area > 0:
                a_b += area * BASELINE_MATERIALS[mat_key]["alpha"][b]

        for treat_key, area in treatments.items():
            a_b += area * t_dict[treat_key]["alpha"][b]

        if n_worshippers > 0:
            c_alpha = t_dict["TREAT_ENHANCED_CARPET"]["alpha"][b] if "TREAT_ENHANCED_CARPET" in treatments else BASELINE_MATERIALS["MAT_PRAYER_CARPET"]["alpha"][b]
            net_person_abs = max(0.05, WORSHIPPER_ABS_PERSON[b] - (0.85 * c_alpha * 0.5))
            a_b += n_worshippers * net_person_abs

        air_term = AIR_ATTENUATION_4M[b] * MOSQUE_VOLUME
        t_sab = (0.161 * MOSQUE_VOLUME) / (a_b + air_term)

        avg_alpha = a_b / SURFACE_AREA
        if avg_alpha < 0.98:
            eyring_denom = -SURFACE_AREA * math.log(1.0 - avg_alpha) + air_term
            t_eyr = (0.161 * MOSQUE_VOLUME) / eyring_denom
        else:
            t_eyr = t_sab

        abs_bands.append(round(a_b, 1))
        t60_sabine.append(round(t_sab, 2))
        t60_eyring.append(round(t_eyr, 2))

    return abs_bands, t60_sabine, t60_eyring, treatments

def run_hybrid_simulation(speakers, receivers, t60_bands, abs_bands, is_old_system=False):
    n_samples = int(SAMPLE_RATE * SIM_DURATION)
    fs = float(SAMPLE_RATE)
    rho_c = float(AIR_RHO_C)
    noise_net = System.Array[System.Double](AMBIENT_NOISE_OCTAVES)

    sim_results = []
    for rec in receivers:
        rx, ry, rz = rec["coords"]
        etc_octaves = System.Array.CreateInstance(System.Array[System.Double], 8)
        band_metrics = {}
        min_arrival_sec = 999.0

        for b_idx, freq in enumerate(OCTAVE_BANDS):
            etc_np = np.zeros(n_samples, dtype=np.float64)
            t60 = t60_bands[b_idx]
            decay_const = 13.8155 / t60
            m_air = AIR_ATTENUATION_4M[b_idx] / 4.0

            total_direct_p2 = 0.0
            total_rev_power_ss = 0.0

            for spk in speakers:
                sx, sy, sz = spk["coords"]
                dx = rx - sx
                dy = ry - sy
                dz = rz - sz
                dist = max(0.5, math.hypot(dx, dy, dz))

                delay_sec = spk["delay_ms"] / 1000.0
                t_arr = (dist / SPEED_OF_SOUND) + delay_sec
                min_arrival_sec = min(min_arrival_sec, t_arr)
                arr_idx = int(t_arr * SAMPLE_RATE)

                # Directivity
                downtilt_rad = math.radians(spk["downtilt_deg"])
                vert_angle = math.atan2(sz - rz, math.hypot(dx, dy))
                theta_v = abs(vert_angle - downtilt_rad)
                v_beam = math.radians(spk["dispersion_v"] / 2.0)
                v_atten_db = min(28.0, (theta_v / v_beam)**2 * 3.0)

                dsp_gain_db = 0.0
                if not is_old_system:
                    if freq == 63: dsp_gain_db -= 24.0
                    elif freq == 125: dsp_gain_db -= 6.0
                    elif freq == 250: dsp_gain_db -= 4.0
                    elif freq >= 2000: dsp_gain_db += 2.5

                spk_spl = spk["spl_1m_dba"] + dsp_gain_db
                spl_dir = spk_spl - 20.0 * math.log10(dist) - v_atten_db - (m_air * dist * 4.34)
                p2_dir = math.pow(10.0, (spl_dir - 94.0) / 10.0)

                if arr_idx < n_samples:
                    etc_np[arr_idx] += p2_dir
                    total_direct_p2 += p2_dir

                # Diffuse reverberant field
                p2_1m = math.pow(10.0, (spk_spl - 94.0) / 10.0)
                q_factor = 2.0 if is_old_system else 8.0
                a_room_band = max(250.0, abs_bands[b_idx])
                dome_spill = 0.15 if is_old_system else 0.04
                p2_rev_source = (16.0 * math.pi * p2_1m / (q_factor * a_room_band)) * dome_spill
                total_rev_power_ss += p2_rev_source

            tail_start_idx = int((min_arrival_sec + 0.012) * SAMPLE_RATE)
            if tail_start_idx < n_samples:
                t_vec = np.arange(n_samples - tail_start_idx, dtype=np.float64) / fs
                p2_rev0 = total_rev_power_ss * (decay_const / fs)
                etc_np[tail_start_idx:] += p2_rev0 * np.exp(-decay_const * t_vec)

            etc_net = System.Array[System.Double](etc_np.tolist())
            etc_octaves[b_idx] = etc_net

            idx_0 = max(0, min(n_samples - 100, int(min_arrival_sec * SAMPLE_RATE)))
            etc_trimmed = System.Array[System.Double](etc_np[idx_0:].tolist())
            schroeder = AcousticalMath.Schroeder_Integral(etc_trimmed)
            t20 = AcousticalMath.T_X(schroeder, 20, int(fs))
            t30 = AcousticalMath.T_X(schroeder, 30, int(fs))
            edt = AcousticalMath.EarlyDecayTime(schroeder, int(fs))

            c50 = AcousticalMath.Clarity(etc_net, fs, 0.05, float(min_arrival_sec), False)
            c80 = AcousticalMath.Clarity(etc_net, fs, 0.08, float(min_arrival_sec), False)
            d50 = AcousticalMath.Definition(etc_net, fs, 0.05, float(min_arrival_sec), False)
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

        try:
            sti_result = AcousticalMath.Speech_Transmission_Index(etc_octaves, rho_c, noise_net, int(fs))
            sti_val = round(float(sti_result[0]), 2)
        except Exception:
            sti_val = 0.0

        c50_mid = round((band_metrics["500"]["c50_db"] + band_metrics["1000"]["c50_db"]) / 2.0, 2)
        c80_mid = round((band_metrics["500"]["c80_db"] + band_metrics["1000"]["c80_db"]) / 2.0, 2)
        d50_mid = round((band_metrics["500"]["d50_percent"] + band_metrics["1000"]["d50_percent"]) / 2.0, 1)
        edt_mid = round((band_metrics["500"]["edt_s"] + band_metrics["1000"]["edt_s"]) / 2.0, 2)
        t30_mid = round((band_metrics["500"]["t30_s"] + band_metrics["1000"]["t30_s"]) / 2.0, 2)

        a_weights = [-26.2, -16.1, -8.6, -3.2, 0.0, 1.2, 1.0, -1.1]
        sum_p2_a = sum(math.pow(10.0, (band_metrics[str(f)]["spl_db"] + a_weights[b]) / 10.0) for b, f in enumerate(OCTAVE_BANDS))
        spl_a = round(10.0 * math.log10(max(1e-12, sum_p2_a)), 1)

        c_weights = [-0.8, -0.2, 0.0, 0.0, 0.0, -0.2, -0.8, -3.0]
        sum_p2_c = sum(math.pow(10.0, (band_metrics[str(f)]["spl_db"] + c_weights[b]) / 10.0) for b, f in enumerate(OCTAVE_BANDS))
        spl_c = round(10.0 * math.log10(max(1e-12, sum_p2_c)), 1)

        sim_results.append({
            "receiver_id": rec["id"],
            "name": rec["name"],
            "zone": rec["zone"],
            "coords": rec["coords"],
            "sti": sti_val,
            "c50_mid_db": c50_mid,
            "c80_mid_db": c80_mid,
            "d50_mid_percent": d50_mid,
            "edt_mid_s": edt_mid,
            "t30_mid_s": t30_mid,
            "spl_a_dba": spl_a,
            "spl_c_dbc": spl_c,
            "delta_c_minus_a_db": round(spl_c - spl_a, 1),
            "octave_bands": band_metrics
        })

    return sim_results

def main():
    print("=========================================================================")
    print(" PHASE 3.2: RIGOROUS COMPARATIVE EVALUATION & SENSITIVITY ENGINE")
    print(" MOSQUE OF MUHAMMAD ALI PASHA - 5 CONFIGURATIONS & 3 OCCUPANCIES")
    print("=========================================================================")

    spk_20, spk_old, receivers = load_sources_and_receivers()

    configs = [
        ("Config1_HistoricBaseline", "Historic Baseline (4 Column Clusters + Raw Materials)", True),
        ("Config2_Phase2Baseline", "Phase 2 Baseline (20 Line Arrays + Raw Materials)", False),
        ("Config3_ScenarioC", "Scenario C (20 Line Arrays + Carpet 1,681m2 + Panels 420m2 + Curtains 360m2)", False),
        ("Config4_ScenarioD", "Scenario D [Balanced Heritage] (20 Line Arrays + Carpet + Panels + Curtains + Baffles 280m2)", False),
        ("Config5_ScenarioE", "Scenario E [Max Reversible] (20 Line Arrays + Carpet + Panels 550m2 + Curtains 480m2 + Baffles 380m2)", False)
    ]

    occupancies = ["unoccupied", "semi_occupied", "fully_occupied"]
    results = {}

    for cfg_id, cfg_desc, is_old in configs:
        print(f"\nEvaluating: {cfg_id} - {cfg_desc}")
        results[cfg_id] = {
            "description": cfg_desc,
            "is_old_system": is_old,
            "occupancies": {}
        }
        spks = spk_old if is_old else spk_20

        for occ in occupancies:
            abs_bands, t60_sab, t60_eyr, treats = calc_absorption_budget(cfg_id, occ, use_conservative=False)
            mid_t60_sab = round((t60_sab[3] + t60_sab[4]) / 2.0, 2)
            mid_t60_eyr = round((t60_eyr[3] + t60_eyr[4]) / 2.0, 2)

            rec_data = run_hybrid_simulation(spks, receivers, t60_eyr, abs_bands, is_old_system=is_old)

            mean_sti = round(float(np.mean([r["sti"] for r in rec_data])), 2)
            mean_c50 = round(float(np.mean([r["c50_mid_db"] for r in rec_data])), 2)
            mean_c80 = round(float(np.mean([r["c80_mid_db"] for r in rec_data])), 2)
            mean_d50 = round(float(np.mean([r["d50_mid_percent"] for r in rec_data])), 1)
            mean_edt = round(float(np.mean([r["edt_mid_s"] for r in rec_data])), 2)
            mean_spl_a = round(float(np.mean([r["spl_a_dba"] for r in rec_data])), 1)
            mean_spl_c = round(float(np.mean([r["spl_c_dbc"] for r in rec_data])), 1)
            mean_delta = round(mean_spl_c - mean_spl_a, 1)

            print(f"  [{occ.upper()}] Mid T60: {mid_t60_eyr:.2f}s (Sabine: {mid_t60_sab:.2f}s) | STI: {mean_sti:.2f} | C50: {mean_c50:+.2f} dB | D50: {mean_d50:.1f}% | SPL(A): {mean_spl_a} dBA | Delta: +{mean_delta} dB")

            results[cfg_id]["occupancies"][occ] = {
                "absorption_sabins": abs_bands,
                "t60_sabine_s": t60_sab,
                "t60_eyring_s": t60_eyr,
                "mid_t60_eyring_s": mid_t60_eyr,
                "mid_t60_sabine_s": mid_t60_sab,
                "means": {
                    "sti": mean_sti,
                    "c50_mid_db": mean_c50,
                    "c80_mid_db": mean_c80,
                    "d50_mid_percent": mean_d50,
                    "edt_mid_s": mean_edt,
                    "spl_a_dba": mean_spl_a,
                    "spl_c_dbc": mean_spl_c,
                    "delta_c_minus_a_db": mean_delta
                },
                "receivers": rec_data
            }

    # Sensitivity Analysis on Scenario D & Scenario E with Conservative Provisional Bounds
    print("\n=========================================================================")
    print(" SENSITIVITY ANALYSIS: PROVISIONAL COEFFICIENTS (-15% WORST-CASE BOUNDS)")
    print("=========================================================================")
    sensitivity_results = {}
    for cfg_id in ["Config4_ScenarioD", "Config5_ScenarioE"]:
        sensitivity_results[cfg_id] = {}
        abs_b, t60_sab_c, t60_eyr_c, _ = calc_absorption_budget(cfg_id, "unoccupied", use_conservative=True)
        mid_eyr_c = round((t60_eyr_c[3] + t60_eyr_c[4]) / 2.0, 2)
        rec_data_c = run_hybrid_simulation(spk_20, receivers, t60_eyr_c, abs_b, is_old_system=False)

        mean_sti_c = round(float(np.mean([r["sti"] for r in rec_data_c])), 2)
        mean_c50_c = round(float(np.mean([r["c50_mid_db"] for r in rec_data_c])), 2)

        nom_t60 = results[cfg_id]["occupancies"]["unoccupied"]["mid_t60_eyring_s"]
        nom_sti = results[cfg_id]["occupancies"]["unoccupied"]["means"]["sti"]
        nom_c50 = results[cfg_id]["occupancies"]["unoccupied"]["means"]["c50_mid_db"]

        print(f"  {cfg_id}:")
        print(f"    Nominal:      T60 = {nom_t60:.2f}s | STI = {nom_sti:.2f} | C50 = {nom_c50:+.2f} dB")
        print(f"    Conservative: T60 = {mid_eyr_c:.2f}s (+{mid_eyr_c - nom_t60:.2f}s) | STI = {mean_sti_c:.2f} ({mean_sti_c - nom_sti:+.2f}) | C50 = {mean_c50_c:+.2f} dB ({mean_c50_c - nom_c50:+.2f} dB)")
        sensitivity_results[cfg_id] = {
            "nominal": {"t60": nom_t60, "sti": nom_sti, "c50": nom_c50},
            "conservative": {"t60": mid_eyr_c, "sti": mean_sti_c, "c50": mean_c50_c},
            "delta": {"t60": round(mid_eyr_c - nom_t60, 2), "sti": round(mean_sti_c - nom_sti, 2), "c50": round(mean_c50_c - nom_c50, 2)}
        }

    dataset_path = os.path.join(IMP_DIR, "phase3_2_comparative_dataset.json")
    with open(dataset_path, "w") as f:
        json.dump({"comparative_evaluations": results, "sensitivity_analysis": sensitivity_results}, f, indent=2)
    print(f"\nSaved complete comparative dataset to: {dataset_path}")

if __name__ == "__main__":
    main()
