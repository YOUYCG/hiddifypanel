"""Local Hiddify gateway settings shared by the web app and CLI renderer."""

from __future__ import annotations

import os
from urllib.parse import urlsplit


def _listen_port(name: str, default: int) -> int:
    value = os.environ.get(name, str(default)).strip()
    if not value.isascii() or not value.isdecimal() or len(value) > 5:
        raise ValueError(f"{name} must be a TCP/UDP port number")
    port = int(value)
    if port != default and (not 1024 <= port <= 65535 or port in {3306, 6379, 8181, 9000, 18081}):
        raise ValueError(f"{name} must be {default} or a non-reserved port from 1024 to 65535")
    return port


GATEWAY_CLIENT_HTTP_PORT = _listen_port("HIDDIFY_GATEWAY_HTTP_PORT", 80)
GATEWAY_CLIENT_TLS_PORT = _listen_port("HIDDIFY_GATEWAY_TLS_PORT", 443)
if GATEWAY_CLIENT_HTTP_PORT == GATEWAY_CLIENT_TLS_PORT:
    raise ValueError("Hiddify HTTP and TLS gateway ports must be different")


def domain_gateway_ports(http_port: int | None, tls_port: int | None) -> tuple[int, int]:
    """Resolve domain overrides, keeping standard and opposite gateway ports free of aliases."""
    reserved = {80, 443, GATEWAY_CLIENT_HTTP_PORT, GATEWAY_CLIENT_TLS_PORT}
    return (
        http_port if http_port and http_port not in reserved else GATEWAY_CLIENT_HTTP_PORT,
        tls_port if tls_port and tls_port not in reserved else GATEWAY_CLIENT_TLS_PORT,
    )


def panel_authority(host: str, *, tls: bool, port: int | None = None) -> str:
    """Supply a gateway port if the URL authority lacks an explicit port."""
    if urlsplit(f"//{host}").port is not None:
        return host
    if port is None:
        port = GATEWAY_CLIENT_TLS_PORT if tls else GATEWAY_CLIENT_HTTP_PORT
    return host if port == (443 if tls else 80) else f"{host}:{port}"
