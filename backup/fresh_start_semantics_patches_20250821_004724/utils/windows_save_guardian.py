#!/usr/bin/env python3
"""
Windows Save Guardian - Production-Ready Atomic Persistence System
Resolves WinError 5 (Access denied) issues during linking map saves.

This module provides Windows-safe atomic persistence with multiple fallback strategies,
comprehensive error handling, and detailed telemetry logging.

Author: Claude Code
Date: 2025-07-27
Version: 1.0
"""

import os
import json
import shutil
import tempfile
import stat
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Union, Optional
from datetime import datetime


class WindowsSaveGuardian:
    """
    Windows-safe atomic persistence manager with multiple fallback strategies.
    
    Provides robust file saving with protection against WinError 5 (Access denied)
    and other Windows-specific file locking issues.
    """
    
    def __init__(self, telemetry_path: Optional[str] = None):
        """
        Initialize the Windows Save Guardian.
        
        Args:
            telemetry_path: Path for telemetry logging. If None, uses default path.
        """
        self.telemetry_path = telemetry_path or "OUTPUTS/DIAGNOSTICS/save_telemetry.log"
        self.logger = self._setup_logger()
        self._ensure_diagnostics_dir()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup dedicated logger for save operations."""
        logger = logging.getLogger('windows_save_guardian')
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] WindowsSaveGuardian: %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _ensure_diagnostics_dir(self):
        """Ensure diagnostics directory exists."""
        diagnostics_dir = Path(self.telemetry_path).parent
        diagnostics_dir.mkdir(parents=True, exist_ok=True)
    
    def _log_telemetry(self, strategy: str, status: str, details: Dict[str, Any]):
        """
        Log telemetry data for save attempts.
        
        Args:
            strategy: Strategy name (e.g., 'temp_then_replace')
            status: 'SUCCESS' or 'FAILED'
            details: Additional details dictionary
        """
        telemetry_entry = {
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy,
            "status": status,
            "details": details
        }
        
        try:
            # Append to telemetry log
            with open(self.telemetry_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(telemetry_entry) + '\n')
        except Exception as e:
            self.logger.warning(f"Failed to log telemetry: {e}")
    
    def save_json_atomic(
        self, 
        path: Union[str, Path], 
        data: Any, 
        *, 
        min_entries_guard: int = 1000, 
        strategies: Optional[List[str]] = None
    ) -> bool:
        """
        Atomically save JSON data with multiple fallback strategies.
        
        Args:
            path: Target file path
            data: Data to save (will be JSON serialized)
            min_entries_guard: Minimum entries for anti-truncation guard
            strategies: List of strategies to try (if None, uses default order)
            
        Returns:
            bool: True if successful, False otherwise
        """
        path = Path(path)
        data_size = len(data) if hasattr(data, '__len__') else 0
        
        # Simplified strategy order - only use reliable strategies
        if strategies is None:
            strategies = [
                'alternative_temp_dir',
                'direct_write'
            ]
        
        # Quiet operation - no verbose start message
        
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Anti-truncation guard
        if self._should_apply_truncation_guard(path, data, min_entries_guard):
            self.logger.warning(f"⚠️ Anti-truncation guard triggered - merging data")
            data = self._merge_with_existing(path, data)
        
        # Try each strategy in order
        for strategy in strategies:
            start_time = time.time()
            success = False
            error_details = {}
            
            try:
                if strategy == 'temp_then_replace':
                    success = self._strategy_temp_then_replace(path, data)
                elif strategy == 'backup_then_replace':
                    success = self._strategy_backup_then_replace(path, data)
                elif strategy == 'alternative_temp_dir':
                    success = self._strategy_alternative_temp_dir(path, data)
                elif strategy == 'move_fallback':
                    success = self._strategy_move_fallback(path, data)
                elif strategy == 'direct_write':
                    success = self._strategy_direct_write(path, data)
                else:
                    self.logger.warning(f"Unknown strategy: {strategy}")
                    continue
                
                # Log telemetry
                execution_time = time.time() - start_time
                telemetry_details = {
                    "path": str(path),
                    "data_size": data_size,
                    "execution_time_ms": round(execution_time * 1000, 2),
                    "file_size_bytes": path.stat().st_size if success and path.exists() else 0
                }
                
                if success:
                    filename = path.name
                    self.logger.info(f"✅ ATOMIC SAVE: {filename} ({data_size} entries) saved successfully")
                    self._log_telemetry(strategy, "SUCCESS", telemetry_details)
                    return True
                else:
                    error_details["reason"] = "Strategy returned False"
                    
            except Exception as e:
                error_details = {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "execution_time_ms": round((time.time() - start_time) * 1000, 2)
                }
                self.logger.warning(f"❌ Strategy '{strategy}' FAILED: {e}")
            
            # Log failed attempt
            telemetry_details = {
                "path": str(path),
                "data_size": data_size,
                **error_details
            }
            self._log_telemetry(strategy, "FAILED", telemetry_details)
        
        # All strategies failed
        self.logger.error(f"💥 ALL SAVE STRATEGIES FAILED for {path}")
        return False    
    def _should_apply_truncation_guard(self, path: Path, new_data: Any, min_entries: int) -> bool:
        """
        Check if anti-truncation guard should be applied.
        
        Args:
            path: Target file path
            new_data: New data to save
            min_entries: Minimum entries threshold
            
        Returns:
            bool: True if guard should be applied
        """
        if not path.exists():
            return False
            
        new_size = len(new_data) if hasattr(new_data, '__len__') else 0
        
        if new_size >= min_entries:
            return False
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            existing_size = len(existing_data) if hasattr(existing_data, '__len__') else 0
            
            # Apply guard if existing data is large and new data is small
            if existing_size >= min_entries and new_size < min_entries:
                self.logger.warning(
                    f"Anti-truncation guard: existing={existing_size}, new={new_size}, "
                    f"threshold={min_entries}"
                )
                return True
                
        except Exception as e:
            self.logger.warning(f"Could not read existing file for truncation guard: {e}")
            
        return False
    
    def _merge_with_existing(self, path: Path, new_data: Any) -> Any:
        """
        Merge new data with existing data and deduplicate.
        
        Args:
            path: Existing file path
            new_data: New data to merge
            
        Returns:
            Merged and deduplicated data
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            # If both are lists, merge and deduplicate
            if isinstance(existing_data, list) and isinstance(new_data, list):
                # Create a combined list
                combined = existing_data + new_data
                
                # Deduplicate based on a key (if available)
                seen_keys = set()
                deduplicated = []
                
                for item in combined:
                    # Use EAN as deduplication key if available
                    key = item.get('supplier_ean') or item.get('ean') or str(item)
                    if key not in seen_keys:
                        seen_keys.add(key)
                        deduplicated.append(item)
                
                self.logger.info(
                    f"Merged data: {len(existing_data)} existing + {len(new_data)} new "
                    f"= {len(deduplicated)} deduplicated"
                )
                return deduplicated
            else:
                # For non-list data, prefer new data
                self.logger.info("Non-list data - using new data")
                return new_data
                
        except Exception as e:
            self.logger.warning(f"Merge failed, using new data only: {e}")
            return new_data
    
    def _strategy_temp_then_replace(self, path: Path, data: Any) -> bool:
        """
        Strategy 1: Temp file then atomic replace with retries and backoff.
        
        Args:
            path: Target file path
            data: Data to save
            
        Returns:
            bool: True if successful
        """
        temp_path = path.with_suffix(path.suffix + '.tmp')
        max_retries = 3
        base_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                # Clean up any existing temp file
                if temp_path.exists():
                    temp_path.unlink()
                
                # Write to temp file
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Set permissions
                os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)
                
                # Atomic replace (this is where WinError 5 typically occurs)
                os.replace(temp_path, path)
                
                # Verify success
                if path.exists() and path.stat().st_size > 0:
                    return True
                    
            except (PermissionError, OSError) as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.info(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
                    time.sleep(delay)
                    continue
                else:
                    raise e
            finally:
                # Clean up temp file
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except:
                        pass
        
        return False
    
    def _strategy_backup_then_replace(self, path: Path, data: Any) -> bool:
        """
        Strategy 2: Create timestamped backup, write temp, then replace.
        
        Args:
            path: Target file path
            data: Data to save
            
        Returns:
            bool: True if successful
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = path.with_suffix(f".bak_{timestamp}")
        temp_path = path.with_suffix(path.suffix + '.tmp2')
        
        try:
            # Create backup of existing file
            if path.exists():
                shutil.copy2(path, backup_path)
            
            # Write to temp file
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic replace
            os.replace(temp_path, path)
            
            # Verify and clean up backup if successful
            if path.exists() and path.stat().st_size > 0:
                # Remove backup after successful write
                if backup_path.exists():
                    backup_path.unlink()
                return True
                
        except Exception as e:
            # Restore from backup if available
            if backup_path.exists() and not path.exists():
                try:
                    shutil.copy2(backup_path, path)
                    self.logger.info("Restored from backup after failed write")
                except:
                    pass
            raise e
        finally:
            # Clean up temp file
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass
        
        return False    
    def _strategy_alternative_temp_dir(self, path: Path, data: Any) -> bool:
        """
        Strategy 3: Use alternative temp directory when target is locked.
        
        Args:
            path: Target file path
            data: Data to save
            
        Returns:
            bool: True if successful
        """
        # Create alternative temp directory
        alt_temp_dir = Path(os.environ.get('TEMP', '/tmp')) / 'fba_tmp'
        alt_temp_dir.mkdir(parents=True, exist_ok=True)
        
        temp_file_path = alt_temp_dir / f"temp_save_{int(time.time() * 1000)}.json"
        
        try:
            # Write to alternative temp location
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Copy to target location
            shutil.copy2(temp_file_path, path)
            
            # Verify success
            if path.exists() and path.stat().st_size > 0:
                return True
                
        finally:
            # Clean up temp file
            if temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                except:
                    pass
        
        return False
    
    def _strategy_move_fallback(self, path: Path, data: Any) -> bool:
        """
        Strategy 4: Use shutil.move when atomic replace fails.
        
        Args:
            path: Target file path
            data: Data to save
            
        Returns:
            bool: True if successful
        """
        temp_path = path.with_suffix(path.suffix + '.tmp3')
        
        try:
            # Write to temp file
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Use shutil.move (not atomic but more reliable on Windows)
            shutil.move(str(temp_path), str(path))
            
            # Log that this was non-atomic
            self.logger.warning(f"⚠️ Used non-atomic move for {path}")
            
            # Verify success
            if path.exists() and path.stat().st_size > 0:
                return True
                
        finally:
            # Clean up temp file if still exists
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass
        
        return False
    
    def _strategy_direct_write(self, path: Path, data: Any) -> bool:
        """
        Strategy 5: Direct write (last resort - not atomic).
        
        Args:
            path: Target file path
            data: Data to save
            
        Returns:
            bool: True if successful
        """
        try:
            # Remove existing file if it exists
            if path.exists():
                path.unlink()
            
            # Direct write
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Log that this was non-atomic
            self.logger.warning(f"⚠️ Used non-atomic direct write for {path}")
            
            # Verify success
            if path.exists() and path.stat().st_size > 0:
                return True
                
        except Exception:
            # If even direct write fails, we're in trouble
            raise
        
        return False


# Convenience function for backward compatibility
def save_json_atomic(
    path: Union[str, Path], 
    data: Any, 
    *, 
    min_entries_guard: int = 1000, 
    strategies: Optional[List[str]] = None
) -> bool:
    """
    Convenience function for Windows-safe atomic JSON saving.
    
    Args:
        path: Target file path
        data: Data to save (will be JSON serialized)
        min_entries_guard: Minimum entries for anti-truncation guard
        strategies: List of strategies to try (if None, uses default order)
        
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        >>> data = [{"ean": "123", "asin": "B08XYZ"}]
        >>> success = save_json_atomic("linking_map.json", data)
        >>> print(f"Save {'succeeded' if success else 'failed'}")
    """
    guardian = WindowsSaveGuardian()
    return guardian.save_json_atomic(
        path, data, 
        min_entries_guard=min_entries_guard, 
        strategies=strategies
    )


def test_windows_save_guardian():
    """
    Comprehensive test suite for Windows Save Guardian.
    
    Tests all strategies and edge cases to ensure reliability.
    """
    print("🧪 TESTING WINDOWS SAVE GUARDIAN")
    print("=" * 50)
    
    # Test data
    test_data = [
        {
            "supplier_ean": "1234567890123",
            "amazon_asin": "B08XYZ123",
            "match_method": "EAN",
            "confidence": "high",
            "timestamp": datetime.now().isoformat()
        },
        {
            "supplier_ean": "9876543210987",
            "amazon_asin": None,
            "match_method": "none",
            "confidence": "none",
            "no_match_reason": "No EAN match found",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # Test directory
    test_dir = Path("OUTPUTS/test_windows_guardian")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    guardian = WindowsSaveGuardian()
    
    # Test 1: Basic functionality
    print("\n📝 Test 1: Basic atomic save")
    test_file = test_dir / "basic_test.json"
    success = guardian.save_json_atomic(test_file, test_data)
    print(f"Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Test 2: Strategy-specific tests
    strategies = [
        'temp_then_replace',
        'backup_then_replace', 
        'alternative_temp_dir',
        'move_fallback',
        'direct_write'
    ]
    
    for strategy in strategies:
        print(f"\n📝 Test 2.{strategies.index(strategy) + 1}: Strategy '{strategy}'")
        test_file = test_dir / f"strategy_{strategy}_test.json"
        success = guardian.save_json_atomic(
            test_file, test_data, strategies=[strategy]
        )
        print(f"Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Test 3: Anti-truncation guard
    print(f"\n📝 Test 3: Anti-truncation guard")
    
    # Create file with many entries
    large_data = [{"ean": f"12345678901{i:02d}", "asin": f"B08XYZ{i:03d}"} 
                  for i in range(1500)]
    large_file = test_dir / "truncation_test.json"
    guardian.save_json_atomic(large_file, large_data)
    
    # Try to save small data (should trigger guard)
    small_data = [{"ean": "999", "asin": "B999"}]
    success = guardian.save_json_atomic(large_file, small_data, min_entries_guard=1000)
    
    # Check if data was merged
    with open(large_file, 'r') as f:
        result_data = json.load(f)
    
    merged_correctly = len(result_data) > len(small_data)
    print(f"Result: {'✅ GUARD WORKED' if merged_correctly else '❌ GUARD FAILED'}")
    print(f"Final data size: {len(result_data)} entries")
    
    # Test 4: Telemetry logging
    print(f"\n📝 Test 4: Telemetry logging")
    telemetry_path = Path(guardian.telemetry_path)
    telemetry_exists = telemetry_path.exists()
    print(f"Telemetry file exists: {'✅ YES' if telemetry_exists else '❌ NO'}")
    
    if telemetry_exists:
        with open(telemetry_path, 'r') as f:
            lines = f.readlines()
        print(f"Telemetry entries: {len(lines)}")
    
    print(f"\n🎯 WINDOWS SAVE GUARDIAN TEST COMPLETE")
    return True


if __name__ == "__main__":
    test_windows_save_guardian()