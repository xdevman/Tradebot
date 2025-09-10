# Telegram Trade Bot

A Python-based Telegram bot for trading on Reya Network. Supports placing long and short trades, closing positions, and GTC limit orders. All commands are **admin-only**.  

---

## Features

- Open **long** positions  
- Open **short** positions  
- **Close active positions**  
- Place **GTC limit orders** (long/short)  
- Admin-only commands for security  

---

## Commands

All commands are **admin-only**. Only users listed in the `ADMINS` environment variable can execute them.

| Command                        | Description                         |
|--------------------------------|-------------------------------------|
| `/long <market> <size>`         | Open a **long** position            |
| `/short <market> <size>`        | Open a **short** position           |
| `/close <market>`               | Close an active position            |
| `/limit <market> <size>`        | Place a **GTC limit order**         |

### Examples

```text
/long SOL 0.5       → Open a long position of 0.5 SOL
/short BTC 1        → Open a short position of 1 BTC
/close SOL          → Close the active SOL position
/limit ETH 2        → Place a GTC limit order for 2 ETH

