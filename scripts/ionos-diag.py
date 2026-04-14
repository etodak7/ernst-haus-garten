"""
IONOS Developer API Diagnose-Tool.

Liest Credentials aus ../.env (nicht committed) und macht einen Auth-Test
gegen die IONOS Hosting API. Zeigt, welche Endpoints für den aktuellen
Key erreichbar sind und welche Zonen/Domains wir verwalten können.

Usage:
    python scripts/ionos-diag.py
    python scripts/ionos-diag.py --endpoint dns/v1/zones
    python scripts/ionos-diag.py --endpoint dns/v1/zones/<zone-id>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"
DEFAULT_BASE = "https://api.hosting.ionos.com"


def load_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def build_key(env: dict[str, str]) -> str:
    combined = env.get("IONOS_API_KEY", "").strip()
    if combined:
        return combined
    prefix = env.get("IONOS_API_KEY_PREFIX", "").strip()
    secret = env.get("IONOS_API_KEY_SECRET", "").strip()
    if not prefix or not secret:
        sys.exit("Fehlende Credentials in .env (PREFIX + SECRET).")
    return f"{prefix}.{secret}"


def request(base: str, endpoint: str, key: str, method: str = "GET",
            body: dict | None = None) -> tuple[int, object]:
    url = f"{base.rstrip('/')}/{endpoint.lstrip('/')}"
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, method=method, data=data)
    req.add_header("X-API-Key", key)
    req.add_header("Accept", "application/json")
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as exc:
        try:
            err = json.loads(exc.read() or b"null")
        except Exception:
            err = exc.reason
        return exc.code, err
    except urllib.error.URLError as exc:
        return 0, f"network error: {exc.reason}"


def show(title: str, code: int, payload: object) -> None:
    print(f"\n=== {title} ===")
    print(f"HTTP {code}")
    if isinstance(payload, (dict, list)):
        print(json.dumps(payload, indent=2, ensure_ascii=False)[:4000])
    else:
        print(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", help="Eigener Pfad, z. B. dns/v1/zones")
    parser.add_argument("--base", default=DEFAULT_BASE)
    args = parser.parse_args()

    env = load_env(ENV)
    key = build_key(env)
    print(f"base = {args.base}")
    print(f"key  = {key[:8]}...{key[-4:]} (len {len(key)})")

    if args.endpoint:
        code, payload = request(args.base, args.endpoint, key)
        show(args.endpoint, code, payload)
        return

    show("GET /dns/v1/zones", *request(args.base, "dns/v1/zones", key))


if __name__ == "__main__":
    main()
