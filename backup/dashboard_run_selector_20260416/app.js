document.addEventListener('DOMContentLoaded', () => {

    // ===== NAVIGATION =====
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');

    navItems.forEach(item => {
        item.addEventListener('click', e => {
            e.preventDefault();
            navItems.forEach(n => {
                n.classList.remove('active');
                n.setAttribute('aria-current', 'false');
            });
            views.forEach(v => v.classList.remove('active'));
            item.classList.add('active');
            item.setAttribute('aria-current', 'page');
            document.getElementById(`view-${item.dataset.target}`).classList.add('active');
        });
    });

// ===== GLOBALS =====
    const supplierSelect = document.getElementById('supplierSelect');
    const refreshSelect = document.getElementById('refreshInterval');
    const lineageSelect = document.getElementById('lineageSelect');
    const salesFieldToggle = document.getElementById('salesFieldToggle');
    const statusBadge = document.getElementById('connectionStatus');
    let charts = {};
    let prevMatches = null;
    let refreshTimer = null;
    let lastExtractedCount = null;
    let lastExtractTime = null;
    let _lastChartData = [];
    let _catProfitSorted = [];
    let _catSalesSorted = [];
    // Request sequencing: abort stale in-flight fetches so only the latest response is rendered
    let _metricsAbortCtrl = null;
    let _analysisAbortCtrl = null;
    let _reportsAbortCtrl = null;

    function getSelectedSalesField() {
        return salesFieldToggle && salesFieldToggle.checked
            ? 'amazon_sales_badge'
            : 'bought_in_past_month';
    }

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
    Chart.defaults.color = '#908fa0';
    Chart.defaults.borderColor = 'rgba(70, 69, 84, 0.15)';
    Chart.defaults.font.family = "'Manrope', sans-serif";
    Chart.defaults.plugins.legend.labels.boxWidth = 12;

    const CHART_COLORS = ['#c0c1ff', '#4edea3', '#ffb95f', '#ffb4ab', '#8083ff', '#00a572'];

// ===== FETCH METRICS =====
    async function fetchMetrics(forceRefresh = false) {
        const supplier = supplierSelect.value;
        const lineage = lineageSelect ? lineageSelect.value : 'base';
        statusBadge.innerHTML = '<span class="status-dot"></span> Fetching…';
        statusBadge.className = 'status-badge connecting';

        if (_metricsAbortCtrl) _metricsAbortCtrl.abort();
        _metricsAbortCtrl = new AbortController();

        try {
            const dashReport = document.getElementById('dashboardReportSelect');
            const reportParam = dashReport ? dashReport.value : '';
            const salesField = getSelectedSalesField();
            const forceParam = forceRefresh ? '&force_refresh=1' : '';
            const res = await fetch(`/api/metrics/${supplier}?lineage=${encodeURIComponent(lineage)}&report=${encodeURIComponent(reportParam)}&sales_field=${encodeURIComponent(salesField)}${forceParam}`, { signal: _metricsAbortCtrl.signal });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            if (data.error) {
                statusBadge.innerHTML = '<span class="status-dot"></span> Data Issues';
                statusBadge.className = 'status-badge connecting';
                document.getElementById('tickerText').textContent = `⚠️ Issues: ${(data.issues || []).join(', ')}`;
                return;
            }

            renderDashboard(data);

            // Populate data sources panel
const ds = data.data_sources;
            const dsEl = (id) => document.getElementById(id);
            if (dsEl('dsCachedProducts') && ds) {
                dsEl('dsCachedProducts').textContent = ds.cached_products || '\u2014';
                dsEl('dsLinkingMap').textContent = ds.linking_map || '\u2014';
                dsEl('dsFinancialReport').textContent = ds.financial_report || '\u2014';
                dsEl('dsProcessingState').textContent = ds.processing_state || '\u2014';
                dsEl('dsLogFile').textContent = ds.log_file || '\u2014';
            }

            statusBadge.innerHTML = '<span class="status-dot"></span> Connected';
            statusBadge.className = 'status-badge connected';
            document.getElementById('lastUpdated').textContent = `Updated ${new Date().toLocaleTimeString()}`;
            const effectiveSupplier = (data.meta && data.meta.effective_supplier)
                ? data.meta.effective_supplier
                : supplier;
            document.getElementById('sidebarSupplier').textContent = `Supplier: ${effectiveSupplier}`;
            if (data.paths && data.paths.base_dir) {
                document.getElementById('sidebarBaseDir').textContent = `Base: ${data.paths.base_dir}`;
            }

} catch (err) {
            if (err.name === 'AbortError') return;
            console.error(err);
            statusBadge.innerHTML = '<span class="status-dot"></span> Disconnected';
            statusBadge.className = 'status-badge connecting';
        }
    }

    // Make globally accessible for inline onclick
    window.fetchMetrics = fetchMetrics;

    const validateBtn = document.getElementById('validateBtn');
    if (validateBtn) {
        validateBtn.addEventListener('click', async () => {
            const supplier = supplierSelect.value;
            const lineage = lineageSelect ? lineageSelect.value : 'base';
            const resultEl = document.getElementById('validateResult');
            resultEl.textContent = 'Validating...';

            try {
                const res = await fetch(
                    `/api/validate/${encodeURIComponent(supplier)}?lineage=${encodeURIComponent(lineage)}`
                );
                if (!res.ok) throw new Error(`HTTP ${res.status}`);

                const data = await res.json();
                if (data.valid) {
                    resultEl.textContent = `✓ All files present for ${data.effective_supplier}. Entries: ${data.checks.linking_map_entries ?? '—'}`;
                    resultEl.style.color = 'green';
                } else {
                    resultEl.textContent = `✗ Issues: ${(data.issues || []).join('; ')}`;
                    resultEl.style.color = 'red';
                }
            } catch (e) {
                resultEl.textContent = `Validation failed: ${e.message}`;
                resultEl.style.color = 'red';
            }
        });
    }

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
        const profSales = s(fm, 'count_profitable_with_sales');
        const profSubEl = document.getElementById('profitableSubtitle');
        if (profSubEl) profSubEl.textContent = profSales > 0 ? profSales + ' with sales' : 'Products with +ROI';
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
        _lastChartData = chartData;
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
        renderCategoryProfitChart(data);
        renderCategorySalesChart(data);
        renderSellerMixChart(data);
        renderProfitCompetitionChart(data);
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
            if (d.ROI >= 0.3) return '#4edea3'; // Green > 30%
            if (d.ROI >= 0.15) return '#ffb95f'; // Yellow 15-30%
            return '#ffb4ab'; // Red < 15%
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
            data: { labels, datasets: [{ label: 'Count', data: bins, backgroundColor: 'rgba(192, 193, 255, 0.5)', borderColor: '#c0c1ff', borderWidth: 1 }] },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { title: { display: true, text: 'ROI (%)' }, ticks: { maxTicksLimit: 10 } }, y: { title: { display: true, text: 'Count' } } }
            }
        });
    }

    function renderCategoryProfitChart(data) {
        destroyChart('categoryProfit');
        const ctx = document.getElementById('categoryProfitChart');
        if (!ctx) return;

        const catProfits = {};
        data.forEach(d => {
            if (!d.NetProfit || d.NetProfit <= 0) return;
            // Use Category from backend (enriched via cached products)
            const cat = d.Category || 'Other';
            if (!catProfits[cat]) catProfits[cat] = { total: 0, count: 0 };
            catProfits[cat].total += d.NetProfit;
            catProfits[cat].count++;
        });

        const sorted = Object.entries(catProfits)
            .sort((a, b) => b[1].total - a[1].total)
            .slice(0, 10);
        _catProfitSorted = sorted;

        if (sorted.length === 0) return;

        const labels = sorted.map(([cat, v]) => {
            const name = cat.length > 20 ? cat.slice(0, 17) + '...' : cat;
            return `${name} (${v.count})`;
        });
        const values = sorted.map(([, v]) => Math.round(v.total * 100) / 100);

        charts.categoryProfit = new Chart(ctx.getContext('2d'), {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Total Profit (GBP)',
                    data: values,
                    backgroundColor: 'rgba(78, 222, 163, 0.5)',
                    borderColor: '#4edea3',
                    borderWidth: 1,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx2) => {
                                const entry = sorted[ctx2.dataIndex];
                                return `\u00a3${ctx2.raw.toFixed(2)} total profit \u00b7 ${entry[1].count} products`;
                            }
                        }
                    }
                },
                scales: {
                    x: { title: { display: true, text: 'Total Profit (GBP)' } },
                    y: { ticks: { font: { size: 11 } } }
                },
                onClick: (evt, elements) => {
                    if (elements.length > 0) {
                        const catName = _catProfitSorted[elements[0].index][0];
                        showCategoryModal(catName, 'profit');
                    }
                }
            }
        });
    }

    function renderProfitCompetitionChart(data) {
        destroyChart('profitCompetition');
        const ctx = document.getElementById('profitCompetitionChart');
        if (!ctx) return;

        const pts = data
            .filter(d => d.NetProfit != null && Number(d.total_offer_count) > 0)
            .map(d => ({
                x: Number(d.total_offer_count),
                y: d.NetProfit,
                label: d.SupplierTitle
            }));

        if (pts.length === 0) return;

        const colors = pts.map(p => p.y > 0 ? 'rgba(78, 222, 163, 0.6)' : 'rgba(255, 180, 171, 0.6)');

        charts.profitCompetition = new Chart(ctx.getContext('2d'), {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Products',
                    data: pts,
                    backgroundColor: colors,
                    borderColor: 'rgba(255,255,255,0.1)',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: c => [
                                `${(c.raw.label || '').substring(0, 40)}`,
                                `Offers: ${c.raw.x}, Profit: \u00a3${c.raw.y.toFixed(2)}`
                            ]
                        }
                    }
                },
                scales: {
                    x: { title: { display: true, text: 'Total Offer Count' } },
                    y: { title: { display: true, text: 'Net Profit (GBP)' } }
                }
            }
        });
    }

    function renderCategorySalesChart(data) {
        destroyChart('categorySales');
        const ctx = document.getElementById('categorySalesChart');
        if (!ctx) return;
        const catData = {};
        data.forEach(d => {
            if (!d.NetProfit || d.NetProfit <= 0) return;
            const sales = Number(d.sales_value) || 0;
            if (sales <= 0) return;
            const cat = d.Category || 'Other';
            if (!catData[cat]) catData[cat] = { count: 0, totalProfit: 0 };
            catData[cat].count++;
            catData[cat].totalProfit += d.NetProfit;
        });
        const sorted = Object.entries(catData).sort((a, b) => b[1].count - a[1].count).slice(0, 10);
        _catSalesSorted = sorted;
        if (sorted.length === 0) return;
        const labels = sorted.map(([cat, v]) => {
            const name = cat.length > 20 ? cat.slice(0, 17) + '...' : cat;
            return `${name} (${v.count})`;
        });
        const values = sorted.map(([, v]) => v.count);
        charts.categorySales = new Chart(ctx.getContext('2d'), {
            type: 'bar',
            data: { labels, datasets: [{ label: 'Products with Sales', data: values, backgroundColor: 'rgba(78, 222, 163, 0.5)', borderColor: '#4edea3', borderWidth: 1 }] },
            options: {
                indexAxis: 'y',
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx2) => {
                                const entry = sorted[ctx2.dataIndex];
                                return `${ctx2.raw} products with sales \u00b7 \u00a3${entry[1].totalProfit.toFixed(2)} total profit`;
                            }
                        }
                    }
                },
                scales: { x: { title: { display: true, text: 'Profitable Products with Sales' } }, y: { ticks: { font: { size: 11 } } } },
                onClick: (evt, elements) => {
                    if (elements.length > 0) {
                        const catName = _catSalesSorted[elements[0].index][0];
                        showCategoryModal(catName, 'sales');
                    }
                }
            }
        });
    }

    function showCategoryModal(categoryName, filterMode) {
        let products = _lastChartData.filter(d => (d.Category || 'Other') === categoryName);
        if (filterMode === 'profit') {
            products = products.filter(d => d.NetProfit > 0);
        } else if (filterMode === 'sales') {
            products = products.filter(d => d.NetProfit > 0 && Number(d.sales_value) > 0);
        }
        products.sort((a, b) => (b.NetProfit || 0) - (a.NetProfit || 0));
        document.getElementById('categoryModalTitle').textContent = `${categoryName} — ${products.length} products`;
        const tbody = document.getElementById('categoryModalBody');
        tbody.innerHTML = products.map((p, i) => `<tr>
            <td>${i + 1}</td>
            <td title="${escapeHtml(p.SupplierTitle || '')}">${escapeHtml((p.SupplierTitle || '').substring(0, 40))}</td>
            <td title="${escapeHtml(p.AmazonTitle || '')}">${escapeHtml((p.AmazonTitle || '').substring(0, 40))}</td>
            <td>${p.ROI != null ? Number(p.ROI).toFixed(1) + '%' : '--'}</td>
            <td class="${p.NetProfit > 0 ? 'success-text' : ''}">${p.NetProfit != null ? '\u00a3' + Number(p.NetProfit).toFixed(2) : '--'}</td>
            <td>${p.sales_value ? Number(p.sales_value).toLocaleString() : '--'}</td>
        </tr>`).join('') || '<tr><td colspan="6" class="empty-state">No products</td></tr>';
        document.getElementById('categoryModal').style.display = 'block';
    }

    function renderSellerMixChart(data) {
        destroyChart('sellerMix');
        const ctx = document.getElementById('sellerMixChart').getContext('2d');
        const withOffers = data.filter(d => Number(d.total_offer_count) > 0);
        if (!withOffers.length) return;
        const low = withOffers.filter(d => d.total_offer_count <= 5).length;
        const med = withOffers.filter(d => d.total_offer_count > 5 && d.total_offer_count <= 20).length;
        const high = withOffers.filter(d => d.total_offer_count > 20).length;

        charts.sellerMix = new Chart(ctx, {
            type: 'doughnut',
            data: { labels: [`Low 1-5 (${low})`, `Med 6-20 (${med})`, `High 20+ (${high})`], datasets: [{ data: [low, med, high], backgroundColor: ['rgba(78, 222, 163, 0.7)', 'rgba(255, 185, 95, 0.7)', 'rgba(255, 180, 171, 0.7)'], borderColor: ['#4edea3', '#ffb95f', '#ffb4ab'], borderWidth: 2 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } }
        });
    }

    function escapeHtml(str) { const d = document.createElement('div'); d.textContent = str; return d.innerHTML; }

    function renderTables(data) {
        function truncate(str, n) {
            if (!str) return '';
            return (str.length > n) ? str.substr(0, n - 1) + '...' : str;
        }

        // 1. Render Top 20 Products by Profit
        const topProducts = [...data]
            .filter(item => item.NetProfit > 0)
            .sort((a, b) => b.NetProfit - a.NetProfit)
            .slice(0, 20);

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

        // 2. Top Products with Sales
        const topSales = [...data]
            .filter(item => item.NetProfit > 0 && Number(item.sales_value) > 0)
            .sort((a, b) => Number(b.sales_value) - Number(a.sales_value))
            .slice(0, 10);

        const salesBody = document.getElementById('topSalesTableBody');
        if (salesBody) {
            salesBody.innerHTML = topSales.map(item => `
                <tr>
                    <td title="${escapeHtml(item.SupplierTitle || '')}">${escapeHtml(truncate(item.SupplierTitle, 25))}</td>
                    <td title="${escapeHtml(item.AmazonTitle || '')}">${escapeHtml(truncate(item.AmazonTitle, 25))}</td>
                    <td class="accent-val">${Number(item.sales_value).toLocaleString()}</td>
                    <td class="success-text">\u00a3${(item.NetProfit || 0).toFixed(2)}</td>
                    <td class="accent-val">${(item.ROI * 100).toFixed(1)}%</td>
                </tr>
            `).join('') || '<tr><td colspan="5" class="empty-state">No products with sales data yet.</td></tr>';
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
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, supplier: supplierSelect.value })
            });

            // Remove thinking indicator and create a live trace container
            removeThinking();
            const bubbleId = 'chat-bubble-' + Date.now();
            const outerDiv = document.createElement('div');
            outerDiv.className = 'chat-message assistant';
            outerDiv.innerHTML = '<div class="avatar">🤖</div><div class="msg-bubble" id="' + bubbleId + '"></div>';
            chatHistory.appendChild(outerDiv);
            chatHistory.scrollTop = chatHistory.scrollHeight;
            const bubbleEl = document.getElementById(bubbleId);

            // Read the SSE stream progressively
            const reader = res.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const parts = buffer.split('\n\n');
                buffer = parts.pop(); // keep incomplete last chunk

                for (const part of parts) {
                    if (!part.startsWith('data: ')) continue;
                    let data;
                    try { data = JSON.parse(part.substring(6)); } catch { continue; }

                    if (data.type === 'trace_update') {
                        const s = data.step;
                        const stepDiv = document.createElement('div');
                        stepDiv.className = 'trace-step';
                        stepDiv.innerHTML =
                            '<span class="trace-label">STEP ' + s.step + ' ⚡ ' + (s.tool || '').toUpperCase() + '</span>' +
                            (s.explanation ? '<p class="trace-explanation">' + escapeHtml(s.explanation) + '</p>' : '') +
                            (s.result ? '<details class="trace-result-details"><summary>Tool Output</summary><pre class="trace-result">' + escapeHtml(typeof s.result === 'string' ? s.result : JSON.stringify(s.result, null, 2)) + '</pre></details>' : '');
                        bubbleEl.appendChild(stepDiv);
                        chatHistory.scrollTop = chatHistory.scrollHeight;

                    } else if (data.type === 'final_answer') {
                        const ans = document.createElement('div');
                        ans.className = 'final-answer';
                        ans.textContent = data.text;
                        bubbleEl.appendChild(ans);
                        chatHistory.scrollTop = chatHistory.scrollHeight;

                    } else if (data.type === 'approval_needed') {
                        bubbleEl.innerHTML += renderApproval(data.pending_tool);
                        chatHistory.scrollTop = chatHistory.scrollHeight;

                    } else if (data.type === 'approval_pending') {
                        const warn = document.createElement('div');
                        warn.className = 'error-block';
                        warn.textContent = '⚠️ ' + (data.message || '');
                        bubbleEl.appendChild(warn);

                    } else if (data.type === 'error') {
                        const err = document.createElement('div');
                        err.className = 'error-block';
                        err.innerHTML = '<strong>⚠️ Error:</strong> ' + escapeHtml(data.message || 'Unknown error');
                        bubbleEl.appendChild(err);
                    }
                }
            }
        } catch (err) {
            removeThinking();
            addChatBubble('assistant', '<div class="error-block"><strong>⚠️ Network Error:</strong> ' + escapeHtml(err.message) + '</div>');
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

        // ===== AI ANALYSIS AGENT LOGIC =====
    let _aiJobId = null;
    let _aiPollTimer = null;

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

    async function loadAiCategories() {
        const supplier = supplierSelect.value;
        const lineage = lineageSelect ? lineageSelect.value : 'base';
        const sel = document.getElementById('aiCategoryFilter');
        if (!sel) return;
        sel.innerHTML = '<option value="">Loading…</option>';
        try {
            const res = await fetch(`/api/categories/${encodeURIComponent(supplier)}?lineage=${lineage}`);
            const data = await res.json();
            if (!data.categories || !data.categories.length) {
                sel.innerHTML = '<option value="">No categories found</option>';
            } else {
                sel.innerHTML = data.categories.map(c =>
                    `<option value="${c.url}">${c.name} (${c.count})</option>`
                ).join('');
            }
        } catch (e) { sel.innerHTML = '<option value="">Error loading categories</option>'; }
    }

    async function loadFinancialReportsUnified() {
        const supplier = supplierSelect.value;
        const lineage = lineageSelect ? lineageSelect.value : 'base';
        const dashboardSel = document.getElementById('dashboardReportSelect');
        const analysisSel = document.getElementById('analysisReportSelect');
        if (!dashboardSel && !analysisSel) return;

        if (_reportsAbortCtrl) _reportsAbortCtrl.abort();
        _reportsAbortCtrl = new AbortController();

        const prevDashboardValue = dashboardSel ? dashboardSel.value : '';
        const prevAnalysisValue = analysisSel ? analysisSel.value : '';

        try {
            const res = await fetch(`/api/reports/${encodeURIComponent(supplier)}?lineage=${lineage}`, { signal: _reportsAbortCtrl.signal });
            const data = await res.json();
            let html = '<option value="">\u2014 latest \u2014</option>';
            if (data.reports && data.reports.length) {
                html += data.reports.map(r => {
                    const dt = new Date(r.mtime * 1000).toLocaleDateString();
                    return `<option value="${r.filename}">${r.filename} (${r.rows} rows, ${dt})</option>`;
                }).join('');
            }

            if (dashboardSel) {
                dashboardSel.innerHTML = html;
                dashboardSel.value = prevDashboardValue;
                if (dashboardSel.value !== prevDashboardValue) dashboardSel.value = '';
            }
            if (analysisSel) {
                analysisSel.innerHTML = html;
                analysisSel.value = prevAnalysisValue;
                if (analysisSel.value !== prevAnalysisValue) analysisSel.value = '';
            }
        } catch (e) {
            if (e.name === 'AbortError') return;
        }
    }

    const aiModeEl = document.getElementById('aiMode');
    if (aiModeEl) {
        aiModeEl.addEventListener('change', () => {
            const grp = document.getElementById('aiAutoNGroup');
            if (grp) grp.style.display = aiModeEl.value === 'auto' ? 'block' : 'none';
        });
    }

    window.aiFilterToggle = function() {
        const mode = (document.querySelector('input[name="aiFilterMode"]:checked') || {}).value || 'none';
        document.getElementById('aiRowRangeGroup').style.display = mode === 'rows' ? 'block' : 'none';
        document.getElementById('aiCategoryGroup').style.display = mode === 'category' ? 'block' : 'none';
        if (mode === 'category') loadAiCategories();
    };

    window.runAiAnalysis = async function() {
        const csvPath = (document.getElementById('aiReportSelect') || {}).value || '';
        const filterMode = (document.querySelector('input[name="aiFilterMode"]:checked') || {}).value || 'none';
        const fromRow = filterMode === 'rows' ? ((document.getElementById('aiFromRow') || {}).value || null) : null;
        const toRow = filterMode === 'rows' ? ((document.getElementById('aiToRow') || {}).value || null) : null;
        const categoryFilter = filterMode === 'category' ? ((document.getElementById('aiCategoryFilter') || {}).value || '') : '';
        const batchSize = parseInt((document.getElementById('aiBatchSize') || {}).value || '20');
        const supplier = supplierSelect.value;
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
                body: JSON.stringify({
                    csv_path: csvPath,
                    supplier: supplier,
                    from_row: fromRow ? parseInt(fromRow) : null,
                    to_row: toRow ? parseInt(toRow) : null,
                    batch_size: batchSize,
                    category_filter: categoryFilter
                })
            });
            const data = await res.json();
            if (data.error) {
                if (statusEl) statusEl.textContent = data.message;
                if (runBtn) runBtn.disabled = false;
                if (stopBtn) stopBtn.style.display = 'none';
                return;
            }
            _aiJobId = data.job_id;
            if (statusEl) statusEl.textContent = `Job ${_aiJobId} running…`;
            _startAiPoll();
        } catch (e) {
            if (statusEl) statusEl.textContent = `Error: ${e.message}`;
            if (runBtn) runBtn.disabled = false;
            if (stopBtn) stopBtn.style.display = 'none';
        }
    };

    window.stopAiAnalysis = async function() {
        if (_aiPollTimer) { clearInterval(_aiPollTimer); _aiPollTimer = null; }
        const jobId = _aiJobId;
        _aiJobId = null;
        const runBtn = document.getElementById('aiRunBtn');
        const stopBtn = document.getElementById('aiStopBtn');
        const statusEl = document.getElementById('aiJobStatus');
        if (runBtn) runBtn.disabled = false;
        if (stopBtn) stopBtn.style.display = 'none';
        if (statusEl) statusEl.textContent = 'Cancelling...';
        if (jobId) {
            try { await fetch(`/api/ai-analyze/cancel/${jobId}`, { method: 'POST' }); } catch (e) {}
        }
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

                if (outputEl) { outputEl.textContent = (job.output || []).join('\n') || 'Running…'; outputEl.scrollTop = outputEl.scrollHeight; }
                if (metaEl) metaEl.textContent = `${job.elapsed}s elapsed`;

                if (job.status === 'done' || job.status === 'error') {
                    clearInterval(_aiPollTimer); _aiPollTimer = null; _aiJobId = null;
                    if (statusEl) statusEl.textContent = job.status === 'done' ? '✓ Analysis complete' : `✗ Error: ${job.error || 'unknown'}`;
                    if (runBtn) runBtn.disabled = false;
                    if (stopBtn) stopBtn.style.display = 'none';
                } else {
                    if (statusEl) statusEl.textContent = `Running… (${job.elapsed}s)`;
                }
            } catch (e) { clearInterval(_aiPollTimer); _aiPollTimer = null; }
        }, 2000);
    }

    // ===== AUTO-REFRESH =====
    function setupRefresh() {
        if (refreshTimer) clearInterval(refreshTimer);
        const secs = parseInt(refreshSelect.value);
        if (secs > 0) refreshTimer = setInterval(() => fetchMetrics(false), secs * 1000);
    }

    refreshSelect.addEventListener('change', setupRefresh);
    supplierSelect.addEventListener('change', () => {
        const dSel = document.getElementById('dashboardReportSelect');
        const aSel = document.getElementById('analysisReportSelect');
        if (dSel) { dSel.value = ''; dSel.innerHTML = '<option value="">\u2014 latest \u2014</option>'; }
        if (aSel) { aSel.value = ''; aSel.innerHTML = '<option value="">\u2014 latest \u2014</option>'; }
        prevMatches = null;
        setupRefresh();
        fetchMetrics();
        loadAiReports();
        loadAiCategories();
        loadFinancialReportsUnified();
    });
    if (lineageSelect) {
        lineageSelect.addEventListener('change', () => {
            const dSel = document.getElementById('dashboardReportSelect');
            const aSel = document.getElementById('analysisReportSelect');
            if (dSel) { dSel.value = ''; dSel.innerHTML = '<option value="">\u2014 latest \u2014</option>'; }
            if (aSel) { aSel.value = ''; aSel.innerHTML = '<option value="">\u2014 latest \u2014</option>'; }
            prevMatches = null;
            setupRefresh();
            fetchMetrics();
            loadAiReports();
            loadAiCategories();
            loadFinancialReportsUnified();
        });
    }
    if (salesFieldToggle) {
        salesFieldToggle.addEventListener('change', () => {
            fetchMetrics();
            if (typeof window.loadAnalysis === 'function') {
                window.loadAnalysis();
            }
        });
    }

    // ===== INIT =====
    fetchMetrics();
    loadAiReports();
    loadAiCategories();
    loadFinancialReportsUnified();
    setupRefresh();
    // ===== NEW CHAT RESET =====
    window.resetChat = async function() {
        try {
            await fetch('/api/chat/reset', { method: 'POST' });
        } catch (e) { /* ignore */ }
        // Clear the UI
        const chatHistory = document.getElementById('chatHistory');
        chatHistory.innerHTML = '<div class="chat-message assistant"><div class="avatar">🤖</div><div class="msg-bubble">Chat cleared. How can I assist?</div></div>';
    };

    // ===== ANALYSIS TAB =====
    let analysisData = [];
    let analysisPage = 1;
    const ANALYSIS_PAGE_SIZE = 25;

window.loadAnalysis = async function() {
        const supplier = supplierSelect.value;
        const lineage = lineageSelect ? lineageSelect.value : 'base';
        const salesField = getSelectedSalesField();
        const tier = document.getElementById('analysisTierFilter').value;
        const minRoi = document.getElementById('analysisMinRoi').value;
        const minProfit = document.getElementById('analysisMinProfit').value;
        const minSales = document.getElementById('analysisMinSales').value;
        const sortBy = document.getElementById('analysisSortBy').value;
        const categoryFilter = (document.getElementById('analysisCategoryFilter') || {}).value || '';

        if (_analysisAbortCtrl) _analysisAbortCtrl.abort();
        _analysisAbortCtrl = new AbortController();

        try {
            const report = (document.getElementById('analysisReportSelect') || {}).value || '';
            const params = new URLSearchParams({
                lineage, tier, sort: sortBy,
                sales_field: salesField,
                ...(report ? { report } : {}),
                ...(minRoi ? { min_roi: minRoi } : {}),
                ...(minProfit ? { min_profit: minProfit } : {}),
                ...(minSales ? { min_sales: minSales } : {}),
                ...(categoryFilter ? { category: categoryFilter } : {}),
            });
            const res = await fetch(`/api/analysis/${encodeURIComponent(supplier)}?${params}`, { signal: _analysisAbortCtrl.signal });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            if (data.error) {
                document.getElementById('analysisTableBody').innerHTML =
                    `<tr><td colspan="8" class="empty-state">${escapeHtml(data.message || 'Error loading analysis')}</td></tr>`;
                return;
            }

            // Update tier counts
            const tc = data.tier_counts || {};
            document.getElementById('tier1Count').textContent = (tc.TIER_1_VERIFIED || 0).toLocaleString();
            document.getElementById('tier2Count').textContent = (tc.TIER_2_LIKELY || 0).toLocaleString();
            document.getElementById('tier3Count').textContent = (tc.TIER_3_NEEDS_REVIEW || 0).toLocaleString();
            document.getElementById('tier4Count').textContent = (tc.TIER_4_REJECTED || 0).toLocaleString();
            document.getElementById('analysisTotalRows').textContent = (data.total_rows || 0).toLocaleString();

            analysisData = data.rows || [];
            analysisPage = 1;
            renderAnalysisTable();
            // Populate category dropdown
            const catSel = document.getElementById('analysisCategoryFilter');
            if (catSel && data.distinct_categories) {
                const cur = catSel.value;
                catSel.innerHTML = '<option value="">All Categories</option>' +
                    data.distinct_categories.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');
                catSel.value = cur;
            }
            const expBtn = document.getElementById('exportAnalysisBtn');
            if (expBtn) expBtn.style.display = analysisData.length > 0 ? 'inline-flex' : 'none';

} catch (err) {
            if (err.name === 'AbortError') return;
            console.error('Analysis error:', err);
            document.getElementById('analysisTableBody').innerHTML =
                `<tr><td colspan="8" class="empty-state">Error: ${escapeHtml(err.message)}</td></tr>`;
        }
    };

    function renderAnalysisTable() {
        const start = (analysisPage - 1) * ANALYSIS_PAGE_SIZE;
        const pageData = analysisData.slice(start, start + ANALYSIS_PAGE_SIZE);
        const totalPages = Math.ceil(analysisData.length / ANALYSIS_PAGE_SIZE);

        document.getElementById('analysisResultCount').textContent = `${analysisData.length} results`;

        const tbody = document.getElementById('analysisTableBody');
        if (pageData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" class="empty-state">No products match filters</td></tr>';
            document.getElementById('analysisPagination').innerHTML = '';
            return;
        }

        const tierColors = {
            'TIER_1_VERIFIED': '#4edea3',
            'TIER_2_LIKELY': '#c0c1ff',
            'TIER_3_NEEDS_REVIEW': '#ffb95f',
            'TIER_4_REJECTED': '#ffb4ab',
        };

        tbody.innerHTML = pageData.map((row, i) => {
            const tierColor = tierColors[row.tier] || '#908fa0';
            const roi = row.ROI ? Number(row.ROI).toFixed(1) + '%' : '--';  // G1 FIX: ROI already stored as % in CSV
            const profit = row.NetProfit ? '\u00a3' + Number(row.NetProfit).toFixed(2) : '--';
            const flags = (row.flags || []).join(', ');
            const tierShort = (row.tier || '').replace('TIER_', 'T').replace('_VERIFIED', '').replace('_LIKELY', '').replace('_NEEDS_REVIEW', '').replace('_REJECTED', '');
            return `<tr style="border-left: 3px solid ${tierColor}">
                <td>${start + i + 1}</td>
                <td title="${escapeHtml(row.SupplierTitle || '')}">${escapeHtml((row.SupplierTitle || '').substring(0, 35))}</td>
                <td title="${escapeHtml(row.AmazonTitle || '')}">${escapeHtml((row.AmazonTitle || '').substring(0, 35))}</td>
                <td style="font-size:0.75rem; max-width:120px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${escapeHtml(row.Category || '')}">${escapeHtml((row.Category || '').substring(0, 18))}</td>
                <td><span class="badge" style="background:${tierColor}; color: #131314;">${tierShort}</span></td>
                <td>${row.confidence_score || 0}</td>
                <td>${roi}</td>
                <td class="${Number(row.NetProfit) > 0 ? 'success-text' : ''}">${profit}</td>
                <td>${row.sales_value ? Number(row.sales_value).toLocaleString() : '--'}</td>
                <td style="font-size:0.7rem; max-width:120px; overflow:hidden; text-overflow:ellipsis;" title="${escapeHtml(flags)}">${escapeHtml(flags)}</td>
            </tr>`;
        }).join('');

        // Pagination
        const pagEl = document.getElementById('analysisPagination');
        if (totalPages <= 1) { pagEl.innerHTML = ''; return; }
        let pagHtml = '';
        if (analysisPage > 1) pagHtml += `<button class="btn-outline" onclick="window.analysisGoPage(${analysisPage - 1})">&lt;</button>`;
        for (let p = 1; p <= totalPages; p++) {
            if (p === analysisPage) pagHtml += `<button class="btn-primary" style="min-width:36px;">${p}</button>`;
            else if (p <= 3 || p >= totalPages - 2 || Math.abs(p - analysisPage) <= 1) {
                pagHtml += `<button class="btn-outline" style="min-width:36px;" onclick="window.analysisGoPage(${p})">${p}</button>`;
            } else if (p === 4 || p === totalPages - 3) {
                pagHtml += '<span style="color:var(--text-muted);">...</span>';
            }
        }
        if (analysisPage < totalPages) pagHtml += `<button class="btn-outline" onclick="window.analysisGoPage(${analysisPage + 1})">&gt;</button>`;
        pagEl.innerHTML = pagHtml;
    }

    window.analysisGoPage = function(p) {
        analysisPage = p;
        renderAnalysisTable();
    };

    window.exportAnalysisCsv = function() {
        if (!analysisData.length) return;
        const cols = Object.keys(analysisData[0]).filter(k => !k.startsWith('_'));
        const header = cols.join(',');
        const rows = analysisData.map(row =>
            cols.map(c => {
                const v = (row[c] == null ? '' : String(row[c]));
                return v.includes(',') || v.includes('"') || v.includes('\n')
                    ? `"${v.replace(/"/g, '""')}"` : v;
            }).join(',')
        );
        const csv = [header, ...rows].join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `fba_analysis_${new Date().toISOString().slice(0,10)}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

});
