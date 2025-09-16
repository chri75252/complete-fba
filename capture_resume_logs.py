#!/usr/bin/env python3
"""
Capture and analyze resume logs for Category A Run 2
"""

import subprocess
import sys
import time
import os
from datetime import datetime

def capture_resume_behavior():
    """Capture the resume behavior and startup logs"""
    
    print("=" * 80)
    print("CATEGORY A - RUN 2: RESUME VERIFICATION TEST")
    print("=" * 80)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("MONITORING FOR:")
    print("✓ Resume detection messages")
    print("✓ Exact resumption pointer (cat_idx=0, prod_idx=8)")
    print("✓ Proof banners (FIRST_AFTER_RESUME, RESUME HONORED)")
    print("✓ Phase detection (amazon_analysis)")
    print("✓ Processing counter continuation from 10,451")
    print("=" * 80)
    print()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    log_file = f"resume_test_A_run2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Resume Test A Run 2 - {datetime.now()}\n")
            f.write("=" * 80 + "\n\n")
            
            # Start process
            process = subprocess.Popen(
                [sys.executable, "run_custom_poundwholesale.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            start_time = time.time()
            line_count = 0
            
            # Key tracking variables
            resume_indicators = []
            proof_banners = []
            phase_confirmations = []
            pointer_confirmations = []
            processing_increments = []
            
            print("LIVE CAPTURE:")
            print("-" * 60)
            
            # Monitor for up to 2 minutes
            while time.time() - start_time < 120:
                line = process.stdout.readline()
                if not line:
                    if process.poll() is not None:
                        break
                    time.sleep(0.1)
                    continue
                
                line = line.strip()
                if line:
                    line_count += 1
                    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    formatted_line = f"[{timestamp}] {line}"
                    
                    # Write to log
                    f.write(formatted_line + "\n")
                    f.flush()
                    
                    # Display and analyze
                    print(formatted_line)
                    
                    # Check for key indicators
                    line_lower = line.lower()
                    
                    # Resume detection
                    if any(word in line_lower for word in ['resume', 'resuming', 'resumption']):
                        resume_indicators.append(line)
                        print(f"🔄 RESUME DETECTED: {line}")
                    
                    # Proof banners
                    if any(banner in line for banner in ['FIRST_AFTER_RESUME', 'RESUME HONORED', 'RESUMING FROM']):
                        proof_banners.append(line)
                        print(f"🎯 PROOF BANNER: {line}")
                    
                    # Exact pointer confirmation
                    if 'cat_idx=0' in line and 'prod_idx=8' in line:
                        pointer_confirmations.append(line)
                        print(f"📍 POINTER CONFIRMED: {line}")
                    
                    # Phase detection
                    if 'amazon_analysis' in line_lower or 'phase:' in line_lower:
                        phase_confirmations.append(line)
                        print(f"🔍 PHASE DETECTED: {line}")
                    
                    # Processing increments
                    if 'processed:' in line_lower or 'successful_products:' in line:
                        processing_increments.append(line)
                        if '10,451' in line or '10451' in line:
                            print(f"📊 COUNTER CONTINUATION: {line}")
                
                # Let it run for a good sample
                if time.time() - start_time > 90:  # 1.5 minutes
                    print("\n⏱️  Sample period complete, terminating...")
                    break
            
            # Graceful shutdown
            print("\n🛑 Terminating process...")
            process.terminate()
            time.sleep(3)
            
            if process.poll() is None:
                process.kill()
                process.wait()
            
            # Write summary to log
            f.write("\n" + "=" * 80 + "\n")
            f.write("RESUME TEST SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Duration: {time.time() - start_time:.1f} seconds\n")
            f.write(f"Lines captured: {line_count}\n")
            f.write(f"Resume indicators: {len(resume_indicators)}\n")
            f.write(f"Proof banners: {len(proof_banners)}\n")
            f.write(f"Pointer confirmations: {len(pointer_confirmations)}\n")
            f.write(f"Phase confirmations: {len(phase_confirmations)}\n")
            f.write(f"Processing increments: {len(processing_increments)}\n\n")
            
            # Write detailed findings
            for category, items in [
                ("RESUME INDICATORS", resume_indicators),
                ("PROOF BANNERS", proof_banners), 
                ("POINTER CONFIRMATIONS", pointer_confirmations),
                ("PHASE CONFIRMATIONS", phase_confirmations),
                ("PROCESSING INCREMENTS", processing_increments[:5])  # First 5 only
            ]:
                if items:
                    f.write(f"{category}:\n")
                    for item in items:
                        f.write(f"  - {item}\n")
                    f.write("\n")
        
        # Console summary
        print("\n" + "=" * 80)
        print("RESUME TEST ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"📁 Log saved to: {log_file}")
        print(f"⏱️  Duration: {time.time() - start_time:.1f} seconds")
        print(f"📄 Lines captured: {line_count}")
        print()
        print("KEY FINDINGS:")
        print(f"🔄 Resume indicators found: {len(resume_indicators)}")
        print(f"🎯 Proof banners detected: {len(proof_banners)}")
        print(f"📍 Pointer confirmations: {len(pointer_confirmations)}")
        print(f"🔍 Phase confirmations: {len(phase_confirmations)}")
        print(f"📊 Processing increments: {len(processing_increments)}")
        
        # Success assessment
        success_criteria = [
            len(resume_indicators) > 0,
            len(pointer_confirmations) > 0,
            len(phase_confirmations) > 0
        ]
        
        success_rate = sum(success_criteria) / len(success_criteria) * 100
        print(f"\n✅ Resume Test Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 75:
            print("🎉 RESUME TEST PASSED - System properly detected and honored resume state")
        else:
            print("❌ RESUME TEST FAILED - Missing critical resume indicators")
        
        return log_file
        
    except Exception as e:
        print(f"❌ Error during capture: {e}")
        return None

if __name__ == "__main__":
    capture_resume_behavior()