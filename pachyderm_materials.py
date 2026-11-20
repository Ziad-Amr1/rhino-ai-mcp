"""Pachyderm Acoustic Material Library Manager.

Registers and synchronizes verified acoustic materials for the Muhammad Ali Mosque
with Pachyderm Acoustic Simulation in Rhinoceros 3D.
"""

import os
import sys

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from mosque_acoustic_data import ACOUSTIC_MATERIALS

PACHYDERM_PKG_DIR = os.path.expandvars(
    r"%APPDATA%\McNeel\Rhinoceros\packages\9.0\pachyderm_acoustic_simulation\2.7.0.0"
)
PACH_LIB_PATH = os.path.join(PACHYDERM_PKG_DIR, "misc", "Pach_Materials_Library.txt")


def register_mosque_materials_in_pachyderm():
    """Appends verified mosque materials to Pachyderm's native material library file."""
    if not os.path.exists(PACH_LIB_PATH):
        print(f"[WARN] Pachyderm library file not found at: {PACH_LIB_PATH}")
        return False

    with open(PACH_LIB_PATH, "r", encoding="utf-8") as f:
        existing_content = f.read()

    lines = existing_content.strip().splitlines()
    existing_keys = set(line.split(":")[0].strip() for line in lines if ":" in line)

    new_entries = []
    for mat_id, data in ACOUSTIC_MATERIALS.items():
        mat_name = data["name"]
        code = data["pach_code"]
        entry = f"{mat_name}:{code}"
        if mat_name not in existing_keys:
            new_entries.append(entry)

    if new_entries:
        with open(PACH_LIB_PATH, "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(new_entries) + "\n")
        print(f"[SUCCESS] Registered {len(new_entries)} mosque materials in Pachyderm library!")
        for e in new_entries:
            print(f"  + {e}")
    else:
        print("[INFO] All mosque materials are already registered in Pachyderm library.")

    return True


if __name__ == "__main__":
    register_mosque_materials_in_pachyderm()
