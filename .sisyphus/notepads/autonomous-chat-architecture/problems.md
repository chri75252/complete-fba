## 2026-03-02 - Open problems

- Need a robust strategy for long-running autonomous reasoning that avoids Streamlit UI freeze while still maintaining deterministic, inspectable state.
- Need a standard event schema for per-step trace entries so thought updates, tool params, tool results, and approval boundaries can be rendered consistently.
- Need explicit failure policy (invalid JSON loops, repeated same tool, and no-progress cycles) that exits safely with a user-visible explanation.
