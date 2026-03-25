import os
import re

out = open('clearance_output_results.txt', 'w', encoding='utf-8')

paths = [
    r'c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-',
    r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-_BACKUP_FULL'
]

files_with_size = []
for p in paths:
    for root, dirs, files in os.walk(p):
        for f in files:
            if 'clearance' in f.lower() and 'king' in f.lower():
                try:
                    fp = os.path.join(root, f)
                    size = os.path.getsize(fp)
                    files_with_size.append((size, fp))
                except Exception:
                    pass

files_with_size.sort(reverse=True)
out.write('LARGEST clearance-king FILES:\n')
for size, fp in files_with_size[:30]:
    out.write(f'{size/1024:.2f} KB - {fp}\n')
out.write('-' * 80 + '\n')

for p in paths:
    try:
        outputs_dir = os.path.join(p, 'OUTPUTS')
        if not os.path.exists(outputs_dir):
            outputs_dir = os.path.join(p, 'OUTPUTS - Copy')
        for root, dirs, files in os.walk(outputs_dir):
            for f in files:
                if 'clearance' in f.lower() and f.endswith('.csv'):
                    try:
                        fp = os.path.join(root, f)
                        size = os.path.getsize(fp)
                        out.write(f'CSV REPORT: {size/1024:.2f} KB - {fp}\n')
                    except Exception:
                        pass
    except Exception:
        pass
out.write('-' * 80 + '\n')

log_dir = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-_BACKUP_FULL\logs\debug'

logs_with_kings = []
for f in os.listdir(log_dir):
    if f.endswith('.log'):
        fp = os.path.join(log_dir, f)
        try:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                if 'clearance' in content.lower():
                    logs_with_kings.append(fp)
        except Exception:
            pass

out.write(f'Found {len(logs_with_kings)} logs mentioning clearance.\n')

for log in logs_with_kings:
    try:
        with open(log, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            
            cat_lines = [
                l for l in lines 
                if re.search(r'(extract|product|categor|analyzed|found|financial)', l, re.I) and ('clearance' in l.lower())
            ]
            
            if cat_lines:
                out.write(f'\n--- LOG: {os.path.basename(log)} ---\n')
                out.write('  [Clearance-king context lines]\n')
                for l in cat_lines[-30:]:  # Print up to 30 matching lines
                    out.write('  ' + l.strip()[:200] + '\n')
    except Exception as e:
        pass

out.close()
