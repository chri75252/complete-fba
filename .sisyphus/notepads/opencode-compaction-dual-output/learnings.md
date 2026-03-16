# Learnings - opencode-compaction-dual-output

Created: 2026-03-13

- 
[2026-03-13] Backed up config files to C:\Users\chris\.config\opencode\backup\compaction_dual_output_20260313\ before starting compaction work. 
Added local OpenCode plugin 'compaction-dual-output.js' to ensure dual-output directives are preserved during compaction cycles. 
- [2026-03-13] Enabled preemptive compaction in oh-my-opencode.json by adding "experimental": { "preemptive_compaction": true } at the top-level.
[2026-03-13] Patched opencode.json to add compaction config (auto: true, prune: true, reserved: 20000) for dual-output support. 
- [compaction-dual-output:v1] Plugins must export a function (not a plain object) and use (input, output) signature for experimental.session.compacting to avoid breaking default prompt logic. 
- [2026-03-13] Fixed 'compaction-dual-output.js' to return the correct OpenCode Plugin interface (hook keys at top-level, not nested under 'hooks'). Updated directive to use explicit '##' headings for Goal, Instructions, Discoveries, Accomplished, Relevant files / directories, and Handoff Addendum. 
