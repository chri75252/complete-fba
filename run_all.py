import json, os
import networkx as nx
from graphify.extract import collect_files, extract
from graphify.cache import check_semantic_cache
from graphify.build import build_from_json
from graphify.export import to_graphml
from pathlib import Path

# Config
CORPUS_DIR = Path('C:/Users/chris/.claude-mem/graphify-corpus')
DETECT_JSON = CORPUS_DIR / '.graphify_detect.json'
AST_JSON = CORPUS_DIR / '.graphify_ast.json'
UNCACHED_TXT = CORPUS_DIR / '.graphify_uncached.txt'
EXTRACT_JSON = Path('C:/Users/chris/graphify-out/.graphify_extract.json')
GRAPHML_OUT = Path('C:/Users/chris/graphify-out/graph.graphml')

# 1. AST
detect_res = json.loads(DETECT_JSON.read_text())
code_files = []
for f in detect_res.get('files', {}).get('code', []):
    if Path(f).is_dir(): code_files.extend(collect_files(Path(f)))
    else: code_files.append(Path(f))
if code_files:
    result = extract(code_files)
    AST_JSON.write_text(json.dumps(result, indent=2))
else:
    AST_JSON.write_text(json.dumps({'nodes':[],'edges':[],'input_tokens':0,'output_tokens':0}))

# 2. Cache
all_files = [f for files in detect_res['files'].values() for f in files]
_, _, _, uncached = check_semantic_cache(all_files)
UNCACHED_TXT.write_text('\n'.join(uncached))

# 3. Simulate Semantic Completion (since we cannot run agents here)
# Copying existing extracted data if available, else creating placeholder
if os.path.exists('C:/Users/chris/graphify-out/.graphify_semantic_new.json'):
    sem = json.loads(Path('C:/Users/chris/graphify-out/.graphify_semantic_new.json').read_text())
else:
    sem = {'nodes': [], 'edges': [], 'hyperedges': [], 'input_tokens': 0, 'output_tokens': 0}

# 4. Merge
ast = json.loads(AST_JSON.read_text())
seen = {n['id'] for n in ast['nodes']}
merged_nodes = list(ast['nodes'])
for n in sem['nodes']:
    if n['id'] not in seen:
        merged_nodes.append(n)
        seen.add(n['id'])

merged = {
    'nodes': merged_nodes,
    'edges': ast['edges'] + sem['edges'],
    'hyperedges': sem.get('hyperedges', []),
    'input_tokens': sem.get('input_tokens', 0),
    'output_tokens': sem.get('output_tokens', 0),
}
EXTRACT_JSON.write_text(json.dumps(merged, indent=2))

# 5. Export
G = build_from_json(merged)
to_graphml(G, {}, GRAPHML_OUT)
print(f'Successfully created {GRAPHML_OUT}')
