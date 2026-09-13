import asyncio
import os
import asyncio
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Header, HTTPException, Query
from playwright.async_api import async_playwright


# =========================================================
# CONFIG
# =========================================================

APP_API_URL = os.getenv(
    "APP_API_URL",
    "http://vulnmart:8000",
).rstrip("/")

APP_BROWSER_URL = os.getenv(
    "APP_BROWSER_URL",
    "http://host.docker.internal:8000",
).rstrip("/")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

BOT_TRIGGER_SECRET = os.getenv(
    "BOT_TRIGGER_SECRET",
    "vulnmart-bot-local-secret",
)

REVIEW_WAIT_SECONDS = int(
    os.getenv("REVIEW_WAIT_SECONDS", "5")
)


# =========================================================
# GLOBAL STATE
# =========================================================

playwright = None
browser = None
context = None
page = None

review_queue: asyncio.Queue[int] = asyncio.Queue()
worker_task = None


# =========================================================
# ADMIN LOGIN
# =========================================================

async def login_admin():
    global context
    global page

    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        raise RuntimeError(
            "ADMIN_USERNAME / ADMIN_PASSWORD belum diset"
        )

    print("[BOT] Logging in as admin...")

    async with httpx.AsyncClient(timeout=10.0) as client:

        response = await client.post(
            f"{APP_API_URL}/api/auth/login",
            json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
            },
        )

        response.raise_for_status()

        data = response.json()

    token = data.get("access_token")

    if not token:
        raise RuntimeError(
            f"Login response tidak memiliki access_token: {data}"
        )

    print("[BOT] API login successful")

    # -----------------------------------------------------
    # Buat browser page
    # -----------------------------------------------------

    page = await context.new_page()

    # Browser harus membuka origin yang memang bisa
    # dijangkau dari container browser.
    await page.goto(
        APP_BROWSER_URL,
        wait_until="domcontentloaded",
    )

    # -----------------------------------------------------
    # Simpan JWT ke localStorage
    # -----------------------------------------------------

    await page.evaluate(
        """
        token => {
            localStorage.setItem("access_token", token);
        }
        """,
        token,
    )

    print("[BOT] Admin session injected")

    # -----------------------------------------------------
    # Set cookie juga
    # -----------------------------------------------------

    await context.add_cookies(
        [
            {
                "name": "access_token",
                "value": token,
                "url": APP_BROWSER_URL,
                "httpOnly": True,
                "secure": False,
                "sameSite": "Lax",
            }
        ]
    )

    print("[BOT] Admin login successful")


# =========================================================
# REVIEW USER
# =========================================================

async def review_user(user_id: int):
    global context

    print(f"[BOT] Reviewing user {user_id}")

    review_page = await context.new_page()

    try:

        target_url = (
            f"{APP_BROWSER_URL}/admin/users/{user_id}"
        )

        print(f"[BOT] Opening {target_url}")

        await review_page.goto(
            target_url,
            wait_until="networkidle",
        )

        print(
            f"[BOT] Page loaded for user {user_id}"
        )

        # Beri waktu XSS / JS untuk dieksekusi
        await review_page.wait_for_timeout(
            REVIEW_WAIT_SECONDS * 1000
        )

        print(
            f"[BOT] Finished reviewing user {user_id}"
        )

    except Exception as exc:

        print(
            f"[BOT] Review failed for user {user_id}: {exc}"
        )

    finally:

        await review_page.close()


# =========================================================
# QUEUE WORKER
# =========================================================

async def review_worker():
    print("[BOT] Review worker started")

    while True:
        user_id = await review_queue.get()

        print(f"[BOT] Worker picked user {user_id}")

        try:
            await review_user(user_id)

        except Exception as exc:
            print(
                f"[BOT] Worker error for user {user_id}: {exc}"
            )

        finally:
            review_queue.task_done()


# =========================================================
# FASTAPI LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    global playwright
    global browser
    global context
    global worker_task

    print("[BOT] Starting Playwright...")

    playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(
        headless=True
    )

    context = await browser.new_context()

    # Auto login admin
    await login_admin()

    # Start queue worker
    worker_task = asyncio.create_task(
        review_worker()
    )

    print("[BOT] Admin bot ready")

    try:

        yield

    finally:

        print("[BOT] Shutting down...")

        if worker_task:
            worker_task.cancel()

            try:
                await worker_task
            except asyncio.CancelledError:
                pass

        if context:
            await context.close()

        if browser:
            await browser.close()

        if playwright:
            await playwright.stop()


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="VulnMart Admin Review Bot",
    lifespan=lifespan,
)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
async def root():

    return {
        "status": "ok",
        "service": "vulnmart-admin-bot",
    }


# =========================================================
# REVIEW ENDPOINT
# =========================================================

@app.post("/review")
async def trigger_review(
    user_id: int = Query(...),
    x_bot_secret: str | None = Header(
        default=None,
        alias="X-Bot-Secret",
    ),
):

    if x_bot_secret != BOT_TRIGGER_SECRET:

        raise HTTPException(
            status_code=403,
            detail="Invalid bot secret",
        )

    await review_queue.put(user_id)

    print(
        f"[BOT] Queued review for user {user_id}"
    )

    return {
        "status": "queued",
        "user_id": user_id,
    }