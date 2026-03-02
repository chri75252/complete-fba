## 2026-03-01 - Open problems / technical debt

- No provider-agnostic API currently exposes model-native chain-of-thought safely; only planner `explanation` is consistently available across providers.
- `get_run_outputs` discovers files but does not itself compute quality metrics (e.g., matched-ASIN ratio), so validation quality depends on follow-up `read_repo_file` calls.
- There is no canonical "validation rubric" embedded in planner instructions yet; behavior may vary by model unless a fixed review prompt template is added in UI.

## 2026-03-01 - Remaining open problems after validator task

- The new validator function is not yet wired into `control_plane/chat_orchestrator.py` tool routing, so chat-side invocation still requires integration work.
- Exception signature matching currently treats benign teardown tracebacks the same as hard run failures; severity classification rules may need refinement.
- If future runs move artifacts to nested sandbox directories, path discovery should be upgraded to recursive dual-read to keep validator accuracy.

## 2026-03-02 - Remaining open problems after triangulation fallback

- LSP diagnostics for Python files are still blocked by missing `basedpyright-langserver` command resolution in the current tool environment, so static diagnostics are not yet enforceable in-session.
