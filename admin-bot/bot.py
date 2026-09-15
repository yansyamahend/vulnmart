import asyncio
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)


# ============================================================
# Configuration
# ============================================================

APP_BROWSER_URL = os.getenv(
    "APP_BROWSER_URL",
    "http://vulnmart:8000",
).rstrip("/")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

BOT_TRIGGER_SECRET = os.getenv(
    "BOT_TRIGGER_SECRET",
    "change-this-secret",
)

REVIEW_WAIT_SECONDS = int(
    os.getenv("REVIEW_WAIT_SECONDS", "5")
)


# ============================================================
# Global state
# ============================================================

playwright_instance: Optional[Playwright] = None
browser: Optional[Browser] = None
context: Optional[BrowserContext] = None
worker_task: Optional[asyncio.Task] = None

review_queue: asyncio.Queue[int] = asyncio.Queue()


# ============================================================
# Browser helpers
# ============================================================

async def get_admin_page() -> Page:
    if context is None:
        raise RuntimeError("Browser context is not initialized")

    return await context.new_page()


# ============================================================
# Admin login
# ============================================================

async def login_admin() -> None:
    """
    Login through the VulnMart API from inside a browser page.

    Flow:

        /login
          |
          v
        POST /api/auth/login
          |
          v
        access_token
          |
          v
        localStorage.access_token
          |
          v
        POST /api/auth/set-session
        application/x-www-form-urlencoded
          |
          v
        HttpOnly access_token cookie
          |
          v
        /admin
    """

    print("[BOT] Logging in as admin...")

    page = await get_admin_page()

    try:
        # ----------------------------------------------------
        # Load login page so the fetch happens in the same
        # browser origin as VulnMart.
        # ----------------------------------------------------

        await page.goto(
            f"{APP_BROWSER_URL}/login",
            wait_until="domcontentloaded",
        )

        print("[BOT] Login page loaded")

        # ----------------------------------------------------
        # Login API
        # ----------------------------------------------------

        login_result = await page.evaluate(
            """
            async ({ username, password }) => {
                const response = await fetch(
                    "/api/auth/login",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            username: username,
                            password: password
                        })
                    }
                );

                const text = await response.text();

                let data;

                try {
                    data = JSON.parse(text);
                } catch {
                    data = {
                        raw: text
                    };
                }

                return {
                    status: response.status,
                    ok: response.ok,
                    data: data
                };
            }
            """,
            {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
            },
        )

        print(
            f"[BOT] Login API status: "
            f"{login_result['status']}"
        )

        if not login_result["ok"]:
            raise RuntimeError(
                "Admin API login failed: "
                f"{login_result['data']}"
            )

        login_data = login_result["data"]

        token = login_data.get("access_token")

        if not token:
            raise RuntimeError(
                "Login succeeded but access_token "
                f"was missing: {login_data}"
            )

        print("[BOT] access_token received")

        # ----------------------------------------------------
        # Store JWT exactly like login.html does.
        # ----------------------------------------------------

        await page.evaluate(
            """
            token => {
                localStorage.setItem(
                    "access_token",
                    token
                );
            }
            """,
            token,
        )

        print("[BOT] access_token stored in localStorage")

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # /api/auth/set-session uses:
        #
        #     token: str = Form(...)
        #
        # so we MUST send:
        #
        # Content-Type:
        # application/x-www-form-urlencoded
        #
        # body:
        # token=<JWT>
        # ----------------------------------------------------

        session_result = await page.evaluate(
            """
            async (token) => {
                const body = new URLSearchParams();

                body.set("token", token);

                const response = await fetch(
                    "/api/auth/set-session",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type":
                                "application/x-www-form-urlencoded"
                        },
                        body: body.toString()
                    }
                );

                return {
                    status: response.status,
                    text: await response.text()
                };
            }
            """,
            token,
        )

        print(
            "[BOT] Session bridge status: "
            f"{session_result['status']}"
        )

        if session_result["status"] != 200:
            raise RuntimeError(
                "set-session failed: "
                f"{session_result}"
            )

        print("[BOT] HttpOnly session cookie established")

        # ----------------------------------------------------
        # Verify actual server-side session.
        # ----------------------------------------------------

        await page.goto(
            f"{APP_BROWSER_URL}/admin",
            wait_until="networkidle",
        )

        print(
            f"[BOT] Admin verification URL: "
            f"{page.url}"
        )

        if page.url.rstrip("/").endswith("/login"):
            raise RuntimeError(
                "Admin session verification failed: "
                "redirected to /login"
            )

        print("[BOT] Admin login successful")
        print("[BOT] Admin session verified")

    finally:
        await page.close()


# ============================================================
# Review user
# ============================================================

async def review_user(user_id: int) -> None:
    """
    Open the admin user's profile using the authenticated
    browser session.
    """

    if context is None:
        raise RuntimeError(
            "Browser context is not initialized"
        )

    print(f"[BOT] Reviewing user {user_id}")

    page = await context.new_page()

    # --------------------------------------------------------
    # Debug hooks
    # --------------------------------------------------------

    def on_console(message):
        try:
            print(
                f"[BOT][CONSOLE][{message.type}] "
                f"{message.text}"
            )
        except Exception:
            pass

    def on_page_error(error):
        print(
            f"[BOT][PAGE ERROR] {error}"
        )

    page.on("console", on_console)
    page.on("pageerror", on_page_error)

    try:
        target_url = (
            f"{APP_BROWSER_URL}/admin/users/{user_id}"
        )

        print(
            f"[BOT] Opening {target_url}"
        )

        await page.goto(
            target_url,
            wait_until="networkidle",
        )

        print(
            f"[BOT] Page URL: {page.url}"
        )

        print(
            f"[BOT] Page title: "
            f"{await page.title()}"
        )

        # ----------------------------------------------------
        # If the admin session expired, log in again once.
        # ----------------------------------------------------

        if page.url.rstrip("/").endswith("/login"):
            print(
                "[BOT] Session expired, "
                "logging in again..."
            )

            await page.close()

            await login_admin()

            page = await context.new_page()

            page.on("console", on_console)
            page.on("pageerror", on_page_error)

            print(
                f"[BOT] Retrying {target_url}"
            )

            await page.goto(
                target_url,
                wait_until="networkidle",
            )

            print(
                f"[BOT] Retry URL: {page.url}"
            )

        # ----------------------------------------------------
        # Final check.
        # ----------------------------------------------------

        if page.url.rstrip("/").endswith("/login"):
            raise RuntimeError(
                "Admin session still invalid "
                "after re-login"
            )

        print(
            f"[BOT] Page loaded for user {user_id}"
        )

        # ----------------------------------------------------
        # Keep page alive so XSS / scripts / external
        # callbacks have time to execute.
        # ----------------------------------------------------

        if REVIEW_WAIT_SECONDS > 0:
            print(
                f"[BOT] Waiting "
                f"{REVIEW_WAIT_SECONDS}s "
                f"for page activity..."
            )

            await page.wait_for_timeout(
                REVIEW_WAIT_SECONDS * 1000
            )

        print(
            f"[BOT] Finished reviewing user {user_id}"
        )

    except Exception as exc:
        print(
            f"[BOT] Review error for user "
            f"{user_id}: {exc}"
        )

        raise

    finally:
        try:
            await page.close()
        except Exception:
            pass


# ============================================================
# Review worker
# ============================================================

async def review_worker() -> None:
    print("[BOT] Review worker started")

    while True:
        user_id = await review_queue.get()

        try:
            print(
                f"[BOT] Worker picked user {user_id}"
            )

            await review_user(user_id)

        except asyncio.CancelledError:
            raise

        except Exception as exc:
            print(
                f"[BOT] Worker error for user "
                f"{user_id}: {exc}"
            )

        finally:
            review_queue.task_done()


# ============================================================
# FastAPI lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global playwright_instance
    global browser
    global context
    global worker_task

    print("[BOT] Starting Playwright...")

    playwright_instance = await async_playwright().start()

    browser = await playwright_instance.chromium.launch(
        headless=True,
    )

    context = await browser.new_context(
        ignore_https_errors=True,
        viewport={
            "width": 1280,
            "height": 900,
        },
    )

    try:
        # ----------------------------------------------------
        # Authenticate before accepting jobs.
        # ----------------------------------------------------

        await login_admin()

        print("[BOT] Admin bot ready")

        # ----------------------------------------------------
        # Start review worker.
        # ----------------------------------------------------

        worker_task = asyncio.create_task(
            review_worker()
        )

        yield

    finally:
        print("[BOT] Shutting down...")

        # ----------------------------------------------------
        # Stop worker.
        # ----------------------------------------------------

        if worker_task is not None:
            worker_task.cancel()

            try:
                await worker_task
            except asyncio.CancelledError:
                pass

            worker_task = None

        # ----------------------------------------------------
        # Close browser resources.
        # ----------------------------------------------------

        if context is not None:
            try:
                await context.close()
            except Exception:
                pass

            context = None

        if browser is not None:
            try:
                await browser.close()
            except Exception:
                pass

            browser = None

        if playwright_instance is not None:
            try:
                await playwright_instance.stop()
            except Exception:
                pass

            playwright_instance = None

        print("[BOT] Shutdown complete")


# ============================================================
# FastAPI
# ============================================================

app = FastAPI(
    title="VulnMart Admin Bot",
    lifespan=lifespan,
)


# ============================================================
# Health
# ============================================================

@app.get("/")
async def health():
    return {
        "status": "ok",
        "service": "vulnmart-admin-bot",
        "queue_size": review_queue.qsize(),
    }


# ============================================================
# Review endpoint
# ============================================================

@app.post("/review")
async def trigger_review(
    user_id: int,
    x_bot_secret: Optional[str] = Header(
        default=None,
        alias="X-Bot-Secret",
    ),
):
    if x_bot_secret != BOT_TRIGGER_SECRET:
        raise HTTPException(
            status_code=403,
            detail="Forbidden",
        )

    if context is None:
        raise HTTPException(
            status_code=503,
            detail="Browser is not ready",
        )

    await review_queue.put(user_id)

    print(
        f"[BOT] Queued review for user {user_id}"
    )

    return {
        "status": "queued",
        "user_id": user_id,
        "queue_size": review_queue.qsize(),
    }