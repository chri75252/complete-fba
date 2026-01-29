# DeepSeek-R1:7B Configuration for Supplier-Onboarding Skill
# Purpose: Enable tool-calling capabilities for multi-step workflow execution

import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests

# ============================================================================
# TOOL DEFINITIONS (for DeepSeek-R1 to understand)
# ============================================================================

SUPPLIER_ONBOARDING_TOOLS = [
    {
        "name": "read_file",
        "description": "Read contents of a file. Use for validating categories, selectors, and generated scripts.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute or relative path to file"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Use for creating JSON configs (categories, selectors, wizard input).",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute or relative path to file"
                },
                "content": {
                    "type": "string",
                    "description": "File content to write"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "execute_command",
        "description": "Execute a bash/shell command. Use for running wizard, validation scripts, curl checks.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to execute"
                },
                "timeout": {
                    "type": "number",
                    "description": "Timeout in seconds (default: 60)"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "list_directory",
        "description": "List files in a directory. Use for verifying file existence and structure.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "Path to directory"
                },
                "pattern": {
                    "type": "string",
                    "description": "Optional glob pattern (e.g., '*.json')"
                }
            },
            "required": ["directory_path"]
        }
    },
    {
        "name": "ask_user",
        "description": "Ask user a question and wait for response. Use for progressive discovery and confirmation checkpoints.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Question to ask user"
                },
                "checkpoint_type": {
                    "type": "string",
                    "description": "Type: 'information_gathering', 'validation_checkpoint', 'confirmation'"
                }
            },
            "required": ["question"]
        }
    },
    {
        "name": "validate_json",
        "description": "Validate JSON structure and required fields. Use for config file validation.",
        "parameters": {
            "type": "object",
            "properties": {
                "json_content": {
                    "type": "string",
                    "description": "JSON string to validate"
                },
                "required_keys": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of required keys"
                }
            },
            "required": ["json_content"]
        }
    },
    {
        "name": "count_lines",
        "description": "Count lines in a file. Use for runner script validation (must be 117-143 lines, not 26).",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to file"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "grep_file",
        "description": "Search for pattern in file. Use for verifying imports, workflow keys, authentication logic.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to file"
                },
                "pattern": {
                    "type": "string",
                    "description": "Regex pattern to search for"
                }
            },
            "required": ["file_path", "pattern"]
        }
    }
]

# ============================================================================
# SYSTEM PROMPT (Skill-Specific Instructions for DeepSeek-R1)
# ============================================================================

SUPPLIER_ONBOARDING_SYSTEM_PROMPT = """You are a supplier onboarding specialist for the Amazon FBA Agent System.

**YOUR MISSION**: Guide users through a 7-step supplier onboarding process using the skill located at:
`.claude/skills/supplier-onboarding/`

**CRITICAL RULES FROM EXECUTION_ENFORCEMENT.md**:

1. **NEVER SKIP VALIDATION**: Every checkpoint in EXECUTION_ENFORCEMENT.md is MANDATORY
2. **PROVIDE EVIDENCE**: Every step requires proof (file reads, validation results)
3. **STOP AT CHECKPOINTS**: 15+ user confirmation points - NEVER proceed without approval
4. **FOLLOW EXACT FORMAT**: Output must match SKILL.md and EXECUTION_ENFORCEMENT.md templates

**7-STEP WORKFLOW** (from SKILL.md lines 18-29):
- Step 0: Data Preprocessing (LLM manual work - Read/Write tools only)
- Step 1: Gather Information (Progressive discovery with ask_user)
- Step 2: Prepare Configurations (Create JSON files)
- Step 3: Invoke Wizard (execute_command: python wizard.py)
- Step 4: Validate Files (read_file ALL generated files)
- Step 5: Report Results (Comprehensive summary)
- Step 6: Pre-Run Verification (System readiness checks)
- Step 7: User Decision (Test run vs main run)

**AVAILABLE TOOLS**:
{tools}

**TOOL CALLING FORMAT**:
When you need to use a tool, respond with:
```json
{
  "reasoning": "Why I need to use this tool and what I expect",
  "tool": "tool_name",
  "parameters": {
    "param1": "value1"
  }
}
```

**VALIDATION CHECKBOXES** (from EXECUTION_ENFORCEMENT.md):
Every validation section has checkboxes. You MUST:
- Read the file
- Verify EACH checkbox manually
- Report status of ALL checkboxes
- Stop if ANY checkbox fails

**EXAMPLE - Step 4.1.A (Runner Script Structure Check)**:
```
Runner Script Validation (SKILL.MD Section 4.1, Lines 418-499):

A. Structure (Lines 423-452):
- [ ] Line count: 153 (within 117-143 range) ✅
- [ ] All imports present ✅
- [ ] Main function exists ✅
- [ ] Entry point correct ✅

Status: ✅ PASS

USER: Confirm runner validation before I check config files.
```

**KEY SUCCESS CRITERIA**:
- Total of 280+ validation checkboxes across all steps
- 15+ stop points requiring user confirmation
- All files read and analyzed (not just existence checks)
- Evidence provided for every validation

**CHAIN-OF-THOUGHT REQUIREMENT**:
For EVERY step, show your reasoning:
1. What am I validating?
2. What tool do I need?
3. What do I expect to find?
4. Did I find it?
5. Pass/fail?
6. Next action?

**START EVERY SESSION** with this declaration (EXECUTION_ENFORCEMENT.md lines 13-19):
"I am about to onboard [supplier_name] using the supplier-onboarding skill.
I have read SKILL.md completely (lines 1-1234) and understand ALL steps are mandatory.
I will not skip validation checkpoints. I will provide evidence for each step.
I will stop at critical checkpoints and get user confirmation before proceeding."

**WHEN IN DOUBT**: STOP and ask user for clarification. Never proceed without confirmation at checkpoints.
"""

# ============================================================================
# TOOL EXECUTOR (Actual File Operations)
# ============================================================================

class ToolExecutor:
    """Executes tool calls from DeepSeek-R1 and returns results"""

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)

    async def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return result"""
        try:
            if tool_name == "read_file":
                return await self._read_file(parameters["file_path"])
            elif tool_name == "write_file":
                return await self._write_file(parameters["file_path"], parameters["content"])
            elif tool_name == "execute_command":
                timeout = parameters.get("timeout", 60)
                return await self._execute_command(parameters["command"], timeout)
            elif tool_name == "list_directory":
                pattern = parameters.get("pattern")
                return await self._list_directory(parameters["directory_path"], pattern)
            elif tool_name == "ask_user":
                return await self._ask_user(parameters["question"], parameters.get("checkpoint_type"))
            elif tool_name == "validate_json":
                required = parameters.get("required_keys", [])
                return await self._validate_json(parameters["json_content"], required)
            elif tool_name == "count_lines":
                return await self._count_lines(parameters["file_path"])
            elif tool_name == "grep_file":
                return await self._grep_file(parameters["file_path"], parameters["pattern"])
            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"error": str(e), "traceback": str(e.__traceback__)}

    async def _read_file(self, file_path: str) -> Dict:
        """Read file contents"""
        path = self.repo_root / file_path
        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "success": True,
            "file_path": file_path,
            "content": content,
            "line_count": len(content.splitlines())
        }

    async def _write_file(self, file_path: str, content: str) -> Dict:
        """Write file contents"""
        path = self.repo_root / file_path
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "success": True,
            "file_path": file_path,
            "bytes_written": len(content.encode('utf-8'))
        }

    async def _execute_command(self, command: str, timeout: int) -> Dict:
        """Execute shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout} seconds"}

    async def _list_directory(self, directory_path: str, pattern: Optional[str]) -> Dict:
        """List directory contents"""
        path = self.repo_root / directory_path
        if not path.exists():
            return {"error": f"Directory not found: {directory_path}"}

        if pattern:
            files = list(path.glob(pattern))
        else:
            files = list(path.iterdir())

        return {
            "success": True,
            "directory": directory_path,
            "files": [f.name for f in files],
            "count": len(files)
        }

    async def _ask_user(self, question: str, checkpoint_type: Optional[str]) -> Dict:
        """Ask user a question (returns immediately - actual Q&A happens in chat UI)"""
        return {
            "success": True,
            "question": question,
            "checkpoint_type": checkpoint_type or "general",
            "awaiting_user_response": True
        }

    async def _validate_json(self, json_content: str, required_keys: List[str]) -> Dict:
        """Validate JSON structure"""
        try:
            data = json.loads(json_content)
            missing_keys = [key for key in required_keys if key not in data]

            return {
                "success": len(missing_keys) == 0,
                "valid_json": True,
                "missing_keys": missing_keys,
                "present_keys": list(data.keys())
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "valid_json": False,
                "error": str(e)
            }

    async def _count_lines(self, file_path: str) -> Dict:
        """Count lines in file"""
        read_result = await self._read_file(file_path)
        if "error" in read_result:
            return read_result

        line_count = read_result["line_count"]

        # Critical validation for runner scripts
        is_shim = line_count == 26
        is_valid_runner = 117 <= line_count <= 143

        return {
            "success": True,
            "file_path": file_path,
            "line_count": line_count,
            "is_shim": is_shim,
            "is_valid_runner": is_valid_runner,
            "warning": "❌ CRITICAL: This is a 26-line shim, not a full runner!" if is_shim else None
        }

    async def _grep_file(self, file_path: str, pattern: str) -> Dict:
        """Search for pattern in file"""
        import re

        read_result = await self._read_file(file_path)
        if "error" in read_result:
            return read_result

        content = read_result["content"]
        matches = []

        for line_num, line in enumerate(content.splitlines(), start=1):
            if re.search(pattern, line):
                matches.append({
                    "line_number": line_num,
                    "line_content": line.strip()
                })

        return {
            "success": True,
            "file_path": file_path,
            "pattern": pattern,
            "match_count": len(matches),
            "matches": matches
        }

# ============================================================================
# CONVERSATION LOOP (Manages Chat with Tool Calling)
# ============================================================================

class SupplierOnboardingAgent:
    """Manages DeepSeek-R1 conversation loop with tool calling for supplier onboarding"""

    def __init__(self, repo_root: Path, ollama_url: str = "http://localhost:11434"):
        self.repo_root = Path(repo_root)
        self.ollama_url = ollama_url
        self.executor = ToolExecutor(repo_root)
        self.conversation_history = []

        # Initialize with system prompt
        tools_json = json.dumps(SUPPLIER_ONBOARDING_TOOLS, indent=2)
        system_prompt = SUPPLIER_ONBOARDING_SYSTEM_PROMPT.format(tools=tools_json)

        self.conversation_history.append({
            "role": "system",
            "content": system_prompt
        })

    async def chat(self, user_message: str) -> str:
        """Send user message and handle tool calls"""
        # Add user message
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Get LLM response
        response = await self._call_deepseek_r1(self.conversation_history)
        assistant_message = response["message"]["content"]

        # Check if response contains tool call
        tool_call = self._parse_tool_call(assistant_message)

        if tool_call:
            # Execute tool
            tool_result = await self.executor.execute(
                tool_call["tool"],
                tool_call["parameters"]
            )

            # Add tool result to conversation
            tool_message = f"Tool Result ({tool_call['tool']}):\n{json.dumps(tool_result, indent=2)}"
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            self.conversation_history.append({
                "role": "user",
                "content": tool_message
            })

            # Get next response after tool execution
            response = await self._call_deepseek_r1(self.conversation_history)
            final_message = response["message"]["content"]

            self.conversation_history.append({
                "role": "assistant",
                "content": final_message
            })

            return final_message
        else:
            # No tool call, just return response
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            return assistant_message

    async def _call_deepseek_r1(self, messages: List[Dict]) -> Dict:
        """Call Ollama API with DeepSeek-R1"""
        response = requests.post(
            f"{self.ollama_url}/api/chat",
            json={
                "model": "deepseek-r1:7b",
                "messages": messages,
                "stream": False
            }
        )
        return response.json()

    def _parse_tool_call(self, message: str) -> Optional[Dict]:
        """Parse tool call from LLM response"""
        # Look for JSON code block with tool call
        import re

        # Match ```json ... ``` blocks
        json_blocks = re.findall(r'```json\s*(\{.*?\})\s*```', message, re.DOTALL)

        for block in json_blocks:
            try:
                data = json.loads(block)
                if "tool" in data and "parameters" in data:
                    return data
            except json.JSONDecodeError:
                continue

        return None

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

async def main():
    """Example usage of supplier onboarding agent"""

    # Initialize agent
    repo_root = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-")
    agent = SupplierOnboardingAgent(repo_root)

    print("=== Supplier Onboarding Agent (DeepSeek-R1:7B) ===\n")
    print("Agent initialized with supplier-onboarding skill")
    print("Type 'exit' to quit\n")

    # Example: Start onboarding
    response = await agent.chat("I want to onboard a new supplier: example-wholesale.com")
    print(f"Agent: {response}\n")

    # Continue conversation loop
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        response = await agent.chat(user_input)
        print(f"\nAgent: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())
