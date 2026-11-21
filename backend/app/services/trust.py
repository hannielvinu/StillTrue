from pathlib import Path
from urllib.parse import urlsplit
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]

# Government and intergovernmental suffixes publish the rules themselves.
GOVERNMENT_SUFFIXES = (
    "gov",
    "mil",
    "gov.in",
    "nic.in",
    "gov.uk",
    "gc.ca",
    "canada.ca",
    "gov.au",
    "govt.nz",
    "europa.eu",
    "gov.sg",
    "go.jp",
    "gouv.fr",
    "bund.de",
    "gob.es",
    "gov.ie",
    "un.org",
)
# Never accepted as the "official publisher" of a fact, whatever the extractor says.
NOT_AUTHORITIES = (
    "wikipedia.org",
    "reddit.com",
    "quora.com",
    "medium.com",
    "substack.com",
    "x.com",
    "twitter.com",
    "facebook.com",
    "linkedin.com",
    "youtube.com",
    "stackoverflow.com",
    "github.io",
    "blogspot.com",
    "wordpress.com",
    "pricepertoken.com",
    "forbes.com",
    "investopedia.com",
    "nerdwallet.com",
    "cleartax.in",
    "google.com",
    "bing.com",
)
_HOST = re.compile(r"^(?=.{4,100}$)([a-z0-9-]+\.)+[a-z]{2,}$")


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


def matches(host: str, domains: list[str] | tuple[str, ...]) -> bool:
    return any(host == d or host.endswith("." + d) for d in domains)


def authority(value: str | None) -> str | None:
    """Normalise the extractor's 'official publisher' domain, or reject it."""
    if not value:
        return None
    host = value.strip().lower().removeprefix("https://").removeprefix("http://")
    host = host.split("/")[0].removeprefix("www.")
    if not _HOST.match(host) or matches(host, NOT_AUTHORITIES):
        return None
    return host


def official_domains(pack: dict, claim_authority: str | None = None) -> list[str]:
    extra = [claim_authority] if pack.get("allow_publisher_domain", True) else []
    return list(dict.fromkeys([d for d in [*extra, *pack["tier1_domains"]] if d]))


def tier(url: str, pack: dict, claim_authority: str | None = None) -> int:
    host = domain(url)
    if not host or matches(host, pack["blocked_domains"]):
        return 0
    if matches(host, official_domains(pack, claim_authority)):
        return 1
    if pack.get("allow_government", True) and matches(host, GOVERNMENT_SUFFIXES):
        return 1
    return 2 if matches(host, pack["tier2_domains"]) else 3
