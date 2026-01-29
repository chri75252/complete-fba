@echo off
setlocal
REM Change to repo root (this bat file's directory)
cd /d "%~dp0"
REM ---- Terminal 1: Start Control Plane Worker ----
start "FBA Control Plane Worker" cmd /k ^
"cd /d \"%~dp0\" && python -m control_plane worker"
REM ---- Terminal 2: Set LLM env vars + Start Dashboard ----
start "FBA Dashboard (Operator+Chat)" cmd /k ^
"cd /d \"%~dp0\" && ^
set CONTROL_PLANE_LLM_PROVIDER=ollama && ^
set CONTROL_PLANE_LLM_BASE_URL=http://localhost:11434 && ^
set CONTROL_PLANE_LLM_MODEL=deepseek-r1:7b && ^
set CONTROL_PLANE_OLLAMA_BASE_URL=http://localhost:11434 && ^
set CONTROL_PLANE_OLLAMA_MODEL=deepseek-r1:7b && ^
python dashboard/run_dashboard.py"
endlocal