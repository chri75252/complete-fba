import json, sys

p = r'C:\Users\chris\claude-clean\projects\C--Users-chris-Desktop-Amazon-FBA-Agent-System-v32---latest-good---Copy--8----Copy---Copy---POSTLONGRUNPREKIRO2-beforecompletion-\783dd241-f90d-4113-b933-400c8f5ec405.jsonl'

with open(p, encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Extract key user messages
user_msgs = []
for i, line in enumerate(lines):
    j = json.loads(line)
    if j.get('type') == 'user':
        msg = j.get('message', {})
        c = msg.get('content', '')
        if isinstance(c, str):
            txt = c
        elif isinstance(c, list):
            parts = []
            for part in c:
                if isinstance(part, dict) and part.get('type') == 'text':
                    parts.append(part.get('text', ''))
            txt = ' '.join(parts)
        else:
            txt = str(c)
        if len(txt.strip()) > 20 and not txt.strip().startswith('<local-command') and not txt.strip().startswith('<command-name>'):
            user_msgs.append((i, j.get('timestamp', '')[:19], txt))

# Write to file
outpath = r'C:\Users\chris\Desktop\chat_user_msgs.txt'
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(f"Total lines in JSONL: {len(lines)}\n")
    f.write(f"Total meaningful user messages: {len(user_msgs)}\n\n")
    for idx, (i, ts, txt) in enumerate(user_msgs):
        f.write(f"\n=== USER MSG #{idx} (LINE {i}, {ts}) ===\n")
        f.write(txt[:2000])
        f.write('\n')

print(f"Wrote {len(user_msgs)} messages to {outpath}")