#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-Enhanced FBA Supplier Setup - Main Entry Point (Full Implementation)

Conversational interface for configuring new suppliers with guided setup.

Session 6 Implementation - Complete End-to-End Flow
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai_enhanced_setup.conversation_orchestrator import ConversationOrchestrator
from ai_enhanced_setup.config_generator import ConfigGenerator, ConfigValidator
from ai_enhanced_setup.workflow_executor import WorkflowExecutor
from ai_enhanced_setup.result_summarizer import ResultSummarizer
from ai_enhanced_setup.conversation_state_manager import ConversationStateManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def print_welcome():
    """Display welcome message."""
    print("\n" + "=" * 60)
    print("AI-ENHANCED FBA SUPPLIER SETUP")
    print("=" * 60)
    print()
    print("💰 Estimated Cost: $0.10-$0.20 per conversation")
    print("   Accepted range: $2-$4 for value-added setup")
    print("   • Optional features: Selector suggestions, result analysis")
    print()
    print("⚠️  What this tool DOES:")
    print("   ✅ Conversational supplier configuration")
    print("   ✅ Natural language guidance")
    print("   ✅ Automated config generation")
    print("   ✅ Sanity batch validation")
    print()
    print("⚠️  What this tool DOES NOT DO:")
    print("   ❌ Automatically extract CSS selectors (you provide them)")
    print("   ❌ Modify existing workflow code (non-destructive)")
    print("   ❌ Debug workflow problems (use existing tools)")
    print()
    print("=" * 60)
    print()


def check_api_keys():
    """Validate required API keys."""
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    print("📋 API Keys Check:")
    if anthropic_key:
        print(f"   ✅ ANTHROPIC_API_KEY: Found")
        return True
    else:
        print("   ❌ ANTHROPIC_API_KEY: Not found")
        print()
        print("⚠️  Setup Required:")
        print("   1. Get API key from: https://console.anthropic.com/")
        print("   2. Set environment variable:")
        print("      export ANTHROPIC_API_KEY='sk-ant-...'")
        print("   3. Re-run this script")
        print()
        return False


def check_for_resume():
    """Check for incomplete session and offer resume."""
    state_manager = ConversationStateManager()
    session_id = state_manager.detect_incomplete_session()
    
    if session_id:
        state = state_manager.load_state(session_id)
        if state:
            print("📂 Found incomplete session")
            print(f"   Last updated: {state.get('last_updated')}")
            print(f"   Cost so far: ${state.get('cost_tracker', 0):.3f}")
            print()
            
            choice = input("Resume this session? (y/n): ").strip().lower()
            if choice == 'y':
                return session_id
    
    return None


def run_conversation_flow():
    """Run conversational data collection flow."""
    print("Starting conversation with Claude Sonnet 3.5...")
    print()
    
    try:
        # Check for resume
        resume_session = check_for_resume()
        
        if resume_session:
            orchestrator = ConversationOrchestrator()
            orchestrator.load_from_state(resume_session)
            print("✅ Session resumed")
            print()
        else:
            orchestrator = ConversationOrchestrator()
            response = orchestrator.start_conversation()
            print(f"AI: {response}")
            print()
        
        # Conversation loop
        while True:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'cancel']:
                print("\n⚠️  Setup cancelled. Session state saved for later resume.")
                return None
            
            result = orchestrator.continue_conversation(user_input)
            
            print(f"\nAI: {result['response']}")
            print(f"\n💰 Cost so far: ${result['cost_so_far']:.3f}")
            print()
            
            if result.get('budget_exceeded'):
                print("⚠️  Budget limit reached. Continuing with collected data...")
                print()
            
            if result['complete']:
                # Generate confirmation summary
                summary = orchestrator.generate_confirmation_summary(result['collected_data'])
                print(summary)
                print()
                
                confirm = input("Confirm and proceed? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    return result['collected_data']
                else:
                    print("Please provide corrections...")
                    continue
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted. Session state saved for later resume.")
        return None
    except Exception as e:
        logger.exception(f"Conversation flow failed: {e}")
        print(f"\n❌ Error: {e}")
        return None


def generate_and_validate_configs(collected_data):
    """Generate and validate configuration files."""
    print("\n✅ Generating configs...")
    
    try:
        generator = ConfigGenerator()
        validator = ConfigValidator()
        
        # Generate configs
        supplier_config = generator.generate_supplier_config(collected_data)
        categories_config = generator.generate_categories_config(collected_data)
        
        # Validate
        is_valid, errors = validator.validate_supplier_config(supplier_config)
        if not is_valid:
            print("❌ Supplier config validation failed:")
            for error in errors:
                print(f"   - {error}")
            return None
        
        is_valid, errors = validator.validate_categories_config(categories_config)
        if not is_valid:
            print("❌ Categories config validation failed:")
            for error in errors:
                print(f"   - {error}")
            return None
        
        # Write configs
        supplier_id = supplier_config['supplier_id']
        success = generator.write_configs_atomic(supplier_config, categories_config, supplier_id)
        
        if success:
            print(f"   • config/supplier_configs/{supplier_id}.json")
            print(f"   • config/{supplier_id}_categories.json")
            print(f"   • Updated config/system_config.json")
            print()
            print("✅ Configs validated successfully!")
            return supplier_id
        else:
            print("❌ Failed to write configs")
            return None
            
    except Exception as e:
        logger.exception(f"Config generation failed: {e}")
        print(f"❌ Error: {e}")
        return None


def run_sanity_batch(supplier_id):
    """Execute and validate sanity batch."""
    print("\n🧪 Running sanity batch (25 products)...")
    print("   This will take 2-5 minutes...")
    print()
    
    try:
        executor = WorkflowExecutor()
        
        # Execute
        result = executor.execute_sanity_batch(supplier_id)
        
        if not result['success']:
            print(f"\n❌ Sanity batch failed (return code: {result['return_code']})")
            return False
        
        print(f"\n✅ Sanity batch completed in {result['duration_seconds']:.1f}s")
        print()
        
        # Validate
        validation = executor.validate_sanity_results(supplier_id)
        
        print("📊 Validation Results:")
        for criterion, status in validation['results'].items():
            emoji = "✅" if status == "pass" else "❌"
            print(f"   {emoji} {criterion}: {status}")
        print()
        
        if validation['failures']:
            print("⚠️  Failures:")
            for failure in validation['failures']:
                print(f"   - {failure}")
            print()
        
        if validation['passed']:
            print("   🎉 All checks passed!")
            return True
        else:
            print("   ❌ Validation failed. Review errors and retry.")
            return False
            
    except Exception as e:
        logger.exception(f"Sanity batch execution failed: {e}")
        print(f"❌ Error: {e}")
        return False


def run_full_workflow(supplier_id, categories):
    """Execute full workflow."""
    print(f"\n🚀 Ready for full run?")
    print(f"   This will process all products in: {', '.join([c['name'] for c in categories])}")
    print(f"   Estimated time: 30-60 minutes")
    print()
    
    choice = input("Continue? (y/n): ").strip().lower()
    if choice != 'y':
        print("⏸️  Full run skipped")
        return False
    
    try:
        executor = WorkflowExecutor()
        result = executor.execute_full_run(supplier_id)
        
        if result['success']:
            print(f"\n✅ Full analysis completed in {result['duration_seconds']:.1f}s")
            return True
        else:
            print(f"\n❌ Full run failed (return code: {result['return_code']})")
            return False
            
    except Exception as e:
        logger.exception(f"Full workflow execution failed: {e}")
        print(f"❌ Error: {e}")
        return False


def generate_summary_reports(supplier_id):
    """Generate and display summary reports."""
    print("\n📁 Generating results summary...")
    
    try:
        summarizer = ResultSummarizer()
        summary = summarizer.summarize_run(supplier_id)
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("OUTPUTS") / "AI_SETUP_RESULTS" / supplier_id
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate reports
        summary_path = results_dir / f"summary_{timestamp}.md"
        curated_path = results_dir / f"curated_{timestamp}.csv"
        
        summarizer.generate_summary_markdown(summary, str(summary_path))
        
        artifacts = summarizer.read_artifacts(supplier_id)
        if artifacts['csv_rows']:
            summarizer.export_curated_csv(artifacts['csv_rows'], str(curated_path))
        
        # Display summary
        print()
        print("=" * 60)
        print("RESULTS SUMMARY")
        print("=" * 60)
        print()
        
        metrics = summary['metrics']
        print("📊 Key Metrics:")
        print(f"   • Products Processed: {metrics['products_processed']}")
        print(f"   • Products Matched: {metrics['products_matched']} ({metrics['match_rate_pct']}%)")
        print(f"   • Profitable Products: {metrics['profitable_products']}")
        print(f"   • Total Potential Profit: £{metrics['total_potential_profit']:.2f}")
        print(f"   • Average ROI: {metrics['average_roi']:.1f}%")
        print(f"   • Average Margin: {metrics['average_margin']:.1f}%")
        print()
        
        if summary['top_opportunities']:
            print("🏆 Top 5 Opportunities:")
            for idx, opp in enumerate(summary['top_opportunities'][:5], 1):
                print(f"   {idx}. {opp['supplier_title'][:40]} - £{opp['net_profit_gbp']:.2f} profit ({opp['roi_pct']:.0f}% ROI)")
            print()
        
        if summary['anomalies']:
            print("⚠️  Anomalies Detected:")
            for anomaly in summary['anomalies']:
                print(f"   • {anomaly}")
            print()
        
        print("📄 Detailed Reports:")
        print(f"   • Summary: {summary_path}")
        if artifacts['csv_rows']:
            print(f"   • Curated CSV: {curated_path}")
        print()
        
        return True
        
    except Exception as e:
        logger.exception(f"Summary generation failed: {e}")
        print(f"❌ Error: {e}")
        return False


def main():
    """Main entry point."""
    try:
        # Welcome
        print_welcome()
        
        # Check API keys
        if not check_api_keys():
            return 1
        
        print()
        
        # Run conversation
        collected_data = run_conversation_flow()
        
        if not collected_data:
            return 130  # User cancelled
        
        # Generate configs
        supplier_id = generate_and_validate_configs(collected_data)
        
        if not supplier_id:
            return 1
        
        # Run sanity batch
        sanity_passed = run_sanity_batch(supplier_id)
        
        if not sanity_passed:
            print("\n⚠️  Fix issues and retry sanity batch before full run")
            return 1
        
        # Run full workflow (optional)
        full_completed = run_full_workflow(supplier_id, collected_data.get('categories', []))
        
        # Generate summary
        if full_completed or sanity_passed:
            generate_summary_reports(supplier_id)
        
        # Final message
        print("=" * 60)
        print("SETUP COMPLETE")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Review results in OUTPUTS/AI_SETUP_RESULTS/")
        print("2. Verify flagged products manually")
        print("3. Schedule regular runs (daily/weekly)")
        print()
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return 130
    
    except Exception as e:
        logger.exception("Unexpected error during setup")
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
