from pathlib import Path
from control_plane.chat_orchestrator import execute_tool_call, ToolCall

def test():
    tc = ToolCall(
        name="enqueue_run",
        params={
            "supplier_domain": "angelwholesale.co.uk",
            "workflow_key": "angelwholesale_workflow",
            "runner_script": "run_custom_angelwholesale-co-uk.py",
            "category_urls": ["https://example.com/1", "https://example.com/2"],
            "sandbox_suffix": "<optional_for_resuming>"
        }
    )
    res = execute_tool_call(tc, Path("."))
    print("Result:", res)

if __name__ == "__main__":
    test()
