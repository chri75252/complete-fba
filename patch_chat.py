import re

with open('control_plane/chat_orchestrator.py', 'r', encoding='utf-8') as f:
    text = f.read()

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

with open('control_plane/chat_orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Patched chat_orchestrator.py")
