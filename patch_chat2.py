import re

with open('control_plane/chat_orchestrator.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 1
text = re.sub(
    r'except Exception as e:\s+if attempt < 2:\s+prompt \+= f"\n\nYour last response was invalid[^\n]+\n\s+continue\s+data = \{"tool": "ask_clarify", "params": \{"user_text": user_text, "error": str\(e\)\}\}',
    r'''except Exception as e:
            if attempt < 2:
                prompt += f"\n\nYour last response was invalid/unparseable JSON ({type(e).__name__}: {e}). Return ONLY valid JSON."
                continue
            return AgentStep(kind="final_answer", text=f"LLM Provider Error: {str(e)}")''',
    text
)

with open('control_plane/chat_orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(text)

