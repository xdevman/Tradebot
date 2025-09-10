from os import getenv
from dotenv import load_dotenv
from sdk.reya_rpc.types import MarketIds

load_dotenv()

telegram_userid = int(getenv("TID"))

def validate_ticker(text: str) -> str | None:
    ticker = text.strip().upper()
    try:
        market_id = getattr(MarketIds, ticker).value
        return ticker
    except AttributeError:
            # return "❌ Invalid market name: {ticker}"
            return None

def validate_amount(text: str) -> float | None:
    try:
        amount = float(text.strip())
        if amount <= 0:
            return None
        return amount
    except ValueError:
        return None
    
async def is_admin(message):
    return message.from_user.id == telegram_userid

from functools import wraps

def admin_only(func):
    @wraps(func)
    async def wrapper(message, *args, **kwargs):
        if not await is_admin(message):
            await message.answer("❌ You are not authorized.")
            return
        return await func(message, *args, **kwargs)
    return wrapper