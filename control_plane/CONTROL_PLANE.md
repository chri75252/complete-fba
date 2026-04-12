# Control Plane

**Location:** `control_plane/`

## Overview

The control plane handles job orchestration, AI-powered chat interactions, and system coordination. It bridges the dashboard with the core workflow engine.

---

## Directory Structure

```
control_plane/
├── chat_orchestrator.py        # AI chat interface
├── worker.py                   # Job execution engine
├── job_manager.py              # Job queue management
├── run_product_list_refresh.py # Product refresh workflow
├── paths.py                    # Centralized path resolution
├── rag_index.py                # RAG context indexing
├── rag_retriever.py            # RAG retrieval
├── rag_retrieval.py            # RAG utilities
├── financial_query.py           # Financial data queries
├── build_index.py              # Index builder
├── audit.py                    # Audit logging
├── checklists.py               # Checklist management
├── constants.py                # Constants
├── config_merger.py           # Config merging
├── env_config.py              # Environment config
├── json_io.py                 # JSON utilities
├── llm_parser.py               # LLM output parsing
├── llm_provider.py             # LLM provider
├── normalize.py               # Normalization utilities
├── rd2_policy.py              # RD2 policy enforcement
├── status_reader.py            # Status reading
├── __main__.py               # CLI entry point
├── __init__.py
├── internal/
│   ├── file_io.py
│   └── path_resolver.py
├── llm/
│   ├── __init__.py
│   ├── parser.py
│   └── providers.py
├── schemas/
│   ├── __init__.py
│   └── models.py
└── tools/
    ├── __init__.py
    ├── amazon_cache.py
    ├── cached_products.py
    ├── check_sandbox_manifest.py
    ├── clarify.py
    ├── financial.py
    ├── jobs.py
    ├── linking_map.py
    ├── logs.py
    ├── output_writer.py
    ├── product_list_builder.py
    ├── product_list_refresh.py
    ├── repo_files.py
    ├── run_outputs.py
    ├── run_validation.py
    ├── state.py
    ├── status.py
    ├── tool_param_validation.py
    └── trace.py
```

---

## Core Components

### 1. Chat Orchestrator

**Location:** `control_plane/chat_orchestrator.py`

**Purpose:** Handles AI-powered chat interactions with the system

**Capabilities:**
- Natural language queries about products
- Job submission via chat
- Run status queries
- Financial analysis requests
- Supplier-specific queries

**Key Methods:**
```python
async def chat_send(message: str, context: dict) -> ChatResponse:
    # Process user message, route to appropriate handler
    
async def chat_history() -> list[Message]:
    # Return conversation history
    
async def chat_reset():
    # Clear conversation context
```

### 2. Worker

**Location:** `control_plane/worker.py`

**Purpose:** Executes jobs asynchronously

**Job Types:**
| Job | Description |
|-----|-------------|
| `category_run` | Full category-based extraction |
| `product_list_refresh` | Product list refresh workflow |
| `ai_chat` | AI chat processing |

**Key Methods:**
```python
async def execute_job(job: Job) -> JobResult:
    # Execute job and return result
    
async def cancel_job(job_id: str) -> bool:
    # Cancel running job
    
def get_job_status(job_id: str) -> JobStatus:
    # Get current job status
```

### 3. Job Manager

**Location:** `control_plane/job_manager.py`

**Purpose:** Manages job queue and scheduling

**Features:**
- Job queue with priority
- Job state tracking
- Cancellation support
- Progress callbacks

---

## Job Types

### Category Run
```python
{
    "type": "category_run",
    "supplier": "poundwholesale.co.uk",
    "run_id": "uuid-here",
    "options": {
        "max_products": 1000,
        "resume": True
    }
}
```

### Product List Refresh
```python
{
    "type": "product_list_refresh",
    "supplier": "poundwholesale.co.uk",
    "product_urls": ["https://..."],
    "run_id": "uuid-here"
}
```

### AI Chat
```python
{
    "type": "ai_chat",
    "query": "Find products with ROI > 100%",
    "context": {
        "supplier": "poundwholesale.co.uk"
    }
}
```

---

## Path Resolution

**Location:** `control_plane/paths.py`

**Purpose:** Centralized path resolution for all system paths

```python
class ControlPlanePaths:
    @staticmethod
    def get_repo_root() -> Path:
        return Path(__file__).parent.parent
    
    @staticmethod
    def get_output_root() -> Path:
        return ControlPlanePaths.get_repo_root() / "OUTPUTS"
    
    @staticmethod
    def get_linking_map_path(supplier: str, run_id: str = None) -> Path:
        # Returns path based on sandbox vs main
```

---

## RAG (Retrieval Augmented Generation)

### Index Builder

**Location:** `control_plane/rag_index.py`

**Purpose:** Builds searchable index of system knowledge

```python
class RAGIndex:
    def build_index(self, documents: list[Document]):
        # Create embeddings and store
        
    def query(self, query: str, top_k: int = 5) -> list[Document]:
        # Retrieve relevant documents
```

### Retriever

**Location:** `control_plane/rag_retriever.py`

**Purpose:** Retrieves context for AI queries

---

## Tools

### Status Tools

**Location:** `control_plane/tools/status.py`

```python
def get_run_status(supplier: str) -> dict:
    # Returns current run status
    
def get_processing_state(supplier: str) -> dict:
    # Returns processing state file contents
```

### Financial Tools

**Location:** `control_plane/tools/financial.py`

```python
def get_financial_summary(supplier: str) -> dict:
    # Returns summary of financial report
    
def query_products(query: str, filters: dict) -> list[dict]:
    # Query products with filters
```

### Linking Map Tools

**Location:** `control_plane/tools/linking_map.py`

```python
def get_linking_map(supplier: str, run_id: str = None) -> list[dict]:
    # Returns linking map entries
    
def get_match_statistics(supplier: str) -> dict:
    # Returns match rate statistics
```

---

## API Integration

The control plane integrates with the dashboard via `dashboard_v2_redesign/api.py`:

```
Dashboard UI
    │
    ▼
api.py (Flask/Streamlit)
    │
    ▼
Control Plane
    │
    ├──► Chat Orchestrator (AI chat)
    │
    ├──► Worker (Job execution)
    │
    └──► Tools (Data queries)
```

---

## LLM Providers

**Location:** `control_plane/llm/providers.py`

Supported providers:
- OpenAI
- Anthropic (Claude)
- Google (Gemini)
- Local (Ollama)

```python
class LLMProvider:
    async def complete(prompt: str) -> str:
        # Generate completion
        
    async def chat(messages: list[dict]) -> str:
        # Chat completion
```

---

## CLI Entry Point

**Location:** `control_plane/__main__.py`

```bash
# Run a job
python -m control_plane --job category_run --supplier poundwholesale.co.uk

# Check status
python -m control_plane --status

# Start worker
python -m control_plane --worker
```

---

## Audit Logging

**Location:** `control_plane/audit.py`

Logs all control plane operations:
- Job submissions
- Job completions
- Chat interactions
- Errors and failures

---

## Related Files

| File | Location | Purpose |
|------|----------|---------|
| Dashboard API | `dashboard_v2_redesign/api.py` | Dashboard backend |
| Workflow | `tools/passive_extraction_workflow_latest.py` | Core extraction |
| State Manager | `utils/fixed_enhanced_state_manager.py` | State persistence |

---

*Document Version: 1.0*
*Last Updated: 2026-04-11*
