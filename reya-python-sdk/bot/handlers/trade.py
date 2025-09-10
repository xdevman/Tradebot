from aiogram import Bot, Dispatcher,Router,F
from aiogram.types import Message,InlineKeyboardButton,InlineKeyboardMarkup,CallbackQuery
from aiogram import types
from aiogram.filters import Command,CommandObject,StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.core.reya.positions import create_client, set_long_order
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



@trade_router.message(TradeStates.waiting_for_ticker)
async def position_ticker(message: Message, state: FSMContext):
    ticker = message.text.strip().upper()
    if not ticker or len(ticker) > 15:
        await message.answer("❌ Invalid ticker. Try again (e.g., BTC).")
        return
    await state.update_data(ticker=ticker)
    await message.answer(f"Ticker set to: {ticker}\nNow send the amount in USD (e.g., 100).")
    await state.set_state(TradeStates.waiting_for_amount)
    return

@trade_router.message(TradeStates.waiting_for_amount)
async def position_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError("Amount must be positive.")
    except ValueError:
        await message.answer("❌ Invalid amount. Please send a positive number (e.g., 100).")
        return
    await state.update_data(amount=amount)
    data = await state.get_data()
    ticker = data.get("ticker")
    await message.answer(f"Amount set to: ${amount}\nPlease confirm opening a long position for {ticker} with amount ${amount} (yes/no).",reply_markup=confirm_keyboard())
    await state.set_state(TradeStates.waiting_for_confirmation)
    return

@trade_router.callback_query(TradeStates.waiting_for_confirmation)
async def position_confirmation(cb: CallbackQuery, state: FSMContext):
    confirmation = cb.data
    
    if confirmation not in ["confirm", "cancel"]:
        await cb.message.answer("❌ Please respond with 'yes' or 'no'.")
        return
    if confirmation == "cancel":
        await cb.message.answer("Operation cancelled. To start over, send /long.")
        await state.clear()
        return
    data = await state.get_data()
    ticker = data.get("ticker")
    amount = data.get("amount")
    # Here you would add the logic to open the long position using your trading API
    await cb.message.answer(f"✅ Long position opened for {ticker} with amount ${amount}.")
    await state.clear()
    return