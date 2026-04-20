from __future__ import annotations

import json
import pathlib
import re
import time

import requests
from bs4 import BeautifulSoup

ROOT = pathlib.Path(
    r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
)
INPUT_FILE = (
    ROOT
    / "OUTPUTS"
    / "PRODUCTS_LISTS"
    / "poundwholesale-co-uk_phase5_validation_candidates_20260414_232258.json"
)
OUTPUT_FILE = (
    ROOT
    / "OUTPUTS"
    / "PRODUCTS_LISTS"
    / "poundwholesale-co-uk_phase5_api_avenue_results_20260415_0200.json"
)

STOP_WORDS = {"the", "and", "with", "for", "in", "of", "a", "an", "to", "by"}
PRICE_RE = re.compile(r"(?:GBP|\xa3|\u00a3)\s?\d+(?:\.\d{2})?", re.IGNORECASE)


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower())) - STOP_WORDS


def overlap_count(a: str, b: str) -> int:
    return len(tokens(a) & tokens(b))


def fetch_url(session: requests.Session, url: str, expected_text: str) -> dict:
    t0 = time.perf_counter()
    try:
        response = session.get(url, timeout=20, allow_redirects=True)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        html = response.text[:300000]
        soup = BeautifulSoup(html, "html.parser")
        title = (
            soup.title.string.strip()[:200]
            if soup.title is not None and soup.title.string is not None
            else ""
        )
        page_text = " ".join(soup.get_text(" ", strip=True).split())[:8000]
        combined = f"{title} {page_text}".strip()
        live = (response.status_code < 400) and (
            re.search(r"404|page not found|sorry", combined.lower()) is None
        )
        price_match = PRICE_RE.search(page_text)
        return {
            "status_code": response.status_code,
            "elapsed_ms": elapsed_ms,
            "title": title,
            "live": live,
            "price_text": price_match.group(0) if price_match else None,
            "plausible": overlap_count(expected_text, combined) >= 2,
        }
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        return {
            "status_code": None,
            "elapsed_ms": elapsed_ms,
            "title": "",
            "live": False,
            "price_text": None,
            "plausible": False,
            "error": str(exc)[:180],
        }


def main() -> None:
    payload = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    candidates = payload["products"]

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        }
    )

    start = time.perf_counter()
    results = []
    for item in candidates:
        supplier = fetch_url(session, item["url"], item["title"])
        amazon = fetch_url(session, item["amazon_url"], item["amazon_title"])
        decision = (
            "keep"
            if supplier["live"]
            and amazon["live"]
            and supplier["plausible"]
            and amazon["plausible"]
            else "deprioritize"
        )
        results.append(
            {
                "title": item["title"],
                "bucket": item["bucket"],
                "supplier_url": item["url"],
                "amazon_url": item["amazon_url"],
                "supplier": supplier,
                "amazon": amazon,
                "decision": decision,
            }
        )

    elapsed_s = round(time.perf_counter() - start, 2)
    summary = {
        "products": len(results),
        "keep": sum(1 for row in results if row["decision"] == "keep"),
        "deprioritize": sum(1 for row in results if row["decision"] == "deprioritize"),
        "supplier_live": sum(1 for row in results if row["supplier"]["live"]),
        "amazon_live": sum(1 for row in results if row["amazon"]["live"]),
        "avg_supplier_ms": round(
            sum(row["supplier"]["elapsed_ms"] for row in results) / len(results), 1
        ),
        "avg_amazon_ms": round(
            sum(row["amazon"]["elapsed_ms"] for row in results) / len(results), 1
        ),
        "total_elapsed_s": elapsed_s,
    }
    out = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "method": "requests+html_parse (API-like extraction avenue)",
        "summary": summary,
        "results": results,
    }
    OUTPUT_FILE.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(str(OUTPUT_FILE))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
