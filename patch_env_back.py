import re

with open('.env', 'r', encoding='utf-8') as f:
    text = f.read()

# Restore the exact OpenCode key you provided
text = re.sub(
    r'OPENCODE_API_KEY=.*',
    r'OPENCODE_API_KEY=sk-GMbiEsviZXDUx75qccYZNDmQLypRGq4bOwughDWWuLW6rdG2zB1TAlnHj7BCeb5T',
    text
)

# Switch the provider back to OpenCode
text = re.sub(
    r'CONTROL_PLANE_LLM_PROVIDER=openai',
    r'CONTROL_PLANE_LLM_PROVIDER=opencode',
    text
)

with open('.env', 'w', encoding='utf-8') as f:
    f.write(text)

print("Restored .env to opencode with your exact key.")
