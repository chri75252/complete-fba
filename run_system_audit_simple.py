#!/usr/bin/env python3
"""
Simple System Audit Runner - Windows compatible version without Unicode
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Add tools directory to path
current_dir = Path(__file__).parent
tools_dir = current_dir / "tools"
sys.path.insert(0, str(tools_dir))

def main():
    """Execute comprehensive system audit with two-run protocol"""
    workspace_path = Path(current_dir).resolve()
    
    print("=" * 60)
    print("AMAZON FBA AGENT SYSTEM - COMPREHENSIVE AUDIT")
    print("=" * 60)
    print(f"Workspace: {workspace_path}")
    print(f"Start Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    try:
        # Execute two-run test protocol
        print("\n[PHASE 1] Two-Run Test Protocol")
        print("-" * 40)
        
        protocol_results = execute_two_run_protocol(workspace_path)
        
        # Display results
        print_results_summary(protocol_results)
        
        # Check output files
        print("\n[PHASE 2] Output File Analysis")
        print("-" * 40)
        
        analyze_output_files(workspace_path)
        
        print("\n[AUDIT COMPLETE] System validation finished")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nAUDIT FAILED: {e}")
        sys.exit(1)

def execute_two_run_protocol(workspace_path):
    """Execute the two-run test protocol"""
    protocol_id = f"audit_{int(time.time())}"
    results = {
        "protocol_id": protocol_id,
        "start_time": time.time(),
        "workspace": str(workspace_path),
        "run_results": {},
        "overall_success": False
    }
    
    try:
        # Run 1: Fresh Processing (limited for testing)
        print("\n[RUN 1] Fresh Processing Test")
        run1_results = execute_test_run(workspace_path, "fresh", limit_products=10)
        results["run_results"]["run1_fresh"] = run1_results
        print(f"Run 1 Result: {'SUCCESS' if run1_results['success'] else 'FAILED'}")
        if not run1_results['success']:
            print(f"Error: {run1_results.get('error', 'Unknown error')}")
        
        # Wait between runs
        print("\nWaiting 3 seconds between runs...")
        time.sleep(3)
        
        # Run 2: Resume Processing Test
        print("\n[RUN 2] Resume Processing Test")
        run2_results = execute_test_run(workspace_path, "resume", limit_products=5)
        results["run_results"]["run2_resume"] = run2_results
        print(f"Run 2 Result: {'SUCCESS' if run2_results['success'] else 'FAILED'}")
        if not run2_results['success']:
            print(f"Error: {run2_results.get('error', 'Unknown error')}")
        
        # Overall assessment
        results["overall_success"] = run1_results["success"] and run2_results["success"]
        
    except Exception as e:
        results["error"] = str(e)
        print(f"Protocol execution failed: {e}")
    
    finally:
        results["end_time"] = time.time()
        results["total_duration"] = results["end_time"] - results["start_time"]
    
    # Save results
    save_protocol_results(workspace_path, results)
    
    return results

def execute_test_run(workspace_path, run_type, limit_products=10):
    """Execute a single test run"""
    print(f"  Executing {run_type} run with {limit_products} product limit...")
    
    run_results = {
        "run_type": run_type,
        "start_time": time.time(),
        "success": False,
        "products_processed": 0,
        "files_created": {},
        "validation_results": {}
    }
    
    try:
        # Setup for run type
        if run_type == "fresh":
            setup_fresh_run(workspace_path)
        elif run_type == "resume":
            validate_resume_state(workspace_path)
        
        # Record baseline file counts
        baseline_counts = count_output_files(workspace_path)
        
        # Execute the system with test limits
        execution_result = run_fba_system(workspace_path, limit_products)
        
        # Record post-execution file counts
        final_counts = count_output_files(workspace_path)
        
        # Validate results
        validation_results = validate_run_results(workspace_path, run_type, baseline_counts, final_counts)
        
        run_results.update({
            "success": execution_result["success"],
            "products_processed": execution_result.get("products_processed", 0),
            "files_created": calculate_file_differences(baseline_counts, final_counts),
            "validation_results": validation_results,
            "execution_output": execution_result.get("output", "")
        })
        
        if not execution_result["success"]:
            run_results["error"] = execution_result.get("error", "Execution failed")
        
    except Exception as e:
        run_results["error"] = str(e)
        print(f"  Run execution failed: {e}")
    
    finally:
        run_results["end_time"] = time.time()
        run_results["duration"] = run_results["end_time"] - run_results["start_time"]
    
    return run_results

def setup_fresh_run(workspace_path):
    """Setup for fresh run by clearing processing state"""
    print("    Setting up fresh run...")
    
    # Clear processing state files
    state_dir = workspace_path / "OUTPUTS" / "CACHE" / "processing_states"
    if state_dir.exists():
        for state_file in state_dir.glob("*.json"):
            try:
                state_file.unlink()
                print(f"    Removed state file: {state_file.name}")
            except Exception as e:
                print(f"    Warning: Could not remove {state_file.name}: {e}")

def validate_resume_state(workspace_path):
    """Validate that resume state exists"""
    print("    Validating resume state...")
    
    state_dir = workspace_path / "OUTPUTS" / "CACHE" / "processing_states"
    state_files = list(state_dir.glob("*.json")) if state_dir.exists() else []
    
    if not state_files:
        print("    Warning: No state files found for resume test")
        return False
    
    # Validate at least one state file is valid JSON
    for state_file in state_files:
        try:
            with open(state_file, 'r') as f:
                data = json.load(f)
                print(f"    State file validated: {state_file.name}")
                return True
        except Exception as e:
            print(f"    State file invalid: {state_file.name} - {e}")
    
    return False

def run_fba_system(workspace_path, limit_products):
    """Execute the FBA system with test limits"""
    print(f"    Running FBA system (limit: {limit_products} products)...")
    
    run_script = workspace_path / "run_custom_poundwholesale.py"
    if not run_script.exists():
        return {"success": False, "error": f"Run script not found: {run_script}"}
    
    try:
        # Set environment variables for test mode
        env = os.environ.copy()
        env.update({
            "FBA_TEST_MODE": "true",
            "FBA_TEST_LIMIT": str(limit_products),
            "FBA_AUDIT_MODE": "true"
        })
        
        # Execute with timeout
        result = subprocess.run(
            [sys.executable, str(run_script)],
            cwd=str(workspace_path),
            capture_output=True,
            text=True,
            timeout=180,  # 3 minute timeout
            env=env
        )
        
        success = result.returncode == 0
        output = result.stdout if success else result.stderr
        
        return {
            "success": success,
            "return_code": result.returncode,
            "output": output,
            "products_processed": extract_products_processed(output)
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Execution timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def extract_products_processed(output):
    """Extract number of products processed from output"""
    # Look for common patterns in output
    import re
    
    patterns = [
        r"processed (\d+) products?",
        r"(\d+) products? processed",
        r"total.*?(\d+).*?products?",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE)
        if matches:
            return int(matches[-1])  # Return last match
    
    return 0

def count_output_files(workspace_path):
    """Count output files for comparison"""
    outputs_dir = workspace_path / "OUTPUTS"
    
    counts = {
        "cache_files": 0,
        "linking_maps": 0,
        "processing_states": 0,
        "financial_reports": 0,
        "manifests": 0
    }
    
    try:
        # Cache files
        cache_dir = outputs_dir / "cached_products"
        if cache_dir.exists():
            counts["cache_files"] = len(list(cache_dir.glob("*.json")))
        
        # Linking maps
        linking_dir = outputs_dir / "FBA_ANALYSIS" / "linking_maps"
        if linking_dir.exists():
            counts["linking_maps"] = len(list(linking_dir.rglob("*.json")))
        
        # Processing states
        state_dir = outputs_dir / "CACHE" / "processing_states"
        if state_dir.exists():
            counts["processing_states"] = len(list(state_dir.glob("*.json")))
        
        # Financial reports
        financial_dir = outputs_dir / "FBA_ANALYSIS" / "financial_reports"
        if financial_dir.exists():
            counts["financial_reports"] = len(list(financial_dir.glob("*.csv")))
        
        # Manifests
        manifest_dir = outputs_dir / "manifests"
        if manifest_dir.exists():
            counts["manifests"] = len(list(manifest_dir.rglob("*.json")))
    
    except Exception as e:
        print(f"    Warning: Error counting files: {e}")
    
    return counts

def calculate_file_differences(baseline, final):
    """Calculate differences in file counts"""
    differences = {}
    
    for file_type in baseline:
        diff = final.get(file_type, 0) - baseline.get(file_type, 0)
        differences[file_type] = diff
    
    return differences

def validate_run_results(workspace_path, run_type, baseline_counts, final_counts):
    """Validate run results against expected criteria"""
    validation = {
        "file_creation_check": True,
        "schema_validation": True,
        "frequency_validation": True,
        "resume_validation": True,
        "errors": []
    }
    
    try:
        file_diffs = calculate_file_differences(baseline_counts, final_counts)
        
        # Basic file creation check
        if run_type == "fresh":
            if file_diffs.get("cache_files", 0) <= 0:
                validation["file_creation_check"] = False
                validation["errors"].append("No cache files created")
        
        # Resume validation
        if run_type == "resume":
            # Should process incrementally, not recreate everything
            if file_diffs.get("processing_states", 0) < 0:
                validation["resume_validation"] = False
                validation["errors"].append("Processing state files were deleted during resume")
        
        # Schema validation for created files
        schema_check = validate_file_schemas(workspace_path)
        validation["schema_validation"] = schema_check["valid"]
        if not schema_check["valid"]:
            validation["errors"].extend(schema_check["errors"])
    
    except Exception as e:
        validation["errors"].append(f"Validation error: {e}")
    
    return validation

def validate_file_schemas(workspace_path):
    """Basic schema validation for output files"""
    validation = {"valid": True, "errors": []}
    
    try:
        outputs_dir = workspace_path / "OUTPUTS"
        
        # Check cache files
        cache_dir = outputs_dir / "cached_products"
        if cache_dir.exists():
            for cache_file in cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                        if not isinstance(data, (list, dict)):
                            validation["errors"].append(f"Invalid cache file format: {cache_file.name}")
                except Exception as e:
                    validation["errors"].append(f"Cache file read error: {cache_file.name}")
        
        # Check processing states
        state_dir = outputs_dir / "CACHE" / "processing_states"
        if state_dir.exists():
            for state_file in state_dir.glob("*.json"):
                try:
                    with open(state_file, 'r') as f:
                        data = json.load(f)
                        required_fields = ["current_category_index", "current_product_index_in_category"]
                        for field in required_fields:
                            if field not in data:
                                validation["errors"].append(f"Missing field {field} in {state_file.name}")
                except Exception as e:
                    validation["errors"].append(f"State file read error: {state_file.name}")
    
    except Exception as e:
        validation["valid"] = False
        validation["errors"].append(f"Schema validation error: {e}")
    
    if validation["errors"]:
        validation["valid"] = False
    
    return validation

def analyze_output_files(workspace_path):
    """Analyze output files after test execution"""
    outputs_dir = workspace_path / "OUTPUTS"
    
    print("  Analyzing output files...")
    
    # Count all output files
    file_counts = count_output_files(workspace_path)
    
    print("  File Count Summary:")
    for file_type, count in file_counts.items():
        print(f"    {file_type}: {count} files")
    
    # Check for recent files (created in last hour)
    recent_files = find_recent_files(outputs_dir)
    print(f"  Recent files (last hour): {len(recent_files)}")
    
    for file_path in recent_files[:5]:  # Show first 5
        rel_path = file_path.relative_to(workspace_path)
        file_size = file_path.stat().st_size
        print(f"    {rel_path} ({file_size} bytes)")
    
    # Validate key files exist
    key_files_check = validate_key_files_exist(workspace_path)
    print("  Key Files Validation:")
    for check, status in key_files_check.items():
        status_str = "PASS" if status else "FAIL"
        print(f"    {check}: {status_str}")

def find_recent_files(directory, hours=1):
    """Find files modified in the last N hours"""
    cutoff_time = time.time() - (hours * 3600)
    recent_files = []
    
    try:
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.stat().st_mtime > cutoff_time:
                recent_files.append(file_path)
    except Exception as e:
        print(f"    Warning: Error finding recent files: {e}")
    
    return sorted(recent_files, key=lambda p: p.stat().st_mtime, reverse=True)

def validate_key_files_exist(workspace_path):
    """Validate that key system files exist"""
    checks = {}
    
    # System config
    config_file = workspace_path / "config" / "system_config.json"
    checks["system_config"] = config_file.exists()
    
    # Run scripts
    run_script = workspace_path / "run_custom_poundwholesale.py"
    checks["run_script"] = run_script.exists()
    
    # Core workflow
    workflow_script = workspace_path / "tools" / "passive_extraction_workflow_latest.py"
    checks["workflow_script"] = workflow_script.exists()
    
    # Output directories
    outputs_dir = workspace_path / "OUTPUTS"
    checks["outputs_directory"] = outputs_dir.exists()
    
    return checks

def save_protocol_results(workspace_path, results):
    """Save protocol results to file"""
    try:
        audit_dir = workspace_path / "OUTPUTS" / "AUDIT_REPORTS"
        audit_dir.mkdir(exist_ok=True)
        
        results_file = audit_dir / f"{results['protocol_id']}_results.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")
        
    except Exception as e:
        print(f"Warning: Could not save results: {e}")

def print_results_summary(results):
    """Print a summary of the protocol results"""
    print("\nPROTOCOL RESULTS SUMMARY")
    print("-" * 40)
    print(f"Protocol ID: {results['protocol_id']}")
    print(f"Total Duration: {results['total_duration']:.1f} seconds")
    print(f"Overall Success: {'YES' if results['overall_success'] else 'NO'}")
    
    if 'run_results' in results:
        run1 = results['run_results'].get('run1_fresh', {})
        run2 = results['run_results'].get('run2_resume', {})
        
        print(f"\nRun 1 (Fresh): {'SUCCESS' if run1.get('success') else 'FAILED'}")
        print(f"  Duration: {run1.get('duration', 0):.1f}s")
        print(f"  Products: {run1.get('products_processed', 0)}")
        
        print(f"\nRun 2 (Resume): {'SUCCESS' if run2.get('success') else 'FAILED'}")
        print(f"  Duration: {run2.get('duration', 0):.1f}s")
        print(f"  Products: {run2.get('products_processed', 0)}")
        
        # File creation summary
        if run1.get('files_created'):
            print(f"\nFiles Created in Run 1:")
            for file_type, count in run1['files_created'].items():
                if count > 0:
                    print(f"  {file_type}: {count}")

if __name__ == "__main__":
    main()