from pathlib import Path
from control_plane.chat_orchestrator import _compute_rag_info, agent_plan_step, execute_tool_call

def main():
    user_text = "i meed you to analyze the first 10 products, of the following categories: https://angelwholesale.co.uk/Category/All-Baby-and-child and https://angelwholesale.co.uk/Category/Baby-Socks-and-Booties"
    repo_root = Path('.')
    rag_info, rag_context = _compute_rag_info(user_text)
    
    scratchpad = []
    
    print("--- STARTING AGENT LOOP ---")
    for step_num in range(10):
        print(f"\n[Step {step_num + 1}]")
        step = agent_plan_step(
            user_text=user_text,
            repo_root=repo_root,
            scratchpad=scratchpad,
            chat_history=[],
            rag_info_tuple=(rag_info, rag_context)
        )
        
        print(f"Kind: {step.kind}")
        if step.tool_call:
            print(f"Tool: {step.tool_call.name}")
            print(f"Params: {step.tool_call.params}")
            print(f"Explanation: {step.tool_call.explanation}")
            
            # Execute tool
            res = execute_tool_call(step.tool_call, repo_root)
            print(f"Result: {res}")
            
            # Add to scratchpad
            scratchpad.append({"role": "observation", "result": res})
        else:
            print(f"Text: {step.text}")
            break

if __name__ == "__main__":
    main()
