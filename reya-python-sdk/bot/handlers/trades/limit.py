from aiogram import Bot, Dispatcher,Router,F
from aiogram.types import Message,InlineKeyboardButton,InlineKeyboardMarkup,CallbackQuery
from aiogram import types
from aiogram.filters import Command,CommandObject,StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.core.reya.positions import create_client, gtc_limit_orders
from bot.keyboards.inline_confirm import confirm_keyboard
from bot.states.trade_states import limit_States
from bot.utils.validators import admin_only, validate_ticker


limit_router = Router()

@limit_router.message(Command("limit"),StateFilter("*"))
@admin_only
async def limit_handler(message: Message, command: CommandObject, state: FSMContext):
    args = command.args
    await state.clear()
    
    if args:
        args_list = args.split()
        
        if len(args_list) == 4:
            ticker = validate_ticker(args_list[0])
            side = args_list[1]
            amount = args_list[2]
            price = args_list[3] 
            if not ticker:
                await message.answer("❌ Invalid ticker. Try again (e.g., BTC).")
                return
            await message.answer(f"Please confirm opening a {side} limit order for {ticker} with amount {amount} tokens at {price}",reply_markup=confirm_keyboard("limit"))
            await state.update_data(ticker=ticker)
            await state.update_data(side=side)
            await state.update_data(amount=amount)
            await state.update_data(price=price)

            await state.set_state(limit_States.waiting_for_confirmation)

            return
        elif len(args_list) == 3:
            ticker = validate_ticker(args_list[0])
            side = args_list[1]
            amount = args_list[2]
            if not ticker:
                await message.answer("❌ Invalid ticker. Try again (e.g., BTC).")
                return
            await message.answer(f"Now send the price (e.g., 0.80).")
            await state.update_data(ticker=ticker)
            await state.update_data(side=side)
            await state.update_data(amount=amount)
            await state.set_state(limit_States.waiting_for_price)

            return
        elif len(args_list) == 2:
            ticker = validate_ticker(args_list[0])
            side = args_list[1]
            if not ticker:
                await message.answer("❌ Invalid ticker. Try again (e.g., BTC).")
                return
            await message.answer(f"Now send the amount in tokens (e.g., 100).")
            await state.update_data(ticker=ticker)
            await state.update_data(side=side)
            await state.set_state(limit_States.waiting_for_amount)
            return
        elif len(args_list) == 1:
            ticker = validate_ticker(args_list[0])
            if not ticker:
                await message.answer("❌ Invalid ticker. Try again (e.g., BTC).")
                return
            await message.answer(f"Ticker set to: {ticker}\nNow set the side: long or short.")
            await state.update_data(ticker=ticker)
            await state.set_state(limit_States.waiting_for_side)
            return
        else:
            await message.answer("""
Open a limit order using a one-liner in the following format 
/limit <ticker> <side> <amount> <price> e.g. limit OP long 100 0.80
Otherwise use just /limit to open a limit order""")
            return
    else:
        await message.answer("📌 Send the ticker symbol (e.g., BTC).")
        await state.set_state(limit_States.waiting_for_ticker)
        return
        # await message.answer("open limit order with default settings")
        # client = await create_client()
        # order_id = await set_long_order(client)
        # await message.answer(f"✅ Order placed with ID: {order_id}")
        # return

@limit_router.message(Command("cancel"),StateFilter("*"))
@admin_only
async def limit_handler(message: Message, command: CommandObject, state: FSMContext):
    args = command.args
    await state.clear()
    
    if args:
        args_list = args.split()
        return


@limit_router.message(limit_States.waiting_for_ticker)
async def limit_ticker(message: Message, state: FSMContext):
    ticker = validate_ticker(message.text.strip().upper())   
    if not ticker:
        await message.answer("❌ Invalid ticker. Try again (e.g., BTC).")
        return
    await state.update_data(ticker=ticker)
    await message.answer(f"Ticker set to: {ticker}\nNow set the side: long or short.")
    await state.set_state(limit_States.waiting_for_side)
    return

@limit_router.message(limit_States.waiting_for_side)
async def limit_side(message: Message, state: FSMContext):
    try:
        side = message.text.strip().lower()
        # print(side)
        if side != "long" and side != "short":
            raise ValueError("side must long or short")
    except ValueError:
        await message.answer("❌ Invalid side. Please set long or short")
        return
    await state.update_data(side=side)
    data = await state.get_data()
    ticker = data.get("ticker")
    await message.answer(f"Side set to: {side}\nNow send the amount in tokens (e.g., 100).")
    await state.set_state(limit_States.waiting_for_amount)
    return

@limit_router.message(limit_States.waiting_for_amount)
async def limit_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError("Amount must be positive.")
    except ValueError:
        await message.answer("❌ Invalid amount. Please send a positive number (e.g., 100).")
        return
    await state.update_data(amount=amount)    
    await message.answer(f"Amount set to: {amount}\nNow send the price (e.g., 0.80).")
    await state.set_state(limit_States.waiting_for_price)
    return

@limit_router.message(limit_States.waiting_for_price)
async def limit_amount(message: Message, state: FSMContext):
    try:
        price = float(message.text.strip())
        if type(price) != float:
            raise ValueError("price must be number.")
    except ValueError:
        await message.answer("❌ Invalid amount. Please send a positive number (e.g., 100).")
        return
    await state.update_data(price=price)
    data = await state.get_data()
    ticker = data.get("ticker")
    amount = data.get("amount")
    side = data.get("side")
    await message.answer(f"Price set to: {price}\nPlease confirm opening a {side} limit order for {ticker} with amount {amount} tokens at {price}.",reply_markup=confirm_keyboard("limit"))
    await state.set_state(limit_States.waiting_for_confirmation)
    return


@limit_router.callback_query(limit_States.waiting_for_confirmation)
async def limit_confirmation(cb: CallbackQuery, state: FSMContext):
    confirmation = cb.data
    
    if confirmation not in ["limit:confirm", "limit:cancel"]:
        await cb.message.answer("❌ Please respond with 'yes' or 'no'.")
        return
    if confirmation == "limit:cancel":
        await cb.message.answer("Operation cancelled. To start over, send /limit.")
        await state.clear()
        return
    client = await create_client()
    data = await state.get_data()
    ticker = data.get("ticker")
    amount = data.get("amount")
    price = data.get("price")
    side = data.get("side")
    if side == "long":
        is_buy = True   
    else:
        is_buy = False
    result =  await gtc_limit_orders(client=client, market_name=ticker, is_buy=is_buy, price=str(price), size=str(amount))
    # print(result)
    await client.close()
    # Here you would add the logic to open the limit order using your trading API
    await cb.message.answer(f"✅ {side} limit order opened successfully!\nTicker: {ticker}\nAmount: {amount} tokens\nPrice: {price}\n{result}")
    await state.clear()
    return
