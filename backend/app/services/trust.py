from pathlib import Path
from urllib.parse import urlsplit
import yaml

ROOT = Path(__file__).resolve().parents[1]


def packs() -> dict:
    return {p.stem: yaml.safe_load(p.read_text()) for p in (ROOT / "packs").glob("*.yaml")}


def domain(url: str) -> str:
    try:
        parsed = urlsplit(url)
        return (
            (parsed.hostname or "").lower()
            if parsed.scheme in ("http", "https") and not parsed.username
            else ""
        )
    except ValueError:
        return ""


def matches(host: str, domains: list[str]) -> bool:
    return any(host == d or host.endswith("." + d) for d in domains)


def tier(url: str, pack: dict) -> int:
    host = domain(url)
    if not host or matches(host, pack["blocked_domains"]):
        return 0
    if matches(host, pack["tier1_domains"]):
        return 1
    return 2 if matches(host, pack["tier2_domains"]) else 3
