#!/usr/bin/env python3
"""
Windows Memory Management System
===============================

Windows-native memory management for Amazon FBA Agent System.
Replaces WSL-specific memory management with Windows-compatible alternatives.

Author: Amazon FBA Agent System
Date: 2025-07-23
Priority: HIGH - Enables Windows compatibility
"""

import os
import psutil
import subprocess
import time
import logging
import gc
from typing import Dict, Any, Optional, List
from pathlib import Path

# Configure logging
log = logging.getLogger(__name__)

class WindowsMemoryManager:
    """
    Windows-native memory management for supplier scraping operations
    
    Provides Windows-compatible memory monitoring, cleanup, and process management
    without relying on Linux-specific commands or WSL functionality.
    """
    
    def __init__(self, warning_threshold_gb: float = 6.0, critical_threshold_gb: float = 8.0, emergency_threshold_gb: float = 10.0):
        """
        Initialize Windows memory manager
        
        Args:
            warning_threshold_gb: Memory usage to trigger warnings (default: 6GB)
            critical_threshold_gb: Memory usage to trigger aggressive cleanup (default: 8GB)  
            emergency_threshold_gb: Memory usage to trigger emergency shutdown (default: 10GB)
        """
        self.warning_threshold_gb = warning_threshold_gb
        self.critical_threshold_gb = critical_threshold_gb
        self.emergency_threshold_gb = emergency_threshold_gb
        
        # Tracking attributes
        self.last_cleanup_time = time.time()
        self.cleanup_interval_seconds = 300  # 5 minutes (more frequent than WSL)
        self.memory_history = []  # Track memory usage over time
        self.cleanup_count = 0
        
        log.info(f"🪟 WindowsMemoryManager initialized: warning={warning_threshold_gb}GB, critical={critical_threshold_gb}GB, emergency={emergency_threshold_gb}GB")
    
    def get_windows_memory_usage(self) -> Dict[str, Any]:
        """
        Get comprehensive Windows memory usage information
        
        Returns:
            Dictionary with memory usage details
        """
        try:
            # Get system memory info
            memory_info = psutil.virtual_memory()
            
            # Calculate Windows-specific metrics
            total_gb = memory_info.total / (1024 ** 3)
            used_gb = memory_info.used / (1024 ** 3)
            available_gb = memory_info.available / (1024 ** 3)
            percent_used = memory_info.percent
            
            # Track Chrome processes (major memory consumer)
            chrome_memory_mb = 0
            chrome_processes = 0
            chrome_process_list = []
            
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        proc_memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                        chrome_memory_mb += proc_memory_mb
                        chrome_processes += 1
                        chrome_process_list.append({
                            'pid': proc.info['pid'],
                            'memory_mb': proc_memory_mb
                        })
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
                'chrome_memory_mb': chrome_memory_mb,
                'chrome_processes': chrome_processes,
                'chrome_process_details': chrome_process_list,
                'python_memory_mb': python_memory_mb,
                'python_processes': python_processes,
                'timestamp': time.time()
            }
            
            # Add to history
            self.memory_history.append(result)
            # Keep only last 100 entries
            if len(self.memory_history) > 100:
                self.memory_history = self.memory_history[-100:]
            
            return result
            
        except Exception as e:
            log.warning(f"⚠️ Failed to get Windows memory usage: {e}")
            return {}
    
    def get_memory_pressure_level(self, current_usage: Optional[Dict[str, Any]] = None) -> str:
        """
        Determine memory pressure level based on current usage
        
        Returns:
            String indicating pressure level: "normal", "warning", "critical", "emergency"
        """
        if not current_usage:
            current_usage = self.get_windows_memory_usage()
        
        if not current_usage:
            return "unknown"
        
        used_gb = current_usage.get('used_memory_gb', 0)
        
        if used_gb >= self.emergency_threshold_gb:
            return "emergency"
        elif used_gb >= self.critical_threshold_gb:
            return "critical"
        elif used_gb >= self.warning_threshold_gb:
            return "warning"
        else:
            return "normal"
    
    async def force_windows_memory_cleanup(self) -> bool:
        """
        Force Windows memory cleanup using native Windows methods
        
        Returns:
            True if cleanup was successful, False otherwise
        """
        try:
            log.info("🧹 Forcing Windows memory cleanup...")
            
            # 1. Python garbage collection
            collected = gc.collect()
            log.info(f"🐍 Python garbage collection freed {collected} objects")
            
            # 2. Windows memory trim (if available)
            try:
                # Try to use Windows SetProcessWorkingSetSize to trim working set
                import ctypes
                from ctypes import wintypes
                
                kernel32 = ctypes.windll.kernel32
                current_process = kernel32.GetCurrentProcess()
                
                # Trim working set
                result = kernel32.SetProcessWorkingSetSize(current_process, -1, -1)
                if result:
                    log.info("✅ Windows working set trimmed successfully")
                else:
                    log.warning("⚠️ Windows working set trim failed")
                    
            except Exception as e:
                log.warning(f"⚠️ Windows working set trim not available: {e}")
            
            # 3. Force Chrome garbage collection if possible
            try:
                chrome_processes = []
                for proc in psutil.process_iter(['pid', 'name']):
                    if 'chrome' in proc.info['name'].lower():
                        chrome_processes.append(proc.info['pid'])
                
                if chrome_processes:
                    log.info(f"🌐 Found {len(chrome_processes)} Chrome processes for cleanup")
                    # Note: We don't kill Chrome processes, just note them for monitoring
                
            except Exception as e:
                log.warning(f"⚠️ Chrome process enumeration failed: {e}")
            
            return True
            
        except Exception as e:
            log.error(f"❌ Windows memory cleanup failed: {e}")
            return False
    
    async def emergency_memory_cleanup(self) -> bool:
        """
        Emergency memory cleanup procedure for critical memory pressure
        
        Returns:
            True if cleanup was successful, False otherwise
        """
        try:
            log.warning("🚨 EMERGENCY MEMORY CLEANUP INITIATED")
            
            # Get memory before cleanup
            before_cleanup = self.get_windows_memory_usage()
            before_used_gb = before_cleanup.get('used_memory_gb', 0)
            
            cleanup_success = True
            
            # 1. Aggressive Python garbage collection
            for i in range(3):  # Multiple passes
                collected = gc.collect()
                log.info(f"🐍 Emergency garbage collection pass {i+1}: freed {collected} objects")
            
            # 2. Windows memory cleanup
            cleanup_success = await self.force_windows_memory_cleanup()
            
            # 3. Clear Python caches
            try:
                import sys
                if hasattr(sys, '_clear_type_cache'):
                    sys._clear_type_cache()
                    log.info("🧹 Python type cache cleared")
            except Exception as e:
                log.warning(f"⚠️ Python cache clear failed: {e}")
            
            # 4. Get memory after cleanup
            after_cleanup = self.get_windows_memory_usage()
            after_used_gb = after_cleanup.get('used_memory_gb', 0)
            freed_gb = before_used_gb - after_used_gb
            
            self.cleanup_count += 1
            self.last_cleanup_time = time.time()
            
            if freed_gb > 0:
                log.info(f"✅ Emergency cleanup freed {freed_gb:.2f}GB memory")
            else:
                log.warning("⚠️ Emergency cleanup completed but no significant memory freed")
            
            return cleanup_success
            
        except Exception as e:
            log.error(f"❌ Emergency memory cleanup failed: {e}")
            return False
    
    def should_trigger_cleanup(self, current_usage: Optional[Dict[str, Any]] = None) -> bool:
        """
        Determine if memory cleanup should be triggered
        
        Args:
            current_usage: Current memory usage info
            
        Returns:
            True if cleanup should be triggered
        """
        if not current_usage:
            current_usage = self.get_windows_memory_usage()
        
        if not current_usage:
            return False
        
        # Check time-based cleanup
        time_since_cleanup = time.time() - self.last_cleanup_time
        if time_since_cleanup > self.cleanup_interval_seconds:
            return True
        
        # Check memory-based cleanup
        pressure_level = self.get_memory_pressure_level(current_usage)
        if pressure_level in ["critical", "emergency"]:
            return True
        
        # Check Chrome memory specifically
        chrome_memory_mb = current_usage.get('chrome_memory_mb', 0)
        if chrome_memory_mb > 2048:  # 2GB Chrome memory
            return True
        
        return False
    
    async def monitor_memory_during_processing(self, product_count: int) -> bool:
        """
        Monitor memory during product processing
        
        Args:
            product_count: Current product processing count
            
        Returns:
            True if memory is healthy, False if emergency action needed
        """
        usage = self.get_windows_memory_usage()
        if not usage:
            return True
        
        pressure_level = self.get_memory_pressure_level(usage)
        
        if pressure_level == "emergency":
            log.error(f"🚨 EMERGENCY memory pressure at product {product_count}")
            await self.emergency_memory_cleanup()
            return False
        elif pressure_level == "critical":
            log.warning(f"⚠️ CRITICAL memory pressure at product {product_count}")
            await self.force_windows_memory_cleanup()
        elif pressure_level == "warning":
            log.info(f"⚠️ WARNING memory pressure at product {product_count}")
            if self.should_trigger_cleanup(usage):
                await self.force_windows_memory_cleanup()
        
        # Log memory status every 50 products
        if product_count % 50 == 0:
            used_gb = usage.get('used_memory_gb', 0)
            chrome_mb = usage.get('chrome_memory_mb', 0)
            log.info(f"📊 Memory status at product {product_count}: {used_gb:.1f}GB used, Chrome: {chrome_mb:.0f}MB")
        
        return True


# Global instance for easy access
_windows_memory_manager = None

def get_windows_memory_manager() -> WindowsMemoryManager:
    """Get global Windows memory manager instance"""
    global _windows_memory_manager
    if _windows_memory_manager is None:
        _windows_memory_manager = WindowsMemoryManager()
    return _windows_memory_manager

async def monitor_memory_during_supplier_scraping(product_count: int) -> bool:
    """
    Monitor memory during supplier scraping operations (Windows-compatible)
    
    Args:
        product_count: Current product count being processed
        
    Returns:
        True if memory is healthy, False if emergency action needed
    """
    manager = get_windows_memory_manager()
    return await manager.monitor_memory_during_processing(product_count)

if __name__ == "__main__":
    # Test the Windows memory manager
    import asyncio
    
    async def test_memory_manager():
        manager = WindowsMemoryManager()
        
        print("🧪 Testing Windows Memory Manager...")
        
        # Test memory usage monitoring
        usage = manager.get_windows_memory_usage()
        print(f"Memory usage: {usage}")
        
        # Test pressure level detection
        pressure = manager.get_memory_pressure_level(usage)
        print(f"Memory pressure level: {pressure}")
        
        # Test cleanup (if needed)
        if manager.should_trigger_cleanup(usage):
            print("Testing memory cleanup...")
            success = await manager.force_windows_memory_cleanup()
            print(f"Cleanup success: {success}")
        
        print("✅ Windows Memory Manager test complete")
    
    asyncio.run(test_memory_manager())