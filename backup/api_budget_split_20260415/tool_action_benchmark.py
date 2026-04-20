from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests


ROOT = Path(
    r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
)
INPUT = ROOT / "OUTPUTS" / "PRODUCTS_LISTS" / "poundwholesale-co-uk_phase5_validation_candidates_20260414_232258.json"
OUT = ROOT / "OUTPUTS" / "PRODUCTS_LISTS" / "tool_action_benchmark_20260415_0220.json"


def bench_firecrawl(sample_urls: list[str], key: str) -> dict:
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    calls = []
    for url in sample_urls:
        t0 = time.perf_counter()
        ok = False
        status = None
        chars = 0
        err = None
        try:
            r = requests.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers=headers,
                json={"url": url, "formats": ["markdown"], "onlyMainContent": True},
                timeout=60,
            )
            status = r.status_code
            j = r.json()
            ok = bool(j.get("success"))
            chars = len(((j.get("data") or {}).get("markdown") or ""))
        except Exception as exc:  # noqa: BLE001
            err = str(exc)[:160]
        calls.append(
            {
                "url": url,
                "status": status,
                "success": ok,
                "chars": chars,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1),
                "error": err,
            }
        )
    success = [c for c in calls if c["success"]]
    return {
        "actions": len(calls),
        "success_count": len(success),
        "success_rate": round(len(success) / max(1, len(calls)), 3),
        "avg_ms": round(sum(c["elapsed_ms"] for c in calls) / max(1, len(calls)), 1),
        "calls": calls,
    }


def bench_tavily(key: str) -> dict:
    queries = [
        "UK kitchen cleaners demand trend 2026 ecommerce",
        "UK skincare ecommerce demand trend 2026",
    ]
    calls = []
    for q in queries:
        t0 = time.perf_counter()
        status = None
        results_count = 0
        ok = False
        err = None
        try:
            r = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": key, "query": q, "search_depth": "basic", "max_results": 4},
                timeout=45,
            )
            status = r.status_code
            j = r.json()
            results_count = len(j.get("results", []))
            ok = status == 200 and results_count > 0
        except Exception as exc:  # noqa: BLE001
            err = str(exc)[:160]
        calls.append(
            {
                "query": q,
                "status": status,
                "results_count": results_count,
                "success": ok,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1),
                "error": err,
            }
        )
    success = [c for c in calls if c["success"]]
    return {
        "actions": len(calls),
        "success_count": len(success),
        "success_rate": round(len(success) / max(1, len(calls)), 3),
        "avg_ms": round(sum(c["elapsed_ms"] for c in calls) / max(1, len(calls)), 1),
        "calls": calls,
    }


def bench_scrapfly(key: str) -> dict:
    t0 = time.perf_counter()
    try:
        r = requests.get(
            "https://api.scrapfly.io/scrape",
            params={"key": key, "url": "https://www.amazon.co.uk/dp/B098P62161", "render_js": "false"},
            timeout=40,
        )
        ok = r.status_code == 200
        return {
            "actions": 1,
            "success_count": 1 if ok else 0,
            "success_rate": 1.0 if ok else 0.0,
            "avg_ms": round((time.perf_counter() - t0) * 1000, 1),
            "status": r.status_code,
            "sample": r.text[:280],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "actions": 1,
            "success_count": 0,
            "success_rate": 0.0,
            "avg_ms": round((time.perf_counter() - t0) * 1000, 1),
            "status": None,
            "sample": str(exc)[:160],
        }


def bench_apify(token: str) -> dict:
    t0 = time.perf_counter()
    try:
        r = requests.get("https://api.apify.com/v2/users/me", params={"token": token}, timeout=40)
        ok = r.status_code == 200
        return {
            "actions": 1,
            "success_count": 1 if ok else 0,
            "success_rate": 1.0 if ok else 0.0,
            "avg_ms": round((time.perf_counter() - t0) * 1000, 1),
            "status": r.status_code,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "actions": 1,
            "success_count": 0,
            "success_rate": 0.0,
            "avg_ms": round((time.perf_counter() - t0) * 1000, 1),
            "status": None,
            "error": str(exc)[:160],
        }


def main() -> None:
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    sample = data["products"][:4]
    sample_urls = []
    for row in sample:
        sample_urls.append(row["url"])
        sample_urls.append(row["amazon_url"])

    firecrawl = bench_firecrawl(sample_urls, os.getenv("FIRECRAWL_API_KEY", ""))
    tavily = bench_tavily(os.getenv("TAVILY_API_KEY", ""))
    scrapfly = bench_scrapfly(os.getenv("SCRAPIFY_API_KEY", ""))
    apify = bench_apify(os.getenv("APIFY_TOKEN", ""))

    result = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cohort_size": len(data["products"]),
        "firecrawl": firecrawl,
        "tavily": tavily,
        "scrapfly_alias": scrapfly,
        "apify_token_check": apify,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(str(OUT))
    print(json.dumps({k: v for k, v in result.items() if k != "firecrawl" and k != "tavily"}, indent=2))


if __name__ == "__main__":
    main()
