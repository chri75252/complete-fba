#!/usr/bin/env python3
"""
Senior Code Investigator - Read-Only Workflow Audit
Discovers all workflow scripts, detects corruption, generates diagnostics.
"""
import os
import sys
import json
import csv
import re
import ast
import difflib
import py_compile
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import tempfile

# Base configuration
BASE_PATH = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-")
OUTPUT_DIR = BASE_PATH / "diagnostics_output"
DIFFS_DIR = OUTPUT_DIR / "diffs"
DUBAI_TZ = timezone(timedelta(hours=4))

# High-risk files (explicit acceptance test requirement)
HIGH_RISK_FILES = [
    "tools\\authentication_manager.py",
    "tools\\cache_manager.py",
    "utils\\path_manager.py"
]

# Issue taxonomy
ISSUE_TYPES = {
    'BinaryZipBlob': 'critical',
    'BinaryGeneric': 'critical',
    'EncodingMismatch': 'medium',
    'CRonly_LineEndings': 'medium',
    'Truncated': 'high',
    'OverwrittenOlderVersion': 'high',
    'SyntaxError': 'critical',
    'MissingSymbols': 'high',
    'MissingFile': 'critical',
    'Other': 'low'
}

class WorkflowAuditor:
    def __init__(self):
        self.workflow_files = {}  # path -> {discovered_via: [sources]}
        self.broken_files = []
        self.all_imports = defaultdict(set)
        self.defined_symbols = defaultdict(set)
        self._backup_dirs = None  # Cache for backup directories
        
    def discover_from_docs(self):
        """Parse workflow docs for referenced scripts"""
        doc_files = [
            BASE_PATH / "latest_workflow.md",
            BASE_PATH / "AGENTS.md",
        ]
        
        # Find walkthrough files
        for pattern in ["walkthrough*", "walkthrough*/*"]:
            doc_files.extend(BASE_PATH.glob(pattern))
        
        code_pattern = re.compile(r'(?:^|\s|`)((?:tools|utils|agents|config|dashboard)/[\w/\\]+\.py)', re.MULTILINE)
        module_pattern = re.compile(r'(?:from|import)\s+([\w.]+)', re.MULTILINE)
        
        for doc in doc_files:
            if not doc.exists() or not doc.is_file():
                continue
                
            try:
                content = doc.read_text(encoding='utf-8', errors='ignore')
                
                # Find direct file references
                for match in code_pattern.finditer(content):
                    file_path = match.group(1).replace('/', '\\')
                    full_path = BASE_PATH / file_path
                    if full_path.exists():
                        self._add_workflow_file(file_path, f"doc:{doc.name}")
                
                # Find module references
                for match in module_pattern.finditer(content):
                    module = match.group(1)
                    if '.' in module:
                        parts = module.split('.')
                        if parts[0] in ['tools', 'utils', 'agents', 'config', 'dashboard']:
                            file_path = '/'.join(parts) + '.py'
                            file_path = file_path.replace('/', '\\')
                            full_path = BASE_PATH / file_path
                            if full_path.exists():
                                self._add_workflow_file(file_path, f"doc:{doc.name}")
                                
            except Exception as e:
                print(f"Warning: Could not parse {doc}: {e}", file=sys.stderr)
    
    def discover_from_imports(self):
        """Build import graph from root packages"""
        root_packages = ['tools', 'utils', 'agents', 'config', 'dashboard']
        
        for pkg in root_packages:
            pkg_path = BASE_PATH / pkg
            if not pkg_path.exists():
                continue
                
            for py_file in pkg_path.rglob('*.py'):
                rel_path = py_file.relative_to(BASE_PATH).as_posix().replace('/', '\\')
                self._add_workflow_file(rel_path, "import_scan")
                self._extract_imports(py_file, rel_path)
        
        # Add root-level scripts
        for py_file in BASE_PATH.glob('*.py'):
            if py_file.name.startswith('run_') or py_file.name.startswith('test_'):
                rel_path = py_file.relative_to(BASE_PATH).as_posix().replace('/', '\\')
                self._add_workflow_file(rel_path, "root_script")
                self._extract_imports(py_file, rel_path)
    
    def _add_workflow_file(self, rel_path, source):
        """Add file to workflow registry"""
        if rel_path not in self.workflow_files:
            self.workflow_files[rel_path] = {'discovered_via': []}
        if source not in self.workflow_files[rel_path]['discovered_via']:
            self.workflow_files[rel_path]['discovered_via'].append(source)
    
    def _extract_imports(self, file_path, rel_path):
        """Extract imports from a Python file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            try:
                tree = ast.parse(content, filename=str(file_path))
                
                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.all_imports[rel_path].add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.all_imports[rel_path].add(node.module)
                            # Add transitive imports
                            if node.module.split('.')[0] in ['tools', 'utils', 'agents', 'config', 'dashboard']:
                                imp_file = node.module.replace('.', '\\') + '.py'
                                self._add_workflow_file(imp_file, f"imported_by:{rel_path}")
                
                # Extract defined symbols
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                        self.defined_symbols[rel_path].add(node.name)
                        
            except SyntaxError:
                pass  # Will be caught in health check
        except Exception:
            pass
    
    def add_high_risk_files(self):
        """Explicitly add high-risk files"""
        for rel_path in HIGH_RISK_FILES:
            self._add_workflow_file(rel_path, "high_risk_explicit")
    
    def check_file_health(self, rel_path):
        """Perform comprehensive health check on a file"""
        file_path = BASE_PATH / rel_path
        issues = []
        
        # Check existence
        if not file_path.exists():
            return [{
                'path': rel_path,
                'issue_type': 'MissingFile',
                'severity': 'critical',
                'reason': 'Referenced in workflow but file does not exist',
                'evidence_excerpt': 'N/A',
                'discovered_via': ', '.join(self.workflow_files[rel_path]['discovered_via']),
                'candidate_restore_source': self._find_backup_candidate(rel_path)
            }]
        
        # Binary/encoding scan
        try:
            raw_bytes = file_path.read_bytes()
            
            # Check for ZIP signatures
            if b'PK\x03\x04' in raw_bytes or b'PK\x05\x06' in raw_bytes or b'PK\x07\x08' in raw_bytes:
                issues.append({
                    'path': rel_path,
                    'issue_type': 'BinaryZipBlob',
                    'severity': 'critical',
                    'reason': 'ZIP signature detected in Python file',
                    'evidence_excerpt': f'PK pattern at offset {raw_bytes.find(b"PK")}',
                    'discovered_via': ', '.join(self.workflow_files[rel_path]['discovered_via']),
                    'candidate_restore_source': self._find_backup_candidate(rel_path)
                })
                return issues
            
            # Check for null bytes and control characters
            null_count = raw_bytes.count(b'\x00')
            control_bytes = sum(1 for b in raw_bytes if b < 32 and b not in (9, 10, 13))
            control_ratio = control_bytes / max(len(raw_bytes), 1)
            
            if null_count > 0 or control_ratio > 0.005:
                issues.append({
                    'path': rel_path,
                    'issue_type': 'BinaryGeneric',
                    'severity': 'critical',
                    'reason': f'{null_count} null bytes, {control_ratio:.2%} control chars',
                    'evidence_excerpt': f'First 50 bytes: {raw_bytes[:50]!r}',
                    'discovered_via': ', '.join(self.workflow_files[rel_path]['discovered_via']),
                    'candidate_restore_source': self._find_backup_candidate(rel_path)
                })
                return issues
            
            # Check line endings
            if b'\r' in raw_bytes and b'\n' not in raw_bytes:
                issues.append({
                    'path': rel_path,
                    'issue_type': 'CRonly_LineEndings',
                    'severity': 'medium',
                    'reason': 'Classic Mac (CR-only) line endings detected',
                    'evidence_excerpt': 'All line breaks are \\r without \\n',
                    'discovered_via': ', '.join(self.workflow_files[rel_path]['discovered_via']),
                    'candidate_restore_source': self._find_backup_candidate(rel_path)
                })
            
            # Encoding check
            try:
                content = raw_bytes.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content = raw_bytes.decode('cp1252')
                    non_ascii = sum(1 for c in content if ord(c) > 127)
                    if non_ascii / max(len(content), 1) > 0.7:
                        issues.append({
                            'path': rel_path,
                            'issue_type': 'EncodingMismatch',
                            'severity': 'medium',
                            'reason': 'UTF-8 decode failed, cp1252 has >70% non-ASCII',
                            'evidence_excerpt': f'{non_ascii}/{len(content)} non-ASCII chars',
                            'discovered_via': ', '.join(self.workflow_files[rel_path]['discovered_via']),
                            'candidate_restore_source': self._find_backup_candidate(rel_path)
                        })
                except:
                    issues.append({
                        'path': rel_path,
                        'issue_type': 'EncodingMismatch',
                        'severity': 'medium',
                        'reason': 'Cannot decode as UTF-8 or cp1252',
                        'evidence_excerpt': 'Encoding detection failed',
                        'discovered_via': ', '.join(self.workflow_files[rel_path]['discovered_via']),
                        'candidate_restore_source': self._find_backup_candidate(rel_path)
                    })
                    return issues
            
            # Syntax check
            if rel_path.endswith('.py'):
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp:
                        tmp.write(content)
                        tmp_path = tmp.name
                    try:
                        py_compile.compile(tmp_path, doraise=True)
                    finally:
                        os.unlink(tmp_path)
                except py_compile.PyCompileError as e:
                    issues.append({
                        'path': rel_path,
                        'issue_type': 'SyntaxError',
                        'severity': 'critical',
                        'reason': f'Python syntax error: {str(e)[:100]}',
                        'evidence_excerpt': str(e)[:200],
                        'discovered_via': ', '.join(self.workflow_files[rel_path]['discovered_via']),
                        'candidate_restore_source': self._find_backup_candidate(rel_path)
                    })
            
            # Size check (truncation)
            candidate = self._find_backup_candidate(rel_path)
            if candidate:
                candidate_path = BASE_PATH.parent / candidate / rel_path
                if candidate_path.exists():
                    candidate_size = candidate_path.stat().st_size
                    current_size = file_path.stat().st_size
                    if current_size < candidate_size * 0.5:  # More than 50% smaller
                        issues.append({
                            'path': rel_path,
                            'issue_type': 'Truncated',
                            'severity': 'high',
                            'reason': f'File is {current_size} bytes vs {candidate_size} in backup',
                            'evidence_excerpt': f'{(1 - current_size/candidate_size):.0%} smaller',
                            'discovered_via': ', '.join(self.workflow_files[rel_path]['discovered_via']),
                            'candidate_restore_source': candidate
                        })
                        self._generate_diff(rel_path, candidate_path, file_path)
            
            # Version check (overwritten)
            if candidate and not any(i['issue_type'] == 'Truncated' for i in issues):
                candidate_path = BASE_PATH.parent / candidate / rel_path
                if candidate_path.exists():
                    try:
                        candidate_content = candidate_path.read_text(encoding='utf-8', errors='ignore')
                        diff_ratio = difflib.SequenceMatcher(None, content, candidate_content).ratio()
                        
                        if diff_ratio < 0.8:  # Significant difference
                            # Check for missing APIs
                            try:
                                current_tree = ast.parse(content)
                                candidate_tree = ast.parse(candidate_content)
                                
                                current_defs = {n.name for n in ast.walk(current_tree) 
                                              if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
                                candidate_defs = {n.name for n in ast.walk(candidate_tree)
                                                if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
                                
                                missing = candidate_defs - current_defs
                                if missing:
                                    issues.append({
                                        'path': rel_path,
                                        'issue_type': 'OverwrittenOlderVersion',
                                        'severity': 'high',
                                        'reason': f'Missing {len(missing)} symbols vs backup: {", ".join(list(missing)[:5])}',
                                        'evidence_excerpt': f'Similarity: {diff_ratio:.1%}',
                                        'discovered_via': ', '.join(self.workflow_files[rel_path]['discovered_via']),
                                        'candidate_restore_source': candidate
                                    })
                                    self._generate_diff(rel_path, candidate_path, file_path)
                            except:
                                pass
                    except:
                        pass
        
        except Exception as e:
            issues.append({
                'path': rel_path,
                'issue_type': 'Other',
                'severity': 'low',
                'reason': f'Health check error: {str(e)[:100]}',
                'evidence_excerpt': str(e)[:200],
                'discovered_via': ', '.join(self.workflow_files[rel_path]['discovered_via']),
                'candidate_restore_source': ''
            })
        
        return issues if issues else None
    
    def _find_backup_candidate(self, rel_path):
        """Find best backup candidate for a file"""
        parent = BASE_PATH.parent
        backup_markers = ['good', 'backup', 'copy', 'old', 'Copy']
        
        # Cache backup directories
        if self._backup_dirs is None:
            self._backup_dirs = []
            try:
                for sibling in parent.iterdir():
                    if not sibling.is_dir() or sibling == BASE_PATH:
                        continue
                    name_lower = sibling.name.lower()
                    if any(marker in name_lower for marker in backup_markers):
                        self._backup_dirs.append(sibling)
            except Exception:
                pass
        
        candidates = []
        for backup_dir in self._backup_dirs:
            candidate_file = backup_dir / rel_path
            if candidate_file.exists():
                candidates.append((backup_dir.name, candidate_file))
        
        if not candidates:
            return ''
        
        # Prefer "good" in name, then most recent mtime
        candidates.sort(key=lambda x: (
            'good' in x[0].lower(),
            x[1].stat().st_mtime
        ), reverse=True)
        
        return candidates[0][0]
    
    def _generate_diff(self, rel_path, candidate_path, current_path):
        """Generate unified diff"""
        try:
            candidate_lines = candidate_path.read_text(encoding='utf-8', errors='ignore').splitlines(keepends=True)
            current_lines = current_path.read_text(encoding='utf-8', errors='ignore').splitlines(keepends=True)
            
            diff = difflib.unified_diff(
                current_lines,
                candidate_lines,
                fromfile=f"current/{rel_path}",
                tofile=f"candidate/{rel_path}",
                lineterm=''
            )
            
            diff_path = DIFFS_DIR / f"{rel_path.replace(chr(92), '_')}.diff.txt"
            diff_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(diff_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(diff))
                
        except Exception as e:
            print(f"Warning: Could not generate diff for {rel_path}: {e}", file=sys.stderr)
    
    def run_audit(self):
        """Execute full audit workflow"""
        print("=" * 80)
        print("WORKFLOW FILE DISCOVERY & CORRUPTION AUDIT")
        print(f"Timestamp: {datetime.now(DUBAI_TZ).strftime('%Y-%m-%d %H:%M UTC+4')}")
        print(f"Base Path: {BASE_PATH}")
        print("=" * 80)
        print()
        
        # Step 1: Discover workflow files
        print("[1/4] Discovering workflow files from docs...")
        self.discover_from_docs()
        
        print("[2/4] Building import graph...")
        self.discover_from_imports()
        
        print("[3/4] Adding high-risk files...")
        self.add_high_risk_files()
        
        print(f"      Total workflow files discovered: {len(self.workflow_files)}")
        print()
        
        # Step 2: Health checks
        print("[4/4] Running health checks...")
        total = len(self.workflow_files)
        for idx, rel_path in enumerate(sorted(self.workflow_files.keys()), 1):
            if idx % 20 == 0:
                print(f"      Progress: {idx}/{total}...")
            issues = self.check_file_health(rel_path)
            if issues:
                self.broken_files.extend(issues)
        
        print(f"      Files with issues: {len(self.broken_files)}")
        print()
        
        # Step 3: Generate outputs
        self._save_workflow_files()
        self._save_broken_files()
        self._print_report()
    
    def _save_workflow_files(self):
        """Save workflow_files.json"""
        output = {
            'timestamp': datetime.now(DUBAI_TZ).isoformat(),
            'base_path': str(BASE_PATH),
            'total_files': len(self.workflow_files),
            'files': self.workflow_files
        }
        
        with open(OUTPUT_DIR / 'workflow_files.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
    
    def _save_broken_files(self):
        """Save broken_files.csv"""
        if not self.broken_files:
            return
        
        with open(OUTPUT_DIR / 'broken_files.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'path', 'issue_type', 'severity', 'reason', 
                'evidence_excerpt', 'discovered_via', 'candidate_restore_source'
            ])
            writer.writeheader()
            writer.writerows(self.broken_files)
    
    def _print_report(self):
        """Print Markdown report to STDOUT"""
        print("=" * 80)
        print("# AUDIT REPORT")
        print("=" * 80)
        print()
        print(f"**Timestamp:** {datetime.now(DUBAI_TZ).strftime('%Y-%m-%d %H:%M UTC+4')}")
        print(f"**Base Path:** `{BASE_PATH}`")
        print()
        
        # Summary counts
        print("## Summary")
        print()
        print(f"- **Total workflow scripts:** {len(self.workflow_files)}")
        print(f"- **Files with issues:** {len(self.broken_files)}")
        print()
        
        # Severity breakdown
        severity_counts = defaultdict(int)
        for issue in self.broken_files:
            severity_counts[issue['severity']] += 1
        
        print("### Issues by Severity")
        print()
        for sev in ['critical', 'high', 'medium', 'low']:
            count = severity_counts[sev]
            if count > 0:
                print(f"- **{sev.upper()}:** {count}")
        print()
        
        # Top broken files
        if self.broken_files:
            print("## Top 15 Broken Files")
            print()
            print("| Path | Issue Type | Severity | Reason |")
            print("|------|------------|----------|--------|")
            
            for issue in sorted(self.broken_files, 
                              key=lambda x: (ISSUE_TYPES.get(x['issue_type'], 'low'), x['path']))[:15]:
                path_short = issue['path'][:40] + '...' if len(issue['path']) > 40 else issue['path']
                reason_short = issue['reason'][:50] + '...' if len(issue['reason']) > 50 else issue['reason']
                print(f"| {path_short} | {issue['issue_type']} | {issue['severity']} | {reason_short} |")
            print()
        
        # High-risk files (ACCEPTANCE TEST)
        print("## High-Risk Files (Acceptance Test)")
        print()
        print("| Path | Status | Issue Type | Severity |")
        print("|------|--------|------------|----------|")
        
        for hr_file in HIGH_RISK_FILES:
            issues = [i for i in self.broken_files if i['path'] == hr_file]
            if issues:
                issue = issues[0]
                print(f"| {hr_file} | ❌ BROKEN | {issue['issue_type']} | {issue['severity']} |")
            elif hr_file in self.workflow_files:
                print(f"| {hr_file} | ✅ OK | - | - |")
            else:
                print(f"| {hr_file} | ⚠️ NOT FOUND | - | - |")
        print()
        
        # Artifacts
        print("## Generated Artifacts")
        print()
        print(f"- `diagnostics_output/workflow_files.json` — {len(self.workflow_files)} files")
        print(f"- `diagnostics_output/broken_files.csv` — {len(self.broken_files)} issues")
        
        diff_count = len(list(DIFFS_DIR.glob('*.diff.txt'))) if DIFFS_DIR.exists() else 0
        print(f"- `diagnostics_output/diffs/*.diff.txt` — {diff_count} diffs")
        print()
        
        print("=" * 80)
        print("END OF REPORT")
        print("=" * 80)

if __name__ == '__main__':
    auditor = WorkflowAuditor()
    auditor.run_audit()
