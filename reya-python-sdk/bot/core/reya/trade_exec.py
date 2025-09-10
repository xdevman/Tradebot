
import os

from dotenv import load_dotenv
from web3 import Web3

from sdk.reya_rpc import MarketIds, TradeParams, get_config, trade

def trade_on_market(order_base,market_name):
    """
    Example script demonstrating how to execute long and short trades on market.
    """

    # Load environment variables from .env file
    load_dotenv()

    # Retrieve the margin account ID from environment variables
    account_id = int(os.environ["ACCOUNT_ID"])

    # Load configuration
    config = get_config()

   
    """
    Executes a trade on a given market.

    Args:
        order_base (float): Trade size in base asset terms.
                            Positive for long (buy), negative for short (sell).
        market_name (str): The market symbol, e.g., "SOL", "BTC", "ETH".
    """

    # Retrieve SOL market ID
    # market_id = MarketIds.SOL.value

    try:
        market_id = getattr(MarketIds, market_name.upper()).value
        print(market_id)
    except AttributeError:
        raise ValueError(f"❌ Invalid market name: {market_name}")

    # Define price limit: 0 for shorts, high limit (1e9) for longs
    price_limit = 0 if order_base < 0 else 1_000_000_000

    # Convert order size amd price limit to 18 decimal places (as required by smart contracts)
    abs_order_base_e18 = Web3.to_wei(abs(order_base), "ether")
    order_base_e18 = abs_order_base_e18 if order_base > 0 else -abs_order_base_e18
    price_limit_e18 = Web3.to_wei(price_limit, "ether")

    # Execute trade transaction
    result = trade(
        config=config,
        params=TradeParams(
            account_id=account_id,
            market_id=market_id,
            base=order_base_e18,
            price_limit=price_limit_e18,
        ),
    )

    execution_price = result["execution_price"] / 1e18
    fees = result["fees"] / 1e6
    return f"Trade information: execution price = {execution_price} and paid fees = {fees} rUSD"
