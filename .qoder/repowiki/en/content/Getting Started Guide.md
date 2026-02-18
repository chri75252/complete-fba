# Getting Started Guide

<cite>
**Referenced Files in This Document**
- [docs/CONCISE_LAUNCH_GUIDE.md](file://docs/CONCISE_LAUNCH_GUIDE.md)
- [SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md](file://SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md)
- [SYSTEM_CHAT_UI_PRDS/LOCAL_LLM_SERENA_MCP_INTEGRATION_GUIDE.md](file://SYSTEM_CHAT_UI_PRDS/LOCAL_LLM_SERENA_MCP_INTEGRATION_GUIDE.md)
- [control_plane/__main__.py](file://control_plane/__main__.py)
- [control_plane/worker.py](file://control_plane/worker.py)
- [control_plane/env_config.py](file://control_plane/env_config.py)
- [dashboard/run_dashboard.py](file://dashboard/run_dashboard.py)
- [run_custom_angelwholesale-co-uk.py](file://run_custom_angelwholesale-co-uk.py)
- [requirements.txt](file://requirements.txt)
- [config/system_config.json](file://config/system_config.json)
- [utils/browser_manager.py](file://utils/browser_manager.py)
- [utils/windows_save_guardian.py](file://utils/windows_save_guardian.py)
</cite>

## Update Summary
**Changes Made**
- Updated to reflect new concise launch guide optimized for Windows CMD environments
- Added detailed setup instructions for local Ollama deployment using qwen3:8b-q4_K_M models
- Included three-terminal startup procedures for dashboard, worker, and optional health checks
- Added comprehensive Chrome debugging setup instructions
- Updated environment variable configuration for Ollama integration
- Enhanced verification steps for successful system validation

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [One-time Setup](#one-time-setup)
4. [Three-Terminal Startup Procedure](#three-terminal-startup-procedure)
5. [Environment Configuration](#environment-configuration)
6. [Initial System Validation](#initial-system-validation)
7. [Chat UI and Control Plane Integration](#chat-ui-and-control-plane-integration)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Verification Procedures](#verification-procedures)
10. [Conclusion](#conclusion)

## Introduction
This Getting Started Guide provides comprehensive instructions for deploying the Amazon FBA Agent System with a focus on Windows CMD environments and local Ollama deployment. The system now uses a streamlined three-terminal startup procedure with qwen3:8b-q4_K_M models for optimal performance and resource efficiency.

**Updated** New concise launch guide optimized for Windows CMD environments with local Ollama deployment using qwen3:8b-q4_K_M models, replacing the previous Windows PowerShell and Linux/WSL configurations.

## Prerequisites
The system requires the following components for successful deployment:

### Hardware Requirements
- **CPU**: Intel i9-12900H or equivalent (powerful processor)
- **RAM**: 34.6GB free (abundant memory capacity)
- **GPU**: RTX 3070 Ti with 7.7GB free VRAM (excellent for local LLM inference)
- **Storage**: Sufficient space for model downloads and processing data

### Software Requirements
- **Windows 10/11** (optimized for CMD environment)
- **Python 3.8+** (recommended: 3.12+)
- **Google Chrome** (version supporting CDP 9222)
- **Ollama** (local LLM server)
- **Git** (for repository cloning)

### Model Requirements
- **Qwen3 8B**: qwen3:8b-q4_K_M (~4.8GB VRAM requirement)
- **Alternative**: DeepSeek-R1:7B (for supplier onboarding reasoning)
- **Optional**: Ministral 3B (ultra-efficient option at 2GB VRAM)

**Section sources**
- [SYSTEM_CHAT_UI_PRDS/LOCAL_LLM_SERENA_MCP_INTEGRATION_GUIDE.md](file://SYSTEM_CHAT_UI_PRDS/LOCAL_LLM_SERENA_MCP_INTEGRATION_GUIDE.md#L787-L810)
- [docs/CONCISE_LAUNCH_GUIDE.md](file://docs/CONCISE_LAUNCH_GUIDE.md#L216-L247)

## One-time Setup

### Chrome Debugging Setup
Launch a dedicated Chrome instance with remote debugging enabled for persistent automation:

```bat
mkdir C:\ChromeDebugProfile_FBA_9222
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=9222 ^
  --remote-debugging-address=127.0.0.1 ^
  --user-data-dir="C:\ChromeDebugProfile_FBA_9222" ^
  --no-first-run --no-default-browser-check
```

**Notes**:
- Install Keepa/SellerAmp extensions into this profile once
- Use the debug Chrome window launched with `--user-data-dir`, not your normal Chrome
- This establishes the persistent Chrome instance required for CDP automation

### Ollama Server Setup
Start the local LLM server with the recommended qwen3:8b-q4_K_M model:

```bat
ollama run qwen3:8b-q4_K_M
```

**Important**: Keep this terminal running continuously as it provides the "brain" for the Chat and Operator features.

**Section sources**
- [docs/CONCISE_LAUNCH_GUIDE.md](file://docs/CONCISE_LAUNCH_GUIDE.md#L15-L38)
- [SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md](file://SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md#L15-L38)

## Three-Terminal Startup Procedure

### Terminal 1: Dashboard (UI)
Start the Streamlit dashboard with Ollama integration:

```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
set "CONTROL_PLANE_LLM_PROVIDER=ollama"
set "CONTROL_PLANE_LLM_BASE_URL=http://localhost:11434"
set "CONTROL_PLANE_LLM_MODEL=qwen3:8b-q4_K_M"
set "CONTROL_PLANE_OLLAMA_BASE_URL=http://localhost:11434"
set "CONTROL_PLANE_OLLAMA_MODEL=qwen3:8b-q4_K_M"
python dashboard\run_dashboard.py
```

**Access**: Open `http://localhost:8501` in your browser

### Terminal 2: Worker (Executes Jobs)
Start the control plane worker that processes queued jobs:

```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python -m control_plane worker
```

**Important**: The worker must be running for any chat-initiated operations to execute.

### Terminal 3: Optional Health Checks
Monitor system health and connectivity:

```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
curl http://localhost:9222/json/version
curl http://localhost:11434/api/tags
```

**Expected Responses**:
- Chrome CDP: JSON with `Browser` and `Protocol-Version` fields
- Ollama: JSON with `models` array containing `qwen3:8b-q4_K_M`

**Section sources**
- [docs/CONCISE_LAUNCH_GUIDE.md](file://docs/CONCISE_LAUNCH_GUIDE.md#L38-L70)
- [SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md](file://SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md#L41-L72)

## Environment Configuration

### Control Plane Environment Variables
The system uses a centralized environment configuration system managed by `env_config.py`:

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `CONTROL_PLANE_LLM_PROVIDER` | LLM provider type | `ollama` | `ollama`, `opencode`, `lmstudio` |
| `CONTROL_PLANE_LLM_BASE_URL` | LLM API endpoint | `http://localhost:11434` | `http://localhost:11434` |
| `CONTROL_PLANE_LLM_MODEL` | Primary model name | `qwen3` | `qwen3:8b-q4_K_M` |
| `CONTROL_PLANE_OLLAMA_BASE_URL` | Ollama API URL | `http://localhost:11434` | `http://localhost:11434` |
| `CONTROL_PLANE_OLLAMA_MODEL` | Ollama model name | `qwen3` | `qwen3:8b-q4_K_M` |

### Environment Configuration Flow
The `ensure_llm_env()` function in `env_config.py` automatically harmonizes provider-specific variables:

```python
def ensure_llm_env() -> None:
    provider_raw = os.environ.get("CONTROL_PLANE_LLM_PROVIDER")
    provider = (_clean(provider_raw) or "none").lower()
    
    # Auto-synchronize Ollama variables
    if provider in {"ollama", "lmstudio"}:
        if ollama_base and not llm_base:
            os.environ["CONTROL_PLANE_LLM_BASE_URL"] = ollama_base
        if llm_base and not ollama_base:
            os.environ["CONTROL_PLANE_OLLAMA_BASE_URL"] = llm_base
        if ollama_model and not llm_model:
            os.environ["CONTROL_PLANE_LLM_MODEL"] = ollama_model
        if llm_model and not ollama_model:
            os.environ["CONTROL_PLANE_OLLAMA_MODEL"] = llm_model
```

**Section sources**
- [control_plane/env_config.py](file://control_plane/env_config.py#L26-L51)
- [docs/CONCISE_LAUNCH_GUIDE.md](file://docs/CONCISE_LAUNCH_GUIDE.md#L44-L48)

## Initial System Validation

### Basic Connectivity Tests
Verify all system components are accessible:

```bat
REM Test Chrome CDP connectivity
curl http://localhost:9222/json/version

REM Test Ollama server
curl http://localhost:11434/api/tags

REM Test Streamlit dashboard
curl http://localhost:8501
```

### Dashboard Verification
- Open `http://localhost:8501` in browser
- Verify Chat tab shows `'ollama'` in sidebar
- Confirm Operator tab recognizes `angelwholesale.co.uk` runs
- Note: "Linking map not found" messages are expected for new suppliers

### Worker Status Check
Monitor the worker process:
```bat
tasklist | findstr python
```

**Expected**: Multiple python.exe processes (dashboard + worker)

**Section sources**
- [docs/CONCISE_LAUNCH_GUIDE.md](file://docs/CONCISE_LAUNCH_GUIDE.md#L50-L56)
- [SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md](file://SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md#L190-L199)

## Chat UI and Control Plane Integration

### How the Chat System Works
The integrated chat UI operates on a tool-call architecture:

1. **Intent Analysis**: Natural language queries are parsed by the local LLM
2. **Tool Proposal**: The system proposes appropriate tools for execution
3. **Confirmation Required**: Write operations require explicit user confirmation
4. **Job Queueing**: Confirmed actions are queued as control plane jobs
5. **Worker Execution**: The worker processes queued jobs asynchronously

### Control Plane Operations
The control plane manages job lifecycle through standardized directories:

```bat
REM Job queue locations
OUTPUTS\CONTROL_PLANE\jobs\pending\
OUTPUTS\CONTROL_PLANE\jobs\running\
OUTPUTS\CONTROL_PLANE\jobs\done\
OUTPUTS\CONTROL_PLANE\jobs\failed\
```

### Supported Operations
- **Category Analysis**: Analyze supplier categories with multiple URLs
- **Product List Refresh**: Process product lists from JSON files
- **Status Monitoring**: Track run progress and retrieve logs
- **Supplier Onboarding**: Execute supplier-specific workflows

**Section sources**
- [SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md](file://SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md#L75-L89)
- [docs/CONCISE_LAUNCH_GUIDE.md](file://docs/CONCISE_LAUNCH_GUIDE.md#L72-L87)

## Troubleshooting Guide

### Common Issues and Solutions

#### Chrome Debug Port Issues
**Problem**: Chrome CDP not accessible
**Solution**:
1. Kill all Chrome instances: `taskkill /F /IM chrome.exe /T`
2. Restart debug Chrome with correct parameters
3. Verify connectivity: `curl http://localhost:9222/json/version`

#### Ollama Server Problems
**Problem**: Ollama not responding
**Solution**:
1. Verify model is loaded: `ollama list`
2. Check server status: `ollama serve`
3. Restart Ollama service if needed

#### Worker Lock Issues
**Problem**: Jobs queue but never start
**Solution**:
1. Check for stale lock: `dir OUTPUTS\CONTROL_PLANE\lock`
2. Safe reset if worker is NOT running:
   ```bat
   rename "OUTPUTS\CONTROL_PLANE\lock\active_run.lock" "active_run.lock.bak_02-02-26_manual"
   python -m control_plane worker
   ```

#### Model Availability Issues
**Problem**: qwen3:8b-q4_K_M not found
**Solution**:
```bat
ollama pull qwen3:8b-q4_K_M
```

**Section sources**
- [SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md](file://SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md#L144-L198)
- [docs/CONCISE_LAUNCH_GUIDE.md](file://docs/CONCISE_LAUNCH_GUIDE.md#L152-L196)

## Verification Procedures

### Comprehensive Success Verification
Follow this step-by-step verification for your first real run:

#### Pre-Run Checklist
1. **Chrome CDP Accessible** (3 sources):
   ```bat
   curl http://localhost:9222/json/version
   ```
   Expected: JSON with `Browser` and `Protocol-Version` fields

2. **Ollama Server Running** (3 sources):
   ```bat
   curl http://localhost:11434/api/tags
   ```
   Expected: JSON with `models` array containing your model

3. **Dashboard Accessible** (3 sources):
   ```bat
   curl http://localhost:8501
   ```
   Expected: HTML response (Streamlit UI)

4. **Worker Process Running** (3 sources):
   ```bat
   tasklist | findstr python
   ```
   Expected: Multiple python.exe processes

5. **Control Plane Directories Exist** (3 sources):
   ```bat
   dir OUTPUTS\CONTROL_PLANE\jobs
   dir OUTPUTS\CONTROL_PLANE\status
   dir OUTPUTS\CONTROL_PLANE\logs
   ```

#### Job Lifecycle Verification
1. **Job Creation**: After confirming chat actions, verify job JSON:
   ```bat
   dir OUTPUTS\CONTROL_PLANE\jobs\pending /b
   type OUTPUTS\CONTROL_PLANE\jobs\pending\job_<run_id>.json
   ```

2. **Status Updates**: Monitor status transitions:
   ```bat
   REM Check status file existence
   if exist OUTPUTS\CONTROL_PLANE\status\<run_id>.json (
       echo Status file exists
       type OUTPUTS\CONTROL_PLANE\status\<run_id>.json
   )
   ```

3. **Processing State**: Verify state file creation:
   ```bat
   dir OUTPUTS\CACHE\processing_states\*sandbox*processing_state.json /b
   ```

4. **Linking Map**: Confirm Amazon matching:
   ```bat
   dir OUTPUTS\FBA_ANALYSIS\linking_maps\ /b
   python -c "import json; lm=json.load(open('OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/linking_map.json')); print(f'Entries: {len(lm)}'); matched = sum(1 for v in lm.values() if v.get('amazon_asin')); print(f'Matched: {matched}')"
   ```

**Section sources**
- [docs/CONCISE_LAUNCH_GUIDE.md](file://docs/CONCISE_LAUNCH_GUIDE.md#L265-L507)
- [SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md](file://SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md#L190-L213)

## Conclusion
The Amazon FBA Agent System now provides an optimized Windows CMD deployment experience with local Ollama integration. The three-terminal startup procedure ensures reliable operation with qwen3:8b-q4_K_M models, while the integrated chat UI enables intuitive operator interaction through deterministic tool execution with confirmation gating.

Key advantages of this setup:
- **Windows-optimized**: CMD-only environment eliminates PowerShell dependencies
- **Local LLM**: Complete offline operation with qwen3:8b-q4_K_M (~4.8GB VRAM)
- **Streamlined**: Three-terminal architecture with clear separation of concerns
- **Reliable**: Robust error handling and recovery mechanisms
- **Verifiable**: Comprehensive validation procedures for successful deployment

**Section sources**
- [docs/CONCISE_LAUNCH_GUIDE.md](file://docs/CONCISE_LAUNCH_GUIDE.md#L1-L11)
- [SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md](file://SYSTEM_CHAT_UI_PRDS/CONCISE_LAUNCH_GUIDE.md#L1-L11)