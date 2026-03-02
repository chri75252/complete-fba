# Issues

## 2026-02-18
- LSP diagnostics tool cannot run for Python in this environment because `basedpyright-langserver` is not installed.
- `bun run build` script is not defined in this repository (`error: Script not found "build"`).
- `bun test` finds zero test files; Python-focused verification is required for code tasks.

## 2026-02-18 (Task 9)
- Reconfirmed: `lsp_diagnostics` fails for Python due to missing `basedpyright-langserver`; relied on `py_compile` verification.
