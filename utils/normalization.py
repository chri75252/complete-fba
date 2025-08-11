import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

TRACKING_PREFIXES = ("utm_", "gclid", "_ga")

def normalize_url(url: str) -> str:
    """
    Normalize URL: lowercase host, strip tracking params, normalize trailing slashes, stable query ordering.
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL string, or original URL if normalization fails
    """
    if not url:
        return ""
    
    try:
        parsed = urlparse(url)
        # Only lowercase the scheme and netloc (host), preserve path case
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path.rstrip('/')
        
        # Filter out tracking parameters and sort remaining ones
        params = [p for p in parse_qsl(parsed.query) if not any(p[0].startswith(pref) for pref in TRACKING_PREFIXES)]
        params.sort()
        query = urlencode(params)
        
        return urlunparse((scheme, netloc, path, parsed.params, query, parsed.fragment))
    except Exception:
        # Fallback to original URL if normalization fails
        return url

def normalize_ean(ean: str) -> str:
    """
    Normalize EAN: string type, preserve leading zeros, trim whitespace.
    
    Args:
        ean: EAN to normalize
        
    Returns:
        Normalized EAN string, or original value if normalization fails
    """
    if ean is None:
        return ""
    
    try:
        if not isinstance(ean, str):
            ean = str(ean)
        return ean.strip()
    except Exception:
        # Fallback to original value if normalization fails
        return str(ean) if ean is not None else ""
