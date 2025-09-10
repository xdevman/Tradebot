from aiogram import Bot, Dispatcher,Router,F
from aiogram.types import Message,InlineKeyboardButton,InlineKeyboardMarkup,CallbackQuery
from aiogram import types
from aiogram.filters import Command,CommandObject,StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.core.reya.positions import create_client
from bot.core.reya.trade_exec import trade_on_market
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
        
            await message.answer(f"open long postions for {ticker} with amount {amount}",reply_markup=confirm_keyboard("long"))
            await state.update_data(ticker=ticker)
            await state.update_data(amount=amount) 
            await state.set_state(Long_States.waiting_for_confirmation)
            return
        elif len(args_list) == 1:
            ticker = validate_ticker(args_list[0])
            if not ticker:
                await message.answer("❌ Invalid ticker. Try again (e.g., BTC).")
                return
            
            await message.answer(f"open long postions for {ticker} with default amount\n Please send the amount in USD (e.g., 100).")
            await state.update_data(ticker=ticker)
            await state.set_state(Long_States.waiting_for_amount)
            return
        else:  # if the agrument was more than 2 
            await message.answer("""
Open a long using a one-liner in the following format 
/long <ticker> <amount of margin to use>  e.g. long OP 100
Otherwise use just /long to open a position""")
            return
    else:
        
        await message.answer("📌 Send the ticker symbol (e.g., BTC).")
        await state.set_state(Long_States.waiting_for_ticker)

        return
        
@long_router.message(Long_States.waiting_for_ticker)
async def long_ticker(message: Message, state: FSMContext):
    ticker = validate_ticker(message.text.strip())
    if not ticker:
        await message.answer("❌ Invalid ticker. Try again (e.g., BTC).")
        return
    
    await state.update_data(ticker=ticker)
    await message.answer(f"Ticker set to: {ticker}\nNow send the amount in USD (e.g., 100).")
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
    await message.answer(f"Amount set to: ${amount}\nPlease confirm opening a long position for {ticker} with amount ${amount} (yes/no).",reply_markup=confirm_keyboard("long"))
    await state.set_state(Long_States.waiting_for_confirmation)
    return

@long_router.callback_query(Long_States.waiting_for_confirmation)
async def long_confirmation(cb: CallbackQuery, state: FSMContext):
    confirmation = cb.data
    
    if confirmation not in ["long:confirm", "long:cancel"]:
        await cb.message.answer("❌ Please respond with 'yes' or 'no'.")
        return
    if confirmation == "long:cancel":
        await cb.message.answer("Operation cancelled. To start over, send /long.")
        await state.clear()
        return
    data = await state.get_data()
    ticker = data.get("ticker")
    amount = data.get("amount")
    print(amount,ticker)
    # Here you would add the logic to open the long position using your trading API
    result = trade_on_market(order_base=amount,market_name=ticker)
    await cb.message.answer(f"✅ Long position opened for {ticker} with amount ${amount}.\n result: {result}")
    await state.clear()
    return