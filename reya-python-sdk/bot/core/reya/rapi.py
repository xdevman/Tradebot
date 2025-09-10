from os import getenv
import requests
from dotenv import load_dotenv

load_dotenv()
address = getenv("WALLET_ADDRESS")

def fetch_wallet_positions():
    response = requests.get(
        f"https://api.reya.xyz/v2/wallet/{address}/positions",
        headers={"Accept":"*/*"},
    )

    data = response.json()
    return data


def fetch_open_orders():
    
    response = requests.get(
        f"https://api.reya.xyz/v2/wallet/{address}/openOrders",
        headers={"Accept":"*/*"},
    )

    data = response.json()
    return data