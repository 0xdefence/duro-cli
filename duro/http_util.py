"""Shared HTTP utilities with security hardening."""
from __future__ import annotations

import json
import re
import ssl
import urllib.request
from urllib.parse import urlparse


def validated_ssl_context() -> ssl.SSLContext:
    """Return an SSL context with hostname checking and cert verification."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx


def validate_url_scheme(url: str, *, allowed_schemes: tuple[str, ...] = ("https",)) -> str:
    """Validate URL scheme. Raises ValueError on invalid scheme."""
    parsed = urlparse(url)
    if parsed.scheme not in allowed_schemes:
        raise ValueError(
            f"URL scheme '{parsed.scheme}' not allowed. Must be one of: {allowed_schemes}"
        )
    if not parsed.netloc:
        raise ValueError("URL must have a valid host")
    return url


def safe_urlopen(req: urllib.request.Request, *, timeout: int = 30) -> bytes:
    """Open a URL with SSL verification and return response bytes."""
    ctx = validated_ssl_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read()
