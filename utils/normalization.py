import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

TRACKING_PREFIXES = ("utm_", "gclid", "_ga")

def normalize_url(url: str) -> str:
    """Normalize URL by lowercasing, removing tracking params, sorting query, stripping trailing slash."""
    if not url:
        return ""
    parsed = urlparse(url.lower())
    params = [p for p in parse_qsl(parsed.query) if not any(p[0].startswith(pref) for pref in TRACKING_PREFIXES)]
    params.sort()
    query = urlencode(params)
    path = parsed.path.rstrip('/')
    return urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, query, parsed.fragment))

def normalize_ean(ean: str) -> str:
    """Trim whitespace and ensure EAN is a clean string with leading zeros preserved."""
    if ean is None:
        return ""
    if not isinstance(ean, str):
        ean = str(ean)
    return ean.strip()
