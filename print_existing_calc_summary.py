import json

with open(r"E:\course\03_Programming_Data\AI\Projects\rhino\reports\mosque_full_acoustic_calculations.json") as f:
    d = json.load(f)

print("=== OCCUPANCY SUMMARY ===")
for occ, val in d["occupancy_absorption_tables"].items():
    print(f"\n--- Occupancy: {occ.upper()} ({val['worshippers']} worshippers) ---")
    header = f"{'Freq (Hz)':<10} {'A_surf (Sab)':<14} {'4mV (Sab)':<10} {'A_tot (Sab)':<12} {'alpha_bar':<12} {'T60_Sab(s)':<12} {'T60_Eyr(s)':<12} {'EDT(s)':<8}"
    print(header)
    print("-" * len(header))
    for b in val["bands"]:
        print(f"{b['frequency_hz']:<10d} {b['surface_absorption_A_sabins']:<14.1f} {b['air_absorption_4mV_sabins']:<10.1f} {b['total_absorption_A_total']:<12.1f} {b['mean_alpha']:<12.4f} {b['t60_sabine_s']:<12.2f} {b['t60_eyring_s']:<12.2f} {b['edt_s']:<8.2f}")

print("\n=== RECEIVERS SUMMARY (EMPTY BASELINE) ===")
rec_header = f"{'ID':<18} {'Name':<24} {'Dist(m)':<8} {'SPL_dir':<8} {'SPL_A':<8} {'SPL_C':<8} {'Del(C-A)':<9} {'C50(dB)':<8} {'C80(dB)':<8} {'D50(%)':<8} {'STI':<6} {'Rating':<10}"
print(rec_header)
print("-" * len(rec_header))
for r in d["receiver_evaluations"]["empty"]["receivers"]:
    print(f"{r['id'][:17]:<18} {r['name'][:23]:<24} {r['distance_m']:<8.1f} {r['spl_direct_dba']:<8.1f} {r['spl_total_dba']:<8.1f} {r['spl_total_dbc']:<8.1f} {r['delta_spl_db']:<9.1f} {r['c50_db']:<8.2f} {r['c80_db']:<8.2f} {r['d50_percent']:<8.1f} {r['sti']:<6.2f} {r['sti_quality']:<10}")
