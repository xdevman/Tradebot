from aiogram.fsm.state import State, StatesGroup



class TradeStates(StatesGroup):
    waiting_for_ticker = State()
    waiting_for_amount = State()
    waiting_for_confirmation = State()

class Long_States(StatesGroup):
    waiting_for_ticker = State()
    waiting_for_amount = State()
    waiting_for_confirmation = State()

class limit_States(StatesGroup):
    waiting_for_ticker = State()
    waiting_for_side = State()
    waiting_for_amount = State()
    waiting_for_price = State()
    waiting_for_confirmation = State()

class Short_States(StatesGroup):
    waiting_for_ticker = State()
    waiting_for_amount = State()
    waiting_for_confirmation = State()

class Close_States(StatesGroup):
    waiting_for_ticker = State()
    waiting_for_confirmation = State()