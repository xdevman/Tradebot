
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.core.reya.positions import create_client


account_router = Router()

@account_router.message(Command("positions"))
async def positions_handler(message: Message):
    
    await message.answer("list of postions")

@account_router.message(Command("orders"))
async def orders_handler(message: Message):
    client = await create_client()
    print("\n--- Getting open orders ---")
    open_orders = await client.get_open_orders()
    print(f"Open orders: {open_orders}")
    await message.answer(f"list of orders\n {open_orders}")