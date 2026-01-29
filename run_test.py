#!/usr/bin/env python
"""Test script to run FBA Agent v4.3.0 with new implementations."""
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), "src")
sys.path.insert(0, src_path)

from pathlib import Path
from fba_agent.run import run_analysis

if __name__ == "__main__":
    input_file = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\report\part1.xlsx")
    runs_dir = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\runs")
    memory_dir = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\memory")
    
    print("=" * 80)
    print("FBA AGENT v4.3.0 TEST RUN")
    print("=" * 80)
    print(f"Input: {input_file}")
    print(f"Runs Dir: {runs_dir}")
    print(f"Memory Dir: {memory_dir}")
    print("=" * 80)
    
    try:
        result = run_analysis(
            input_path=input_file,
            supplier="test_v43",
            runs_dir=runs_dir,
            memory_dir=memory_dir,
            skip_browser=True,
            overrides_path=None,
            fee_rate=0.15,
            max_iterations=1,  # Single iteration for testing
            enable_ai=True,
            provider_name="openai",  # Use OpenAI (configured in .env)
        )
        
        print("\n" + "=" * 80)
        print("RUN COMPLETED")
        print("=" * 80)
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"\n\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
