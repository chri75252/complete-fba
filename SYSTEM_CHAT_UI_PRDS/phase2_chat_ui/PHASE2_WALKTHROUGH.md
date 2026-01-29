# Phase 2 Walkthrough (Chat UI)

## Prerequisites
- Start Ollama and ensure model exists:
  - `http://localhost:11434/api/tags` shows `deepseek-r1:7b`
- Set env vars (example):
  - `set CONTROL_PLANE_LLM_PROVIDER=ollama`
  - `set CONTROL_PLANE_OLLAMA_BASE_URL=http://localhost:11434`
  - `set CONTROL_PLANE_OLLAMA_MODEL=deepseek-r1:7b`

Optional fallback providers:
- OpenAI:
  - `set CONTROL_PLANE_LLM_PROVIDER=openai`
  - `set OPENAI_API_KEY=...`
- Anthropic:
  - `set CONTROL_PLANE_LLM_PROVIDER=anthropic`
  - `set ANTHROPIC_API_KEY=...`

## Start worker
- `python -m control_plane worker`

## Start dashboard
- `python dashboard/run_dashboard.py`

Use tabs:
- `Dashboard` (existing)
- `Operator` (Phase 1)
- `Chat` (Phase 2)

## Chat examples
### Financial query
- "Show me products ROI > 30 and NetProfit > 5 for poundwholesale"

### Output lookup
- "Find cached product with EAN 5015302170042 for efghousewares"
- "Find linking entries for EAN 5015302170042"
- "Read amazon cache for ASIN B0FLY4K9ZS"

### Traces
- "Show trace summary"

### Readiness checks
- "Run readiness check for poundwholesale"

### Enqueue run (requires confirmation)
- "Run poundwholesale workflow on these categories ... max 50 products"

The chat will propose a write tool call and you must click `Confirm execute`.

## Index / RAG
In the Chat tab:
- Click `Refresh system index`
- Click `Build RAG index`

Artifacts written:
- `OUTPUTS/CONTROL_PLANE/index/system_index.json`
- `OUTPUTS/CONTROL_PLANE/index/rag_index.json`
- `OUTPUTS/CONTROL_PLANE/audit/chat_tool_calls.jsonl`
