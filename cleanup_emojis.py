import os
import re

def remove_non_ascii(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove emojis and other non-ascii characters, keeping basic punctuation
        # This regex keeps ASCII characters (0-127)
        cleaned_content = re.sub(r'[^\x00-\x7F]+', '', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        print(f"Cleaned {file_path}")
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")

base_dir = r"c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
files_to_clean = [
    os.path.join(base_dir, "utils", "fixed_enhanced_state_manager.py"),
    os.path.join(base_dir, "tools", "passive_extraction_workflow_latest.py")
]

for file_path in files_to_clean:
    if os.path.exists(file_path):
        remove_non_ascii(file_path)
    else:
        print(f"File not found: {file_path}")
