import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "docs/screenshots"
out.mkdir(parents=True, exist_ok=True)
report = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/chromium", headless=True, args=["--no-sandbox"])
    page = b.new_page(timezone_id="Asia/Kolkata")
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    for dark in [False, True]:
        page.emulate_media(color_scheme="dark" if dark else "light", reduced_motion="reduce")
        for width in [360, 390, 768, 1024, 1280, 1536]:
            page.set_viewport_size({"width": width, "height": 1000})
            page.goto("http://127.0.0.1:8000/")
            page.get_by_role("button", name="Tax threshold", exact=True).click()
            page.get_by_role("button", name="Check freshness", exact=True).click()
            page.get_by_role("heading", name="0 of 1 checked claims are still true").wait_for()
            assert page.get_by_role("status").filter(has_text="MOCK DATA").is_visible()
            overflow = page.evaluate("document.documentElement.scrollWidth > innerWidth")
            assert not overflow, f"Overflow {width} dark={dark}"
            page.evaluate("window.scrollTo(0,0)")
            page.screenshot(
                path=str(out / f"check-{width}-{'dark' if dark else 'light'}.png"), full_page=True
            )
            report.append(
                {
                    "width": width,
                    "theme": "dark" if dark else "light",
                    "overflow": overflow,
                    "mock_run": "complete",
                }
            )
    # keyboard: focus skip link and reach form without a mouse
    page.goto("http://127.0.0.1:8000/")
    page.keyboard.press("Tab")
    assert page.get_by_role("link", name="Skip to content").evaluate(
        "e=>e===document.activeElement"
    )
    page.keyboard.press("Enter")
    for _ in range(15):
        page.keyboard.press("Tab")
        if page.locator("#answer").evaluate("e=>e===document.activeElement"):
            break
    assert page.locator("#answer").evaluate("e=>e===document.activeElement")
    page.keyboard.type("The allowance is 100 units.")
    page.get_by_role("button", name="Check freshness", exact=True).focus()
    page.keyboard.press("Enter")
    page.get_by_role("heading", name="0 of 1 checked claims are still true").wait_for()
    for route, heading in [
        ("/demo", "An answer. With evidence."),
        ("/benchmark", "Benchmark"),
        ("/developers", "Freshness, in your flow."),
        ("/limits", "Useful evidence."),
        ("/how-it-works", "Trust the evidence."),
        ("/missing", "Page not found"),
    ]:
        page.goto("http://127.0.0.1:8000" + route)
        page.get_by_role("heading", level=1).wait_for()
        assert heading in page.get_by_role("heading", level=1).inner_text().replace("\n", " ")
    assert not errors, errors
    b.close()
Path("/tmp/stilltrue-browser-report.json").write_text(
    json.dumps(
        {
            "layouts": report,
            "page_errors": errors,
            "keyboard": "passed",
            "reduced_motion": "enabled",
        },
        indent=2,
    )
)
print("12 responsive/theme mock runs, routes, keyboard and reduced motion passed; no page errors")
