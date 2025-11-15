#!/usr/bin/env python3
"""
Agent Skill: Supplier Onboarding
Orchestrates guided supplier onboarding for Amazon FBA Agent System.

This skill handles:
- Input validation and collection
- Session management
- Wizard invocation via subprocess
- Result presentation

Communication with wizard is ONLY via session files (input.json → output.json).
No direct imports from wizard - maintains strict separation of concerns.
"""

import sys
import json
import uuid
import time
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


class SupplierOnboardingSkill:
    """
    Agent Skill for supplier onboarding orchestration.
    Communicates with wizard ONLY via session files.
    """

    def __init__(self):
        self.repo_root = self._resolve_repo_root()
        self.session_id = str(uuid.uuid4())
        self.session_dir = self._create_session_dir()
        self.run_start_time = time.time()

    def _resolve_repo_root(self) -> Path:
        """
        Resolve absolute repository root.
        Handles Windows, WSL, and Linux paths.
        """
        cwd = Path.cwd()
        markers = [".git", "run_custom_poundwholesale.py", "CLAUDE.md", "config/system_config.json"]
        current = cwd

        while current != current.parent:
            if any((current / marker).exists() for marker in markers):
                return current.absolute()
            current = current.parent

        raise RuntimeError(
            f"Cannot find repository root. Started from: {cwd}\n"
            "Ensure you're running from within the Amazon FBA project directory."
        )

    def _create_session_dir(self) -> Path:
        """
        Create session directory with absolute path.
        Windows/WSL aware.
        """
        if os.name == 'nt':  # Windows
            base = Path("C:/temp/onboarding")
        elif Path("/mnt/c").exists():  # WSL
            base = Path("/mnt/c/temp/onboarding")
        else:  # Linux
            base = Path("/tmp/onboarding")

        session_dir = base / self.session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir.absolute()

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Main skill execution entry point.
        """
        try:
            # 1. Validate inputs
            inputs = self._validate_inputs(**kwargs)

            # 2. Create session input file
            session_input = self._create_session_input(inputs)
            input_file = self.session_dir / "input.json"
            input_file.write_text(json.dumps(session_input, indent=2), encoding='utf-8')

            # 3. Invoke wizard via subprocess
            wizard_result = self._invoke_wizard(input_file)

            # 4. Return result
            return wizard_result

        except Exception as e:
            return {
                "success": False,
                "errors": [str(e)],
                "files_generated": [],
                "sanity_results": {}
            }

        finally:
            # 5. Cleanup (optional - keep for debugging)
            # self._cleanup_session()
            pass

    def _validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """
        Validate required inputs are present.
        NO normalization here - wizard handles that.
        """
        required = ["domain", "categories_source", "selectors_source", "workflow_key"]
        missing = [k for k in required if k not in kwargs or not kwargs[k]]

        if missing:
            raise ValueError(f"Missing required inputs: {missing}")

        return {
            "domain": kwargs["domain"],
            "categories_source": kwargs["categories_source"],
            "selectors_source": kwargs["selectors_source"],
            "workflow_key": kwargs["workflow_key"],
            "mode": kwargs.get("mode", "generate"),
            "scaffolds": kwargs.get("scaffolds", []),
            "test_product_url": kwargs.get("test_product_url"),
            "username": kwargs.get("username"),
            "password": kwargs.get("password"),
            "authentication_required": kwargs.get("authentication_required", False),
            "session_id": self.session_id,
            "run_start_time": self.run_start_time
        }

    def _create_session_input(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create session input for wizard.
        Pass everything as-is - wizard normalizes.
        """
        return {
            **inputs,
            "repo_root": str(self.repo_root.absolute())
        }

    def _invoke_wizard(self, input_file: Path) -> Dict[str, Any]:
        """
        Invoke Python wizard via subprocess with ABSOLUTE paths.
        """
        wizard_script = self.repo_root / "utils/supplier_onboarding_wizard.py"
        output_file = self.session_dir / "output.json"

        if not wizard_script.exists():
            raise FileNotFoundError(
                f"Wizard script not found: {wizard_script}\n"
                "Ensure utils/supplier_onboarding_wizard.py exists in the repository."
            )

        # Build command with absolute paths
        cmd = [
            sys.executable,
            str(wizard_script.absolute()),
            "--input", str(input_file.absolute()),
            "--output", str(output_file.absolute())
        ]

        # Execute wizard
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        # Check execution
        if result.returncode != 0:
            return {
                "success": False,
                "errors": [
                    f"Wizard execution failed (exit code {result.returncode})",
                    f"STDOUT: {result.stdout}",
                    f"STDERR: {result.stderr}"
                ],
                "files_generated": [],
                "sanity_results": {}
            }

        # Read output file
        if not output_file.exists():
            return {
                "success": False,
                "errors": [
                    "Wizard did not produce output file",
                    f"Expected: {output_file}",
                    f"STDOUT: {result.stdout}"
                ],
                "files_generated": [],
                "sanity_results": {}
            }

        return json.loads(output_file.read_text(encoding='utf-8'))

    def _cleanup_session(self):
        """
        Clean up session directory.
        Call this only if you want to remove temp files.
        """
        import shutil
        if self.session_dir.exists():
            shutil.rmtree(self.session_dir)


# Skill entry point
def run_skill(**kwargs) -> Dict[str, Any]:
    """
    Entry point for Claude Code Agent Skills system.
    """
    skill = SupplierOnboardingSkill()
    return skill.execute(**kwargs)


if __name__ == "__main__":
    # Allow standalone testing
    import argparse
    parser = argparse.ArgumentParser(description="Supplier Onboarding Skill")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--categories-source", required=True)
    parser.add_argument("--selectors-source", required=True)
    parser.add_argument("--workflow-key", required=True)
    parser.add_argument("--mode", default="generate")
    parser.add_argument("--scaffolds", nargs="*", default=[])
    parser.add_argument("--test-product-url")
    parser.add_argument("--username", help="Supplier login username (if authentication required)")
    parser.add_argument("--password", help="Supplier login password (if authentication required)")
    parser.add_argument("--authentication-required", action="store_true", help="Set if supplier requires login")

    args = parser.parse_args()

    result = run_skill(
        domain=args.domain,
        categories_source=args.categories_source,
        selectors_source=args.selectors_source,
        workflow_key=args.workflow_key,
        mode=args.mode,
        scaffolds=args.scaffolds,
        test_product_url=args.test_product_url,
        username=args.username,
        password=args.password,
        authentication_required=args.authentication_required
    )

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)
