from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from fluentogram import TranslatorRunner
from src.utils.db import AsyncORM

router = Router()


@router.message(Command("start"))
async def _(
    message: Message,
    bot: Bot,
    db: AsyncORM,
    locale: TranslatorRunner,
):
    await message.answer(locale.welcome_text())
