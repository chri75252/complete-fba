import json
import os
import sys
import re
import time
import threading
import traceback
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Any, Optional
import pandas as pd

# In-memory AI analysis job store
_ai_jobs: dict = {}

# Add the parent directory to sys.path so we can import from dashboard and control_plane
PARENT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(PARENT_DIR))

try:
    from dashboard_legacy_streamlit.metrics_core import MetricsLoader, load_metrics
    from control_plane.job_manager import JobManager
except ImportError as e:
    print(f"Error importing metrics/job modules: {e}")

try:
    from control_plane.audit import write_session_transcript
    from control_plane.chat_orchestrator import (
        ToolCall,
        AgentStep,
        agent_plan_step,
        audit_tool_call,
        execute_tool_call,
        _compute_rag_info,
    )
    from control_plane.env_config import ensure_llm_env
    CHAT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Chat modules not available: {e}")
    CHAT_AVAILABLE = False

app = FastAPI(title="Amazon FBA Agent System API")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _new_session_id() -> str:
    return f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid4().hex[:8]}"

# ---- In-memory chat session state (mirrors Streamlit session_state) ----
chat_state = {
    "messages": [],
    "scratchpad": [],
    "trace": [],
    "tool_executions": [],
    "turn_history": [],
    "pending_tool_call": None,
    "pending_user_text": None,
    "pending_rag_info": None,
    "last_run_id": None,
    "last_products_path": None,
    "last_supplier_domain": None,
    "last_sandbox_supplier": None,
    "session_id": _new_session_id(),
    "session_started_at": _now_iso(),
}


MAX_AGENT_STEPS = 10

class ChatRequest(BaseModel):
    message: str
    supplier: Optional[str] = "poundwholesale.co.uk"

class ApproveRequest(BaseModel):
    approve: bool

# Mount the static directory
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

def get_base_directory():
    """Get the correct base directory for the FBA system"""
    candidates = [
        os.environ.get("FBA_BASE_DIR"),
        str(PARENT_DIR),
        os.getcwd(),
        ".",
    ]
    for candidate in candidates:
        if candidate and os.path.exists(os.path.join(candidate, "OUTPUTS")):
            return candidate
    return os.getcwd()

def validate_supplier_data(base_dir, supplier):
    loader = MetricsLoader(base_dir)
    paths = loader.resolve_paths(supplier)
    issues = []
    if not paths.get("state_file") or not os.path.exists(paths["state_file"]):
        issues.append("State file not found")
    if not paths.get("linking_file") or not os.path.exists(paths["linking_file"]):
        issues.append("Linking map file not found")
    if not paths.get("financial_dir") or not os.path.exists(paths["financial_dir"]):
        issues.append("Financial reports directory not found")
    if not paths.get("logs_dir") or not os.path.exists(paths["logs_dir"]):
        issues.append("Logs directory not found")
    return issues, paths

@app.get("/")
def read_root():
    index_path = Path(__file__).parent / "templates" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "index.html not found"}

@app.get("/api/metrics/{supplier}")
def get_supplier_metrics(supplier: str, lineage: str = "base", report: str = ""):
    base_dir = get_base_directory()
    try:
        effective_supplier = supplier
        if lineage == "latest_sandbox":
            loader = MetricsLoader(base_dir)
            latest = loader.discover_latest_sandbox_supplier(supplier)
            if latest:
                effective_supplier = latest

        issues, paths = validate_supplier_data(base_dir, effective_supplier)
        if issues:
            return JSONResponse({
                "error": True,
                "issues": issues,
                "paths": paths,
                "state_metrics": {"state_file_found": False},
                "linking_metrics": {"total_matches": 0},
                "financial_metrics": {"files_scanned": 0},
                "log_data": [[], None],
                "meta": {
                    "requested_supplier": supplier,
                    "lineage": lineage,
                    "effective_supplier": effective_supplier,
                },
            })

        # We need to serialize paths object cleanly (POSIX paths to str)
        metrics_data = load_metrics(base_dir, effective_supplier)
        metrics_data["meta"] = {
            "requested_supplier": supplier,
            "lineage": lineage,
            "effective_supplier": effective_supplier,
        }
        metrics_data.setdefault("paths", {})["base_dir"] = base_dir

        # Override total_products with cached_products entry count (processing_state value is per-category only)
        try:
            cp_path = metrics_data.get("paths", {}).get("cached_products_file")
            if cp_path and os.path.exists(cp_path):
                cp_data = json.loads(Path(cp_path).read_text(encoding="utf-8"))
                if isinstance(cp_data, list):
                    metrics_data.setdefault("state_metrics", {})["total_products"] = len(cp_data)
        except Exception:
            pass

        # Fix log lineage: ensure logs match requested lineage (base vs sandbox)
        try:
            logs_dir = str(Path(base_dir) / "logs" / "debug")
            if os.path.exists(logs_dir):
                norm = supplier.replace(".", "-").replace(" ", "-").lower()
                all_logs = [f for f in os.listdir(logs_dir) if f.endswith(".log")]
                if lineage == "base":
                    matching = sorted(
                        [f for f in all_logs if f"run_custom_{norm}" in f and "__sandbox__" not in f],
                        key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True
                    )
                else:
                    norm_eff = effective_supplier.replace(".", "-").replace(" ", "-").lower()
                    matching = sorted(
                        [f for f in all_logs if f"run_custom_{norm_eff}" in f],
                        key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True
                    )
                if matching:
                    with open(os.path.join(logs_dir, matching[0]), encoding="utf-8", errors="replace") as lf:
                        lines = lf.readlines()[-200:]
                    metrics_data["log_data"] = [[line.rstrip() for line in lines], matching[0]]
                else:
                    metrics_data["log_data"] = [[], None]
        except Exception as log_err:
            print(f"[LOG-LINEAGE-FIX] Error: {log_err}")

        # Load chart data + override metrics with EAN-matched-only values
        chart_data = []
        fin_dir = metrics_data.get("paths", {}).get("financial_dir")
        latest_file = metrics_data.get("financial_metrics", {}).get("latest_file")

        # If a specific report was requested, override the auto-detected latest
        if report and fin_dir:
            specific = os.path.join(fin_dir, report)
            if os.path.exists(specific):
                latest_file = report
        csv_full_path = os.path.join(fin_dir, latest_file) if fin_dir and latest_file else ""
        print(f"[METRICS-DEBUG] fin_dir={fin_dir} latest_file={latest_file} exists={os.path.exists(csv_full_path) if csv_full_path else False}")
        if fin_dir and latest_file and os.path.exists(csv_full_path):
            try:
                df = pd.read_csv(
                    csv_full_path,
                    engine='python',
                    on_bad_lines='skip',
                    encoding='utf-8',
                    encoding_errors='replace',
                )
                # Normalize variant column names across different report formats
                _col_renames = {'ROI ( % )': 'ROI', 'ROI (%)': 'ROI', 'Net Profit': 'NetProfit'}
                df.rename(columns={k: v for k, v in _col_renames.items() if k in df.columns}, inplace=True)
                if not df.empty:
                    # Numeric conversion
                    for col in ['SupplierPrice_incVAT', 'SellingPrice_incVAT', 'NetProfit', 'ROI',
                                'fba_seller_count', 'fbm_seller_count', 'total_offer_count',
                                'bought_in_past_month']:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')

                    # --- EAN matching filter ---
                    def _norm_ean(s):
                        if pd.isna(s): return ""
                        s = str(s).strip()
                        # Handle float notation (e.g. 5033601694236.0)
                        if s.endswith(".0"): s = s[:-2]
                        # Handle scientific notation (e.g. 5.03360169424E+12 from Excel exports)
                        if 'e' in s.lower():
                            try:
                                s = str(int(float(s)))
                            except (ValueError, OverflowError):
                                pass
                        return re.sub(r"[^0-9]", "", s)

                    if 'EAN' in df.columns and 'EAN_OnPage' in df.columns:
                        df['_ean_norm'] = df['EAN'].apply(_norm_ean)
                        df['_ean_page_norm'] = df['EAN_OnPage'].apply(_norm_ean)
                        ean_mask = (df['_ean_norm'].str.len() > 0) & (df['_ean_page_norm'].str.len() > 0) & (df['_ean_norm'] == df['_ean_page_norm'])
                        df['_ean_matched'] = ean_mask
                    else:
                        df['_ean_matched'] = True  # fallback: treat all as matched

                    # --- Override top-row metrics with EAN-matched only ---
                    df_matched = df[df['_ean_matched']].dropna(subset=['NetProfit'])
                    profitable = df_matched[df_matched['NetProfit'] > 0]
                    fm = metrics_data.get("financial_metrics", {})
                    fm["ean_matched_rows"] = int(df['_ean_matched'].sum())
                    fm["count_profitable"] = len(profitable)
                    fm["avg_roi"] = round(float(profitable['ROI'].mean()) if 'ROI' in profitable.columns and len(profitable) > 0 else 0.0, 1)
                    fm["avg_profit"] = round(float(profitable['NetProfit'].mean()) if len(profitable) > 0 else 0.0, 2)
                    fm["total_profit"] = fm["avg_profit"]  # frontend reads total_profit
                    # Sales-aware metrics
                    if 'bought_in_past_month' in profitable.columns:
                        profitable_with_sales = profitable[profitable['bought_in_past_month'].fillna(0).astype(float) > 0]
                    else:
                        profitable_with_sales = profitable.iloc[0:0]
                    fm["count_profitable_with_sales"] = len(profitable_with_sales)

                    # --- Category enrichment from cached products ---
                    try:
                        cache_path = metrics_data.get("paths", {}).get("cached_products_file")
                        url_to_category = {}
                        if cache_path and os.path.exists(cache_path):
                            import json as _json
                            cached = _json.loads(Path(cache_path).read_text(encoding="utf-8"))
                            for item in (cached if isinstance(cached, list) else []):
                                prod_url = item.get("url", "")
                                src_url = item.get("source_url", "")
                                if prod_url and src_url:
                                    parts = [p for p in src_url.split("/") if p and "." not in p and "http" not in p and len(p) > 2]
                                    cat_name = parts[-1].replace("-", " ").title() if parts else "Other"
                                    url_to_category[prod_url.rstrip("/")] = cat_name
                        if 'SupplierURL' in df.columns and url_to_category:
                            df['Category'] = df['SupplierURL'].apply(
                                lambda u: url_to_category.get(str(u).rstrip("/"), "Other") if pd.notna(u) else "Other"
                            )
                        else:
                            df['Category'] = 'Other'
                    except Exception:
                        df['Category'] = 'Other'

                    # --- Build chart_data: EAN-matched rows for charts ---
                    df_chart = df[df['_ean_matched']].dropna(subset=['ROI', 'NetProfit']).head(2000)
                    chart_cols = ['SupplierTitle', 'AmazonTitle', 'SupplierPrice_incVAT',
                                  'SellingPrice_incVAT', 'NetProfit', 'ROI', 'MatchQuality', 'Category']
                    for extra in ['fba_seller_count', 'fbm_seller_count', 'total_offer_count', 'bought_in_past_month']:
                        if extra in df.columns:
                            chart_cols.append(extra)
                    chart_cols = [c for c in chart_cols if c in df_chart.columns]
                    chart_data = df_chart[chart_cols].fillna(0).to_dict(orient='records')
            except Exception as e:
                print(f"[METRICS-DEBUG] Error loading CSV: {e}\n{traceback.format_exc()}")

        metrics_data["chart_data"] = chart_data

        # C4 FIX: Populate available_reports so dashboard Financial Report dropdown is populated
        if fin_dir and os.path.exists(fin_dir):
            _csv_files = sorted(
                [f for f in os.listdir(fin_dir) if f.endswith(".csv")],
                key=lambda f: os.path.getmtime(os.path.join(fin_dir, f)),
                reverse=True
            )
            metrics_data["available_reports"] = []
            for _f in _csv_files[:20]:
                try:
                    with open(os.path.join(fin_dir, _f), encoding="utf-8", errors="replace") as _rf:
                        _row_count = max(0, sum(1 for _ in _rf) - 1)
                except Exception:
                    _row_count = 0
                metrics_data["available_reports"].append({"filename": _f, "rows": _row_count})

        # Data source mapping for dashboard transparency
        metrics_data["data_sources"] = {
            "cached_products": str(metrics_data.get("paths", {}).get("cached_products_file") or ""),
            "linking_map": str(metrics_data.get("paths", {}).get("linking_map_file") or ""),
            "financial_report": latest_file or "",
            "processing_state": str(metrics_data.get("paths", {}).get("state_file") or ""),
            "log_file": str((metrics_data.get("log_data") or [[], None])[1] or ""),
        }

        # Fix paths types for JSON serialization
        if "paths" in metrics_data:
            for k, v in metrics_data["paths"].items():
                if v is not None:
                    metrics_data["paths"][k] = str(v)
                    
        return metrics_data
    except Exception as e:
        import traceback
        return JSONResponse({"error": True, "issues": [str(e)], "traceback": traceback.format_exc()}, status_code=500)


@app.get("/api/validate/{supplier}")
def run_validation(supplier: str, lineage: str = "base"):
    base_dir = get_base_directory()
    effective_supplier = supplier
    if lineage == "latest_sandbox":
        loader = MetricsLoader(base_dir)
        latest = loader.discover_latest_sandbox_supplier(supplier)
        if latest:
            effective_supplier = latest

    issues, paths = validate_supplier_data(base_dir, effective_supplier)
    checks: dict[str, Any] = {}

    state_file = paths.get("state_file")
    if state_file and os.path.exists(state_file):
        try:
            state = json.loads(Path(state_file).read_text(encoding="utf-8"))
            checks["state_total_categories"] = (
                state.get("system_progression", {}).get("total_categories")
            )
            checks["state_has_resume_pointer"] = (
                "resume_pointer" in state.get("system_progression", {})
            )
            checks["state_readable"] = True
        except Exception:
            checks["state_readable"] = False

    linking_file = paths.get("linking_file")
    if linking_file and os.path.exists(linking_file):
        try:
            linking_map = json.loads(Path(linking_file).read_text(encoding="utf-8"))
            checks["linking_map_entries"] = len(linking_map) if isinstance(linking_map, list) else 0
            checks["linking_map_readable"] = True
        except Exception:
            checks["linking_map_readable"] = False

    return JSONResponse(
        {
            "requested_supplier": supplier,
            "effective_supplier": effective_supplier,
            "lineage": lineage,
            "issues": issues,
            "checks": checks,
            "paths": {k: str(v) if v else None for k, v in paths.items()},
            "valid": len(issues) == 0,
        }
    )

@app.get("/api/analysis/{supplier}")
def get_analysis(supplier: str, lineage: str = "base", tier: str = "all",
                 min_roi: Optional[float] = None, min_profit: Optional[float] = None,
                 sort: str = "confidence", min_sales: Optional[int] = None,
                 page: int = 1, page_size: int = 50000,  # C3 FIX: removed 500-row cap; frontend paginates
                 report: Optional[str] = None, category: Optional[str] = None):
    """Classify financial report rows into confidence tiers and return filtered results."""
    base_dir = get_base_directory()
    try:
        effective_supplier = supplier
        if lineage == "latest_sandbox":
            loader = MetricsLoader(base_dir)
            latest = loader.discover_latest_sandbox_supplier(supplier)
            if latest:
                effective_supplier = latest

        # Find financial report directory
        loader = MetricsLoader(base_dir)
        paths = loader.resolve_paths(effective_supplier)
        fin_dir = paths.get("financial_dir")

        if not fin_dir or not os.path.exists(fin_dir):
            return JSONResponse({"error": True, "message": "No financial reports directory found"})

        # Use specified report filename or fall back to latest
        if report:
            csv_path = os.path.join(fin_dir, report)
            if not os.path.exists(csv_path):
                return JSONResponse({"error": True, "message": f"Report not found: {report}"})
        else:
            csv_files = sorted(
                [f for f in os.listdir(fin_dir) if f.endswith('.csv')],
                key=lambda f: os.path.getmtime(os.path.join(fin_dir, f)),
                reverse=True
            )
            if not csv_files:
                return JSONResponse({"error": True, "message": "No financial report CSVs found"})
            csv_path = os.path.join(fin_dir, csv_files[0])

        # Import the filter module
        import importlib.util
        filter_path = PARENT_DIR / "tools" / "fba_report_filter.py"
        if not filter_path.exists():
            return JSONResponse({"error": True, "message": "fba_report_filter.py not found in tools/"})

        spec = importlib.util.spec_from_file_location("fba_report_filter", str(filter_path))
        filter_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(filter_mod)

        # Read and classify rows
        import csv as csv_mod
        rows = []
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv_mod.DictReader(f)
            for i, row in enumerate(reader, start=2):
                row["_row_id"] = i
                classification = filter_mod.classify_row(row)
                row.update(classification)
                rows.append(row)

        # Compute tier counts (before filtering)
        tier_counts = {}
        for r in rows:
            t = r.get("tier", "UNKNOWN")
            tier_counts[t] = tier_counts.get(t, 0) + 1
        total_rows = len(rows)

        # Apply filters
        if tier != "all":
            rows = [r for r in rows if r.get("tier") == tier]
        if min_roi is not None:
            rows = [r for r in rows if float(r.get("ROI", 0) or 0) >= min_roi / 100]
        if min_profit is not None:
            rows = [r for r in rows if float(r.get("NetProfit", 0) or 0) >= min_profit]
        if min_sales is not None:
            def _safe_sales(val):
                try:
                    return int(float(val)) if val and str(val).strip() else 0
                except (ValueError, TypeError):
                    return 0
            rows = [r for r in rows if _safe_sales(r.get("bought_in_past_month")) >= min_sales]

        # Category enrichment from cached products
        url_to_category = {}
        try:
            loader_cat = MetricsLoader(base_dir)
            cat_paths = loader_cat.resolve_paths(effective_supplier)
            cache_path = cat_paths.get("cached_products_file")
            if cache_path and os.path.exists(cache_path):
                cached = json.loads(Path(cache_path).read_text(encoding="utf-8"))
                for item in (cached if isinstance(cached, list) else []):
                    prod_url = item.get("url", "")
                    src_url = item.get("source_url", "")
                    if prod_url and src_url:
                        parts = [p for p in src_url.split("/") if p and "." not in p and "http" not in p and len(p) > 2]
                        cat_name = parts[-1].replace("-", " ").title() if parts else "Other"
                        url_to_category[prod_url.rstrip("/")] = cat_name
        except Exception:
            pass

        for r in rows:
            sup_url = r.get("SupplierURL", "").rstrip("/")
            r["Category"] = url_to_category.get(sup_url, "Other") if url_to_category else "Other"

        # Collect distinct categories before applying category filter (for dropdown population)
        distinct_categories = sorted(set(r["Category"] for r in rows))

        # Apply category filter
        if category:
            rows = [r for r in rows if r.get("Category") == category]

        # Sort
        if sort == "confidence":
            rows.sort(key=lambda r: r.get("confidence_score", 0), reverse=True)
        elif sort == "roi":
            rows.sort(key=lambda r: float(r.get("ROI", 0) or 0), reverse=True)
        elif sort == "profit":
            rows.sort(key=lambda r: float(r.get("NetProfit", 0) or 0), reverse=True)

        # Limit to page_size rows for performance
        rows = rows[:page_size]

        # Clean rows for JSON
        clean_rows = []
        for r in rows:
            clean_rows.append({
                "_row_id": r.get("_row_id"),
                "SupplierTitle": r.get("SupplierTitle", ""),
                "AmazonTitle": r.get("AmazonTitle", ""),
                "EAN": r.get("EAN", ""),
                "EAN_OnPage": r.get("EAN_OnPage", ""),
                "ASIN": r.get("ASIN", ""),
                "SupplierPrice_incVAT": r.get("SupplierPrice_incVAT"),
                "SellingPrice_incVAT": r.get("SellingPrice_incVAT"),
                "NetProfit": r.get("NetProfit"),
                "ROI": r.get("ROI"),
                "bought_in_past_month": r.get("bought_in_past_month"),
                "tier": r.get("tier"),
                "confidence_score": r.get("confidence_score"),
                "flags": r.get("flags", []),
                "reasons": r.get("reasons", []),
                "ean_exact_match": r.get("ean_exact_match"),
                "SupplierURL": r.get("SupplierURL", ""),
                "AmazonURL": r.get("AmazonURL", ""),
                "fba_seller_count": r.get("fba_seller_count"),
                "Category": r.get("Category", "Other"),
            })

        return {
            "rows": clean_rows,
            "tier_counts": tier_counts,
            "total_rows": total_rows,
            "filtered_count": len(clean_rows),
            "source_file": os.path.basename(csv_path),
            "effective_supplier": effective_supplier,
            "distinct_categories": distinct_categories,
        }

    except Exception as e:
        import traceback as tb
        return JSONResponse({"error": True, "message": str(e), "traceback": tb.format_exc()}, status_code=500)


@app.get("/api/reports/{supplier}")
def list_reports(supplier: str, lineage: str = "base"):
    """List available financial report CSVs for AI analysis."""
    base_dir = get_base_directory()
    try:
        effective_supplier = supplier
        if lineage == "latest_sandbox":
            loader = MetricsLoader(base_dir)
            latest = loader.discover_latest_sandbox_supplier(supplier)
            if latest:
                effective_supplier = latest
        loader = MetricsLoader(base_dir)
        paths = loader.resolve_paths(effective_supplier)
        fin_dir = paths.get("financial_dir")
        if not fin_dir or not os.path.exists(fin_dir):
            return JSONResponse({"reports": [], "error": "No financial reports directory"})
        csv_files = sorted(
            [f for f in os.listdir(fin_dir) if f.endswith(".csv")],
            key=lambda f: os.path.getmtime(os.path.join(fin_dir, f)), reverse=True
        )
        reports = []
        for f in csv_files:
            fp = os.path.join(fin_dir, f)
            row_count = 0
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as rf:
                    row_count = max(0, sum(1 for _ in rf) - 1)
            except Exception:
                pass
            reports.append({"filename": f, "path": fp, "rows": row_count,
                             "mtime": os.path.getmtime(fp)})
        return JSONResponse({"reports": reports, "fin_dir": fin_dir})
    except Exception as e:
        return JSONResponse({"reports": [], "error": str(e)})


@app.get("/api/categories/{supplier}")
def list_categories(supplier: str, lineage: str = "base"):
    """Return distinct categories derived from cached products source_url."""
    base_dir = get_base_directory()
    try:
        effective_supplier = supplier
        if lineage == "latest_sandbox":
            loader = MetricsLoader(base_dir)
            latest = loader.discover_latest_sandbox_supplier(supplier)
            if latest:
                effective_supplier = latest
        loader = MetricsLoader(base_dir)
        paths = loader.resolve_paths(effective_supplier)
        cp_path = paths.get("cached_products_file")
        if not cp_path or not os.path.exists(cp_path):
            return JSONResponse({"categories": []})
        cached = json.loads(Path(cp_path).read_text(encoding="utf-8"))
        cat_map = {}  # source_url -> {url, name, count}
        for item in (cached if isinstance(cached, list) else []):
            src = item.get("source_url", "")
            if not src:
                continue
            if src not in cat_map:
                parts = [p for p in src.split("/") if p and "." not in p and "http" not in p and len(p) > 2]
                name = parts[-1].replace("-", " ").title() if parts else "Other"
                cat_map[src] = {"url": src, "name": name, "count": 0}
            cat_map[src]["count"] += 1
        categories = sorted(cat_map.values(), key=lambda c: c["name"])
        return JSONResponse({"categories": categories})
    except Exception as e:
        return JSONResponse({"categories": [], "error": str(e)})


@app.post("/api/ai-analyze")
async def run_ai_analysis(request: Request):
    """Start an AI analysis job. Returns job_id for polling."""
    body = await request.json()
    csv_path = body.get("csv_path", "")
    from_row = body.get("from_row")
    to_row = body.get("to_row")
    batch_size = int(body.get("batch_size", 20))
    category_filter = (body.get("category_filter") or "").strip()
    supplier_hint = (body.get("supplier") or "").strip()

    if not csv_path or not os.path.exists(csv_path):
        return JSONResponse({"error": True, "message": f"CSV not found: {csv_path}"}, status_code=400)

    analyst_path = PARENT_DIR / "tools" / "fba_ai_analyst.py"
    if not analyst_path.exists():
        return JSONResponse({"error": True, "message": "tools/fba_ai_analyst.py not found"}, status_code=400)

    job_id = str(uuid4())[:8]
    _ai_jobs[job_id] = {"status": "running", "output": [], "error": None,
                        "started_at": time.time(), "csv_path": csv_path}

    def run_job():
        import subprocess, csv as csv_mod
        work_csv = csv_path
        tmp_path = None
        try:
            # Build set of product URLs belonging to the selected category (via cached products source_url)
            cat_product_urls = None
            if category_filter and supplier_hint:
                try:
                    _loader = MetricsLoader(str(PARENT_DIR))
                    _paths = _loader.resolve_paths(supplier_hint)
                    _cp = _paths.get("cached_products_file", "")
                    if _cp and os.path.exists(_cp):
                        _cached = json.loads(Path(_cp).read_text(encoding="utf-8"))
                        cat_product_urls = set()
                        for _item in (_cached if isinstance(_cached, list) else []):
                            if category_filter.lower() in _item.get("source_url", "").lower():
                                cat_product_urls.add(_item.get("url", "").rstrip("/"))
                        _ai_jobs[job_id]["output"].append(
                            f"Category filter: {len(cat_product_urls)} products match '{category_filter}'"
                        )
                except Exception as _ce:
                    _ai_jobs[job_id]["output"].append(f"Category lookup warning: {_ce}")

            if from_row or to_row or category_filter:
                rows = []
                with open(csv_path, "r", encoding="utf-8-sig", errors="replace") as f:
                    reader = csv_mod.DictReader(f)
                    for i, row in enumerate(reader, start=2):
                        if from_row and i < int(from_row) + 1:
                            continue
                        if to_row and i > int(to_row) + 1:
                            break
                        if category_filter:
                            row_url = (row.get("SupplierURL") or "").rstrip("/")
                            if cat_product_urls is not None:
                                # Use cached products mapping (accurate: matches by source_url)
                                if row_url not in cat_product_urls:
                                    continue
                            else:
                                # Fallback: substring match on SupplierURL
                                if category_filter.lower() not in row_url.lower():
                                    continue
                        rows.append(row)
                if not rows:
                    _ai_jobs[job_id]["status"] = "done"
                    _ai_jobs[job_id]["output"] = ["No rows matched the filters."]
                    return
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
                ) as tf:
                    tmp_path = tf.name
                    writer = csv_mod.DictWriter(tf, fieldnames=list(rows[0].keys()))
                    writer.writeheader()
                    writer.writerows(rows)
                work_csv = tmp_path
                _ai_jobs[job_id]["output"].append(f"Filtered to {len(rows)} rows")

            output_dir = str(PARENT_DIR / "OUTPUTS" / "CONTROL_PLANE" / "FINANCIAL_REPORTS")
            os.makedirs(output_dir, exist_ok=True)
            cmd = [sys.executable, str(analyst_path), work_csv,
                   "--batch-size", str(batch_size),
                   "--output-dir", output_dir]
            # Use opencode provider for analyst (separate from chat UI provider)
            analyst_env = os.environ.copy()
            analyst_env["ANALYST_LLM_PROVIDER"] = "opencode"
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                cwd=str(PARENT_DIR), env=analyst_env
            )
            _ai_jobs[job_id]["proc"] = proc
            for line in proc.stdout:
                _ai_jobs[job_id]["output"].append(line.rstrip())
                if _ai_jobs[job_id].get("cancelled"):
                    try: proc.kill()
                    except Exception: pass
                    break
            proc.wait()
            if _ai_jobs[job_id].get("cancelled"):
                _ai_jobs[job_id]["status"] = "error"
                _ai_jobs[job_id]["error"] = "Cancelled by user"
            else:
                _ai_jobs[job_id]["status"] = "done" if proc.returncode == 0 else "error"
        except Exception as ex:
            _ai_jobs[job_id]["status"] = "error"
            _ai_jobs[job_id]["error"] = str(ex)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    threading.Thread(target=run_job, daemon=True).start()
    return JSONResponse({"job_id": job_id})


@app.get("/api/ai-analyze/status/{job_id}")
def get_ai_analyze_status(job_id: str):
    """Poll AI analysis job status."""
    job = _ai_jobs.get(job_id)
    if not job:
        return JSONResponse({"error": True, "message": "Job not found"}, status_code=404)
    return JSONResponse({
        "job_id": job_id,
        "status": job["status"],
        "output": job["output"],
        "error": job.get("error"),
        "elapsed": round(time.time() - job["started_at"], 1),
    })


@app.post("/api/ai-analyze/cancel/{job_id}")
def cancel_ai_analysis(job_id: str):
    """Cancel a running AI analysis job."""
    job = _ai_jobs.get(job_id)
    if not job:
        return JSONResponse({"error": True, "message": "Job not found"}, status_code=404)
    job["cancelled"] = True
    proc = job.get("proc")
    if proc:
        try:
            proc.kill()
        except Exception:
            pass
    job["status"] = "error"
    job["error"] = "Cancelled by user"
    return JSONResponse({"ok": True, "job_id": job_id})


@app.get("/api/workflows")
def list_workflows():
    import json
    cfg_path = PARENT_DIR / "config" / "system_config.json"
    if not cfg_path.exists():
        return []
    try:
        cfg = json.load(open(cfg_path, "r", encoding="utf-8"))
        workflows = cfg.get("workflows", {})
        out = []
        for key, wf in workflows.items():
            supplier = str(wf.get("supplier_name") or "")
            out.append({"key": key, "supplier": supplier})
        out.sort(key=lambda t: t["key"])
        return out
    except Exception:
        return []

# ---- Chat API Endpoints ----

@app.post("/api/chat")
def chat_send(req: ChatRequest):
    """Run the agent loop for a user message. Returns trace steps and final answer or pending approval."""
    if not CHAT_AVAILABLE:
        return JSONResponse({"error": True, "message": "Chat modules not available. Check LLM provider env vars."}, status_code=503)

    base_dir = get_base_directory()
    repo_root = Path(base_dir)
    user_text = req.message.strip()

    if not user_text:
        return JSONResponse({"error": True, "message": "Empty message"}, status_code=400)

    # If there's a pending approval, tell the user
    if chat_state["pending_tool_call"] is not None:
        return JSONResponse({
            "type": "approval_pending",
            "message": "A pending action is waiting for your approval. Please approve or reject it before sending a new message.",
            "pending_tool": {
                "name": chat_state["pending_tool_call"].name,
                "params": chat_state["pending_tool_call"].params,
                "explanation": chat_state["pending_tool_call"].explanation,
                "expected_outputs": chat_state["pending_tool_call"].expected_outputs,
            }
        })

    try:
        ensure_llm_env()
    except Exception as e:
        return JSONResponse({"error": True, "message": f"LLM environment error: {e}"}, status_code=503)

    # Add user message to history
    chat_state["messages"].append({"role": "user", "content": user_text})
    chat_state["scratchpad"] = []
    chat_state["trace"] = []
    chat_state["tool_executions"] = []

    try:
        rag_info, rag_context = _compute_rag_info(user_text)
    except Exception:
        rag_info = {"meta": {}, "chunks": []}
        rag_context = ""

    def event_stream():
        import json as _json
        local_trace = []
        try:
            for step_num in range(MAX_AGENT_STEPS):
                step = agent_plan_step(
                    user_text,
                    repo_root,
                    chat_state["scratchpad"],
                    chat_state["messages"],
                    (rag_info, rag_context),
                    session_state=chat_state,
                )

                if step.kind == "final_answer":
                    chat_state["messages"].append({"role": "assistant", "content": step.text})
                    chat_state["trace"] = list(local_trace)
                    _archive_current_turn("final_answer", final_answer=step.text)
                    _clear_turn_buffers()
                    _persist_chat_session("final_answer")
                    yield "data: " + _json.dumps({"type": "final_answer", "text": step.text, "trace": local_trace}) + "\n\n"
                    return

                if step.kind == "approval_needed":
                    tc = step.tool_call
                    chat_state["pending_tool_call"] = tc
                    chat_state["pending_user_text"] = user_text
                    chat_state["pending_rag_info"] = rag_info
                    _persist_chat_session("approval_needed")
                    yield "data: " + _json.dumps({
                        "type": "approval_needed",
                        "trace": local_trace,
                        "pending_tool": {
                            "name": tc.name,
                            "params": tc.params,
                            "explanation": tc.explanation,
                            "expected_outputs": tc.expected_outputs,
                        }
                    }) + "\n\n"
                    return

                # State tracking for context injection
                if step.result and step.result.get("ok"):
                    if isinstance(step.result.get("run_id"), str) and step.result.get("run_id"):
                        chat_state["last_run_id"] = step.result["run_id"]
                    if isinstance(step.result.get("sandbox_supplier"), str):
                        chat_state["last_sandbox_supplier"] = step.result["sandbox_supplier"]
                    supplier_domain = step.tool_call.params.get("supplier_domain")
                    if isinstance(supplier_domain, str) and supplier_domain.strip():
                        chat_state["last_supplier_domain"] = supplier_domain.strip()
                    products_path = step.tool_call.params.get("products_path")
                    if isinstance(products_path, str) and products_path.strip():
                        chat_state["last_products_path"] = products_path.strip()
                    elif step.tool_call.name == "build_product_list_from_cached":
                        rel_path = step.result.get("rel_path")
                        if isinstance(rel_path, str) and rel_path.strip():
                            chat_state["last_products_path"] = rel_path.strip()

                # Yield trace step IMMEDIATELY as it completes (the key SSE behaviour)
                trace_entry = {
                    "step": step_num + 1,
                    "tool": step.tool_call.name if step.tool_call else "unknown",
                    "explanation": step.tool_call.explanation if step.tool_call else None,
                    "result": _safe_serialize(step.result) if step.result else None,
                }
                local_trace.append(trace_entry)
                chat_state["trace"] = list(local_trace)
                yield "data: " + _json.dumps({"type": "trace_update", "step": trace_entry}) + "\n\n"

                chat_state["scratchpad"].append({"role": "action", "tool": step.tool_call.name, "params": step.tool_call.params})
                chat_state["scratchpad"].append({"role": "observation", "result": step.result})

            # Step limit reached
            fallback_msg = "I reached the maximum number of reasoning steps. See the trace for what I found."
            chat_state["messages"].append({"role": "assistant", "content": fallback_msg})
            chat_state["trace"] = list(local_trace)
            _archive_current_turn("step_limit_final_answer", final_answer=fallback_msg)
            _clear_turn_buffers()
            _persist_chat_session("step_limit_final_answer")
            yield "data: " + _json.dumps({"type": "final_answer", "text": fallback_msg, "trace": local_trace}) + "\n\n"

        except Exception as e:
            _archive_current_turn(
                "agent_error",
                error_message=str(e),
                traceback=traceback.format_exc(),
            )
            _clear_turn_buffers()
            _persist_chat_session("agent_error")
            yield "data: " + _json.dumps({"type": "error", "message": f"Agent error: {str(e)}", "traceback": traceback.format_exc()}) + "\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")



@app.post("/api/chat/approve")
def chat_approve(req: ApproveRequest):
    """Approve or reject the pending write-tool action."""
    if not CHAT_AVAILABLE:
        return JSONResponse({"error": True, "message": "Chat modules not available."}, status_code=503)

    tc = chat_state["pending_tool_call"]
    if tc is None:
        return JSONResponse({"error": True, "message": "No pending action to approve."}, status_code=400)

    user_text = chat_state["pending_user_text"] or ""
    rag_info = chat_state["pending_rag_info"] or {}
    base_dir = get_base_directory()
    repo_root = Path(base_dir)

    if not req.approve:
        rejected_snapshot = _pending_tool_snapshot()
        pending_user_text = _safe_serialize(chat_state.get("pending_user_text"), depth=2)
        pending_rag_info = _safe_serialize(chat_state.get("pending_rag_info"), depth=4)
        # User rejected
        chat_state["messages"].append({"role": "assistant", "content": "Action cancelled by user."})
        _archive_current_turn(
            "approval_rejected",
            pending_tool_call=rejected_snapshot,
            pending_user_text=pending_user_text,
            pending_rag_info=pending_rag_info,
        )
        chat_state["pending_tool_call"] = None
        chat_state["pending_user_text"] = None
        chat_state["pending_rag_info"] = None
        _clear_turn_buffers()
        _persist_chat_session("approval_rejected")
        return {"type": "cancelled", "text": "Action cancelled by user."}

    # Execute the approved tool
    try:
        result = execute_tool_call(tc, repo_root)
        audit_tool_call(user_text, tc, result, rag_info)
        _record_tool_execution(tc, result)

        if result.get("ok"):
            if isinstance(result.get("run_id"), str) and result.get("run_id"):
                chat_state["last_run_id"] = result["run_id"]
            if isinstance(result.get("sandbox_supplier"), str):
                chat_state["last_sandbox_supplier"] = result["sandbox_supplier"]

            supplier_domain = tc.params.get("supplier_domain")
            if isinstance(supplier_domain, str) and supplier_domain.strip():
                chat_state["last_supplier_domain"] = supplier_domain.strip()

            products_path = tc.params.get("products_path")
            if isinstance(products_path, str) and products_path.strip():
                chat_state["last_products_path"] = products_path.strip()
            elif tc.name == "build_product_list_from_cached":
                rel_path = result.get("rel_path")
                if isinstance(rel_path, str) and rel_path.strip():
                    chat_state["last_products_path"] = rel_path.strip()


        chat_state["pending_tool_call"] = None
        chat_state["pending_user_text"] = None
        chat_state["pending_rag_info"] = None

        chat_state["messages"].append({
            "role": "assistant",
            "content": f"Action `{tc.name}` executed successfully.",
        })
        _archive_current_turn(
            "approval_executed",
            executed_tool=tc.name,
            executed_result=_safe_serialize(result, depth=4),
        )
        _clear_turn_buffers()
        _persist_chat_session("approval_executed")

        return {
            "type": "executed",
            "tool": tc.name,
            "result": _safe_serialize(result),
        }
    except Exception as e:
        return JSONResponse({
            "error": True,
            "message": f"Execution error: {str(e)}",
            "traceback": traceback.format_exc(),
        }, status_code=500)


@app.get("/api/chat/history")
def chat_history():
    """Return the current chat message history."""
    return {"messages": chat_state["messages"]}


@app.post("/api/chat/reset")
def chat_reset():
    """Clear all chat context to start a fresh session. Prevents token accumulation."""
    _archive_current_turn("chat_reset")
    _persist_chat_session("chat_reset")
    msg_count = len(chat_state["messages"])
    chat_state["messages"] = []
    chat_state["scratchpad"] = []
    chat_state["trace"] = []
    chat_state["tool_executions"] = []
    chat_state["turn_history"] = []
    chat_state["pending_tool_call"] = None
    chat_state["pending_user_text"] = None
    chat_state["pending_rag_info"] = None
    chat_state["last_run_id"] = None
    chat_state["last_products_path"] = None
    chat_state["last_supplier_domain"] = None
    chat_state["last_sandbox_supplier"] = None
    _begin_new_chat_session()
    return {"ok": True, "cleared_messages": msg_count}


def _safe_serialize(obj, depth=3):
    """Recursively make an object JSON-safe."""
    if depth <= 0:
        return "<truncated>"
    if obj is None or isinstance(obj, (bool, int, float)):
        return obj
    if isinstance(obj, str):
        return obj[:5000] if len(obj) > 5000 else obj
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, list):
        return [_safe_serialize(v, depth - 1) for v in obj[:50]]
    if isinstance(obj, dict):
        return {str(k): _safe_serialize(v, depth - 1) for k, v in list(obj.items())[:50]}
    return str(obj)[:2000]


def _record_tool_execution(tc, result: dict) -> None:
    chat_state["tool_executions"].append(
        {
            "tool": tc.name,
            "params": _safe_serialize(tc.params, depth=4),
            "expected_outputs": _safe_serialize(
                getattr(tc, "expected_outputs", None), depth=4
            ),
            "result": _safe_serialize(result, depth=4),
            "executed_at": _now_iso(),
        }
    )
    chat_state["tool_executions"] = chat_state["tool_executions"][-50:]


def _clear_turn_buffers() -> None:
    chat_state["scratchpad"] = []
    chat_state["trace"] = []
    chat_state["tool_executions"] = []


def _archive_current_turn(reason: str, **extra: Any) -> None:
    has_turn_data = bool(
        chat_state["scratchpad"]
        or chat_state["trace"]
        or chat_state["tool_executions"]
        or extra
    )
    if not has_turn_data:
        return

    chat_state["turn_history"].append(
        _safe_serialize(
            {
                "reason": reason,
                "archived_at": _now_iso(),
                "messages": chat_state["messages"][-3:],
                "scratchpad": chat_state["scratchpad"],
                "trace": chat_state["trace"],
                "tool_executions": chat_state["tool_executions"],
                **extra,
            },
            depth=6,
        )
    )
    chat_state["turn_history"] = chat_state["turn_history"][-50:]


def _pending_tool_snapshot() -> dict[str, Any] | None:
    tc = chat_state.get("pending_tool_call")
    if tc is None:
        return None
    return {
        "name": getattr(tc, "name", None),
        "params": _safe_serialize(getattr(tc, "params", None), depth=5),
        "explanation": getattr(tc, "explanation", None),
        "expected_outputs": _safe_serialize(getattr(tc, "expected_outputs", None), depth=5),
    }


def _has_persistable_session_data() -> bool:
    return bool(
        chat_state["messages"]
        or chat_state["scratchpad"]
        or chat_state["trace"]
        or chat_state["tool_executions"]
        or chat_state["turn_history"]
        or chat_state["pending_tool_call"]
        or chat_state["last_run_id"]
        or chat_state["last_products_path"]
        or chat_state["last_supplier_domain"]
        or chat_state["last_sandbox_supplier"]
    )


def _persist_chat_session(reason: str) -> None:
    if not _has_persistable_session_data():
        return

    payload = {
        "session_id": chat_state["session_id"],
        "session_started_at": chat_state["session_started_at"],
        "reason": reason,
        "messages": _safe_serialize(chat_state["messages"], depth=6),
        "scratchpad": _safe_serialize(chat_state["scratchpad"], depth=6),
        "trace": _safe_serialize(chat_state["trace"], depth=6),
        "tool_executions": _safe_serialize(chat_state["tool_executions"], depth=6),
        "turn_history": _safe_serialize(chat_state["turn_history"], depth=6),
        "pending_tool_call": _pending_tool_snapshot(),
        "pending_user_text": _safe_serialize(chat_state["pending_user_text"], depth=2),
        "pending_rag_info": _safe_serialize(chat_state["pending_rag_info"], depth=4),
        "last_run_id": chat_state["last_run_id"],
        "last_products_path": chat_state["last_products_path"],
        "last_supplier_domain": chat_state["last_supplier_domain"],
        "last_sandbox_supplier": chat_state["last_sandbox_supplier"],
    }

    try:
        write_session_transcript(chat_state["session_id"], payload)
    except Exception as e:
        print(f"Transcript persistence failed: {e}")


def _begin_new_chat_session() -> None:
    chat_state["session_id"] = _new_session_id()
    chat_state["session_started_at"] = _now_iso()
