"""
Reusable Playwright helpers for testing the Descriptive Exams Streamlit app.

Streamlit renders widgets as CSS-hidden React components — native Playwright
locators fail. These helpers use data-testid selectors that Streamlit exposes.

Usage:
    python3 -c "
    import asyncio
    from scripts.streamlit_test_utils import run_smoke_test
    asyncio.run(run_smoke_test())
    "
"""

import asyncio
import subprocess
import time
from typing import Optional
from playwright.async_api import Page, Browser, async_playwright


# ── Server lifecycle ───────────────────────────────────────────────────────────

def start_server(port: int = 8501, log_path: str = "/tmp/streamlit_app.log") -> subprocess.Popen:
    """Start the Streamlit dev server. Returns the process handle."""
    import os, sys
    app_path = os.path.join(os.path.dirname(__file__), "..", "web", "app.py")
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", app_path,
         "--server.port", str(port), "--server.headless", "true"],
        stdout=open(log_path, "w"), stderr=subprocess.STDOUT,
    )
    time.sleep(4)
    return proc


def stop_server(proc: Optional[subprocess.Popen] = None) -> None:
    """Stop server by process or by pkill."""
    if proc:
        proc.terminate()
    subprocess.run(["pkill", "-f", "streamlit run"], capture_output=True)


# ── Navigation ─────────────────────────────────────────────────────────────────

async def navigate_to_page(page: Page, sidebar_label: str, wait_ms: int = 2000) -> None:
    """Click a sidebar navigation item by its exact label text."""
    await page.get_by_text(sidebar_label, exact=True).first.click()
    await page.wait_for_timeout(wait_ms)


async def click_tab(page: Page, tab_name: str, wait_ms: int = 2000) -> None:
    """Click a Streamlit tab. Uses get_by_role to avoid strict-mode conflicts
    (tab name appears in both sidebar and tab bar)."""
    await page.get_by_role("tab", name=tab_name).click()
    await page.wait_for_timeout(wait_ms)


# ── Form interaction ───────────────────────────────────────────────────────────

async def answer_radio_groups(
    page: Page,
    option_idx: int = 0,
    skip_groups: int = 0,
) -> int:
    """
    Select one option in every stRadio group on the page.

    Args:
        option_idx: Which option to select (0 = first, 1 = second, …)
        skip_groups: Number of radio groups to skip from the start
                     (use to skip mode-selector radios if any)

    Returns:
        Number of groups successfully answered.
    """
    # Scroll main content area to expose all form content
    await page.evaluate("""
        const main = document.querySelector('section.main') ||
                     document.querySelector('.main') ||
                     document.body;
        main.scrollTop = main.scrollHeight;
    """)
    await page.wait_for_timeout(400)

    groups = page.locator("[data-testid='stRadio']")
    total = await groups.count()
    answered = 0

    for i in range(skip_groups, total):
        group = groups.nth(i)
        label = group.locator("label").nth(option_idx)
        try:
            await label.click(timeout=5000)
            answered += 1
            await page.wait_for_timeout(80)
        except Exception:
            # Scroll the specific element into view via JS, then retry
            await page.evaluate(
                f"document.querySelectorAll('[data-testid=\"stRadio\"]')"
                f"[{i}]?.querySelector('label')?.scrollIntoView({{block:'center'}})"
            )
            await page.wait_for_timeout(200)
            try:
                await label.click(timeout=3000)
                answered += 1
            except Exception:
                pass  # form still rendering — skip

    return answered


async def click_selectbox(page: Page, idx: int, option_text: str) -> None:
    """Open the idx-th Streamlit selectbox and pick an option by text.

    Do NOT use page.locator("select").select_option() — Streamlit uses
    a custom React dropdown, not a native <select>.
    """
    box = page.locator("[data-testid='stSelectbox']").nth(idx)
    await box.click()
    await page.wait_for_timeout(300)
    await page.get_by_role("option", name=option_text).click()
    await page.wait_for_timeout(200)


async def submit_form(page: Page, button_text: str, wait_ms: int = 5000) -> None:
    """Click a form submit button and wait for Streamlit to re-render."""
    await page.get_by_role("button", name=button_text).click()
    await page.wait_for_timeout(wait_ms)


# ── Result verification ────────────────────────────────────────────────────────

async def check_for_errors(page: Page) -> list[str]:
    """Return list of error indicators found in the page HTML. Empty = clean."""
    body = await page.content()
    found = []
    if "KeyError" in body:
        found.append("KeyError")
    if "Traceback" in body:
        found.append("Traceback")
    if "AttributeError" in body:
        found.append("AttributeError")
    if "NameError" in body:
        found.append("NameError")
    return found


async def get_expander_count(page: Page) -> int:
    """Return number of open/closed <details> expanders on the page."""
    return await page.locator("details").count()


async def open_expander(page: Page, idx: int = 0) -> None:
    """Open the idx-th expander."""
    await page.locator("details").nth(idx).click()
    await page.wait_for_timeout(500)


async def page_contains(page: Page, text: str) -> bool:
    """Check if the page body contains a given string."""
    body = await page.content()
    return text in body


# ── Full smoke test ────────────────────────────────────────────────────────────

async def run_smoke_test(port: int = 8501, headless: bool = True) -> dict:
    """
    Smoke-test every page in the app. Returns a dict of page → pass/fail/errors.

    Does NOT start the server — assumes it is already running on the given port.
    """
    results = {}

    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        base_url = f"http://localhost:{port}"

        await page.goto(base_url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        pages_to_test = [
            ("app", None),
            ("Model Answers", None),
            ("Quiz", None),
            ("Study Brief", None),
            ("My Progress", None),
            ("Return Quiz", None),
            ("RBI Prep", None),
        ]

        for label, _ in pages_to_test:
            try:
                if label == "app":
                    await page.goto(base_url, wait_until="networkidle", timeout=20000)
                    await page.wait_for_timeout(2000)
                else:
                    await navigate_to_page(page, label)

                errors = await check_for_errors(page)
                await page.screenshot(path=f"/tmp/smoke_{label.replace(' ', '_')}.png")
                results[label] = {"status": "FAIL" if errors else "PASS", "errors": errors}
            except Exception as exc:
                results[label] = {"status": "ERROR", "errors": [str(exc)]}

        # RBI Prep — test all 4 tabs
        try:
            await navigate_to_page(page, "RBI Prep")
            for tab in ["Key Data", "Phase 1 Drill", "Tier 2 Quiz", "My Progress"]:
                await click_tab(page, tab)
                errors = await check_for_errors(page)
                key = f"RBI/{tab}"
                results[key] = {"status": "FAIL" if errors else "PASS", "errors": errors}
                await page.screenshot(path=f"/tmp/smoke_rbi_{tab.replace(' ', '_')}.png")
        except Exception as exc:
            results["RBI/tabs"] = {"status": "ERROR", "errors": [str(exc)]}

        await browser.close()

    return results


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    results = asyncio.run(run_smoke_test())
    print("\n=== Smoke Test Results ===")
    for page_name, result in results.items():
        status = result["status"]
        marker = "✅" if status == "PASS" else "❌"
        print(f"{marker} {page_name}: {status}", end="")
        if result["errors"]:
            print(f"  → {result['errors']}", end="")
        print()
