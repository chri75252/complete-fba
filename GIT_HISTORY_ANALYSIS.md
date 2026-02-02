# Git History Analysis: Tool Selection & Category URL Behavior

## Executive Summary

This analysis traces the evolution of tool selection behavior, `category_urls` parameter handling, `find_linking_entries`, and `enqueue_run` functionality across the codebase. The primary changes occurred in **control_plane/chat_orchestrator.py** and **dashboard/chat_panel.py** between **January 25-29, 2026**.

---

## Key Commits & Changes

### Commit 1: `7fb0e681f` - "pre chat ui, llm analyze categroies and product list4"
**Date:** January 29, 2026 11:06:39 +0400  
**Status:** CURRENT HEAD (latest)

#### What Changed:
- **New file:** `control_plane/chat_orchestrator.py` (442 lines)
- **New import:** `ProductListRefreshRequest`, `enqueue_product_list_refresh`
- **Tool selection expansion:** Added `enqueue_product_list_refresh` to WRITE_TOOLS
- **Prompt enhancement:** Added critical validation rule for `category_urls`

#### Key Code Changes:

**1. Tool Dictionary Expansion:**
```python
WRITE_TOOLS = {
    "enqueue_run": "enqueue_run",
    "enqueue_onboarding": "enqueue_onboarding",
    "enqueue_product_list_refresh": "enqueue_product_list_refresh",  # NEW
}
```

**2. Critical Validation in Prompt:**
```python
"IMPORTANT: Never choose `enqueue_run` unless `category_urls` is a non-empty list.\n"
```

**3. Tool Schema for `enqueue_run`:**
```python
"enqueue_run": {
    "type": "write",
    "params": {
        "workflow_key": "<workflow_key>",
        "supplier_domain": "<supplier-domain>",
        "runner_script": "<runner-script>",
        "category_urls": ["<category-url>"],  # CRITICAL: Must be non-empty list
        "max_products": 50,
        "max_products_per_category": 50,
        "notes": "user request",
    },
}
```

**4. New Tool Schema for Product List Refresh:**
```python
"enqueue_product_list_refresh": {
    "type": "write",
    "params": {
        "supplier_domain": "<supplier-domain>",
        "products_path": "C:/path/to/products_subset.json",
        "run_id": "<run-id>",
        "notes": "user request",
        "dry_run": False,
    },
}
```

**5. Tool Execution Handler:**
```python
if name == "enqueue_product_list_refresh":
    req = ProductListRefreshRequest(
        supplier_domain=str(p.get("supplier_domain") or ""),
        products=None,
        products_path=str(p.get("products_path") or "") or None,
        run_id=str(p.get("run_id") or "") or None,
        notes=str(p.get("notes") or "") or None,
        dry_run=bool(p.get("dry_run")),
    )
    return enqueue_product_list_refresh(repo_root, req)
```

#### Why This Change:
- **Separation of concerns:** Split product list refresh into dedicated tool
- **Safety:** Explicit validation prevents `enqueue_run` with empty category URLs
- **Flexibility:** Allows LLM to choose between full run vs. product list refresh

---

### Commit 2: `prd04_product_list_refresh_20260129` (Backup)
**Date:** January 29, 2026 20:12:41 +0400  
**Status:** Backup before current HEAD

#### What Changed:
- **Baseline version** before product list refresh tool was added
- Contains the `ask_clarify` tool addition
- Has the RAG integration and prompt enhancement

#### Key Differences from Current:
- Missing `ProductListRefreshRequest` import
- Missing `enqueue_product_list_refresh` import
- WRITE_TOOLS only has 2 entries (no product list refresh)
- No product list refresh schema in tools_desc

---

### Commit 3: `chat_ux_and_product_refresh_20260129` (Backup)
**Date:** January 26, 2026 13:07:00 +0400  
**Status:** Earlier version with chat_panel.py

#### What Changed in chat_panel.py:
- **Added:** `tool_call.explanation` field support
- **Enhanced:** Message rendering to use explanation when available
- **Improved:** Tool result display logic

#### Code Changes:
```python
# BEFORE (chat_ux backup):
assistant_content = (
    str(result.get("message"))
    if isinstance(result.get("message"), str) and result.get("message")
    else f"Executed tool: `{tool_call.name}`\n\nResult: `{result.get('ok')}`"
)

# AFTER (current):
assistant_content = (
    tool_call.explanation
    if isinstance(getattr(tool_call, "explanation", None), str)
    and tool_call.explanation
    else str(result.get("message"))
    if isinstance(result.get("message"), str) and result.get("message")
    else f"Executed tool: `{tool_call.name}`\n\nResult: `{result.get('ok')}`"
)
```

#### Why This Change:
- **Better UX:** Tool explanations shown before execution results
- **Clarity:** LLM can provide reasoning for tool selection
- **Transparency:** Users see both explanation and result

---

### Commit 4: `chat_ui_fixes_20260126` (Backup)
**Date:** January 26, 2026 12:07:00 +0400  
**Status:** Earlier version with RAG integration

#### What Changed:
- **Added:** RAG context and metadata to prompt building
- **Enhanced:** `build_prompt()` signature with `rag_context` and `rag_meta` parameters
- **Expanded:** Tool descriptions with generic placeholders (`<supplier-domain>`, `<category-url>`)

#### Key Additions:
```python
def build_prompt(
    user_text: str,
    system_index: dict[str, Any] | None,
    rag_context: str,        # NEW
    rag_meta: dict[str, Any], # NEW
) -> str:
```

#### Why This Change:
- **Context awareness:** RAG provides relevant documentation
- **Flexibility:** Generic placeholders allow dynamic tool selection
- **Scalability:** Support for multiple suppliers and workflows

---

### Commit 5: `rag_integration_20260126` (Backup)
**Date:** January 26, 2026 00:22:00 +0400  
**Status:** Earlier version with basic RAG

#### What Changed:
- **Added:** RAG retriever imports
- **Added:** RAG index loading and retrieval
- **Enhanced:** `plan_tool_call()` to include RAG context

#### Key Additions:
```python
from control_plane.rag_retriever import load_rag_index, retrieve_rag, format_rag_context
from control_plane.rd2_policy import RagConfig, default_rag_config, should_use_rag

# In plan_tool_call():
rag_cfg: RagConfig = default_rag_config()
rag_enabled = bool(rag_cfg.enabled) and should_use_rag(user_text)
rag_index = load_rag_index(get_paths().rag_index_path)
```

#### Why This Change:
- **Knowledge integration:** RAG provides system documentation context
- **Intelligent selection:** LLM makes better tool choices with context
- **Reduced hallucination:** Grounded in actual system capabilities

---

### Commit 6: `runner_and_tool_fix_20260126` (Backup)
**Date:** January 25, 2026 19:17:00 +0400  
**Status:** Earliest version in backup chain

#### What Changed:
- **Initial tool framework:** Basic READ_TOOLS and WRITE_TOOLS dictionaries
- **Core tools:** `find_linking_entries`, `enqueue_run` established
- **Simple prompt:** No RAG, no explanation field

#### Key Features:
```python
READ_TOOLS = {
    "query_financial": "query_financial",
    "show_status": "show_status",
    "tail_logs": "tail_logs",
    "show_trace_summary": "show_trace_summary",
    "read_processing_state": "read_processing_state",
    "find_cached_products": "find_cached_products",
    "find_linking_entries": "find_linking_entries",  # CORE TOOL
    "read_amazon_cache_by_asin": "read_amazon_cache_by_asin",
}

WRITE_TOOLS = {
    "enqueue_run": "enqueue_run",  # CORE TOOL
}
```

#### Why This Change:
- **Foundation:** Established core tool selection pattern
- **Linking maps:** `find_linking_entries` for supplier-to-Amazon matching
- **Workflow execution:** `enqueue_run` for starting processing

---

## Evolution Timeline

```
Jan 25, 2026 19:17 ─ runner_and_tool_fix_20260126
                     └─ Basic tool framework
                        ├─ find_linking_entries (read)
                        └─ enqueue_run (write)

Jan 26, 2026 00:22 ─ rag_integration_20260126
                     └─ Add RAG context
                        ├─ RAG retriever imports
                        └─ RAG-aware prompt building

Jan 26, 2026 12:07 ─ chat_ui_fixes_20260126
                     └─ Enhance prompt with RAG
                        ├─ Generic placeholders
                        └─ RAG metadata in prompt

Jan 26, 2026 13:07 ─ chat_ux_and_product_refresh_20260129
                     └─ Add explanation field
                        ├─ tool_call.explanation
                        └─ Better message rendering

Jan 29, 2026 20:12 ─ prd04_product_list_refresh_20260129
                     └─ Baseline before product refresh

Jan 29, 2026 20:42 ─ 7fb0e681f (CURRENT HEAD)
                     └─ Add product list refresh tool
                        ├─ enqueue_product_list_refresh
                        ├─ Critical category_urls validation
                        └─ ask_clarify tool
```

---

## Key Behavioral Changes

### 1. Category URLs Validation
**When:** Commit 7fb0e681f  
**What:** Added explicit validation rule in prompt

```python
"IMPORTANT: Never choose `enqueue_run` unless `category_urls` is a non-empty list.\n"
```

**Why:** Prevent invalid runs with empty category lists  
**Impact:** LLM must verify category_urls before selecting enqueue_run

### 2. Tool Selection Expansion
**When:** Commit 7fb0e681f  
**What:** Added `enqueue_product_list_refresh` as alternative to `enqueue_run`

**Why:** Separate concerns - full run vs. product list refresh  
**Impact:** More granular control over workflow execution

### 3. Explanation Field Addition
**When:** Commit chat_ux_and_product_refresh_20260129  
**What:** Added `explanation: str | None` to ToolCall dataclass

```python
@dataclass(frozen=True)
class ToolCall:
    name: str
    params: dict[str, Any]
    explanation: str | None = None  # NEW
```

**Why:** Provide user-facing reasoning for tool selection  
**Impact:** Better transparency in chat UI

### 4. RAG Integration
**When:** Commit rag_integration_20260126  
**What:** Added RAG context to prompt building

**Why:** Ground tool selection in actual system documentation  
**Impact:** More accurate tool selection with context awareness

### 5. Generic Placeholder Adoption
**When:** Commit chat_ui_fixes_20260126  
**What:** Changed from hardcoded values to generic placeholders

```python
# BEFORE:
"supplier_domain": "poundwholesale.co.uk",

# AFTER:
"supplier_domain": "<supplier-domain>",
```

**Why:** Support multiple suppliers dynamically  
**Impact:** Scalable tool selection across suppliers

---

## find_linking_entries Evolution

### Initial Implementation (runner_and_tool_fix_20260126)
```python
"find_linking_entries": {
    "type": "read",
    "params": {
        "supplier_domain": "...",
        "supplier_ean": None,
        "amazon_asin": None,
        "supplier_url": None,
        "limit": 50,
    },
}
```

### Current Implementation (7fb0e681f)
```python
"find_linking_entries": {
    "type": "read",
    "params": {
        "supplier_domain": "<supplier-domain>",
        "supplier_ean": None,
        "amazon_asin": None,
        "supplier_url": None,
        "limit": 50,
    },
}
```

**Changes:** Only placeholder format changed (no functional changes)  
**Purpose:** Query supplier-to-Amazon linking maps  
**Use Case:** Find matching products between supplier and Amazon

---

## enqueue_run Evolution

### Initial Implementation (runner_and_tool_fix_20260126)
```python
"enqueue_run": {
    "type": "write",
    "params": {
        "workflow_key": "poundwholesale_workflow",
        "supplier_domain": "poundwholesale.co.uk",
        "runner_script": "run_custom_poundwholesale.py",
        "category_urls": ["https://..."],
        "max_products": 50,
        "max_products_per_category": 50,
        "notes": "user request",
    },
}
```

### Current Implementation (7fb0e681f)
```python
"enqueue_run": {
    "type": "write",
    "params": {
        "workflow_key": "<workflow_key>",
        "supplier_domain": "<supplier-domain>",
        "runner_script": "<runner-script>",
        "category_urls": ["<category-url>"],
        "max_products": 50,
        "max_products_per_category": 50,
        "notes": "user request",
    },
}
```

**Plus validation rule:**
```python
"IMPORTANT: Never choose `enqueue_run` unless `category_urls` is a non-empty list.\n"
```

**Changes:**
1. Hardcoded values → generic placeholders
2. Added explicit validation rule
3. category_urls must be non-empty list

**Purpose:** Enqueue a full FBA extraction run  
**Use Case:** Start supplier scraping with specific category URLs

---

## Control Plane Architecture Impact

### Tool Selection Flow
```
User Input
    ↓
plan_tool_call()
    ├─ Load system index
    ├─ Load RAG index
    ├─ Retrieve RAG context
    ├─ Build prompt with:
    │  ├─ Tool schemas
    │  ├─ System index
    │  ├─ RAG context
    │  └─ Validation rules
    ├─ Call LLM provider
    └─ Return ToolCall(name, params, explanation)
    ↓
Chat Panel
    ├─ Display explanation (if present)
    ├─ Execute tool
    └─ Display result
```

### Tool Execution Flow
```
ToolCall(name, params)
    ↓
execute_tool_call()
    ├─ Route by tool name
    ├─ Validate parameters
    ├─ Call tool function
    └─ Return result
    ↓
Chat Panel
    └─ Display result to user
```

---

## Summary of Changes

| Aspect | Initial | Current | Change |
|--------|---------|---------|--------|
| **Tool Count** | 8 read + 1 write | 11 read + 3 write | +3 read, +2 write |
| **RAG Support** | None | Full integration | Added context awareness |
| **Validation** | None | Explicit rules | Added category_urls check |
| **Explanation** | None | Optional field | Added transparency |
| **Placeholders** | Hardcoded | Generic | Improved flexibility |
| **Product Refresh** | None | Dedicated tool | Added granular control |

---

## Files Modified

### Primary Files
1. **control_plane/chat_orchestrator.py**
   - 442 lines (current)
   - Evolved from 9.1K (runner_and_tool_fix) to 17K (current)
   - Key additions: RAG, validation, product refresh tool

2. **dashboard/chat_panel.py**
   - 7.5K (current)
   - Evolved from basic rendering to explanation-aware display
   - Key additions: explanation field handling

### Supporting Files
- `control_plane/rag_retriever.py` - RAG context retrieval
- `control_plane/rd2_policy.py` - RAG configuration
- `control_plane/tools/__init__.py` - Tool definitions
- `control_plane/audit.py` - Tool call auditing

---

## Recommendations for Future Development

1. **Validation Enhancement:** Consider adding more granular validation rules for other tools
2. **Tool Documentation:** Maintain tool schemas in sync with actual implementations
3. **RAG Updates:** Keep RAG index current with system changes
4. **Explanation Quality:** Ensure LLM provides clear, actionable explanations
5. **Error Handling:** Add better error messages for invalid tool parameters
