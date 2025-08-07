#!/usr/bin/env python3
"""
WSL Compatible Save Function for Linking Maps
Resolves WinError 5 permission failures in WSL environment
"""

import os
import json
import shutil
import tempfile
import stat
from pathlib import Path
import logging

def wsl_compatible_save(data, target_path, log=None):
    """
    WSL-compatible atomic save function with multiple fallback strategies
    
    Strategies:
    1. Enhanced atomic write with explicit permissions
    2. WSL-native temp directory approach  
    3. Multiple fallback methods for reliability
    4. Direct write as last resort
    
    Args:
        data: Data to save (will be JSON serialized)
        target_path: Final file path (Path object or string)
        log: Logger instance (optional)
        
    Returns:
        bool: True if successful, False otherwise
    """
    if log is None:
        log = logging.getLogger(__name__)
        
    target_path = Path(target_path)
    
    # Ensure directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Strategy 1: Enhanced atomic write with explicit permissions
    try:
        log.info(f"🔧 Strategy 1: Enhanced atomic write with permissions for {target_path}")
        
        # Create temp file in same directory for atomic move
        temp_path = target_path.with_suffix(target_path.suffix + '.tmp')
        
        # Write to temp file
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # Set explicit permissions on temp file
        os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)
        
        # Atomic move with os.replace
        os.replace(temp_path, target_path)
        
        # Verify success
        if target_path.exists() and target_path.stat().st_size > 0:
            log.info(f"✅ Strategy 1 SUCCESS: Saved {len(data)} entries to {target_path}")
            return True
            
    except PermissionError as e:
        log.warning(f"⚠️ Strategy 1 FAILED (PermissionError): {e}")
        # Clean up temp file if it exists
        if temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass
    except Exception as e:
        log.warning(f"⚠️ Strategy 1 FAILED (Other): {e}")
        # Clean up temp file if it exists
        if temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass
    
    # Strategy 2: WSL-native temp directory approach
    try:
        log.info(f"🔧 Strategy 2: WSL-native temp directory approach")
        
        # Use system temp directory (typically /tmp in WSL)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
            json.dump(data, temp_file, indent=2, ensure_ascii=False)
            temp_file_path = temp_file.name
            
        # Copy from temp to target
        shutil.copy2(temp_file_path, target_path)
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        # Verify success
        if target_path.exists() and target_path.stat().st_size > 0:
            log.info(f"✅ Strategy 2 SUCCESS: Saved {len(data)} entries to {target_path}")
            return True
            
    except Exception as e:
        log.warning(f"⚠️ Strategy 2 FAILED: {e}")
        # Clean up temp file if it exists
        try:
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
        except:
            pass
    
    # Strategy 3: shutil.move approach
    try:
        log.info(f"🔧 Strategy 3: shutil.move approach")
        
        temp_path = target_path.with_suffix(target_path.suffix + '.tmp2')
        
        # Write to temp file
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # Use shutil.move instead of os.replace
        shutil.move(str(temp_path), str(target_path))
        
        # Verify success
        if target_path.exists() and target_path.stat().st_size > 0:
            log.info(f"✅ Strategy 3 SUCCESS: Saved {len(data)} entries to {target_path}")
            return True
            
    except Exception as e:
        log.warning(f"⚠️ Strategy 3 FAILED: {e}")
        # Clean up temp file if it exists
        if temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass
    
    # Strategy 4: Direct write (last resort - not atomic but works)
    try:
        log.warning(f"🔧 Strategy 4: Direct write (LAST RESORT - not atomic)")
        
        # Remove existing file if it exists
        if target_path.exists():
            target_path.unlink()
            
        # Direct write
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        # Verify success
        if target_path.exists() and target_path.stat().st_size > 0:
            log.warning(f"⚠️ Strategy 4 SUCCESS (non-atomic): Saved {len(data)} entries to {target_path}")
            return True
            
    except Exception as e:
        log.error(f"❌ Strategy 4 FAILED: {e}")
    
    # All strategies failed
    log.error(f"❌ ALL SAVE STRATEGIES FAILED for {target_path}")
    return False


def test_wsl_save():
    """Test the WSL-compatible save function"""
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
    
    test_path = Path("/tmp/test_linking_map.json")
    
    # Test the save function
    success = wsl_compatible_save(test_data, test_path)
    
    if success:
        print(f"✅ Test SUCCESS: Saved to {test_path}")
        
        # Verify the data
        with open(test_path, 'r') as f:
            loaded_data = json.load(f)
            
        print(f"✅ Verification: Loaded {len(loaded_data)} entries")
        
        # Clean up
        test_path.unlink()
        
    else:
        print(f"❌ Test FAILED")
        
    return success


if __name__ == "__main__":
    test_wsl_save()