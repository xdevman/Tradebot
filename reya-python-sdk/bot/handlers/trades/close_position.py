from aiogram import Bot, Dispatcher,Router,F
from aiogram.types import Message,InlineKeyboardButton,InlineKeyboardMarkup,CallbackQuery
from aiogram import types
from aiogram.filters import Command,CommandObject,StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.core.reya.rapi import fetch_wallet_positions
from bot.core.reya.positions import ioc_market_orders, create_client
from bot.keyboards.inline_confirm import confirm_keyboard
from bot.states.trade_states import Close_States
from bot.utils.postions_format import format_position, format_positions
from bot.utils.validators import admin_only, validate_ticker


close_router = Router()

def search_positions(positions_data: list[dict], query: str) -> list[dict]:
    query = query.upper()
    return [pos for pos in positions_data if pos["symbol"].startswith(query)]

@close_router.message(Command("close"),StateFilter("*"))
@admin_only
async def close_handler(message: Message,command: CommandObject,state: FSMContext):
    args = command.args
    await state.clear()
    positions_data = fetch_wallet_positions()  # your function
    if not positions_data:
        await message.answer("No open positions ❌")
        return

    
    if args:
        args_list = args.split()
        
        if len(args_list) == 1:
            ticker = validate_ticker(args_list[0])
            
            if not ticker:
                await message.answer("❌ Invalid ticker. Try again (e.g., BTC).")
                return
            positions_data = fetch_wallet_positions()

            matches = search_positions(positions_data, ticker)
            if not matches:
                await message.answer(f"No active positions found for {ticker} ❌")
                return
            
            await message.answer(f"{format_position(matches[0])}\n\nDo you want to close this position?",reply_markup=confirm_keyboard("close"))
            await state.update_data(ticker=ticker)
            await state.update_data(amount=matches[0]["qty"])
            await state.update_data(side=matches[0]["side"])
            
            await state.set_state(Close_States.waiting_for_confirmation)
            return
        else:  # if the agrument was more than 1
            await message.answer("""
Close a Position using a one-liner in the following format 
/close <ticker> e.g. /close OP
Otherwise use just /close to close a position""")
            return
    else:
        formatted = format_positions(positions_data)
        await message.answer(formatted)
        await message.answer("📌 Send the ticker symbol (e.g., BTC).")
        await state.set_state(Close_States.waiting_for_ticker)

        return
        
@close_router.message(Close_States.waiting_for_ticker)
async def close_ticker(message: Message, state: FSMContext):
    ticker = validate_ticker(message.text.strip())
    if not ticker:
        await message.answer("❌ Invalid ticker. Try again (e.g., BTC).")
        return
    positions_data = fetch_wallet_positions()

    matches = search_positions(positions_data, ticker)

    if not matches:
        await message.answer(f"No active positions found for {ticker} ❌")
        return

    await state.update_data(ticker=ticker)
    await state.update_data(amount=matches[0]["qty"])
    await state.update_data(side=matches[0]["side"])
    await message.answer(
        f"{format_position(matches[0])}\n\nDo you want to close this position?",
        reply_markup=confirm_keyboard("close"))
    await state.set_state(Close_States.waiting_for_confirmation)

@close_router.callback_query(Close_States.waiting_for_confirmation)
async def close_confirmation(cb: CallbackQuery, state: FSMContext):
    confirmation = cb.data
    
    if confirmation not in ["close:confirm", "close:cancel"]:
        await cb.message.answer("❌ Please respond with 'yes' or 'no'.")
        return
    if confirmation == "close:cancel":
        await cb.message.answer("Operation cancelled. To start over, send /close.")
        await state.clear()
        return
    data = await state.get_data()
    ticker = data.get("ticker")
    amount = float(data.get("amount"))
    side = data.get("side")
    if side == "B":   # Long
        is_buy = False
    elif side == "A":  # Short
        is_buy = True
    client = await create_client()
    # Here you would add the logic to close the position using your trading API
    result = ioc_market_orders(order_base=str(amount),market_name=ticker,is_buy=is_buy)
    
    await cb.message.answer(f"✅ {ticker} position closed size : {amount}.\n result: {result}")
    await state.clear()
    await client.close()
    return
