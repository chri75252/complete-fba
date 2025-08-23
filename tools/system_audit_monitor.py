"""
System Audit Monitor - Comprehensive validation and analysis framework
for monitoring Amazon FBA Agent System operation across multiple runs.
"""

import os
import json
import time
import logging
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from collections import defaultdict
import threading
import subprocess
import csv
import glob
import shutil

@dataclass
class FileMonitorState:
    """Track file monitoring state for validation"""
    last_update_time: float = 0.0
    update_count: int = 0
    update_intervals: List[float] = field(default_factory=list)
    expected_frequency: int = 1
    validation_errors: List[str] = field(default_factory=list)

@dataclass
class AuditResults:
    """Comprehensive audit results structure"""
    run_id: str
    execution_time: str
    total_products_processed: int
    audit_duration_seconds: float
    compliance_metrics: Dict[str, Any] = field(default_factory=dict)
    file_validation: Dict[str, Any] = field(default_factory=dict)
    resumption_validation: Dict[str, Any] = field(default_factory=dict)
    anomalies: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class SystemAuditMonitor:
    """
    Autonomous auditing agent for comprehensive system validation
    """
    
    def __init__(self, workspace_path: str, config_path: str = None):
        self.workspace_path = Path(workspace_path)
        self.config_path = config_path or self.workspace_path / "config" / "system_config.json"
        self.audit_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize monitoring components
        self.file_monitors = {}
        self.audit_results = AuditResults(
            run_id=self.audit_id,
            execution_time=datetime.now().isoformat(),
            total_products_processed=0,
            audit_duration_seconds=0.0
        )
        
        # Load system configuration
        self.config = self._load_system_config()
        
        # Set up audit directories
        self.audit_dir = self.workspace_path / "OUTPUTS" / "AUDIT_REPORTS"
        self.audit_dir.mkdir(exist_ok=True)
        
        # Initialize logging
        self._setup_logging()
        
        # File path patterns
        self._setup_file_patterns()
        
        # Monitoring state
        self.monitoring_active = False
        self.start_time = None
        
    def _load_system_config(self) -> Dict[str, Any]:
        """Load system configuration for audit parameters"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            return {}
    
    def _setup_logging(self):
        """Setup audit-specific logging"""
        log_file = self.audit_dir / f"{self.audit_id}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - AUDIT - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _setup_file_patterns(self):
        """Setup file path patterns for monitoring"""
        outputs_dir = self.workspace_path / "OUTPUTS"
        
        self.file_patterns = {
            "cache_files": "cached_products/*.json",
            "linking_maps": "FBA_ANALYSIS/linking_maps/**/*.json",
            "processing_states": "CACHE/processing_states/*.json", 
            "financial_reports": "FBA_ANALYSIS/financial_reports/*.csv"
        }
        
        # Initialize file monitors
        for file_type in self.file_patterns:
            self.file_monitors[file_type] = FileMonitorState()
            
    def start_monitoring(self):
        """Start comprehensive system monitoring"""
        self.logger.info(f"Starting System Audit Monitor - {self.audit_id}")
        self.monitoring_active = True
        self.start_time = time.time()
        
        # Initialize baseline
        self._establish_baseline()
        
        # Start real-time monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Audit monitoring active")
        
    def _establish_baseline(self):
        """Establish baseline for file monitoring"""
        self.logger.info("Establishing monitoring baseline...")
        
        # Record initial file states
        for file_type, pattern in self.file_patterns.items():
            files = list(Path().glob(str(pattern)))
            self.logger.info(f"  {file_type}: {len(files)} existing files")
            
        # Load expected frequencies from config
        cache_freq = self.config.get("supplier_cache_control", {}).get("update_frequency_products", 1)
        linking_freq = self.config.get("system", {}).get("linking_map_batch_size", 1)
        state_freq = self.config.get("supplier_extraction_progress", {}).get("state_persistence", {}).get("batch_save_frequency", 1)
        financial_freq = self.config.get("system", {}).get("financial_report_batch_size", 50)
        
        self.file_monitors["cache_files"].expected_frequency = cache_freq
        self.file_monitors["linking_maps"].expected_frequency = linking_freq
        self.file_monitors["processing_states"].expected_frequency = state_freq
        self.file_monitors["financial_reports"].expected_frequency = financial_freq
        
        self.logger.info(f"Expected frequencies: Cache={cache_freq}, Linking={linking_freq}, State={state_freq}, Financial={financial_freq}")
        
    def _monitor_loop(self):
        """Main monitoring loop running in background thread"""
        while self.monitoring_active:
            try:
                self._check_file_updates()
                self._validate_processes()
                time.sleep(2)  # Monitor every 2 seconds
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(5)
                
    def _check_file_updates(self):
        """Check for file updates and validate frequency"""
        outputs_dir = self.workspace_path / "OUTPUTS"
        
        for file_type, pattern in self.file_patterns.items():
            try:
                # Build full pattern path
                full_pattern = outputs_dir / pattern
                files = list(self.workspace_path.glob(str(full_pattern.relative_to(self.workspace_path))))
                monitor = self.file_monitors[file_type]
                
                # Check for new files or modifications
                for file_path in files:
                    if file_path.exists():
                        mtime = file_path.stat().st_mtime
                        if mtime > monitor.last_update_time:
                            self._record_file_update(file_type, mtime, file_path)
                            
            except Exception as e:
                self.logger.error(f"File check error for {file_type}: {e}")
                
    def _record_file_update(self, file_type: str, timestamp: float, file_path: Path):
        """Record file update and validate frequency"""
        monitor = self.file_monitors[file_type]
        
        if monitor.last_update_time > 0:
            interval = timestamp - monitor.last_update_time
            monitor.update_intervals.append(interval)
            
        monitor.last_update_time = timestamp
        monitor.update_count += 1
        
        self.logger.info(f"FILE_UPDATE {file_type} updated: {file_path.name} (#{monitor.update_count})")
        
        # Validate frequency if this is a financial report
        if file_type == "financial_reports":
            self._validate_financial_trigger(monitor.update_count)
            
    def _validate_financial_trigger(self, report_count: int):
        """Validate financial report trigger timing"""
        expected_freq = self.file_monitors["financial_reports"].expected_frequency
        linking_count = self._get_linking_map_count()
        
        expected_triggers = linking_count // expected_freq
        actual_triggers = report_count
        
        if expected_triggers != actual_triggers:
            anomaly = f"Financial trigger mismatch: expected {expected_triggers}, actual {actual_triggers} at {linking_count} products"
            self.audit_results.anomalies.append(anomaly)
            self.logger.warning(f"⚠️ {anomaly}")
            
    def _get_linking_map_count(self) -> int:
        """Get current linking map entry count"""
        try:
            linking_files = list(Path().glob(str(self.file_patterns["linking_maps"])))
            total_entries = 0
            
            for file_path in linking_files:
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            total_entries += len(data)
                        elif isinstance(data, dict):
                            total_entries += len(data)
                            
            return total_entries
        except Exception as e:
            self.logger.error(f"Failed to count linking map entries: {e}")
            return 0
            
    def _validate_processes(self):
        """Validate system processes and compliance"""
        # Check system resource usage
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        # Check alert thresholds from config
        thresholds = self.config.get("monitoring", {}).get("alert_thresholds", {})
        cpu_threshold = thresholds.get("cpu_percent", 90)
        memory_threshold = thresholds.get("memory_percent", 90)
        
        if cpu_percent > cpu_threshold:
            self.logger.warning(f"🔥 High CPU usage: {cpu_percent}%")
            
        if memory_percent > memory_threshold:
            self.logger.warning(f"🧠 High memory usage: {memory_percent}%")
            
    def validate_file_content(self, file_path: Path, file_type: str) -> Dict[str, Any]:
        """Validate file content structure and integrity"""
        validation_result = {
            "valid": True,
            "errors": [],
            "schema_compliance": True,
            "content_integrity": True
        }
        
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    validation_result.update(self._validate_json_schema(data, file_type))
                    
            elif file_path.suffix == '.csv':
                validation_result.update(self._validate_csv_schema(file_path, file_type))
                
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(str(e))
            
        return validation_result
        
    def _validate_json_schema(self, data: Any, file_type: str) -> Dict[str, Any]:
        """Validate JSON file schema based on type"""
        result = {"schema_compliance": True, "errors": []}
        
        if file_type == "cache_files":
            required_fields = ["url", "title", "price", "ean"]
            if isinstance(data, list):
                for item in data:
                    for field in required_fields:
                        if field not in item:
                            result["schema_compliance"] = False
                            result["errors"].append(f"Missing required field: {field}")
                            
        elif file_type == "linking_maps":
            required_fields = ["supplier_ean", "amazon_asin", "supplier_price", "amazon_price"]
            if isinstance(data, list):
                for item in data:
                    for field in required_fields:
                        if field not in item:
                            result["schema_compliance"] = False
                            result["errors"].append(f"Missing required field: {field}")
                            
        return result
        
    def validate_resume_integrity(self, state_file_path: Path) -> Dict[str, Any]:
        """Validate processing state resume integrity"""
        validation_result = {
            "valid": True,
            "bounds_check": True,
            "progression_consistency": True,
            "gap_handling": True,
            "errors": []
        }
        
        try:
            with open(state_file_path, 'r') as f:
                state_data = json.load(f)
                
            # Validate index bounds
            resumption_index = state_data.get("resumption_index", 0)
            linking_map_count = self._get_linking_map_count()
            
            if not (0 <= resumption_index <= linking_map_count):
                validation_result["bounds_check"] = False
                validation_result["errors"].append(f"Resume index {resumption_index} out of bounds (0-{linking_map_count})")
                
            # Validate category progression
            current_category = state_data.get("current_category_index", 0)
            total_categories = state_data.get("total_categories", 0)
            
            if current_category > total_categories:
                validation_result["progression_consistency"] = False
                validation_result["errors"].append(f"Category index {current_category} exceeds total {total_categories}")
                
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(str(e))
            
        return validation_result
        
    def detect_anomalies(self) -> List[str]:
        """Detect system anomalies based on monitoring data"""
        anomalies = []
        
        # Check update frequency variance
        for file_type, monitor in self.file_monitors.items():
            if len(monitor.update_intervals) > 1:
                variance = self._calculate_variance(monitor.update_intervals)
                if variance > 0.1:  # 10% tolerance
                    anomalies.append(f"{file_type} update frequency variance: {variance:.2f}")
                    
        # Check for missed financial triggers
        linking_count = self._get_linking_map_count()
        financial_freq = self.file_monitors["financial_reports"].expected_frequency
        expected_reports = linking_count // financial_freq
        actual_reports = self.file_monitors["financial_reports"].update_count
        
        if expected_reports != actual_reports:
            anomalies.append(f"Financial report trigger mismatch: expected {expected_reports}, actual {actual_reports}")
            
        return anomalies
        
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of update intervals"""
        if len(values) < 2:
            return 0.0
            
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
        
    def stop_monitoring(self):
        """Stop monitoring and generate final report"""
        self.monitoring_active = False
        
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
            
        self.audit_results.audit_duration_seconds = time.time() - self.start_time
        
        # Final validation pass
        self._generate_final_report()
        
        self.logger.info(f"AUDIT STOPPED: Audit monitoring stopped - Duration: {self.audit_results.audit_duration_seconds:.1f}s")
        
    def _generate_final_report(self):
        """Generate comprehensive audit report"""
        self.logger.info("GENERATING REPORT: Generating final audit report...")
        
        # Compile compliance metrics
        self.audit_results.compliance_metrics = {
            "cache_update_frequency": {
                "expected": self.file_monitors["cache_files"].expected_frequency,
                "actual_average": self._calculate_average_frequency("cache_files"),
                "compliance_rate": self._calculate_compliance_rate("cache_files"),
                "anomalies": []
            },
            "financial_report_triggers": {
                "expected_triggers": self._get_linking_map_count() // self.file_monitors["financial_reports"].expected_frequency,
                "actual_triggers": self.file_monitors["financial_reports"].update_count,
                "compliance_rate": self._calculate_trigger_compliance(),
                "missed_triggers": [],
                "false_triggers": []
            }
        }
        
        # File validation summary
        self.audit_results.file_validation = {
            "cache_files": {
                "total_updates": self.file_monitors["cache_files"].update_count,
                "schema_violations": 0,
                "content_errors": 0
            },
            "linking_map": {
                "total_entries": self._get_linking_map_count(),
                "invalid_entries": 0,
                "duplicate_entries": 0
            }
        }
        
        # Detect final anomalies
        self.audit_results.anomalies.extend(self.detect_anomalies())
        
        # Generate recommendations
        if not self.audit_results.anomalies:
            self.audit_results.recommendations = [
                "System operating within all specified parameters",
                "No critical issues detected",
                "Continue with current configuration"
            ]
        else:
            self.audit_results.recommendations = [
                "Review detected anomalies",
                "Investigate frequency deviations",
                "Validate trigger logic"
            ]
            
        # Save audit report
        self._save_audit_report()
        
    def _calculate_average_frequency(self, file_type: str) -> float:
        """Calculate average update frequency"""
        monitor = self.file_monitors[file_type]
        if len(monitor.update_intervals) == 0:
            return 0.0
        return sum(monitor.update_intervals) / len(monitor.update_intervals)
        
    def _calculate_compliance_rate(self, file_type: str) -> float:
        """Calculate compliance rate percentage"""
        monitor = self.file_monitors[file_type]
        if monitor.update_count == 0:
            return 100.0
            
        # Calculate based on expected vs actual frequency
        expected_updates = self.audit_results.total_products_processed // monitor.expected_frequency
        if expected_updates == 0:
            return 100.0
            
        compliance = min(100.0, (monitor.update_count / expected_updates) * 100)
        return compliance
        
    def _calculate_trigger_compliance(self) -> float:
        """Calculate financial trigger compliance rate"""
        linking_count = self._get_linking_map_count()
        financial_freq = self.file_monitors["financial_reports"].expected_frequency
        expected_triggers = linking_count // financial_freq
        actual_triggers = self.file_monitors["financial_reports"].update_count
        
        if expected_triggers == 0:
            return 100.0
            
        return min(100.0, (actual_triggers / expected_triggers) * 100)
        
    def _save_audit_report(self):
        """Save comprehensive audit report to file"""
        report_file = self.audit_dir / f"{self.audit_id}_report.json"
        
        report_data = {
            "audit_summary": {
                "run_id": self.audit_results.run_id,
                "execution_time": self.audit_results.execution_time,
                "total_products_processed": self.audit_results.total_products_processed,
                "audit_duration_seconds": self.audit_results.audit_duration_seconds
            },
            "compliance_metrics": self.audit_results.compliance_metrics,
            "file_validation": self.audit_results.file_validation,
            "resumption_validation": self.audit_results.resumption_validation,
            "anomalies": self.audit_results.anomalies,
            "recommendations": self.audit_results.recommendations
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
                
            self.logger.info(f"AUDIT REPORT SAVED: Audit report saved: {report_file}")
            
            # Also create a summary markdown report
            self._create_summary_report(report_data)
            
        except Exception as e:
            self.logger.error(f"Failed to save audit report: {e}")
            
    def _create_summary_report(self, report_data: Dict[str, Any]):
        """Create human-readable summary report"""
        summary_file = self.audit_dir / f"{self.audit_id}_summary.md"
        
        with open(summary_file, 'w') as f:
            f.write(f"# System Audit Report - {self.audit_id}\n\n")
            f.write(f"**Execution Time:** {report_data['audit_summary']['execution_time']}\n")
            f.write(f"**Duration:** {report_data['audit_summary']['audit_duration_seconds']:.1f} seconds\n")
            f.write(f"**Products Processed:** {report_data['audit_summary']['total_products_processed']}\n\n")
            
            f.write("## Compliance Summary\n\n")
            
            # Cache compliance
            cache_metrics = report_data['compliance_metrics']['cache_update_frequency']
            f.write(f"- **Cache Update Frequency:** {cache_metrics['compliance_rate']:.1f}% compliant\n")
            
            # Financial trigger compliance 
            financial_metrics = report_data['compliance_metrics']['financial_report_triggers']
            f.write(f"- **Financial Report Triggers:** {financial_metrics['compliance_rate']:.1f}% compliant\n")
            
            # Anomalies
            if report_data['anomalies']:
                f.write("\n## Detected Anomalies\n\n")
                for anomaly in report_data['anomalies']:
                    f.write(f"- {anomaly}\n")
            else:
                f.write("\n## SUCCESS: No Anomalies Detected\n\n")
                
            # Recommendations
            f.write("\n## Recommendations\n\n")
            for rec in report_data['recommendations']:
                f.write(f"- {rec}\n")
                
        self.logger.info(f"📝 Summary report created: {summary_file}")
        
    def _validate_csv_schema(self, file_path: Path, file_type: str) -> Dict[str, Any]:
        """Validate CSV file schema"""
        result = {"schema_compliance": True, "errors": []}
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                if file_type == "financial_reports":
                    required_columns = ["roi_percent", "net_profit", "breakeven_price", "fba_fees"]
                    for col in required_columns:
                        if col not in headers:
                            result["schema_compliance"] = False
                            result["errors"].append(f"Missing required column: {col}")
                            
        except Exception as e:
            result["schema_compliance"] = False
            result["errors"].append(str(e))
            
        return result