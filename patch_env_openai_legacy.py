import re

with open('.env', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the broken key with the legacy OpenAI key that actually worked earlier
text = re.sub(
    r'OPENAI_API_KEY=proj_nGtJQbQ8hv1ulGBeiYenJmNT',
    r'OPENAI_API_KEY=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',
    text
)

with open('.env', 'w', encoding='utf-8') as f:
    f.write(text)

print("Reverted to the functional OpenAI API key.")
