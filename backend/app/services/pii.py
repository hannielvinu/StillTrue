import re

PATTERNS = [
    ("EMAIL", r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    ("PAN", r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    ("SSN", r"\b\d{3}-\d{2}-\d{4}\b"),
    ("AADHAAR", r"(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)"),
    ("PHONE", r"(?<!\d)(?:\+91[ -]?)?[6-9]\d{9}(?!\d)"),
    ("PHONE", r"(?<!\w)(?:\+\d{1,3}[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]\d{3}[ .-]\d{4}(?!\d)"),
]


def luhn(s: str) -> bool:
    digits = [int(c) for c in re.sub(r"\D", "", s)]
    return (
        13 <= len(digits) <= 19
        and sum(
            (n * 2 - 9 if n * 2 > 9 else n * 2) if i % 2 else n
            for i, n in enumerate(reversed(digits))
        )
        % 10
        == 0
    )


def scan(text: str, redact: bool = True) -> tuple[str, list[dict]]:
    matches = []
    for kind, pattern in [("CARD", r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"), *PATTERNS]:
        for m in re.finditer(pattern, text):
            if kind == "CARD" and not luhn(m.group()):
                continue
            if not any(m.start() < e and m.end() > s for s, e, _ in matches):
                matches.append((m.start(), m.end(), kind))
    masked = text
    for start, end, kind in sorted(matches, reverse=True):
        if redact:
            masked = masked[:start] + f"[{kind}]" + masked[end:]
    return masked, [{"kind": k, "start": s, "end": e} for s, e, k in sorted(matches)]
