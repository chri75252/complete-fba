"""
Test script for Gemini FBA Analysis Skill.
"""
import os
import sys
from pathlib import Path

# Ensure src is in python path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fba_agent.providers import ProviderConfig
from fba_agent.skills.providers.gemini_skill_provider import GeminiSkillProvider
from fba_agent.skills.fba_analysis_skill import FbaAnalysisSkill

def test_skill():
    print("Initializing Gemini Skill...")
    
    # Configure provider (assumes GOOGLE_API_KEY or OPENAI_API_KEY env var is set or handled by BaseProvider logic)
    # Using 'gemini-1.5-flash' as a default efficient model for testing
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("Warning: GEMINI_API_KEY not found. Using MOCK Provider for logic verification.")
        
        class MockGeminiSkillProvider:
            def chat_with_tools(self, system, user, tools):
                print(f"  [Mock] System Prompt Length: {len(system)}")
                print(f"  [Mock] User Prompt: {user[:50]}...")
                print(f"  [Mock] Tools Provided: {[t['function']['name'] for t in tools]}")
                
                # Return fake responses based on the tool name
                tool_name = tools[0]['function']['name']
                if tool_name == "save_calibration_config":
                    return {
                        "explicit_units": ["pcs", "pk"],
                        "brand_position": "start",
                        "dimension_shield_keywords": ["cm", "mm"],
                        "allow_trailing_number_as_qty": True
                    }
                elif tool_name == "submit_analysis_result":
                    return {
                        "verdict": "VERIFIED",
                        "confidence": 95,
                        "pack_verdict": "1:1",
                        "rsu": 1.0,
                        "adjusted_profit": 2.35,
                        "key_match_evidence": "Exact match",
                        "filter_reason": "-"
                    }
                return {}

        provider = MockGeminiSkillProvider()
    else:
        config = ProviderConfig(
            name="gemini_skill", 
            api_key=api_key,
            model_small="gemini-1.5-flash",
            model_large="gemini-1.5-pro"
        ) 
        provider = GeminiSkillProvider(config)
        
    skill = FbaAnalysisSkill(provider)

    # 1. Test Preflight
    print("\n--- Testing Preflight Calibration ---")
    mock_csv_sample = """
    SupplierTitle,AmazonTitle
    "PACK OF 6 - DOVE SOAP","Dove Beauty Cream Bar 6 Pack"
    "LUCOZADE ENERGY ORANGE 24X380ML","Lucozade Energy Orange 380ml (Pack of 24)"
    "AMTECH 9 LED TORCH","Amtech 9 LED Mini Torch"
    """
    try:
        calibration = skill.run_preflight(mock_csv_sample)
        print("Calibration Result:", calibration)
    except Exception as e:
        print(f"Preflight failed: {e}")
        return

    # 2. Test Analysis
    print("\n--- Testing Row Analysis ---")
    mock_row = {
        "SupplierTitle": "AMTECH 9 LED TORCH",
        "AmazonTitle": "Amtech 9 LED Mini Torch",
        "EAN": "5032759031078",
        "EAN_OnPage": "5032759031078",
        "SupplierPrice": 1.72,
        "SellingPrice": 7.99,
        "NetProfit": 2.35
    }
    
    try:
        result = skill.analyze_row(mock_row, calibration)
        print("Analysis Result:", result)
    except Exception as e:
        print(f"Analysis failed: {e}")

if __name__ == "__main__":
    test_skill()
