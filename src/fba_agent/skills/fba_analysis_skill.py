"""
Gemini Skill Implementation for FBA Analysis.
Wraps the logic and prompts into a tool-using agent.
"""
from pathlib import Path

# Use the new isolated provider
from fba_agent.skills.providers.gemini_skill_provider import GeminiSkillProvider
from fba_agent.skills.schemas import PREFLIGHT_TOOL_SCHEMA, ANALYSIS_TOOL_SCHEMA

class FbaAnalysisSkill:
    def __init__(self, provider: GeminiSkillProvider):
        self.provider = provider
        self._load_prompts()

    def _load_prompts(self):
        # Paths based on the report
        base_dir = Path("RESERACH/REPORT/PROMPTS GUIDES/finale")
        
        # Load Preflight Prompt
        preflight_path = base_dir / "AG_PREFLIGHT_CALIBRATION_PROMPT_v1.2_patched (1).md"
        if preflight_path.exists():
            self.preflight_prompt = preflight_path.read_text(encoding="utf-8")
        else:
            self.preflight_prompt = "You are a Preflight Calibration Agent..." # Fallback

        # Load Analysis Prompt
        analysis_path = base_dir / "FINANCIAL_REPORT_PROMPT_ANALYSIS_AG1_v1.2_AUDITED_OUT_v5 (1).md"
        if analysis_path.exists():
            self.analysis_prompt = analysis_path.read_text(encoding="utf-8")
        else:
            self.analysis_prompt = "You are an FBA Analysis Agent..." # Fallback

    def run_preflight(self, sample_rows: str) -> dict:
        """
        Executes the Preflight Calibration using Gemini Function Calling.
        """
        system_msg = self.preflight_prompt
        user_msg = f"Here are the first 50 rows of the supplier file:\n\n{sample_rows}\n\nPerform the calibration and call the 'save_calibration_config' function."
        
        # Use the specialized method for tools
        return self.provider.chat_with_tools(
            system=system_msg,
            user=user_msg,
            tools=[PREFLIGHT_TOOL_SCHEMA]
        )

    def analyze_row(self, row_data: dict, calibration_config: dict) -> dict:
        """
        Executes the Main Analysis for a single row using Gemini Function Calling.
        """
        system_msg = self.analysis_prompt
        
        # Inject calibration into the prompt (simulating the dynamic injection described in docs)
        config_str = str(calibration_config)
        system_msg = system_msg.replace("[USER_FILE_PATH]", "Current Row Data") # Placeholder replacement
        system_msg += f"\n\n--- ACTIVE CALIBRATION CONFIG ---\n{config_str}\n---------------------------------"

        user_msg = f"Analyze this product row:\n{row_data}\n\nCall 'submit_analysis_result' with your verdict."

        return self.provider.chat_with_tools(
            system=system_msg,
            user=user_msg,
            tools=[ANALYSIS_TOOL_SCHEMA]
        )