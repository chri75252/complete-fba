#!/usr/bin/env python3
"""
Quick Corruption Scanner - Fast binary/ZIP corruption detection
"""
import json
import csv
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE_PATH = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-")
OUTPUT_DIR = BASE_PATH / "diagnostics_output"
DUBAI_TZ = timezone(timedelta(hours=4))

# Load workflow files from previous scan
with open(OUTPUT_DIR / "workflow_files.json", 'r', encoding='utf-8') as f:
    data = json.load(f)
    workflow_files = list(data['files'].keys())

print(f"Quick Corruption Scan - {datetime.now(DUBAI_TZ).strftime('%Y-%m-%d %H:%M UTC+4')}")
print(f"Scanning {len(workflow_files)} workflow files...")
print()

broken_files = []

for idx, rel_path in enumerate(workflow_files, 1):
    if idx % 50 == 0:
        print(f"Progress: {idx}/{len(workflow_files)}...")
    
    file_path = BASE_PATH / rel_path
    
    if not file_path.exists():
        broken_files.append({
            'path': rel_path,
            'issue_type': 'MissingFile',
            'severity': 'critical',
            'reason': 'File not found',
            'evidence': 'N/A'
        })
        continue
    
    try:
        raw_bytes = file_path.read_bytes()
        
        # Check for ZIP signatures
        if b'PK\x03\x04' in raw_bytes or b'PK\x05\x06' in raw_bytes or b'PK\x07\x08' in raw_bytes:
            offset = raw_bytes.find(b'PK')
            broken_files.append({
                'path': rel_path,
                'issue_type': 'BinaryZipBlob',
                'severity': 'critical',
                'reason': 'ZIP signature detected',
                'evidence': f'PK at offset {offset}, first 100 bytes: {raw_bytes[:100]!r}'
            })
            continue
        
        # Check for null bytes
        null_count = raw_bytes.count(b'\x00')
        if null_count > 0:
            broken_files.append({
                'path': rel_path,
                'issue_type': 'BinaryGeneric',
                'severity': 'critical',
                'reason': f'{null_count} null bytes detected',
                'evidence': f'First 100 bytes: {raw_bytes[:100]!r}'
            })
            continue
        
        # Check for excessive control characters
        control_bytes = sum(1 for b in raw_bytes if b < 32 and b not in (9, 10, 13))
        control_ratio = control_bytes / max(len(raw_bytes), 1)
        
        if control_ratio > 0.01:  # >1% control chars is suspicious
            broken_files.append({
                'path': rel_path,
                'issue_type': 'BinaryGeneric',
                'severity': 'critical',
                'reason': f'{control_ratio:.2%} control characters',
                'evidence': f'First 100 bytes: {raw_bytes[:100]!r}'
            })
            continue
        
        # Check for CR-only line endings
        if b'\r' in raw_bytes and b'\n' not in raw_bytes:
            broken_files.append({
                'path': rel_path,
                'issue_type': 'CRonly_LineEndings',
                'severity': 'medium',
                'reason': 'Classic Mac CR-only line endings',
                'evidence': f'Contains {raw_bytes.count(b"\r")} CR chars, 0 LF chars'
            })
            continue
        
        # Check encoding
        try:
            raw_bytes.decode('utf-8')
        except UnicodeDecodeError as e:
            broken_files.append({
                'path': rel_path,
                'issue_type': 'EncodingMismatch',
                'severity': 'medium',
                'reason': 'UTF-8 decode failed',
                'evidence': str(e)[:200]
            })
            continue
            
    except Exception as e:
        broken_files.append({
            'path': rel_path,
            'issue_type': 'Other',
            'severity': 'low',
            'reason': f'Scan error: {str(e)[:100]}',
            'evidence': str(e)[:200]
        })

print(f"\nScan complete: {len(broken_files)} files with issues found")

# Save results
if broken_files:
    with open(OUTPUT_DIR / 'broken_files.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['path', 'issue_type', 'severity', 'reason', 'evidence'])
        writer.writeheader()
        writer.writerows(broken_files)
    print(f"Saved broken_files.csv")

# Print summary
print("\n" + "="*80)
print("QUICK SCAN SUMMARY")
print("="*80)
print()

severity_counts = {}
for issue in broken_files:
    sev = issue['severity']
    severity_counts[sev] = severity_counts.get(sev, 0) + 1

for sev in ['critical', 'high', 'medium', 'low']:
    count = severity_counts.get(sev, 0)
    if count > 0:
        print(f"{sev.upper()}: {count} files")

if broken_files:
    print("\n## Top Issues\n")
    for issue in broken_files[:20]:
        print(f"- {issue['path']}")
        print(f"  {issue['issue_type']}: {issue['reason']}")
        print()

# Check high-risk files specifically
print("\n## High-Risk Files Status\n")
high_risk = ['tools\\authentication_manager.py', 'tools\\cache_manager.py', 'utils\\path_manager.py']
for hr in high_risk:
    issues = [i for i in broken_files if i['path'] == hr]
    if issues:
        print(f"❌ {hr}: {issues[0]['issue_type']}")
    else:
        print(f"✅ {hr}: OK")

print("\n" + "="*80)
