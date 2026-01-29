@echo off
setlocal

REM Repo root = folder containing this BAT
set "REPO=%~dp0"

REM Normalize (strip trailing backslash for pushd safety)
if "%REPO:~-1%"=="\" set "REPO=%REPO:~0,-1%"

REM Terminal 1: Control-plane worker
start "FBA Control Plane Worker" cmd.exe /k pushd /d "%REPO%" ^&^& echo REPO=%REPO% ^&^& python -m control_plane worker

REM Terminal 2: Set env vars + Start Dashboard
start "FBA Dashboard OperatorChat" cmd.exe /k pushd /d "%REPO%" ^&^& set "CONTROL_PLANE_LLM_PROVIDER=ollama" ^&^& set "CONTROL_PLANE_LLM_BASE_URL=http://localhost:11434" ^&^& set "CONTROL_PLANE_LLM_MODEL=deepseek-r1:7b" ^&^& set "CONTROL_PLANE_OLLAMA_BASE_URL=http://localhost:11434" ^&^& set "CONTROL_PLANE_OLLAMA_MODEL=deepseek-r1:7b" ^&^& echo CONTROL_PLANE_LLM_PROVIDER=%CONTROL_PLANE_LLM_PROVIDER% ^&^& echo CONTROL_PLANE_OLLAMA_MODEL=%CONTROL_PLANE_OLLAMA_MODEL% ^&^& python dashboard\run_dashboard.py

endlocal

