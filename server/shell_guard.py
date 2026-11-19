# ==============================================================================
# Program: shell_guard.py
# Purpose: Dependency-free access-control helpers for the /ws/shell terminal WebSocket in server/main.py.
# ==============================================================================

# How this file fits the app: /ws/shell hands the browser a real shell (inside the Docker sandbox, or on the
# host). That is remote code execution for whoever can open the socket, and browsers do NOT apply CORS to
# WebSockets, so any web page open in the same browser could connect to ws://127.0.0.1:8000/ws/shell. The
# functions here are the checks main.py runs before it spawns anything:
#   1. Origin check   - a browser always sends the page's Origin on a WebSocket handshake; non-local ones are
#                       refused (is_local_origin).
#   2. Host check     - defeats DNS rebinding, where a hostile domain resolves to 127.0.0.1 and the Origin then
#                       looks "same site" (is_loopback_host).
#   3. Token          - a random per-run secret the legitimate client fetches from /api/shell-token (itself
#                       guarded by the two checks above) and sends as the first frame; compared in constant
#                       time (token_matches).
#   4. Host-shell opt-in - without Docker the endpoint used to silently fall back to bash on the host; that
#                       now requires ZEUS_ALLOW_HOST_SHELL=1 (host_shell_allowed).
# Kept free of fastapi imports so tests/test_shell_guard.py can exercise it without installing the server's
# dependencies.
# Environment: ZEUS_SHELL_TOKEN (optional fixed token, at least 16 characters, for scripted clients) and
# ZEUS_ALLOW_HOST_SHELL ("1" to permit the host-bash fallback).
# Known limit: this protects against other web pages and other machines, not against another local process
# running as the same user (such a process can already run anything the shell could).

import hmac
import os
import secrets
from urllib.parse import urlparse

# Minimum accepted length for an operator-supplied ZEUS_SHELL_TOKEN: shorter values are guessable by a local
# attacker making many handshakes, so they are ignored (with a random token used instead).
MIN_ENV_TOKEN_LENGTH = 16

# Host names that mean "this machine". "[::1]" is how urlparse/Host headers spell the IPv6 loopback with
# brackets, "::1" is what urlparse(...).hostname returns without them.
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _load_token():
    """Chooses the per-run shell token.

    Returns:
        str: ZEUS_SHELL_TOKEN when set and long enough, otherwise a fresh 256-bit URL-safe random string.
        A fresh value per server start means a token leaked from an old run is useless.
    """
    configured = os.environ.get("ZEUS_SHELL_TOKEN", "")
    if len(configured) >= MIN_ENV_TOKEN_LENGTH:
        return configured
    return secrets.token_urlsafe(32)


# Module-level so every request in this process compares against the same value; regenerated on restart.
SHELL_TOKEN = _load_token()


def _hostname(value):
    """Extracts the lower-cased host name from an Origin value or a Host header.

    Args:
        value: "http://127.0.0.1:5173", "localhost:8000", "[::1]:8000" ... (scheme optional).

    Returns:
        str or None: host name without port or brackets; None when it cannot be parsed.
    """
    if not value:
        return None
    # urlparse only fills .hostname when a scheme/"//" is present, so bare Host headers get one added.
    text = value if "//" in value else "//" + value
    try:
        host = urlparse(text).hostname
    except ValueError:
        return None
    return host.lower() if host else None


def is_local_origin(origin):
    """Decides whether a WebSocket/HTTP Origin header names a loopback page.

    Args:
        origin: raw Origin header, or None when the client sent none.

    Returns:
        bool: True for a missing Origin (non-browser clients such as curl send none; they still need the
        token, and a browser always sends one) and for http(s) origins on 127.0.0.1, localhost or ::1 (any
        port: the Vite dev server on 5173 and the game on 8000 both qualify). False for anything else,
        including the literal "null" origin sent by sandboxed iframes and file:// pages.
    """
    if origin is None:
        return True
    origin = origin.strip()
    if origin == "" or origin.lower() == "null":
        return False
    # Only web schemes: "file://localhost/..." or "chrome-extension://127.0.0.1" must not pass on host alone.
    if not (origin.lower().startswith("http://") or origin.lower().startswith("https://")):
        return False
    return _hostname(origin) in LOOPBACK_HOSTS


def is_loopback_host(host_header):
    """Checks the HTTP Host header names a loopback address (DNS-rebinding defence).

    In a DNS-rebinding attack a hostile domain (evil.example) is made to resolve to 127.0.0.1, so the browser
    sends Host: evil.example:8000 to this server and the page's script talks to it as "same origin". Requiring
    a loopback Host header refuses every such request, whatever Origin the attacker's page claims.

    Args:
        host_header: raw Host header value or None.

    Returns:
        bool: True only when it names 127.0.0.1, localhost or ::1.
    """
    return _hostname(host_header) in LOOPBACK_HOSTS


def is_loopback_client(client_host):
    """True when the TCP peer is this machine (defence in depth next to the 127.0.0.1-only bind).

    Args:
        client_host: peer address string from the ASGI scope (websocket.client.host), or None.
    """
    return client_host in LOOPBACK_HOSTS or (client_host or "").startswith("::ffff:127.")


def token_matches(candidate):
    """Constant-time comparison of a client-supplied token with SHELL_TOKEN.

    hmac.compare_digest avoids leaking, through response timing, how many leading characters were right.

    Args:
        candidate: text from the first WebSocket frame (may be None or non-string if the frame was binary).

    Returns:
        bool: True only for an exact match.
    """
    if not isinstance(candidate, str):
        return False
    return hmac.compare_digest(candidate.strip().encode("utf-8"), SHELL_TOKEN.encode("utf-8"))


def host_shell_allowed():
    """True when the operator explicitly allowed the host-bash fallback (ZEUS_ALLOW_HOST_SHELL=1).

    Read on every call (not cached at import) so tests and operators can flip it without a reload. Anything
    other than the exact string "1" means no.
    """
    return os.environ.get("ZEUS_ALLOW_HOST_SHELL") == "1"
