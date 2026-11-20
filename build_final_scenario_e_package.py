"""Builds the complete FINAL_SCENARIO_E_DELIVERABLES package structure and data exports."""
import os
import shutil
import json
import pandas as pd
import numpy as np

PROJECT_DIR = r"E:\course\03_Programming_Data\AI\Projects\rhino"
IMP_DIR = os.path.join(PROJECT_DIR, "Improved_Acoustic_System")
FINAL_DIR = os.path.join(IMP_DIR, "FINAL_SCENARIO_E_DELIVERABLES")

folders = [
    "01_FINAL_MODEL",
    "02_SIMULATION_DATA",
    "03_ACOUSTIC_VISUALIZATIONS",
    "04_ARCHITECTURAL_IMAGES",
    "05_FINAL_VIDEO",
    "06_FINAL_REPORT",
    "07_PRESENTATION"
]

for f in folders:
    os.makedirs(os.path.join(FINAL_DIR, f), exist_ok=True)

print("Created folder structure in:", FINAL_DIR)

# 1. Copy Model to 01_FINAL_MODEL
src_model = os.path.join(IMP_DIR, "SCENARIO_E_FINAL_MODEL.3dm")
dst_model = os.path.join(FINAL_DIR, "01_FINAL_MODEL", "SCENARIO_E_FINAL_MODEL.3dm")
shutil.copy2(src_model, dst_model)
print("Copied final 3DM model to 01_FINAL_MODEL")

# Also copy Scenario D as a separate reference archive
shutil.copy2(os.path.join(IMP_DIR, "SCENARIO_D_FINAL_MODEL.3dm"), 
             os.path.join(FINAL_DIR, "01_FINAL_MODEL", "SCENARIO_D_REFERENCE_MODEL.3dm"))

# 2. Process Simulation Data & Build CSV + Excel Exports
comp_dataset_path = os.path.join(IMP_DIR, "phase3_2_comparative_dataset.json")
with open(comp_dataset_path, "r") as f:
    comp_data = json.load(f)

scen_e = comp_data["comparative_evaluations"]["Config5_ScenarioE"]

# Export CSV for each occupancy
csv_dir = os.path.join(FINAL_DIR, "02_SIMULATION_DATA")
excel_path = os.path.join(csv_dir, "SCENARIO_E_ACOUSTIC_SIMULATION_RESULTS.xlsx")

excel_writer = pd.ExcelWriter(excel_path, engine="openpyxl")

# Sheet 1: Configuration Comparison Summary
summary_rows = []
for cfg_id, cfg_data in comp_data["comparative_evaluations"].items():
    desc = cfg_data["description"]
    for occ in ["unoccupied", "semi_occupied", "fully_occupied"]:
        m = cfg_data["occupancies"][occ]["means"]
        t60_e = cfg_data["occupancies"][occ]["mid_t60_eyring_s"]
        t60_s = cfg_data["occupancies"][occ]["mid_t60_sabine_s"]
        summary_rows.append({
            "Configuration_ID": cfg_id,
            "Description": desc,
            "Occupancy": occ.capitalize(),
            "Mid_T60_Eyring_s": t60_e,
            "Mid_T60_Sabine_s": t60_s,
            "Mean_STI": m["sti"],
            "Mean_C50_dB": m["c50_mid_db"],
            "Mean_C80_dB": m["c80_mid_db"],
            "Mean_D50_Percent": m["d50_mid_percent"],
            "Mean_EDT_s": m["edt_mid_s"],
            "Mean_SPL_A_dBA": m["spl_a_dba"],
            "Mean_SPL_C_dBC": m["spl_c_dbc"],
            "Delta_C_minus_A_dB": m["delta_c_minus_a_db"]
        })

df_summary = pd.DataFrame(summary_rows)
df_summary.to_csv(os.path.join(csv_dir, "comparative_configurations_summary.csv"), index=False)
df_summary.to_excel(excel_writer, sheet_name="All_Configurations_Summary", index=False)

# Sheets for Scenario E Receivers
for occ in ["unoccupied", "semi_occupied", "fully_occupied"]:
    recs = scen_e["occupancies"][occ]["receivers"]
    rec_rows = []
    for r in recs:
        row = {
            "Receiver_ID": r["receiver_id"],
            "Location_Name": r["name"],
            "Zone": r["zone"],
            "X_m": r["coords"][0],
            "Y_m": r["coords"][1],
            "Z_m": r["coords"][2],
            "STI": r["sti"],
            "C50_mid_dB": r["c50_mid_db"],
            "C80_mid_dB": r["c80_mid_db"],
            "D50_mid_percent": r["d50_mid_percent"],
            "EDT_mid_s": r["edt_mid_s"],
            "T30_mid_s": r["t30_mid_s"],
            "SPL_A_dBA": r["spl_a_dba"],
            "SPL_C_dBC": r["spl_c_dbc"],
            "Delta_C_minus_A_dB": r["delta_c_minus_a_db"]
        }
        # Add octave band SPL & C50
        for b in [63, 125, 250, 500, 1000, 2000, 4000, 8000]:
            b_str = str(b)
            row[f"SPL_{b}Hz_dB"] = r["octave_bands"][b_str]["spl_db"]
            row[f"C50_{b}Hz_dB"] = r["octave_bands"][b_str]["c50_db"]
            row[f"D50_{b}Hz_pct"] = r["octave_bands"][b_str]["d50_percent"]
            row[f"EDT_{b}Hz_s"] = r["octave_bands"][b_str]["edt_s"]
            row[f"T30_{b}Hz_s"] = r["octave_bands"][b_str]["t30_s"]
        rec_rows.append(row)

    df_rec = pd.DataFrame(rec_rows)
    df_rec.to_csv(os.path.join(csv_dir, f"scenario_e_receivers_{occ}.csv"), index=False)
    sheet_title = f"ScenE_Rec_{occ[:4].capitalize()}"
    df_rec.to_excel(excel_writer, sheet_name=sheet_title, index=False)

# Octave Decay Sheet
bands = [63, 125, 250, 500, 1000, 2000, 4000, 8000]
decay_rows = []
for occ in ["unoccupied", "semi_occupied", "fully_occupied"]:
    t_eyr = scen_e["occupancies"][occ]["t60_eyring_s"]
    t_sab = scen_e["occupancies"][occ]["t60_sabine_s"]
    abs_s = scen_e["occupancies"][occ]["absorption_sabins"]
    for i, b in enumerate(bands):
        decay_rows.append({
            "Occupancy": occ.capitalize(),
            "Octave_Band_Hz": b,
            "Total_Absorption_Sabins": abs_s[i],
            "T60_Eyring_s": t_eyr[i],
            "T60_Sabine_s": t_sab[i]
        })
df_decay = pd.DataFrame(decay_rows)
df_decay.to_csv(os.path.join(csv_dir, "scenario_e_octave_decay_summary.csv"), index=False)
df_decay.to_excel(excel_writer, sheet_name="Octave_Decay_Data", index=False)

# Sensitivity Analysis Sheet
sens_rows = []
for cfg_id, s_data in comp_data["sensitivity_analysis"].items():
    sens_rows.append({
        "Configuration": cfg_id,
        "Nominal_T60_s": s_data["nominal"]["t60"],
        "Conservative_T60_s": s_data["conservative"]["t60"],
        "Delta_T60_s": s_data["delta"]["t60"],
        "Nominal_STI": s_data["nominal"]["sti"],
        "Conservative_STI": s_data["conservative"]["sti"],
        "Delta_STI": s_data["delta"]["sti"],
        "Nominal_C50_dB": s_data["nominal"]["c50"],
        "Conservative_C50_dB": s_data["conservative"]["c50"],
        "Delta_C50_dB": s_data["delta"]["c50"]
    })
df_sens = pd.DataFrame(sens_rows)
df_sens.to_excel(excel_writer, sheet_name="Sensitivity_Analysis", index=False)

excel_writer.close()
print(f"Generated multi-sheet Excel workbook: {excel_path}")

# Metadata JSON
meta = {
    "project": "Mosque of Muhammad Ali Pasha - Citadel of Cairo",
    "phase": "Final Phase - Locked Scenario E Study",
    "selected_configuration": "Scenario E: Maximum Reversible Acoustic Cladding",
    "model_filename": "SCENARIO_E_FINAL_MODEL.3dm",
    "net_interior_volume_m3": 39840.0,
    "total_surface_area_m2": 11450.0,
    "simulation_solver": "Pachyderm Acoustic Universal v2.7.0.0 (.NET CLR Hybrid Solver)",
    "solver_methodology": {
        "direct_sound": "Exact 3D vector directivity, downtilt, delay alignment, 1/r distance law, atmospheric absorption",
        "reverberant_field": "Analytical Eyring-Norris diffuse decay integration per octave band",
        "post_processing": "Pachyderm AcousticalMath Schroeder Integral, Clarity, Definition, and IEC 60268-16 MTF STI algorithms"
    },
    "sound_sources": {
        "type": "Compact column line-array loudspeakers (Active 2-way with DSP)",
        "count": 20,
        "zones": ["Central Dome Inner Arcades (8)", "Lateral Outer Aisles (8)", "Qibla Front Wall (2)", "North Entrance Portals (2)"],
        "operating_spl_1m": "65 - 72 dBA",
        "delay_groups": "5 synchronized delay groups (0.0 ms to 42.5 ms)"
    },
    "receivers": {
        "count": 16,
        "standard": "ISO 3382-1:2009",
        "grid": ["Ground Floor Front Qibla (3)", "Ground Floor Central Dome (5)", "Ground Floor Aisles (2)", "Ground Floor Rear Entrance (2)", "First Floor Elevated Galleries (4)"]
    },
    "treatments_deployed": {
        "enhanced_carpet": {"area_m2": 1681.0, "thickness_mm": 22.0, "alpha_500hz": 0.65, "alpha_1000hz": 0.75, "status": "Provisional"},
        "perforated_wood_panels": {"area_m2": 550.0, "thickness_mm": 106.0, "alpha_500hz": 0.85, "alpha_1000hz": 0.75, "status": "Provisional"},
        "retractable_heavy_curtains": {"area_m2": 480.0, "thickness_mm": 6.0, "alpha_500hz": 0.75, "alpha_1000hz": 0.85, "status": "Verified ISO 354"},
        "suspended_acoustic_baffles": {"area_m2": 380.0, "thickness_mm": 60.0, "alpha_500hz": 0.85, "alpha_1000hz": 0.95, "status": "Provisional"}
    }
}
with open(os.path.join(csv_dir, "simulation_metadata.json"), "w") as f:
    json.dump(meta, f, indent=2)
print("Saved simulation metadata JSON.")
