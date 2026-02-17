from __future__ import annotations

import argparse
import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from control_plane.paths import get_paths

log = logging.getLogger(__name__)

SELECTORS_OF_INTEREST = [
    "a.btn-load-more",
    "button.load-more",
    ".pagination",
    "nav.pagination",
    "[data-pagination]",
    ".product-list",
    ".product-grid",
]


async def run_probe(
    url: str,
    probe_id: str,
    capture_html: bool = False,
    capture_screenshot: bool = False,
    capture_trace: bool = False,
    capture_har: bool = False,
) -> dict:
    from playwright.async_api import async_playwright

    paths = get_paths()
    out_dir = paths.control_plane_root / "diagnostics" / probe_id
    out_dir.mkdir(parents=True, exist_ok=True)

    report: dict = {
        "probe_id": probe_id,
        "url": url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "page_title": None,
        "content_length": 0,
        "selectors_found": {},
        "errors": [],
    }

    pw = await async_playwright().start()
    try:
        cdp_endpoint = await _resolve_cdp_endpoint(9222)
        browser = await pw.chromium.connect_over_cdp(cdp_endpoint, timeout=15000)
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()

        if capture_har:
            har_path = out_dir / "network.har"
            ctx = await browser.new_context(record_har_path=str(har_path))

        if capture_trace:
            await ctx.tracing.start(screenshots=True, snapshots=True)

        page = await ctx.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
        except Exception as exc:
            report["errors"].append(f"navigation: {exc}")
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)

        report["page_title"] = await page.title()

        if capture_html:
            html = await page.content()
            report["content_length"] = len(html)
            (out_dir / "page.html").write_text(html, encoding="utf-8")

        if capture_screenshot:
            await page.screenshot(path=str(out_dir / "screenshot.png"), full_page=True)

        for sel in SELECTORS_OF_INTEREST:
            try:
                count = await page.locator(sel).count()
                if count > 0:
                    report["selectors_found"][sel] = count
            except Exception:
                pass

        product_text = await page.evaluate("""
            () => {
                const el = document.querySelector('[class*="viewed"], [class*="showing"]');
                return el ? el.textContent.trim() : null;
            }
        """)
        if product_text:
            report["product_count_text"] = product_text

        if capture_trace:
            trace_path = out_dir / "trace.zip"
            await ctx.tracing.stop(path=str(trace_path))
            report["trace_path"] = str(trace_path)

        await page.close()

        if capture_har:
            await ctx.close()
            report["har_path"] = str(har_path)

    except Exception as exc:
        report["errors"].append(str(exc))
    finally:
        await pw.stop()

    report_path = out_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    log.info(f"Probe complete: {report_path}")
    return report


async def _resolve_cdp_endpoint(port: int) -> str:
    import aiohttp

    for host in [f"http://[::1]:{port}", f"http://127.0.0.1:{port}"]:
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(f"{host}/json/version", timeout=aiohttp.ClientTimeout(total=3)) as r:
                    if r.status == 200:
                        data = await r.json()
                        ws = data.get("webSocketDebuggerUrl", "")
                        if ws:
                            return ws
                        return f"{host}"
        except Exception:
            continue
    return f"http://127.0.0.1:{port}"


def build_parser(parent_sub: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    if parent_sub is not None:
        p = parent_sub.add_parser("diagnostics-probe")
    else:
        p = argparse.ArgumentParser(prog="diagnostics-probe")
    p.add_argument("--url", required=True)
    p.add_argument("--probe-id", required=True)
    p.add_argument("--html", action="store_true")
    p.add_argument("--screenshot", action="store_true")
    p.add_argument("--trace", action="store_true")
    p.add_argument("--har", action="store_true")
    return p


def main(args: argparse.Namespace) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    report = asyncio.run(run_probe(
        url=args.url,
        probe_id=args.probe_id,
        capture_html=args.html,
        capture_screenshot=args.screenshot,
        capture_trace=args.trace,
        capture_har=args.har,
    ))
    found = report.get("selectors_found", {})
    errors = report.get("errors", [])
    print(f"Probe {args.probe_id}: title={report.get('page_title')!r}, "
          f"selectors={len(found)}, errors={len(errors)}")
    if found:
        for sel, cnt in found.items():
            print(f"  {sel}: {cnt}")
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
