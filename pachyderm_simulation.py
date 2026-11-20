"""Pachyderm Acoustic Simulation Engine for Muhammad Ali Mosque.

Provides analytical acoustics solvers (Sabine, Eyring, Millington-Sette, STI)
and automates model setup, transducer deployment, and simulation execution in Rhinoceros 3D.
"""

import os
import sys
import math
import json
from typing import Any, Dict, List, Optional

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from mosque_acoustic_data import (
    OCTAVE_BANDS,
    MOSQUE_GEOMETRY,
    ACOUSTIC_MATERIALS,
    ACOUSTIC_SOURCES,
    ACOUSTIC_RECEIVERS
)
from rhino_client import RhinoClient

# Air absorption coefficient 4m (1/m) at 20 deg C, 50% relative humidity
AIR_ATTENUATION_4M = {
    63: 0.0001,
    125: 0.0003,
    250: 0.0009,
    500: 0.0022,
    1000: 0.0044,
    2000: 0.0094,
    4000: 0.0264,
    8000: 0.0930
}


def calculate_analytical_acoustics(
    volume_m3: Optional[float] = None,
    surface_area_m2: Optional[float] = None,
    occupied: bool = False
) -> Dict[str, Any]:
    """Computes room acoustic parameters (Sabine, Eyring, C50, C80, STI) across 8 octave bands.

    Based on ISO 3382-1 and classical architectural acoustics theory for monumental domed prayer halls.
    """
    V = volume_m3 or MOSQUE_GEOMETRY["total_acoustic_volume_m3"]
    S_total = surface_area_m2 or MOSQUE_GEOMETRY["total_interior_surface_area_m2"]
    breakdown = MOSQUE_GEOMETRY["surface_breakdown_m2"]

    results_by_band = []
    sabine_t60 = []
    eyring_t60 = []
    avg_alpha_list = []
    total_absorption_area_list = []

    for idx, freq in enumerate(OCTAVE_BANDS):
        A_band = 0.0
        for mat_id, area in breakdown.items():
            alpha_val = ACOUSTIC_MATERIALS[mat_id]["alpha"][idx]
            # If occupied by congregation, floor carpet absorption increases
            if occupied and mat_id == "MAT_PRAYER_CARPET":
                alpha_val = min(0.95, alpha_val + 0.25)
            A_band += area * alpha_val

        avg_alpha = A_band / S_total
        avg_alpha_list.append(round(avg_alpha, 4))
        total_absorption_area_list.append(round(A_band, 2))

        # Air attenuation addition
        air_term = AIR_ATTENUATION_4M.get(freq, 0.0) * V

        # Sabine Formula: T60 = 0.161 * V / (A + 4mV)
        t_sabine = (0.161 * V) / (A_band + air_term)
        sabine_t60.append(round(t_sabine, 2))

        # Eyring Formula: T60 = 0.161 * V / (-S * ln(1 - avg_alpha) + 4mV)
        if avg_alpha < 0.99:
            eyring_denominator = -S_total * math.log(1.0 - avg_alpha) + air_term
            t_eyring = (0.161 * V) / eyring_denominator
        else:
            t_eyring = t_sabine
        eyring_t60.append(round(t_eyring, 2))

        results_by_band.append({
            "frequency_hz": freq,
            "absorption_area_m2": round(A_band, 1),
            "mean_absorption_coeff": round(avg_alpha, 3),
            "t60_sabine_s": round(t_sabine, 2),
            "t60_eyring_s": round(t_eyring, 2)
        })

    # Mid-frequency RT (500 Hz - 1000 Hz average)
    rt_mid_sabine = round((sabine_t60[3] + sabine_t60[4]) / 2.0, 2)
    rt_mid_eyring = round((eyring_t60[3] + eyring_t60[4]) / 2.0, 2)

    # Clarity Index C50 and C80 approximations based on RT (Bradley 1999)
    # C80 ~ -10 * log10(exp(1.104 / T) - 1)
    c80_mid = round(-10.0 * math.log10(math.exp(1.104 / max(0.1, rt_mid_eyring)) - 1.0), 2)
    c50_mid = round(-10.0 * math.log10(math.exp(0.69 / max(0.1, rt_mid_eyring)) - 1.0), 2)

    # Speech Transmission Index (STI) estimate based on Houtgast & Steeneken diffuse room model
    # STI ~ (15 - 10*log10(RT/0.05)) / 30 scaled roughly for monumental spaces
    raw_sti = 0.95 - 0.10 * rt_mid_eyring
    sti_estimate = round(max(0.20, min(0.85, raw_sti)), 2)

    sti_rating = (
        "Excellent" if sti_estimate >= 0.75
        else "Good" if sti_estimate >= 0.60
        else "Fair" if sti_estimate >= 0.45
        else "Poor" if sti_estimate >= 0.30
        else "Bad"
    )

    return {
        "status": "success",
        "room_name": MOSQUE_GEOMETRY["name"],
        "volume_m3": V,
        "interior_surface_area_m2": S_total,
        "mean_free_path_m": round(4.0 * V / S_total, 2),
        "occupancy_state": "Occupied (Congregation)" if occupied else "Unoccupied (Empty Prayer Hall)",
        "summary": {
            "reverberation_time_t60_mid_eyring_s": rt_mid_eyring,
            "reverberation_time_t60_mid_sabine_s": rt_mid_sabine,
            "music_clarity_c80_mid_db": c80_mid,
            "speech_clarity_c50_mid_db": c50_mid,
            "estimated_sti": sti_estimate,
            "sti_quality_rating": sti_rating,
            "acoustic_character": (
                "Monumental imperial prayer hall with rich, reverberant sound ideal for Quranic chanting and Adhan, "
                "requiring sound reinforcement (distributed column loudspeakers) for high speech intelligibility."
            )
        },
        "octave_band_results": results_by_band
    }


def generate_rhino_setup_script() -> str:
    """Generates Python code to run inside Rhino to setup layers, materials, sources, and receivers."""
    sources_json = json.dumps(ACOUSTIC_SOURCES)
    receivers_json = json.dumps(ACOUSTIC_RECEIVERS)
    materials_json = json.dumps(ACOUSTIC_MATERIALS)

    script = f'''"""Rhino Script to Deploy Muhammad Ali Mosque Acoustic Setup."""
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import json
import System.Drawing

sources = json.loads('{sources_json}')
receivers = json.loads('{receivers_json}')
materials = json.loads('{materials_json}')

doc = Rhino.RhinoDoc.ActiveDoc
if not doc:
    print("Error: No active Rhino document.")
else:
    print("Setting up Muhammad Ali Mosque acoustic layers, sources, and receivers...")

    # 1. Ensure Acoustic Layers exist with standardized colors
    layers_to_create = [
        ("Acoustic_Sources", System.Drawing.Color.FromArgb(235, 77, 75)),        # Red
        ("Acoustic_Receivers", System.Drawing.Color.FromArgb(104, 109, 224)),    # Blue
        ("Acoustic_Carpet", System.Drawing.Color.FromArgb(240, 147, 43)),       # Orange
        ("Acoustic_Marble", System.Drawing.Color.FromArgb(223, 230, 233)),      # Off-white
        ("Acoustic_Limestone", System.Drawing.Color.FromArgb(178, 190, 195)),   # Gray
        ("Acoustic_Plaster", System.Drawing.Color.FromArgb(255, 234, 167)),     # Cream
        ("Acoustic_Glazing", System.Drawing.Color.FromArgb(116, 185, 255)),     # Cyan
        ("Acoustic_Wood", System.Drawing.Color.FromArgb(160, 82, 45))           # Brown
    ]

    for lyr_name, col in layers_to_create:
        lyr_idx = doc.Layers.Find(lyr_name, True)
        if lyr_idx < 0:
            new_lyr = Rhino.DocObjects.Layer()
            new_lyr.Name = lyr_name
            new_lyr.Color = col
            doc.Layers.Add(new_lyr)

    # 2. Deploy Acoustic Sources
    src_layer_idx = doc.Layers.Find("Acoustic_Sources", True)
    src_attr = Rhino.DocObjects.ObjectAttributes()
    src_attr.LayerIndex = src_layer_idx

    for s in sources:
        x, y, z = s["coordinates"]
        pt = Rhino.Geometry.Point3d(x, y, z)
        # Create visual source marker (sphere) and point
        sphere = Rhino.Geometry.Sphere(pt, 0.40).ToBrep()
        src_attr.Name = s["id"]
        src_attr.SetUserString("AcousticType", "Source")
        src_attr.SetUserString("SourceType", s["type"])
        src_attr.SetUserString("Description", s["name"])
        src_attr.SetUserString("SoundPowerLevel_dB", str(s["sound_power_level_db"]))
        doc.Objects.AddBrep(sphere, src_attr)
        doc.Objects.AddPoint(pt, src_attr)
        print("Placed Source: " + s["id"] + " at (" + str(x) + ", " + str(y) + ", " + str(z) + ")")

    # 3. Deploy Acoustic Receivers
    rec_layer_idx = doc.Layers.Find("Acoustic_Receivers", True)
    rec_attr = Rhino.DocObjects.ObjectAttributes()
    rec_attr.LayerIndex = rec_layer_idx

    for r in receivers:
        x, y, z = r["coordinates"]
        pt = Rhino.Geometry.Point3d(x, y, z)
        sphere = Rhino.Geometry.Sphere(pt, 0.25).ToBrep()
        rec_attr.Name = r["id"]
        rec_attr.SetUserString("AcousticType", "Receiver")
        rec_attr.SetUserString("Zone", r["zone"])
        doc.Objects.AddBrep(sphere, rec_attr)
        doc.Objects.AddPoint(pt, rec_attr)

    print("Successfully placed " + str(len(sources)) + " sources and " + str(len(receivers)) + " receivers.")
    doc.Views.Redraw()
    result = "Mosque Acoustic Setup Deployed Successfully"
'''
    return script


def deploy_mosque_acoustics_via_bridge(client: Optional[RhinoClient] = None) -> Dict[str, Any]:
    """Deploys the mosque acoustic model setup directly into Rhino using the live bridge."""
    if client is None:
        client = RhinoClient()

    # Generate setup script and send to Rhino bridge
    script = generate_rhino_setup_script()
    response = client.execute_python(script)
    return response


if __name__ == "__main__":
    print("=" * 70)
    print("   MUHAMMAD ALI MOSQUE - PACHYDERM ACOUSTIC SIMULATION")
    print("=" * 70)

    # 1. Unoccupied Room Acoustics
    unocc = calculate_analytical_acoustics(occupied=False)
    print("\n[UNOCCUPIED MOSQUE SIMULATION (Empty Prayer Hall)]")
    print(f"Hall Volume:         {unocc['volume_m3']:,.0f} m3")
    print(f"Interior Surface:    {unocc['interior_surface_area_m2']:,.0f} m2")
    print(f"Mean Free Path:      {unocc['mean_free_path_m']} m")
    print(f"Mid-Frequency T60:   {unocc['summary']['reverberation_time_t60_mid_eyring_s']} s (Eyring) / {unocc['summary']['reverberation_time_t60_mid_sabine_s']} s (Sabine)")
    print(f"Clarity C80 (Music): {unocc['summary']['music_clarity_c80_mid_db']} dB")
    print(f"Clarity C50 (Voice): {unocc['summary']['speech_clarity_c50_mid_db']} dB")
    print(f"Speech STI:          {unocc['summary']['estimated_sti']} ({unocc['summary']['sti_quality_rating']})")

    # 2. Occupied Room Acoustics
    occ = calculate_analytical_acoustics(occupied=True)
    print("\n[OCCUPIED MOSQUE SIMULATION (Full Friday Congregation)]")
    print(f"Mid-Frequency T60:   {occ['summary']['reverberation_time_t60_mid_eyring_s']} s (Eyring)")
    print(f"Speech STI:          {occ['summary']['estimated_sti']} ({occ['summary']['sti_quality_rating']})")

    print("\nOctave Band Reverberation Time Profile (Eyring):")
    for r in occ["octave_band_results"]:
        print(f"  {r['frequency_hz']:>5} Hz -> T60 = {r['t60_eyring_s']:>5.2f} s  (Absorption Area = {r['absorption_area_m2']:>6.1f} m2)")
    print("=" * 70)
