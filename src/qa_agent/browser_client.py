from __future__ import annotations

import logging
import re
from pathlib import Path

from playwright.async_api import Page, async_playwright

from .config import settings


class BrowserClient:
    def screenshot_path(self, run_id: str, role: str) -> Path:
        return settings.screenshot_dir / f"{run_id}-{role}.png"

    async def capture_workflow_screenshot(self, workflow_id: str, run_id: str, role: str) -> str:
        settings.screenshot_dir.mkdir(parents=True, exist_ok=True)
        path = self.screenshot_path(run_id=run_id, role=role)
        url = settings.n8n_base_url + settings.n8n_workflow_page_template.format(workflow_id=workflow_id)
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1600, "height": 1000})
            page.set_default_timeout(60_000)
            await self._open_workflow_page(page, url)
            await page.screenshot(path=str(path), full_page=True)
            await browser.close()
        return str(Path(path))

    async def execute_manual_workflow(self, workflow_id: str, screenshot_path: Path | None = None) -> None:
        url = settings.n8n_base_url + settings.n8n_workflow_page_template.format(workflow_id=workflow_id)
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1600, "height": 1000})
            page.set_default_timeout(60_000)
            await self._open_workflow_page(page, url)
            if screenshot_path:
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=str(screenshot_path), full_page=True)
            await self._click_execute_workflow(page)
            await page.wait_for_timeout(8000)
            await browser.close()

    async def _open_workflow_page(self, page: Page, url: str) -> None:
        await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        await self._login_if_needed(page)
        await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        try:
            await page.wait_for_load_state("networkidle", timeout=30_000)
        except Exception:
            logging.info("n8n workflow page did not reach networkidle before timeout.")
        await self._wait_for_workflow_editor(page)
        logging.info("n8n workflow page loaded; current browser URL is %s, title is %r", page.url, await page.title())

    async def _wait_for_workflow_editor(self, page: Page) -> None:
        editor_ready_selector = ", ".join(
            [
                'button:has-text("Execute workflow")',
                'button:has-text("Execute Workflow")',
                'button:has-text("Test workflow")',
                'button:has-text("Test Workflow")',
                '[role="button"]:has-text("Execute workflow")',
                '[role="button"]:has-text("Execute Workflow")',
                '[role="button"]:has-text("Test workflow")',
                '[role="button"]:has-text("Test Workflow")',
                '[aria-label*="Execute"]',
                '[aria-label*="Test"]',
                '[data-test-id*="canvas"]',
                '[class*="node-view"]',
            ]
        )
        try:
            await page.wait_for_selector(editor_ready_selector, state="visible", timeout=90_000)
        except Exception:
            logging.warning("n8n workflow editor controls were not visible after waiting.")
        await page.wait_for_timeout(2000)

    async def _login_if_needed(self, page: Page) -> None:
        if not settings.n8n_username or not settings.n8n_password:
            logging.warning("n8n login skipped because N8N_USERNAME or N8N_PASSWORD is empty.")
            return
        try:
            await page.wait_for_selector("input", state="visible", timeout=15_000)
        except Exception:
            return
        email_input = page.get_by_label("Email").or_(
            page.locator(
                'input[type="email"], '
                'input[name="email"], '
                'input[autocomplete="username"], '
                'input[placeholder*="email" i], '
                'input[id*="email" i]'
            )
        ).first
        password_input = page.get_by_label("Password").or_(
            page.locator(
                'input[type="password"], '
                'input[name="password"], '
                'input[autocomplete="current-password"], '
                'input[placeholder*="password" i], '
                'input[id*="password" i]'
            )
        ).first
        if await email_input.count() == 0:
            email_input = page.locator("input:visible").first
        if await password_input.count() == 0:
            password_input = page.locator('input[type="password"]:visible').first
        if await email_input.count() == 0 or await password_input.count() == 0:
            logging.warning("n8n login form was visible, but email/password fields were not found.")
            return
        await email_input.fill(settings.n8n_username)
        await password_input.fill(settings.n8n_password)
        sign_in_button = page.locator('button[type="submit"]').or_(
            page.get_by_role("button", name="Sign in")
        ).first
        if await sign_in_button.count() == 0:
            logging.warning("n8n login fields were filled, but the sign-in button was not found.")
            return
        await sign_in_button.click()
        await page.wait_for_load_state("domcontentloaded")
        for _ in range(20):
            if "/signin" not in page.url:
                break
            await page.wait_for_timeout(1000)
        logging.info("n8n login attempted; current browser URL is %s", page.url)

    async def _click_execute_workflow(self, page: Page) -> None:
        if "/signin" in page.url:
            raise RuntimeError(
                "n8n login did not complete; still on the sign-in page. "
                "Check N8N_USERNAME and N8N_PASSWORD in .env by logging into n8n manually with the same values."
            )
        role_button = page.get_by_role("button", name=re.compile(r"(execute|test)\s+workflow", re.I)).first
        try:
            await role_button.wait_for(state="visible", timeout=60_000)
            await role_button.click()
            return
        except Exception:
            pass
        selectors = [
            'button:has-text("Execute workflow")',
            'button:has-text("Execute Workflow")',
            'button:has-text("Test workflow")',
            'button:has-text("Test Workflow")',
            '[role="button"]:has-text("Execute workflow")',
            '[role="button"]:has-text("Execute Workflow")',
            '[role="button"]:has-text("Test workflow")',
            '[role="button"]:has-text("Test Workflow")',
            '[aria-label*="Execute"]',
            '[aria-label*="Test"]',
        ]
        for selector in selectors:
            locator = page.locator(selector).first
            try:
                await locator.wait_for(state="visible", timeout=10_000)
                await locator.click()
                return
            except Exception:
                continue
        raise RuntimeError("Could not find the Execute Workflow button in n8n UI.")
