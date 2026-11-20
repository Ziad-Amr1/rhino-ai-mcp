"""Muhammad Ali Mosque Acoustic Data Specification

Authoritative acoustic materials, transducer coordinates, and geometric properties
for the monumental prayer hall of the Mosque of Muhammad Ali (Citadel of Cairo).
"""

# Octave band center frequencies (Hz)
OCTAVE_BANDS = [63, 125, 250, 500, 1000, 2000, 4000, 8000]

# Hall Geometric Properties
MOSQUE_GEOMETRY = {
    "name": "Mosque of Muhammad Ali (Citadel of Cairo)",
    "floor_dimensions_m": [41.0, 41.0],
    "floor_area_m2": 1681.0,
    "springing_height_m": 19.94,
    "central_dome_apex_z_m": 52.0,
    "central_dome_springing_z_m": 31.0,
    "total_acoustic_volume_m3": 39840.0,
    "total_interior_surface_area_m2": 11450.0,
    "surface_breakdown_m2": {
        "MAT_PRAYER_CARPET": 1681.0,        # Ground congregation floor
        "MAT_MARBLE_POLISHED": 3120.0,      # Lower 11m alabaster/marble revetment
        "MAT_LIMESTONE_MASONRY": 2980.0,    # Upper piers, spandrels, main arches
        "MAT_PLASTER_LIME": 3250.0,         # Central dome, semi-domes, exedrae vaults
        "MAT_GLAZING_8MM": 320.0,           # Semicircular arched windows
        "MAT_WOOD_HEAVY": 99.0              # Minbar, Dikka, monumental doors
    }
}

# Verified Acoustic Material Coefficients across Octave Bands [63, 125, 250, 500, 1000, 2000, 4000, 8000 Hz]
# Alpha = absorption coefficient (0.0 to 1.0), Scattering = diffuse reflection coefficient (0.0 to 1.0)
ACOUSTIC_MATERIALS = {
    "MAT_MARBLE_POLISHED": {
        "name": "Polished Marble / Alabaster Revetment",
        "description": "Dense, honed Egyptian alabaster and Carrara marble wall facing",
        "alpha": [0.01, 0.01, 0.01, 0.01, 0.02, 0.02, 0.03, 0.03],
        "scattering": 0.05,
        "standard_ref": "Cox & D'Antonio (2016), ODEON Code 1001",
        "pach_code": "0101010102020303"
    },
    "MAT_LIMESTONE_MASONRY": {
        "name": "Structural Dressed Limestone",
        "description": "Heavy dressed Mokattam limestone masonry blocks (arches, piers)",
        "alpha": [0.02, 0.02, 0.02, 0.03, 0.04, 0.05, 0.05, 0.05],
        "scattering": 0.20,
        "standard_ref": "Vorländer (2008), CATT-Acoustic Table G01",
        "pach_code": "0202020304050505"
    },
    "MAT_PLASTER_LIME": {
        "name": "Historic Lime / Gypsum Plaster",
        "description": "Multi-coat traditional slaked lime and gypsum decorative ceiling plaster",
        "alpha": [0.02, 0.02, 0.02, 0.03, 0.04, 0.04, 0.05, 0.05],
        "scattering": 0.15,
        "standard_ref": "Cox & D'Antonio (2016), ODEON Code 2002",
        "pach_code": "0202020304040505"
    },
    "MAT_PRAYER_CARPET": {
        "name": "Wool Prayer Carpet on Underlay",
        "description": "Heavy tufted wool mosque prayer carpet over felt pad on stone floor",
        "alpha": [0.05, 0.10, 0.20, 0.35, 0.50, 0.60, 0.65, 0.65],
        "scattering": 0.10,
        "standard_ref": "Egan (2007) Architectural Acoustics, ODEON Code 4005",
        "pach_code": "0510203550606565"
    },
    "MAT_GLAZING_8MM": {
        "name": "Laminated Safety Glass (8mm)",
        "description": "Monolithic 8.0 mm laminated architectural glass in arched windows",
        "alpha": [0.18, 0.18, 0.06, 0.04, 0.03, 0.02, 0.02, 0.02],
        "scattering": 0.05,
        "standard_ref": "Cox & D'Antonio (2016), ODEON Code 3001",
        "pach_code": "1818060403020202"
    },
    "MAT_WOOD_HEAVY": {
        "name": "Carved Hardwood (Oak/Cedar)",
        "description": "Solid monumental doors, Minbar pulpit, and elevated Dikka platform",
        "alpha": [0.14, 0.14, 0.10, 0.08, 0.08, 0.07, 0.06, 0.06],
        "scattering": 0.25,
        "standard_ref": "Vorländer (2008), CATT-Acoustic Table W02",
        "pach_code": "1414100808070606"
    }
}

# Transducer Layout: Sound Sources
ACOUSTIC_SOURCES = [
    {
        "id": "SRC_IMAM_MIHRAB",
        "name": "Imam Reciter (Mihrab)",
        "coordinates": [0.0, 18.5, 1.5],
        "type": "SpeakingPerson",
        "sound_power_level_db": 74.0,  # Raised vocal effort for Islamic recitation
        "spectrum_db": [60.0, 66.0, 72.0, 75.0, 71.0, 65.0, 59.0, 52.0],
        "use": "Daily prayer recitation (speech / chanting)"
    },
    {
        "id": "SRC_KHATIB_MINBAR",
        "name": "Khatib Preacher (Minbar)",
        "coordinates": [2.8, 17.0, 3.2],
        "type": "SpeakingPerson",
        "sound_power_level_db": 76.0,  # Elevated preaching vocal effort
        "spectrum_db": [62.0, 68.0, 74.0, 77.0, 73.0, 67.0, 61.0, 54.0],
        "use": "Friday sermon (Khutbah)"
    },
    {
        "id": "SRC_MUEZZIN_DIKKA",
        "name": "Muezzin Chanter (Dikka)",
        "coordinates": [0.0, -8.0, 4.5],
        "type": "SpeakingPerson",
        "sound_power_level_db": 78.0,  # Loud projected chanting
        "spectrum_db": [64.0, 70.0, 76.0, 79.0, 75.0, 69.0, 63.0, 56.0],
        "use": "Adhan call & Quranic chanting"
    }
]

# Transducer Layout: Microphone Receivers (Z = 1.2m seated ear height on ground, Z = 9.5m gallery)
ACOUSTIC_RECEIVERS = [
    # Ground congregation carpet zone
    {"id": "REC_GROUND_01_FRONT_C", "name": "Front Center (Qibla)", "coordinates": [0.0, 14.0, 1.2], "zone": "Ground Front"},
    {"id": "REC_GROUND_02_FRONT_E", "name": "Front East", "coordinates": [8.0, 14.0, 1.2], "zone": "Ground Front"},
    {"id": "REC_GROUND_03_FRONT_W", "name": "Front West", "coordinates": [-8.0, 14.0, 1.2], "zone": "Ground Front"},
    {"id": "REC_GROUND_04_DOME_C", "name": "Central Dome Center", "coordinates": [0.0, 0.0, 1.2], "zone": "Ground Dome Center"},
    {"id": "REC_GROUND_05_DOME_NE", "name": "Dome Northeast", "coordinates": [7.0, 7.0, 1.2], "zone": "Ground Dome Northeast"},
    {"id": "REC_GROUND_06_DOME_NW", "name": "Dome Northwest", "coordinates": [-7.0, 7.0, 1.2], "zone": "Ground Dome Northwest"},
    {"id": "REC_GROUND_07_DOME_SE", "name": "Dome Southeast", "coordinates": [7.0, -7.0, 1.2], "zone": "Ground Dome Southeast"},
    {"id": "REC_GROUND_08_DOME_SW", "name": "Dome Southwest", "coordinates": [-7.0, -7.0, 1.2], "zone": "Ground Dome Southwest"},
    {"id": "REC_GROUND_09_MID_E", "name": "Mid East Lateral Aisle", "coordinates": [14.0, 0.0, 1.2], "zone": "Ground Aisle East"},
    {"id": "REC_GROUND_10_MID_W", "name": "Mid West Lateral Aisle", "coordinates": [-14.0, 0.0, 1.2], "zone": "Ground Aisle West"},
    {"id": "REC_GROUND_11_REAR_C", "name": "Rear Center Entrance", "coordinates": [0.0, -14.0, 1.2], "zone": "Ground Rear"},
    {"id": "REC_GROUND_12_REAR_W", "name": "Rear West Entrance", "coordinates": [-12.0, -14.0, 1.2], "zone": "Ground Rear"},
    # Upper Women's Galleries
    {"id": "REC_GALLERY_01_WEST", "name": "Gallery West Center", "coordinates": [-18.0, 0.0, 9.5], "zone": "Gallery West"},
    {"id": "REC_GALLERY_02_EAST", "name": "Gallery East Center", "coordinates": [18.0, 0.0, 9.5], "zone": "Gallery East"},
    {"id": "REC_GALLERY_03_REAR_W", "name": "Gallery Rear West", "coordinates": [-10.0, -18.0, 9.5], "zone": "Gallery Rear"},
    {"id": "REC_GALLERY_04_REAR_E", "name": "Gallery Rear East", "coordinates": [10.0, -18.0, 9.5], "zone": "Gallery Rear"}
]
