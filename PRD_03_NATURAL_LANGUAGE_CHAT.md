# PRD 03: Natural Language Chat Implementation

**Version**: 1.0  
**Date**: 2026-01-28  
**Status**: Ready for Implementation  
**Author**: System Architect  

---

## 1. Executive Summary

### 1.1 Problem Statement

The current Chat UI outputs **JSON-only responses** that are confusing to users. When users type natural language queries like "analyze the gloves category from efghousewares", they receive raw JSON tool outputs without explanation:

```json
{"ok": true, "count": 0, "rows": [], "path": "...linking_map.json"}
```

Users cannot understand:
- What action was taken
- Why the action was chosen
- What the result means
- What to do next

### 1.2 Proposed Solution

Transform the Chat UI into a **conversational assistant** that:
1. Accepts natural language input (current behavior - no change needed)
2. Outputs natural language explanations WITH tool execution
3. Shows raw JSON in expandable sections for technical users
4. Asks clarifying questions conversationally when ambiguous

### 1.3 Key Technical Discovery

Research confirmed that **Qwen3-8B via Ollama supports triple-output responses**:
- `message.content` → Natural language explanation
- `message.thinking` → Internal reasoning (via `think=True`)
- `message.tool_calls` → Structured JSON for deterministic execution

This enables conversational chat WITHOUT sacrificing tool execution reliability.

### 1.4 Scope

| In Scope | Out of Scope |
|----------|--------------|
| `control_plane/` modifications | `tools/` workflow engine |
| `dashboard/` modifications | `utils/` utilities |
| Natural language responses | New tool implementations |
| Ollama API enhancements | Cloud LLM providers |
| Post-execution summarization | Pre-execution confirmation changes |

---

## 2. Goals and Non-Goals

### 2.1 Goals

| ID | Goal | Success Metric |
|----|------|----------------|
| G1 | Users receive natural language explanations | 100% of responses include `message` field with prose |
| G2 | Tool execution remains deterministic | 0% change to existing tool behavior |
| G3 | JSON details accessible when needed | All tool results available in expandable UI |
| G4 | Clarifying questions are conversational | `ask_clarify` returns prose, not JSON list |
| G5 | Zero breaking changes to existing workflow | All existing tests pass |

### 2.2 Non-Goals

| ID | Non-Goal | Reason |
|----|----------|--------|
| NG1 | Edit `tools/` or `utils/` | Hard constraint from previous work |
| NG2 | Modify main OUTPUTS artifacts | Hard constraint from previous work |
| NG3 | Implement new tools | Out of scope for this PRD |
| NG4 | Support cloud LLM providers | Focus on local Ollama/Qwen3 |
| NG5 | Real-time streaming UI | Future enhancement |

---

## 3. Technical Specification

### 3.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CURRENT FLOW (JSON-Only)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  User Input ──► LLM ──► {"tool":"X","params":{}} ──► Execute ──► JSON│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

                              ▼ TRANSFORM TO ▼

┌─────────────────────────────────────────────────────────────────────┐
│                      NEW FLOW (Natural Language)                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  User Input ──► LLM (think=True, tools=[...])                      │
│                  │                                                  │
│                  ├──► message.content (Explanation) ──► Display    │
│                  ├──► message.thinking (Reasoning) ──► [Optional]  │
│                  └──► message.tool_calls (JSON) ──► Execute        │
│                                         │                           │
│                                         ▼                           │
│                              Tool Result (JSON)                     │
│                                         │                           │
│                                         ▼                           │
│                         Summarize Result (2nd LLM call)            │
│                                         │                           │
│                                         ▼                           │
│                    Natural Language Summary ──► Display             │
│                    + JSON in Expander ──► [Technical Details]       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Changes

#### 3.2.1 LLM Provider Enhancement

**File**: `control_plane/llm/providers.py`

**Current State**:
```python
@dataclass(frozen=True)
class OllamaProvider:
    base_url: str
    model: str

    def generate_json(self, prompt: str) -> dict[str, Any]:
        # Forces JSON-only output via format="json"
```

**New State**:
```python
@dataclass(frozen=True)
class OllamaProvider:
    base_url: str
    model: str

    def generate_json(self, prompt: str) -> dict[str, Any]:
        # Existing method - unchanged for backward compatibility
        ...

    def generate_with_tools(
        self, 
        messages: list[dict], 
        tools: list[dict],
        think: bool = True
    ) -> dict[str, Any]:
        """
        Generate response with tool calling and optional thinking.
        
        Returns dict with:
        - content: Natural language explanation
        - thinking: Reasoning trace (if think=True)
        - tool_calls: List of tool call objects
        """
        import requests
        url = self.base_url.rstrip("/") + "/api/chat"
        resp = requests.post(
            url,
            json={
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "think": think,
                "stream": False,
                "options": {"temperature": 0.3},
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        msg = data.get("message", {})
        return {
            "content": msg.get("content", ""),
            "thinking": msg.get("thinking", ""),
            "tool_calls": msg.get("tool_calls", []),
        }

    def generate_text(self, prompt: str) -> str:
        """
        Generate natural language text (no JSON forcing).
        Used for post-tool summarization.
        """
        import requests
        url = self.base_url.rstrip("/") + "/api/generate"
        resp = requests.post(
            url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                # NO format="json" - allow natural language
                "options": {"temperature": 0.3},
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
```

#### 3.2.2 Chat Orchestrator Enhancement

**File**: `control_plane/chat_orchestrator.py`

**Changes Required**:

1. **Update ToolCall dataclass** to include explanation:
```python
@dataclass(frozen=True)
class ToolCall:
    name: str
    params: dict[str, Any]
    explanation: str = ""  # NEW: Natural language from LLM
    thinking: str = ""     # NEW: Reasoning trace (optional)
```

2. **Add tool schema for Ollama tools API**:
```python
def _build_tools_schema() -> list[dict]:
    """Build Ollama-compatible tools schema."""
    return [
        {
            "type": "function",
            "function": {
                "name": "ask_clarify",
                "description": "Ask user for clarification when request is ambiguous or missing required information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "questions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of clarifying questions"
                        }
                    },
                    "required": ["questions"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_financial",
                "description": "Query financial data for products matching criteria",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "supplier_domain": {"type": "string", "description": "Supplier domain e.g. poundwholesale.co.uk"},
                        "roi_min": {"type": "number", "description": "Minimum ROI percentage"},
                        "netprofit_min": {"type": "number", "description": "Minimum net profit in GBP"},
                        "limit": {"type": "integer", "description": "Max results to return"}
                    },
                    "required": ["supplier_domain"]
                }
            }
        },
        # ... additional tools following same pattern
    ]
```

3. **New conversational planning function**:
```python
def plan_tool_call_conversational(
    user_text: str, 
    repo_root: Path,
    chat_history: list[dict] | None = None
) -> tuple[ToolCall, dict[str, Any]]:
    """
    Plan tool call using Ollama's native tool calling with thinking mode.
    Returns natural language explanation alongside tool call.
    """
    provider = get_provider()
    
    # Build messages with system context
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant for an Amazon FBA analysis system.\n"
                "You help users query product data, check system status, and manage extraction runs.\n"
                "Always explain what you're doing in natural language.\n"
                "If the request is unclear, ask clarifying questions.\n"
                "Be conversational and helpful."
            )
        }
    ]
    
    # Add chat history if provided
    if chat_history:
        messages.extend(chat_history)
    
    # Add current user message
    messages.append({"role": "user", "content": user_text})
    
    # Get tools schema
    tools = _build_tools_schema()
    
    # Call LLM with thinking enabled
    result = provider.generate_with_tools(messages, tools, think=True)
    
    # Parse tool call from response
    tool_calls = result.get("tool_calls", [])
    
    if tool_calls:
        tc = tool_calls[0]  # Use first tool call
        fn = tc.get("function", {})
        name = fn.get("name", "")
        args = json.loads(fn.get("arguments", "{}"))
    else:
        # No tool call - treat as ask_clarify
        name = "ask_clarify"
        args = {"questions": ["Could you please provide more details about what you'd like to do?"]}
    
    # Build ToolCall with explanation
    tool_call = ToolCall(
        name=name,
        params=args,
        explanation=result.get("content", ""),
        thinking=result.get("thinking", "")
    )
    
    # Build RAG info (existing pattern)
    rag_info = {"meta": {"enabled": False}, "sources_used": [], "scores": []}
    
    return tool_call, rag_info
```

4. **Add post-tool summarization function**:
```python
def summarize_tool_result(
    tool_name: str,
    params: dict[str, Any],
    result: dict[str, Any],
    user_text: str
) -> str:
    """
    Generate natural language summary of tool execution result.
    Called after tool execution to explain results to user.
    """
    provider = get_provider()
    
    # Truncate large results
    result_str = json.dumps(result, indent=2, default=str)
    if len(result_str) > 3000:
        result_str = result_str[:3000] + "\n... (truncated for brevity)"
    
    prompt = f"""You just executed a tool for the user. Summarize the result in 2-4 sentences.
Be helpful, clear, and conversational. If there are issues or empty results, explain what that means and suggest next steps.

User's original request: {user_text}

Tool executed: {tool_name}
Parameters used: {json.dumps(params, default=str)}

Result:
{result_str}

Write a clear, helpful summary in natural language. Do NOT output JSON."""
    
    try:
        summary = provider.generate_text(prompt)
        return summary.strip()
    except Exception as e:
        # Fallback if summarization fails
        ok = result.get("ok", False)
        count = result.get("count", result.get("rows", []))
        if isinstance(count, list):
            count = len(count)
        return f"Executed {tool_name}. {'Success' if ok else 'Failed'}. Found {count} results." if count else f"Executed {tool_name}. {'Success' if ok else 'Failed'}."
```

#### 3.2.3 Chat Panel UI Enhancement

**File**: `dashboard/chat_panel.py`

**Changes Required**:

1. **Update message rendering to show natural language + JSON expander**:
```python
def render_chat_panel(base_dir: str) -> None:
    # ... existing setup code ...
    
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            # Display natural language content
            st.markdown(msg["content"])
            
            # Display thinking/reasoning in collapsible (optional)
            thinking = msg.get("thinking")
            if thinking:
                with st.expander("Show reasoning", expanded=False):
                    st.text(thinking)
            
            # Display tool result JSON in collapsible
            tool_result = msg.get("tool_result")
            if tool_result is not None:
                with st.expander("Technical details (JSON)", expanded=False):
                    st.json(_truncate_value(tool_result))
```

2. **Update tool execution flow**:
```python
    # ... after user input ...
    
    # Use new conversational planning
    from control_plane.chat_orchestrator import (
        plan_tool_call_conversational,
        summarize_tool_result,
    )
    
    tool_call, rag_info = plan_tool_call_conversational(user_input, Path(base_dir))
    
    # Show LLM's explanation BEFORE executing
    if tool_call.explanation:
        st.session_state["chat_messages"].append({
            "role": "assistant",
            "content": tool_call.explanation,
            "thinking": tool_call.thinking,
            "tool_result": None
        })
    
    # Execute tool
    result = execute_tool_call(tool_call, Path(base_dir))
    audit_tool_call(user_input, tool_call, result, rag_info)
    
    # Generate natural language summary of result
    summary = summarize_tool_result(
        tool_call.name, 
        tool_call.params, 
        result, 
        user_input
    )
    
    # Append summary with JSON in expander
    st.session_state["chat_messages"].append({
        "role": "assistant",
        "content": summary,
        "thinking": None,
        "tool_result": result
    })
```

### 3.3 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           USER INTERACTION FLOW                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. USER TYPES: "Show me products with ROI over 30% for poundwholesale" │
│                                    │                                     │
│                                    ▼                                     │
│  2. STREAMLIT captures input in st.chat_input()                         │
│                                    │                                     │
│                                    ▼                                     │
│  3. plan_tool_call_conversational() called                              │
│     ├── Builds messages array with system + user content                │
│     ├── Calls Ollama with think=True, tools=[...]                       │
│     └── Returns ToolCall(name, params, explanation, thinking)           │
│                                    │                                     │
│                                    ▼                                     │
│  4. DISPLAY EXPLANATION (Before Execution)                              │
│     "I'll search for products from poundwholesale.co.uk with ROI       │
│      greater than 30%. Let me query the financial data..."              │
│                                    │                                     │
│                                    ▼                                     │
│  5. execute_tool_call() runs deterministic Python function              │
│     └── Returns JSON: {"ok": true, "count": 15, "rows": [...]}         │
│                                    │                                     │
│                                    ▼                                     │
│  6. summarize_tool_result() generates natural language summary          │
│     └── "I found 15 products matching your criteria. The top           │
│          product has an ROI of 45% with estimated profit of £12.50."   │
│                                    │                                     │
│                                    ▼                                     │
│  7. DISPLAY TO USER:                                                    │
│     ┌─────────────────────────────────────────────────────────┐        │
│     │ 🤖 Assistant                                            │        │
│     │                                                         │        │
│     │ I found 15 products matching your criteria. The top    │        │
│     │ product has an ROI of 45% with estimated profit of     │        │
│     │ £12.50. Here are the results...                        │        │
│     │                                                         │        │
│     │ ▶ Technical details (JSON)                             │        │
│     │   └── {"ok": true, "count": 15, "rows": [...]}         │        │
│     └─────────────────────────────────────────────────────────┘        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Implementation Plan

### 4.1 Task Breakdown

| Task ID | Task | File(s) | Category | Skills | Est. Time |
|---------|------|---------|----------|--------|-----------|
| T1 | Add `generate_with_tools()` to OllamaProvider | `control_plane/llm/providers.py` | quick | - | 15 min |
| T2 | Add `generate_text()` to OllamaProvider | `control_plane/llm/providers.py` | quick | - | 10 min |
| T3 | Update ToolCall dataclass | `control_plane/chat_orchestrator.py` | quick | - | 5 min |
| T4 | Add `_build_tools_schema()` function | `control_plane/chat_orchestrator.py` | quick | - | 20 min |
| T5 | Add `plan_tool_call_conversational()` | `control_plane/chat_orchestrator.py` | quick | - | 30 min |
| T6 | Add `summarize_tool_result()` | `control_plane/chat_orchestrator.py` | quick | - | 15 min |
| T7 | Update chat_panel.py message rendering | `dashboard/chat_panel.py` | visual-engineering | frontend-ui-ux | 20 min |
| T8 | Update chat_panel.py tool execution flow | `dashboard/chat_panel.py` | quick | - | 25 min |
| T9 | Add backward compatibility checks | Multiple | quick | - | 15 min |
| T10 | Integration testing | - | quick | - | 30 min |

**Total Estimated Time**: ~3 hours

### 4.2 Implementation Order

```
Phase 1: Provider Layer (T1, T2)
    │
    ▼
Phase 2: Orchestrator Layer (T3, T4, T5, T6)
    │
    ▼
Phase 3: UI Layer (T7, T8)
    │
    ▼
Phase 4: Integration & Testing (T9, T10)
```

### 4.3 Detailed Task Specifications

#### T1: Add `generate_with_tools()` to OllamaProvider

**File**: `control_plane/llm/providers.py`

**Location**: After existing `generate_json()` method in `OllamaProvider` class

**Code to Add**:
```python
def generate_with_tools(
    self, 
    messages: list[dict[str, Any]], 
    tools: list[dict[str, Any]],
    think: bool = True
) -> dict[str, Any]:
    """
    Generate response using Ollama's native tool calling with optional thinking.
    
    Args:
        messages: List of chat messages [{"role": "...", "content": "..."}]
        tools: List of tool schemas in Ollama format
        think: Enable thinking/reasoning mode (default True)
    
    Returns:
        Dict with keys: content, thinking, tool_calls
    """
    import requests
    
    url = self.base_url.rstrip("/") + "/api/chat"
    payload = {
        "model": self.model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.3},
    }
    
    if tools:
        payload["tools"] = tools
    
    if think:
        payload["think"] = True
    
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    
    msg = data.get("message", {})
    
    # Parse tool_calls if present
    raw_tool_calls = msg.get("tool_calls", [])
    tool_calls = []
    for tc in raw_tool_calls:
        fn = tc.get("function", {})
        tool_calls.append({
            "name": fn.get("name", ""),
            "arguments": fn.get("arguments", "{}")
        })
    
    return {
        "content": msg.get("content", ""),
        "thinking": msg.get("thinking", ""),
        "tool_calls": tool_calls,
    }
```

#### T2: Add `generate_text()` to OllamaProvider

**File**: `control_plane/llm/providers.py`

**Location**: After `generate_with_tools()` method

**Code to Add**:
```python
def generate_text(self, prompt: str) -> str:
    """
    Generate natural language text without JSON formatting.
    Used for post-tool summarization.
    
    Args:
        prompt: The prompt to send to the LLM
    
    Returns:
        Natural language string response
    """
    import requests
    
    url = self.base_url.rstrip("/") + "/api/generate"
    resp = requests.post(
        url,
        json={
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3},
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("response", "")
```

#### T3: Update ToolCall dataclass

**File**: `control_plane/chat_orchestrator.py`

**Current** (line ~59-62):
```python
@dataclass(frozen=True)
class ToolCall:
    name: str
    params: dict[str, Any]
```

**New**:
```python
@dataclass(frozen=True)
class ToolCall:
    name: str
    params: dict[str, Any]
    explanation: str = ""
    thinking: str = ""
```

#### T4-T6: See Section 3.2.2 for full code

---

## 5. Test Plan

### 5.1 Unit Tests

| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| UT1 | `generate_with_tools()` returns all three fields | Dict has content, thinking, tool_calls |
| UT2 | `generate_text()` returns string | Non-empty string response |
| UT3 | `ToolCall` accepts explanation field | Dataclass instantiates correctly |
| UT4 | `summarize_tool_result()` handles empty result | Returns fallback message |
| UT5 | `summarize_tool_result()` handles large result | Truncates and summarizes |

### 5.2 Integration Tests

| Test ID | Scenario | Steps | Expected |
|---------|----------|-------|----------|
| IT1 | Simple query | User asks "show status" | Natural language response + JSON expander |
| IT2 | Ambiguous query | User asks "analyze" | Clarifying questions in prose |
| IT3 | Financial query | User asks "products with ROI > 30%" | Explanation + results summary |
| IT4 | Missing supplier | User asks "show products" without supplier | Prompts for supplier naturally |

### 5.3 Manual Verification Checklist

- [ ] Chat UI loads without errors
- [ ] User can type natural language
- [ ] LLM returns explanation before tool execution
- [ ] Tool executes correctly (same as before)
- [ ] Summary appears after execution
- [ ] JSON expandable shows raw result
- [ ] Clarifying questions are conversational
- [ ] No regression in existing functionality

---

## 6. Rollback Strategy

### 6.1 Backup Before Implementation

```bash
# Create backup directory
mkdir -p SYSTEM_CHAT_UI_PRDS/backups/prd03_natural_language_20260128

# Backup files to be modified
cp control_plane/llm/providers.py SYSTEM_CHAT_UI_PRDS/backups/prd03_natural_language_20260128/
cp control_plane/chat_orchestrator.py SYSTEM_CHAT_UI_PRDS/backups/prd03_natural_language_20260128/
cp dashboard/chat_panel.py SYSTEM_CHAT_UI_PRDS/backups/prd03_natural_language_20260128/
```

### 6.2 Rollback Procedure

If issues occur:
1. Stop Streamlit dashboard
2. Copy backup files back to original locations
3. Restart dashboard
4. Verify original behavior restored

### 6.3 Feature Flag (Optional)

Add environment variable to toggle new behavior:
```python
USE_CONVERSATIONAL_MODE = os.environ.get("CHAT_CONVERSATIONAL_MODE", "true").lower() == "true"

if USE_CONVERSATIONAL_MODE:
    tool_call, rag_info = plan_tool_call_conversational(user_input, repo_root)
else:
    tool_call, rag_info = plan_tool_call(user_input, repo_root)  # Original
```

---

## 7. Success Criteria

### 7.1 Functional Requirements

| ID | Requirement | Verification |
|----|-------------|--------------|
| FR1 | Natural language explanations appear before tool execution | Visual inspection |
| FR2 | Natural language summaries appear after tool execution | Visual inspection |
| FR3 | Raw JSON available in expandable section | Click expander, verify JSON |
| FR4 | Clarifying questions use natural language | Test ambiguous query |
| FR5 | All existing tools continue to work | Run each tool type |

### 7.2 Non-Functional Requirements

| ID | Requirement | Target | Verification |
|----|-------------|--------|--------------|
| NFR1 | Response latency | < 10s for explanation + execution + summary | Stopwatch |
| NFR2 | No breaking changes | 0 test failures | Run test suite |
| NFR3 | Backward compatibility | Old ToolCall usage still works | Compile check |

### 7.3 User Experience Criteria

| ID | Criteria | Verification |
|----|----------|--------------|
| UX1 | User understands what action will be taken | Read explanation before execution |
| UX2 | User understands what happened | Read summary after execution |
| UX3 | Technical users can access raw data | JSON expander works |
| UX4 | Conversation feels natural | Subjective evaluation |

---

## 8. Appendix

### 8.1 Ollama API Reference

**Chat Endpoint with Tools**:
```bash
POST http://localhost:11434/api/chat
{
  "model": "qwen3",
  "messages": [...],
  "tools": [...],
  "think": true,
  "stream": false
}
```

**Response Structure**:
```json
{
  "message": {
    "role": "assistant",
    "content": "Natural language explanation",
    "thinking": "Internal reasoning trace",
    "tool_calls": [
      {
        "function": {
          "name": "tool_name",
          "arguments": "{\"param\": \"value\"}"
        }
      }
    ]
  }
}
```

### 8.2 Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `CONTROL_PLANE_LLM_PROVIDER` | LLM provider type | `ollama` |
| `CONTROL_PLANE_OLLAMA_BASE_URL` | Ollama API URL | `http://localhost:11434` |
| `CONTROL_PLANE_OLLAMA_MODEL` | Model to use | `qwen3` |
| `CHAT_CONVERSATIONAL_MODE` | Enable new mode | `true` |

### 8.3 File Change Summary

| File | Lines Added | Lines Modified | Lines Removed |
|------|-------------|----------------|---------------|
| `control_plane/llm/providers.py` | ~60 | 0 | 0 |
| `control_plane/chat_orchestrator.py` | ~150 | ~5 | 0 |
| `dashboard/chat_panel.py` | ~30 | ~20 | ~5 |

---

## 9. Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | System Architect | 2026-01-28 | ✓ |
| Reviewer | - | - | - |
| Approver | User | - | - |

---

**END OF PRD**
