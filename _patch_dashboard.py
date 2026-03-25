"""Patch script for dashboard_v2_redesign changes."""
import os, re, textwrap

BASE = r"c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"

# ============================================================
# 1. api.py — imports + _ai_jobs + log lineage fix + new endpoints
# ============================================================
api_path = os.path.join(BASE, "dashboard_v2_redesign", "api.py")
with open(api_path, "r", encoding="utf-8") as f:
    api = f.read()

# --- 1a: Add new imports + _ai_jobs ---
OLD_IMPORTS = (
    "import json\n"
    "import os\n"
    "import sys\n"
    "import traceback\n"
    "from datetime import datetime, timezone\n"
    "from pathlib import Path\n"
    "from uuid import uuid4\n"
    "from fastapi import FastAPI, HTTPException\n"
    "from fastapi.staticfiles import StaticFiles\n"
    "from fastapi.responses import FileResponse, JSONResponse, StreamingResponse\n"
    "from pydantic import BaseModel\n"
    "from typing import Any, Optional\n"
    "import pandas as pd"
)
NEW_IMPORTS = (
    "import json\n"
    "import os\n"
    "import sys\n"
    "import re\n"
    "import time\n"
    "import threading\n"
    "import traceback\n"
    "import tempfile\n"
    "from datetime import datetime, timezone\n"
    "from pathlib import Path\n"
    "from uuid import uuid4\n"
    "from fastapi import FastAPI, HTTPException, Request\n"
    "from fastapi.staticfiles import StaticFiles\n"
    "from fastapi.responses import FileResponse, JSONResponse, StreamingResponse\n"
    "from pydantic import BaseModel\n"
    "from typing import Any, Optional\n"
    "import pandas as pd\n"
    "\n"
    "# In-memory AI analysis job store\n"
    "_ai_jobs: dict = {}"
)
assert OLD_IMPORTS in api, "OLD_IMPORTS not found!"
api = api.replace(OLD_IMPORTS, NEW_IMPORTS, 1)
print("1a imports OK")

# --- 1b: Log lineage fix ---
OLD_LINEAGE = (
    '        metrics_data.setdefault("paths", {})["base_dir"] = base_dir\n'
    "        \n"
    "        # Load chart data"
)
NEW_LINEAGE = (
    '        metrics_data.setdefault("paths", {})["base_dir"] = base_dir\n'
    "\n"
    "        # Fix log lineage: ensure logs match requested lineage (base vs sandbox)\n"
    "        try:\n"
    '            logs_dir = str(Path(base_dir) / "logs" / "debug")\n'
    "            if os.path.exists(logs_dir):\n"
    '                norm = supplier.replace(".", "-").replace(" ", "-").lower()\n'
    '                all_logs = [f for f in os.listdir(logs_dir) if f.endswith(".log")]\n'
    '                if lineage == "base":\n'
    "                    matching = sorted(\n"
    '                        [f for f in all_logs if f"run_custom_{norm}" in f and "__sandbox__" not in f],\n'
    "                        key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True\n"
    "                    )\n"
    "                else:\n"
    '                    norm_eff = effective_supplier.replace(".", "-").replace(" ", "-").lower()\n'
    "                    matching = sorted(\n"
    '                        [f for f in all_logs if f"run_custom_{norm_eff}" in f],\n'
    "                        key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True\n"
    "                    )\n"
    "                if matching:\n"
    '                    with open(os.path.join(logs_dir, matching[0]), encoding="utf-8", errors="replace") as lf:\n'
    "                        lines = lf.readlines()[-200:]\n"
    '                    metrics_data["log_data"] = [[line.rstrip() for line in lines], matching[0]]\n'
    "                else:\n"
    '                    metrics_data["log_data"] = [[], None]\n'
    "        except Exception:\n"
    "            pass\n"
    "\n"
    "        # Load chart data"
)
assert OLD_LINEAGE in api, "OLD_LINEAGE not found!"
api = api.replace(OLD_LINEAGE, NEW_LINEAGE, 1)
print("1b lineage fix OK")

# --- 1c: New endpoints ---
NEW_ENDPOINTS = '''\
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


@app.post("/api/ai-analyze")
async def run_ai_analysis(request: Request):
    """Start an AI analysis job. Returns job_id for polling."""
    body = await request.json()
    csv_path = body.get("csv_path", "")
    from_row = body.get("from_row")
    to_row = body.get("to_row")
    batch_size = int(body.get("batch_size", 20))
    category_filter = (body.get("category_filter") or "").strip()

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
                            url = (row.get("SupplierURL") or row.get("CategoryURL") or "").lower()
                            if category_filter.lower() not in url:
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

            cmd = [sys.executable, str(analyst_path), work_csv, "--batch-size", str(batch_size)]
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", cwd=str(PARENT_DIR)
            )
            for line in proc.stdout:
                _ai_jobs[job_id]["output"].append(line.rstrip())
            proc.wait()
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


@app.get("/api/workflows")'''

assert '@app.get("/api/workflows")' in api, "workflows endpoint not found!"
api = api.replace('@app.get("/api/workflows")', NEW_ENDPOINTS, 1)
print("1c new endpoints OK")

with open(api_path, "w", encoding="utf-8") as f:
    f.write(api)
print("api.py saved OK")


# ============================================================
# 2. index.html — operator section replacement
# ============================================================
html_path = os.path.join(BASE, "dashboard_v2_redesign", "templates", "index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Rename nav item label
OLD_OP_NAV_LABEL = "Operator"
# Only change the nav-item text (inside the nav link), not the view heading
# Find the specific nav-item for operator
OLD_OP_NAV = '            data-target="operator" aria-current="false">\n'
assert OLD_OP_NAV in html, "Operator nav item not found"

# Replace the operator section
OLD_OPERATOR_SECTION = '''\
        <!-- ========== OPERATOR VIEW ========== -->
        <section id="view-operator" class="view">
          <header class="view-header">
            <div>
              <h1>Operator Control Plane</h1>
              <p class="view-subtitle">
                Workflow management and job deployment
              </p>
            </div>
          </header>
          <div class="grid-2 stagger-1">
            <div class="card">
              <div class="card-header">
                <h3>🚀 Trigger Workflow</h3>
              </div>
              <div class="card-body">
                <div class="input-group">
                  <label>Target Workflow</label
                  ><select id="workflowsDropdown" class="glass-input">
                    <option>Loading…</option>
                  </select>
                </div>
                <div class="form-row">
                  <div class="input-group">
                    <label>Max Products (Total)</label
                    ><input
                      type="number"
                      id="maxProducts"
                      class="glass-input"
                      value="50"
                    />
                  </div>
                  <div class="input-group">
                    <label>Max per Category</label
                    ><input
                      type="number"
                      id="maxProductsPerCat"
                      class="glass-input"
                      value="50"
                    />
                  </div>
                </div>
                <button class="btn-primary" id="launchWorkflowBtn">
                  Deploy Job
                </button>
              </div>
            </div>
            <div class="card">
              <div class="card-header">
                <h3>📡 Active Jobs</h3>
              </div>
              <div class="card-body">
                <p class="empty-state">
                  No active jobs to display. Deploy a workflow to begin.
                </p>
              </div>
            </div>
          </div>
        </section>'''

NEW_OPERATOR_SECTION = '''\
        <!-- ========== AI ANALYSIS AGENT VIEW ========== -->
        <section id="view-operator" class="view">
          <header class="view-header">
            <div>
              <h1>AI Analysis Agent</h1>
              <p class="view-subtitle">Run LLM-powered product analysis on financial reports</p>
            </div>
          </header>

          <!-- Config row -->
          <div class="grid-2 stagger-1" style="margin-bottom:1rem">
            <div class="card">
              <div class="card-header"><h3>Report &amp; Filters</h3></div>
              <div class="card-body" style="display:flex;flex-direction:column;gap:.75rem">
                <div class="input-group">
                  <label>Financial Report</label>
                  <select id="aiReportSelect" class="glass-input">
                    <option value="">— select supplier first —</option>
                  </select>
                </div>
                <div class="form-row">
                  <div class="input-group">
                    <label>From row</label>
                    <input type="number" id="aiFromRow" class="glass-input" placeholder="all" min="2"/>
                  </div>
                  <div class="input-group">
                    <label>To row</label>
                    <input type="number" id="aiToRow" class="glass-input" placeholder="all"/>
                  </div>
                </div>
                <div class="input-group">
                  <label>Category filter (URL keyword, optional)</label>
                  <input type="text" id="aiCategoryFilter" class="glass-input" placeholder="e.g. toys-wholesale"/>
                </div>
                <div class="input-group">
                  <label>Batch size</label>
                  <input type="number" id="aiBatchSize" class="glass-input" value="20" min="1" max="50"/>
                </div>
              </div>
            </div>

            <div class="card">
              <div class="card-header"><h3>Mode &amp; Trigger</h3></div>
              <div class="card-body" style="display:flex;flex-direction:column;gap:.75rem">
                <div class="input-group">
                  <label>Mode</label>
                  <select id="aiMode" class="glass-input">
                    <option value="manual">Manual — run on demand</option>
                    <option value="auto">Auto — every N new products</option>
                  </select>
                </div>
                <div class="input-group" id="aiAutoNGroup" style="display:none">
                  <label>Run every N products</label>
                  <input type="number" id="aiAutoN" class="glass-input" value="50" min="10"/>
                </div>
                <div id="aiJobStatus" style="font-family:var(--font-mono);font-size:.75rem;color:var(--text-muted);min-height:1.5rem"></div>
                <button class="btn-primary" id="aiRunBtn" onclick="window.runAiAnalysis()">
                  Run AI Analysis
                </button>
                <button class="btn-outline" id="aiStopBtn" onclick="window.stopAiAnalysis()" style="display:none">
                  Cancel
                </button>
              </div>
            </div>
          </div>

          <!-- Output log -->
          <div class="card stagger-2">
            <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
              <h3>Analysis Output</h3>
              <span id="aiOutputMeta" style="font-size:.75rem;color:var(--text-muted)"></span>
            </div>
            <div id="aiOutputLog" style="
              font-family:var(--font-mono);font-size:.75rem;color:var(--text-variant);
              background:var(--bg-surface-lowest);border-radius:var(--radius-md);
              padding:1rem;min-height:12rem;max-height:28rem;overflow-y:auto;
              white-space:pre-wrap;line-height:1.6
            ">Waiting for analysis run…</div>
          </div>
        </section>'''

assert OLD_OPERATOR_SECTION in html, "Operator section not found!"
html = html.replace(OLD_OPERATOR_SECTION, NEW_OPERATOR_SECTION, 1)
print("2 operator section replaced OK")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("index.html saved OK")


# ============================================================
# 3. app.js — replace loadWorkflows + add AI analysis logic
# ============================================================
js_path = os.path.join(BASE, "dashboard_v2_redesign", "static", "js", "app.js")
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

OLD_OPERATOR_JS = '''\
    // ===== OPERATOR LOGIC =====
    async function loadWorkflows() {
        const dd = document.getElementById('workflowsDropdown');
        try {
            const res = await fetch('/api/workflows');
            const wfs = await res.json();
            dd.innerHTML = wfs.map(w => `<option value="${w.key}">${w.key} (${w.supplier})</option>`).join('') || '<option>No workflows found</option>';
        } catch (e) { dd.innerHTML = '<option>Error loading</option>'; }
    }'''

NEW_OPERATOR_JS = '''\
    // ===== AI ANALYSIS AGENT LOGIC =====
    let _aiJobId = null;
    let _aiPollTimer = null;
    let _aiAutoInterval = null;

    // Load reports when supplier or lineage changes
    async function loadAiReports() {
        const supplier = supplierSelect.value;
        const lineage = lineageSelect ? lineageSelect.value : 'base';
        const sel = document.getElementById('aiReportSelect');
        if (!sel) return;
        sel.innerHTML = '<option value="">Loading…</option>';
        try {
            const res = await fetch(`/api/reports/${encodeURIComponent(supplier)}?lineage=${lineage}`);
            const data = await res.json();
            if (!data.reports || !data.reports.length) {
                sel.innerHTML = '<option value="">No reports found</option>';
            } else {
                sel.innerHTML = data.reports.map(r => {
                    const dt = new Date(r.mtime * 1000).toLocaleDateString();
                    return `<option value="${r.path}">${r.filename} (${r.rows} rows, ${dt})</option>`;
                }).join('');
            }
        } catch (e) { sel.innerHTML = '<option value="">Error loading reports</option>'; }
    }

    // Toggle auto N field
    const aiModeEl = document.getElementById('aiMode');
    if (aiModeEl) {
        aiModeEl.addEventListener('change', () => {
            const grp = document.getElementById('aiAutoNGroup');
            if (grp) grp.style.display = aiModeEl.value === 'auto' ? 'block' : 'none';
        });
    }

    window.runAiAnalysis = async function() {
        const csvPath = (document.getElementById('aiReportSelect') || {}).value || '';
        const fromRow = (document.getElementById('aiFromRow') || {}).value || null;
        const toRow = (document.getElementById('aiToRow') || {}).value || null;
        const batchSize = parseInt((document.getElementById('aiBatchSize') || {}).value || '20');
        const categoryFilter = (document.getElementById('aiCategoryFilter') || {}).value || '';
        const statusEl = document.getElementById('aiJobStatus');
        const outputEl = document.getElementById('aiOutputLog');
        const metaEl = document.getElementById('aiOutputMeta');
        const runBtn = document.getElementById('aiRunBtn');
        const stopBtn = document.getElementById('aiStopBtn');

        if (!csvPath) { if (statusEl) statusEl.textContent = 'Select a report first.'; return; }

        if (statusEl) statusEl.textContent = 'Starting job…';
        if (outputEl) outputEl.textContent = 'Submitting analysis request…';
        if (runBtn) runBtn.disabled = true;
        if (stopBtn) stopBtn.style.display = 'inline-flex';

        try {
            const res = await fetch('/api/ai-analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({csv_path: csvPath, from_row: fromRow ? parseInt(fromRow) : null,
                    to_row: toRow ? parseInt(toRow) : null, batch_size: batchSize,
                    category_filter: categoryFilter})
            });
            const data = await res.json();
            if (data.error) { if (statusEl) statusEl.textContent = data.message; if (runBtn) runBtn.disabled = false; return; }
            _aiJobId = data.job_id;
            if (statusEl) statusEl.textContent = `Job ${_aiJobId} running…`;
            _startAiPoll();
        } catch (e) {
            if (statusEl) statusEl.textContent = `Error: ${e.message}`;
            if (runBtn) runBtn.disabled = false;
            if (stopBtn) stopBtn.style.display = 'none';
        }
    };

    window.stopAiAnalysis = function() {
        if (_aiPollTimer) { clearInterval(_aiPollTimer); _aiPollTimer = null; }
        _aiJobId = null;
        const runBtn = document.getElementById('aiRunBtn');
        const stopBtn = document.getElementById('aiStopBtn');
        const statusEl = document.getElementById('aiJobStatus');
        if (runBtn) runBtn.disabled = false;
        if (stopBtn) stopBtn.style.display = 'none';
        if (statusEl) statusEl.textContent = 'Cancelled.';
    };

    function _startAiPoll() {
        if (_aiPollTimer) clearInterval(_aiPollTimer);
        _aiPollTimer = setInterval(async () => {
            if (!_aiJobId) { clearInterval(_aiPollTimer); return; }
            try {
                const res = await fetch(`/api/ai-analyze/status/${_aiJobId}`);
                const job = await res.json();
                const outputEl = document.getElementById('aiOutputLog');
                const statusEl = document.getElementById('aiJobStatus');
                const metaEl = document.getElementById('aiOutputMeta');
                const runBtn = document.getElementById('aiRunBtn');
                const stopBtn = document.getElementById('aiStopBtn');

                if (outputEl) outputEl.textContent = (job.output || []).join('\\n') || 'Running…';
                if (outputEl) outputEl.scrollTop = outputEl.scrollHeight;
                if (metaEl) metaEl.textContent = `${job.elapsed}s elapsed`;

                if (job.status === 'done' || job.status === 'error') {
                    clearInterval(_aiPollTimer);
                    _aiPollTimer = null;
                    _aiJobId = null;
                    if (statusEl) statusEl.textContent = job.status === 'done' ? '✓ Analysis complete' : `✗ Error: ${job.error || 'unknown'}`;
                    if (runBtn) runBtn.disabled = false;
                    if (stopBtn) stopBtn.style.display = 'none';
                } else {
                    if (statusEl) statusEl.textContent = `Running… (${job.elapsed}s)`;
                }
            } catch (e) {
                clearInterval(_aiPollTimer);
                _aiPollTimer = null;
            }
        }, 2000);
    }'''

assert OLD_OPERATOR_JS in js, "Operator JS block not found!"
js = js.replace(OLD_OPERATOR_JS, NEW_OPERATOR_JS, 1)
print("3a operator JS replaced OK")

# Update init: replace loadWorkflows() with loadAiReports()
OLD_INIT = "    fetchMetrics();\n    loadWorkflows();\n    setupRefresh();"
NEW_INIT = "    fetchMetrics();\n    loadAiReports();\n    setupRefresh();"
assert OLD_INIT in js, "Init block not found!"
js = js.replace(OLD_INIT, NEW_INIT, 1)
print("3b init updated OK")

# Also call loadAiReports when supplier/lineage changes
OLD_LISTENERS = ("    supplierSelect.addEventListener('change', () => { prevMatches = null; fetchMetrics(); });\n"
                 "    if (lineageSelect) {\n"
                 "        lineageSelect.addEventListener('change', () => { prevMatches = null; fetchMetrics(); });\n"
                 "    }")
NEW_LISTENERS = ("    supplierSelect.addEventListener('change', () => { prevMatches = null; fetchMetrics(); loadAiReports(); });\n"
                 "    if (lineageSelect) {\n"
                 "        lineageSelect.addEventListener('change', () => { prevMatches = null; fetchMetrics(); loadAiReports(); });\n"
                 "    }")
assert OLD_LISTENERS in js, "Listeners block not found!"
js = js.replace(OLD_LISTENERS, NEW_LISTENERS, 1)
print("3c listeners updated OK")

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)
print("app.js saved OK")

print("\nAll patches applied successfully.")
