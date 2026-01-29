import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from ..config import MEMORY_DIR

logger = logging.getLogger(__name__)

class SupplierMemory:
    """
    Manages persistent storage for supplier-specific configurations,
    traps, and overrides.
    """

    def __init__(self, supplier_id: str):
        self.supplier_id = self._sanitize_id(supplier_id)
        self.base_path = MEMORY_DIR / "suppliers" / self.supplier_id
        self._ensure_dir()

    def _sanitize_id(self, name: str) -> str:
        """Sanitizes supplier name for filesystem."""
        return "".join(c for c in name if c.isalnum() or c in ('-', '_')).lower()

    def _ensure_dir(self):
        self.base_path.mkdir(parents=True, exist_ok=True)

    def load_calibration(self) -> Dict[str, Any]:
        """Loads calibration.json or returns defaults."""
        path = self.base_path / "calibration.json"
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load calibration for {self.supplier_id}: {e}")
            return {}

    def save_calibration(self, config: Dict[str, Any]):
        path = self.base_path / "calibration.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def load_traps(self) -> List[Dict[str, Any]]:
        """Loads traps.jsonl."""
        path = self.base_path / "traps.jsonl"
        traps = []
        if not path.exists():
            return traps
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        traps.append(json.loads(line))
        except Exception as e:
            logger.error(f"Failed to load traps for {self.supplier_id}: {e}")
        return traps

    def append_trap(self, trap: Dict[str, Any]):
        """Appends a new trap to the library."""
        path = self.base_path / "traps.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(trap) + "\n")

    def load_overrides(self) -> Dict[str, Any]:
        """
        Loads overrides.jsonl
        Returns a dict mapping RowID (or other key) to override data.
        """
        path = self.base_path / "overrides.jsonl"
        overrides = {}
        if not path.exists():
            return overrides
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        if "RowID" in item:
                            overrides[str(item["RowID"])] = item
        except Exception as e:
            logger.error(f"Failed to load overrides for {self.supplier_id}: {e}")
        return overrides

    def append_override(self, override: Dict[str, Any]):
        path = self.base_path / "overrides.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(override) + "\n")
