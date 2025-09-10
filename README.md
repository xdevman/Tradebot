# Telegram Trade Bot

A Python-based Telegram bot for trading on Reya Network, using the included [reya-python-sdk](https://github.com/Reya-Labs/reya-python-sdk). Supports placing long and short trades, closing positions, and GTC limit orders. All commands are **admin-only**.

---

## Features

- Open **long** positions  
- Open **short** positions  
- **Close active positions**  
- Place **GTC limit orders** (long/short)  
- Admin-only commands for security

---

## Commands

- `/long <ticker> <amount>` – Open a long position  
- `/short <ticker> <amount>` – Open a short position  
- `/limit <ticker> <side> <amount> <price>` – Open a limit order (GTC)  
- `/close <ticker>` – Close an active position  

## Notes

- Only the Telegram user ID set in the `TID` variable in your `.env` file can execute commands. You can find your user ID using this bot: t.me/userinfobot
- Amounts are in token size (not USD).  
- Limit orders are **Good-Til-Cancelled (GTC)**.

### Examples

```text
/long SOL 0.5       → Open a long position of 0.5 SOL
/short BTC 1        → Open a short position of 1 BTC
/close SOL          → Close the active SOL position
/limit ETH short 2  → Place a GTC limit order for 2 ETH
```

