
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
    
    await message.answer("""
📌 Bot Commands - ADMIN ONLY

/long <ticker> <amount>  
Open a long position on a token.  
- <ticker>: Symbol of the token (e.g., OP, BTC)  
- <amount>: Size in tokens to open the position (e.g., 500)  
You can also just type /long and set ticker & amount step by step.

/short <ticker> <amount>  
Open a short position on a token.  
- <ticker>: Symbol of the token (e.g., OP, BTC)  
- <amount>: Size in tokens to open the position (e.g., 500)  
You can also just type /short and set ticker & amount step by step.

/limit <ticker> <side> <amount> <price>  
Open a limit order (GTC) for a token.  
- <ticker>: Symbol of the token (e.g., OP, BTC)  
- <side>: 'long' or 'short'  
- <amount>: Size in tokens  
- <price>: Limit price to execute the order  
You can also type /limit and fill each field step by step.

/close <ticker>  
Close an active position on a token.  
- <ticker>: Symbol of the token you want to close.  
This will automatically use the reverse size to close your position.

⚠️ Only admins can use these commands.
""")
# Run the bot
async def main() -> None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    # client = asyncio.run(create_client())
    # order_id = asyncio.run(set_long_order(client))
    # print("test", order_id)