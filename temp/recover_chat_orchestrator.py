#!/usr/bin/env python3
"""
Recovery script for control_plane/chat_orchestrator.py
======================================================
This script attempts to reconstruct the chat_orchestrator.py file as it existed
before git restore (around Mar 5, 2026 08:09).

It uses:
1. The most recent backup (chat_orchestrator.py.bak_09-02-26) as the base
2. Applies the modifications from patch_chat.py, patch_chat2.py, patch_chat3.py, patch_chat4.py

Usage: python temp/recover_chat_orchestrator.py
Output: temp/recovered_chat_orchestrator.py
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
BACKUP_FILE = REPO_ROOT / "control_plane" / "chat_orchestrator.py.bak_09-02-26"
OUTPUT_FILE = REPO_ROOT / "temp" / "recovered_chat_orchestrator.py"


def load_base_file() -> str:
    """Load the base backup file."""
    if not BACKUP_FILE.exists():
        print(f"ERROR: Backup file not found: {BACKUP_FILE}")
        sys.exit(1)
    print(f"Loading base file: {BACKUP_FILE}")
    return BACKUP_FILE.read_text(encoding="utf-8")


def apply_patch_chat(text: str) -> str:
    """Apply patch_chat.py modifications."""
    print("Applying patch_chat.py...")
    
    # Fix 1: Exception handling in agent_plan_step
    old_ex_agent = """        except Exception as e:
            if attempt < 2:
                prompt += f"\n\nYour last response was invalid/unparseable JSON ({type(e).__name__}: {e}). Return ONLY valid JSON."
                continue
            data = {"tool": "ask_clarify", "params": {"user_text": user_text, "error": str(e)}}"""

    new_ex_agent = """        except Exception as e:
            if attempt < 2:
                prompt += f"\n\nYour last response was invalid/unparseable JSON ({type(e).__name__}: {e}). Return ONLY valid JSON."
                continue
            # If the provider hard-fails (e.g. 429), abort the loop entirely
            return AgentStep(kind="final_answer", result=f"LLM Provider Error: {str(e)}")"""

    text = text.replace(old_ex_agent, new_ex_agent)

    # Fix 2: Exception handling in plan_tool_call
    old_ex_plan = """        except Exception as e:
            if attempt < 2:
                prompt = (
                    prompt
                    + f"\n\nYour last response was invalid/unparseable JSON ({type(e).__name__}: {e}). "
                    + "Return ONLY a single valid JSON object with keys: tool, params, explanation."
                )
                continue
            data = {
                "tool": "ask_clarify",
                "params": {"user_text": user_text, "error_context": str(e)},
            }"""

    new_ex_plan = """        except Exception as e:
            if attempt < 2:
                prompt = (
                    prompt
                    + f"\n\nYour last response was invalid/unparseable JSON ({type(e).__name__}: {e}). "
                    + "Return ONLY a single valid JSON object with keys: tool, params, explanation."
                )
                continue
            data = {
                "tool": "final_answer",
                "params": {"answer": f"LLM Provider Error: {str(e)}"},
            }"""

    text = text.replace(old_ex_plan, new_ex_plan)

    # Fix 3: category_urls strict check in agent_plan_step
    old_url_agent = """        if tool == "enqueue_run":
            urls = params.get("category_urls")
            if not isinstance(urls, list) or not [
                u for u in urls if isinstance(u, str) and u.strip()
            ]:"""

    new_url_agent = """        if tool == "enqueue_run":
            urls = params.get("category_urls")
            if isinstance(urls, str):
                import re
                extracted = re.findall(r'https?://[^\s,]+', urls)
                urls = extracted if extracted else [urls.strip()]
                params["category_urls"] = urls

            if not isinstance(urls, list) or not [
                u for u in urls if isinstance(u, str) and u.strip()
            ]:"""

    text = text.replace(old_url_agent, new_url_agent)

    # Fix 4: category_urls strict check in plan_tool_call
    old_url_plan = """        if data["tool"] == "enqueue_run":
            urls = data["params"].get("category_urls")
            if not isinstance(urls, list) or not [
                u for u in urls if isinstance(u, str) and u.strip()
            ]:"""

    new_url_plan = """        if data["tool"] == "enqueue_run":
            urls = data["params"].get("category_urls")
            if isinstance(urls, str):
                import re
                extracted = re.findall(r'https?://[^\s,]+', urls)
                urls = extracted if extracted else [urls.strip()]
                data["params"]["category_urls"] = urls

            if not isinstance(urls, list) or not [
                u for u in urls if isinstance(u, str) and u.strip()
            ]:"""

    text = text.replace(old_url_plan, new_url_plan)
    
    return text


def apply_patch_chat2(text: str) -> str:
    """Apply patch_chat2.py modifications."""
    print("Applying patch_chat2.py...")
    
    # Additional fix for agent_plan_step exception handling (variant)
    # This uses regex to handle slightly different formatting
    text = re.sub(
        r'except Exception as e:\s+if attempt < 2:\s+prompt \+= f"\n\nYour last response was invalid[^\n]+\n\s+continue\s+data = \{"tool": "ask_clarify", "params": \{"user_text": user_text, "error": str\(e\)\}\}',
        r'''except Exception as e:
            if attempt < 2:
                prompt += f"\n\nYour last response was invalid/unparseable JSON ({type(e).__name__}: {e}). Return ONLY valid JSON."
                continue
            return AgentStep(kind="final_answer", text=f"LLM Provider Error: {str(e)}")''',
        text
    )
    
    return text


def apply_patch_chat3(text: str) -> str:
    """Apply patch_chat3.py modifications."""
    print("Applying patch_chat3.py...")
    
    # Fix the schema example
    text = re.sub(
        r'"sandbox_suffix": "sandbox_20260210_143022"',
        r'"sandbox_suffix": "<optional_for_resuming>"',
        text
    )

    # Fix execute_tool_call sandbox generation to match fallback
    old_exec_sandbox = """        sandbox_suffix = str(p.get("sandbox_suffix") or "").strip()
        if not sandbox_suffix:
            sandbox_suffix = "sandbox"

        # Build sandbox_supplier for output paths/polling, but keep supplier_name canonical for credential lookup
        sandbox_supplier = f"{req.supplier_domain}__{sandbox_suffix}\""""

    new_exec_sandbox = """        sandbox_suffix = str(p.get("sandbox_suffix") or "").strip()
        if not sandbox_suffix or sandbox_suffix == "<optional_for_resuming>":
            sandbox_suffix = f"sandbox__{run_id[:8]}"

        # Build sandbox_supplier for output paths/polling, but keep supplier_name canonical for credential lookup
        sandbox_supplier = f"{req.supplier_domain}__{sandbox_suffix}\""""

    text = text.replace(old_exec_sandbox, new_exec_sandbox)
    
    return text


def apply_patch_chat4(text: str) -> str:
    """Apply patch_chat4.py modifications."""
    print("Applying patch_chat4.py...")
    
    # Fix fallback generator as well
    old_fallback_sandbox = """            sandbox_suffix = str(params.get("sandbox_suffix") or "").strip()
            if not sandbox_suffix:
                sandbox_suffix = f"sandbox__{sandbox_id}\""""

    new_fallback_sandbox = """            sandbox_suffix = str(params.get("sandbox_suffix") or "").strip()
            if not sandbox_suffix or sandbox_suffix == "<optional_for_resuming>":
                sandbox_suffix = f"sandbox__{sandbox_id}\""""

    text = text.replace(old_fallback_
