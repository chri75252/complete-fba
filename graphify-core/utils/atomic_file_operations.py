#!/usr/bin/env python3
"""
Atomic File Operations Module
Provides thread-safe, atomic file operations with cross-platform file locking
"""

import os
import json
import time
import fcntl
import tempfile
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import contextmanager

class AtomicFileOperations:
    """Thread-safe atomic file operations with file locking."""
    
    def __init__(self):
        self._locks = {}
        self._global_lock = threading.Lock()
    
    @contextmanager
    def file_lock(self, file_path: Path, timeout: float = 5.0):
        """Cross-platform file locking context manager."""
        lock_path = file_path.with_suffix(file_path.suffix + '.lock')
        
        try:
            # Create lock file
            with open(lock_path, 'w') as lock_file:
                if os.name == 'nt':
                    # Windows file locking
                    import msvcrt
                    start_time = time.time()
                    while time.time() - start_time < timeout:
                        try:
                            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                            break
                        except OSError:
                            time.sleep(0.1)
                    else:
                        raise TimeoutError(f"Could not acquire lock for {file_path}")
                else:
                    # Unix file locking
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                
                yield
                
        finally:
            # Remove lock file
            try:
                if lock_path.exists():
                    lock_path.unlink()
            except Exception:
                pass  # Lock cleanup is best-effort
    
    def atomic_write_json(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """Atomically write JSON data to file with locking."""
        try:
            with self.file_lock(file_path):
                # Write to temporary file first
                temp_path = file_path.with_suffix('.tmp')
                
                # Ensure parent directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write data to temporary file
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Atomic replacement
                if os.name == 'nt':
                    # Windows requires removing target first
                    if file_path.exists():
                        file_path.unlink()
                    temp_path.rename(file_path)
                else:
                    # Unix supports atomic rename over existing file
                    temp_path.rename(file_path)
                
                return True
                
        except Exception as e:
            # Cleanup temporary file on error
            temp_path = file_path.with_suffix('.tmp')
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            return False
    
    def atomic_read_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Atomically read JSON data from file with locking."""
        if not file_path.exists():
            return None
            
        try:
            with self.file_lock(file_path, timeout=2.0):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            return None
    
    def atomic_append_json_array(self, file_path: Path, new_entries: list) -> bool:
        """Atomically append entries to JSON array file."""
        try:
            with self.file_lock(file_path):
                # Read existing data
                existing_data = []
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                
                # Append new entries
                if isinstance(existing_data, list):
                    existing_data.extend(new_entries)
                else:
                    existing_data = new_entries
                
                # Write atomically
                return self.atomic_write_json(file_path, existing_data)
                
        except Exception:
            return False
    
    def safe_backup_create(self, file_path: Path, backup_suffix: str = ".backup") -> Optional[Path]:
        """Create a backup of file before modification."""
        if not file_path.exists():
            return None
            
        backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception:
            return None
    
    def validate_json_integrity(self, file_path: Path) -> bool:
        """Validate that JSON file has proper integrity."""
        if not file_path.exists():
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, OSError):
            return False

# Global instance for module-level usage
atomic_ops = AtomicFileOperations()

def atomic_json_write(file_path: str, data: Dict[str, Any]) -> bool:
    """Module-level function for atomic JSON writing."""
    return atomic_ops.atomic_write_json(Path(file_path), data)

def atomic_json_read(file_path: str) -> Optional[Dict[str, Any]]:
    """Module-level function for atomic JSON reading."""
    return atomic_ops.atomic_read_json(Path(file_path))

def atomic_json_append_array(file_path: str, new_entries: list) -> bool:
    """Module-level function for atomic JSON array appending."""
    return atomic_ops.atomic_append_json_array(Path(file_path), new_entries)

def validate_json_file(file_path: str) -> bool:
    """Module-level function for JSON validation."""
    return atomic_ops.validate_json_integrity(Path(file_path))

if __name__ == "__main__":
    # Basic test
    test_data = {
        "test": True,
        "timestamp": datetime.now().isoformat(),
        "data": list(range(100))
    }
    
    test_path = Path("test_atomic_write.json")
    
    print("Testing atomic write operations...")
    success = save_json_atomic(test_path, test_data)
    print(f"Atomic write test: {'✅ PASSED' if success else '❌ FAILED'}")
    
    # Cleanup
    if test_path.exists():
        test_path.unlink()
        print("Test file cleaned up")