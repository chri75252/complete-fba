"""
FBA Dashboard Metrics Core Module - FIXED VERSION
Handles all file I/O and metrics calculation with improved performance and error handling
"""

import json
import os
import csv
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd


class MetricsLoader:
    """Efficient metrics loader with improved file resolution and error handling"""

    # Column detection patterns - case insensitive
    ROI_COLUMNS = [
        'roi', 'roi_percent', 'roi_percentage', 'return_on_investment',
        'return_on_investment_percent', 'return_rate'
    ]

    PROFIT_COLUMNS = [
        'profit', 'net_profit', 'estimated_profit', 'margin',
        'gross_profit', 'total_profit', 'potential_profit'
    ]

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.getcwd()
        self._cache = {}
        self._file_mtimes = {}

    def resolve_paths(self, supplier_hint: str) -> Dict[str, str]:
        """
        IMPROVED: Resolve file paths with better supplier name handling
        """
        # Normalize supplier name for different formats
        normalized_supplier = supplier_hint.replace('.', '_').lower()

        # Try multiple supplier name variations
        supplier_variations = [
            normalized_supplier,
            supplier_hint,
            supplier_hint.replace('-', '_'),
            supplier_hint.replace('.', '-'),
        ]

        # Find processing state file
        state_dir = os.path.join(self.base_dir, "OUTPUTS", "CACHE", "processing_states")
        state_file = None

        for supplier_name in supplier_variations:
            patterns = [
                f"{supplier_name}_processing_state.json",
            ]

            for pattern in patterns:
                candidate = os.path.join(state_dir, pattern)
                if os.path.exists(candidate):
                    state_file = candidate
                    break
            if state_file:
                break

        # Find linking map directory - check both formats
        linking_dir = os.path.join(self.base_dir, "OUTPUTS", "FBA_ANALYSIS", "linking_maps")
        linking_file = None

        for supplier_name in supplier_variations:
            # Try dotted format first (original format)
            candidate_file = os.path.join(linking_dir, supplier_name.replace('_', '.'), "linking_map.json")
            if os.path.exists(candidate_file):
                linking_file = candidate_file
                break

            # Try underscore format
            candidate_file = os.path.join(linking_dir, supplier_name, "linking_map.json")
            if os.path.exists(candidate_file):
                linking_file = candidate_file
                break

        # Find financial reports directory
        financial_dir = os.path.join(self.base_dir, "OUTPUTS", "FBA_ANALYSIS", "financial_reports")

        # Find logs directory
        logs_dir = os.path.join(self.base_dir, "logs", "debug")

        # Check existence before returning
        return {
            "state_file": state_file if state_file and os.path.exists(state_file) else None,
            "linking_file": linking_file if linking_file and os.path.exists(linking_file) else None,
            "financial_dir": financial_dir if os.path.exists(financial_dir) else None,
            "logs_dir": logs_dir if os.path.exists(logs_dir) else None
        }

    def load_state_metrics(self, state_file: str) -> Dict[str, Any]:
        """Load state metrics with improved error handling"""
        if not state_file or not os.path.exists(state_file):
            return {
                "state_file_found": False,
                "total_products": None,
                "is_valid_total_categories_233": None,
                "last_updated": None,
                "processing_status": None,
                "successful_products": None,
                "processed_products": None,
                "fresh_starts": None
            }

        # Check cache first
        try:
            mtime = os.path.getmtime(state_file)
            cache_key = f"state_{state_file}_{mtime}"

            if cache_key in self._cache:
                return self._cache[cache_key]
        except OSError:
            pass

        try:
            # Simple JSON read with error handling
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            metrics = {
                "state_file_found": True,
                "total_products": data.get("total_products", 0),
                "is_valid_total_categories_233": data.get("total_products", 0) == 233,
                "last_updated": self._parse_datetime(data.get("last_updated")),
                "processing_status": data.get("processing_status", "Unknown"),
                "successful_products": data.get("successful_products", 0),
                "processed_products": data.get("successful_products", 0),
                "fresh_starts": 1 if data.get("is_fresh_start", False) else 0
            }

            self._cache[cache_key] = metrics
            return metrics

        except json.JSONDecodeError as e:
            return {
                "state_file_found": True,
                "total_products": None,
                "is_valid_total_categories_233": None,
                "last_updated": None,
                "processing_status": f"JSON Error: {str(e)}",
                "successful_products": None,
                "processed_products": None,
                "fresh_starts": None
            }
        except Exception as e:
            return {
                "state_file_found": True,
                "total_products": None,
                "is_valid_total_categories_233": None,
                "last_updated": None,
                "processing_status": f"Error: {str(e)}",
                "successful_products": None,
                "processed_products": None,
                "fresh_starts": None
            }

    def load_linking_map_metrics(self, linking_file: str) -> Dict[str, Any]:
        """Load linking map metrics with improved performance and error handling"""
        if not linking_file or not os.path.exists(linking_file):
            return {
                "total_matches": 0,
                "high_confidence_rate": 0.0,
                "confidence_counts": {},
                "match_method_counts": {},
                "no_ean_count": 0
            }

        # Check cache first
        try:
            mtime = os.path.getmtime(linking_file)
            cache_key = f"linking_{linking_file}_{mtime}"

            if cache_key in self._cache:
                return self._cache[cache_key]
        except OSError:
            pass

        try:
            # Check file size first - if too large, sample instead of full read
            file_size = os.path.getmtime(linking_file)

            if file_size > 10 * 1024 * 1024:  # 10MB limit
                # Sample the file for large files
                return self._sample_linking_metrics(linking_file)

            # For smaller files, use streaming approach
            confidence_counts = {"high": 0, "medium": 0, "low": 0}
            method_counts = {}
            no_ean_count = 0
            total_matches = 0
            sample_limit = 10000  # Limit items processed for performance

            for i, item in enumerate(self._stream_json_array(linking_file)):
                if i >= sample_limit:
                    break

                total_matches += 1

                # Confidence counting
                confidence = str(item.get("confidence", "unknown")).lower()
                if confidence in confidence_counts:
                    confidence_counts[confidence] += 1
                else:
                    confidence_counts[confidence] = 1

                # Method counting
                method = str(item.get("match_method", "unknown")).lower()
                method_counts[method] = method_counts.get(method, 0) + 1

                # EAN counting
                if not item.get("supplier_ean") or str(item.get("supplier_ean")).strip() == "":
                    no_ean_count += 1

            # Calculate high confidence rate
            high_conf_count = confidence_counts.get("high", 0)
            high_confidence_rate = (high_conf_count / total_matches * 100) if total_matches > 0 else 0

            metrics = {
                "total_matches": total_matches,
                "high_confidence_rate": round(high_confidence_rate, 2),
                "confidence_counts": confidence_counts,
                "match_method_counts": method_counts,
                "no_ean_count": no_ean_count,
                "sampled": file_size > 10 * 1024 * 1024
            }

            self._cache[cache_key] = metrics
            return metrics

        except Exception as e:
            return {
                "total_matches": 0,
                "high_confidence_rate": 0.0,
                "confidence_counts": {},
                "match_method_counts": {},
                "no_ean_count": 0,
                "error": str(e)
            }

    def _sample_linking_metrics(self, linking_file: str) -> Dict[str, Any]:
        """Sample large linking map files for better performance"""
        try:
            # Read first and last portions of the file
            with open(linking_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try to extract a reasonable sample
            if content.startswith('['):
                # Find the first 1000 items
                items_processed = 0
                confidence_counts = {"high": 0, "medium": 0, "low": 0}
                method_counts = {}
                no_ean_count = 0
                total_matches = 0

                # Simple regex-based item extraction
                item_pattern = r'\{[^{}]*\}'
                import re

                items = re.findall(item_pattern, content[:50000])  # First 50KB

                for item_str in items[:1000]:  # Process first 1000 items
                    try:
                        item = json.loads(item_str)
                        total_matches += 1

                        confidence = str(item.get("confidence", "unknown")).lower()
                        if confidence in confidence_counts:
                            confidence_counts[confidence] += 1
                        else:
                            confidence_counts[confidence] = 1

                        method = str(item.get("match_method", "unknown")).lower()
                        method_counts[method] = method_counts.get(method, 0) + 1

                        if not item.get("supplier_ean") or str(item.get("supplier_ean")).strip() == "":
                            no_ean_count += 1
                    except:
                        continue

                high_conf_count = confidence_counts.get("high", 0)
                high_confidence_rate = (high_conf_count / total_matches * 100) if total_matches > 0 else 0

                return {
                    "total_matches": total_matches,
                    "high_confidence_rate": round(high_confidence_rate, 2),
                    "confidence_counts": confidence_counts,
                    "match_method_counts": method_counts,
                    "no_ean_count": no_ean_count,
                    "sampled": True,
                    "note": f"Sampled from large file (first {total_matches} items)"
                }

            return {
                "total_matches": 0,
                "high_confidence_rate": 0.0,
                "confidence_counts": {},
                "match_method_counts": {},
                "no_ean_count": 0,
                "sampled": True,
                "note": "Could not sample file format"
            }

        except Exception as e:
            return {
                "total_matches": 0,
                "high_confidence_rate": 0.0,
                "confidence_counts": {},
                "match_method_counts": {},
                "no_ean_count": 0,
                "error": f"Sampling error: {str(e)}"
            }

    def load_financial_metrics(self, financial_dir: str) -> Dict[str, Any]:
        """Load financial metrics with improved error handling"""
        if not financial_dir or not os.path.exists(financial_dir):
            return {
                "files_scanned": 0,
                "rows_total": 0,
                "count_profitable": 0,
                "avg_roi": 0.0,
                "total_profit": 0.0,
                "notes": ["Financial reports directory not found"]
            }

        try:
            csv_files = [f for f in os.listdir(financial_dir) if f.endswith('.csv')]
            if not csv_files:
                return {
                    "files_scanned": 0,
                    "rows_total": 0,
                    "count_profitable": 0,
                    "avg_roi": 0.0,
                    "total_profit": 0.0,
                    "notes": ["No CSV files found in financial reports directory"]
                }

            total_rows = 0
            profitable_count = 0
            total_roi_sum = 0.0
            total_profit_sum = 0.0
            notes = []

            roi_col = None
            profit_col = None

            # Process files with size limit
            max_file_size = 50 * 1024 * 1024  # 50MB limit per file

            for csv_file in csv_files:
                file_path = os.path.join(financial_dir, csv_file)

                try:
                    # Skip files that are too large
                    if os.path.getsize(file_path) > max_file_size:
                        notes.append(f"Skipped large file: {csv_file}")
                        continue

                    # Read CSV with dtype=str first to avoid type inference issues
                    df = pd.read_csv(file_path, dtype=str, nrows=5)  # Sample first for column detection

                    # Detect columns once
                    if roi_col is None:
                        roi_col = self._find_column(df.columns, self.ROI_COLUMNS)
                        profit_col = self._find_column(df.columns, self.PROFIT_COLUMNS)

                    if roi_col is None and profit_col is None:
                        notes.append(f"Could not infer ROI/profit columns from {csv_file}")
                        continue

                    # Read full file with detected columns
                    df_full = pd.read_csv(file_path, dtype=str)
                    total_rows += len(df_full)

                    if roi_col:
                        # Convert ROI values
                        roi_values = pd.to_numeric(
                            df_full[roi_col].astype(str).str.replace('%', '').astype(float) / 100,
                            errors='coerce'
                        )

                        # Count profitable (ROI > 15% = 0.15)
                        profitable_mask = roi_values > 0.15
                        profitable_count += profitable_mask.sum()

                        # Sum ROI for average calculation
                        total_roi_sum += roi_values.sum()

                    if profit_col:
                        # Convert profit values
                        profit_values = pd.to_numeric(df_full[profit_col], errors='coerce')
                        total_profit_sum += profit_values.sum()

                except Exception as e:
                    notes.append(f"Error processing {csv_file}: {str(e)}")
                    continue

            avg_roi = (total_roi_sum / total_rows * 100) if total_rows > 0 else 0.0

            return {
                "files_scanned": len(csv_files),
                "rows_total": total_rows,
                "count_profitable": int(profitable_count),
                "avg_roi": round(avg_roi, 2),
                "total_profit": round(total_profit_sum, 2),
                "notes": notes if notes else ["Successfully processed all files"]
            }

        except Exception as e:
            return {
                "files_scanned": 0,
                "rows_total": 0,
                "count_profitable": 0,
                "avg_roi": 0.0,
                "total_profit": 0.0,
                "notes": [f"Error processing financial reports: {str(e)}"]
            }

    def tail_logs(self, logs_dir: str, pattern: str = "run_custom_.*\\.log", lines: int = 200) -> Tuple[List[str], Optional[str]]:
        """Tail the latest log file with improved error handling"""
        if not logs_dir or not os.path.exists(logs_dir):
            return [], None

        try:
            # Find matching log files
            log_files = [f for f in os.listdir(logs_dir)
                        if re.match(pattern, f) and f.endswith('.log')]

            if not log_files:
                return [], None

            # Get the most recent file
            log_files.sort(key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True)
            latest_log = os.path.join(logs_dir, log_files[0])

            # Check file size
            file_size = os.path.getsize(latest_log)
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                lines = min(lines, 100)  # Reduce lines for large files

            # Read last N lines efficiently
            with open(latest_log, 'r', encoding='utf-8', errors='replace') as f:
                # Read all lines and take last N
                all_lines = f.readlines()
                tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

                # Clean up line endings and decode
                clean_lines = [line.rstrip('\n\r') for line in tail_lines]

                return clean_lines, log_files[0]

        except Exception as e:
            return [f"Error reading logs: {str(e)}"], None

    def _stream_json_array(self, filepath: str):
        """Stream JSON array items one by one to avoid memory issues"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()

            # Handle both array and object formats
            if content.startswith('['):
                # JSON array - stream items
                content = content[1:-1]  # Remove [ and ]

                # Simple streaming approach for well-formed JSON
                brace_count = 0
                current_item = ""
                in_string = False
                escape_next = False

                for char in content:
                    if escape_next:
                        current_item += char
                        escape_next = False
                        continue

                    if char == '\\':
                        escape_next = True
                        current_item += char
                        continue

                    if char == '"' and not escape_next:
                        in_string = not in_string
                        current_item += char
                        continue

                    if not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1

                            if brace_count == 0:
                                current_item += char
                                try:
                                    yield json.loads(current_item)
                                except json.JSONDecodeError:
                                    pass  # Skip malformed items
                                current_item = ""
                                continue

                    current_item += char

            elif content.startswith('{'):
                # JSON object - parse directly
                yield json.loads(content)

    def _find_column(self, df_columns: List[str], potential_names: List[str]) -> Optional[str]:
        """Find matching column name from potential names (case-insensitive)"""
        df_lower = [col.lower().replace('_', '').replace(' ', '') for col in df_columns]

        for potential in potential_names:
            normalized = potential.lower().replace('_', '').replace(' ', '')
            if normalized in df_lower:
                return df_columns[df_lower.index(normalized)]

        return None

    def _parse_datetime(self, dt_str: str) -> Optional[datetime]:
        """Parse datetime string in various formats"""
        if not dt_str:
            return None

        try:
            # Handle ISO format with timezone
            if 'T' in dt_str:
                # Remove timezone info for parsing
                dt_clean = dt_str.split('+')[0].replace('Z', '')
                return datetime.fromisoformat(dt_clean)
            else:
                # Try other formats
                return datetime.fromisoformat(dt_str)
        except (ValueError, TypeError):
            return None


def load_metrics(base_dir: str, supplier_hint: str) -> Dict[str, Any]:
    """Main function to load all metrics"""
    loader = MetricsLoader(base_dir)
    paths = loader.resolve_paths(supplier_hint)

    return {
        "paths": paths,
        "state_metrics": loader.load_state_metrics(paths["state_file"]),
        "linking_metrics": loader.load_linking_map_metrics(paths["linking_file"]),
        "financial_metrics": loader.load_financial_metrics(paths["financial_dir"]),
        "log_data": loader.tail_logs(paths["logs_dir"])
    }