from aiogram import Bot, Dispatcher,Router,F
from aiogram.types import Message,InlineKeyboardButton,InlineKeyboardMarkup,CallbackQuery
from aiogram import types
from aiogram.filters import Command,CommandObject,StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
# from bot.core.reya.positions import create_client, set_long_order
from bot.keyboards.inline_confirm import confirm_keyboard
from bot.states.trade_states import TradeStates, limit_States
trade_router = Router()


@trade_router.message(Command("close"))
async def close_handler(message: types.Message):
    
    await message.answer("close your postions")
    
@trade_router.message(Command("tp"))
async def tp_handler(message: types.Message):
    
    await message.answer("set takeprofit for active positions")

@trade_router.message(Command("sl"))
async def sl_handler(message: types.Message):
    
    await message.answer("set stoploss for active positions")
