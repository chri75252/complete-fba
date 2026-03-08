import re

with open('control_plane/chat_orchestrator.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix fallback generator as well
old_fallback_sandbox = """            sandbox_suffix = str(params.get("sandbox_suffix") or "").strip()
            if not sandbox_suffix:
                sandbox_suffix = f"sandbox__{sandbox_id}\""""

new_fallback_sandbox = """            sandbox_suffix = str(params.get("sandbox_suffix") or "").strip()
            if not sandbox_suffix or sandbox_suffix == "<optional_for_resuming>":
                sandbox_suffix = f"sandbox__{sandbox_id}\""""

text = text.replace(old_fallback_sandbox, new_fallback_sandbox)

with open('control_plane/chat_orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Patched chat_orchestrator.py fallback logic.")
