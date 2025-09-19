
"""Sentinel monitoring utilities used by PassiveExtractionWorkflow.

The original module was corrupted. This implementation restores the
monitoring hooks that the workflow expects while keeping the behaviour
light-weight and side-effect free.
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class _TotalsCheck:
    metric: str
    cache_count: int
    linking_count: int
    divergence_pct: float


@dataclass
class _SaveRetry:
    component: str
    attempt: int
    success: bool


class _SentinelRegistry:
    """Global registry that aggregates monitoring data across sessions."""

    _lock = threading.Lock()
    _state: Dict[str, Dict[str, object]] = {}

    @classmethod
    def get_state(cls, supplier_name: str) -> Dict[str, object]:
        with cls._lock:
            state = cls._state.get(supplier_name)
            if state is None:
                state = {
                    "sessions": 0,
                    "totals": [],
                    "path_variants": defaultdict(set),
                    "linking_shrinks": 0,
                    "save_retries": [],
                }
                cls._state[supplier_name] = state
            return state

    @classmethod
    def register_session(cls, supplier_name: str) -> int:
        state = cls.get_state(supplier_name)
        with cls._lock:
            state["sessions"] = int(state.get("sessions", 0)) + 1
            return state["sessions"]


class SentinelMonitor:
    """Runtime monitor that surfaces suspicious state transitions."""

    def __init__(self, supplier_name: str, logger: Optional[logging.Logger] = None) -> None:
        self.supplier_name = supplier_name
        self.logger = logger or logging.getLogger(f"SentinelMonitor[{supplier_name}]")
        self._registry_state = _SentinelRegistry.get_state(supplier_name)
        self._session_id = _SentinelRegistry.register_session(supplier_name)
        self._lock = threading.Lock()

        self._totals_checks: List[_TotalsCheck] = []
        self._path_variants: Dict[str, Set[str]] = defaultdict(set)
        self._shrink_events = 0
        self._save_retries: List[_SaveRetry] = []

    # ------------------------------------------------------------------
    def check_totals_divergence(self, linking_count: int, cache_count: int, metric: str) -> None:
        """Compare cached data counts and log when they diverge significantly."""

        linking_count = int(linking_count or 0)
        cache_count = int(cache_count or 0)
        denominator = cache_count if cache_count > 0 else max(linking_count, 1)
        diff = abs(linking_count - cache_count)
        divergence_pct = (diff / denominator) * 100 if denominator else 0.0

        check = _TotalsCheck(metric=metric, cache_count=cache_count, linking_count=linking_count, divergence_pct=divergence_pct)

        with self._lock:
            self._totals_checks.append(check)
            self._registry_state["totals"].append(check)

        if divergence_pct >= 50.0:
            self.logger.warning(
                "WARNING: %s divergence %.1f%% (linking=%s, cache=%s)",
                metric,
                divergence_pct,
                linking_count,
                cache_count,
            )
        else:
            self.logger.info(
                "Sentinel: %s divergence %.1f%% (linking=%s, cache=%s)",
                metric,
                divergence_pct,
                linking_count,
                cache_count,
            )

    # ------------------------------------------------------------------
    def check_path_variants(self, raw_path: str, metric: str) -> None:
        """Track different path spellings used for the same resource."""

        try:
            canonical = str(Path(raw_path).expanduser().resolve(strict=False)).lower()
        except Exception:
            canonical = str(raw_path).lower()

        with self._lock:
            variants = self._path_variants[metric]
            variants.add(canonical)
            registry_variants = self._registry_state["path_variants"][metric]
            registry_variants.add(canonical)

            if len(registry_variants) > 1:
                self.logger.warning(
                    "WARNING: %s path variants detected: %s",
                    metric,
                    sorted(registry_variants),
                )

    # ------------------------------------------------------------------
    def check_linking_map_shrinkage(self, current_size: int, previous_size: int) -> None:
        """Raise an alert if the linking map shrinks unexpectedly."""

        current_size = int(current_size or 0)
        previous_size = int(previous_size or 0)
        if previous_size and current_size < previous_size:
            loss = previous_size - current_size
            with self._lock:
                self._shrink_events += 1
                self._registry_state["linking_shrinks"] = int(self._registry_state.get("linking_shrinks", 0)) + 1
            self.logger.warning(
                "WARNING: linking map shrank by %s entries (from %s to %s)",
                loss,
                previous_size,
                current_size,
            )
        else:
            self.logger.info(
                "Sentinel: linking map size verified (%s -> %s)",
                previous_size,
                current_size,
            )

    # ------------------------------------------------------------------
    def track_save_retry(self, component: str, success: bool, attempt: int) -> None:
        """Record dedicated save retry attempts for later diagnostics."""

        retry = _SaveRetry(component=component, attempt=int(attempt or 0), success=bool(success))
        with self._lock:
            self._save_retries.append(retry)
            self._registry_state["save_retries"].append(retry)

        if success:
            self.logger.info(
                "Sentinel: %s save succeeded on attempt %s",
                component,
                retry.attempt,
            )
        else:
            self.logger.warning(
                "WARNING: %s save failed on attempt %s",
                component,
                retry.attempt,
            )

    # ------------------------------------------------------------------
    def finalize_monitoring(self) -> None:
        """Emit a concise session summary at the end of the workflow."""

        summary = {
            "session_id": self._session_id,
            "totals_checks": len(self._totals_checks),
            "divergence_alerts": sum(1 for check in self._totals_checks if check.divergence_pct >= 50.0),
            "path_metrics": {metric: len(variants) for metric, variants in self._path_variants.items()},
            "shrink_events": self._shrink_events,
            "save_retries": len(self._save_retries),
        }
        self.logger.info("Sentinel summary: %s", summary)


def get_sentinel_monitor(supplier_name: str, logger: Optional[logging.Logger] = None) -> SentinelMonitor:
    """Factory used by the workflow to obtain a monitor instance."""

    return SentinelMonitor(supplier_name=supplier_name, logger=logger)


__all__ = ["SentinelMonitor", "get_sentinel_monitor"]
