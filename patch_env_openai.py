import re

with open('.env', 'r', encoding='utf-8') as f:
    text = f.read()

# Switch provider to openai
text = re.sub(
    r'CONTROL_PLANE_LLM_PROVIDER=opencode',
    r'CONTROL_PLANE_LLM_PROVIDER=openai',
    text
)

# Insert the provided OpenAI key (note: user provided a project token, but we will inject it where OpenAI key goes)
# First we look for OPENAI_API_KEY
if 'OPENAI_API_KEY=' in text:
    text = re.sub(
        r'OPENAI_API_KEY=.*',
        r'OPENAI_API_KEY=proj_nGtJQbQ8hv1ulGBeiYenJmNT',
        text
    )
else:
    # Append if not present
    text += '\nOPENAI_API_KEY=proj_nGtJQbQ8hv1ulGBeiYenJmNT\n'

# Add the specific model override for the OpenAI provider
if 'CONTROL_PLANE_OPENAI_MODEL=' in text:
    text = re.sub(
        r'CONTROL_PLANE_OPENAI_MODEL=.*',
        r'CONTROL_PLANE_OPENAI_MODEL=gpt-4o-mini',
        text
    )
else:
    text += '\nCONTROL_PLANE_OPENAI_MODEL=gpt-4o-mini\n'

with open('.env', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated .env for OpenAI")
