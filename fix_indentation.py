import os

def fix_indentation(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            # Replace tabs with 4 spaces
            new_line = line.replace('\t', '    ')
            new_lines.append(new_line)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Fixed indentation in {file_path}")
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")

base_dir = r"c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
files_to_fix = [
    os.path.join(base_dir, "utils", "fixed_enhanced_state_manager.py"),
    os.path.join(base_dir, "tools", "passive_extraction_workflow_latest.py")
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        fix_indentation(file_path)
    else:
        print(f"File not found: {file_path}")
