from __future__ import annotations

import asyncio
import logging

from aiogram import Bot

from .browser_client import BrowserClient
from .config import settings
from .db import init_db
from .llm import build_llm
from .n8n_client import N8nClient
from .qa_flow import QaFlow
from .telegram_bot import build_dispatcher, run_bot


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    print("Starting QA agent...", flush=True)
    print("Checking database...", flush=True)
    init_db()
    print("Database OK.", flush=True)
    n8n_client = N8nClient()
    try:
        print("Checking model provider...", flush=True)
        llm = build_llm()
        print("Model provider OK.", flush=True)
        flow = QaFlow(n8n_client=n8n_client, browser_client=BrowserClient(), llm=llm)
        bot = Bot(token=settings.telegram_bot_token)
        print("Checking Telegram bot token...", flush=True)
        me = await asyncio.wait_for(bot.get_me(), timeout=20)
        print(f"Telegram bot connected: @{me.username}", flush=True)
        print("Waiting for Telegram messages...", flush=True)
        dispatcher = build_dispatcher(flow)
        await run_bot(bot, dispatcher)
    finally:
        await n8n_client.close()


if __name__ == "__main__":
    asyncio.run(main())
