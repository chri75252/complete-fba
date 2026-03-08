from pathlib import Path
b = Path("backup/autonomous_chat_architecture_react_20260303/chat_orchestrator.py")
if b.exists():
    print("Mtime:", b.stat().st_mtime)
    print("Size:", b.stat().st_size)
    text = b.read_text(encoding='utf-8')
    print("Has agent loop:", "def agent_plan_step" in text)
