# CRITICAL ROOT CAUSE: State File Destroyed at Every Startup

**Date**: October 17, 2025
**Severity**: CRITICAL - Complete State Loss
**Status**: ROOT CAUSE IDENTIFIED

## THE ACTUAL BUG

State file is completely destroyed and recreated with default values during EVERY system startup, BEFORE the code that loads existing state can execute.

## EXECUTION SEQUENCE (THE KILLER)

```
1. run_custom_poundwholesale.py starts
2. PassiveExtractionWorkflow.__init__() called
3. self.state_manager = EnhancedStateManager(supplier_name)
4. [Something in workflow init triggers save_state_atomic()]
5. 💀 DEFAULT STATE WRITTEN TO DISK (24 entries)
   - current_phase = "supplier"
   - persistent_category_index = 1
   - frozen_category_denominators = {}
   - All counters = 0
6. 🔥 OLD STATE FILE DESTROYED
7. Later: initialize_workflow_session() called
8. load_state() reads the default state that was just written
9. "Resumption" from position 1 (actually fresh start)
```

## FORENSIC EVIDENCE

**Log Timestamps (Oct 17, 03:12:08)**:
- `.938` - First ATOMIC SAVE (24 entries) ← WRITES DEFAULT
- `.947` - Second ATOMIC SAVE (24 entries) ← OVERWRITES
- `.951` - Third ATOMIC SAVE (24 entries) ← OVERWRITES
- `.952` - initialize_workflow_session() CALLED ← TOO LATE
- `.953` - load_state() reads destroyed file

**State File Comparison**:
- Before: created_at="2025-10-15T06:17:25", phase="amazon_analysis", denominators={58}
- After: created_at="2025-10-16T23:16:05", phase="supplier", denominators={}
- **New created_at timestamp proves file recreation, not update**

## WHY ALL "FIXES" FAILED

- Fix A (Phase Guard): Works, but state already reset before it can protect
- Fix B (PCI Hardening): Works, but checks flag set after state destroyed
- Fix C (Index Binding): Works, but both inputs are defaults (1,1)
- Fix D (Category Skip): Works perfectly, but PCI always 1 so nothing skips
- Fix E (Observability): Works perfectly, just logging

**All fixes execute AFTER state destruction, so they protect nothing.**

## THE REAL FIX (3 Lines of Code)

**Option A: Block Saves During Initialization**

```python
class EnhancedStateManager:
    def __init__(self, supplier_name: str):
        self._initialization_complete = False  # NEW FLAG

    def save_state_atomic(self, note: str = ""):
        if not self._initialization_complete:
            return  # DON'T SAVE during init

    def initialize_workflow_session(self) -> int:
        # ... load state ...
        self._initialization_complete = True  # ENABLE SAVES
        return start_category_index
```

**Option B: Remove Line 306 Save**

File: `utils/fixed_enhanced_state_manager.py`
Line 306: `self.save_state_atomic()` ← DELETE THIS

**Option C: Fix Workflow Init Order**

Call `initialize_workflow_session()` IMMEDIATELY after creating state_manager, before any other initialization that might trigger saves.

## HISTORICAL IMPACT

**"FRESH START CONTRADICTION" log messages since AUGUST 2025 prove this has been broken for 2+ months.**

Every run has been a hidden fresh start. No successful resumes since August.

## MY FAILURES

1. Verified code without understanding execution sequence
2. Read logs without understanding timing relationships
3. Declared "Production Ready" without execution path analysis
4. Missed August warnings in logs
5. Fixed symptoms instead of finding root cause

## IMMEDIATE ACTION

1. DO NOT RUN until fix deployed
2. Apply Option A (safest - prevents premature saves)
3. Test with interruption
4. Validate PCI/phase/denominators preserved
5. Monitor 10 production runs

---

**This is the REAL bug. Everything else was theater.**
