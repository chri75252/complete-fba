# FBA Agent System Launch Guide

## 1. Run Local LLM (Ollama)
Open a fresh terminal and run:
```bash
ollama run deepseek-r1:7b
```
*Note: Keep this terminal open. It provides the "brain" for the Chat and Operator features.*

---

## 2. Launch FBA System (Manual Commands)

### Terminal A: The Worker (Handles Jobs)
**PowerShell**:
```powershell
cd "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python -m control_plane worker
```

**CMD**:
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python -m control_plane worker
```

### Terminal B: The Dashboard (User Interface)
**PowerShell**:
```powershell
cd "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
$env:CONTROL_PLANE_LLM_PROVIDER="ollama"
$env:CONTROL_PLANE_LLM_BASE_URL="http://localhost:11434"
$env:CONTROL_PLANE_LLM_MODEL="deepseek-r1:7b"
$env:CONTROL_PLANE_OLLAMA_BASE_URL="http://localhost:11434"
$env:CONTROL_PLANE_OLLAMA_MODEL="deepseek-r1:7b"
python dashboard\run_dashboard.py
```

**CMD**:
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
set "CONTROL_PLANE_LLM_PROVIDER=ollama"
set "CONTROL_PLANE_LLM_BASE_URL=http://localhost:11434"
set "CONTROL_PLANE_LLM_MODEL=deepseek-r1:7b"
set "CONTROL_PLANE_OLLAMA_BASE_URL=http://localhost:11434"
set "CONTROL_PLANE_OLLAMA_MODEL=deepseek-r1:7b"
python dashboard\run_dashboard.py
```

---

## 3. Verify Success
1. **Chat Tab**: Sidebar should show `'ollama'`.
2. **Operator Tab**: Creating a run for `angelwholesale.co.uk` will now correctly use `run_custom_angelwholesale-co-uk.py`.
3. **Data Loading**: If "Linking map not found" appears, it just means that specific supplier hasn't produced matching data yet.
