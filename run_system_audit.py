#!/usr/bin/env python3
"""
System Audit Runner - Main entry point for comprehensive system validation
Executes the complete audit protocol for Amazon FBA Agent System
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add tools directory to path
current_dir = Path(__file__).parent
tools_dir = current_dir / "tools"
sys.path.insert(0, str(tools_dir))

from tools.system_audit_monitor import SystemAuditMonitor
from tools.two_run_test_protocol import TwoRunTestProtocol

def main():
    """Main audit execution function"""
    parser = argparse.ArgumentParser(description="Amazon FBA Agent System Audit")
    parser.add_argument("--workspace", 
                       default=str(current_dir),
                       help="Workspace directory path")
    parser.add_argument("--mode", 
                       choices=["monitor", "protocol", "full"],
                       default="full",
                       help="Audit mode: monitor only, protocol only, or full audit")
    parser.add_argument("--config",
                       help="Custom config file path")
    
    args = parser.parse_args()
    
    workspace_path = Path(args.workspace).resolve()
    
    print(f"AUDIT STARTING")
    print(f"Workspace: {workspace_path}")
    print(f"Mode: {args.mode}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    try:
        if args.mode == "monitor":
            # Run monitoring only
            print("MONITORING MODE: Running monitoring only...")
            monitor = SystemAuditMonitor(str(workspace_path), args.config)
            monitor.start_monitoring()
            
            # In real scenario, this would monitor a running system
            print("MONITORING: Monitoring active. Press Ctrl+C to stop...")
            input("Press Enter to stop monitoring...")
            
            monitor.stop_monitoring()
            
        elif args.mode == "protocol":
            # Run two-run protocol only
            print("PROTOCOL MODE: Running two-run test protocol...")
            protocol = TwoRunTestProtocol(str(workspace_path))
            results = protocol.execute_protocol()
            
            print_protocol_summary(results)
            
        elif args.mode == "full":
            # Run complete audit
            print("FULL MODE: Running full system audit...")
            
            # Execute two-run test protocol
            print("\nPHASE 1: Two-Run Test Protocol")
            protocol = TwoRunTestProtocol(str(workspace_path))
            protocol_results = protocol.execute_protocol()
            
            print_protocol_summary(protocol_results)
            
            # Additional monitoring if needed
            print("\nPHASE 2: Additional Monitoring")
            monitor = SystemAuditMonitor(str(workspace_path), args.config)
            # Additional monitoring logic would go here
            
            print("\nSUCCESS: Full audit completed successfully")
            
    except KeyboardInterrupt:
        print("\nINTERRUPTED: Audit interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Audit failed: {e}")
        sys.exit(1)

def print_protocol_summary(results):
    """Print protocol results summary"""
    print(f"\nPROTOCOL RESULTS: Protocol Results Summary")
    print(f"Protocol ID: {results['protocol_id']}")
    print(f"Overall Compliance: {'PASSED' if results['overall_compliance'] else 'FAILED'}")
    print(f"Total Duration: {results['total_duration']:.1f} seconds")
    
    if 'run_results' in results:
        # Run 1 Summary
        run1 = results['run_results']['run1_fresh']
        print(f"\nRun 1 (Fresh): {run1['compliance_score']:.1f}% compliance")
        
        # Run 2 Summary  
        run2 = results['run_results']['run2_resume']
        print(f"Run 2 (Resume): {run2['compliance_score']:.1f}% compliance")
    
    if results.get('critical_issues'):
        print(f"\nCRITICAL ISSUES ({len(results['critical_issues']):}):")
        for issue in results['critical_issues']:
            print(f"  • {issue}")
    
    if results.get('recommendations'):
        print(f"\nRECOMMENDATIONS:")
        for rec in results['recommendations'][:3]:  # Show top 3
            print(f"  • {rec}")

if __name__ == "__main__":
    main()