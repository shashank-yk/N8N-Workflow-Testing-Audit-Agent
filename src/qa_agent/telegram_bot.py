from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from .db import get_latest_report, get_report, save_report
from .qa_flow import QaFlow


def build_dispatcher(flow: QaFlow) -> Dispatcher:
    dispatcher = Dispatcher()

    @dispatcher.message(Command("start"))
    async def start(message: Message) -> None:
        logging.info("Received /start from chat_id=%s", message.chat.id)
        await message.answer("Ready. Use: test <workflow name> or report latest")

    @dispatcher.message(F.text.startswith("test "))
    async def test_workflow(message: Message) -> None:
        logging.info("Received test command from chat_id=%s", message.chat.id)
        workflow_name = message.text.removeprefix("test ").strip()
        await message.answer(f"Testing {workflow_name} now...")
        report = await flow.run(workflow_name)
        save_report(report)
        await message.answer(report.to_markdown())

    @dispatcher.message(F.text.startswith("report "))
    async def report(message: Message) -> None:
        logging.info("Received report command from chat_id=%s", message.chat.id)
        query = message.text.removeprefix("report ").strip()
        record = get_latest_report() if query == "latest" else get_report(query)
        if not record:
            await message.answer("No report found.")
            return
        await message.answer(record.report_markdown)

    return dispatcher


async def run_bot(bot: Bot, dispatcher: Dispatcher) -> None:
    await dispatcher.start_polling(bot)
