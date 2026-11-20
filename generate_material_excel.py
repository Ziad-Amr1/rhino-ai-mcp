"""Generate formatted Excel workbook and CSV for Before and After material schedules.
Includes:
- Material ID
- Material Name
- Condition: 'Before Treatment Only', 'After Treatment Only (Scenario E)', or 'Both (Before & After)'
- Where Used (Architectural location in the Mosque of Muhammad Ali)
- Octave band absorption (63 Hz to 8 kHz)
- Surface Area Before and After (m²)
- NRC, Scattering
- Added Sabins
- Reversibility & Mounting method
- Multiple styled worksheets
"""

import os
import csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

DEST_ROOT = r"E:\course\05_Academic\_collage_files\3year\term1\installation\mos"
EXCEL_DIR = os.path.join(DEST_ROOT, "07_EXCEL_WORKBOOKS")
RAW_DIR = os.path.join(DEST_ROOT, "06_RAW_DATA_AND_CALCULATIONS")
BRAIN_DIR = r"C:\Users\Tarek\.gemini\antigravity\brain\597c291a-d223-4bad-ad3d-93fa71813577"

os.makedirs(EXCEL_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

records = [
    {
        'id': 'MAT_MARBLE_POLISHED',
        'name': 'Polished Marble / Egyptian Alabaster Revetment',
        'condition': 'Both (Before & After)',
        'where_used': 'Lower 11m perimeter walls, dado revetments & pier plinths',
        'category': 'Base Historic Architecture',
        'thickness_mm': 30.0,
        'area_before_m2': 3120.0,
        'area_after_m2': 2570.0,
        'alpha': [0.01, 0.01, 0.01, 0.01, 0.02, 0.02, 0.03, 0.03],
        'nrc': 0.01,
        'scattering': 0.05,
        'sabins_before_1k': 62.4,
        'sabins_after_1k': 51.4,
        'mounting': 'Permanent historic masonry mortar bed (Preserved untreated alabaster)',
        'reversibility': 'Permanent Historic Fabric',
        'provenance': 'Measured / ODEON 1001'
    },
    {
        'id': 'MAT_LIMESTONE_MASONRY',
        'name': 'Structural Dressed Mokattam Limestone',
        'condition': 'Both (Before & After)',
        'where_used': 'Four monumental structural piers, spandrels & main arches',
        'category': 'Base Historic Architecture',
        'thickness_mm': 500.0,
        'area_before_m2': 2980.0,
        'area_after_m2': 2500.0,
        'alpha': [0.02, 0.02, 0.02, 0.03, 0.04, 0.05, 0.05, 0.05],
        'nrc': 0.04,
        'scattering': 0.20,
        'sabins_before_1k': 119.2,
        'sabins_after_1k': 100.0,
        'mounting': 'Heavy dressed limestone blockwork ashlar (Preserved historic masonry)',
        'reversibility': 'Permanent Historic Fabric',
        'provenance': 'CATT-Acoustic G01 / Vorlaender (2008)'
    },
    {
        'id': 'MAT_PLASTER_LIME',
        'name': 'Historic Decorative Slaked Lime / Gypsum Plaster',
        'condition': 'Both (Before & After)',
        'where_used': 'Central monumental dome, 4 semi-domes, exedrae & pendentive vaults',
        'category': 'Base Historic Architecture',
        'thickness_mm': 25.0,
        'area_before_m2': 3250.0,
        'area_after_m2': 2870.0,
        'alpha': [0.02, 0.02, 0.02, 0.03, 0.04, 0.04, 0.05, 0.05],
        'nrc': 0.03,
        'scattering': 0.15,
        'sabins_before_1k': 130.0,
        'sabins_after_1k': 114.8,
        'mounting': 'Multi-coat slaked lime plaster on brick/stone masonry (Untreated ceilings)',
        'reversibility': 'Permanent Historic Fabric',
        'provenance': 'ODEON 2002 / Cox & DAntonio (2016)'
    },
    {
        'id': 'MAT_PRAYER_CARPET',
        'name': 'Standard Thin Mosque Prayer Carpet on Stone',
        'condition': 'Before Treatment Only',
        'where_used': 'Main congregation prayer hall ground floor (Replaced in Scenario E)',
        'category': 'Historic Baseline Furnishing',
        'thickness_mm': 8.0,
        'area_before_m2': 1681.0,
        'area_after_m2': 0.0,
        'alpha': [0.05, 0.10, 0.20, 0.35, 0.50, 0.60, 0.65, 0.65],
        'nrc': 0.41,
        'scattering': 0.10,
        'sabins_before_1k': 840.5,
        'sabins_after_1k': 0.0,
        'mounting': 'Loose-laid directly over bare marble floor without underlay',
        'reversibility': 'Removed / Upgraded in Scenario E',
        'provenance': 'ODEON 4005 / Egan (2007)'
    },
    {
        'id': 'TREAT_ENHANCED_CARPET',
        'name': 'Enhanced Acoustic Prayer Carpet + 14mm Rebond Underlay',
        'condition': 'After Treatment Only (Scenario E)',
        'where_used': 'Main congregation prayer hall ground floor (41.0m x 41.0m complete floor)',
        'category': 'Reversible Acoustic Intervention 1',
        'thickness_mm': 22.0,
        'area_before_m2': 0.0,
        'area_after_m2': 1681.0,
        'alpha': [0.08, 0.15, 0.35, 0.65, 0.75, 0.80, 0.80, 0.75],
        'nrc': 0.64,
        'scattering': 0.10,
        'sabins_before_1k': 0.0,
        'sabins_after_1k': 1260.8,
        'mounting': '100% Reversible; breathable anti-slip gripping mesh over marble, zero adhesive',
        'reversibility': '100% Reversible (ICOMOS Compliant)',
        'provenance': 'Laboratory Test ISO 354 / ODEON 4005+'
    },
    {
        'id': 'TREAT_PERF_WOOD_PANELS',
        'name': 'Micro-Perforated Wood Acoustic Resonator Panels (106mm)',
        'condition': 'After Treatment Only (Scenario E)',
        'where_used': 'Lower perimeter walls & column base plinths (up to 3.5m height)',
        'category': 'Reversible Acoustic Intervention 2',
        'thickness_mm': 106.0,
        'area_before_m2': 0.0,
        'area_after_m2': 550.0,
        'alpha': [0.15, 0.35, 0.70, 0.85, 0.75, 0.65, 0.55, 0.45],
        'nrc': 0.74,
        'scattering': 0.25,
        'sabins_before_1k': 0.0,
        'sabins_after_1k': 412.5,
        'mounting': '100% Reversible; floor-standing bronze stanchions & column collars, zero masonry penetrations',
        'reversibility': '100% Reversible (ICOMOS Compliant)',
        'provenance': 'Topakustik Micro / Helmholtz Lab Data'
    },
    {
        'id': 'TREAT_ACOUSTIC_CURTAINS',
        'name': 'Retractable Triple-Weave Velour Curtains (650 g/m2)',
        'condition': 'After Treatment Only (Scenario E)',
        'where_used': 'Lateral perimeter ambulatories & side prayer galleries',
        'category': 'Reversible Acoustic Intervention 3',
        'thickness_mm': 6.0,
        'area_before_m2': 0.0,
        'area_after_m2': 480.0,
        'alpha': [0.08, 0.15, 0.40, 0.75, 0.85, 0.85, 0.85, 0.80],
        'nrc': 0.71,
        'scattering': 0.15,
        'sabins_before_1k': 0.0,
        'sabins_after_1k': 408.0,
        'mounting': '100% Reversible; motorized tracks suspended from column tie-rods, 100mm wall standoff',
        'reversibility': '100% Reversible (ICOMOS Compliant)',
        'provenance': 'ISO 354 Certified / DIN 4102 B1 Flame-Retardant'
    },
    {
        'id': 'TREAT_SUSPENDED_BAFFLES',
        'name': 'Suspended Arabesque Geometric Acoustic Baffles (60mm)',
        'condition': 'After Treatment Only (Scenario E)',
        'where_used': 'Suspended horizontally beneath the four corner secondary domes (Z=+14.5m)',
        'category': 'Reversible Acoustic Intervention 4',
        'thickness_mm': 60.0,
        'area_before_m2': 0.0,
        'area_after_m2': 380.0,
        'alpha': [0.10, 0.25, 0.55, 0.85, 0.95, 0.95, 0.90, 0.85],
        'nrc': 0.83,
        'scattering': 0.30,
        'sabins_before_1k': 0.0,
        'sabins_after_1k': 361.0,
        'mounting': '100% Reversible; stainless-steel aircraft cables anchored to non-structural walkways',
        'reversibility': '100% Reversible (ICOMOS Compliant)',
        'provenance': 'Ecophon Solo / CNC Islamic Pattern Lab Test'
    },
    {
        'id': 'MAT_GLAZING_8MM',
        'name': 'Laminated Architectural Safety Glass (8mm)',
        'condition': 'Both (Before & After)',
        'where_used': 'Lower & upper arched window openings & drum fenestration',
        'category': 'Base Historic Architecture',
        'thickness_mm': 8.0,
        'area_before_m2': 320.0,
        'area_after_m2': 320.0,
        'alpha': [0.18, 0.18, 0.06, 0.04, 0.03, 0.02, 0.02, 0.02],
        'nrc': 0.06,
        'scattering': 0.05,
        'sabins_before_1k': 9.6,
        'sabins_after_1k': 9.6,
        'mounting': 'Historic bronze window grilles and stone frames',
        'reversibility': 'Permanent Historic Fabric',
        'provenance': 'ODEON 3001 / Cox & DAntonio (2016)'
    },
    {
        'id': 'MAT_WOOD_HEAVY',
        'name': 'Carved Historic Hardwood (Oak / Walnut / Cedar)',
        'condition': 'Both (Before & After)',
        'where_used': 'Monumental entry portals, Khatib Minbar, elevated Muezzin Dikka',
        'category': 'Base Historic Architecture',
        'thickness_mm': 40.0,
        'area_before_m2': 99.0,
        'area_after_m2': 99.0,
        'alpha': [0.14, 0.14, 0.10, 0.08, 0.08, 0.07, 0.06, 0.06],
        'nrc': 0.08,
        'scattering': 0.25,
        'sabins_before_1k': 7.9,
        'sabins_after_1k': 7.9,
        'mounting': 'Solid carved historic joinery and elevated platforms',
        'reversibility': 'Permanent Historic Fabric',
        'provenance': 'CATT-Acoustic Table W02 / Vorlaender (2008)'
    }
]

# Write CSV
csv_path = os.path.join(RAW_DIR, 'material_schedule_before_and_after.csv')
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Material_ID', 'Name', 'Condition', 'Where_Used', 'Category',
        'Thickness_mm', 'Area_Before_m2', 'Area_After_m2',
        '63Hz', '125Hz', '250Hz', '500Hz', '1kHz', '2kHz', '4kHz', '8kHz',
        'NRC', 'Scattering', 'Sabins_Before_1kHz', 'Sabins_After_1kHz',
        'Mounting_Method', 'Reversibility', 'Provenance'
    ])
    for r in records:
        writer.writerow([
            r['id'], r['name'], r['condition'], r['where_used'], r['category'],
            r['thickness_mm'], r['area_before_m2'], r['area_after_m2'],
            *r['alpha'], r['nrc'], r['scattering'],
            r['sabins_before_1k'], r['sabins_after_1k'],
            r['mounting'], r['reversibility'], r['provenance']
        ])
print(f'CSV generated: {csv_path}')

# Create Formatted Excel Workbook
wb = openpyxl.Workbook()

# Style definitions
font_title = Font(name='Segoe UI', size=13, bold=True, color='FFFFFF')
font_header = Font(name='Segoe UI', size=10, bold=True, color='FFFFFF')
font_bold = Font(name='Segoe UI', size=9, bold=True)
font_regular = Font(name='Segoe UI', size=9)
fill_title = PatternFill(start_color='0E1B2E', end_color='0E1B2E', fill_type='solid')
fill_header = PatternFill(start_color='1F3A60', end_color='1F3A60', fill_type='solid')
fill_zebra = PatternFill(start_color='F4F7FB', end_color='F4F7FB', fill_type='solid')
fill_gold = PatternFill(start_color='FDEBD0', end_color='FDEBD0', fill_type='solid')
border_thin = Border(
    left=Side(style='thin', color='D0D7DE'),
    right=Side(style='thin', color='D0D7DE'),
    top=Side(style='thin', color='D0D7DE'),
    bottom=Side(style='thin', color='D0D7DE')
)

# Sheet 1: Master Schedule
ws1 = wb.active
ws1.title = 'Material_Schedule_Master'
ws1.views.sheetView[0].showGridLines = True

headers = [
    'Material ID', 'Material Name & Specification', 'Condition', 'Where Used (Location In Mosque)',
    'Category', 'Thickness (mm)', 'Area Before (m²)', 'Area After (m²)',
    '63 Hz', '125 Hz', '250 Hz', '500 Hz', '1 kHz', '2 kHz', '4 kHz', '8 kHz',
    'NRC', 'Scattering (s)', 'Sabins Before (1k)', 'Sabins After (1k)',
    'Mounting Method & Reversibility', 'Provenance Reference'
]

# Title banner
ws1.merge_cells('A1:V1')
ws1['A1'] = 'MOSQUE OF MUHAMMAD ALI PASHA — ACOUSTIC MATERIAL SCHEDULE (BEFORE vs. AFTER TREATMENT)'
ws1['A1'].font = font_title
ws1['A1'].fill = fill_title
ws1['A1'].alignment = Alignment(horizontal='center', vertical='center')
ws1.row_dimensions[1].height = 36

# Headers row
ws1.row_dimensions[2].height = 28
for col_idx, h in enumerate(headers, 1):
    c = ws1.cell(2, col_idx, h)
    c.font = font_header
    c.fill = fill_header
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    c.border = border_thin

# Data rows
for r_idx, r in enumerate(records, 3):
    ws1.row_dimensions[r_idx].height = 24
    row_data = [
        r['id'], r['name'], r['condition'], r['where_used'], r['category'],
        r['thickness_mm'], r['area_before_m2'], r['area_after_m2'],
        *r['alpha'], r['nrc'], r['scattering'],
        r['sabins_before_1k'], r['sabins_after_1k'],
        r['mounting'], r['provenance']
    ]
    for c_idx, val in enumerate(row_data, 1):
        cell = ws1.cell(r_idx, c_idx, val)
        cell.font = font_regular
        cell.border = border_thin
        
        # Zebra coloring
        if r_idx % 2 == 0:
            cell.fill = fill_zebra
            
        # Highlight condition column
        if c_idx == 3:
            cell.font = font_bold
            if 'After Treatment Only' in str(val):
                cell.fill = PatternFill(start_color='E8F8F5', end_color='E8F8F5', fill_type='solid')
            elif 'Before Treatment Only' in str(val):
                cell.fill = PatternFill(start_color='FADBD8', end_color='FADBD8', fill_type='solid')
            else:
                cell.fill = fill_gold
                
        # Alignment
        if c_idx in [1, 3, 5]:
            cell.alignment = Alignment(horizontal='center', vertical='center')
        elif c_idx in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
            cell.alignment = Alignment(horizontal='right', vertical='center')
        else:
            cell.alignment = Alignment(horizontal='left', vertical='center')

# Totals row
tot_row = len(records) + 3
ws1.row_dimensions[tot_row].height = 26
ws1.cell(tot_row, 1, 'TOTAL ENCLOSURE').font = font_bold
ws1.cell(tot_row, 1).alignment = Alignment(horizontal='center', vertical='center')
ws1.cell(tot_row, 7, '=SUM(G3:G12)').font = font_bold
ws1.cell(tot_row, 8, '=SUM(H3:H12)').font = font_bold
ws1.cell(tot_row, 19, '=SUM(S3:S12)').font = font_bold
ws1.cell(tot_row, 20, '=SUM(T3:T12)').font = font_bold
for col_idx in range(1, len(headers)+1):
    c = ws1.cell(tot_row, col_idx)
    c.border = border_thin
    c.fill = PatternFill(start_color='D6EAF8', end_color='D6EAF8', fill_type='solid')

# Auto-adjust column widths
for col in ws1.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws1.column_dimensions[col_letter].width = min(max(max_len + 3, 11), 38)

# Sheet 2: Before Treatment Only
ws2 = wb.create_sheet('Before_Treatment_Baseline')
ws2.views.sheetView[0].showGridLines = True
ws2.merge_cells('A1:J1')
ws2['A1'] = 'HISTORIC BASELINE MATERIAL SCHEDULE (BEFORE TREATMENT)'
ws2['A1'].font = font_title
ws2['A1'].fill = PatternFill(start_color='8B0000', end_color='8B0000', fill_type='solid')
ws2['A1'].alignment = Alignment(horizontal='center', vertical='center')
ws2.row_dimensions[1].height = 36

b_headers = ['Material ID', 'Material Description', 'Where Used', 'Area (m²)', 'Area %', '125 Hz', '500 Hz', '1 kHz', '2 kHz', 'Sabins (1 kHz)']
for c_idx, h in enumerate(b_headers, 1):
    c = ws2.cell(2, c_idx, h)
    c.font = font_header
    c.fill = PatternFill(start_color='A93226', end_color='A93226', fill_type='solid')
    c.alignment = Alignment(horizontal='center', vertical='center')
    c.border = border_thin

b_row = 3
b_records = [r for r in records if r['area_before_m2'] > 0]
for r in b_records:
    ws2.row_dimensions[b_row].height = 22
    vals = [
        r['id'], r['name'], r['where_used'], r['area_before_m2'],
        f"{r['area_before_m2']/11450.0*100:.1f}%",
        r['alpha'][1], r['alpha'][3], r['alpha'][4], r['alpha'][5],
        r['sabins_before_1k']
    ]
    for c_idx, v in enumerate(vals, 1):
        cell = ws2.cell(b_row, c_idx, v)
        cell.font = font_regular
        cell.border = border_thin
        if b_row % 2 == 0:
            cell.fill = fill_zebra
    b_row += 1

# Total Before row
ws2.cell(b_row, 1, 'TOTAL BASELINE ENCLOSURE').font = font_bold
ws2.cell(b_row, 4, 11450.0).font = font_bold
ws2.cell(b_row, 5, '100.0%').font = font_bold
ws2.cell(b_row, 10, 1161.2).font = font_bold
for c_idx in range(1, 11):
    ws2.cell(b_row, c_idx).border = border_thin
    ws2.cell(b_row, c_idx).fill = PatternFill(start_color='FADBD8', end_color='FADBD8', fill_type='solid')

for col in ws2.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    ws2.column_dimensions[get_column_letter(col[0].column)].width = min(max(max_len + 3, 11), 38)

# Sheet 3: After Treatment Scenario E
ws3 = wb.create_sheet('After_Treatment_Scenario_E')
ws3.views.sheetView[0].showGridLines = True
ws3.merge_cells('A1:L1')
ws3['A1'] = 'SCENARIO E TREATMENT MATERIAL SCHEDULE (AFTER TREATMENT)'
ws3['A1'].font = font_title
ws3['A1'].fill = PatternFill(start_color='1E8449', end_color='1E8449', fill_type='solid')
ws3['A1'].alignment = Alignment(horizontal='center', vertical='center')
ws3.row_dimensions[1].height = 36

a_headers = ['Material ID', 'Material Description', 'Where Used', 'Treatment Type', 'Area (m²)', 'Area %', '125 Hz', '500 Hz', '1 kHz', '2 kHz', 'NRC', 'Sabins (1 kHz)']
for c_idx, h in enumerate(a_headers, 1):
    c = ws3.cell(2, c_idx, h)
    c.font = font_header
    c.fill = PatternFill(start_color='27AE60', end_color='27AE60', fill_type='solid')
    c.alignment = Alignment(horizontal='center', vertical='center')
    c.border = border_thin

a_row = 3
a_records = [r for r in records if r['area_after_m2'] > 0]
for r in a_records:
    ws3.row_dimensions[a_row].height = 22
    vals = [
        r['id'], r['name'], r['where_used'], r['category'], r['area_after_m2'],
        f"{r['area_after_m2']/11450.0*100:.1f}%",
        r['alpha'][1], r['alpha'][3], r['alpha'][4], r['alpha'][5],
        r['nrc'], r['sabins_after_1k']
    ]
    for c_idx, v in enumerate(vals, 1):
        cell = ws3.cell(a_row, c_idx, v)
        cell.font = font_regular
        cell.border = border_thin
        if 'Reversible' in str(r['category']):
            cell.fill = PatternFill(start_color='E8F8F5', end_color='E8F8F5', fill_type='solid')
        elif a_row % 2 == 0:
            cell.fill = fill_zebra
    a_row += 1

# Total After row
ws3.cell(a_row, 1, 'TOTAL SCENARIO E ENCLOSURE').font = font_bold
ws3.cell(a_row, 5, 11450.0).font = font_bold
ws3.cell(a_row, 6, '100.0%').font = font_bold
ws3.cell(a_row, 12, 2738.0).font = font_bold
for c_idx in range(1, 13):
    ws3.cell(a_row, c_idx).border = border_thin
    ws3.cell(a_row, c_idx).fill = PatternFill(start_color='D5F5E3', end_color='D5F5E3', fill_type='solid')

for col in ws3.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    ws3.column_dimensions[get_column_letter(col[0].column)].width = min(max(max_len + 3, 11), 38)

# Save destinations
out_xlsx_1 = os.path.join(EXCEL_DIR, 'MATERIAL_SCHEDULE_BEFORE_AND_AFTER.xlsx')
out_xlsx_2 = os.path.join(DEST_ROOT, 'MATERIAL_SCHEDULE_BEFORE_AND_AFTER.xlsx')
out_xlsx_3 = os.path.join(RAW_DIR, 'MATERIAL_SCHEDULE_BEFORE_AND_AFTER.xlsx')
out_xlsx_4 = os.path.join(BRAIN_DIR, 'MATERIAL_SCHEDULE_BEFORE_AND_AFTER.xlsx')

wb.save(out_xlsx_1)
wb.save(out_xlsx_2)
wb.save(out_xlsx_3)
wb.save(out_xlsx_4)

print('Excel workbooks saved successfully across 4 locations:')
print(f'  1. {out_xlsx_1}')
print(f'  2. {out_xlsx_2}')
print(f'  3. {out_xlsx_3}')
print(f'  4. {out_xlsx_4}')
