#!/usr/bin/env python3
"""
WSL Memory Management System
============================

Critical memory leak fix for 13GB VmmemWSL consumption during supplier scraping.
Implements comprehensive memory monitoring, cleanup, and emergency shutdown to prevent
system freeze and performance degradation.

Author: Amazon FBA Agent System
Date: 2025-07-22
Priority: CRITICAL - Prevents system-wide memory exhaustion
"""

import os
import psutil
import subprocess
import time
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

# Configure logging
log = logging.getLogger(__name__)

class WSLMemoryManager:
    """
    Comprehensive WSL memory management for supplier scraping operations
    
    Prevents 13GB VmmemWSL accumulation that causes command prompt freezing
    and system performance degradation during 18+ hour processing sessions.
    """
    
    def __init__(self, warning_threshold_gb: float = 8.0, critical_threshold_gb: float = 12.0, emergency_threshold_gb: float = 15.0):
        """
        Initialize WSL memory manager
        
        Args:
            warning_threshold_gb: Memory usage to trigger warnings (default: 8GB)
            critical_threshold_gb: Memory usage to trigger aggressive cleanup (default: 12GB)  
            emergency_threshold_gb: Memory usage to trigger emergency shutdown (default: 15GB)
        """
        self.warning_threshold_gb = warning_threshold_gb
        self.critical_threshold_gb = critical_threshold_gb
        self.emergency_threshold_gb = emergency_threshold_gb
        
        # Tracking attributes
        self.last_cleanup_time = time.time()
        self.cleanup_interval_seconds = 600  # 10 minutes
        self.memory_history = []  # Track memory usage over time
        self.cleanup_count = 0
        
        log.info(f"🧠 WSLMemoryManager initialized: warning={warning_threshold_gb}GB, critical={critical_threshold_gb}GB, emergency={emergency_threshold_gb}GB")
    
    def get_wsl_memory_usage(self) -> Dict[str, Any]:
        """
        Get comprehensive WSL memory usage information
        
        Returns:
            Dictionary with memory usage details
        """
        try:
            # Get system memory info
            memory_info = psutil.virtual_memory()
            swap_info = psutil.swap_memory()
            
            # Calculate WSL-specific metrics
            total_gb = memory_info.total / (1024 ** 3)
            used_gb = memory_info.used / (1024 ** 3)
            available_gb = memory_info.available / (1024 ** 3)
            percent_used = memory_info.percent
            
            # Get swap usage
            swap_used_gb = swap_info.used / (1024 ** 3)
            swap_total_gb = swap_info.total / (1024 ** 3)
            
            # Track Chrome processes (major memory consumer)
            chrome_memory_mb = 0
            chrome_processes = 0
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        chrome_memory_mb += proc.info['memory_info'].rss / (1024 * 1024)
                        chrome_processes += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Track Python processes
            python_memory_mb = 0
            python_processes = 0
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_memory_mb += proc.info['memory_info'].rss / (1024 * 1024)
                        python_processes += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            result = {
                'total_memory_gb': total_gb,
                'used_memory_gb': used_gb,
                'available_memory_gb': available_gb,
                'memory_percent': percent_used,
                'swap_used_gb': swap_used_gb,
                'swap_total_gb': swap_total_gb,
                'chrome_memory_mb': chrome_memory_mb,
                'chrome_processes': chrome_processes,
                'python_memory_mb': python_memory_mb,
                'python_processes': python_processes,
                'timestamp': time.time()
            }
            
            # Add to history
            self.memory_history.append(result)
            
            # Keep only last 100 measurements
            if len(self.memory_history) > 100:
                self.memory_history = self.memory_history[-100:]
            
            return result
            
        except Exception as e:
            log.warning(f"⚠️ Failed to get WSL memory usage: {e}")
            return {}
    
    def check_memory_pressure(self, current_usage: Optional[Dict[str, Any]] = None) -> str:
        """
        Check current memory pressure level
        
        Args:
            current_usage: Optional pre-calculated usage dict
            
        Returns:
            String indicating pressure level: "normal", "warning", "critical", "emergency"
        """
        if not current_usage:
            current_usage = self.get_wsl_memory_usage()
        
        if not current_usage:
            return "unknown"
        
        used_gb = current_usage.get('used_memory_gb', 0)
        memory_percent = current_usage.get('memory_percent', 0)
        
        if used_gb >= self.emergency_threshold_gb or memory_percent >= 95:
            return "emergency"
        elif used_gb >= self.critical_threshold_gb or memory_percent >= 90:
            return "critical"
        elif used_gb >= self.warning_threshold_gb or memory_percent >= 80:
            return "warning"
        else:
            return "normal"
    
    async def force_linux_cache_cleanup(self) -> bool:
        """
        Force Linux page cache, buffer cache, and dentry cleanup
        
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            log.info("🧹 Forcing Linux cache cleanup...")
            
            # Sync filesystems first
            result = subprocess.run(['sync'], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                log.info("✅ Filesystem sync completed")
            else:
                log.warning(f"⚠️ Sync failed: {result.stderr}")
            
            # Drop caches (requires root or proper permissions)
            try:
                # Method 1: Direct cache drop (requires permissions)
                with open('/proc/sys/vm/drop_caches', 'w') as f:
                    f.write('3')
                log.info("✅ Linux caches cleared via /proc/sys/vm/drop_caches")
                return True
            except PermissionError:
                # Method 2: Use sudo if available
                try:
                    result = subprocess.run(['sudo', 'sh', '-c', 'echo 3 > /proc/sys/vm/drop_caches'], 
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        log.info("✅ Linux caches cleared via sudo")
                        return True
                    else:
                        log.warning(f"⚠️ Sudo cache clear failed: {result.stderr}")
                except FileNotFoundError:
                    log.warning("⚠️ Sudo not available for cache cleanup")
            
            return False
            
        except Exception as e:
            log.error(f"❌ Linux cache cleanup failed: {e}")
            return False
    
    def cleanup_temp_directories(self) -> bool:
        """
        Clean up temporary directories that may accumulate during scraping
        
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            log.info("🗂️ Cleaning temporary directories...")
            
            temp_dirs = [
                '/tmp',
                '/var/tmp',
                os.path.expanduser('~/.cache'),
                os.path.expanduser('~/.tmp'),
            ]
            
            total_freed_mb = 0
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        # Get size before cleanup
                        size_before = self._get_directory_size(temp_dir)
                        
                        # Clean old files (older than 1 hour)
                        cutoff_time = time.time() - 3600
                        files_removed = 0
                        
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    if os.path.getctime(file_path) < cutoff_time:
                                        os.remove(file_path)
                                        files_removed += 1
                                except (OSError, PermissionError):
                                    continue
                        
                        # Get size after cleanup
                        size_after = self._get_directory_size(temp_dir)
                        freed_mb = (size_before - size_after) / (1024 * 1024)
                        total_freed_mb += freed_mb
                        
                        if files_removed > 0:
                            log.info(f"🗑️ Cleaned {temp_dir}: {files_removed} files, {freed_mb:.1f}MB freed")
                        
                    except Exception as e:
                        log.warning(f"⚠️ Failed to clean {temp_dir}: {e}")
                        continue
            
            log.info(f"✅ Temporary directory cleanup complete: {total_freed_mb:.1f}MB total freed")
            return True
            
        except Exception as e:
            log.error(f"❌ Temporary directory cleanup failed: {e}")
            return False
    
    def _get_directory_size(self, directory: str) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, FileNotFoundError):
                        continue
        except Exception:
            pass
        return total_size
    
    async def emergency_memory_cleanup(self) -> bool:
        """
        Emergency memory cleanup procedure for critical memory pressure
        
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            log.warning("🚨 EMERGENCY MEMORY CLEANUP INITIATED")
            
            # Get memory before cleanup
            before_cleanup = self.get_wsl_memory_usage()
            before_used_gb = before_cleanup.get('used_memory_gb', 0)
            
            cleanup_success = True
            
            # 1. Force Python garbage collection
            import gc
            collected = gc.collect()
            log.info(f"🐍 Python garbage collection freed {collected} objects")
            
            # 2. Clean Linux caches
            cache_success = await self.force_linux_cache_cleanup()
            if not cache_success:
                cleanup_success = False
            
            # 3. Clean temporary directories
            temp_success = self.cleanup_temp_directories()
            if not temp_success:
                cleanup_success = False
            
            # 4. Get memory after cleanup
            after_cleanup = self.get_wsl_memory_usage()
            after_used_gb = after_cleanup.get('used_memory_gb', 0)
            freed_gb = before_used_gb - after_used_gb
            
            # Update cleanup tracking
            self.cleanup_count += 1
            self.last_cleanup_time = time.time()
            
            log.info(f"🧠 Emergency cleanup results: {freed_gb:.2f}GB freed ({before_used_gb:.1f}GB → {after_used_gb:.1f}GB)")
            
            # Check if cleanup was effective
            pressure_after = self.check_memory_pressure(after_cleanup)
            if pressure_after in ["critical", "emergency"]:
                log.error(f"❌ Emergency cleanup insufficient - pressure still {pressure_after}")
                return False
            else:
                log.info(f"✅ Emergency cleanup successful - pressure now {pressure_after}")
                return True
            
        except Exception as e:
            log.error(f"❌ Emergency memory cleanup failed: {e}")
            return False
    
    def should_trigger_cleanup(self, current_usage: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if memory cleanup should be triggered
        
        Args:
            current_usage: Optional pre-calculated usage dict
            
        Returns:
            True if cleanup should be triggered, False otherwise
        """
        if not current_usage:
            current_usage = self.get_wsl_memory_usage()
        
        if not current_usage:
            return False
        
        # Time-based cleanup (every 10 minutes)
        time_since_cleanup = time.time() - self.last_cleanup_time
        if time_since_cleanup > self.cleanup_interval_seconds:
            return True
        
        # Pressure-based cleanup
        pressure = self.check_memory_pressure(current_usage)
        if pressure in ["warning", "critical", "emergency"]:
            return True
        
        return False
    
    def get_memory_trend_analysis(self) -> Dict[str, Any]:
        """
        Analyze memory usage trends from history
        
        Returns:
            Dictionary with trend analysis
        """
        if len(self.memory_history) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate trend over last measurements
        recent_measurements = self.memory_history[-10:] if len(self.memory_history) >= 10 else self.memory_history
        
        # Memory usage trend
        first_usage = recent_measurements[0]['used_memory_gb']
        last_usage = recent_measurements[-1]['used_memory_gb']
        trend_gb = last_usage - first_usage
        trend_percent = (trend_gb / first_usage) * 100 if first_usage > 0 else 0
        
        # Time span
        time_span_minutes = (recent_measurements[-1]['timestamp'] - recent_measurements[0]['timestamp']) / 60
        
        # Growth rate
        growth_rate_gb_per_hour = (trend_gb / time_span_minutes) * 60 if time_span_minutes > 0 else 0
        
        return {
            "trend": "increasing" if trend_gb > 0.1 else "decreasing" if trend_gb < -0.1 else "stable",
            "trend_gb": trend_gb,
            "trend_percent": trend_percent,
            "growth_rate_gb_per_hour": growth_rate_gb_per_hour,
            "measurements": len(recent_measurements),
            "time_span_minutes": time_span_minutes,
            "current_usage_gb": last_usage,
            "cleanup_count": self.cleanup_count
        }
    
    def log_memory_status(self, product_count: int = 0) -> None:
        """
        Log comprehensive memory status for monitoring
        
        Args:
            product_count: Current product processing count
        """
        usage = self.get_wsl_memory_usage()
        if not usage:
            return
        
        pressure = self.check_memory_pressure(usage)
        trend = self.get_memory_trend_analysis()
        
        # Format status message
        status_icon = {
            "normal": "✅",
            "warning": "⚠️", 
            "critical": "🚨",
            "emergency": "🆘"
        }.get(pressure, "❓")
        
        log.info(f"{status_icon} Memory Status [Product {product_count}]: "
                f"{usage['used_memory_gb']:.1f}GB used ({usage['memory_percent']:.1f}%), "
                f"Chrome: {usage['chrome_memory_mb']:.0f}MB, "
                f"Python: {usage['python_memory_mb']:.0f}MB, "
                f"Pressure: {pressure.upper()}")
        
        # Log trend if significant
        if trend['trend'] != "stable":
            log.info(f"📈 Memory Trend: {trend['trend']} ({trend['trend_gb']:+.2f}GB, "
                    f"{trend['growth_rate_gb_per_hour']:+.1f}GB/h)")

# Global instance for easy access
_wsl_memory_manager = None

def get_wsl_memory_manager() -> WSLMemoryManager:
    """Get global WSL memory manager instance"""
    global _wsl_memory_manager
    if _wsl_memory_manager is None:
        _wsl_memory_manager = WSLMemoryManager()
    return _wsl_memory_manager

async def monitor_memory_during_supplier_scraping(product_count: int) -> bool:
    """
    Monitor memory during supplier scraping operations
    
    Args:
        product_count: Current product processing count
        
    Returns:
        True if memory is healthy, False if emergency action needed
    """
    manager = get_wsl_memory_manager()
    
    # Get current usage
    usage = manager.get_wsl_memory_usage()
    if not usage:
        return True  # Assume healthy if can't get info
    
    # Log status every 100 products or if pressure detected
    pressure = manager.check_memory_pressure(usage)
    if product_count % 100 == 0 or pressure != "normal":
        manager.log_memory_status(product_count)
    
    # Trigger cleanup if needed
    if manager.should_trigger_cleanup(usage):
        log.info(f"🧹 Triggering memory cleanup at product {product_count}")
        success = await manager.emergency_memory_cleanup()
        if not success:
            log.error(f"❌ Memory cleanup failed - system may be unstable")
    
    # Check if emergency action needed
    if pressure == "emergency":
        log.error(f"🆘 EMERGENCY: Memory usage critical - recommend stopping processing")
        return False
    
    return True

if __name__ == "__main__":
    # Test the WSL memory manager
    import asyncio
    
    async def test_memory_manager():
        manager = WSLMemoryManager()
        
        print("🧪 Testing WSL Memory Manager...")
        
        # Test memory usage monitoring
        usage = manager.get_wsl_memory_usage()
        print(f"Memory usage: {usage}")
        
        # Test pressure checking
        pressure = manager.check_memory_pressure(usage)
        print(f"Memory pressure: {pressure}")
        
        # Test trend analysis
        trend = manager.get_memory_trend_analysis()
        print(f"Memory trend: {trend}")
        
        # Test cleanup if needed
        if manager.should_trigger_cleanup(usage):
            print("Triggering cleanup...")
            success = await manager.emergency_memory_cleanup()
            print(f"Cleanup success: {success}")
        
        print("✅ WSL Memory Manager test complete")
    
    asyncio.run(test_memory_manager())