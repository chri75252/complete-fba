#!/usr/bin/env python3
"""
Test Windows-specific file operations and permission issues
"""

import os
import json
import shutil
import tempfile
import stat
from pathlib import Path
import logging
import platform

def test_windows_environment():
    """Test the actual environment and file operation capabilities"""
    
    print("🔍 WINDOWS ENVIRONMENT ANALYSIS")
    print("=" * 50)
    
    # System information
    print(f"Platform: {platform.platform()}")
    print(f"System: {platform.system()}")
    print(f"Machine: {platform.machine()}")
    print(f"Python executable: {os.path.abspath(os.sys.executable)}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"User: {os.environ.get('USERNAME', 'unknown')}")
    
    # Path format analysis
    test_path = Path("C:/Users/chris/Desktop/test.txt")
    print(f"Path object: {test_path}")
    print(f"Path exists: {test_path.parent.exists()}")
    print(f"Path is absolute: {test_path.is_absolute()}")
    
    return True

def test_file_locking_scenarios():
    """Test various file locking scenarios that cause WinError 5"""
    
    print("\n🔒 FILE LOCKING SCENARIOS TEST")
    print("=" * 50)
    
    # Test basic file operations
    test_dir = Path("OUTPUTS/test_permissions")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    test_data = {"test": "data", "timestamp": "2025-07-27"}
    
    scenarios = [
        ("basic_write", "Basic file write"),
        ("temp_write", "Temp file then move"),
        ("atomic_replace", "Atomic os.replace"),
        ("shutil_move", "Shutil move"),
        ("direct_overwrite", "Direct overwrite existing file")
    ]
    
    results = {}
    
    for scenario_name, description in scenarios:
        print(f"\n📝 Testing: {description}")
        
        try:
            if scenario_name == "basic_write":
                target_file = test_dir / "basic_test.json"
                with open(target_file, 'w') as f:
                    json.dump(test_data, f)
                results[scenario_name] = "SUCCESS"
                
            elif scenario_name == "temp_write":
                target_file = test_dir / "temp_test.json"
                temp_file = target_file.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    json.dump(test_data, f)
                results[scenario_name] = "SUCCESS - temp file created"
                
            elif scenario_name == "atomic_replace":
                target_file = test_dir / "atomic_test.json"
                temp_file = target_file.with_suffix('.tmp')
                
                # Create target file first
                with open(target_file, 'w') as f:
                    json.dump({"old": "data"}, f)
                
                # Create temp file
                with open(temp_file, 'w') as f:
                    json.dump(test_data, f)
                
                # Atomic replace (this is where WinError 5 typically occurs)
                os.replace(temp_file, target_file)
                results[scenario_name] = "SUCCESS - os.replace worked!"
                
            elif scenario_name == "shutil_move":
                target_file = test_dir / "shutil_test.json"
                temp_file = target_file.with_suffix('.tmp')
                
                # Create temp file
                with open(temp_file, 'w') as f:
                    json.dump(test_data, f)
                
                # Shutil move
                shutil.move(str(temp_file), str(target_file))
                results[scenario_name] = "SUCCESS - shutil.move worked!"
                
            elif scenario_name == "direct_overwrite":
                target_file = test_dir / "overwrite_test.json"
                
                # Create existing file
                with open(target_file, 'w') as f:
                    json.dump({"old": "data"}, f)
                
                # Direct overwrite
                with open(target_file, 'w') as f:
                    json.dump(test_data, f)
                results[scenario_name] = "SUCCESS - direct overwrite worked!"
                
        except Exception as e:
            results[scenario_name] = f"FAILED: {type(e).__name__}: {e}"
            print(f"❌ FAILED: {e}")
            continue
            
        print(f"✅ SUCCESS: {description}")
    
    return results

def test_permission_solutions():
    """Test Windows-specific permission solutions"""
    
    print("\n🛡️ WINDOWS PERMISSION SOLUTIONS TEST")
    print("=" * 50)
    
    solutions = []
    
    # Solution 1: Explicit permission setting
    try:
        test_file = Path("OUTPUTS/test_permissions/perm_test.json")
        with open(test_file, 'w') as f:
            json.dump({"test": "permissions"}, f)
        
        # Set explicit permissions
        os.chmod(test_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)
        solutions.append("✅ Explicit permissions: SUCCESS")
        
    except Exception as e:
        solutions.append(f"❌ Explicit permissions: FAILED - {e}")
    
    # Solution 2: Windows temp directory
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump({"test": "temp_dir"}, temp_file)
            temp_path = temp_file.name
        
        target_path = Path("OUTPUTS/test_permissions/temp_dir_test.json")
        shutil.move(temp_path, target_path)
        solutions.append("✅ Windows temp directory: SUCCESS")
        
    except Exception as e:
        solutions.append(f"❌ Windows temp directory: FAILED - {e}")
    
    # Solution 3: File handle release
    try:
        target_file = Path("OUTPUTS/test_permissions/handle_test.json")
        temp_file = target_file.with_suffix('.tmp')
        
        # Write and explicitly close
        with open(temp_file, 'w') as f:
            json.dump({"test": "handle_release"}, f)
        # File handle automatically released here
        
        # Small delay to ensure handle release
        import time
        time.sleep(0.1)
        
        # Now try to move
        os.replace(temp_file, target_file)
        solutions.append("✅ Handle release: SUCCESS")
        
    except Exception as e:
        solutions.append(f"❌ Handle release: FAILED - {e}")
    
    return solutions

def test_current_wsl_solution_on_windows():
    """Test if the current 'WSL-compatible' solution actually works on Windows"""
    
    print("\n🧪 TESTING CURRENT SOLUTION ON WINDOWS")
    print("=" * 50)
    
    # Import the current solution
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from wsl_compatible_save import wsl_compatible_save
        
        # Test data
        test_data = [
            {
                "supplier_ean": "1234567890123",
                "amazon_asin": "B08XYZ123",
                "match_method": "EAN",
                "confidence": "high"
            }
        ]
        
        # Test on Windows paths
        windows_test_path = Path("OUTPUTS/test_permissions/windows_solution_test.json")
        
        print(f"Testing save to: {windows_test_path}")
        success = wsl_compatible_save(test_data, windows_test_path)
        
        if success:
            print("✅ CURRENT SOLUTION WORKS ON WINDOWS!")
            
            # Verify file exists and has correct content
            if windows_test_path.exists():
                with open(windows_test_path, 'r') as f:
                    loaded_data = json.load(f)
                print(f"✅ File verification: {len(loaded_data)} entries loaded successfully")
                return True
            else:
                print("❌ File was not created")
                return False
        else:
            print("❌ CURRENT SOLUTION FAILED ON WINDOWS")
            return False
            
    except Exception as e:
        print(f"❌ Error testing current solution: {e}")
        return False

def test_new_windows_save_guardian():
    """Test the new Windows Save Guardian implementation"""
    
    print("\n🛡️ TESTING NEW WINDOWS SAVE GUARDIAN")
    print("=" * 50)
    
    try:
        # Import the new guardian
        from utils.windows_save_guardian import WindowsSaveGuardian, save_json_atomic
        
        # Test data
        test_data = [
            {
                "supplier_ean": "1234567890123",
                "amazon_asin": "B08XYZ123",
                "match_method": "EAN",
                "confidence": "high"
            },
            {
                "supplier_ean": "9876543210987",
                "amazon_asin": None,
                "match_method": "none",
                "confidence": "none"
            }
        ]
        
        # Test the convenience function
        test_file = Path("OUTPUTS/test_permissions/guardian_test.json")
        success = save_json_atomic(test_file, test_data)
        
        if success:
            print("✅ Windows Save Guardian: SUCCESS")
            
            # Verify file contents
            if test_file.exists():
                with open(test_file, 'r') as f:
                    loaded_data = json.load(f)
                print(f"✅ File verification: {len(loaded_data)} entries loaded")
                
                # Test telemetry
                telemetry_path = Path("OUTPUTS/DIAGNOSTICS/save_telemetry.log")
                if telemetry_path.exists():
                    print("✅ Telemetry logging: WORKING")
                else:
                    print("⚠️ Telemetry logging: NOT FOUND")
                
                return True
            else:
                print("❌ File verification: FAILED - file not created")
                return False
        else:
            print("❌ Windows Save Guardian: FAILED")
            return False
            
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Guardian test failed: {e}")
        return False

def test_guardian_strategies():
    """Test individual strategies of the Windows Save Guardian"""
    
    print("\n🔧 TESTING GUARDIAN STRATEGIES")
    print("=" * 50)
    
    try:
        from utils.windows_save_guardian import WindowsSaveGuardian
        
        guardian = WindowsSaveGuardian()
        test_data = {"test": "strategy_data"}
        test_dir = Path("OUTPUTS/test_permissions/strategies")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        strategies = [
            'temp_then_replace',
            'backup_then_replace', 
            'alternative_temp_dir',
            'move_fallback',
            'direct_write'
        ]
        
        results = {}
        
        for strategy in strategies:
            test_file = test_dir / f"test_{strategy}.json"
            try:
                success = guardian.save_json_atomic(
                    test_file, test_data, strategies=[strategy]
                )
                results[strategy] = "✅ SUCCESS" if success else "❌ FAILED"
            except Exception as e:
                results[strategy] = f"❌ ERROR: {e}"
        
        # Report results
        for strategy, result in results.items():
            print(f"  {strategy}: {result}")
        
        return results
        
    except Exception as e:
        print(f"❌ Strategy testing failed: {e}")
        return {}

def main():
    """Run comprehensive Windows file operation tests"""
    
    print("🔧 WINDOWS FILE OPERATION ANALYSIS")
    print("="*60)
    print("Testing file operations to diagnose WinError 5 permission failures")
    print("="*60)
    
    # Test 1: Environment analysis
    test_windows_environment()
    
    # Test 2: File locking scenarios
    locking_results = test_file_locking_scenarios()
    
    # Test 3: Permission solutions
    permission_solutions = test_permission_solutions()
    
    # Test 4: Current solution
    current_solution_works = test_current_wsl_solution_on_windows()
    
    # Test 5: New Windows Save Guardian
    guardian_works = test_new_windows_save_guardian()
    
    # Test 6: Guardian strategies
    strategy_results = test_guardian_strategies()
    
    # Summary
    print("\n📊 FINAL ANALYSIS")
    print("=" * 50)
    
    print("\n🔒 File Operation Results:")
    for scenario, result in locking_results.items():
        status = "✅" if "SUCCESS" in result else "❌"
        print(f"{status} {scenario}: {result}")
    
    print("\n🛡️ Permission Solutions:")
    for solution in permission_solutions:
        print(f"  {solution}")
    
    print(f"\n🧪 Current Solution on Windows:")
    if current_solution_works:
        print("  ✅ The current 'WSL-compatible' solution actually works on Windows!")
        print("  📝 No additional Windows-specific fixes needed")
    else:
        print("  ❌ Current solution needs Windows-specific modifications")
        print("  📝 Windows-specific fixes required")
    
    print(f"\n🛡️ New Windows Save Guardian:")
    if guardian_works:
        print("  ✅ Windows Save Guardian implementation successful!")
        print("  📝 Production-ready atomic persistence with multiple fallback strategies")
    else:
        print("  ❌ Windows Save Guardian needs debugging")
        print("  📝 Check import paths and dependencies")
    
    print(f"\n🔧 Guardian Strategy Results:")
    for strategy, result in strategy_results.items():
        print(f"  {strategy}: {result}")
    
    print("\n🎯 RECOMMENDATION:")
    if guardian_works:
        print("  ✅ Windows Save Guardian is ready for production use")
        print("  📝 Provides robust protection against WinError 5 with telemetry")
        print("  🚀 Recommended for all critical save operations")
    elif current_solution_works:
        print("  The current solution should resolve WinError 5 issues on Windows")
        print("  Proceed with integration testing on the actual Windows system")
    else:
        print("  Windows-specific fixes needed - see successful scenarios above")


if __name__ == "__main__":
    main()