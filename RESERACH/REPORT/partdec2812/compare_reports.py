"""
GROUND TRUTH COMPARISON ANALYSIS v2
Properly handles row ID offset between ground truth (0-based) and reports (1-based).
"""

import pandas as pd
import re

# === LOAD GROUND TRUTH ===
gt_df = pd.read_csv('ground_truth_analysis.csv', index_col=0)

# Report row IDs are 1-based, ground truth is 0-based
# So report [786] = ground truth index 785
# We need to ADD 1 to ground truth indices to match report format

gt_verified = set(idx + 1 for idx in gt_df[gt_df['verdict'] == 'VERIFIED'].index.tolist())
gt_highly_likely = set(idx + 1 for idx in gt_df[gt_df['verdict'] == 'HIGHLY_LIKELY'].index.tolist())
gt_needs_verification = set(idx + 1 for idx in gt_df[gt_df['verdict'] == 'NEEDS_VERIFICATION'].index.tolist())
gt_filtered_out = set(idx + 1 for idx in gt_df[gt_df['verdict'] == 'FILTERED_OUT'].index.tolist())
gt_low_priority = set(idx + 1 for idx in gt_df[gt_df['verdict'] == 'LOW_PRIORITY'].index.tolist())
gt_other = set(idx + 1 for idx in gt_df[gt_df['verdict'] == 'OTHER'].index.tolist())

print("="*70)
print("GROUND TRUTH SUMMARY (IDs adjusted to 1-based)")
print("="*70)
print(f"VERIFIED: {len(gt_verified)} - Sample IDs: {sorted(list(gt_verified))[:5]}")
print(f"HIGHLY LIKELY: {len(gt_highly_likely)} - Sample IDs: {sorted(list(gt_highly_likely))[:5]}")
print(f"NEEDS VERIFICATION: {len(gt_needs_verification)} - Sample IDs: {sorted(list(gt_needs_verification))[:5]}")
print(f"FILTERED OUT: {len(gt_filtered_out)} - Sample IDs: {sorted(list(gt_filtered_out))[:5]}")
print()

def extract_row_ids_manual(filepath):
    """Manually extract row IDs from markdown tables"""
    rows = {
        'VERIFIED': set(),
        'HIGHLY_LIKELY': set(),
        'NEEDS_VERIFICATION': set(),
        'FILTERED_OUT': set()
    }
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_section = None
    
    for line in lines:
        # Detect section headers
        if '## VERIFIED' in line:
            current_section = 'VERIFIED'
        elif '## HIGHLY LIKELY' in line:
            current_section = 'HIGHLY_LIKELY'
        elif '## NEEDS VERIFICATION' in line:
            current_section = 'NEEDS_VERIFICATION'
        elif '## FILTERED OUT' in line:
            current_section = 'FILTERED_OUT'
        elif line.startswith('##'):
            current_section = None
        
        if current_section and '|' in line:
            # Look for [RowID] pattern
            match = re.search(r'\[(\d+)\]', line)
            if match:
                rows[current_section].add(int(match.group(1)))
            # Also look for RowID= pattern  
            match2 = re.search(r'RowID=(\d+)', line)
            if match2:
                rows[current_section].add(int(match2.group(1)))
    
    return rows

# Parse both reports
codex_path = r'COMP\CODEX 4 PRMPT\PHASEA_MANUAL_REPORT_20251229.md'
webapp_path = r'COMP\CODEX 4 PRMPT\PHASEA_MANUAL_REPORT_20251229webapp.md'

codex_rows = extract_row_ids_manual(codex_path)
webapp_rows = extract_row_ids_manual(webapp_path)

print("="*70)
print("CODEX v4.0 REPORT - EXTRACTED")
print("="*70)
for cat, ids in codex_rows.items():
    print(f"{cat}: {len(ids)} items - Sample: {sorted(list(ids))[:5]}")

print()
print("="*70)
print("WEBAPP v4.0 REPORT - EXTRACTED")
print("="*70)
for cat, ids in webapp_rows.items():
    print(f"{cat}: {len(ids)} items - Sample: {sorted(list(ids))[:5]}")

# === DETAILED CROSS-REFERENCE ===
def analyze_accuracy(report_name, report_rows):
    """Analyze accuracy of a report against ground truth"""
    
    print()
    print("="*70)
    print(f"{report_name} - DETAILED ACCURACY ANALYSIS")
    print("="*70)
    
    all_results = {}
    
    for category, row_ids in report_rows.items():
        # Check against each ground truth category
        in_gt_verified = row_ids & gt_verified
        in_gt_highly_likely = row_ids & gt_highly_likely
        in_gt_needs_verification = row_ids & gt_needs_verification
        in_gt_filtered_out = row_ids & gt_filtered_out
        in_gt_low_priority = row_ids & gt_low_priority
        in_gt_other = row_ids & gt_other
        
        total = len(row_ids)
        
        print(f"\n{category} ({total} items):")
        print(f"  In GT VERIFIED: {len(in_gt_verified)}")
        print(f"  In GT HIGHLY LIKELY: {len(in_gt_highly_likely)}")
        print(f"  In GT NEEDS VERIFICATION: {len(in_gt_needs_verification)}")
        print(f"  In GT FILTERED OUT: {len(in_gt_filtered_out)}")
        print(f"  In GT LOW_PRIORITY: {len(in_gt_low_priority)}")
        print(f"  In GT OTHER: {len(in_gt_other)}")
        
        # Calculate accuracy based on category
        if category == 'VERIFIED':
            correct = len(in_gt_verified)
        elif category == 'HIGHLY_LIKELY':
            correct = len(in_gt_highly_likely)
        elif category == 'NEEDS_VERIFICATION':
            correct = len(in_gt_needs_verification)
        elif category == 'FILTERED_OUT':
            correct = len(in_gt_filtered_out)
        else:
            correct = 0
        
        accuracy = (correct / total * 100) if total > 0 else 0
        print(f"  ACCURACY: {correct}/{total} = {accuracy:.1f}%")
        
        all_results[category] = {
            'total': total,
            'correct': correct,
            'accuracy': accuracy,
            'breakdown': {
                'VERIFIED': list(in_gt_verified)[:5],
                'HIGHLY_LIKELY': list(in_gt_highly_likely)[:5],
                'NEEDS_VERIFICATION': list(in_gt_needs_verification)[:5],
                'FILTERED_OUT': list(in_gt_filtered_out)[:5]
            }
        }
    
    return all_results

codex_results = analyze_accuracy("CODEX v4.0", codex_rows)
webapp_results = analyze_accuracy("WEBAPP v4.0", webapp_rows)

# === SUMMARY COMPARISON TABLE ===
print()
print("="*70)
print("FINAL COMPARISON SUMMARY")
print("="*70)
print()
print("| Category | Ground Truth | Codex v4.0 | Codex Accuracy | WebApp v4.0 | WebApp Accuracy |")
print("|----------|--------------|------------|----------------|-------------|-----------------|")
for cat in ['VERIFIED', 'HIGHLY_LIKELY', 'NEEDS_VERIFICATION', 'FILTERED_OUT']:
    gt_count = len(gt_verified if cat == 'VERIFIED' else 
                   gt_highly_likely if cat == 'HIGHLY_LIKELY' else 
                   gt_needs_verification if cat == 'NEEDS_VERIFICATION' else 
                   gt_filtered_out)
    codex_count = len(codex_rows[cat])
    codex_acc = codex_results[cat]['accuracy']
    webapp_count = len(webapp_rows[cat])
    webapp_acc = webapp_results[cat]['accuracy']
    print(f"| {cat} | {gt_count} | {codex_count} | {codex_acc:.1f}% | {webapp_count} | {webapp_acc:.1f}% |")

# === KEY FINDINGS ===
print()
print("="*70)
print("KEY FINDINGS")
print("="*70)

# Codex VERIFIED items - where are they in ground truth?
print("\nCODEX VERIFIED items breakdown:")
codex_verified_in_gt = {}
for rid in codex_rows['VERIFIED']:
    if rid in gt_verified:
        codex_verified_in_gt[rid] = 'VERIFIED'
    elif rid in gt_highly_likely:
        codex_verified_in_gt[rid] = 'HIGHLY_LIKELY'
    elif rid in gt_needs_verification:
        codex_verified_in_gt[rid] = 'NEEDS_VERIFICATION'
    elif rid in gt_filtered_out:
        codex_verified_in_gt[rid] = 'FILTERED_OUT'
    elif rid in gt_low_priority:
        codex_verified_in_gt[rid] = 'LOW_PRIORITY'
    else:
        codex_verified_in_gt[rid] = 'OTHER'

from collections import Counter
print(Counter(codex_verified_in_gt.values()))

# WebApp HIGHLY_LIKELY - where are they in ground truth?
print("\nWEBAPP HIGHLY_LIKELY items breakdown:")
webapp_hl_in_gt = {}
for rid in webapp_rows['HIGHLY_LIKELY']:
    if rid in gt_verified:
        webapp_hl_in_gt[rid] = 'VERIFIED'
    elif rid in gt_highly_likely:
        webapp_hl_in_gt[rid] = 'HIGHLY_LIKELY'
    elif rid in gt_needs_verification:
        webapp_hl_in_gt[rid] = 'NEEDS_VERIFICATION'
    elif rid in gt_filtered_out:
        webapp_hl_in_gt[rid] = 'FILTERED_OUT'
    elif rid in gt_low_priority:
        webapp_hl_in_gt[rid] = 'LOW_PRIORITY'
    else:
        webapp_hl_in_gt[rid] = 'OTHER'

print(Counter(webapp_hl_in_gt.values()))
