#!/usr/bin/env python3

import asyncio
import logging
import os

from dotenv import load_dotenv

from sdk.reya_rest_api import ReyaTradingClient
from sdk.reya_rest_api.config import get_config
from sdk.reya_rest_api.constants.enums import Limit, LimitOrderType, TimeInForce
from sdk.reya_rpc.types import MarketIds
# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Create a logger for this module
logger = logging.getLogger("reya.positions")


def print_separator(title: str):
    """Print a section separator."""
    logger.info("=" * 60)
    logger.info(f" {title} ")
    logger.info("=" * 60)


def handle_order_response(order_type: str, response):
    """Handle and log order response."""
    if hasattr(response, "raw_response"):
        raw = response.raw_response
        if raw.get("success", False):
            logger.info(f"✅ {order_type} order created successfully!")
            if "orderId" in raw:
                logger.info(f"   Order ID: {raw['orderId']}")
            if "transactionHash" in raw:
                logger.info(f"   Transaction Hash: {raw['transactionHash']}")
        else:
            logger.error(f"❌ {order_type} order failed:")
            logger.error(f"   Full error response: {raw}")
            if isinstance(raw, dict):
                logger.error(f"   Error message: {raw.get('error', 'Unknown error')}")
                if "details" in raw:
                    logger.error(f"   Error details: {raw['details']}")
                if "code" in raw:
                    logger.error(f"   Error code: {raw['code']}")
    else:
        logger.info(f"📝 {order_type} response: {response}")
    return response



async def gtc_limit_orders(client: ReyaTradingClient,market_name: str, is_buy: bool, price: str, size: str):
    """Test GTC (Good Till Cancel) limit orders asynchronously."""
    print_separator("TESTING GTC LIMIT ORDERS")
    
    # Set order type
    order_type = LimitOrderType(limit=Limit(time_in_force=TimeInForce.GTC))
    try:
        market_id = getattr(MarketIds, market_name.upper()).value
        print(market_id)
    except AttributeError:
        raise ValueError(f"❌ Invalid market name: {market_name}")
    # Return order IDs for potential cancellation testing
    buy_order_id = None
    sell_order_id = None

    if is_buy:
        # buy limit order
        logger.info("Creating GTC limit buy order...")
        response = await client.create_limit_order(
            market_id=market_id,
            is_buy=is_buy,
            price=price,
            size=size,
            order_type=order_type,
        )
        buy_order_response = handle_order_response("GTC Limit Buy", response)
        
        if hasattr(buy_order_response, "raw_response") and "orderId" in buy_order_response.raw_response:
            buy_order_id = buy_order_response.raw_response["orderId"]

    else:
        # sell limit order
        logger.info("Creating GTC limit sell order...")
        response = await client.create_limit_order(
            market_id=market_id,
            is_buy=is_buy,
            price=price,
            size=size,
            order_type=order_type,
        )
        sell_order_response = handle_order_response("GTC Limit Sell", response)

        if hasattr(sell_order_response, "raw_response") and "orderId" in sell_order_response.raw_response:
            sell_order_id = sell_order_response.raw_response["orderId"]


    return buy_order_id, sell_order_id



async def stop_loss_orders(client: ReyaTradingClient,market_id: int,is_buy: bool,trigger_price: str):
    """Stop Loss orders asynchronously."""
    print_separator("TESTING STOP LOSS ORDERS")

    # Return order IDs
    long_sl_id = None
    short_sl_id = None

    if is_buy: 
        # stop loss for long position (sell when price drops)
        logger.info("Creating stop loss for long position...")
        response = await client.create_stop_loss_order(
            market_id=market_id,
            is_buy=is_buy,
            trigger_price=trigger_price,
        )
        long_sl_response = handle_order_response("Stop Loss (Long Position)", response)
        
        if hasattr(long_sl_response, "raw_response") and "orderId" in long_sl_response.raw_response:
            long_sl_id = long_sl_response.raw_response["orderId"]
    else:
        # stop loss for short position (buy when price rises)
        logger.info("Creating stop loss for short position...")
        response = await client.create_stop_loss_order(
            market_id=market_id,
            is_buy=is_buy,
            trigger_price=trigger_price,
        )
        short_sl_response = handle_order_response("Stop Loss (Short Position)", response)

        if hasattr(short_sl_response, "raw_response") and "orderId" in short_sl_response.raw_response:
            short_sl_id = short_sl_response.raw_response["orderId"]


    return long_sl_id, short_sl_id


async def take_profit_orders(client: ReyaTradingClient,market_id: int,is_buy: bool,trigger_price: str):
    """Take Profit orders asynchronously."""
    print_separator("TESTING TAKE PROFIT ORDERS")

    # Return order IDs
    long_tp_id = None
    short_tp_id = None
    if not is_buy:
        # take profit for long position (sell when price rises)
        logger.info("Creating take profit for long position...")
        response = await client.create_take_profit_order(
            market_id=market_id,
            is_buy=is_buy,
            trigger_price=trigger_price,
        )
        long_tp_response = handle_order_response("Take Profit (Long Position)", response)

        if hasattr(long_tp_response, "raw_response") and "orderId" in long_tp_response.raw_response:
            long_tp_id = long_tp_response.raw_response["orderId"]
    else:
        # take profit for short position (buy when price drops)
        logger.info("Creating take profit for short position...")
        response = await client.create_take_profit_order(
             market_id=market_id,
            is_buy=is_buy,
            trigger_price=trigger_price,
        )
        short_tp_response = handle_order_response("Take Profit (Short Position)", response)

        if hasattr(short_tp_response, "raw_response") and "orderId" in short_tp_response.raw_response:
            short_tp_id = short_tp_response.raw_response["orderId"]


    return long_tp_id, short_tp_id


async def order_cancellation(client: ReyaTradingClient, order_ids: list):
    """order cancellation asynchronously."""
    print_separator("ORDER CANCELLATION")

    valid_order_ids = [oid for oid in order_ids if oid is not None]

    if not valid_order_ids:
        logger.warning("⚠️  No valid order IDs available for cancellation testing")
        return

    # Cancel the first available order
    order_id = valid_order_ids[0]
    logger.info(f"Attempting to cancel order: {order_id}")

    response = await client.cancel_order(order_id=order_id)
    handle_order_response("Order Cancellation", response)


async def test_order_retrieval(client: ReyaTradingClient):
    """Test retrieving orders and positions asynchronously."""
    print_separator("ORDER AND POSITION RETRIEVAL")

    # Get trades
    logger.info("Retrieving trades...")
    trades = await client.get_trades()
    logger.info(f"📊 Found {len(trades)} trades")

    # Get open orders
    logger.info("Retrieving open orders...")
    open_orders = await client.get_open_orders()
    logger.info(f"📊 Found {len(open_orders)} open orders")

    # Get positions
    logger.info("Retrieving positions...")
    positions = await client.get_positions()
    logger.info(f"📊 Found {len(positions)} positions")


async def create_client():
    """Run comprehensive order asynchronously."""
    print_separator("REYA TRADING API - CREATE CLIENT")
    logger.info("🚀 Starting comprehensive order testing...")

    # Load environment variables
    load_dotenv()

    # Verify required environment variables
    required_vars = ["PRIVATE_KEY", "ACCOUNT_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file and ensure all required variables are set.")
        return

    # Create a client instance
    client = ReyaTradingClient()
    logger.info("✅ Client initialized successfully")
    logger.info(f"   Account ID: {client.config.account_id}")
    logger.info(f"   Chain ID: {client.config.chain_id}")
    logger.info(f"   API URL: {client.config.api_url}")
    logger.info(f"   Wallet: {client.wallet_address}")

    return client


async def temp(client: ReyaTradingClient):
      # Collect order IDs for cancellation testing
    all_order_ids = []


    # Test 3: Stop Loss Orders
    long_sl_id, short_sl_id = await stop_loss_orders(client)
    all_order_ids.extend([long_sl_id, short_sl_id])

    # Test 4: Take Profit Orders
    long_tp_id, short_tp_id = await take_profit_orders(client)
    all_order_ids.extend([long_tp_id, short_tp_id])


    # Test 6: Order Cancellation (optional)
    # Uncomment the next line to test order cancellation
    await order_cancellation(client, all_order_ids)

    print_separator("TESTING COMPLETE")
    logger.info("🎉 All order type tests completed!")
    logger.info("💡 Review the logs above to see results for each order type.")
    logger.info("📝 Note: Some orders may fail due to market conditions, insufficient balance, or other constraints.")

# client =  create_client()

async def set_long_order(client):
    result =  await gtc_limit_orders(client=client,market_id=4,is_buy=True,price="0.47",size="5000")
    print(result)

async def set_short_order(client,market_id:int,price:str,size:str):
    result =  await gtc_limit_orders(client=client,market_id=4,is_buy=True,price="0.47",size="5000")
    print(result)



if __name__ == "__main__":
    client = asyncio.run(create_client())
    order_id = asyncio.run(set_long_order(client))
    print(order_id)