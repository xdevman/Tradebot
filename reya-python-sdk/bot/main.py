
import asyncio
from os import getenv
from tracemalloc import BaseFilter
from aiogram import types
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from bot.utils.validators import admin_only
from dotenv import load_dotenv
from bot.handlers import trade, account
from bot.handlers.trades import long, limit, short, close_position

load_dotenv()

TOKEN = getenv("BOT_TOKEN")

telegram_userid = int(getenv("TID"))
dp = Dispatcher()



dp.include_router(long.long_router)
dp.include_router(short.short_router)
dp.include_router(account.account_router)
dp.include_router(limit.limit_router)
dp.include_router(close_position.close_router)


# async def is_admin(message: Message) -> bool:
#     return message.from_user.id == telegram_userid


@dp.message(Command("start"))
@admin_only
async def start_handler(message: types.Message):
    
    await message.answer("welcome. for more information use /help command")
    
@dp.message(Command("help"))
@admin_only
async def start_handler(message: types.Message):
    
    await message.answer("Available commands:\n /long <ticker> <amount> - Open a long position\n /short <ticker> <amount> - Open a short position\n /limit <ticker> <side> <amount> <price> - Place a limit order\n /account - View account details")

# Run the bot
async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    # client = asyncio.run(create_client())
    # order_id = asyncio.run(set_long_order(client))
    # print("test", order_id)