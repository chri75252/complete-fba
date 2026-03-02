## 2026-02-26

- Open question for hardening: whether to permit direct `write_output_file` writes to `OUTPUTS/CONTROL_PLANE/jobs/pending` long-term, or keep job creation exclusively through enqueue tools and only allow pending writes for controlled recovery workflows.
- Open question for completeness: Step 6 in SKILL calls for `py_compile` and connectivity checks; current planner toolset lacks a generic command execution tool, so these checks must be approximated unless a dedicated safe command tool is introduced.
- Open question for policy: decide whether credentials-related onboarding fields should be accepted in chat flows at all, given stricter no-secrets handling preferences.
- Remaining design choice: whether to also allow direct writes to setup/ and temp/ for strict SKILL parity, or keep chat in minimal-safe mode with wizard-input-only generation.
- Remaining design choice: whether to implement a safe command-exec tool for py_compile/CDP checks (Step 6), since current planner toolset cannot execute shell commands directly.

## 2026-02-27

- Open implementation task: decide whether to keep strict one-tool-per-turn UX or add a bounded autonomous chain mode (max steps, allowed tools, stop conditions) for skill workflows.
- Remaining hardening question: current fuzzy normalization strips `.co.uk`, `.com`, and hyphens only; domains with other TLD patterns may need normalization expansion if new suppliers use different suffixes.
