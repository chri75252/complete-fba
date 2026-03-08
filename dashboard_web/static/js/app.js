document.addEventListener('DOMContentLoaded', () => {

    // ===== NAVIGATION =====
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');

    navItems.forEach(item => {
        item.addEventListener('click', e => {
            e.preventDefault();
            navItems.forEach(n => n.classList.remove('active'));
            views.forEach(v => v.classList.remove('active'));
            item.classList.add('active');
            document.getElementById(`view-${item.dataset.target}`).classList.add('active');
        });
    });

    // ===== GLOBALS =====
    const supplierSelect = document.getElementById('supplierSelect');
    const refreshSelect = document.getElementById('refreshInterval');
    const statusBadge = document.getElementById('connectionStatus');
    let charts = {};
    let prevMatches = null;
    let refreshTimer = null;
    let lastExtractedCount = null;
    let lastExtractTime = null;

    // 1. Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.shiftKey && e.key.toLowerCase() === 'r') {
            e.preventDefault();
            if (typeof window.fetchMetrics === 'function') {
                window.fetchMetrics();
            }
        }
    });

    // Chart.js global defaults for dark theme
    Chart.defaults.color = '#a3a3a3';
    Chart.defaults.borderColor = 'rgba(255,255,255,0.08)';
    Chart.defaults.font.family = "'Manrope', sans-serif";
    Chart.defaults.plugins.legend.labels.boxWidth = 12;

    const CHART_COLORS = ['#e2fd52', '#00e5ff', '#ff0055', '#ffb800', '#00ff66', '#9d00ff'];

    // ===== FETCH METRICS =====
    async function fetchMetrics() {
        const supplier = supplierSelect.value;
        statusBadge.innerHTML = '<span class="status-dot"></span> Fetching…';
        statusBadge.className = 'status-badge connecting';

        try {
            const res = await fetch(`/api/metrics/${supplier}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            if (data.error) {
                statusBadge.innerHTML = '<span class="status-dot"></span> Data Issues';
                statusBadge.className = 'status-badge connecting';
                document.getElementById('tickerText').textContent = `⚠️ Issues: ${(data.issues || []).join(', ')}`;
                return;
            }

            renderDashboard(data);

            statusBadge.innerHTML = '<span class="status-dot"></span> Connected';
            statusBadge.className = 'status-badge connected';
            document.getElementById('lastUpdated').textContent = `Updated ${new Date().toLocaleTimeString()}`;
            document.getElementById('sidebarSupplier').textContent = `Supplier: ${supplier}`;
            if (data.paths && data.paths.base_dir) {
                document.getElementById('sidebarBaseDir').textContent = `Base: ${data.paths.base_dir}`;
            }

        } catch (err) {
            console.error(err);
            statusBadge.innerHTML = '<span class="status-dot"></span> Disconnected';
            statusBadge.className = 'status-badge connecting';
        }
    }

    // Make globally accessible for inline onclick
    window.fetchMetrics = fetchMetrics;

    // ===== RENDER DASHBOARD =====
    function renderDashboard(data) {
        const s = (obj, key, def = 0) => (obj && obj[key] !== undefined && obj[key] !== null) ? obj[key] : def;
        const fmt = n => (typeof n === 'number') ? n.toLocaleString() : String(n);

        const sm = data.state_metrics || {};
        const lm = data.linking_metrics || {};
        const fm = data.financial_metrics || {};

        // --- Live Ticker ---
        const nowMatches = s(lm, 'total_matches');
        let delta = 0;
        if (prevMatches !== null) delta = nowMatches - prevMatches;
        prevMatches = nowMatches;
        document.getElementById('tickerText').textContent =
            `Live — Matches: ${fmt(nowMatches)} (${delta >= 0 ? '+' : ''}${delta}) · Phase: ${s(sm, 'processing_status', 'Unknown')} · Profitable: ${fmt(s(fm, 'count_profitable'))}`;

        // Velocity Tracking
        const currentExtracted = s(sm, 'total_products', 0);
        const now = Date.now();
        if (lastExtractedCount !== null && lastExtractTime !== null) {
            const timeDiffMins = (now - lastExtractTime) / 60000;
            if (timeDiffMins > 0) {
                const rowsPolled = currentExtracted - lastExtractedCount;
                const velocity = Math.max(0, Math.round(rowsPolled / timeDiffMins));
                const velEl = document.getElementById('scrapeVelocity');
                if (velEl) velEl.textContent = `${velocity} rows/min`;
            }
        }
        lastExtractedCount = currentExtracted;
        lastExtractTime = now;

        // --- Metric Cards ---
        document.getElementById('totalExtracted').textContent = fmt(s(sm, 'total_products'));
        document.getElementById('totalProcessed').textContent = fmt(s(lm, 'total_matches'));
        document.getElementById('profitableProducts').textContent = fmt(s(fm, 'count_profitable'));
        const avgRoi = s(fm, 'avg_roi');
        document.getElementById('avgROI').textContent = avgRoi ? `${Number(avgRoi).toFixed(1)}%` : '--%';
        document.getElementById('filesScanned').textContent = fmt(s(fm, 'files_scanned'));
        const tp = s(fm, 'total_profit');
        document.getElementById('totalProfit').textContent = tp > 0 ? `£${Number(tp).toLocaleString('en-GB', { minimumFractionDigits: 2 })}` : '£0.00';

        // --- System Health ---
        document.getElementById('systemPhase').textContent = s(sm, 'processing_status', 'Unknown');
        document.getElementById('catIndex').textContent = `${s(sm, 'persistent_category_index')} / ${s(sm, 'total_categories')}`;
        const catUrl = s(sm, 'current_category_url', '—');
        let shortCat = '—';
        if (catUrl && catUrl !== '—') {
            const parts = catUrl.split('://').pop();
            shortCat = parts.includes('/') ? parts.split('/').slice(1).join('/') : parts;
        }
        document.getElementById('currentCatUrl').textContent = shortCat;

        const cp = sm.category_progress || {};
        document.getElementById('supplierProgress').textContent = `${fmt(s(cp, 'supplier_products_completed'))} / ${fmt(s(cp, 'supplier_products_needing_extraction'))}`;
        document.getElementById('amazonProgress').textContent = `${fmt(s(cp, 'amazon_products_completed'))} / ${fmt(s(cp, 'amazon_products_needing_analysis'))}`;
        document.getElementById('freshStarts').textContent = fmt(s(sm, 'fresh_starts'));
        document.getElementById('totalRows').textContent = fmt(s(fm, 'rows_total'));

        // --- Matching Performance ---
        document.getElementById('totalMatches').textContent = fmt(s(lm, 'total_matches'));
        const hcr = s(lm, 'high_confidence_rate');
        document.getElementById('highConfidence').textContent = hcr ? `${Number(hcr).toFixed(1)}%` : '--%';
        document.getElementById('noEanCount').textContent = fmt(s(lm, 'no_ean_count'));

        const methods = lm.match_method_counts || {};
        const topMethod = Object.entries(methods).sort((a, b) => b[1] - a[1])[0];
        document.getElementById('primaryMethod').textContent = topMethod ? topMethod[0].charAt(0).toUpperCase() + topMethod[0].slice(1) : '—';

        // Match success rate
        const tExtracted = s(sm, 'total_products', 0);
        if (tExtracted > 0) {
            const successRate = ((nowMatches / tExtracted) * 100).toFixed(1);
            const msEl = document.getElementById('matchSuccessRate');
            if (msEl) msEl.textContent = `${successRate}%`;
        }

        // Confidence Distribution
        const confCounts = lm.confidence_counts || {};
        const confBars = document.getElementById('confBars');
        if (Object.keys(confCounts).length > 0) {
            confBars.innerHTML = Object.entries(confCounts).map(([k, v]) =>
                `<div class="conf-chip"><span class="conf-chip-label">${k}</span><span class="conf-chip-val">${fmt(v)}</span></div>`
            ).join('');
        } else {
            confBars.innerHTML = '<span class="conf-empty">No data</span>';
        }

        // --- Charts ---
        const chartData = data.chart_data || [];
        if (chartData.length > 0) {
            renderAllCharts(chartData);
            renderTables(chartData);
        }

        // --- Logs ---
        const logData = data.log_data || [];
        if (logData[0] && logData[0].length > 0) {
            const lines = logData[0].slice(-50);
            document.getElementById('logTail').innerHTML = lines.map(l => escapeHtml(l)).join('<br>');
            const logPanel = document.querySelector('.log-trace');
            logPanel.scrollTop = logPanel.scrollHeight;
        }
        if (logData[1]) {
            document.getElementById('logFilename').textContent = logData[1];
        }
    }

    // ===== ALL CHARTS =====
    function renderAllCharts(data) {
        renderProfitChart(data);
        renderRoiHistogram(data);
        renderPriceRatioHistogram(data);
        renderMatchQualityChart(data);
        renderSellerMixChart(data);
    }

    function destroyChart(key) {
        if (charts[key]) { charts[key].destroy(); charts[key] = null; }
    }

    function renderProfitChart(data) {
        destroyChart('profit');
        const ctx = document.getElementById('profitChart').getContext('2d');
        const pts = data.filter(d => d.SellingPrice_incVAT && d.NetProfit).map(d => ({
            x: d.SellingPrice_incVAT, y: d.NetProfit, label: d.SupplierTitle
        }));

        const pointBackgroundColors = data.filter(d => d.SellingPrice_incVAT && d.NetProfit).map(d => {
            if (d.ROI >= 0.3) return '#00ff66'; // Green > 30%
            if (d.ROI >= 0.15) return '#ffb800'; // Yellow 15-30%
            return '#ff3333'; // Red < 15%
        });

        charts.profit = new Chart(ctx, {
            type: 'scatter',
            data: { datasets: [{ label: 'Products', data: pts, backgroundColor: pointBackgroundColors, borderColor: 'rgba(255,255,255,0.1)', pointRadius: 4, pointHoverRadius: 6 }] },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => [`${c.raw.label || ''}`, `Sell: £${c.raw.x.toFixed(2)}, Profit: £${c.raw.y.toFixed(2)}`] } } },
                scales: { x: { title: { display: true, text: 'Selling Price (£)' } }, y: { title: { display: true, text: 'Net Profit (£)' } } }
            }
        });
    }

    function renderRoiHistogram(data) {
        destroyChart('roi');
        const ctx = document.getElementById('roiHistChart').getContext('2d');
        const rois = data.map(d => d.ROI).filter(r => r != null && isFinite(r));
        if (rois.length === 0) return;

        const min = Math.floor(Math.min(...rois));
        const max = Math.ceil(Math.max(...rois));
        const binCount = 30;
        const binSize = Math.max((max - min) / binCount, 1);
        const bins = Array(binCount).fill(0);
        const labels = [];

        for (let i = 0; i < binCount; i++) {
            const lo = min + i * binSize;
            labels.push(`${lo.toFixed(0)}%`);
        }
        rois.forEach(r => {
            const idx = Math.min(Math.floor((r - min) / binSize), binCount - 1);
            if (idx >= 0) bins[idx]++;
        });

        charts.roi = new Chart(ctx, {
            type: 'bar',
            data: { labels, datasets: [{ label: 'Count', data: bins, backgroundColor: 'rgba(168,85,247,0.5)', borderColor: '#a855f7', borderWidth: 1 }] },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { title: { display: true, text: 'ROI (%)' }, ticks: { maxTicksLimit: 10 } }, y: { title: { display: true, text: 'Count' } } }
            }
        });
    }

    function renderPriceRatioHistogram(data) {
        destroyChart('priceRatio');
        const ctx = document.getElementById('priceRatioChart').getContext('2d');
        const ratios = data.filter(d => d.SupplierPrice_incVAT > 0 && d.SellingPrice_incVAT).map(d => d.SellingPrice_incVAT / d.SupplierPrice_incVAT).filter(r => isFinite(r));
        if (ratios.length === 0) return;

        const min = Math.floor(Math.min(...ratios) * 10) / 10;
        const max = Math.ceil(Math.max(...ratios) * 10) / 10;
        const binCount = 25;
        const binSize = Math.max((max - min) / binCount, 0.1);
        const bins = Array(binCount).fill(0);
        const labels = [];

        for (let i = 0; i < binCount; i++) labels.push(`${(min + i * binSize).toFixed(1)}x`);
        ratios.forEach(r => {
            const idx = Math.min(Math.floor((r - min) / binSize), binCount - 1);
            if (idx >= 0) bins[idx]++;
        });

        charts.priceRatio = new Chart(ctx, {
            type: 'bar',
            data: { labels, datasets: [{ label: 'Count', data: bins, backgroundColor: 'rgba(236,72,153,0.5)', borderColor: '#ec4899', borderWidth: 1 }] },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { title: { display: true, text: 'Price Ratio (x)' }, ticks: { maxTicksLimit: 10 } }, y: { title: { display: true, text: 'Count' } } }
            }
        });
    }

    function renderMatchQualityChart(data) {
        destroyChart('matchQuality');
        const ctx = document.getElementById('matchQualityChart').getContext('2d');
        const counts = {};
        data.forEach(d => { const q = d.MatchQuality || 'Unknown'; counts[q] = (counts[q] || 0) + 1; });
        const labels = Object.keys(counts);
        const values = Object.values(counts);
        if (labels.length === 0) return;

        charts.matchQuality = new Chart(ctx, {
            type: 'bar',
            data: { labels, datasets: [{ label: 'Count', data: values, backgroundColor: labels.map((_, i) => CHART_COLORS[i % CHART_COLORS.length] + '88'), borderColor: labels.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]), borderWidth: 1 }] },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { title: { display: true, text: 'Match Quality' } }, y: { title: { display: true, text: 'Count' } } }
            }
        });
    }

    function renderSellerMixChart(data) {
        destroyChart('sellerMix');
        const ctx = document.getElementById('sellerMixChart').getContext('2d');
        let fbaTotal = 0, fbmTotal = 0;
        data.forEach(d => {
            if (d.fba_seller_count) fbaTotal += Number(d.fba_seller_count) || 0;
            if (d.fbm_seller_count) fbmTotal += Number(d.fbm_seller_count) || 0;
        });
        if (fbaTotal === 0 && fbmTotal === 0) return;

        charts.sellerMix = new Chart(ctx, {
            type: 'doughnut',
            data: { labels: ['FBA Sellers', 'FBM Sellers'], datasets: [{ data: [fbaTotal, fbmTotal], backgroundColor: ['rgba(99,102,241,0.7)', 'rgba(249,115,22,0.7)'], borderColor: ['#6366f1', '#f97316'], borderWidth: 2 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } }
        });
    }

    function escapeHtml(str) { const d = document.createElement('div'); d.textContent = str; return d.innerHTML; }

    function renderTables(data) {
        function truncate(str, n) {
            if (!str) return '';
            return (str.length > n) ? str.substr(0, n - 1) + '...' : str;
        }

        // 1. Render Top 5 Products by Profit
        const topProducts = [...data]
            .filter(item => item.NetProfit > 0)
            .sort((a, b) => b.NetProfit - a.NetProfit)
            .slice(0, 5);

        const topBody = document.getElementById('topProductsTableBody');
        if (topBody) {
            topBody.innerHTML = topProducts.map(item => `
                <tr>
                    <td title="${escapeHtml(item.SupplierTitle || '')}">${escapeHtml(truncate(item.SupplierTitle, 25))}</td>
                    <td title="${escapeHtml(item.AmazonTitle || '')}">${escapeHtml(truncate(item.AmazonTitle, 25))}</td>
                    <td class="accent-val">${(item.ROI * 100).toFixed(1)}%</td>
                    <td class="success-text">£${(item.NetProfit || 0).toFixed(2)}</td>
                </tr>
            `).join('') || '<tr><td colspan="4" class="empty-state">No profitable products found yet.</td></tr>';
        }

        // 2. Render Fuzzy Matches (Review Table)
        const fuzzyMatches = [...data]
            .filter(item => item.MatchQuality && !item.MatchQuality.includes('Exact') && !item.MatchQuality.includes('High'))
            .slice(0, 5);

        const fuzzyBody = document.getElementById('fuzzyMatchTableBody');
        if (fuzzyBody) {
            fuzzyBody.innerHTML = fuzzyMatches.map(item => `
                <tr>
                    <td title="${escapeHtml(item.SupplierTitle || '')}">${escapeHtml(truncate(item.SupplierTitle, 30))}</td>
                    <td title="${escapeHtml(item.AmazonTitle || '')}">${escapeHtml(truncate(item.AmazonTitle, 30))}</td>
                    <td><span class="badge warn-text">${item.MatchQuality || 'Unknown'}</span></td>
                </tr>
            `).join('') || '<tr><td colspan="3" class="empty-state">No fuzzy matches to review!</td></tr>';
        }
    }

    // ===== CHAT LOGIC =====
    const chatInput = document.getElementById('chatInput');
    const chatHistory = document.getElementById('chatHistory');
    const sendBtn = document.getElementById('chatSendBtn');

    function addChatBubble(role, content) {
        const div = document.createElement('div');
        div.className = `chat-message ${role}`;
        div.innerHTML = `<div class="avatar">${role === 'user' ? '👤' : '🤖'}</div><div class="msg-bubble">${content}</div>`;
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function addThinking() {
        const div = document.createElement('div');
        div.className = 'chat-message assistant';
        div.id = 'thinking-indicator';
        div.innerHTML = '<div class="avatar">🤖</div><div class="msg-bubble thinking-bubble"><span class="thinking-dots">Thinking<span>.</span><span>.</span><span>.</span></span></div>';
        chatHistory.appendChild(div);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function removeThinking() { const el = document.getElementById('thinking-indicator'); if (el) el.remove(); }

    function renderTrace(trace) {
        if (!trace || trace.length === 0) return '';
        return '<div class="trace-container">' + trace.map(s =>
            `<div class="trace-step"><span class="trace-label">STEP ${s.step} ⚡ ${(s.tool || '').toUpperCase()}</span>` +
            (s.explanation ? `<p class="trace-explanation">${s.explanation}</p>` : '') +
            (s.result ? `<details class="trace-result-details"><summary>Tool Output</summary><pre class="trace-result">${escapeHtml(typeof s.result === 'string' ? s.result : JSON.stringify(s.result, null, 2))}</pre></details>` : '') +
            '</div>'
        ).join('') + '</div>';
    }

    function renderApproval(tool) {
        const p = JSON.stringify(tool.params, null, 2);
        let html = `<div class="approval-card"><h4>⚠️ Action Requires Approval</h4><div class="approval-tool-name">${tool.name}</div>`;
        if (tool.explanation) html += `<p class="approval-explanation">${tool.explanation}</p>`;
        html += `<pre class="approval-params">${escapeHtml(p)}</pre>`;
        if (tool.expected_outputs && tool.expected_outputs.length) {
            html += '<p><strong>Expected outputs:</strong></p><ul>' + tool.expected_outputs.map(o => `<li><code>${escapeHtml(String(o))}</code></li>`).join('') + '</ul>';
        }
        html += '<div class="approval-actions"><button class="btn-approve" onclick="handleApprove(true)">✅ Approve</button><button class="btn-reject" onclick="handleApprove(false)">❌ Reject</button></div></div>';
        return html;
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;
        addChatBubble('user', escapeHtml(text));
        chatInput.value = '';
        chatInput.disabled = true;
        sendBtn.disabled = true;
        addThinking();
        try {
            const res = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: text, supplier: supplierSelect.value }) });
            const data = await res.json();
            removeThinking();
            if (data.error) {
                addChatBubble('assistant', `<div class="error-block"><strong>⚠️ Error:</strong> ${escapeHtml(data.message || 'Unknown error')}</div>` + (data.trace ? renderTrace(data.trace) : ''));
            } else if (data.type === 'final_answer') {
                addChatBubble('assistant', renderTrace(data.trace) + `<div class="final-answer">${escapeHtml(data.text)}</div>`);
            } else if (data.type === 'approval_needed') {
                addChatBubble('assistant', renderTrace(data.trace) + renderApproval(data.pending_tool));
            } else if (data.type === 'approval_pending') {
                addChatBubble('assistant', `<div class="error-block">⚠️ ${escapeHtml(data.message)}</div>`);
            }
        } catch (err) {
            removeThinking();
            addChatBubble('assistant', `<div class="error-block"><strong>⚠️ Network Error:</strong> ${escapeHtml(err.message)}</div>`);
        } finally {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    }

    window.handleApprove = async function (approve) {
        document.querySelectorAll('.btn-approve, .btn-reject').forEach(b => b.disabled = true);
        addThinking();
        try {
            const res = await fetch('/api/chat/approve', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ approve }) });
            const data = await res.json();
            removeThinking();
            if (data.error) { addChatBubble('assistant', `<div class="error-block"><strong>⚠️ Error:</strong> ${escapeHtml(data.message)}</div>`); }
            else if (data.type === 'cancelled') { addChatBubble('assistant', `<em>${escapeHtml(data.text)}</em>`); }
            else if (data.type === 'executed') {
                let c = `<div class="success-block">✅ <strong>${escapeHtml(data.tool)}</strong> executed successfully.</div>`;
                if (data.result) c += `<details class="trace-result-details"><summary>Result</summary><pre class="trace-result">${escapeHtml(typeof data.result === 'string' ? data.result : JSON.stringify(data.result, null, 2))}</pre></details>`;
                addChatBubble('assistant', c);
            }
        } catch (err) { removeThinking(); addChatBubble('assistant', `<div class="error-block"><strong>⚠️ Network Error:</strong> ${escapeHtml(err.message)}</div>`); }
    };

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } });

    // ===== OPERATOR LOGIC =====
    async function loadWorkflows() {
        const dd = document.getElementById('workflowsDropdown');
        try {
            const res = await fetch('/api/workflows');
            const wfs = await res.json();
            dd.innerHTML = wfs.map(w => `<option value="${w.key}">${w.key} (${w.supplier})</option>`).join('') || '<option>No workflows found</option>';
        } catch (e) { dd.innerHTML = '<option>Error loading</option>'; }
    }

    // ===== AUTO-REFRESH =====
    function setupRefresh() {
        if (refreshTimer) clearInterval(refreshTimer);
        const secs = parseInt(refreshSelect.value);
        if (secs > 0) refreshTimer = setInterval(fetchMetrics, secs * 1000);
    }

    refreshSelect.addEventListener('change', setupRefresh);
    supplierSelect.addEventListener('change', () => { prevMatches = null; fetchMetrics(); });

    // ===== INIT =====
    fetchMetrics();
    loadWorkflows();
    setupRefresh();
});
