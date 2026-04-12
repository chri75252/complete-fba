from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode
import unicodedata

_TRACKERS = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid"}

def _nfc(s: str|None) -> str:
    return unicodedata.normalize("NFC", (s or "").strip())

def normalize_url(u: str|None) -> str:
    if not u:
        return ""
    raw = _nfc(u)
    p = urlparse(raw)
    host = p.netloc.lower()
    path = p.path.rstrip("/")
    q = [(k,v) for (k,v) in parse_qsl(p.query, keep_blank_values=False)
         if k and k.lower() not in _TRACKERS]
    return urlunparse((p.scheme.lower(), host, path, "", urlencode(sorted(q)), ""))

def normalize_ean(e: str|None) -> str|None:
    if not e: return None
    s = "".join(ch for ch in _nfc(e) if ch.isdigit())
    return s or None

def stable_key(url: str|None, ean: str|None) -> str:
    ne = normalize_ean(ean)
    if ne:  # **EAN-first authority**
        return f"ean:{ne}"
    nu = normalize_url(url)
    return f"url:{nu}" if nu else "anon:__missing__"
