from aiogram import Bot, Dispatcher,Router,F
from aiogram.types import Message,InlineKeyboardButton,InlineKeyboardMarkup,CallbackQuery
from aiogram import types
from aiogram.filters import Command,CommandObject,StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.core.reya.positions import create_client,ioc_market_orders

from bot.keyboards.inline_confirm import confirm_keyboard
from bot.states.trade_states import Long_States
from bot.utils.validators import admin_only, validate_amount, validate_ticker


long_router = Router()


@long_router.message(Command("long"),StateFilter("*"))
@admin_only
async def long_handler(message: Message,command: CommandObject,state: FSMContext):
    args = command.args
    await state.clear()
    if args:
        args_list = args.split()
        
        if len(args_list) == 2:
            ticker = validate_ticker(args_list[0])
            amount = validate_amount(args_list[1])
            if not ticker:
                await message.answer("❌ Invalid ticker. Try again (e.g., BTC).")
                return
            if not amount:
                await message.answer("❌ Invalid amount. Please send a positive number (e.g., 100).")
                return
        
            await message.answer(f"""Amount set to: {amount} {ticker}
Please confirm opening a long position with this amount:
✅ Confirm: yes
❌ Cancel: no""",reply_markup=confirm_keyboard("long"))
            await state.update_data(ticker=ticker)
            await state.update_data(amount=amount) 
            await state.set_state(Long_States.waiting_for_confirmation)
            return
        elif len(args_list) == 1:
            ticker = validate_ticker(args_list[0])
            if not ticker:
                await message.answer("❌ Invalid ticker. Try again (e.g., BTC).")
                return
            
            await message.answer(f"""Ticker set to: {ticker}
Now send the amount in tokens you want to long.
Example: 500""")
            await state.update_data(ticker=ticker)
            await state.set_state(Long_States.waiting_for_amount)
            return
        else:  # if the agrument was more than 2 
            await message.answer("""
❌ Invalid command format!
To open a long position in one line:
  /long <TICKER> <AMOUNT_IN_TOKENS>
Example: /long OP 500
Or just type /long to set ticker and amount step by step.""")
            return
    else:
        
        await message.answer("📌 Please send the ticker symbol of the token you want to long (e.g., BTC, OP, ETH).")
        await state.set_state(Long_States.waiting_for_ticker)

        return
        
@long_router.message(Long_States.waiting_for_ticker)
async def long_ticker(message: Message, state: FSMContext):
    ticker = validate_ticker(message.text.strip())
    if not ticker:
        await message.answer("❌ Invalid ticker symbol. Try again (e.g., BTC, OP, ETH).")
        return
    
    await state.update_data(ticker=ticker)
    await message.answer(f"Ticker set to: {ticker}\nNow send the amount in tokens you want to long.\nExample: 5")
    await state.set_state(Long_States.waiting_for_amount)
    return

@long_router.message(Long_States.waiting_for_amount)
async def long_amount(message: Message, state: FSMContext):
    
    amount = validate_amount(message.text.strip())
    if not amount:
        await message.answer("❌ Invalid amount. Please send a positive number (e.g., 100).")
        return
     
    await state.update_data(amount=amount)
    data = await state.get_data()
    ticker = data.get("ticker")
    await message.answer(f"Amount set to: {amount} {ticker}\nPlease confirm opening a long position with this amount.",reply_markup=confirm_keyboard("long"))
    await state.set_state(Long_States.waiting_for_confirmation)
    return

@long_router.callback_query(Long_States.waiting_for_confirmation)
async def long_confirmation(cb: CallbackQuery, state: FSMContext):
    confirmation = cb.data
    
    if confirmation not in ["long:confirm", "long:cancel"]:
        await cb.message.answer("❌ Please respond with 'confirm' or 'cancel'.")
        return
    if confirmation == "long:cancel":
        await cb.message.answer("Operation cancelled. To start over, send /long.")
        await state.clear()
        return
    data = await state.get_data()
    ticker = data.get("ticker")
    amount = data.get("amount")
    client = await create_client()
    # Here you would add the logic to open the long position using your trading API
    result = await ioc_market_orders(client=client,order_base=str(amount),market_name=ticker,is_buy=True)
    await cb.message.answer(f"✅ Long position opened successfully!\nTicker: {ticker}\nAmount: {amount} {ticker}\n{result}")
    await state.clear()
    await client.close()
    return