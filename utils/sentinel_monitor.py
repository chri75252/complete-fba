"""
Sentinel Monitoring System for Amazon FBA Agent System v3.7

This module implements comprehensive proactive monitoring to detect silent failures:
1. Linking map shrinkage detection (>5% threshold = CRITICAL)
2. Session/global totals divergence monitoring  
3. Missing path variants detection (dot vs underscore)
4. Save retry patterns and strategy usage monitoring

All sentinels write to OUTPUTS/DIAGNOSTICS/sentinels.log with structured alerts.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading
import time

# Set up logging
log = logging.getLogger(__name__)

@dataclass
class SentinelAlert:
    """Structured alert for sentinel monitoring"""
    level: str  # CRITICAL, WARNING, INFO, ERROR
    sentinel_type: str
    message: str
    timestamp: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "sentinel_type": self.sentinel_type,
            "message": self.message,
            "timestamp": self.timestamp,
            "data": self.data
        }

class SentinelMonitor:
    """Proactive monitoring system for Amazon FBA Agent System"""
    
    def __init__(self, supplier_name: str):
        self.supplier_name = supplier_name
        self.start_time = datetime.now(timezone.utc)
        
        # Initialize sentinel log path
        self.log_dir = Path("OUTPUTS/DIAGNOSTICS")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.sentinel_log_path = self.log_dir / "sentinels.log"
        
        # Initialize tracking variables
        self.linking_map_history = deque(maxlen=100)  # Track last 100 measurements
        self.session_totals = defaultdict(int)
        self.global_totals = defaultdict(int)
        self.path_variants_seen = set()
        self.save_retry_counts = defaultdict(int)
        self.save_strategy_usage = defaultdict(int)
        
        # Sentinel thresholds (configurable)
        self.linking_map_shrinkage_threshold = 0.05  # 5%
        self.totals_divergence_threshold = 0.10  # 10%
        self.path_variant_window = 50  # Check for variants in last 50 operations
        
        # Thread safety
        self._lock = threading.Lock()
        
        log.info(f"✅ SENTINEL MONITOR: Initialized for supplier '{supplier_name}'")
        self._write_sentinel_log(SentinelAlert(
            level="INFO",
            sentinel_type="INITIALIZATION",
            message=f"Sentinel monitor started for supplier: {supplier_name}",
            timestamp=self.start_time.isoformat(),
            data={"supplier_name": supplier_name, "thresholds": {
                "linking_map_shrinkage": self.linking_map_shrinkage_threshold,
                "totals_divergence": self.totals_divergence_threshold,
                "path_variant_window": self.path_variant_window
            }}
        ))
    
    def _write_sentinel_log(self, alert: SentinelAlert) -> None:
        """Write structured alert to sentinels.log"""
        try:
            with open(self.sentinel_log_path, 'a', encoding='utf-8') as f:
                log_entry = json.dumps(alert.to_dict(), separators=(',', ':'))
                f.write(f"{log_entry}\n")
        except Exception as e:
            log.error(f"❌ SENTINEL LOG ERROR: Failed to write to {self.sentinel_log_path}: {e}")
    
    def check_linking_map_shrinkage(self, current_size: int, previous_size: Optional[int] = None) -> None:
        """
        CRITICAL SENTINEL: Monitor for linking map shrinkage >5%
        This detects silent data loss during save operations
        """
        with self._lock:
            self.linking_map_history.append({
                'size': current_size,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            if previous_size is None and len(self.linking_map_history) >= 2:
                previous_size = self.linking_map_history[-2]['size']
            
            if previous_size is not None and previous_size > 0:
                shrinkage = (previous_size - current_size) / previous_size
                
                if shrinkage > self.linking_map_shrinkage_threshold:
                    alert = SentinelAlert(
                        level="CRITICAL",
                        sentinel_type="LINKING_MAP_SHRINKAGE",
                        message=f"CRITICAL: Linking map shrunk by {shrinkage:.1%} from {previous_size} to {current_size}",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        data={
                            "previous_size": previous_size,
                            "current_size": current_size,
                            "shrinkage_percentage": shrinkage,
                            "threshold": self.linking_map_shrinkage_threshold,
                            "supplier_name": self.supplier_name
                        }
                    )
                    self._write_sentinel_log(alert)
                    log.critical(f"🚨 {alert.message}")
                    
                elif shrinkage > 0.01:  # Warning for >1% shrinkage
                    alert = SentinelAlert(
                        level="WARNING",
                        sentinel_type="LINKING_MAP_SHRINKAGE",
                        message=f"WARNING: Linking map shrunk by {shrinkage:.1%} from {previous_size} to {current_size}",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        data={
                            "previous_size": previous_size,
                            "current_size": current_size,
                            "shrinkage_percentage": shrinkage,
                            "threshold": self.linking_map_shrinkage_threshold,
                            "supplier_name": self.supplier_name
                        }
                    )
                    self._write_sentinel_log(alert)
                    log.warning(f"⚠️ {alert.message}")
    
    def check_totals_divergence(self, session_count: int, global_count: int, metric_name: str) -> None:
        """
        WARNING SENTINEL: Monitor session vs global totals divergence
        Detects inconsistencies between in-memory and file-based counts
        """
        with self._lock:
            self.session_totals[metric_name] = session_count
            self.global_totals[metric_name] = global_count
            
            if global_count > 0:
                divergence = abs(session_count - global_count) / global_count
                
                if divergence > self.totals_divergence_threshold:
                    alert = SentinelAlert(
                        level="WARNING",
                        sentinel_type="TOTALS_DIVERGENCE",
                        message=f"WARNING: {metric_name} divergence {divergence:.1%} (session: {session_count}, global: {global_count})",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        data={
                            "metric_name": metric_name,
                            "session_count": session_count,
                            "global_count": global_count,
                            "divergence_percentage": divergence,
                            "threshold": self.totals_divergence_threshold,
                            "supplier_name": self.supplier_name
                        }
                    )
                    self._write_sentinel_log(alert)
                    log.warning(f"⚠️ {alert.message}")
    
    def check_path_variants(self, filepath: str, operation: str = "access") -> None:
        """
        WARNING SENTINEL: Detect missing path variants (dot vs underscore)
        Identifies potential file access issues due to path naming inconsistencies
        """
        with self._lock:
            path_obj = Path(filepath)
            
            # Generate possible variants
            filename = path_obj.name
            parent = path_obj.parent
            
            dot_variant = filename.replace('_', '.')
            underscore_variant = filename.replace('.', '_')
            
            variants = {
                'original': filepath,
                'dot_variant': str(parent / dot_variant) if dot_variant != filename else None,
                'underscore_variant': str(parent / underscore_variant) if underscore_variant != filename else None
            }
            
            # Track seen paths
            self.path_variants_seen.add(filepath)
            
            # Check for missing variants that should exist
            missing_variants = []
            for variant_type, variant_path in variants.items():
                if variant_path and variant_path != filepath:
                    if Path(variant_path).exists() and variant_path not in self.path_variants_seen:
                        missing_variants.append((variant_type, variant_path))
            
            if missing_variants:
                alert = SentinelAlert(
                    level="WARNING",
                    sentinel_type="MISSING_PATH_VARIANTS",
                    message=f"WARNING: Found {len(missing_variants)} missing path variants for {filename}",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    data={
                        "original_path": filepath,
                        "operation": operation,
                        "missing_variants": missing_variants,
                        "supplier_name": self.supplier_name
                    }
                )
                self._write_sentinel_log(alert)
                log.warning(f"⚠️ {alert.message}")
    
    def track_save_retry(self, strategy: str, success: bool, attempt_count: int = 1) -> None:
        """
        INFO/ERROR SENTINEL: Monitor save retry patterns and strategy usage
        Tracks reliability of different save strategies
        """
        with self._lock:
            self.save_strategy_usage[strategy] += 1
            
            if not success:
                self.save_retry_counts[strategy] += attempt_count
                
                alert = SentinelAlert(
                    level="ERROR" if attempt_count > 3 else "INFO",
                    sentinel_type="SAVE_RETRY_PATTERN",
                    message=f"{'ERROR' if attempt_count > 3 else 'INFO'}: Save strategy '{strategy}' failed after {attempt_count} attempts",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    data={
                        "strategy": strategy,
                        "success": success,
                        "attempt_count": attempt_count,
                        "total_retries": self.save_retry_counts[strategy],
                        "total_usage": self.save_strategy_usage[strategy],
                        "supplier_name": self.supplier_name
                    }
                )
                self._write_sentinel_log(alert)
                if attempt_count > 3:
                    log.error(f"❌ {alert.message}")
                else:
                    log.info(f"ℹ️ {alert.message}")
            else:
                # Log successful strategy usage periodically
                if self.save_strategy_usage[strategy] % 10 == 0:  # Every 10th use
                    alert = SentinelAlert(
                        level="INFO",
                        sentinel_type="SAVE_STRATEGY_SUCCESS",
                        message=f"INFO: Save strategy '{strategy}' completed successfully ({self.save_strategy_usage[strategy]} total uses)",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        data={
                            "strategy": strategy,
                            "success": success,
                            "total_usage": self.save_strategy_usage[strategy],
                            "total_retries": self.save_retry_counts[strategy],
                            "supplier_name": self.supplier_name
                        }
                    )
                    self._write_sentinel_log(alert)
                    log.info(f"ℹ️ {alert.message}")
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary"""
        with self._lock:
            runtime = datetime.now(timezone.utc) - self.start_time
            
            return {
                "supplier_name": self.supplier_name,
                "runtime_seconds": runtime.total_seconds(),
                "linking_map_measurements": len(self.linking_map_history),
                "current_linking_map_size": self.linking_map_history[-1]['size'] if self.linking_map_history else 0,
                "session_totals": dict(self.session_totals),
                "global_totals": dict(self.global_totals),
                "path_variants_tracked": len(self.path_variants_seen),
                "save_retry_counts": dict(self.save_retry_counts),
                "save_strategy_usage": dict(self.save_strategy_usage),
                "thresholds": {
                    "linking_map_shrinkage": self.linking_map_shrinkage_threshold,
                    "totals_divergence": self.totals_divergence_threshold,
                    "path_variant_window": self.path_variant_window
                }
            }
    
    def finalize_monitoring(self) -> None:
        """Write final monitoring summary to sentinel log"""
        summary = self.get_monitoring_summary()
        
        alert = SentinelAlert(
            level="INFO",
            sentinel_type="MONITORING_SUMMARY",
            message=f"INFO: Monitoring session completed for {self.supplier_name}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            data=summary
        )
        self._write_sentinel_log(alert)
        log.info(f"✅ SENTINEL MONITOR: Session completed for {self.supplier_name}")

# Global sentinel monitor instance
_sentinel_monitor = None

def get_sentinel_monitor(supplier_name: str) -> SentinelMonitor:
    """Get or create global sentinel monitor instance"""
    global _sentinel_monitor
    if _sentinel_monitor is None or _sentinel_monitor.supplier_name != supplier_name:
        _sentinel_monitor = SentinelMonitor(supplier_name)
    return _sentinel_monitor

def reset_sentinel_monitor():
    """Reset global sentinel monitor (for testing)"""
    global _sentinel_monitor
    _sentinel_monitor = None