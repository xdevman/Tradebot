from ..reya.positions import create_client, gtc_limit_orders


client = create_client()

# show the active positions
def show_positions():
    pass

def show_orders():
    pass


# set limit order
def set_long_order():
    result = gtc_limit_orders(client=client,market_id=4,is_buy=True,price=0.47,size=5)
    print(result)
def set_short_order():
    pass


#set take profits for active postions
def set_long_take_profit():
    pass

def set_short_take_profit():
    pass


#set stoploss for active positions
def set_long_stop_loss():
    pass

def set_short_stop_loss():
    pass


# execute positions by marketprice
def execute_long_position():
    pass

def execute_short_position():
    pass


# cancell the open orders
def cancell_order():
    pass


# close active positions
def close_position():
    pass

print(set_long_order())