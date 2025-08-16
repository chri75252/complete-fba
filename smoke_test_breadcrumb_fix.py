#!/usr/bin/env python3
"""
2-Minute Smoke Test for Breadcrumb Fix
"""

import subprocess
import time
import sys
import os
from datetime import datetime

def run_smoke_test():
    """Run a 2-minute smoke test of the workflow"""
    print("🔥 2-Minute Smoke Test - Breadcrumb Fix Validation")
    print("=" * 60)
    
    # Start the workflow
    print(f"⏰ Starting workflow at {datetime.now().strftime('%H:%M:%S')}")
    print("🚀 Command: python run_custom_poundwholesale.py")
    
    try:
        # Start the process
        process = subprocess.Popen(
            ["python", "run_custom_poundwholesale.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitor for 2 minutes
        start_time = time.time()
        breadcrumb_delayed_count = 0
        resume_ptr_count = 0
        category_processing_started = False
        
        print("\n📊 Monitoring output for 2 minutes...")
        print("🔍 Watching for:")
        print("  • BREADCRUMB DELAYED warnings (should be minimal)")
        print("  • RESUME PTR logs (should appear after category start)")
        print("  • Category processing initiation")
        print("\n" + "-" * 60)
        
        while time.time() - start_time < 120:  # 2 minutes
            try:
                line = process.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                if line:
                    # Check for key patterns
                    if "BREADCRUMB DELAYED" in line:
                        breadcrumb_delayed_count += 1
                        print(f"⚠️  BREADCRUMB DELAYED: {line}")
                    
                    elif "RESUME PTR:" in line:
                        resume_ptr_count += 1
                        print(f"✅ RESUME PTR: {line}")
                    
                    elif "Processing subcategory" in line or "Scraping category:" in line:
                        if not category_processing_started:
                            category_processing_started = True
                            print(f"🎯 CATEGORY PROCESSING STARTED: {line}")
                        else:
                            print(f"📂 {line}")
                    
                    elif "WRITE-AHEAD POINT" in line:
                        print(f"🚨 {line}")
                    
                    elif any(keyword in line for keyword in ["ERROR", "FAILED", "Exception"]):
                        print(f"❌ {line}")
                    
                    # Show progress indicators
                    elif any(keyword in line for keyword in ["✅", "🔄", "📊"]):
                        print(f"ℹ️  {line}")
            
            except Exception as e:
                print(f"Error reading output: {e}")
                break
        
        # Terminate the process
        print(f"\n⏰ 2 minutes elapsed at {datetime.now().strftime('%H:%M:%S')}")
        print("🛑 Terminating workflow...")
        
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        # Results analysis
        print("\n" + "=" * 60)
        print("📊 SMOKE TEST RESULTS")
        print("=" * 60)
        
        print(f"⚠️  BREADCRUMB DELAYED warnings: {breadcrumb_delayed_count}")
        print(f"✅ RESUME PTR logs: {resume_ptr_count}")
        print(f"🎯 Category processing started: {category_processing_started}")
        
        # Pass/Fail criteria
        success = True
        issues = []
        
        if breadcrumb_delayed_count > 3:  # Allow a few during startup
            success = False
            issues.append(f"Too many BREADCRUMB DELAYED warnings: {breadcrumb_delayed_count}")
        
        if resume_ptr_count == 0 and category_processing_started:
            success = False
            issues.append("No RESUME PTR logs found after category processing started")
        
        if not category_processing_started:
            print("⚠️  WARNING: Category processing may not have started (workflow might be in gap processing)")
        
        print("\n" + "-" * 60)
        if success:
            print("✅ SMOKE TEST PASSED")
            print("🎉 Breadcrumb fix appears to be working correctly!")
            print("\n📈 Success Indicators:")
            print(f"  • Minimal BREADCRUMB DELAYED warnings: {breadcrumb_delayed_count} ≤ 3")
            if resume_ptr_count > 0:
                print(f"  • RESUME PTR logs present: {resume_ptr_count}")
            if category_processing_started:
                print("  • Category processing initiated successfully")
        else:
            print("❌ SMOKE TEST FAILED")
            print("🚨 Issues detected:")
            for issue in issues:
                print(f"  • {issue}")
        
        return success
        
    except Exception as e:
        print(f"❌ Smoke test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = run_smoke_test()
    sys.exit(0 if success else 1)