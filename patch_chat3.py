import re

with open('control_plane/chat_orchestrator.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the schema example
text = re.sub(
    r'"sandbox_suffix": "sandbox_20260210_143022"',
    r'"sandbox_suffix": "<optional_for_resuming>"',
    text
)

# Fix execute_tool_call sandbox generation to match fallback
old_exec_sandbox = """        sandbox_suffix = str(p.get("sandbox_suffix") or "").strip()
        if not sandbox_suffix:
            sandbox_suffix = "sandbox"

        # Build sandbox_supplier for output paths/polling, but keep supplier_name canonical for credential lookup
        sandbox_supplier = f"{req.supplier_domain}__{sandbox_suffix}\""""

new_exec_sandbox = """        sandbox_suffix = str(p.get("sandbox_suffix") or "").strip()
        if not sandbox_suffix or sandbox_suffix == "<optional_for_resuming>":
            sandbox_suffix = f"sandbox__{run_id[:8]}"

        # Build sandbox_supplier for output paths/polling, but keep supplier_name canonical for credential lookup
        sandbox_supplier = f"{req.supplier_domain}__{sandbox_suffix}\""""

text = text.replace(old_exec_sandbox, new_exec_sandbox)

with open('control_plane/chat_orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Patched chat_orchestrator.py schema and sandbox generation.")
