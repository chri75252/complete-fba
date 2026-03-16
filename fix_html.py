import re

with open('dashboard/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The incorrect part starts from `<!DOCTYPE html>` inside the `<select id="supplierSelect">` block
# Up to the end of the duplicated part which should end just before `<div class="input-group"> \n <label>Auto Refresh</label>`

# Find the start of the incorrect block
bad_start_pattern = r'(<option value="efghousewares\.co\.uk">efghousewares\.co\.uk</option>)\n<!DOCTYPE html>.*?<div class="sidebar-config">\s*<div class="config-header">Configuration</div>\s*<div class="input-group">\s*<label>Supplier Source</label>\s*<select id="supplierSelect" class="glass-input">\s*<option value="poundwholesale\.co\.uk">poundwholesale\.co\.uk</option>\s*<option value="clearance-king\.co\.uk">clearance-king\.co\.uk</option>\s*<option value="angelwholesale\.co\.uk">angelwholesale\.co\.uk</option>\s*<option value="efghousewares\.co\.uk">efghousewares\.co\.uk</option>'

fixed_content = re.sub(bad_start_pattern, r'\1', content, flags=re.DOTALL)

with open('dashboard/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(fixed_content)
