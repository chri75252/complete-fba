## [2026-03-08] Relaxed Planner ID Recall Rules  
- Relaxed Rule 13 in `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` to explicitly allow using IDs and paths from chat history.  
- Clarified that using information from history is NOT "guessing".  
- This helps the LLM be less cautious about using IDs it sees in the history, which was a known issue. 
  
## [2026-03-08] High-Fidelity Pruning Logic  
- Implemented _prune_value helper in control_plane/chat_orchestrator.py to recursively prune large nested structures in tool_result.  
- Replaced the restrictive whitelist-based stripping in _sanitize_chat_history with the recursive pruning model.  
- This preserves all dictionary keys (preventing "agent amnesia" for keys like rel_path) while truncating large lists (max 10 items) and strings (max 1000 chars).  
- This ensures structural awareness of paths and IDs is maintained within the LLM's context window. 
