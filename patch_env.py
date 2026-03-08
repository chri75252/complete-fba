import re

with open('.env', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the OpenCode key
text = re.sub(
    r'OPENCODE_API_KEY=.*',
    r'OPENCODE_API_KEY=sk-ZYZZQCo0bkwUbUCpmqWL4wuPJJKnRX1hx2juACaPIlTJDMclUcrqOuwuSSZca1dm',
    text
)

# Temporarily switch the provider to OpenAI so the user isn't blocked by the OpenCode limits
text = re.sub(
    r'CONTROL_PLANE_LLM_PROVIDER=opencode',
    r'CONTROL_PLANE_LLM_PROVIDER=openai',
    text
)

with open('.env', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated .env")
